# 现在在上python课，太他妈无聊了，于是决定从此开始写注释
from math import log
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup
from os import system
from time import sleep
from random import randint, sample
import pyttsx3
from operator import attrgetter
DTFormat = r'%Y/%m/%d %H:%M'  # 存储时间的文本的格式，excel同款
spliter = '\t'  # 存储文件的分隔符
Ω = 0.95  # 经验权重，常数
Rchecktime = 150  # R==1时，抽查底数
MaxCalcLimit = 300  # R==1的判断条件
ForgetLine = 0.4  # 遗忘标准（可调？）
PATH = r'E:\myfiles\python\Linear_Memo\src\LMFiles\test.nmf'

class card():
    '''
    方法:
        创建
        从文本读出
        输出为文本
        复习操作
        更改操作
        判过期
    '''
    # 给card对象多一些抽象，方便表达
    def __init__(self, F: str = '', B: str = '', T: str = datetime.now().strftime(DTFormat), D: float = 0.0, S: float = 20.0, Δ: float = 1, R: int = 0) -> None:
        self.basedata = [F.lower(), B, T, D, S, Δ, R]
        # 对位：         0，        1，2，3，4，5，6
        # 我也不想做如此愚蠢的操作啊

    def out_text(self) -> str:
        # 文本输出card，方便存储
        text = ''
        for i in self.basedata:
            text += str(i) + spliter
        return text[:-1]
    
    def read_text(self, text) -> None:
        # 从文件读取卡片信息
        templist = text.split(spliter)
        self.basedata[0] = templist[0]
        self.basedata[1] = templist[1]
        self.basedata[2] = templist[2]
        self.basedata[3] = float(templist[3])
        self.basedata[4] = float(templist[4])
        self.basedata[5] = float(templist[5])
        self.basedata[6] = int(templist[6])
        # 啊，真烦

    def is_overtime(self) -> bool:
        # 判断是否过期
        if self.basedata[6] == 1:
            if randint(0, Rchecktime) == 1:
                return True
            else:
                return False
        elif self.basedata[6] == 2:
            if randint(0, Rchecktime/5) == 1:
                return True
            else:
                return False
        period = datetime.now() - datetime.strptime(self.basedata[2], DTFormat)
        if period.days < self.basedata[5]:
            # 不超时
            return False
        return True

    def front(self) -> str:
        return self.basedata[0].replace('<br />', '\n')
    
    def setFront(self, text) -> None:
        self.basedata[0] = text.replace('\n', '<br />')

    def back(self) -> str:
        return self.basedata[1].replace('<br />', '\n')
    
    def setBack(self, text) -> None:
        self.basedata[1] = text.replace('\n', '<br />')

    def S(self) -> str:
        return self.basedata[4]

    def Δ(self) -> str:
        return self.basedata[5]

    def review(self, feedback: float) -> bool:  # 返回值表示是否解除过期状态
        '''返回[1,100]'''
        if abs(feedback - 100) <= 0.00000000000001:
            self.basedata[6] = 2
            return None
        # 核心三句
        S = Ω * feedback + (1 - Ω) * self.basedata[4]*100
        Δ = self.basedata[5] * log(ForgetLine + self.basedata[3])/log(S/100)
        T = datetime.now().strftime(DTFormat)
        if Δ > MaxCalcLimit:
            R = 1
        else:
            R = self.basedata[6]
        # 判断永久记忆是否退化
        if R == 1 and Δ < MaxCalcLimit * 0.8:
            R = 0
            S = 20
            Δ = 1
        if R == 2 and feedback <= 30:
            R = 0
            S = 20
            Δ = 1
        self.basedata[4] = S/100
        self.basedata[5] = Δ
        self.basedata[2] = T
        self.basedata[6] = R
        # print(Δ)
        if Δ < 0:
            raise ValueError
        if Δ > 1:
            return True
        return False


def bulk_load(path) -> (list[card], list[card]):
    # 批量导入数据
    with open(path, 'r', encoding='UTF-8') as file:
        txt = file.read()
        lines = txt.split('\n')
    Ov = []
    Ta = []
    for line in lines:
        c = card()
        c.read_text(line)
        if c.is_overtime():
            Ov.append(c)
        else:
            Ta.append(c)
    return (Ov, Ta)


def bulk_save(path, clist):
    # 批量导出数据
    text = ''
    for c in clist:
        text += c.out_text() + '\n'
    with open(path, 'w', encoding='UTF-8') as file:
        file.write(text[:-1])


def rev_loop(Ov: list[card], Ta: list[card]):
    # 复习
    for c in sample(Ov, len(Ov)):
        system('cls')
        print(c.front())
        input()
        system('cls')
        print(c.front() + '\n\n' + c.back())
        feedback = int(input(':')) * 10
        if c.review(feedback):
            Ta.append(c)
            Ov.remove(c)
    return Ov, Ta


if __name__ == '__main__':
    OverdueCardList, TaciturnCardList = bulk_load(PATH)
    try:
        OverdueCardList, TaciturnCardList = rev_loop(OverdueCardList, TaciturnCardList)
    except KeyboardInterrupt:
        pass
    bulk_save(PATH, OverdueCardList + TaciturnCardList)
