from C_DEFINE import *
from CANData import *


# noinspection PyBroadException
def itekon_can_open():
    try:  # 尝试打开CAN盒
        # 加载dll动态库 依赖库kerneldlls 需要放置到python二进制文件目录中。
        # 关闭设备
        print(CAN_Data.ItekonCan.VCI_CloseDevice(4, 0))
        QThread.msleep(10)
        # 打开设备
        if CAN_Data.ItekonCan.VCI_OpenDevice(4, 0, 0) == 0:
            MessageOpen.ui_critical('Open Port Error', 'CAN盒不能正常打开！')
            return 0
        # 初始化can通道
        CAN_Data.ItekonCan.VCI_InitCAN(4, 0, 0, CAN_Data.init_config_c)
        CAN_Data.ItekonCan.VCI_InitCAN(4, 0, 1, CAN_Data.init_config_c)
        # 启动can通道
        CAN_Data.ItekonCan.VCI_StartCAN(4, 0, 0)
        CAN_Data.ItekonCan.VCI_StartCAN(4, 0, 1)
        return 1

    except:
        Sys_Controller.MessageBox_Flag = 2
        Sys_Controller.MessageTitle = 'Open Port Error'
        Sys_Controller.MessageStr = 'CAN盒不能正常打开！'
        return 0


class TaskCAN(QObject):
    def __init__(self, parent=None):
        super(TaskCAN, self).__init__(parent)
        self.CAN_SCPI_Data = CAN_DATA()
        self.Out_Data_Def = InvDataTypeDef()

    Task_CAN_Switch_tabWidget_signal = pyqtSignal(int)  # CAN任务发出的切换页面信号

    BL_Statu_update_signal = pyqtSignal(str)  # BL信息更新信号
    BL_Statu_setdata_signal = pyqtSignal(str)  # BL信息设定信号
    BL_Progress_update_signal = pyqtSignal(int)  # BL进度更新信号
    label_CAN_update_signal = pyqtSignal(str)  # 更新CAN页面左上角状态标签
    CAN_Set_V_update_signal = pyqtSignal(str)  # 更新CAN页面设置输出电压值
    CAN_Set_Souce_I_update_signal = pyqtSignal(str)  # 更新CAN设置源电流值
    CAN_Set_Souce_P_update_signal = pyqtSignal(str)  # 更新CAN设置源功率值
    CAN_Set_Load_I_update_signal = pyqtSignal(str)  # 更新CAN设置载电流值
    CAN_Set_Load_P_update_signal = pyqtSignal(str)  # 更新CAN设置载功率值

    CAN_Output_V_Show_update_signal = pyqtSignal(str)  # 更新CAN页面电压值
    CAN_Output_I_Show_update_signal = pyqtSignal(str)  # 更新CAN页面电流值
    CAN_Output_P_Show_update_signal = pyqtSignal(str)  # 更新CAN页面功率值
    SCPI_Statu_update_signal = pyqtSignal(str)  # 更新CAN SCPI状态简览

    def run(self):
        while True:
            self.CAN_BL_Check()
            self.CAN_SCPI_Check()
            QThread.msleep(1)

    def CAN_BL_Check(self):
        if Sys_Controller.Test_CAN_BL_Start == 1:  # 烧录事件仅触发一次
            self.bl_process_open()
            Sys_Controller.Test_CAN_BL_Start = 0
            return

    def CAN_SCPI_Check(self):
        if Sys_Controller.Test_CAN_SCPI_Start == 1:  # 烧录事件仅触发一次
            self.scpi_process_open()
            Sys_Controller.Test_CAN_SCPI_Start = 0
            return

    def send_data_th_dsp(self, bl_Step):  # 选定流程发送
        CAN_Data.send_msg.ID = 0xFFFFFFFF
        CAN_Data.send_msg.DataLen = 8
        CAN_Data.send_msg.Data[0] = 0x00
        CAN_Data.send_msg.Data[1] = 0x00
        CAN_Data.send_msg.Data[2] = 0x00
        CAN_Data.send_msg.Data[3] = 0x00
        CAN_Data.send_msg.Data[4] = 0x00
        CAN_Data.send_msg.Data[5] = 0x00
        CAN_Data.send_msg.Data[6] = 0x00
        CAN_Data.send_msg.Data[7] = 0x00  # CAN包初始化
        if bl_Step == 1:  # 跳转包 发送参数定义
            CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
            CAN_Data.send_msg.Data[0] = 0x00
            CAN_Data.send_msg.Data[1] = 0x01
        elif bl_Step == 2:  # 连接包 发送参数定义
            CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
            CAN_Data.send_msg.Data[0] = 0x00
            CAN_Data.send_msg.Data[1] = 0x02
        elif bl_Step == 3:  # 程序数据包 发送参数定义  MCU进行擦除
            CAN_Data.bl_step = CAN_C_DEFINE.KIND_FLASH_FAT  # 寄存当前流程的bKind
            CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
            CAN_Data.send_msg.Data[0] = (CAN_Data.BL_ADDR_START & 0xFF)
            CAN_Data.send_msg.Data[1] = (CAN_Data.BL_ADDR_START & 0xFF00) >> 8
            CAN_Data.send_msg.Data[2] = (CAN_Data.BL_ADDR_START & 0xFF0000) >> 16
            CAN_Data.send_msg.Data[3] = (CAN_Data.BL_ADDR_START & 0xFF000000) >> 24
            CAN_Data.send_msg.Data[4] = (CAN_Data.BL_CounterLen & 0xFF000000) >> 24
            CAN_Data.send_msg.Data[5] = (CAN_Data.BL_CounterLen & 0xFF0000) >> 16
            CAN_Data.send_msg.Data[6] = (CAN_Data.BL_CounterLen & 0xFF00) >> 8
            CAN_Data.send_msg.Data[7] = (CAN_Data.BL_CounterLen & 0xFF)
        elif bl_Step == 4:  # 定义包 发送起始地址和程序大小
            CAN_Data.verify_data_send_pause = 0
            CAN_Data.bl_step = CAN_C_DEFINE.KIND_FLASH_CHEC  # 寄存当前流程的bKind
            CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
            CAN_Data.send_msg.Data[0] = ((CAN_Data.BL_ADDR_START + (
                    CAN_Data.bl_packa_num_past * 0x8)) & 0xFF000000) >> 24
            CAN_Data.send_msg.Data[1] = ((CAN_Data.BL_ADDR_START + (CAN_Data.bl_packa_num_past * 0x8)) & 0xFF0000) >> 16
            CAN_Data.send_msg.Data[2] = ((CAN_Data.BL_ADDR_START + (CAN_Data.bl_packa_num_past * 0x8)) & 0xFF00) >> 8
            CAN_Data.send_msg.Data[3] = ((CAN_Data.BL_ADDR_START + (CAN_Data.bl_packa_num_past * 0x8)) & 0xFF)
            CAN_Data.verify_data = b''
            up_file = open(Sys_Controller.filetype, 'rb')  # 打开文件
            up_file.seek(CAN_Data.bl_counter_len_past, 0)  # 从起始位置即文件首行首字符开始移动 x 个字符
            if (CAN_Data.bl_packa_num - CAN_Data.bl_packa_num_past) > 128:
                CAN_Data.bl_data_verify = 0
                CAN_Data.verify_data = up_file.read(1024)
                for verify_cnt in range(1024):
                    CAN_Data.bl_data_verify += CAN_Data.verify_data[verify_cnt]
                    CAN_Data.bl_data_verify &= 0xFFFF
                    if CAN_Data.verify_data[verify_cnt] != 0xFF:
                        CAN_Data.verify_data_send_pause = 1
                CAN_Data.send_msg.Data[4] = (CAN_Data.bl_data_verify & 0xFF00) >> 8
                CAN_Data.send_msg.Data[5] = (CAN_Data.bl_data_verify & 0xFF)
                CAN_Data.send_msg.Data[6] = (0x400 & 0xFF00) >> 8
                CAN_Data.send_msg.Data[7] = (0x400 & 0xFF)
            else:
                CAN_Data.bl_data_verify = 0
                CAN_Data.verify_data = up_file.read(CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past)
                for verify_cnt in range(CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past):
                    CAN_Data.bl_data_verify += CAN_Data.verify_data[verify_cnt]
                    CAN_Data.bl_data_verify &= 0xFFFF
                    if CAN_Data.verify_data[verify_cnt] != 0xFF:
                        CAN_Data.verify_data_send_pause = 1
                CAN_Data.send_msg.Data[4] = (CAN_Data.bl_data_verify & 0xFF00) >> 8
                CAN_Data.send_msg.Data[5] = (CAN_Data.bl_data_verify & 0xFF)
                CAN_Data.send_msg.Data[6] = (((CAN_Data.bl_packa_num - CAN_Data.bl_packa_num_past) * 8) & 0xFF00) >> 8
                CAN_Data.send_msg.Data[7] = (((CAN_Data.bl_packa_num - CAN_Data.bl_packa_num_past) * 8) & 0xFF)
        elif bl_Step == 5:  # 数据包 填充程序数据
            CAN_Data.bl_step = CAN_C_DEFINE.KIND_FLASH_BURN  # 寄存当前流程的bKind
            CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
            if CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past >= 8:
                for pack_num in range(8):
                    CAN_Data.send_msg.Data[pack_num] = CAN_Data.flash_data[pack_num]
                    # if pack_num >= 4:
                    #     send_msg.Data[pack_num] = CAN_Data.flash_data[7 - (pack_num % 4)]
                    # else:
                    #     send_msg.Data[pack_num] = CAN_Data.flash_data[3 - pack_num % 4]
            else:
                # CAN_Data.send_msg.DataLen = CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past
                for pack_num in range(CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past):
                    CAN_Data.send_msg.Data[pack_num] = CAN_Data.flash_data[pack_num]
                #     if pack_num >= 4:
                #         send_msg.Data[pack_num] = CAN_Data.flash_data[7 - (pack_num % 4)]
                #     else:
                #         send_msg.Data[pack_num] = CAN_Data.flash_data[3 - pack_num % 4]
        elif bl_Step == 6:  # 结束包 重启跳入程序
            CAN_Data.bl_step = CAN_C_DEFINE.KIND_FLASH_ANS_RESET  # 寄存当前流程的bKind
            CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
            CAN_Data.send_msg.Data[0] = 0x00
            CAN_Data.send_msg.Data[1] = 0x06
            CAN_Data.ItekonCan.VCI_Transmit(4, 0, 0, CAN_Data.send_msg_c, 1)
        # 发送函数
        if CAN_Data.verify_data_send_pause == 0:
            return 1
        ret = CAN_Data.ItekonCan.VCI_Transmit(4, 0, 0, CAN_Data.send_msg_c, 1)  # 此函数见CAN盒API
        if ret == 0:
            MessageOpen.ui_critical('Error', '有一次发送失败了！检查总线')
            return 0
        else:
            return 1

    def send_data_th_tm4c(self, bl_Step):  # 选定流程发送
        try:
            CAN_Data.send_msg.ID = 0xFFFFFFFF
            CAN_Data.send_msg.DataLen = 8
            CAN_Data.send_msg.Data[0] = 0x00
            CAN_Data.send_msg.Data[1] = 0x00
            CAN_Data.send_msg.Data[2] = 0x00
            CAN_Data.send_msg.Data[3] = 0x00
            CAN_Data.send_msg.Data[4] = 0x00
            CAN_Data.send_msg.Data[5] = 0x00
            CAN_Data.send_msg.Data[6] = 0x00
            CAN_Data.send_msg.Data[7] = 0x00  # CAN包初始化
            if bl_Step == 1:  # 跳转包 发送参数定义
                CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
                CAN_Data.send_msg.Data[0] = 0x00
                CAN_Data.send_msg.Data[1] = 0x01
            elif bl_Step == 2:  # 连接包 发送参数定义
                CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
                CAN_Data.send_msg.Data[0] = 0x00
                CAN_Data.send_msg.Data[1] = 0x02
            elif bl_Step == 3:  # 程序数据包 发送参数定义  MCU进行擦除
                CAN_Data.bl_step = CAN_C_DEFINE.KIND_FLASH_FAT  # 寄存当前流程的bKind
                CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
                CAN_Data.send_msg.Data[0] = (CAN_Data.BL_ADDR_START & 0xFF)
                CAN_Data.send_msg.Data[1] = (CAN_Data.BL_ADDR_START & 0xFF00) >> 8
                CAN_Data.send_msg.Data[2] = (CAN_Data.BL_ADDR_START & 0xFF0000) >> 16
                CAN_Data.send_msg.Data[3] = (CAN_Data.BL_ADDR_START & 0xFF000000) >> 24
                CAN_Data.send_msg.Data[4] = (CAN_Data.BL_CounterLen & 0xFF)
                CAN_Data.send_msg.Data[5] = (CAN_Data.BL_CounterLen & 0xFF00) >> 8
                CAN_Data.send_msg.Data[6] = (CAN_Data.BL_CounterLen & 0xFF0000) >> 16
                CAN_Data.send_msg.Data[7] = (CAN_Data.BL_CounterLen & 0xFF000000) >> 24
            elif bl_Step == 4:  # 定义包 发送起始地址和程序大小
                CAN_Data.verify_data_send_pause = 0
                CAN_Data.bl_step = CAN_C_DEFINE.KIND_FLASH_CHEC  # 寄存当前流程的bKind
                CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
                CAN_Data.send_msg.Data[0] = ((CAN_Data.BL_ADDR_START + (CAN_Data.bl_packa_num_past * 0x8)) & 0xFF)
                CAN_Data.send_msg.Data[1] = ((CAN_Data.BL_ADDR_START + (
                        CAN_Data.bl_packa_num_past * 0x8)) & 0xFF00) >> 8
                CAN_Data.send_msg.Data[2] = ((CAN_Data.BL_ADDR_START + (
                        CAN_Data.bl_packa_num_past * 0x8)) & 0xFF0000) >> 16
                CAN_Data.send_msg.Data[3] = ((CAN_Data.BL_ADDR_START + (
                        CAN_Data.bl_packa_num_past * 0x8)) & 0xFF000000) >> 24
                CAN_Data.verify_data = b''
                up_file = open(Sys_Controller.filetype, 'rb')  # 打开文件
                up_file.seek(CAN_Data.bl_counter_len_past, 0)  # 从起始位置即文件首行首字符开始移动 x 个字符
                if (CAN_Data.bl_packa_num - CAN_Data.bl_packa_num_past) > 128:
                    CAN_Data.bl_data_verify = 0
                    CAN_Data.verify_data = up_file.read(1024)
                    for verify_cnt in range(1024):
                        CAN_Data.bl_data_verify += CAN_Data.verify_data[verify_cnt]
                        CAN_Data.bl_data_verify &= 0xFFFF
                        if CAN_Data.verify_data[verify_cnt] != 0xFF:
                            CAN_Data.verify_data_send_pause = 1
                    CAN_Data.send_msg.Data[4] = (CAN_Data.bl_data_verify & 0xFF)
                    CAN_Data.send_msg.Data[5] = (CAN_Data.bl_data_verify & 0xFF00) >> 8
                    CAN_Data.send_msg.Data[6] = (0x400 & 0xFF)
                    CAN_Data.send_msg.Data[7] = (0x400 & 0xFF00) >> 8
                else:
                    CAN_Data.bl_data_verify = 0
                    CAN_Data.verify_data = up_file.read(CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past)
                    for verify_cnt in range(CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past):
                        CAN_Data.bl_data_verify += CAN_Data.verify_data[verify_cnt]
                        CAN_Data.bl_data_verify &= 0xFFFF
                        if CAN_Data.verify_data[verify_cnt] != 0xFF:
                            CAN_Data.verify_data_send_pause = 1
                    CAN_Data.send_msg.Data[4] = (CAN_Data.bl_data_verify & 0xFF)
                    CAN_Data.send_msg.Data[5] = (CAN_Data.bl_data_verify & 0xFF00) >> 8
                    CAN_Data.send_msg.Data[6] = (((CAN_Data.bl_packa_num - CAN_Data.bl_packa_num_past) * 8) & 0xFF)
                    CAN_Data.send_msg.Data[7] = (((
                                                          CAN_Data.bl_packa_num - CAN_Data.bl_packa_num_past) * 8) & 0xFF00) >> 8
            elif bl_Step == 5:  # 数据包 填充程序数据
                CAN_Data.bl_step = CAN_C_DEFINE.KIND_FLASH_BURN  # 寄存当前流程的bKind
                CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
                if CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past >= 8:
                    for pack_num in range(8):
                        CAN_Data.send_msg.Data[pack_num] = CAN_Data.flash_data[pack_num]
                        # if pack_num >= 4:
                        #     send_msg.Data[pack_num] = CAN_Data.flash_data[7 - (pack_num % 4)]
                        # else:
                        #     send_msg.Data[pack_num] = CAN_Data.flash_data[3 - pack_num % 4]
                else:
                    # CAN_Data.send_msg.DataLen = CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past
                    for pack_num in range(CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past):
                        CAN_Data.send_msg.Data[pack_num] = CAN_Data.flash_data[pack_num]
                    CAN_Data.send_msg.DataLen = CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past
                    #     if pack_num >= 4:
                    #         send_msg.Data[pack_num] = CAN_Data.flash_data[7 - (pack_num % 4)]
                    #     else:
                    #         send_msg.Data[pack_num] = CAN_Data.flash_data[3 - pack_num % 4]
            elif bl_Step == 6:  # 结束包 重启跳入程序
                CAN_Data.bl_step = CAN_C_DEFINE.KIND_FLASH_ANS_RESET  # 寄存当前流程的bKind
                CAN_Data.send_msg.ID = CAN_Data.BL_tx_arb_id + (CAN_Data.bl_step << 16)
                CAN_Data.send_msg.Data[0] = 0x00
                CAN_Data.send_msg.Data[1] = 0x06
                CAN_Data.ItekonCan.VCI_Transmit(4, 0, 0, CAN_Data.send_msg_c, 1)
            # 发送函数
            if CAN_Data.verify_data_send_pause == 0:
                return 1
            ret = CAN_Data.ItekonCan.VCI_Transmit(4, 0, 0, CAN_Data.send_msg_c, 1)  # 此函数见CAN盒API
            if ret == 0:
                MessageOpen.ui_critical('Error', '有一次发送失败了！检查总线')
                return 0
            else:
                return 1
        except IOError:
            return 0

    # BL中的接收数据
    # noinspection PyBroadException
    def bl_rx_statu(self):
        try:
            can_rx_num = 0
            can_norx_num = 0
            while can_rx_num == 0:
                can_rx_num = CAN_Data.ItekonCan.VCI_GetReceiveNum(4, 0, 0)
                can_norx_num += 1
                while can_rx_num != 0:
                    can_rx_num -= CAN_Data.ItekonCan.VCI_Receive(4, 0, 0, CAN_Data.recv_msg_c, 1, 0)  # 读一包
                    can_norx_num += 1
                    CAN_ID_State = 0

                    if MainUI.BL_path_object_cab.currentText() == '机柜广播' and MainUI.BL_path_object_model.currentText() == '模块广播':
                        if (CAN_Data.recv_msg.ID & 0x07FFFC00) == (CAN_Data.BL_rx_arb_id + (CAN_Data.bl_step << 16)):
                            CAN_ID_State = 1
                    elif MainUI.BL_path_object_cab.currentText() == '机柜广播':
                        if (CAN_Data.recv_msg.ID & 0x07FFFC3F) == (CAN_Data.BL_rx_arb_id + (CAN_Data.bl_step << 16)):
                            CAN_ID_State = 1
                    elif MainUI.BL_path_object_cab.currentText() == '模块广播':
                        if (CAN_Data.recv_msg.ID & 0x07FFFFC0) == (CAN_Data.BL_rx_arb_id + (CAN_Data.bl_step << 16)):
                            CAN_ID_State = 1
                    else:
                        if (CAN_Data.recv_msg.ID & 0x07FFFFFF) == (CAN_Data.BL_rx_arb_id + (CAN_Data.bl_step << 16)):
                            CAN_ID_State = 1

                    if CAN_ID_State == 1:
                        if hex(CAN_Data.recv_msg.Data[0] & 0xFF) == hex(CAN_Data.send_msg.Data[0] & 0xFF):
                            if hex(CAN_Data.recv_msg.Data[1] & 0xFF) == hex(CAN_Data.send_msg.Data[1] & 0xFF):
                                # MainUI.BL_Statu.insertPlainText()
                                # list_to_hex_string(list(CAN_Data.recv_msg.Data))  # bits转字符串显示
                                # MainUI.BL_Statu.moveCursor(QTextCursor.End)
                                if hex(CAN_Data.recv_msg.Data[3] & 0xFF) == hex(CAN_C_DEFINE.cACK) or hex(
                                        CAN_Data.recv_msg.Data[3] & 0xFF) == hex(CAN_C_DEFINE.cNAK):
                                    while not CAN_Data.ItekonCan.VCI_ClearBuffer(4, 0, 1):  # 确保清除缓冲区
                                        continue
                                    return 1
                                if hex(CAN_Data.recv_msg.Data[3] & 0xFF) == hex(CAN_C_DEFINE.cERRERASE):
                                    MessageOpen.ui_critical('Error', '有一次flash擦除失败了！')
                                    while not CAN_Data.ItekonCan.VCI_ClearBuffer(4, 0, 1):  # 确保清除缓冲区
                                        continue
                                    return 2
                                if hex(CAN_Data.recv_msg.Data[3] & 0xFF) == hex(CAN_C_DEFINE.cERRPROGRAM):
                                    MessageOpen.ui_critical('Error', '有一次数据写入失败了！')
                                    while not CAN_Data.ItekonCan.VCI_ClearBuffer(4, 0, 1):  # 确保清除缓冲区
                                        continue
                                    return 3
                                if hex(CAN_Data.recv_msg.Data[3] & 0xFF) == hex(CAN_C_DEFINE.cERRADDRESS):
                                    MessageOpen.ui_critical('Error', '有一次地址错误产生了！')
                                    while not CAN_Data.ItekonCan.VCI_ClearBuffer(4, 0, 1):  # 确保清除缓冲区
                                        continue
                                    return 4
                                if hex(CAN_Data.recv_msg.Data[3] & 0xFF) == hex(CAN_C_DEFINE.cERRCHECKSUM):
                                    MessageOpen.ui_critical('Error', '有一次校验错误产生了！')
                                    while not CAN_Data.ItekonCan.VCI_ClearBuffer(4, 0, 1):  # 确保清除缓冲区
                                        continue
                                    return 4
                    if ((CAN_Data.recv_msg.ID & 0x07FFFFFF) != (CAN_Data.BL_rx_arb_id + (CAN_Data.bl_step << 16))) and ((CAN_Data.recv_msg.ID & 0x07FFFFFF) == (CAN_Data.BL_rx_arb_id + (CAN_C_DEFINE.KIND_FLASH_INV_M << 16))):
                        if hex(CAN_Data.recv_msg.Data[2] & 0xFF) == hex(0x06):
                            can_norx_num = 0
                            continue  # 此处表明芯片在线且没收到BL流程的指令
                    if can_norx_num > 1000:
                        break
                QThread.msleep(1)
                if can_norx_num > 1000:
                    return 0
            return 0
        except:
            return 0

    # 开启BL流程
    # noinspection PyBroadException
    def bl_process_open(self):
        if itekon_can_open() == 0:
            return None
        try:
            up_file = open(Sys_Controller.filetype, 'rb')  # ''' rb : read bin file'''
        except:
            MessageOpen.ui_critical('Open file Error', '文件异常！')
            return 0
        up_file.seek(0)  # 文件光标移动到开头 28335
        file_indicate_1 = up_file.read(2)
        up_file.seek(0x4000)  # 文件光标移动到0x4000 28377
        file_indicate_2 = up_file.read(2)
        # 机柜号ID检测
        if MainUI.BL_path_object_cab.currentText() == '机柜广播':
            CabID = 0
        elif MainUI.BL_path_object_cab.currentText() == '机柜1':
            CabID = 1
        elif MainUI.BL_path_object_cab.currentText() == '机柜2':
            CabID = 2
        elif MainUI.BL_path_object_cab.currentText() == '机柜3':
            CabID = 3
        elif MainUI.BL_path_object_cab.currentText() == '机柜4':
            CabID = 4
        elif MainUI.BL_path_object_cab.currentText() == '机柜5':
            CabID = 5
        elif MainUI.BL_path_object_cab.currentText() == '机柜6':
            CabID = 6
        elif MainUI.BL_path_object_cab.currentText() == '机柜7':
            CabID = 7
        elif MainUI.BL_path_object_cab.currentText() == '机柜8':
            CabID = 8
        elif MainUI.BL_path_object_cab.currentText() == '机柜9':
            CabID = 9
        elif MainUI.BL_path_object_cab.currentText() == '机柜10':
            CabID = 10
        else:
            CabID = 0
        # 模块号ID检测
        if MainUI.BL_path_object_model.currentText() == '模块广播':
            ModelID = 0
        elif MainUI.BL_path_object_model.currentText() == '模块1':
            ModelID = 1
        elif MainUI.BL_path_object_model.currentText() == '模块2':
            ModelID = 2
        elif MainUI.BL_path_object_model.currentText() == '模块3':
            ModelID = 3
        elif MainUI.BL_path_object_model.currentText() == '模块4':
            ModelID = 4
        elif MainUI.BL_path_object_model.currentText() == '模块5':
            ModelID = 5
        elif MainUI.BL_path_object_model.currentText() == '模块6':
            ModelID = 6
        elif MainUI.BL_path_object_model.currentText() == '模块7':
            ModelID = 7
        elif MainUI.BL_path_object_model.currentText() == '模块8':
            ModelID = 8
        elif MainUI.BL_path_object_model.currentText() == '模块9':
            ModelID = 9
        elif MainUI.BL_path_object_model.currentText() == '模块10':
            ModelID = 10
        else:
            ModelID = 0

        if MainUI.BL_path_object.currentText() == 'REC':
            if file_indicate_1 != b'\xB0\xAA':
                MessageOpen.ui_critical('File Error', '选取的烧录文件不匹配！')
                return None
            CAN_Data.BL_tx_arb_id = id_bit_union(ModelID, CabID,
                                                 CAN_C_DEFINE.RX_OBJECT_REC, CAN_C_DEFINE.Parameter_Default,
                                                 CAN_C_DEFINE.TX_OBJECT_UPP, 0)
            CAN_Data.BL_rx_arb_id = id_bit_union(ModelID, CabID,
                                                 CAN_C_DEFINE.RX_OBJECT_UPP, CAN_C_DEFINE.Parameter_Default,
                                                 CAN_C_DEFINE.TX_OBJECT_REC, 0)
            CAN_Data.bl_step = CAN_C_DEFINE.KIND_FLASH_REC_M  # 跳转及握手包，此处初始化，完成跳转及握手，流程第三步再修改此变量
            CAN_Data.BL_ADDR_START = 0x300000
            CAN_Data.BL_ADDR_START_MAX = 0x370000
            # CAN_Data.bl_process_DSP()
            CAN_Data.bl_process = self.send_data_th_dsp  # 注册发送流程
        elif MainUI.BL_path_object.currentText() == 'INV':
            if (file_indicate_1 != b'\xB1\xAA') and (file_indicate_2 != b'\xB2\xAA'):
                MessageOpen.ui_critical('File Error', '选取的烧录文件不匹配！')
                return None
            CAN_Data.BL_tx_arb_id = id_bit_union(ModelID, CabID,
                                                 CAN_C_DEFINE.RX_OBJECT_INV, CAN_C_DEFINE.Parameter_Default,
                                                 CAN_C_DEFINE.TX_OBJECT_UPP, 0)
            CAN_Data.BL_rx_arb_id = id_bit_union(ModelID, CabID,
                                                 CAN_C_DEFINE.RX_OBJECT_UPP, CAN_C_DEFINE.Parameter_Default,
                                                 CAN_C_DEFINE.TX_OBJECT_INV, 0)
            CAN_Data.bl_step = CAN_C_DEFINE.KIND_FLASH_INV_M  # 跳转及握手包，此处初始化，完成跳转及握手，流程第三步再修改此变量
            CAN_Data.BL_ADDR_START = 0x300000
            CAN_Data.BL_ADDR_START_MAX = 0x370000
            # CAN_Data.bl_process_DSP()
            CAN_Data.bl_process = self.send_data_th_dsp
        elif MainUI.BL_path_object.currentText() == 'MON':
            CAN_Data.BL_tx_arb_id = id_bit_union(CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.Parameter_Default,
                                                 CAN_C_DEFINE.RX_OBJECT_MON, CAN_C_DEFINE.Parameter_Default,
                                                 CAN_C_DEFINE.TX_OBJECT_UPP, 0)
            CAN_Data.BL_rx_arb_id = id_bit_union(CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.Parameter_Default,
                                                 CAN_C_DEFINE.RX_OBJECT_UPP, CAN_C_DEFINE.Parameter_Default,
                                                 CAN_C_DEFINE.TX_OBJECT_MON, 0)
            CAN_Data.bl_step = CAN_C_DEFINE.KIND_FLASH_MON_M  # 跳转及握手包，此处初始化，完成跳转及握手，流程第三步再修改此变量
            CAN_Data.BL_ADDR_START = 0x4000
            CAN_Data.BL_ADDR_START_MAX = 0x40000000
            # CAN_Data.bl_process_TM4C()
            CAN_Data.bl_process = self.send_data_th_tm4c
        self.bl_process_step()

    def bl_process_step(self):
        bl_counter = 0  # 下载次数累计初始化
        CAN_Data.verify_data_send_pause = 1  # 有效包初始化
        # bl_flow_err_flag = 0  # 流程错误标志初始化
        if len(Sys_Controller.filetype) == 0:
            MessageOpen.ui_critical('Open file Error', '文件异常！')
            return None
        if CAN_Data.bl_process(1) == 0:  # 第一步，启用跳转至芯片BL
            return
        self.BL_Statu_update_signal.emit('跳转中')
        CAN_Data.BL_CounterLen = 0  # 文件大小清0
        up_file = open(Sys_Controller.filetype, 'rb')  # ''' rb : read bin file'''
        CAN_Data.BL_CounterLen = os.path.getsize(Sys_Controller.filetype)  # 获取下载文件的大小
        if CAN_Data.BL_CounterLen > (CAN_Data.BL_ADDR_START_MAX - CAN_Data.BL_ADDR_START):
            CAN_Data.BL_CounterLen = (CAN_Data.BL_ADDR_START_MAX - CAN_Data.BL_ADDR_START)
        CAN_Data.bl_packa_num = CAN_Data.BL_CounterLen // 8  # 计算需发送的包数
        if CAN_Data.BL_CounterLen % 8 != 0:
            CAN_Data.bl_packa_num += 1
        if self.bl_rx_statu() != 1:  # 接收回复数据 并检查ACK
            MessageOpen.ui_critical('Jump Error', '未正确跳转至BL程序！')
        QThread.msleep(1000)  # 跳转时需稍作等待
        if CAN_Data.bl_process(2) == 0:  # 第二步，发送连接包
            return
        self.BL_Statu_update_signal.emit('PING')
        if self.bl_rx_statu() != 1:  # 接收回复数据 并检查ACK
            bl_counter += 1
            MessageOpen.ui_critical('Ping Error', 'Ping失败！')
            return
        QThread.msleep(1000)  # 擦除前时需稍作等待
        while CAN_Data.bl_packa_num > 0:
            if bl_counter > 5:
                MessageOpen.ui_critical('BL Error', '烧录重试次数已过多！')
                return
            bl_flow_err_flag = 0
            CAN_Data.bl_packa_num_past = 0  # 已发数据包计数清0
            CAN_Data.bl_counter_len_past = 0  # 已发送数据清零
            if CAN_Data.bl_process(3) == 0:  # 第三步，发送程序数据擦除包
                return
            self.BL_Statu_update_signal.emit('正在擦除程序')
            if self.bl_rx_statu() != 1:  # 接收回复数据 并检查ACK
                bl_counter += 1
                continue
            up_file.seek(0)  # 文件光标移动到开头
            if self.bl_rx_statu() != 1:  # 接收回复数据 并检查ACK
                bl_counter += 1
                continue
            while CAN_Data.bl_packa_num_past < CAN_Data.bl_packa_num and bl_flow_err_flag == 0:
                # QMetaObject.invokeMethod(MainUI.BL_Progress, "setValue",
                #                          (int(CAN_Data.bl_packa_num_past / CAN_Data.bl_packa_num * 100),))
                # MainUI.BL_Progress.setValue(int(CAN_Data.bl_packa_num_past / CAN_Data.bl_packa_num * 100))
                self.BL_Progress_update_signal.emit(int(CAN_Data.bl_packa_num_past / CAN_Data.bl_packa_num * 100))
                if CAN_Data.bl_process(4) == 0:  # 第四步，发送多包数据参数包 当前每多包阶段均为1024个字节
                    return
                self.BL_Statu_update_signal.emit('正在发送第' + str(
                    int(math.floor(CAN_Data.bl_packa_num_past / 128))) + '包')
                if (CAN_Data.BL_ADDR_START + (CAN_Data.bl_packa_num_past * 0x4)) >= CAN_Data.BL_ADDR_START_MAX:
                    CAN_Data.bl_packa_num_past = CAN_Data.bl_packa_num
                    break
                # if CAN_Data.verify_data == CAN_Data.verify_data_empty:
                # CAN_Data.bl_counter_len_past += 8
                # CAN_Data.bl_packa_num_past += 1
                # continue
                if CAN_Data.verify_data_send_pause == 1:
                    if self.bl_rx_statu() != 1:  # 接收回复数据 并检查ACK
                        bl_counter += 1
                        continue
                while (CAN_Data.bl_packa_num - CAN_Data.bl_packa_num_past) > 0:  # 第五步，开始传输升级数据
                    read_addr = up_file.tell()  # 获取读开始地址
                    up_file.seek(read_addr, 0)  # 从起始位置即文件首行首字符开始移动 x 个字符
                    CAN_Data.flash_data = b''
                    if CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past >= 8:
                        CAN_Data.flash_data = up_file.read(8)
                    else:
                        CAN_Data.flash_data += up_file.read(CAN_Data.BL_CounterLen - CAN_Data.bl_counter_len_past)
                    if CAN_Data.verify_data_send_pause == 1:
                        if CAN_Data.bl_process(5) == 0:  # 发送数据包
                            return
                    CAN_Data.bl_counter_len_past += 8
                    CAN_Data.bl_packa_num_past += 1
                    if ((read_addr + 8) % 1024) == 0:
                        break
                if CAN_Data.verify_data_send_pause == 1:
                    if self.bl_rx_statu() != 1:  # 接收回复数据 并检查ACK
                        bl_counter += 1
                        # bl_flow_err_flag = 1
                        break
            if bl_flow_err_flag == 1:
                continue
            CAN_Data.bl_process(6)  # 第六步，结束传输
            if self.bl_rx_statu() != 1:  # 接收回复数据 并检查ACK
                bl_counter += 1
                continue
            MessageOpen.ui_CloseInformation('DL Succeed', '烧录成功')
            self.BL_Progress_update_signal.emit(0)
            self.BL_Statu_setdata_signal.emit("请选择正确的烧录对象和烧录文件，点击”下载“开始烧录")
            # QMetaObject.invokeMethod(MainUI.BL_Progress, "setValue",
            #                          (0,))
            # MainUI.BL_Progress.setValue(0)
            CAN_Data.ItekonCan.VCI_CloseDevice(4, 0)
            return 1

    # 开启SCPI发送流程
    def scpi_process_open(self):
        try:
            Send_Str = MainUI.CAN_SCPI_Text.toPlainText()
            Send_Str = Send_Str + "\r\n"
            Send_Hex = [ctypes.c_ubyte(ord(ch)) for ch in Send_Str]
            # Send_Hex = bytearray.fromhex(Send_Str)
            Str_Len = len(Send_Str)
            Send_Packa_Num = Str_Len // 8  # 计算需发送的包数
            if Str_Len % 8 != 0:
                Send_Packa_Num += 1
            self.CAN_SCPI_Data.send_msg.ID = id_bit_union(CAN_C_DEFINE.Parameter_Default,
                                                          CAN_C_DEFINE.Parameter_Default,
                                                          CAN_C_DEFINE.RX_OBJECT_MON, CAN_C_DEFINE.KIND_EXTERNAL_SCPI,
                                                          CAN_C_DEFINE.TX_OBJECT_UPP, 0)
            self.CAN_SCPI_Data.send_msg.DataLen = 8
            while Send_Packa_Num > 0:
                for i in range(8):
                    self.CAN_SCPI_Data.send_msg.Data[i] = 0
                    if Str_Len > 0:
                        self.CAN_SCPI_Data.send_msg.Data[i] = Send_Hex[len(Send_Str) - Str_Len]
                        Str_Len = Str_Len - 1
                ret = CAN_Data.ItekonCan.VCI_Transmit(4, 0, 0, self.CAN_SCPI_Data.send_msg_c, 1)  # 此函数见CAN盒API
                Send_Packa_Num = Send_Packa_Num - 1
                #                QThread.msleep(20)  # 每帧CAN包稍作释放避免卡死
                if ret == 0:
                    MessageOpen.ui_critical('Error', '有一次发送失败了！检查总线')
                    return 0
        except IOError:
            return 0

    # 参数设置CAN实现------------------>
    # noinspection PyBroadException
    def CAN_DC_inquire_state_1_send(self):
        CAN_Data.send_msg.ID = 0x5074000
        CAN_Data.send_msg.ID = id_bit_union(CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.Parameter_Default,
                                            CAN_C_DEFINE.RX_OBJECT_MON, CAN_C_DEFINE.KIND_INQUIRE_STATE,
                                            CAN_C_DEFINE.TX_OBJECT_UPP, 0)
        CAN_Data.send_msg.DataLen = 8
        CAN_Data.send_msg.Data[0] = 0x00
        CAN_Data.send_msg.Data[1] = 0x01  # 查询输出的电压和电流数据
        CAN_Data.send_msg.Data[2] = 0x00
        CAN_Data.send_msg.Data[3] = 0x00
        CAN_Data.send_msg.Data[4] = 0x00
        CAN_Data.send_msg.Data[5] = 0x00
        CAN_Data.send_msg.Data[6] = 0x00
        CAN_Data.send_msg.Data[7] = 0x00  # CAN包初始化
        try:
            ret = CAN_Data.ItekonCan.VCI_Transmit(4, 0, 0, CAN_Data.send_msg_c, 1)  # 此函数见CAN盒API
            if ret == 0:
                MessageOpen.ui_critical('Error', '有一次发送失败了！检查总线')
                return 0
            else:
                return 1
        except:
            return 0

    # noinspection PyBroadException
    def CAN_DC_inquire_state_2_send(self):
        self.label_CAN_update_signal.emit('同步中')
        CAN_Data.send_msg.ID = 0x5074000
        CAN_Data.send_msg.ID = id_bit_union(CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.Parameter_Default,
                                            CAN_C_DEFINE.RX_OBJECT_MON, CAN_C_DEFINE.KIND_INQUIRE_STATE,
                                            CAN_C_DEFINE.TX_OBJECT_UPP, 0)
        CAN_Data.send_msg.DataLen = 8
        CAN_Data.send_msg.Data[0] = 0x00
        CAN_Data.send_msg.Data[1] = 0x02  # 同步当前的设定值
        CAN_Data.send_msg.Data[2] = 0x00
        CAN_Data.send_msg.Data[3] = 0x00
        CAN_Data.send_msg.Data[4] = 0x00
        CAN_Data.send_msg.Data[5] = 0x00
        CAN_Data.send_msg.Data[6] = 0x00
        CAN_Data.send_msg.Data[7] = 0x00  # CAN包初始化
        try:
            ret = CAN_Data.ItekonCan.VCI_Transmit(4, 0, 0, CAN_Data.send_msg_c, 1)  # 此函数见CAN盒API
            if ret == 0:
                MessageOpen.ui_critical('Error', '有一次发送失败了！检查总线')
                return 0
            else:
                return 1
        except:
            return 0

    # noinspection PyBroadException
    def CAN_DC_set_cmd_send(self, cmd, param):
        CAN_Data.send_msg.ID = id_bit_union(CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.Parameter_Default,
                                            CAN_C_DEFINE.RX_OBJECT_MON, CAN_C_DEFINE.KIND_SET,
                                            CAN_C_DEFINE.TX_OBJECT_UPP, 0)
        CAN_Data.send_msg.DataLen = 8
        CAN_Data.send_msg.Data[0] = 0x00
        CAN_Data.send_msg.Data[1] = cmd  # 同步当前的设定值
        CAN_Data.send_msg.Data[2] = 0x00
        CAN_Data.send_msg.Data[3] = 0x00
        CAN_Data.send_msg.Data[4] = 0x00
        CAN_Data.send_msg.Data[5] = 0x00
        CAN_Data.send_msg.Data[6] = 0x00
        CAN_Data.send_msg.Data[7] = 0x00  # CAN包初始化
        if cmd == CanControlCmdDef.CTRL_CMD_OUT_ON:
            pass
        elif cmd == CanControlCmdDef.CTRL_CMD_OUT_OFF:
            pass
        elif cmd == CanControlCmdDef.KEYBOARD_SET_OUTPUT_VOLTAGE:
            CAN_Data.send_msg.Data[2] = ((param >> 24) & 0xFF)
            CAN_Data.send_msg.Data[3] = ((param >> 16) & 0xFF)
            CAN_Data.send_msg.Data[4] = ((param >> 8) & 0xFF)
            CAN_Data.send_msg.Data[5] = (param & 0xFF)
            DC_User_Set_Data.OutputVoltage = param
            self.CAN_Set_V_update_signal.emit("{:.2f}".format(DC_User_Set_Data.OutputVoltage / 100))
            pass
        elif cmd == CanControlCmdDef.KEYBOARD_SET_LOAD_CURRENT:
            CAN_Data.send_msg.Data[2] = (param >> 24) & 0xFF
            CAN_Data.send_msg.Data[3] = (param >> 16) & 0xFF
            CAN_Data.send_msg.Data[4] = (param >> 8) & 0xFF
            CAN_Data.send_msg.Data[5] = param & 0xFF
            DC_User_Set_Data.LoadCurrent = param
            self.CAN_Set_Load_I_update_signal.emit("{:.3f}".format(DC_User_Set_Data.LoadCurrent / 1000))
            pass
        elif cmd == CanControlCmdDef.KEYBOARD_SET_LOAD_POWER:
            CAN_Data.send_msg.Data[2] = (param >> 24) & 0xFF
            CAN_Data.send_msg.Data[3] = (param >> 16) & 0xFF
            CAN_Data.send_msg.Data[4] = (param >> 8) & 0xFF
            CAN_Data.send_msg.Data[5] = param & 0xFF
            DC_User_Set_Data.LoadPower = param
            self.CAN_Set_Load_P_update_signal.emit("{:.0f}".format(DC_User_Set_Data.LoadPower))
            pass
        elif cmd == CanControlCmdDef.KEYBOARD_SET_SOURCE_CURRENT:
            CAN_Data.send_msg.Data[2] = (param >> 24) & 0xFF
            CAN_Data.send_msg.Data[3] = (param >> 16) & 0xFF
            CAN_Data.send_msg.Data[4] = (param >> 8) & 0xFF
            CAN_Data.send_msg.Data[5] = param & 0xFF
            DC_User_Set_Data.SourceCurrent = param
            self.CAN_Set_Souce_I_update_signal.emit("{:.3f}".format(DC_User_Set_Data.SourceCurrent / 1000))
            pass
        elif cmd == CanControlCmdDef.KEYBOARD_SET_SOURCE_POWER:
            CAN_Data.send_msg.Data[2] = (param >> 24) & 0xFF
            CAN_Data.send_msg.Data[3] = (param >> 16) & 0xFF
            CAN_Data.send_msg.Data[4] = (param >> 8) & 0xFF
            CAN_Data.send_msg.Data[5] = param & 0xFF
            DC_User_Set_Data.SourcePower = param
            self.CAN_Set_Souce_P_update_signal.emit("{:.0f}".format(DC_User_Set_Data.SourcePower))
            pass
        try:
            ret = CAN_Data.ItekonCan.VCI_Transmit(4, 0, 0, CAN_Data.send_msg_c, 1)  # 此函数见CAN盒API
            if ret == 0:
                MessageOpen.ui_critical('Error', '有一次发送失败了！检查总线')
                return 0
            else:
                return 1
        except:
            return 0

    # 解析接收到的CAN包
    # noinspection PyBroadException
    def CAN_DC_receive(self):
        if self.CAN_DC_inquire_state_1_send() == 0:  # 先发送查询包,查询当前输出数据
            self.BL_Statu_update_signal.emit(0)
            return 0
        try:
            can_rx_num = CAN_Data.ItekonCan.VCI_GetReceiveNum(4, 0, 0)
            while can_rx_num != 0:
                can_rx_num -= CAN_Data.ItekonCan.VCI_Receive(4, 0, 0, CAN_Data.recv_msg_c, 1, 0)  # 读一包
                if CAN_Data.recv_msg.DataLen < 8:  # 未满包，清空后面无用字节
                    for i in range(8 - CAN_Data.recv_msg.DataLen):
                        CAN_Data.recv_msg.Data[CAN_Data.recv_msg.DataLen + i] = 0
                if (CAN_Data.recv_msg.ID & 0x0700FC00) == (
                        id_bit_union(CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.Parameter_Default,
                                     CAN_C_DEFINE.RX_OBJECT_UPP, CAN_C_DEFINE.Parameter_Default,
                                     CAN_C_DEFINE.TX_OBJECT_MON,
                                     CAN_C_DEFINE.Parameter_Default) & 0x0700FC00):  # 解析为监控主机发出，上位机收
                    if (CAN_Data.recv_msg.ID & 0x00FF0000) == (
                            id_bit_union(CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.Parameter_Default,
                                         CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.KIND_SET,
                                         CAN_C_DEFINE.Parameter_Default,
                                         CAN_C_DEFINE.Parameter_Default) & 0x00FF0000):  # 解析kind为设置数据应答
                        if CanControlCmdDef.KEYBOARD_SET_OUTPUT_VOLTAGE == ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])):  # 标识传输的为设置输出电压响应信息
                            if ((CAN_Data.recv_msg.Data[2] << 16) + (CAN_Data.recv_msg.Data[3])) == CAN_C_DEFINE.cACK:
                                pass
                            if ((CAN_Data.recv_msg.Data[2] << 16) + (CAN_Data.recv_msg.Data[3])) == CAN_C_DEFINE.cNAK:
                                MessageOpen.ui_warning('warning', '电压参数错误\n设备已自动处理')
                                self.CAN_DC_inquire_state_2_send()
                                pass
                        elif CanControlCmdDef.KEYBOARD_SET_SOURCE_CURRENT == ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])):  # 标识传输的为设置输出源电流响应信息
                            if ((CAN_Data.recv_msg.Data[2] << 16) + (CAN_Data.recv_msg.Data[3])) == CAN_C_DEFINE.cACK:
                                pass
                            if ((CAN_Data.recv_msg.Data[2] << 16) + (CAN_Data.recv_msg.Data[3])) == CAN_C_DEFINE.cNAK:
                                MessageOpen.ui_warning('warning', '源电流参数错误\n设备已自动处理')
                                self.CAN_DC_inquire_state_2_send()
                                pass
                        elif CanControlCmdDef.KEYBOARD_SET_SOURCE_POWER == ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])):  # 标识传输的为设置输出源功率响应信息
                            if ((CAN_Data.recv_msg.Data[2] << 16) + (CAN_Data.recv_msg.Data[3])) == CAN_C_DEFINE.cACK:
                                pass
                            if ((CAN_Data.recv_msg.Data[2] << 16) + (CAN_Data.recv_msg.Data[3])) == CAN_C_DEFINE.cNAK:
                                MessageOpen.ui_warning('warning', '源功率参数错误\n设备已自动处理')
                                self.CAN_DC_inquire_state_2_send()
                                pass
                        elif CanControlCmdDef.KEYBOARD_SET_LOAD_CURRENT == ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])):  # 标识传输的为设置输出源电流响应信息
                            if ((CAN_Data.recv_msg.Data[2] << 16) + (CAN_Data.recv_msg.Data[3])) == CAN_C_DEFINE.cACK:
                                pass
                            if ((CAN_Data.recv_msg.Data[2] << 16) + (CAN_Data.recv_msg.Data[3])) == CAN_C_DEFINE.cNAK:
                                MessageOpen.ui_warning('warning', '载电流参数错误\n设备已自动处理')
                                self.CAN_DC_inquire_state_2_send()
                                pass
                        elif CanControlCmdDef.KEYBOARD_SET_LOAD_POWER == ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])):  # 标识传输的为设置输出源功率响应信息
                            if ((CAN_Data.recv_msg.Data[2] << 16) + (CAN_Data.recv_msg.Data[3])) == CAN_C_DEFINE.cACK:
                                pass
                            if ((CAN_Data.recv_msg.Data[2] << 16) + (CAN_Data.recv_msg.Data[3])) == CAN_C_DEFINE.cNAK:
                                MessageOpen.ui_warning('warning', '载功率参数错误\n设备已自动处理')
                                self.CAN_DC_inquire_state_2_send()
                                pass
                    if (CAN_Data.recv_msg.ID & 0x00FF0000) == (
                            id_bit_union(CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.Parameter_Default,
                                         CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.KIND_ANS_STATE,
                                         CAN_C_DEFINE.Parameter_Default,
                                         CAN_C_DEFINE.Parameter_Default) & 0x00FF0000):  # 解析kind为实时数据应答
                        if ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])) == 0x01:  # 0x01标识传输的为输出电压信息
                            self.Out_Data_Def.BatVolt = uint32_to_int32(
                                ((CAN_Data.recv_msg.Data[2] << 24) + (CAN_Data.recv_msg.Data[3] << 16)
                                 + (CAN_Data.recv_msg.Data[4] << 8) + CAN_Data.recv_msg.Data[5]))
                            self.CAN_Output_V_Show_update_signal.emit("{:.2f}".format(self.Out_Data_Def.BatVolt / 100))
                            self.CAN_Output_P_Show_update_signal.emit(
                                "{:.0f}".format((self.Out_Data_Def.BatCurr * self.Out_Data_Def.BatVolt) / 100000))
                        elif ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])) == 0x02:  # 0x02标识传输的为输出电流信息
                            self.Out_Data_Def.BatCurr = uint32_to_int32(
                                ((CAN_Data.recv_msg.Data[2] << 24) + (CAN_Data.recv_msg.Data[3] << 16)
                                 + (CAN_Data.recv_msg.Data[4] << 8) + CAN_Data.recv_msg.Data[5]))
                            if self.Out_Data_Def.BatCurr > 0:
                                self.Out_Data_Def.BatCurr -= 5
                            elif self.Out_Data_Def.BatCurr < 0 :
                                self.Out_Data_Def.BatCurr += 5
                            self.CAN_Output_I_Show_update_signal.emit("{:.2f}".format(self.Out_Data_Def.BatCurr / 1000))
                            self.CAN_Output_P_Show_update_signal.emit(
                                "{:.0f}".format((self.Out_Data_Def.BatCurr * self.Out_Data_Def.BatVolt) / 100000))
                        elif ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])) == 0x11:  # 0x11标识传输的为设置电压信息
                            DC_User_Set_Data.OutputVoltage = (CAN_Data.recv_msg.Data[2] << 24) + (
                                    CAN_Data.recv_msg.Data[3] << 16) \
                                                             + (CAN_Data.recv_msg.Data[4] << 8) + \
                                                             CAN_Data.recv_msg.Data[5]
                            self.CAN_Set_V_update_signal.emit("{:.2f}".format(DC_User_Set_Data.OutputVoltage / 100))
                            self.label_CAN_update_signal.emit('已同步: )')
                        elif ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])) == 0x12:  # 0x12标识传输的为设置载电流信息
                            DC_User_Set_Data.LoadCurrent = (CAN_Data.recv_msg.Data[2] << 24) + (
                                    CAN_Data.recv_msg.Data[3] << 16) \
                                                           + (CAN_Data.recv_msg.Data[4] << 8) + \
                                                           CAN_Data.recv_msg.Data[5]
                            self.CAN_Set_Load_I_update_signal.emit("{:.3f}".format(DC_User_Set_Data.LoadCurrent / 1000))
                        elif ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])) == 0x13:  # 0x13标识传输的为设置载功率信息
                            DC_User_Set_Data.LoadPower = (CAN_Data.recv_msg.Data[2] << 24) + (
                                    CAN_Data.recv_msg.Data[3] << 16) \
                                                         + (CAN_Data.recv_msg.Data[4] << 8) + \
                                                         CAN_Data.recv_msg.Data[5]
                            self.CAN_Set_Load_P_update_signal.emit("{:.0f}".format(DC_User_Set_Data.LoadPower))
                        elif ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])) == 0x14:  # 0x14标识传输的为设置源电流信息
                            DC_User_Set_Data.SourceCurrent = (CAN_Data.recv_msg.Data[2] << 24) + (
                                    CAN_Data.recv_msg.Data[3] << 16) \
                                                             + (CAN_Data.recv_msg.Data[4] << 8) + \
                                                             CAN_Data.recv_msg.Data[5]
                            self.CAN_Set_Souce_I_update_signal.emit(
                                "{:.3f}".format(DC_User_Set_Data.SourceCurrent / 1000))
                        elif ((CAN_Data.recv_msg.Data[0] << 16) + (
                                CAN_Data.recv_msg.Data[1])) == 0x15:  # 0x15标识传输的为设置源功率信息
                            DC_User_Set_Data.SourcePower = (CAN_Data.recv_msg.Data[2] << 24) + (
                                    CAN_Data.recv_msg.Data[3] << 16) \
                                                           + (CAN_Data.recv_msg.Data[4] << 8) + \
                                                           CAN_Data.recv_msg.Data[5]
                            self.CAN_Set_Souce_P_update_signal.emit("{:.0f}".format(DC_User_Set_Data.SourcePower))
                    if (CAN_Data.recv_msg.ID & 0x00FF0000) == (
                            id_bit_union(CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.Parameter_Default,
                                         CAN_C_DEFINE.Parameter_Default, CAN_C_DEFINE.KIND_ANS_SCPI,
                                         CAN_C_DEFINE.Parameter_Default,
                                         CAN_C_DEFINE.Parameter_Default) & 0x00FF0000):  # 解析kind为SCPI应答
                        new_text = (struct.pack('8B', *CAN_Data.recv_msg.Data).decode('utf-8')).rstrip("\n")
                        self.SCPI_Statu_update_signal.emit(new_text)
                        # MainUI.SCPI_Statu.append(CAN_Data.recv_msg.Data.encode('utf-8'))
            return 0
        except:
            return 0
