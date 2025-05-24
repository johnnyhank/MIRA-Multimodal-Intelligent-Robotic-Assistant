import serial
import time

# 定义microbit的串口配置
MICROBIT_SERIAL_PORT = "/dev/ttyACM0"  # 根据你的实际端口号修改
BAUD_RATE = 115200  # 与microbit代码中的波特率一致

# 初始化串口连接
def connect_microbit():
    try:
        ser = serial.Serial(MICROBIT_SERIAL_PORT, BAUD_RATE, timeout=1)
        print("成功连接到microbit！")
        return ser
    except Exception as e:
        print(f"连接microbit失败: {e}")
        return None

# 向microbit发送数据
def send_data_microbit(ser, data):
    if ser and ser.is_open:
        try:
            ser.write((data + '\n').encode())  # 添加换行符以匹配microbit的read_until
            print(f"已发送数据: {data}")
        except Exception as e:
            print(f"发送数据失败: {e}")
    else:
        print("串口未打开")

# 关闭串口连接
def disconnect_microbit(ser):
    if ser and ser.is_open:
        ser.close()
        print("串口已关闭")

# 示例用法
if __name__ == "__main__":
    ser = connect_microbit()
    if ser:
        try:
            # 发送一些测试数据
            send_data_microbit(ser, "happy")  # 显示笑脸图标
            time.sleep(2)

            send_data_microbit(ser, "heart")  # 显示心形图标
            time.sleep(2)

            send_data_microbit(ser, "birthday")  # 播放生日歌
            time.sleep(10)  # 给足够的时间播放音乐

        finally:
            disconnect_microbit(ser)