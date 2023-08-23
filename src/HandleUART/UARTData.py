from C_DEFINE import *


class UART_DATA:
    def __init__(self):
        self.port_dict = {}  # 用来存放已检测串口的字典
        self.port_get = list()  # 当前获取的端口表
        self.port_list = list()  # 本地存下的端口表
        self.ser = serial.Serial()

        self.port_statu = 0  # 串口开关标志
        self.send_str = ""  # 发送的字符串

        self.read_set_parsed = ''   # 接收到待解析的字符串
        self.no_read_cnt = 0    # 未接收计数

    # 串口状态
    serial_on = 1
    serial_off = 0


UART_Data = UART_DATA()
