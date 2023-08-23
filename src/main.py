from C_DEFINE import *


from main_ui_logic import MainWindow


class MainAPP(MainWindow):
    def __init__(self):
        super().__init__()
        # 调试页面的按钮绑定
        MainUI.tabWidget.currentChanged.connect(self.tabwiget_get)
        # MainUI.sset_btn_open.clicked.connect(self.port_detect)
        MainUI.sset_btn_open.clicked.connect(self.port_open_switch)  # 开关串口时设置并发送一次
        MainUI.App_Lock.clicked.connect(self.top_lock_unlock)
        MainUI.sset_cb_baud.currentIndexChanged.connect(self.sys_boud_change)  # 改变波特率
        MainUI.sset_cb_choose.currentIndexChanged.connect(self.sys_choose_change)  # 改变端口号
        MainUI.pushButton_1.clicked.connect(self.Uart_send_key_down)  # 发送按钮
        MainUI.App_Quit.clicked.connect(QApplication.instance().quit)  # 软件退出按钮
        # 烧录页面的绑定
        MainUI.BL_openfile.clicked.connect(self.getpath)  # 选取烧录文件
        MainUI.BL_path.currentIndexChanged.connect(self.getpath4BLpath)  # 选取烧录文件
        MainUI.BL_download.clicked.connect(self.CAN_BL_Start_Set)  # 开启下载流程
        MainUI.App_Quit_2.clicked.connect(QApplication.instance().quit)  # 软件退出按钮
        # CAN页面的绑定
        MainUI.CAN_Set_V.blockCountChanged.connect(self.CAN_DC_CAN_Set_V_blockChanged)  # 输入电压输入框，回车触发函数
        MainUI.CAN_Set_Souce_I.blockCountChanged.connect(
            self.CAN_DC_CAN_Set_Souce_I_blockChanged)  # 输入电压输入框，回车触发函数
        MainUI.CAN_Set_Souce_P.blockCountChanged.connect(
            self.CAN_DC_CAN_Set_Souce_P_blockChanged)  # 输入电压输入框，回车触发函数
        MainUI.CAN_Set_Load_I.blockCountChanged.connect(self.CAN_DC_CAN_Set_Load_I_blockChanged)  # 输入电压输入框，回车触发函数
        MainUI.CAN_Set_Load_P.blockCountChanged.connect(self.CAN_DC_CAN_Set_Load_P_blockChanged)  # 输入电压输入框，回车触发函数
        MainUI.CAN_Device_ON.clicked.connect(self.CAN_DC_set_cmd_send_CTRL_CMD_OUT_ON)  # 设备开机按钮
        MainUI.CAN_Device_OFF.clicked.connect(self.CAN_DC_set_cmd_send_CTRL_CMD_OUT_OFF)  # 设备关机按钮
        MainUI.CAN_Setting_Sync.clicked.connect(self.task_CAN.CAN_DC_inquire_state_2_send)  # 同步设置参数
        MainUI.CAN_V_Send.clicked.connect(self.CAN_DC_set_cmd_send_KEYBOARD_SET_OUTPUT_VOLTAGE)  # 发送输出电压按钮
        MainUI.CAN_Souce_I_Send.clicked.connect(self.CAN_DC_set_cmd_send_KEYBOARD_SET_SOURCE_CURRENT)  # 发送源电流按钮
        MainUI.CAN_Souce_P_Send.clicked.connect(self.CAN_DC_set_cmd_send_KEYBOARD_SET_SOURCE_POWER)  # 发送源功率按钮
        MainUI.CAN_Load_I_Send.clicked.connect(self.CAN_DC_set_cmd_send_KEYBOARD_SET_LOAD_CURRENT)  # 发送载电流按钮
        MainUI.CAN_Load_P_Send.clicked.connect(self.CAN_DC_set_cmd_send_KEYBOARD_SET_LOAD_POWER)  # 发送载功率按钮
        MainUI.CAN_SCPI_Send.clicked.connect(self.CAN_SCPI_send_KIND_EXTERNAL_SCPI)  # 发送SCPI按钮
        MainUI.App_Quit_3.clicked.connect(QApplication.instance().quit)  # 软件退出按钮
        # ---->弹窗对象信号绑定
        MessageOpen.Message_Task_PopUp_signal.connect(self.QMessageBox_come_from_thread)
        # <----


if __name__ == '__main__':

    mainw = MainAPP()
    mainw.show()
    sys.exit(app.exec_())
