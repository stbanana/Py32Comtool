# from PyQt5 import QtCore, QtGui, QtWidgets
#
#
# class TabBar(QtWidgets.QTabBar):
#     def tabSizeHint(self, index):
#         s = QtWidgets.QTabBar.tabSizeHint(self, index)
#         s.transpose()
#         return s
#
#     def paintEvent(self, event):
#         painter = QtWidgets.QStylePainter(self)
#         opt = QtWidgets.QStyleOptionTab()
#
#         for i in range(self.count()):
#             self.initStyleOption(opt, i)
#             painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
#             painter.save()
#
#             s = opt.rect.size()
#             s.transpose()
#             r = QtCore.QRect(QtCore.QPoint(), s)
#             r.moveCenter(opt.rect.center())
#             opt.rect = r
#
#             c = self.tabRect(i).center()
#             painter.translate(c)
#             painter.rotate(90)
#             painter.translate(-c)
#             painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt);
#             painter.restore()
#
#
# class TabWidget(QtWidgets.QTabWidget):
#     def __init__(self, *args, **kwargs):
#         QtWidgets.QTabWidget.__init__(self, *args, **kwargs)
#         self.setTabBar(TabBar(self))
#         self.setTabPosition(QtWidgets.QTabWidget.West)
#
#
# if __name__ == '__main__':
#     import sys
#
#     app = QtWidgets.QApplication(sys.argv)
#     w = TabWidget()
#     w.addTab(QtWidgets.QWidget(), "tab1")
#     w.addTab(QtWidgets.QWidget(), "tab2")
#     w.addTab(QtWidgets.QWidget(), "tab3")
#     w.show()
#
#     sys.exit(app.exec_())


from PyQt5.QtWidgets import QApplication, QPlainTextEdit
from PyQt5.QtGui import QColor

if __name__ == '__main__':
    data = [97, 98, 99, 100, 101, 102, 103, 104]
    (data.encode('utf-8'))
