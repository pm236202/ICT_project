import pandas as pd
import numpy as np

# 设置参数
num_frames = 1000
num_objects = 10  # 不同的移动目标物数量

# 定义物体类别
object_classes = ['person', 'car', 'truck', 'motorbike']

# 初始化数据字典
data = {
    'Frame': [],
    'ID': [],
    'Class': [],
    'Confidence': [],
    'X': [],
    'Y': [],
    'Width': [],
    'Height': []
}

# 随机生成第一帧的物体类别和置信度
initial_classes = []
initial_confidences = []

for object_id in range(num_objects):
    object_class = np.random.choice(object_classes)  # 随机选择物体类别
    confidence = np.random.uniform(0.5, 1.0)  # 随机生成置信度
    initial_classes.append(object_class)
    initial_confidences.append(confidence)

# 为每一帧和每一个物体生成数据
for frame in range(num_frames):
    for object_id in range(num_objects):
        if frame == 0:
            # 第一帧: 使用随机生成的类别和置信度
            object_class = initial_classes[object_id]
            confidence = initial_confidences[object_id]
        else:
            # 后续帧: 类别保持不变，置信度轻微随机波动
            object_class = initial_classes[object_id]
            confidence = np.clip(initial_confidences[object_id] + np.random.normal(0, 0.05), 0.5, 1.0)

        # 随机生成其他属性
        x_coord = np.random.uniform(0, 100)
        y_coord = np.random.uniform(0, 100)
        width = np.random.uniform(1, 10)
        height = np.random.uniform(1, 10)

        # 创建唯一标识符
        identifier = f"{object_class}{object_id + 1}"

        # 添加数据到字典
        data['Frame'].append(frame)
        data['ID'].append(identifier)
        data['Class'].append(object_class)
        data['Confidence'].append(confidence)
        data['X'].append(x_coord)
        data['Y'].append(y_coord)
        data['Width'].append(width)
        data['Height'].append(height)

# 创建 DataFrame
df = pd.DataFrame(data)

# 保存为 CSV 文件
df.to_csv('moving_objects_coordinates.csv', index=False)

print("CSV文件已生成：moving_objects_coordinates.csv")
