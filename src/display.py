from UI.Start_Menu import Ui_MainWindow as WindowST
from UI.Add_Card import Ui_MainWindow as WindowAC
from UI.Chosen_Deck import Ui_MainWindow as WindowCD
from UI.review import Ui_MainWindow as WindowR
from UI.Detail import Ui_MainWindow as WindowDT
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtGui import QFont, QShortcut, QKeySequence
import webbrowser
from controler import bulk_load, bulk_save, card, word_inquiry
from random import randint
import os
import pyttsx3
import threading

engine = pyttsx3.init()
engine.setProperty('rate', 120)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
fontFamily = u"msyh"
globalCounter = 0


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
        self.ui.textEdit.setFont(QFont([fontFamily], 24))
        self.ui.textEdit_2.setFont(QFont([fontFamily], 24))

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

    def Review(self):  # review
        self.Ov, self.Ta = bulk_load(self.path)
        self.ui.label_4.setText(str(len(self.Ov)))
        self.ui.label_5.setText(str(len(self.Ov) + len(self.Ta)))
        self.R = WinR(self.path, self.deckName)
        self.R.show()

    def Home(self):
        self.HomeSignal.emit('')
        self.par.show()
        self.close()


class WinR(QMainWindow):
    def __init__(self, path, name) -> None:
        super().__init__()
        self.ui = WindowR()
        self.ui.setupUi(self)
        self.path = path
        self.setWindowTitle(name)
        self.status = 0  # 0:front;  1:back
        self.Ov, self.Ta = bulk_load(self.path)
        self.ui.lcdNumber.display(str(len(self.Ov)))
        self.ui.lcdNumber_2.display(str(len(self.Ov) + len(self.Ta)))
        self.ui.pushButton_2.clicked.connect(self.next)
        self.ui.verticalSlider.valueChanged.connect(self.trace)
        self.ui.pushButton_3.clicked.connect(self.delete)
        self.ui.pushButton.clicked.connect(self.speak)
        QShortcut(QKeySequence("S"), self).activated.connect(self.speak)
        QShortcut(QKeySequence("Space"), self).activated.connect(self.next)
        QShortcut(QKeySequence("Q"), self).activated.connect(self.trace1)
        QShortcut(QKeySequence("W"), self).activated.connect(self.trace2)
        QShortcut(QKeySequence("E"), self).activated.connect(self.trace3)
        QShortcut(QKeySequence("R"), self).activated.connect(self.trace4)
        QShortcut(QKeySequence("T"), self).activated.connect(self.trace5)
        QShortcut(QKeySequence("Y"), self).activated.connect(self.trace6)
        QShortcut(QKeySequence("U"), self).activated.connect(self.trace7)
        QShortcut(QKeySequence("I"), self).activated.connect(self.trace8)
        QShortcut(QKeySequence("O"), self).activated.connect(self.trace9)
        QShortcut(QKeySequence("P"), self).activated.connect(self.trace0)
        QShortcut(QKeySequence("Down"), self).activated.connect(self.traced)
        QShortcut(QKeySequence("Up"), self).activated.connect(self.traceu)
        # 真他妈蠢爆了
        self.displayFront()

    def speak(self):
        engine.say(self.card.front().split('\n')[0])
        engine.runAndWait()

    def delete(self):
        self.Ov.remove(self.card)
        bulk_save(self.path, self.Ov + self.Ta)
        self.displayFront()

    def trace(self):
        v = self.ui.verticalSlider.value()
        if v == 100:
            v = -0
        self.ui.lcdNumber_3.display(v)

    def trace1(self):
        self.ui.verticalSlider.setValue(10)
        self.ui.lcdNumber_3.display(10)

    def trace2(self):
        self.ui.verticalSlider.setValue(20)
        self.ui.lcdNumber_3.display(20)

    def trace3(self):
        self.ui.verticalSlider.setValue(30)
        self.ui.lcdNumber_3.display(30)

    def trace4(self):
        self.ui.verticalSlider.setValue(40)
        self.ui.lcdNumber_3.display(40)

    def trace5(self):
        self.ui.verticalSlider.setValue(50)
        self.ui.lcdNumber_3.display(50)

    def trace6(self):
        self.ui.verticalSlider.setValue(60)
        self.ui.lcdNumber_3.display(60)

    def trace7(self):
        self.ui.verticalSlider.setValue(70)
        self.ui.lcdNumber_3.display(70)

    def trace8(self):
        self.ui.verticalSlider.setValue(80)
        self.ui.lcdNumber_3.display(80)

    def trace9(self):
        self.ui.verticalSlider.setValue(90)
        self.ui.lcdNumber_3.display(90)

    def trace0(self):
        self.ui.verticalSlider.setValue(100)
        self.ui.lcdNumber_3.display(100)

    def traced(self):
        self.ui.verticalSlider.setValue(self.ui.verticalSlider.value() - 1)
        self.ui.lcdNumber_3.display(self.ui.verticalSlider.value())

    def traceu(self):
        self.ui.verticalSlider.setValue(self.ui.verticalSlider.value() + 1)
        self.ui.lcdNumber_3.display(self.ui.verticalSlider.value())

    # 什么他妈的叫他妈的蠢爆了

    def displayFront(self):
        self.Ov, self.Ta = bulk_load(self.path)
        self.Ov = sorted(self.Ov, key=lambda c: (c.S(), -c.R()))
        if len(self.Ov) == 0:
            self.close()
        self.ui.lcdNumber.display(len(self.Ov))
        self.ui.lcdNumber_2.display(len(self.Ov + self.Ta))
        self.card: card = self.Ov[randint(0, min(10, len(self.Ov)))]
        self.ui.textEdit.setText(self.card.front())
        self.ui.textEdit_2.setText('')
        self.ui.textEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if 'file:///' in self.card.front():
            self.ui.textEdit.append("<img src=\"path\" />".replace('path', self.card.front().split('file:///')[-1]))
            font = self.ui.fontComboBox.currentFont()
            font.setPixelSize(10)
            self.ui.textEdit.setFont(font)
        else:
            font = self.ui.fontComboBox.currentFont()
            font.setPixelSize(self.ui.spinBox.value())
            self.ui.textEdit.setFont(font)
        self.ui.verticalSlider.setValue(40)
        if self.ui.checkBox.isChecked():
            self.ui.label.setText('|S='+str(self.card.S()))
            self.ui.label_2.setText('Δ='+str(self.card.Δ()))
            if self.card.R() == 0:
                tempstr = '......'
            elif self.card.R() == 1:
                tempstr = '!!!!!!'
            else:
                tempstr = '??????'
            self.ui.label_3.setText(tempstr)
        else:
            self.ui.label.setText(' ')
            self.ui.label_2.setText(' ')
            self.ui.label_3.setText(' ')
        if self.ui.checkBox_2.isChecked():
            try:
                task.join()
            except Exception:
                pass
            task = threading.Thread(target=self.speak)
            task.start()
        self.status = 1

    def displayBack(self):
        self.ui.textEdit_2.setText(self.card.back())
        if 'file:///' in self.card.back():
            self.ui.textEdit_2.append("<img src=\"path\" />".replace('path', self.card.back().split('file:///')[-1]))
            font = self.ui.fontComboBox.currentFont()
            font.setPixelSize(10)
            self.ui.textEdit_2.setFont(font)
        else:
            font = self.ui.fontComboBox.currentFont()
            font.setPixelSize(self.ui.spinBox.value())
            self.ui.textEdit_2.setFont(font)
        self.status = 0

    def reviewed(self):
        v = self.ui.verticalSlider.value()
        self.card.review(v)
        if len(self.ui.textEdit.toPlainText().replace('\n\ufffc', '')) > 0:
            self.card.setFront(self.ui.textEdit.toPlainText().replace('\n\ufffc', ''))
        if len(self.ui.textEdit_2.toPlainText().replace('\n\ufffc', '')) > 0:
            self.card.setBack(self.ui.textEdit_2.toPlainText().replace('\n\ufffc', ''))
        bulk_save(self.path, self.Ov + self.Ta)
        global globalCounter
        globalCounter += 1
        self.ui.lcdNumber_4.display(globalCounter)
        self.displayFront()

    def next(self):
        if self.status == 0:
            self.reviewed()
        else:
            self.displayBack()


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
            if os.path.isfile(file_path) and str(file).split('.')[1] == 'NMF':
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
            if os.path.isfile(file_path) and str(file).split('.')[1] == 'NMF':
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
        os.rename(self.selectedDeck, self.selectedDeck.replace('NMF', 'txt'))
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
