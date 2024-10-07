import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# 读取 CSV 文件
df = pd.read_csv('moving_objects_coordinates.csv')

# 检查是否有缺失值，并移除含有缺失值的行
df = df.dropna(subset=[df.columns[0], df.columns[1], df.columns[4], df.columns[5]])  # 第一、第二、第五、第六列

# 按照 ID 和时间戳排序
df = df.sort_values(by=[df.columns[1], df.columns[0]])

# 创建空的列表来存储预测结果
predictions = []

# 按 ID 分组处理
for id_val, group in df.groupby(df.columns[1]):
    timestamps = group.iloc[:, 0].values.reshape(-1, 1)  # 第一列：时间戳
    x_positions = group.iloc[:, 4].values  # 第五列：X位置
    y_positions = group.iloc[:, 5].values  # 第六列：Y位置

    # 创建线性回归模型并训练
    model_x = LinearRegression()
    model_y = LinearRegression()
    model_x.fit(timestamps, x_positions)
    model_y.fit(timestamps, y_positions)

    # 预测未来位置并插入到预测列
    for i in range(len(group)):
        next_timestamp = np.array([[group.iloc[i, 0] + 1]])  # 下一个时间戳（在现有时间戳上加1）
        predicted_x_position = model_x.predict(next_timestamp)[0]
        predicted_y_position = model_y.predict(next_timestamp)[0]

        # 添加预测结果到列表
        predictions.append([group.iloc[i, 0], id_val, predicted_x_position, predicted_y_position])

# 将预测结果转换为 DataFrame
predictions_df = pd.DataFrame(predictions, columns=['timestamp', 'id', 'predicted_x', 'predicted_y'])

# 保存回新的 CSV 文件
predictions_df.to_csv('预测结果.csv', index=False)


