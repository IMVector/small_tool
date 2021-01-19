import pyautogui
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, QMenu, QSystemTrayIcon, qApp, QComboBox
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor, QPainter, QColor,  QPen, QIcon


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 窗口透明
        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                            Qt.FramelessWindowHint | Qt.Tool)  # 保持窗口在最顶端，不显示最大化最小化和关闭按钮，不在任务栏显示
        self.point = QPoint(1000, 500)
        self.m_flag = False
        self.doubleClickFlag = False
        # -------------------通知区域图标右键菜单start------------------
        self.minimizeAction = QAction(u"最小化", self,
                                      triggered=self.hide)
        self.restoreAction = QAction(u"&显示窗口", self,
                                     triggered=self.showNormal)
        # self.quitAction = QAction(u"&退出", self,
        #                           triggered=qApp.quit)
        self.quitAction = QAction(u"&退出", self,triggered=lambda: sys.exit(app.exec_()))
        # 弹出的菜单的行为，包括退出，还原，最小化
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addAction(self.minimizeAction)
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        # -------------------通知区域图标右键菜单end------------------
        # 设置一个iconComboBox
        self.iconComboBox = QComboBox()
        self.iconComboBox.addItem(QIcon('touch.png'), "touch")
        # 设置通知区域的ICON
        self.iconComboBox.currentIndexChanged.connect(self.setIcon)

        # 通知区域icon显示
        self.iconComboBox.setCurrentIndex(1)
        self.trayIcon.show()
        self.trayIcon.activated.connect(self.iconActivated)

    def mouseDoubleClickEvent(self, event):
        self.m_flag = True
        self.m_Position = event.globalPos()-self.pos()  # 获取鼠标相对窗口的位置
        event.accept()
        self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_flag:
            self.move(event.globalPos()-self.m_Position)  # 更改窗口位置
            event.accept()

        self.point = event.pos()#更新鼠标最后的位置
        # print(self.point.x(), self.point.y())

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        if self.m_flag == False:#非移动状态下
            if(self.point.x() < 10 and self.point.x() > -100):  # 后退
                pyautogui.hotkey('altleft', 'tab')
                pyautogui.hotkey('altleft', 'left')
            if(self.point.x() > 30 and self.point.x() < 200):  # 前进
                pyautogui.hotkey('altleft', 'tab')
                pyautogui.hotkey('altleft', 'right')
            # if(self.point.y() < -100 and self.point.y() > -200):
            #     pyautogui.hotkey('altleft', 'tab')
            #     pyautogui.hotkey('ctrl', 'w')

        self.m_flag = False

    def paintEvent(self, event):
        self.painter = QPainter(self)
        self.painter.setRenderHint(QPainter.Antialiasing, True)  # 抗锯齿功能
        self.painter.begin(self)
        self.painter.setPen(QPen(QColor("#CDC9C9"), 10))  # 设置画笔形式
        self.painter.setBrush(QColor("#FFFAFA"))  # 填充内容
        self.painter.drawEllipse(50, 30, 50, 50)
        self.painter.end()

    def setIcon(self, index):
        icon = self.iconComboBox.itemIcon(0)
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)
        self.trayIcon.setToolTip(self.iconComboBox.itemText(index))

    def iconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.doubleClickFlag == False:
                self.showNormal()
                self.doubleClickFlag = True
            else:
                self.hide()
                self.doubleClickFlag = False
        # elif reason == QSystemTrayIcon.MiddleClick:
        #     self.showMessage()
        # (QSystemTrayIcon.Trigger,QSystemTrayIcon.DoubleClick)


app = QApplication(sys.argv)  # 启动主程序
QApplication.setQuitOnLastWindowClosed(False)
window = MainWindow()  # 初始化窗口
desktop = QApplication.desktop()
x = desktop.width()//10*9
y = (desktop.height() - window.height()) // 3*2
window.move(x, y)
window.show()  # 显示窗口
sys.exit(app.exec_())
