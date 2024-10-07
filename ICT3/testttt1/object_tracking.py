import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 读取CSV文件
df = pd.read_csv('moving_objects_coordinates.csv')

# 获取所有唯一的目标ID
unique_ids = df['ID'].unique()

# 初始化一个字典来存储坐标和速度信息
tracking_results = {obj_id: [None] * 1000 for obj_id in unique_ids}
predicted_coordinates = {}

# 遍历每一帧
for frame in range(1000):
    # 找出当前帧的数据
    frame_data = df[df['Frame'] == frame]
    
    # 对于每个目标ID，输出其位置
    for obj_id in unique_ids:
        if not frame_data[frame_data['ID'] == obj_id].empty:
            x = frame_data.loc[frame_data['ID'] == obj_id, 'X'].values[0]
            y = frame_data.loc[frame_data['ID'] == obj_id, 'Y'].values[0]
            tracking_results[obj_id][frame] = (x, y)  # 存储坐标
        else:
            tracking_results[obj_id][frame] = (None, None)

# 对每个目标进行线性回归预测下一帧坐标
for obj_id in unique_ids:
    coordinates = [pos for pos in tracking_results[obj_id] if pos is not None]
    
    if len(coordinates) < 2:
        continue  # 如果有效坐标点少于2个，则跳过该目标
    
    # 创建训练数据
    X = np.arange(len(coordinates)).reshape(-1, 1)  # 帧数（自变量）
    y_x = np.array([coord[0] for coord in coordinates])  # x坐标
    y_y = np.array([coord[1] for coord in coordinates])  # y坐标
    
    # 使用线性回归模型拟合x和y坐标
    model_x = LinearRegression().fit(X, y_x)
    model_y = LinearRegression().fit(X, y_y)
    
    # 预测下一帧的坐标
    next_frame = len(coordinates)
    predicted_x = model_x.predict([[next_frame]])[0]
    predicted_y = model_y.predict([[next_frame]])[0]
    predicted_coordinates[obj_id] = (predicted_x, predicted_y)

# 创建一个新的 DataFrame 用于输出
output_df = pd.DataFrame(index=unique_ids, columns=range(1000))

# 填充 DataFrame
for obj_id, positions in tracking_results.items():
    for frame, (x, y) in enumerate(positions):
        if x is not None and y is not None:
            output_df.at[obj_id, frame] = f"({x:.2f}, {y:.2f})"
        else:
            output_df.at[obj_id, frame] = "未检测到"

# 将预测的下一帧坐标添加到输出中
for obj_id, (pred_x, pred_y) in predicted_coordinates.items():
    output_df.at[obj_id, next_frame] = f"预测: ({pred_x:.2f}, {pred_y:.2f})"

# 将结果写入新的CSV文件
output_df.to_csv('object_tracking_results_with_predictions.csv')
