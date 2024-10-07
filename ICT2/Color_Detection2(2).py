import cv2
import numpy as np
import pandas as pd
import os
from collections import defaultdict

# 设置保存结果的路径
output_dir = r"D:\hdu\ICT\结果"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 加载 YOLOv4-tiny 模型
net = cv2.dnn.readNet(r"D:\hdu\ICT2\yolov4-tiny.weights.bin", r"D:\hdu\ICT2\yolov4-tiny.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# 读取类别文件
class_list = []
with open(r"D:\hdu\ICT2\classes.txt", 'r') as txt:
    class_list = [line.strip() for line in txt.readlines()]

# 颜色映射表：为不同类别分配不同的颜色（RGB格式）
colors = {
    "person": (0, 255, 0),        # 绿色
    "bicycle": (255, 0, 255),     # 紫色
    "motorcycle": (255, 128, 0),  # 橙色
    "car": (0, 0, 255),           # 红色
    "truck": (255, 0, 0),         # 蓝色
    "bus": (255, 255, 0)          # 黄色
}

# 获取 YOLOv4-tiny 的输出层
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# 初始化跟踪器相关的参数
object_id = 0  # 初始ID
previous_objects = []  # 记录上一帧中的物体（ID, 坐标, 尺寸, 类别）
max_distance = 150  # 增加跟踪阈值，若物体之间的距离小于该值，则认为是同一个物体
size_threshold = 0.2  # 宽高比例变化的允许范围，用于判断是否是同一个目标
person_bike_distance = 80  # 人和非机动车之间的距离阈值，用于判断是否为“骑行状态”

# 读取视频文件
video = cv2.VideoCapture(r"D:\hdu\ICT\原素材\20240711152253.ts")

# 检查是否成功加载视频
if not video.isOpened():
    print("无法打开视频文件，检查路径或视频格式是否正确")
    exit()

# 获取视频宽度和高度
fps = video.get(cv2.CAP_PROP_FPS)
frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

output_video_path = os.path.join(output_dir, "检测结果.avi")
out = cv2.VideoWriter(output_video_path, 
                      cv2.VideoWriter_fourcc(*'XVID'), 
                      fps, 
                      (frame_width, frame_height))

# 创建可调整大小的窗口
cv2.namedWindow("Object Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Object Detection", frame_width, frame_height)

# 存储检测结果的列表
detection_results = []
frame_count = 0

# 类别稳定性缓冲：用于记录每个ID的类别
object_class_buffer = defaultdict(lambda: {"class": None, "count": 0})

while True:
    ret, frame = video.read()
    if not ret:
        print("无法读取帧，可能视频已结束或格式不支持")
        break

    # 创建模型输入 (Blob)
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    detections = net.forward(output_layers)

    class_ids, confidences, boxes, current_objects = [], [], [], []

    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:  # 提高置信度阈值到0.5
                box = obj[0:4] * np.array([frame_width, frame_height, frame_width, frame_height])
                (centerX, centerY, width, height) = box.astype("int")
                x = max(0, int(centerX - (width / 2)))
                y = max(0, int(centerY - (height / 2)))
                w = min(frame_width - x, int(width))
                h = min(frame_height - y, int(height))

                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

                # 跟踪器部分：分配物体 ID
                new_id = None
                new_class = class_list[class_id]

                # 只有当类名在类别列表中，且不是未识别类别时才进行ID分配
                if new_class in ["person", "bicycle", "motorcycle", "car", "truck", "bus"]:
                    for prev_obj in previous_objects:
                        prev_id, prev_x, prev_y, prev_w, prev_h, prev_class = prev_obj
                        distance = np.linalg.norm(np.array([x, y]) - np.array([prev_x, prev_y]))
                        size_diff = abs(w - prev_w) / max(prev_w, 1) + abs(h - prev_h) / max(prev_h, 1)

                        # 使用距离和尺寸变化来判断是否为同一目标
                        if distance < max_distance and size_diff < size_threshold:
                            # 当检测到“人”和“非机动车”接近时，标记为“非机动车”
                            if (class_list[class_id] == "person" and prev_class in ["bicycle", "motorcycle"] and distance < person_bike_distance) or \
                               (prev_class == "person" and class_list[class_id] in ["bicycle", "motorcycle"] and distance < person_bike_distance):
                                new_class = "bicycle" if prev_class == "bicycle" or class_list[class_id] == "bicycle" else "motorcycle"
                            
                            new_id = prev_id
                            break
                    
                    if new_id is None:
                        new_id = object_id  # 新物体，分配新 ID
                        object_id += 1
                    
                    current_objects.append((new_id, x, y, w, h, new_class))  # 保存当前帧中的物体ID、坐标和尺寸、类别

                    # 类别稳定性逻辑
                    if object_class_buffer[new_id]["class"] == new_class:
                        object_class_buffer[new_id]["count"] += 1
                    else:
                        object_class_buffer[new_id]["class"] = new_class
                        object_class_buffer[new_id]["count"] = 1

                    # 如果类别在连续3帧中相同，则确认该类别
                    stable_class = object_class_buffer[new_id]["class"] if object_class_buffer[new_id]["count"] >= 3 else None

                    # 保存检测结果，包含物体 ID 和稳定后的类别
                    if stable_class is not None:
                        detection_results.append({
                            "Frame": frame_count,
                            "ID": new_id,
                            "Class": stable_class,
                            "Confidence": confidence,
                            "X": x,
                            "Y": y,
                            "Width": w,
                            "Height": h
                        })
                        print(f"保存检测结果: ID {new_id}, 类别 {stable_class}, 置信度 {confidence}, 坐标 ({x}, {y}), 宽: {w}, 高: {h}")

    # 更新上一帧的物体信息
    previous_objects = current_objects

    indices = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.5, nms_threshold=0.4)  # 调整NMS阈值到0.4
    print(f"保留了 {len(indices)} 个检测框")

    # 绘制边界框并标注
    if len(indices) > 0:
        for idx in indices.flatten():
            if idx < len(current_objects):  # 确保索引不超出 current_objects 的范围
                x, y, w, h = boxes[idx]
                detected_class = object_class_buffer[current_objects[idx][0]]["class"] if object_class_buffer[current_objects[idx][0]]["count"] >= 3 else None
                if detected_class is not None:
                    label = f"ID {current_objects[idx][0]}: {detected_class}: {confidences[idx]:.2f}"
                    
                    # 根据类别选择颜色，如果没有指定默认使用白色
                    color = colors.get(detected_class, (255, 255, 255))

                    # 画出检测到的目标边界框
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    # 在边界框上方显示检测到的目标类别名称和置信度
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # 显示检测结果的每一帧
    cv2.imshow("Object Detection", frame)

    # 使用 30ms 延迟确保窗口刷新
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

    out.write(frame)  # 将每一帧写入输出视频
    frame_count += 1

# 释放视频文件并关闭所有窗口
video.release()
out.release()
cv2.destroyAllWindows()

# 保存检测结果到 CSV 文件
output_csv_path = os.path.join(output_dir, "检测结果.csv")
if detection_results:
    df = pd.DataFrame(detection_results)
    df.to_csv(output_csv_path, index=False)  # 保存为 CSV 文件
    print(f"检测结果已保存到 {output_csv_path}")
else:
    print("没有检测结果保存")
