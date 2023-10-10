from UI.Start_Menu import Ui_MainWindow as WindowST
from UI.Add_Card import Ui_MainWindow as WindowAC
from UI.Chosen_Deck import Ui_MainWindow as WindowCD
from UI.Front import Ui_MainWindow as WindowF
from UI.Back import Ui_MainWindow as WindowB
from UI.Detail import Ui_MainWindow as WindowDT
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QFileDialog, QWidget
from PySide6.QtGui import QTextCursor, QFont
from time import time
from controler import *
import os


PATH = r'E:\myfiles\python\Linear_Memo\src\LMFiles\test.nmf'


class WinAC(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = WindowAC()
        self.ui.setupUi(self)


class WinCD(QMainWindow):
    HomeSignal = Signal(str)

    def __init__(self, path) -> None:
        super().__init__()
        self.path = path
        self.ui = WindowCD()
        self.ui.setupUi(self)
        self.ui.label.setText(path.split('\\')[-1].split('.')[0])
        self.Ov, self.Ta = bulk_load(self.path)
        self.ui.label_4.setText(str(len(self.Ov)))
        self.ui.label_5.setText(str(len(self.Ov) + len(self.Ta)))
        self.ui.pushButton_2.clicked.connect(self.Rv)
        self.ui.actionHome.triggered.connect(self.Home)

    def Rv(self, seq=0):  # review
        self.Ov, self.Ta = bulk_load(self.path)
        self.ui.label_4.setText(str(len(self.Ov)))
        self.ui.label_5.setText(str(len(self.Ov) + len(self.Ta)))
        if seq == 0:
            self.n = randint(0, len(self.Ov) - 1)
        else:
            self.n = self.nf
        self.c = self.Ov[self.n]
        self.subRv1()

    def subRv1(self):
        self.F = WinF(self, self.c.front())
        self.F.show()
        self.F.OKSignal.connect(self.subRv2)
        self.F.BackSignal.connect(self.subRv4)
        self.F.HomeSignal.connect(self.Home)

    def subRv2(self):
        self.B = WinB(self, self.c.front(), self.c.back())
        self.B.show()
        self.B.Reviewed.connect(self.subRv3)
        self.B.BackSignal.connect(self.subRv4)
        self.B.HomeSignal.connect(self.Home)

    def subRv3(self, feedback):
        self.Ov[self.n].review(feedback)
        bulk_save(self.path, self.Ov + self.Ta)
        self.nf = self.n
        if self.n < len(self.Ov):
            self.n += 1
            self.Rv()
        else:
            self.close()

    def subRv4(self):
        self.Rv(1)

    def Home(self):
        self.HomeSignal.emit('')
        self.close()


class WinF(QMainWindow):
    OKSignal = Signal()
    BackSignal = Signal()
    HomeSignal = Signal()

    def __init__(self, parent, t:str) -> None:
        super().__init__(parent=parent)
        self.ui = WindowF()
        self.ui.setupUi(self)
        self.ui.textEdit.setText(t)
        self.ui.pushButton.clicked.connect(self.turn)
        self.ui.actionBack.triggered.connect(self.back)
        self.ui.actionHome.triggered.connect(self.home)

    def home(self):
        self.HomeSignal.emit()
        self.close()

    def back(self):
        self.BackSignal.emit()
        self.close()

    def turn(self):
        self.OKSignal.emit()
        self.close()


class WinB(QMainWindow):
    Reviewed = Signal(float)
    BackSignal = Signal()
    HomeSignal = Signal()

    def __init__(self, parent, tf, tb) -> None:
        super().__init__(parent=parent)
        self.ui = WindowB()
        self.ui.setupUi(self)
        self.ui.textEdit.setText(tf)
        self.ui.textEdit_2.setText(tb)
        self.ui.pushButton.clicked.connect(self.next)
        self.ui.verticalSlider.valueChanged.connect(self.percent)
        self.ui.actionBack.triggered.connect(self.back)
        self.ui.actionHome.triggered.connect(self.home)

    def back(self):
        self.BackSignal.emit()
        self.close()

    def home(self):
        self.HomeSignal.emit()
        self.close()

    def percent(self):
        v = str(self.ui.verticalSlider.value()) + '%'
        self.ui.label_3.setText(v)

    def next(self):
        self.Reviewed.emit(self.ui.verticalSlider.value())
        self.close()


class WinDT(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = WindowDT()
        self.ui.setupUi(self)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        # 设置子窗口
        '''
        self.WinAC = WinAC()
        self.WinCD = WinCD()
        self.WinF = WinF()
        self.WinB = WinB()
        self.WinDT = WinDT()
        self.WinAC.show()
        self.WinDT.show()
        self.WinF.show()
        self.WinB.show()
        self.WinCD.show()
        '''
        self.ui = WindowST()
        self.ui.setupUi(self)
        self.ui.setupUi(self)
        self.ui.actionLoad.triggered.connect(self.Load)
        self.ui.actionExport.triggered.connect(self.Export)
        self.ui.spinBox.valueChanged.connect(self.Select)
        self.ui.pushButton_2.clicked.connect(self.Choose)
        # 定义一些变量（类）
        self.DeckDict = {}
        self.selectedDeck = ''

    def Load(self):
        # 导入文件夹
        path = QFileDialog.getExistingDirectory(self, "选择文件夹", r"E:\myfiles\python\Linear_Memo\src")
        # print(path)
        rt = {}
        files = os.listdir(path)
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path) and str(file).split('.')[1] == 'nmf':
                rt[str(file).split('.')[0]] = file_path
        # print(rt.keys())
        t = ''
        for num, name in enumerate(rt.keys()):
            t += str(num) + '\t' + name + '\n'
        # print(t)
        # 在界面显示牌组
        self.DeckDict = rt
        self.ui.plainTextEdit.setPlainText(t)

    def Export(self):
        # 导出？？？？
        # 好像随时复习随时导出就行了
        # 当成个假功能吧
        pass

    def Select(self):
        # 选择但非选中
        num = self.ui.spinBox.value()
        tempL = []
        for name in self.DeckDict.keys():
            tempL.append(name)
        self.ui.lineEdit.setText(tempL[num])
        self.selectedDeck = self.DeckDict[tempL[num]]
        # print(self.selectedDeck)

    def Choose(self):
        file = self.selectedDeck
        self.WinCD = WinCD(file)
        self.WinCD.show()
        self.hide()
        self.WinCD.HomeSignal.connect(self.show)


def test():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()


test()
