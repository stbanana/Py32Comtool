# 所有使用的模块在此引入
# ---->以下为依赖库，IDE有BUG导致报错
import os
import functools
import threading
from pylab import *
from enum import Enum
# <----
# ---->数学库
import math
#<----
# ---->多任务
import gevent
from gevent import monkey

monkey.patch_all()
# ---->串口相关
import serial
import serial.tools.list_ports
# <----
# ---->界面相关
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt, QCoreApplication, QThread, pyqtSignal, QMetaObject, QObject, pyqtSlot, QMetaObject
from PyQt5.QtGui import QTextCursor  # , QKeyEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QLabel, QComboBox, \
    QPushButton  # QGridLayout，  QStyleFactory
from PyQt5.QtWidgets import QFileDialog
from main_ui import Ui_MainWindow
# <----
import struct
import ctypes
from PY4CAdapt import *

# matplotlib模块必须单独引入
import matplotlib

matplotlib.use('Qt5Agg')  # 使用 matplotlib中的FigureCanvas (在使用 Qt5 Backends中 FigureCanvas继承自QtWidgets.QWidget)
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

# QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
app = QApplication([])  # app队列对象

# ---->以下.py文件 为避免重复导入的问题 按需复制并导入
# from Test_CAN import *
# from CANData import *


# <----

# 以下五个 爱泰CAN盒的包内结构-->
# c_uint UINT; c_byte BYTE; c_ulong DWORD; c_ubyte UCHAR
class VCI_CAN_OBJ(ctypes.Structure):  # 传输的CAN帧结构
    _fields_ = [
        ('ID', ctypes.c_uint),
        ('TimeStamp', ctypes.c_uint),
        ('TimeFlag', ctypes.c_byte),
        ('SendType', ctypes.c_byte),
        ('RemoteFlag', ctypes.c_byte),
        ('ExternFlag', ctypes.c_byte),
        ('DataLen', ctypes.c_byte),
        ('Data', ctypes.c_ubyte * 8),
        ('Reserved', ctypes.c_byte * 3)
    ]


class VCI_INIT_CONFIG(ctypes.Structure):
    _fields_ = [
        ('AccCode', ctypes.c_ulong),
        ('AccMask', ctypes.c_ulong),
        ('Reserved', ctypes.c_ulong),
        ('Filter', ctypes.c_ubyte),
        ('Timing0', ctypes.c_ubyte),
        ('Timing1', ctypes.c_ubyte),
        ('Mode', ctypes.c_ubyte),
    ]


class VCI_BOARD_INFO(ctypes.Structure):  # 包含CAN系列接口卡的设备信息
    _fields_ = [
        ('hw_Version', ctypes.c_ushort),
        ('fw_Version', ctypes.c_ushort),
        ('dr_Version', ctypes.c_ushort),
        ('in_Version', ctypes.c_ushort),
        ('irq_Num', ctypes.c_ushort),
        ('can_Num', ctypes.c_ubyte),
        ('str_Serial_Num', ctypes.c_byte * 20),
        ('str_hw_Type', ctypes.c_byte * 40),
        ('Reserved', ctypes.c_ushort * 4)
    ]


class VCI_ERR_INFO(ctypes.Structure):
    _fields_ = [
        ('ErrCode', ctypes.c_uint),
        ('Passive_ErrData', ctypes.c_byte * 3),
        ('ArLost_ErrData', ctypes.c_byte)
    ]


class VCI_CAN_STATUS(ctypes.Structure):
    _fields_ = [
        ('ErrInterrupt', ctypes.c_ubyte),
        ('regMode', ctypes.c_ubyte),
        ('regStatus', ctypes.c_ubyte),
        ('regALCapture', ctypes.c_ubyte),
        ('regECCapture', ctypes.c_ubyte),
        ('regEWLimit', ctypes.c_ubyte),
        ('regRECounter', ctypes.c_ubyte),
        ('regTECounter', ctypes.c_ubyte),
        ('Reserved', ctypes.c_ulong)
    ]


# 一个CAN协议 在C中的宏定义的复制-->
class CAN_C_DEFINE:
    def __init__(self):
        pass

    cACK = 0x06
    cERRERASE = 0x60
    cERRPROGRAM = 0x61
    cERRADDRESS = 0x62
    cERRCHECKSUM = 0x63
    cNAK = 0x15

    # 缺省填充
    Parameter_Default = 0x00
    # ②Rx_Message(6bits):收件方
    RX_OBJECT_ECU = 0x01
    RX_OBJECT_INV = 0x02
    RX_OBJECT_REC = 0x04
    RX_OBJECT_BPS = 0x08
    RX_OBJECT_MON = 0x10
    RX_OBJECT_UPP = 0x20

    # ③Kind(8bits):数据类型
    KIND_INQUIRE_STATE = 0x01  # 查询状态命令
    KIND_INQUIRE_REVISE = 0x02  # 查询校正参数
    KIND_SET = 0x05  # 设置命令
    KIND_REVISE = 0x06  # 校正命令
    KIND_SYNC = 0x07  # 同步命令
    KIND_MON_DATA = 0x08  # 监控数据命令
    KIND_INQUIRE_VAR = 0x09  # 查询变量命令
    KIND_EXTERNAL_SCPI = 0x0A  # 外部SCPI

    KIND_ANS_STATE = 0xA1  # 应答查询状态命令
    KIND_ANS_REVISE = 0xA2  # 应答查询校正命令
    KIND_ANS_VAR = 0xA9  # 应答查询变量命令
    KIND_ANS_SCPI = 0xAA  # 应答SCPI


    KIND_FLASH_REC_M = 0xFA  # 烧录命令:命令REC烧录主机(APP)
    KIND_FLASH_INV_M = 0xFB  # 烧录命令:命令INV烧录主机(APP)
    KIND_FLASH_ECU_M = 0xFC  # 烧录命令:命令ECU烧录主机(APP)
    KIND_FLASH_BPS_M = 0xFD  # 烧录命令:命令BPS烧录主机(APP)
    KIND_FLASH_MON_M = 0xFF  # 烧录命令:命令MON烧录主机(APP)

    KIND_FLASH_M = KIND_FLASH_INV_M

    KIND_FLASH_REC_S = 0xF1  # 烧录命令:命令REC烧录从机(APP)
    KIND_FLASH_INV_S = 0xF2  # 烧录命令:命令INV烧录从机(APP)
    KIND_FLASH_ECU_S = 0xF9  # 烧录命令:命令ECU烧录从机(APP)
    KIND_FLASH_BPS_S = 0xFE  # 烧录命令:命令BPS烧录从机(APP)

    KIND_FLASH_S = KIND_FLASH_INV_S

    KIND_FLASH_INFO = 0xF3  # 烧录命令:统计烧录台数命令(BOOTLOADER)
    KIND_FLASH_FAT = 0xF4  # 烧录命令:擦除数据命令(BOOTLOADER)
    KIND_FLASH_BURN = 0xF5  # 烧录命令:烧录数据命令(BOOTLOADER)
    KIND_FLASH_ANS_INFO = 0xF6  # 烧录命令:应答统计烧录台数命令(BOOTLOADER)
    KIND_FLASH_CHEC = 0xF7  # 烧录命令:烧录的地址数据长度数据校验和信息(BOOTLOADER)
    KIND_FLASH_ANS_RESET = 0xF8  # 烧录命令:应答烧录结束重启芯片，跳转APP(BOOTLOADER)

    # ④Tx_Message（3Bits）:寄件方
    TX_OBJECT_ECU = 0x00
    TX_OBJECT_INV = 0x01
    TX_OBJECT_REC = 0x02
    TX_OBJECT_BPS = 0x03
    TX_OBJECT_MON = 0x04
    TX_OBJECT_UPP = 0x05


# <--
# KIND_SET的cmd枚举
class CanControlCmdDef:
    def __init__(self):
        pass

    CTRL_CMD_EE_GridStd = 0x01  # 系统指令，data[3]标识指令,设定模式
    CTRL_CMD_OUT_ON = 0x02  # 开启输出
    CTRL_CMD_OUT_OFF = 0x03  # 关闭输出
    CTRL_CMD_FAULT_CLEAR = 0x04  # 故障清除
    #      CTRL_CMD_BATT_CHECK          #  电池自检
    #      CTRL_CMD_CANCEL_BATT_CHECK   #  取消电池自检
    #      CTRL_CMD_CHARGER_FORCE_BOOST #  强制均充命令
    #      CTRL_CMD_CHARGER_FORCE_FLOAT  #  强制浮充命令

    KEYBOARD_SET_OUTPUT_VOLTAGE = 0X11  # 小键盘设置输出电压
    KEYBOARD_SET_LOAD_CURRENT = 0X12  # 小键盘设置载电流
    KEYBOARD_SET_LOAD_POWER = 0X13  # 载功率设置
    KEYBOARD_SET_SOURCE_CURRENT = 0X14  # 小键盘设置源电流
    KEYBOARD_SET_SOURCE_POWER = 0X15  # 源功率设置

    KEYBOARD_SET_VOLTAGE_SLEW_RATE = 0X21  # 小键盘设置电压压摆率
    KEYBOARD_SET_CURRENT_SLEW_RATE = 0X22  # 小键盘设置电压压摆率
    KEYBOARD_SET_OVER_VOLTAGE_PROTECTION = 0X23  # 小键盘设置过电压保护点
    KEYBOARD_SET_SOURCE_OCP = 0X24  # 小键盘设置源模式过流保护点
    KEYBOARD_SET_SOURCE_OPP = 0X25  # 小键盘设置源模式过功率保护点
    KEYBOARD_SET_LOAD_OCP = 0X26  # 小键盘设置载模式过流保护点
    KEYBOARD_SET_LOAD_OPP = 0X27  # 小键盘设置载模式过功率保护点
    KEYBOARD_SET_DC_ON = 0x28  # 小键盘设置DC_ON的上升点及下降点


# Inv数据结构
class InvDataTypeDef:
    def __init__(self):
        self.BatVolt = 0  # 输出电压  （单位:0.01V）
        self.BatCurr = 0  # 输出电流  （单位:0.001A）


# 设置参数的数据结构
class stDCUserSetData:
    def __init__(self):
        self.OutputVoltage = 0  # 设置输出电压0.01v         存入时*100
        self.LoadCurrent = 0  # 设置输出载电流0.001A        存入时*1000
        self.LoadPower = 0  # 设置输出载功率1w
        self.SourceCurrent = 0  # 设置输出源电流0.001A        存入时*1000
        self.SourcePower = 0  # 设置输出源功率1w


def list_to_hex_string(list_data):
    list_str = '['
    for x in list_data:
        list_str += '0x{:02X},'.format(x)  # 转换成十六进制并大写
    list_str = list_str[:-1]  # 最后一个',' 不取
    list_str += ']'
    return list_str


class MessageOpenFunc(QObject):
    def __init__(self, parent=None):
        super(MessageOpenFunc, self).__init__(parent)
        self.MessageBox_Flag = 0  # 弹窗管理：0不弹窗 1消息弹窗 2可能风险弹窗 3.警告弹窗
        self.MessageTitle = ''
        self.MessageStr = ''

    Message_Task_PopUp_signal = pyqtSignal()  # CAN任务弹窗信号

    def ui_warning(self, MessageTitle, MessageStr):
        self.MessageBox_Flag = 3
        self.MessageTitle = MessageTitle
        self.MessageStr = MessageStr
        self.Message_Task_PopUp_signal.emit()

    def ui_critical(self, MessageTitle, MessageStr):
        self.MessageBox_Flag = 2
        self.MessageTitle = MessageTitle
        self.MessageStr = MessageStr
        self.Message_Task_PopUp_signal.emit()

    def ui_CloseInformation(self, MessageTitle, MessageStr):
        self.MessageBox_Flag = 1
        self.MessageTitle = MessageTitle
        self.MessageStr = MessageStr
        self.Message_Task_PopUp_signal.emit()


class SYS_CONTROLLER:
    def __init__(self):
        self.Test_CAN_BL_Start = 0  # 控制是否启用了CAN的流程，避免重复启用
        self.Test_CAN_SCPI_Start = 0  # 控制是否启用了SCPI发送的流程，避免重复启用

        self.filetype = ''  # 选取的烧录文件
        self.BL_flie_path_route = "./"  # bin文件路径


Sys_Controller = SYS_CONTROLLER()  # 系统控制对象
DC_User_Set_Data = stDCUserSetData()  # DC源设置参数对象
MainUI = Ui_MainWindow()  # UI主窗口对象
MessageOpen = MessageOpenFunc()  # UI弹窗管理
