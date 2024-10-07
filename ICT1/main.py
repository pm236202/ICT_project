import struct

class TSPacket:
    def __init__(self, packet_data):
        self.packet_data = packet_data

    @property
    def packet_type(self):
        return self.packet_data[1] & 0x1F

    @property
    def payload(self):
        # 提取有效载荷
        adaptation_field_control = (self.packet_data[1] >> 2) & 0x03
        if adaptation_field_control == 0x03:
            # 只有适配字段
            return None
        elif adaptation_field_control == 0x02:
            # 只有负载
            payload_start_index = 4
            return self.packet_data[payload_start_index:]
        else:
            # 适配字段和负载
            adaptation_field_length = self.packet_data[4]
            payload_start_index = 5 + adaptation_field_length
            return self.packet_data[payload_start_index:]

class PESPacket:
    def __init__(self, ts_packet):
        self.packet_data = ts_packet.payload

    @property
    def stream_type(self):
        if self.packet_data is not None and len(self.packet_data) >= 5:
            return self.packet_data[0]
        return None

    @property
    def data(self):
        if self.packet_data is not None and len(self.packet_data) >= 5:
            return self.packet_data[5:]
        return None

def parse_sei_data(sei_data):
    sei_payload = sei_data[4:]  # 去掉前四个字节（SEI payload type 和长度）

    while sei_payload:
        sei_payload_type, = struct.unpack('B', sei_payload[:1])
        sei_payload_length, = struct.unpack('B', sei_payload[1:2])

        # 获取 SEI payload 数据
        sei_payload_data = sei_payload[2:2 + sei_payload_length]

        # 输出 SEI payload 类型和数据
        print(f"SEI Payload Type: {sei_payload_type}")
        print(f"SEI Payload Data: {sei_payload_data.hex()}")

        # 具体解析 SEI 数据
        if sei_payload_type == 0x03:  # User Data Registered ID
            parse_user_data_registered_id(sei_payload_data)
        elif sei_payload_type == 0x01:  # Unregistered SEI message
            parse_unregistered_sei_message(sei_payload_data)

        # 更新 sei_payload
        sei_payload = sei_payload[2 + sei_payload_length]

def parse_user_data_registered_id(data):
    # 解析 User Data Registered ID
    registered_id, = struct.unpack('>L', data[:4])
    remaining_data = data[4:]
    print(f"Registered ID: {registered_id}")
    print(f"Remaining Data: {remaining_data.hex()}")

def parse_unregistered_sei_message(data):
    # 解析 Unregistered SEI message
    message_type, = struct.unpack('B', data[:1])
    message_length, = struct.unpack('B', data[1:2])
    message_data = data[2:2 + message_length]
    print(f"Message Type: {message_type}")
    print(f"Message Length: {message_length}")
    print(f"Message Data: {message_data.hex()}")

def parse_ts_file(ts_file_path, output_file_path):
    # 打开TS文件
    with open(ts_file_path, 'rb') as file:
        sei_info_list = []

        while True:
            # 读取188字节的TS包
            packet_data = file.read(188)
            if not packet_data:
                break

            # 解析TS包
            ts_packet = TSPacket(packet_data)

            # 如果是PES包，尝试读取包含SEI信息的PES包
            if ts_packet.packet_type == 0x00:  # PES包的包类型为0x00
                pes_packet = PESPacket(ts_packet)
                if pes_packet.stream_type == 0x06:  # H.264 SEI的流类型为0x06
                    sei_info = pes_packet.data
                    if sei_info:
                        sei_info_list.append(sei_info)

    # 将SEI信息保存到文本文件
    with open(output_file_path, 'w') as output_file:
        for sei_info in sei_info_list:
            output_file.write(f"{sei_info.hex()}\n")

    # 解析并打印SEI信息
    for sei_info in sei_info_list:
        parse_sei_data(sei_info)

# 调用函数读取TS文件并将SEI信息保存到文本文件
parse_ts_file("D:\学习\ict\output.h264", "D:\学习\ict\sei_info4.txt")