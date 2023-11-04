from UI.Start_Menu import Ui_MainWindow as WindowST
from UI.Add_Card import Ui_MainWindow as WindowAC
from UI.Chosen_Deck import Ui_MainWindow as WindowCD
from UI.Front import Ui_MainWindow as WindowF
from UI.Back import Ui_MainWindow as WindowB
from UI.Detail import Ui_MainWindow as WindowDT
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtGui import QFont, QShortcut, QKeySequence
import webbrowser
from controler import bulk_load, bulk_save, card, word_inquiry
from random import randint
import os
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 120)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


class WinAC(QMainWindow):
    refreshSignal = Signal()

    def __init__(self, path) -> None:
        super().__init__()
        self.ui = WindowAC()
        self.ui.setupUi(self)
        self.path = path
        self.cardList: list = bulk_load(self.path)[0] + bulk_load(self.path)[1]
        self.ui.actionHome.triggered.connect(self.home)
        self.ui.pushButton.clicked.connect(self.addCard)
        self.ui.pushButton_3.clicked.connect(self.clear)
        self.ui.pushButton_2.clicked.connect(self.inquiry)
        # 创建快捷键
        self.ShortAD = QShortcut(QKeySequence("Alt+O"), self)
        # 给快捷键设置信号事件
        self.ShortAD.activated.connect(self.addCard)
        self.ShortIQ = QShortcut(QKeySequence("Alt+I"), self)
        self.ShortIQ.activated.connect(self.inquiry)
        self.ui.textEdit.setFont(QFont([u"Cascadia Mono"], 24))
        self.ui.textEdit_2.setFont(QFont([u"Cascadia Mono"], 24))

    def home(self):
        self.close()
        self.refreshSignal.emit()

    def addCard(self):
        F = self.ui.textEdit.toPlainText().replace('\n', '<br />')
        B = self.ui.textEdit_2.toPlainText().replace('\n', '<br />')
        newCard = card(F, B)
        self.cardList.append(newCard)
        bulk_save(self.path, self.cardList)
        self.ui.textEdit.setText("")
        self.ui.textEdit_2.setText("")

    def clear(self):
        self.ui.textEdit.setText("")
        self.ui.textEdit_2.setText("")

    def inquiry(self):
        word = self.ui.textEdit.toPlainText()
        F, B = word_inquiry(word).split('\t')
        self.ui.textEdit.setText(F)
        self.ui.textEdit_2.setText(B)


class WinCD(QMainWindow):
    HomeSignal = Signal(str)

    def __init__(self, path, parent) -> None:
        super().__init__()
        self.path = path
        self.par = parent
        self.ui = WindowCD()
        self.ui.setupUi(self)
        self.deckName = path.split('\\')[-1].split('.')[0]
        self.ui.label.setText(self.deckName)
        self.Ov, self.Ta = bulk_load(self.path)
        self.ui.label_4.setText(str(len(self.Ov)))
        self.ui.label_5.setText(str(len(self.Ov) + len(self.Ta)))
        self.ui.pushButton_2.clicked.connect(self.Review)
        self.ui.actionHome.triggered.connect(self.Home)
        self.ui.pushButton_3.clicked.connect(self.Detail)
        self.ui.pushButton.clicked.connect(self.AddCard)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.Review)
        QShortcut(QKeySequence("Ctrl+A"), self).activated.connect(self.AddCard)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.Detail)

    def AddCard(self):
        self.A = WinAC(self.path)
        self.A.show()
        self.A.refreshSignal.connect(self.refresh)

    def refresh(self):
        self.Ov, self.Ta = bulk_load(self.path)
        self.ui.label_4.setText(str(len(self.Ov)))
        self.ui.label_5.setText(str(len(self.Ov) + len(self.Ta)))

    def Detail(self):
        self.Ov, self.Ta = bulk_load(self.path)
        text = ''
        clist = self.Ov + self.Ta
        for c in clist:
            text += c.out_text() + '\n'
        self.D = WinDT(text[:-1], self.path)
        self.D.show()

    def Review(self, seq=0):  # review
        self.Ov, self.Ta = bulk_load(self.path)
        self.ui.label_4.setText(str(len(self.Ov)))
        self.ui.label_5.setText(str(len(self.Ov) + len(self.Ta)))
        self.Ov = sorted(self.Ov, key=lambda c: (c.S(), -c.R()))
        '''
        l = 0
        for i in self.Ov:
            if i.S() == l:
                continue
            print(i.S(), end=' ')
            l = i.S()
        '''
        if len(self.Ov) == 0:
            return None
        if seq == 0:
            self.n = randint(0, min(10, len(self.Ov) - 1))  # randint(0, len(self.Ov) - 1)
        else:
            self.n = self.nf
        self.c: card = self.Ov[self.n]
        self.subReview1()

    def subReview1(self):
        self.F = WinF(self, self.c.front(), self.deckName)
        self.F.showMaximized()
        self.F.OKSignal.connect(self.subReview2)
        self.F.BackSignal.connect(self.subReview4)
        self.F.HomeSignal.connect(self.Home)

    def subReview2(self):
        self.B = WinB(self, self.c.front(), self.c.back(), self.deckName)
        self.B.showMaximized()
        self.B.Reviewed.connect(self.subReview3)
        self.B.BackSignal.connect(self.subReview4)
        self.B.HomeSignal.connect(self.Home)

    def subReview3(self, feedback, F, B):
        if feedback == 748.0:
            self.Ov.remove(self.c)
            self.nf = self.n
            bulk_save(self.path, self.Ov + self.Ta)
            self.Review()
        else:
            self.c.review(feedback)
            self.c.setFront(F)
            self.c.setBack(B)
            # print(self.c.out_text())
            bulk_save(self.path, self.Ov + self.Ta)
            self.nf = self.n
            if self.n < len(self.Ov):
                self.n += 1
                self.Review()
            else:
                self.close()

    def subReview4(self):
        self.Review(1)

    def Home(self):
        self.HomeSignal.emit('')
        self.par.show()
        self.close()


class WinF(QMainWindow):
    OKSignal = Signal()
    BackSignal = Signal()
    HomeSignal = Signal()

    def __init__(self, parent, t: str, title: str) -> None:
        super().__init__(parent=parent)
        self.ui = WindowF()
        self.ui.setupUi(self)
        self.ui.textEdit.setText(t)
        if 'file:///' in t:
            self.ui.textEdit.append("<img src=\"path\" />".replace('path', t.split('file:///')[-1]))
            self.ui.textEdit.setFont(QFont([u"Cascadia Mono"], 4))
        else:
            self.ui.textEdit.setFont(QFont([u"Cascadia Mono"], 24))
        self.t = t
        self.ui.pushButton.clicked.connect(self.turn)
        self.ui.actionBack.triggered.connect(self.back)
        self.ui.actionHome.triggered.connect(self.home)
        self.setWindowTitle(title)
        self.ui.pushButton_2.clicked.connect(self.speak)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.speak)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.turn)
        # self.setGeometry(0, 0, 1920, 1080)
        # self.ui.textEdit.textChanged.connect(self.ui.textEdit.setText(self.t))

    def speak(self):
        engine.say(self.t.split('\n')[0])
        engine.runAndWait()

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
    Reviewed = Signal(float, str, str)
    BackSignal = Signal()
    HomeSignal = Signal()

    def __init__(self, parent, tf: str, tb: str, title: str) -> None:
        super().__init__(parent=parent)
        self.ui = WindowB()
        self.ui.setupUi(self)
        self.ui.textEdit.setText(tf)
        self.ui.textEdit_2.setText(tb)
        if 'file:///' in tf:
            self.ui.textEdit.append("<img src=\"path\" />".replace('path', tf.split('file:///')[-1]))
            self.ui.textEdit.setFont(QFont([u"Cascadia Mono"], 4))
        else:
            self.ui.textEdit.setFont(QFont([u"Cascadia Mono"], 24))
        if 'file:///' in tb:
            self.ui.textEdit_2.append("<img src=\"path\" />".replace('path', tb.split('file:///')[-1]))
            self.ui.textEdit_2.setFont(QFont([u"Cascadia Mono"], 4))
        else:
            self.ui.textEdit_2.setFont(QFont([u"Cascadia Mono"], 24))
        self.ui.pushButton.clicked.connect(self.next)
        self.ui.verticalSlider.valueChanged.connect(self.percent)
        self.ui.actionBack.triggered.connect(self.back)
        self.ui.actionHome.triggered.connect(self.home)
        self.ui.pushButton_3.clicked.connect(self.delet)
        self.setWindowTitle(title)
        QShortcut(QKeySequence("Ctrl+Enter"), self).activated.connect(self.next)
        QShortcut(QKeySequence("Ctrl+Delete"), self).activated.connect(self.delet)

    def delet(self):
        v = 748.0
        F = self.ui.textEdit.toPlainText().replace('\n\ufffc', '')
        B = self.ui.textEdit_2.toPlainText().replace('\n\ufffc', '')
        self.Reviewed.emit(v, F, B)
        self.close()

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
        v = self.ui.verticalSlider.value()
        F = self.ui.textEdit.toPlainText().replace('\n\ufffc', '')
        B = self.ui.textEdit_2.toPlainText().replace('\n\ufffc', '')
        self.Reviewed.emit(v, F, B)
        self.close()


class WinDT(QMainWindow):
    def __init__(self, text, path) -> None:
        super().__init__()
        self.ui = WindowDT()
        self.ui.setupUi(self)
        self.path = path
        self.ui.plainTextEdit.setPlainText(text)
        self.ui.plainTextEdit.textChanged.connect(self.save)
        self.ui.actionHome_2.triggered.connect(self.home)

    def home(self):
        self.close()

    def save(self):
        text = self.ui.plainTextEdit.toPlainText()
        with open(self.path, 'w', encoding='UTF-8') as file:
            file.write(text)


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
        font = self.ui.plainTextEdit.font()
        font.setPointSize(12)
        self.ui.plainTextEdit.setFont(font)
        self.ui.actionLoad.triggered.connect(self.Load)
        self.ui.actionExport.triggered.connect(self.Export)
        self.ui.spinBox.valueChanged.connect(self.Select)
        self.ui.pushButton_2.clicked.connect(self.Choose)
        self.ui.actionGithub_Link.triggered.connect(self.gitLink)
        self.ui.lineEdit.textChanged.connect(self.Rename)
        self.ui.pushButton.clicked.connect(self.addDeck)
        self.ui.pushButton_5.clicked.connect(self.deletDeck)
        # 定义一些变量（类）
        self.DeckDict = {}
        self.selectedDeck = ''
        try:
            self.initLoad()
            self.Select()
        except Exception:
            pass

    def gitLink(self):
        webbrowser.open('https://github.com/zpb911km/Linear_Memo/tree/Z01')

    def initLoad(self):
        # 导入文件夹
        try:
            path = open(r'E:\\myfiles\\python\\Linear_Memo\\src\\lastPath.txt', 'r', encoding='UTF-8').read()
        except FileExistsError:
            return None
        # print(path)
        if len(path) == 0:
            return None
        rt = {}
        files = os.listdir(path)
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path) and str(file).split('.')[1] == 'nmf':
                rt[str(file).split('.')[0]] = file_path
        self.DeckDict = rt
        # print(rt.keys())
        tempL = []
        for name in self.DeckDict.keys():
            tempL.append(name)
        t = 'index\tname\t\tOvertime\tsum\n'
        for num, name in enumerate(rt.keys()):
            try:
                self.Ov, self.Ta = bulk_load(rt[name])
                t += str(num) + '\t' + name + '\t\t' + str(len(self.Ov)) + '\t' + str(len(self.Ov) + len(self.Ta)) + '\n'
            except IndexError:
                print(rt[name])
                t += str(num) + '\t' + name + '\t\t' + 'error' + '\t' + 'error' + '\n'
        # print(t)
        # 在界面显示牌组
        self.ui.plainTextEdit.setPlainText(t)

    def Load(self):
        # 导入文件夹
        path = QFileDialog.getExistingDirectory(self, "选择文件夹", r"E:\myfiles\python\Linear_Memo\src")
        open(r'E:\myfiles\python\Linear_Memo\src\lastPath.txt', 'w', encoding='UTF-8').write(path)
        # print(path)
        rt = {}
        files = os.listdir(path)
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path) and str(file).split('.')[1] == 'nmf':
                rt[str(file).split('.')[0]] = file_path
        self.DeckDict = rt
        # print(rt.keys())
        tempL = []
        for name in self.DeckDict.keys():
            tempL.append(name)
        t = 'index\tname\t\tOvertime\tsum\n'
        for num, name in enumerate(rt.keys()):
            try:
                self.Ov, self.Ta = bulk_load(rt[name])
                t += str(num) + '\t' + name + '\t\t' + str(len(self.Ov)) + '\t' + str(len(self.Ov) + len(self.Ta)) + '\n'
            except IndexError:
                print(rt[name])
                t += str(num) + '\t' + name + '\t\t' + 'error' + '\t' + 'error' + '\n'
        # print(t)
        # 在界面显示牌组
        self.ui.plainTextEdit.setPlainText(t)

    def Export(self):
        # 导出？？？？
        # 好像随时复习随时导出就行了
        # 当成个假功能吧
        pass

    def Select(self):
        # 选择但非选中
        try:
            self.ui.lineEdit.textChanged.disconnect(self.Rename)
        except RuntimeError:
            pass
        num = self.ui.spinBox.value()
        tempL = []
        for name in self.DeckDict.keys():
            tempL.append(name)
        try:
            self.ui.lineEdit.setText(tempL[num])
            self.selectedDeck = self.DeckDict[tempL[num]]
        except IndexError:
            self.ui.lineEdit.setText('IndexError!')
        self.ui.lineEdit.textChanged.connect(self.Rename)
        t = 'index\tname\t\tOvertime\tsum\n'
        for num, name in enumerate(self.DeckDict.keys()):
            try:
                self.Ov, self.Ta = bulk_load(self.DeckDict[name])
                t += str(num) + '\t' + name + '\t\t' + str(len(self.Ov)) + '\t' + str(len(self.Ov) + len(self.Ta)) + '\n'
            except IndexError:
                print(self.DeckDict[name])
                t += str(num) + '\t' + name + '\t\t' + 'error' + '\t' + 'error' + '\n'
        self.ui.plainTextEdit.setPlainText(t)

    def Choose(self):
        file = self.selectedDeck
        self.WinCD = WinCD(file, self)
        self.WinCD.show()
        # self.hide()
        self.WinCD.HomeSignal.connect(self.initLoad)

    def Rename(self):
        file = self.selectedDeck
        name = self.ui.lineEdit.text()
        forname = file.split('\\')[-1].split('.')[0]
        try:
            file = file.split('\\')[0] + '\\' + file.split('\\')[1][:-3].replace(forname, name) + file[-3:]
        except IndexError:
            file = name + '.nmf'
        if len(name) == 0:
            return None
        del self.DeckDict[forname]
        self.DeckDict[name] = file
        os.rename(self.selectedDeck, file)
        self.selectedDeck = file
        t = 'index\tname\t\tOvertime\tTaciturn\n'
        for num, name in enumerate(self.DeckDict.keys()):
            self.Ov, self.Ta = bulk_load(self.DeckDict[name])
            t += str(num) + '\t' + name + '\t\t' + str(len(self.Ov)) + '\t' + str(len(self.Ov) + len(self.Ta)) + '\n'
        self.ui.plainTextEdit.setPlainText(t)
        del file, name, forname

    def addDeck(self):
        self.DeckDict['newDeck'] = self.selectedDeck.replace(self.selectedDeck.split('\\')[-1], 'newDeck.nmf')
        open(self.selectedDeck.replace(self.selectedDeck.split('\\')[-1], 'newDeck.nmf'), 'w', encoding='UTF-8').write('		2023/06/08 17:40	0.0	1.0	1.0	0')
        t = 'index\tname\t\tOvertime\tTaciturn\n'
        for num, name in enumerate(self.DeckDict.keys()):
            self.Ov, self.Ta = bulk_load(self.DeckDict[name])
            t += str(num) + '\t' + name + '\t\t' + str(len(self.Ov)) + '\t' + str(len(self.Ov) + len(self.Ta)) + '\n'
        self.ui.plainTextEdit.setPlainText(t)
        self.Select()

    def deletDeck(self):
        os.rename(self.selectedDeck, self.selectedDeck.replace('nmf', 'txt'))
        del self.DeckDict[self.selectedDeck.split('\\')[-1].split('.')[0]]
        t = 'index\tname\t\tOvertime\tTaciturn\n'
        for num, name in enumerate(self.DeckDict.keys()):
            self.Ov, self.Ta = bulk_load(self.DeckDict[name])
            t += str(num) + '\t' + name + '\t\t' + str(len(self.Ov)) + '\t' + str(len(self.Ov) + len(self.Ta)) + '\n'
        self.ui.plainTextEdit.setPlainText(t)
        self.Select()


def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()


if __name__ == '__main__':
    main()
