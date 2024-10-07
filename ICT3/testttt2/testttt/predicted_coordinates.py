import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

# 读取原始数据
df = pd.read_csv('object_tracking_results.csv', index_col=0)

# 存储预测结果的列表
predictions = []

# 对每个对象进行逐帧预测
for obj_id in df.index:
    positions = df.loc[obj_id].values
    X = np.array(range(len(positions))).reshape(-1, 1)  # 帧数
    y = np.array([eval(pos) for pos in positions])  # 转换为坐标元组

    # 初始化模型
    model_x = LinearRegression()
    model_y = LinearRegression()

    # 遍历每一帧，进行预测
    for i in range(len(positions) - 1):
        # 使用当前帧的历史数据进行训练
        X_train = X[:i + 1]  # 包含到当前帧的所有帧数
        y_train = y[:i + 1]  # 包含到当前帧的所有位置
        
        # 拟合模型
        model_x.fit(X_train, y_train[:, 0])
        model_y.fit(X_train, y_train[:, 1])

        # 预测下一帧
        next_frame = np.array([[i + 1]])  # 下一帧的索引
        predicted_x = model_x.predict(next_frame)
        predicted_y = model_y.predict(next_frame)

        # 将预测结果添加到列表中
        predictions.append({'ID': obj_id, 'Frame': i + 1, 'Predicted_X': predicted_x[0], 'Predicted_Y': predicted_y[0]})

# 创建预测数据的DataFrame
predicted_df = pd.DataFrame(predictions)

# 将预测结果写入CSV文件
predicted_df.to_csv('predicted_coordinates.csv', index=False)

print("逐帧预测已成功生成并写入到 'predicted_coordinates.csv'。")
