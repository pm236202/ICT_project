import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# 读取原始数据，假设行首为唯一标识符，列首为帧数
df = pd.read_csv('object_tracking_results.csv', index_col=0)

# 设置帧数和目标ID
max_frames = df.shape[1]  # 获取最大帧数
unique_ids = df.index

# 存储结果的列表
results = []

# 计算速度和方向
for obj_id in unique_ids:
    for frame in range(1, max_frames + 1):
        current_position = df.iloc[unique_ids.get_loc(obj_id), frame] if frame in df.columns else None
        previous_position = df.iloc[unique_ids.get_loc(obj_id), frame - 1] if (frame - 1) in df.columns else None

        if current_position and previous_position:
            # 将字符串转换为元组
            current_x, current_y = eval(current_position)
            previous_x, previous_y = eval(previous_position)

            # 计算位移
            displacement_x = current_x - previous_x
            displacement_y = current_y - previous_y

            # 计算速度（假设每帧时间间隔为1）
            speed = np.sqrt(displacement_x**2 + displacement_y**2)

            # 计算方向（以弧度表示，使用arctan2考虑象限）
            direction = np.arctan2(displacement_y, displacement_x)

            # 将结果添加到列表中
            results.append({'Frame': frame, 'ID': obj_id, 'Speed': speed, 'Direction': direction})

# 创建结果DataFrame
results_df = pd.DataFrame(results)

# 如果需要，可以使用StandardScaler标准化速度
scaler = StandardScaler()
results_df['Speed'] = scaler.fit_transform(results_df[['Speed']])

# 将结果写入新的CSV文件
results_df.to_csv('speed_and_direction_results.csv', index=False)

print("速度和方向已成功计算并写入到 'speed_and_direction_results.csv'。")
