from C_DEFINE import *
from CANData import *
from UARTData import *
from Test_CAN import TaskCAN, itekon_can_open
from Test_Uart import TaskUART

tab_page = 0


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 屏幕未使用区域透明隐藏  120
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # 隐藏窗口边框和基础按钮 并置顶

        # 以下为各种变量的声明及初始化

        # 使用ui文件导入定义界面类
        MainUI.setupUi(self)

        # UI调整初始化
        MainUI.BL_Statu.setText("请选择正确的烧录对象和烧录文件，点击”下载“开始烧录")
        MainUI.sset_cb_baud.setCurrentIndex(3)  # 波特率115200
        MainUI.serial_rx_encoding.setCurrentIndex(3)  # 编码方式UTF-8

        # ---->串口相关（简单测试
        self.LockTop = 1
        # 鼠标点击检查，用于拖动界面
        self.start_x = None
        self.start_y = None
        self.anim = None
        # 用来存放接受到的数据并分割成元组
        self.AcceptString = ''
        self.DateGroup = ()
        # <----

        # ---->参数设置页面相关初始化
        # <----

        # 各类定时器的声明
        self.CAN_DC_receive_timer = QTimer()  # 在参数设置页启用 接收CAN包并处理
        # 初始端口

        # 初始化serial对象 用于串口通信
        UART_Data.ser = serial.Serial()
        # 串口检测
        self.port_detect()
        # 初始化CSV存储文件
        # self.path = "data_save.csv"
        # with open("data_save.csv", "w", newline="") as self.csvfile:
        # self.writer = csv.writer(self.csvfile)
        # self.writer.writerow(["passage1", "passage2", "passage3"])

        # 线程对象
        self.threadCAN = QThread(self)
        self.task_CAN = TaskCAN()
        self.task_CAN.moveToThread(self.threadCAN)
        self.task_CAN.Task_CAN_Switch_tabWidget_signal.connect(self.CAN_Switch_Tab_Handle)  # 信号触发的函数连接
        self.task_CAN.BL_Statu_update_signal.connect(self.BL_Statu_update_text)  # 信号触发的函数连接
        self.task_CAN.BL_Statu_setdata_signal.connect(self.BL_Statu_setdate_text)  # 信号触发的函数连接
        self.task_CAN.BL_Progress_update_signal.connect(self.BL_Progress_update_value)  # 信号触发的函数连接

        self.task_CAN.label_CAN_update_signal.connect(self.label_CAN_update_text)  # 信号触发的函数连接
        self.task_CAN.CAN_Set_V_update_signal.connect(self.CAN_Set_V_update_text)  # 信号触发的函数连接
        self.task_CAN.CAN_Set_Souce_I_update_signal.connect(self.CAN_Set_Souce_update_text)  # 信号触发的函数连接
        self.task_CAN.CAN_Set_Souce_P_update_signal.connect(self.CAN_Set_Souce_P_update_text)  # 信号触发的函数连接
        self.task_CAN.CAN_Set_Load_I_update_signal.connect(self.CAN_Set_Load_I_update_text)  # 信号触发的函数连接
        self.task_CAN.CAN_Set_Load_P_update_signal.connect(self.CAN_Set_Load_P_update_text)  # 信号触发的函数连接

        self.task_CAN.CAN_Output_V_Show_update_signal.connect(self.CAN_Output_V_Show_update_text)
        self.task_CAN.CAN_Output_I_Show_update_signal.connect(self.CAN_Output_I_Show_update_text)
        self.task_CAN.CAN_Output_P_Show_update_signal.connect(self.CAN_Output_P_Show_update_text)
        self.task_CAN.SCPI_Statu_update_signal.connect(self.SCPI_Statu_update_text)

        # self.threadCAN.started.connect(self.task_CAN.run)  # 此行表示长时间运行的事件循环
        self.threadCAN.start()

        self.threadUART = QThread(self)
        self.task_UART = TaskUART()
        self.task_UART.moveToThread(self.threadUART)
        self.task_UART.textBrowser_23_update_signal.connect(self.textBrowser_23_update_text)  # 信号触发的函数连接
        self.threadUART.started.connect(self.task_UART.run)  # 此行表示长时间运行的事件循环
        self.threadUART.start()

        # 定时器 参数设置页 接收CAN数据并解析
        self.CAN_DC_receive_timer = QTimer(self)
        self.CAN_DC_receive_timer.timeout.connect(self.task_CAN.CAN_DC_receive)

    def CAN_Switch_Tab_Handle(self, page):
        if page == 0:
            MainUI.tabWidget.setCurrentWidget(MainUI.tab_0)
        elif page == 1:
            MainUI.tabWidget.setCurrentWidget(MainUI.tab_1)
        elif page == 2:
            MainUI.tabWidget.setCurrentWidget(MainUI.tab_2)
        elif page == 3:
            MainUI.tabWidget.setCurrentWidget(MainUI.tab_3)
        elif page == 4:
            MainUI.tabWidget.setCurrentWidget(MainUI.tab_4)

    def BL_Statu_update_text(self, BL_Statu_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        # QtCore.QMetaObject.invokeMethod(MainUI.BL_Statu, "insertPlainText", QtCore.Qt.QueuedConnection,
        #                                 QtCore.Q_ARG(str, BL_Statu_text))
        MainUI.BL_Statu.append(BL_Statu_text)

    def BL_Statu_setdate_text(self, BL_Statu_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        MainUI.BL_Statu.setText(BL_Statu_text)

    def BL_Progress_update_value(self, BL_Progress_value):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        MainUI.BL_Progress.setValue(BL_Progress_value)

    def label_CAN_update_text(self, BL_Progress_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        MainUI.label_CAN.setText(BL_Progress_text)

    def CAN_Set_V_update_text(self, BL_Progress_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        MainUI.CAN_Set_V.setPlainText(BL_Progress_text)

    def CAN_Set_Souce_update_text(self, BL_Progress_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        MainUI.CAN_Set_Souce_I.setPlainText(BL_Progress_text)

    def CAN_Set_Souce_P_update_text(self, BL_Progress_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        MainUI.CAN_Set_Souce_P.setPlainText(BL_Progress_text)

    def CAN_Set_Load_I_update_text(self, BL_Progress_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        MainUI.CAN_Set_Load_I.setPlainText(BL_Progress_text)

    def CAN_Set_Load_P_update_text(self, BL_Progress_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        MainUI.CAN_Set_Load_P.setPlainText(BL_Progress_text)

    def CAN_Output_V_Show_update_text(self, BL_Progress_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        MainUI.CAN_Output_V_Show.setText(BL_Progress_text)

    def CAN_Output_I_Show_update_text(self, BL_Progress_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        MainUI.CAN_Output_I_Show.setText(BL_Progress_text)

    def CAN_Output_P_Show_update_text(self, BL_Progress_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        MainUI.CAN_Output_P_Show.setText(BL_Progress_text)

    def SCPI_Statu_update_text(self, SCPI_Progress_text):
        # 使用调用-槽函数机制以确保更新发生在主线程之中
        existing_text = MainUI.SCPI_Statu.toPlainText()
        new_text = existing_text + SCPI_Progress_text
        MainUI.SCPI_Statu.setText(new_text)
        MainUI.SCPI_Statu.moveCursor(QTextCursor.End)

    def QMessageBox_come_from_thread(self):  # 所有线程通用的弹窗函数
        if MessageOpen.MessageBox_Flag == 1:
            QMessageBox.information(MainUI.From, MessageOpen.MessageTitle, MessageOpen.MessageStr)
        elif MessageOpen.MessageBox_Flag == 2:
            QMessageBox.critical(MainUI.From, MessageOpen.MessageTitle, MessageOpen.MessageStr)
        elif MessageOpen.MessageBox_Flag == 3:
            QMessageBox.warning(MainUI.From, MessageOpen.MessageTitle, MessageOpen.MessageStr)
        MessageOpen.MessageBox_Flag = 0

    def textBrowser_23_update_text(self, update_text):
        # MainUI.serial_rx_encoding.currentIndex()  # 获得选择的是第几项
        # MainUI.serial_rx_encoding.currentText()   # 获得当前选择的字符串
        if MainUI.serial_rx_encoding.currentIndex() == 0:
            hexstr = update_text.encode('utf_8', errors='replace').hex()
            MainUI.textBrowser_23.setPlainText(
                # update_text.encode('ASCII', errors='replace').decode(encoding='ASCII', errors='replace'))  # bits转字符串显示
                " ".join([hexstr[i:i + 2] for i in range(0, len(hexstr), 2)]))  # 暂作为16进制显示
        elif MainUI.serial_rx_encoding.currentIndex() == 1:
            MainUI.textBrowser_23.setPlainText(
                update_text.encode('shift_jisx0213', errors='replace').decode(encoding='shift_jisx0213',
                                                                              errors='replace'))  # bits转字符串显示
        elif MainUI.serial_rx_encoding.currentIndex() == 2:
            MainUI.textBrowser_23.setPlainText(
                update_text.encode('utf_8', errors='replace').decode(encoding='utf_8', errors='replace'))  # bits转字符串显示
        elif MainUI.serial_rx_encoding.currentIndex() == 3:
            MainUI.textBrowser_23.setPlainText(
                update_text.encode('utf_16', errors='replace').decode(encoding='utf_16',
                                                                      errors='replace'))  # bits转字符串显示
        elif MainUI.serial_rx_encoding.currentIndex() == 4:
            MainUI.textBrowser_23.setPlainText(
                update_text.encode('gbk', errors='replace').decode(encoding='gbk', errors='replace'))  # bits转字符串显示
        elif MainUI.serial_rx_encoding.currentIndex() == 5:
            MainUI.textBrowser_23.setPlainText(
                update_text.encode('gb2312', errors='replace').decode(encoding='gb2312',
                                                                      errors='replace'))  # bits转字符串显示
        MainUI.textBrowser_23.moveCursor(QTextCursor.End)

    # 串口检测
    def port_detect(self):
        # 用来存放已检测串口的字典
        UART_Data.port_get = list(serial.tools.list_ports.comports())
        if not UART_Data.port_list == UART_Data.port_get:
            UART_Data.port_dict = {}
            UART_Data.port_list = list(serial.tools.list_ports.comports())
            MainUI.sset_cb_choose.clear()
            # MainUI.BL_sset_cb_choose.clear()
            for port in UART_Data.port_list:
                UART_Data.port_dict["%s" % port[0]] = "%s" % port[1]
                MainUI.sset_cb_choose.addItem(port[0] + '：' + port[1])
                # MainUI.BL_sset_cb_choose.addItem(port[0] + '：' + port[1])
            if len(UART_Data.port_dict) == 0:
                MainUI.sset_cb_choose.addItem('无串口')
        # MainUI.sset_btn_open.setEnabled(True)

        # 以下三个函数用于监测鼠标点击并移动窗口

    def mousePressEvent(self, event):
        if event.button() == 1 and app.widgetAt(event.globalPos()) is not None:  # QtCore.Qt.LeftButton=1
            super(MainWindow, self).mousePressEvent(event)
            self.start_x = event.x()
            self.start_y = event.y()

    # def mouseReleaseEvent(self, event):
    #     self.start_x = None
    #     self.start_y = None

    def mouseMoveEvent(self, event):  # QComboBox
        try:
            # if isinstance(app.widgetAt(event.globalPos()),QWidget) or isinstance(app.widgetAt(event.globalPos()), QLabel):
            if (isinstance(app.widgetAt(event.globalPos()), QLabel)) or (
                    not isinstance(app.widgetAt(event.globalPos()), QComboBox) and not isinstance(
                app.widgetAt(event.globalPos()), QPushButton)
            ):
                super(MainWindow, self).mouseMoveEvent(event)
                dis_x = event.x() - self.start_x
                dis_y = event.y() - self.start_y
                self.move(self.x() + dis_x, self.y() + dis_y)
        except TypeError:
            pass

    # 置顶切换
    def top_lock_unlock(self):
        if self.LockTop:
            self.setWindowFlags(self.windowFlags() & (~QtCore.Qt.WindowStaysOnTopHint))
            MainUI.App_Lock.setStyleSheet("QPushButton\n"
                                          "{\n"
                                          "background-color:rgb(134, 149, 223,60);\n"
                                          "border-radius:12px;\n"
                                          "border-top-left-radius: 12px;\n"
                                          "border-top-right-radius: 12px;\n"
                                          "}")
            self.show()
            self.LockTop = 0
        else:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            MainUI.App_Lock.setStyleSheet("QPushButton\n"
                                          "{\n"
                                          "background-color:rgb(170, 200, 223);\n"
                                          "border-radius:12px;\n"
                                          "border-top-left-radius: 12px;\n"
                                          "border-top-right-radius: 12px;\n"

                                          "}")
            self.show()
            self.LockTop = 1

    # 获得当前TabWidget的值，控制定时器
    def tabwiget_get(self):
        global tab_page
        tab_page = MainUI.tabWidget.currentIndex()  # 获得当前页面号
        self.port_detect()  # 更新串口号
        if tab_page == 0 or tab_page == 2 or tab_page == 3:  # 串口强行关闭判定
            if MainUI.sset_btn_open.text() == '关闭':
                self.port_set_statu(UART_DATA.serial_off)
        if tab_page == 0 or tab_page == 1 or tab_page == 2:  # CAN查询关闭判定
            self.port_set_statu(UART_DATA.serial_off)
            if self.CAN_DC_receive_timer.isActive():  # CAN查询数据定时器
                self.CAN_DC_receive_timer.stop()
        if tab_page == 3:
            if not self.CAN_DC_receive_timer.isActive():
                if itekon_can_open() == 0:
                    MainUI.tabWidget.setCurrentWidget(MainUI.tab_0)
                elif self.task_CAN.CAN_DC_inquire_state_2_send() == 0:
                    MainUI.tabWidget.setCurrentWidget(MainUI.tab_0)
                else:
                    self.CAN_DC_receive_timer.start(500)

    # 获取端口号（串口选择界面想显示完全 但打开串口只需要串口号COMX）
    def get_port_name(self):
        full_name = MainUI.sset_cb_choose.currentText()
        com_name = full_name[0:full_name.rfind('：')]
        return com_name

    # 打开/关闭 串口
    def port_set_statu(self, dat):
        if dat == UART_DATA.serial_on:
            if len(UART_Data.port_dict) == 0:
                self.port_detect()
                QMessageBox.warning(self, 'Open Port Warning', '没有可打开的串口！')
                return None
            UART_Data.ser.port = self.get_port_name()  # 设置端口
            UART_Data.ser.baudrate = int(MainUI.sset_cb_baud.currentText())  # 波特率
            UART_Data.ser.bytesize = 8  # 数据位
            UART_Data.ser.parity = 'N'  # 校验位
            UART_Data.ser.stopbits = 1  # 停止位
            UART_Data.ser.write_timeout = 0
            UART_Data.ser.timeout = 0.2
            UART_Data.ser.inter_byte_timeout = 0.2
            UART_Data.ser.writeTimeout = 0.2
            try:
                UART_Data.ser.open()
                UART_Data.port_statu = 1
                MainUI.sset_btn_open.setText('关闭')
            except serial.SerialException:
                QMessageBox.critical(self, 'Open Port Error', '此串口不能正常打开！')
                return None
        elif dat == UART_DATA.serial_off:
            try:
                UART_Data.ser.close()
                UART_Data.port_statu = 0
                MainUI.sset_btn_open.setText('打开')
            except IOError:
                QMessageBox.critical(self, 'Open Port Error', '此串口不能正常关闭！')
                return None

    # 切换串口状态
    def port_open_switch(self):
        if UART_Data.port_statu == UART_DATA.serial_on:
            self.port_set_statu(UART_DATA.serial_off)
        else:
            self.port_set_statu(UART_DATA.serial_on)

    # 波特率改变
    def sys_boud_change(self):
        try:
            UART_Data.ser.baudrate = int(MainUI.sset_cb_baud.currentText())  # 波特率
            UART_Data.ser.close()
            UART_Data.ser.open()
        except serial.SerialException:
            MainUI.sset_btn_open.setText('关闭')
            QMessageBox.critical(self, 'Open Port Error', '此波特率异常！')
            return None

    # 端口号改变
    def sys_choose_change(self):
        try:
            port = self.get_port_name()  # 设置端口
            if UART_Data.ser.isOpen():
                UART_Data.ser.close()
            UART_Data.ser.port = port
            UART_Data.ser.close()
            self.port_set_statu(UART_DATA.serial_on)

        except serial.SerialException:
            self.port_detect()
            MainUI.sset_btn_open.setText('关闭')
            QMessageBox.critical(self, 'Open Port Error', '此串口号异常！')
            return None

    # 发送实现
    def Uart_send_key_down(self):
        single_sent_string = MainUI.text_input.toPlainText()
        self.task_UART.Uart_Send_Single(single_sent_string)  # 发送一次发送框的字符串

    # BootLoad实现------------------>
    # 选单选取烧录文件
    def getpath4BLpath(self):
        Sys_Controller.filetype = MainUI.BL_path.currentText()
        if Sys_Controller.filetype[0]:
            MainUI.BL_Statu.append(Sys_Controller.filetype + '\r\n')
        else:
            pass

    # 选取烧录文件
    def getpath(self):
        Sys_Controller.filetype = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()",
                                                              Sys_Controller.BL_flie_path_route,
                                                              "Bin Files (*.bin);;Txt Files (*.txt);;Hex Files (*.hex)")  # 设置文件扩展名过滤,注意用双分号间隔
        if Sys_Controller.filetype[0]:
            Sys_Controller.BL_flie_path_route = os.path.dirname(Sys_Controller.filetype[0])
            MainUI.BL_path.addItem(Sys_Controller.filetype[0])
            MainUI.BL_path.setCurrentIndex((MainUI.BL_path.count() - 1))
        else:
            pass

    def CAN_BL_Start_Set(self):
        worker_task = self.task_CAN.bl_process_open  # 此两行为开启一次bootload线程的操作
        QTimer.singleShot(0, worker_task)
        # Sys_Controller.Test_CAN_BL_Start = 1  # 此行为作为定时任务时的控制参数

    # <------------------

    # 参数设置CAN实现------------------>
    # 使用CMD发送的指令
    # 无返回值，供按钮调用
    def CAN_DC_set_cmd_send_CTRL_CMD_OUT_ON(self):  # 设备开机按钮
        self.task_CAN.CAN_DC_set_cmd_send(CanControlCmdDef.CTRL_CMD_OUT_ON, 0)

    def CAN_DC_set_cmd_send_CTRL_CMD_OUT_OFF(self):  # 设备关机按钮
        self.task_CAN.CAN_DC_set_cmd_send(CanControlCmdDef.CTRL_CMD_OUT_OFF, 0)

    def CAN_DC_set_cmd_send_KEYBOARD_SET_OUTPUT_VOLTAGE(self):  # 发送输出电压按钮
        MainUI.CAN_Set_V.setPlainText(re.sub(r'[^\d.]', '', MainUI.CAN_Set_V.toPlainText()))
        self.task_CAN.CAN_DC_set_cmd_send(CanControlCmdDef.KEYBOARD_SET_OUTPUT_VOLTAGE,
                                          int(float(MainUI.CAN_Set_V.toPlainText()) * 100))

    def CAN_DC_set_cmd_send_KEYBOARD_SET_SOURCE_CURRENT(self):  # 发送源电流按钮
        MainUI.CAN_Set_Souce_I.setPlainText(re.sub(r'[^\d.]', '', MainUI.CAN_Set_Souce_I.toPlainText()))
        self.task_CAN.CAN_DC_set_cmd_send(CanControlCmdDef.KEYBOARD_SET_SOURCE_CURRENT,
                                          int(float(MainUI.CAN_Set_Souce_I.toPlainText()) * 1000))

    def CAN_DC_set_cmd_send_KEYBOARD_SET_SOURCE_POWER(self):  # 发送源功率按钮
        MainUI.CAN_Set_Souce_P.setPlainText(re.sub(r'[^\d.]', '', MainUI.CAN_Set_Souce_P.toPlainText()))
        self.task_CAN.CAN_DC_set_cmd_send(CanControlCmdDef.KEYBOARD_SET_SOURCE_POWER,
                                          int(float(MainUI.CAN_Set_Souce_P.toPlainText())))

    def CAN_DC_set_cmd_send_KEYBOARD_SET_LOAD_CURRENT(self):  # 发送载电流按钮
        MainUI.CAN_Set_Load_I.setPlainText(re.sub(r'[^\d.]', '', MainUI.CAN_Set_Load_I.toPlainText()))
        self.task_CAN.CAN_DC_set_cmd_send(CanControlCmdDef.KEYBOARD_SET_LOAD_CURRENT,
                                          int(float(MainUI.CAN_Set_Load_I.toPlainText()) * 1000))

    def CAN_DC_set_cmd_send_KEYBOARD_SET_LOAD_POWER(self):  # 发送载功率按钮
        MainUI.CAN_Set_Load_P.setPlainText(re.sub(r'[^\d.]', '', MainUI.CAN_Set_Load_P.toPlainText()))
        self.task_CAN.CAN_DC_set_cmd_send(CanControlCmdDef.KEYBOARD_SET_LOAD_POWER,
                                          int(float(MainUI.CAN_Set_Load_P.toPlainText())))

    def CAN_SCPI_send_KIND_EXTERNAL_SCPI(self):  # 发送SCPI按钮
        Send_Str = MainUI.CAN_SCPI_Text.toPlainText()
        MainUI.SCPI_Statu.append(("=>  " + Send_Str + "\r\n" + "<=  ").rstrip("\n"))
        worker_task = self.task_CAN.scpi_process_open  # 此两行为开启一次SCPI线程的操作
        QTimer.singleShot(0, worker_task)

    # 参数设置页面的回车触发函数
    def CAN_DC_CAN_Set_V_blockChanged(self):
        MainUI.CAN_Set_V.setPlainText(re.sub(r'[^\d.]', '', MainUI.CAN_Set_V.toPlainText()))
        DC_User_Set_Data.OutputVoltage = int(float(MainUI.CAN_Set_V.toPlainText()) * 100)
        MainUI.CAN_Set_V.setPlainText("{:.2f}".format(DC_User_Set_Data.OutputVoltage / 100))

    def CAN_DC_CAN_Set_Souce_I_blockChanged(self):
        MainUI.CAN_Set_Souce_I.setPlainText(re.sub(r'[^\d.]', '', MainUI.CAN_Set_Souce_I.toPlainText()))
        DC_User_Set_Data.SourceCurrent = int(float(MainUI.CAN_Set_Souce_I.toPlainText()) * 1000)
        MainUI.CAN_Set_Souce_I.setPlainText("{:.3f}".format(DC_User_Set_Data.SourceCurrent / 1000))

    def CAN_DC_CAN_Set_Souce_P_blockChanged(self):
        MainUI.CAN_Set_Souce_P.setPlainText(re.sub(r'[^\d.]', '', MainUI.CAN_Set_Souce_P.toPlainText()))
        DC_User_Set_Data.SourcePower = int(float(MainUI.CAN_Set_Souce_P.toPlainText()))
        MainUI.CAN_Set_Souce_P.setPlainText("{:.0f}".format(DC_User_Set_Data.SourcePower))

    def CAN_DC_CAN_Set_Load_I_blockChanged(self):
        MainUI.CAN_Set_Load_I.setPlainText(re.sub(r'[^\d.]', '', MainUI.CAN_Set_Load_I.toPlainText()))
        DC_User_Set_Data.LoadCurrent = int(float(MainUI.CAN_Set_Load_I.toPlainText()) * 1000)
        MainUI.CAN_Set_Load_I.setPlainText("{:.3f}".format(DC_User_Set_Data.LoadCurrent / 1000))

    def CAN_DC_CAN_Set_Load_P_blockChanged(self):
        MainUI.CAN_Set_Load_P.setPlainText(re.sub(r'[^\d.]', '', MainUI.CAN_Set_Load_P.toPlainText()))
        DC_User_Set_Data.LoadPower = int(float(MainUI.CAN_Set_Load_P.toPlainText()))
        MainUI.CAN_Set_Load_P.setPlainText("{:.0f}".format(DC_User_Set_Data.LoadPower))
