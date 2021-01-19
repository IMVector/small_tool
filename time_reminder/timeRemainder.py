import sys
from datetime import *
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QGridLayout, QWidget, QProgressBar, QHBoxLayout, QVBoxLayout, QAction, QMenu, QSystemTrayIcon, qApp, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt5.QtGui import QCursor, QIcon

StyleSheet = '''
QProgressBar {
    min-height: 12px;
    max-height: 12px;
    border-radius: 6px;
}
QProgressBar::chunk {
    border-radius: 6px;
    background-color: #009688;
}

#abc {
    margin-left:auto;
    margin-right:auto;
}

'''


class Worker(QObject):

    valueChanged = pyqtSignal(int, int, int, int, int)  # 值变化信号
    month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def run(self):

        while True:
            t = datetime.today()
            second = t.second
            minute = t.minute
            hour = t.hour

            left_second = 59-second
            left_minute = 59-minute
            left_hour = 23-hour

            week_gone_time = t.weekday()*86400+second+minute*60+hour*3600  # 本周已过去的时间

            week_percentage = week_gone_time*100//604800  # 604800一周的秒数
            # week_percentage = (t.weekday()+1)*100//7  # 从0开始

            month_percentage = 0
            # print(t.day)
            month_gone_time = (t.day-1)*86400+second+minute * \
                60+hour*3600  # 本月已经过去的时间从1开始，要减1
            # print(month_gone_time)
            if(t.month == 2):
                if(self.is_leap_year(t.year)):
                    month_percentage = month_gone_time*100//2505600
                    # month_percentage = t.day*100//29
                else:
                    # month_percentage = t.day*100//28
                    month_percentage = month_gone_time*100//2419200
            else:
                # month_percentage = t.day*100//self.month[t.month]
                month_percentage = month_gone_time * \
                    100//(self.month[t.month]*86400)

            self.valueChanged.emit(
                left_hour, left_minute, left_second, week_percentage, month_percentage)
            QThread.sleep(1)

    def is_leap_year(self, year):
        """
        判断是否是闰年 
        """
        if (year % 4 == 0 and year % 100 != 0 or year % 400 == 0):
            return True
        else:
            return False


class MainWindow(QMainWindow):
    # 声明无参数的信号,必须作为类成员，否则报错
    signal1 = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        wid = QWidget(self)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)  # 保持窗口在最顶端，不显示最大化最小化和关闭按钮，不在任务栏显示
        #  | Qt.Tool   #不显示任务栏按钮
        self.setCentralWidget(wid)  # 主窗口不加QWidget无法添加布局

        self.label_hint = QLabel(text="今日剩余", objectName="abc")
        self.label_hour = QLabel("0")
        self.label_hour_text = QLabel("时")
        self.label_minute = QLabel("0")
        self.label_minute_text = QLabel("分")
        self.label_second = QLabel("0")
        self.label_second_text = QLabel("秒")
        self.label_week = QLabel("本周")
        self.label_week_percent = QLabel("0%")
        self.label_month = QLabel("本月")
        self.label_month_percent = QLabel("0%")

        self.progressBar_week = QProgressBar(
            self, minimum=0, maximum=100, textVisible=False,)
        self.progressBar_month = QProgressBar(
            self, minimum=0, maximum=100, textVisible=False,)

        self.progressBar_week.setValue(50)
        self.progressBar_month.setValue(75)

        hbox_top = QHBoxLayout()  # 水平布局
        hbox_top.addWidget(self.label_hint)
        hbox_top.setAlignment(Qt.AlignCenter)  # 居中对齐

        hbox_middle = QHBoxLayout()  # 水平布局
        hbox_middle.addWidget(self.label_hour)
        hbox_middle.addWidget(self.label_hour_text)
        hbox_middle.addWidget(self.label_minute)
        hbox_middle.addWidget(self.label_minute_text)
        hbox_middle.addWidget(self.label_second)
        hbox_middle.addWidget(self.label_second_text)

        hbox_bottom_top = QHBoxLayout()  # 水平布局
        hbox_bottom_top.addWidget(self.label_week)
        hbox_bottom_top.addWidget(self.progressBar_week)
        hbox_bottom_top.addWidget(self.label_week_percent)

        hbox_bottom = QHBoxLayout()  # 水平布局
        hbox_bottom.addWidget(self.label_month)
        hbox_bottom.addWidget(self.progressBar_month)
        hbox_bottom.addWidget(self.label_month_percent)

        vbox = QVBoxLayout()  # 垂直布局
        vbox.addLayout(hbox_top)
        vbox.addLayout(hbox_middle)
        vbox.addLayout(hbox_bottom_top)
        vbox.addLayout(hbox_bottom)

        wid.setLayout(vbox)

        self.init()

        # -------------------通知区域图标右键菜单start------------------
        self.minimizeAction = QAction(u"最小化", self,
                                      triggered=self.hide)
        self.restoreAction = QAction(u"&显示窗口", self,
                                     triggered=self.showNormal)
        # self.quitAction = QAction(u"&退出", self,
        #                           triggered=qApp.quit)
        self.quitAction = QAction(u"&退出", self,
                                  triggered=lambda: sys.exit(app.exec_()))
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
        self.iconComboBox.addItem(
            QIcon('time.png'), "time")
        # 设置通知区域的ICON
        self.iconComboBox.currentIndexChanged.connect(
            self.setIcon)

        # 通知区域icon显示
        self.iconComboBox.setCurrentIndex(1)
        self.trayIcon.show()
        self.trayIcon.activated.connect(
            self.iconActivated)

        # 设定弹出主窗口的标题和大小
        # self.setWindowTitle(u"动漫驿站通知程序")
        # self.resize(400, 300)

    # def showMessage(self):
    #     #这里是可以设置弹出对话气泡的icon的，作为实验就省略了
    #     icon = QSystemTrayIcon.MessageIcon()
    #     self.trayIcon.showMessage(
    #         u'提示',u'您有新的任务，请注意查收', icon,1000)

    # def getTasksNum(self):
    #     self.showMessage()

    def setIcon(self, index):
        icon = self.iconComboBox.itemIcon(0)
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)
        self.trayIcon.setToolTip(
            self.iconComboBox.itemText(index))

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

    def quit_application(self):
        self._thread.quit()

    def init(self):
        self.m_flag = False
        self.doubleClickFlag = False
        # 启动线程更新显示时间和进度条
        self._thread = QThread(self)
        self._worker = Worker()
        self._worker.moveToThread(self._thread)  # 移动到线程中执行
        self._thread.finished.connect(self._worker.deleteLater)
        self._worker.valueChanged.connect(self.update_time)

        self._thread.start()  # 启动线程
        QTimer.singleShot(1, self._worker.run)

    def update_time(self, left_hour, left_minute, left_second, week_percentage, month_percentage):
        # 更新显示内容
        self.label_hour.setText(str(left_hour))
        self.label_minute.setText(str(left_minute))
        self.label_second.setText(str(left_second))
        self.progressBar_week.setValue(week_percentage)
        self.label_week_percent.setText(str(week_percentage)+"%")
        self.progressBar_month.setValue(month_percentage)
        self.label_month_percent.setText(str(month_percentage)+"%")

    def mousePressEvent(self, event):
        # 重写鼠标事件
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos()-self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标
        # if event.button() ==Qt.RightButton:

    def mouseMoveEvent(self, QMouseEvent):
        # 重写鼠标事件
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos()-self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        # 重写鼠标事件
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))


app = QApplication(sys.argv)  # 启动主程序
app.setStyleSheet(StyleSheet)
QApplication.setQuitOnLastWindowClosed(False)
window = MainWindow()  # 初始化窗口
window.move(1650, 850)
window.show()  # 显示窗口
# app.exec_()  # 启动事件循环
sys.exit(app.exec_())

# self.button1.clicked.connect(self.slot1)#关联信号与槽
# self.button2.clicked.connect(lambda: self.signal1.emit())# 自定义的信号槽
# self.button3.clicked.connect(lambda : self.slot3("传输显示内容"))# 带参数的信号传输
# self.signal1.connect(self.slot2)

# def slot1(self):
#     self.label.setText("aaaaaaaaaaaaaa")

# def slot2(self):
#     self.label.setText("bbbbbbbbbbbbbb")

# def slot3(self, arg1):
#    self.label.setText(arg1)
# engine = QQmlApplicationEngine()
# Load the qml file into the engine
# engine.load("C:\\Users\\Vector\\Desktop\\untitled.qml")


# 1、直接隐藏界面整个头部内容

# setWindowFlags(Qt.FramelessWindowHint)

# 2、显示最小化按钮

# setWindowFlags(Qt.WindowMinimizeButtonHint)

# 3、显示最大化按钮

# setWindowFlags(Qt.WindowMaximizeButtonHint)

# 4、显示最小化和最大化按钮

# setWindowFlags(Qt.WindowMinMaxButtonsHint)

# 5、显示关闭按钮

# setWindowFlags(Qt.WindowCloseButtonHint)

# 6、固定界面大小尺寸，不能进行缩放（三种方法都可以）

# （1）setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)

# （2）setFixedSize(width, height)

# （3）setMinimumSize(800, 700)

#          setMaximumSize(800, 700);

# 7、取消最小化和最大化，及关闭按钮（利用固定大小方法）

# setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.MSWindowsFixedSizeDialogHint)
