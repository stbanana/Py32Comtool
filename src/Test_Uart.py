from C_DEFINE import *
from UARTData import *


class TaskUART(QObject):
    def __init__(self, parent=None):
        super(TaskUART, self).__init__(parent)

    textBrowser_23_update_signal = pyqtSignal(str)

    # 传口任务主循环
    def run(self):
        while True:
            self.Uart_Schedule()
            self.Uart_Read()
            self.Uart_Write()
            QThread.msleep(10)

    def Uart_Schedule(self):
        return 0

    def Uart_Read(self):
        self.Read_Callback()
        return 0

    def Uart_Write(self):
        return 0

    def Uart_Send_Single(self, send_string):
        try:
            # 非空字符串
            if UART_Data.ser.isOpen():
                if send_string != '':
                    single_sent_string = (send_string + "\r\n").encode('utf-8')
                    UART_Data.ser.write(single_sent_string)
            else:
                return None
        except IOError:
            return None

    def Read_Callback(self):
        try:
            if UART_Data.ser.inWaiting():
                UART_Data.no_read_cnt = 0
                while UART_Data.ser.inWaiting():
                    UART_Data.read_set_parsed += UART_Data.ser.read(1).decode()
                    if UART_Data.read_set_parsed.endswith == '\r':
                        self.String_parsing_universal()
                        UART_Data.read_set_parsed = ''
                        return
                if UART_Data.read_set_parsed != '':
                    self.String_parsing_universal()
                    UART_Data.read_set_parsed = ''
                    return
        except serial.serialutil.SerialException:
            return

    def String_parsing_universal(self):
        self.textBrowser_23_update_signal.emit(UART_Data.read_set_parsed)
        return
