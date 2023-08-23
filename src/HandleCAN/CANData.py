from ctypes import CDLL, pointer

from C_DEFINE import *

# 假装的联合体 CANID位定义
class CanProto_MsgID_BITS(ctypes.LittleEndianStructure):
    _fields_ = [
        ("bParaID", ctypes.c_uint16, 6),
        ("bCabID", ctypes.c_uint16, 4),
        ("bRX_Mes", ctypes.c_uint16, 6),
        ("bKind", ctypes.c_uint16, 8),
        ("bTX_Mes", ctypes.c_uint16, 3),
        ("bPriority", ctypes.c_uint16, 2),
        ("bBITs", ctypes.c_uint16, 3),
    ]
class CanProtoMsgID(ctypes.Union):
    _fields_ = [
        ("all", ctypes.c_int32),
        ("bit", CanProto_MsgID_BITS),
    ]


def Id_4_UnionId(id):
    reid = CanProtoMsgID()
    reid.all = id
    return reid

def id_bit_union(bParaID, bCabID, bRX_Mes, bKind, bTX_Mes, bPriority):
    reid = CanProtoMsgID()
    reid.bit.bParaID = bParaID
    reid.bit.bCabID = bCabID
    reid.bit.bRX_Mes = bRX_Mes
    reid.bit.bKind = bKind
    reid.bit.bTX_Mes = bTX_Mes
    reid.bit.bPriority = bPriority
    return reid.all

class CAN_DATA:
    def __init__(self):
        self.ItekonCan = CDLL('.\\kerneldlls\\ControlCAN.dll')  # BL过程中调用的Itekon的CAN盒API包
        # ---->BL相关
        self.BL_CounterLen = 0  # BL下载总文件大小
        self.BL_AcceptString = ''  # BL过程中的字符串接收
        self.verify_data = b''  # BL过程预读文件的字符串
        self.verify_data_send_pause = 1  # 有效包标志，为0则关闭发送
        self.BL_tx_arb_id = 0x00000000  # BL过程中的发送CANID仲裁，BL流程初始时进行赋值，不赋kind
        self.BL_rx_arb_id = 0x00000000  # BL过程中的接收回复CANID仲裁，ID为此值是流程正常
        self.BL_ADDR_START = 0x300000  # BL过程设定相关,烧录起始地址
        self.BL_ADDR_START_MAX = 0x370000  # BL过程设定相关,烧录最大结尾地址
        self.init_config = VCI_INIT_CONFIG(AccCode=0, AccMask=0xffffffff, Filter=1, Timing0=0x01,
                                           Timing1=0x1C)  # CAN盒初始化参数设置
        self.init_config_c = pointer(self.init_config)  # CAN盒配置
        self.recv_msg = VCI_CAN_OBJ()  # 接收包定义
        self.recv_msg_c = pointer(self.recv_msg)  # 接收包取地址
        self.send_msg = VCI_CAN_OBJ(ID=0x00000000, DataLen=8, ExternFlag=1, RemoteFlag=0, SendType=0, TimeFlag=0,
                                    TimeStamp=0x00)  # 发送包定义
        self.send_msg_c = pointer(self.send_msg)  # 接收包取地址
        self.bl_process = None  # 用于注册发送流程
        self.bl_step = 0  # 寄存已发送的bKind
        self.bl_counter_len_past = 0  # 已发送数据清零
        self.bl_data_verify = 0  # 多包数据的和校验
        self.bl_packa_num = 0  # 需发数据包计数清0
        self.bl_packa_num_past = 0  # 已发数据包计数清0
        self.flash_data = b''
        # <----


ididid = Id_4_UnionId(114514)
CAN_Data = CAN_DATA()
