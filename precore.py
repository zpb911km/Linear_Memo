from math import log
from typing import NamedTuple
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup
from os import system
from time import sleep
from random import randint
import pyttsx3
from operator import attrgetter

engine = pyttsx3.init()
engine.setProperty('rate', 120)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
Path = r'E:\\myfiles\\python\\Linear_Memo\\test.nmf'
DTFormat = r'%Y/%m/%d %H:%M'
spliter = '\t'
splitern = '\t'
Ω = 0.95
Rchecktime = 30
MaxCalcLimit = 300
ForgetLine = 0.4
OverdueCardList = []
TaciturnCardList = []


class card(NamedTuple):
    F: str
    B: str
    T: datetime
    D: float
    S: float
    Δ: float
    I: float


def Replace(text):
    rpl = [
        ['，', ','],
        ['。', '.'],
        ['：', ':'],
        ['；', ';'],
        ['（', '('],
        ['）', ')'],
        ['……', '...'],
        ['、', ','],
        ['！', '!'],
        ['？', '?'],
        ['“', '"'],
        ['”', '"'],
        ['【', '['],
        ['】', ']'],
        ['`', '·'],
        ['<=', '≤'],
        ['>=', '≥']
    ]
    for pair in rpl:
        text = text.replace(pair[0], pair[1])
    return text


def checkRepeat(text: str) -> str:
    lt = text.split('\n')
    o = ''
    for i in range(len(lt)):
        for j in range(i+1, len(lt)):
            if lt[i].split('<br />')[0] == lt[j].split('<br />')[0]:
                lt.remove(lt[j])
    for i in lt:
        o += i + '\n'
    return o[:-1]


def word_inquiry(word: str):
    url = f'https://cn.bing.com/dict/search?q={word}'

    web = get(url)
    t = BeautifulSoup(web.content, 'lxml')
    ans = t.head.find_all("meta")[3].attrs['content'].split('，')

    word = ans[0].split('必应词典为您提供')[-1]
    word = word.split('的释义')[0]
    try:
        pronun = ans[1] + '  ' + ans[2]
    except Exception:
        if len(word.split(' ')) > 1:
            pronun = ' '
            pass
        else:
            raise Exception('No such word!!')

    outputA = str('')
    outputA += word + '<br />' + pronun + '\t'

    try:
        meaning = t.body.find('div', 'contentPadding')\
                    .find('div', 'content', 'b_cards')\
                    .find('div', 'rs_area', 'b_cards')\
                    .find('div', 'lf_area')\
                    .find('div', 'qdef')\
                    .find('ul')\
                    .find_all('li')
    except AttributeError:
        raise Exception('No such word!!')

    for line in meaning:
        prop = line.find('span', 'pos').string.strip()
        mean = line.find('span', 'def', 'b_regtxt').find('span').string.strip()
        if '网' in prop:
            prop = '网:'
        if line == meaning[-1]:
            outputA += Replace(prop) + Replace(mean) + '\t '
        else:
            outputA += Replace(prop) + Replace(mean) + '<br />'
    return outputA


def load(path) -> list[card]:
    with open(path, 'r', encoding='UTF-8') as file:
        txt = file.read()
    l = txt.split('\n')
    o = ''
    for i in range(len(l)):
        for j in range(i+1, len(l)):
            try:
                if l[i].split('<br />')[0] == l[j].split('<br />')[0]:
                    l.remove(l[j])
            except Exception:
                pass
    for i in l:
        o += i + '\n'
    txt = o[:-1]
    cl = []
    lines = txt.split('\n')
    for line in lines:
        a = line.split(spliter)
        if len(a) != 7:
            return []
        cl.append(card._make(a))
    return cl


def save(cl, path) -> None:
    txt = ''
    for c in cl:
        for i in tuple(c):
            txt += str(i) + splitern
        txt = txt[:-len(splitern)]
        txt += '\n'
    with open(path, 'w', encoding='UTF-8') as file:
        file.write(Replace(checkRepeat(txt[:-1])))


def addNewWordCard() -> list[card]:
    word = input('-->')
    t = word_inquiry(word)
    F = t.split('\t')[0]
    B = t.split('\t')[1]
    print(F)
    print(B)
    T = datetime.now().strftime(DTFormat)
    D = 0.0
    i = input('先验稳定性:')
    if len(i) == 0:
        S = 2
    else:
        S = float(i)/10
    Δ = 1
    if S - 0 <= 0.00001:
        I = 2
    else:
        I = 0
    nc = card(F, B, T, D, S, Δ, I)
    return [nc]


def Calculate(cl) -> (list[card], list[card]):
    Overdue = []
    Taciturn = []
    for c in cl:
        lasttime = datetime.strptime(c.T, DTFormat)
        period = datetime.now() - lasttime
        if period.days < eval(c.Δ):
            if float(c.Δ) >= 300:
                Taciturn.append(card(c.F, c.B, c.T, c.D, c.S, c.Δ, 1))
            else:
                Taciturn.append(c)
        else:
            Overdue.append(c)
    return (Overdue, Taciturn)


def Review():
    global OverdueCardList, TaciturnCardList
    OverdueCardList = sorted(OverdueCardList, key=attrgetter('Δ'))
    TaciturnCardList = sorted(TaciturnCardList, key=attrgetter('Δ'))
    if len(OverdueCardList) == 0:
        save(TaciturnCardList, Path)
        print('Over!', datetime.now().strftime(r'%Y/%m/%d %H:%M:%S'))
        return None
    while len(OverdueCardList):
        print(len(OverdueCardList), '  ', len(TaciturnCardList), '\n')
        c = OverdueCardList[randint(0, len(OverdueCardList) - 1)]
        if int(c.I) == 1:
            if randint(0, MaxCalcLimit) != 1:
                continue
        elif int(c.I) == 2:
            if randint(0, Rchecktime) != 1:
                continue
        F = c.F.lower()
        print(F.replace('<br />', '\n'))
        code = input()
        if code == 'e' or code == 'E':
            F = '#edit#' + F
        engine.say(F.split('<br />')[0])
        engine.runAndWait()
        print(c.B.replace('<br />', '\n'))
        try:
            i = float(input('\n:'))
        except Exception:
            print('数字!!!')
            system('cls')
            continue
        if abs(i - 748) < 0.01:
            OverdueCardList.remove(c)
            system('cls')
            continue
        if abs(i - 886) < 0.01:
            save(OverdueCardList + TaciturnCardList, Path)
            exit()
        if i - 0 <= 0.00001:
            I = 2
        else:
            I = 0
        if i <= 0 or i > 10:
            raise ValueError
        S = Ω * i / 10 + (1 - Ω) * float(c.S) / 10
        Δ = float(c.Δ) * log(ForgetLine + float(c.D))/log(S)
        T = datetime.now().strftime(DTFormat)
        if Δ > MaxCalcLimit:
            I = 1
        n = card(F, c.B, T, c.D, S, Δ, I)
        print(Δ)
        if Δ < 0:
            raise ValueError
        if Δ < 1:
            sleep(1)
            OverdueCardList.remove(c)
            OverdueCardList.append(n)
            system('cls')
            continue
        OverdueCardList.remove(c)
        TaciturnCardList.append(n)
        save(OverdueCardList + TaciturnCardList, Path)
        sleep(1)
        system('cls')


def NewcardTEMP():
    CardList = load(Path)
    try:
        NEW = addNewWordCard()
        save(CardList + NEW, Path)
    except Exception as E:
        print(E)


def RevLoop():
    CurrentCard = load(Path)
    global OverdueCardList, TaciturnCardList
    OverdueCardList, TaciturnCardList = Calculate(CurrentCard)
    try:
        Review()
    finally:
        save(OverdueCardList + TaciturnCardList, Path)


if __name__ == '__main__':
    while True:
        i = input('\nAdd or Review :')
        if i == 'A':
            try:
                while True:
                    NewcardTEMP()
            except KeyboardInterrupt:
                pass
        elif i == 'R':
            try:
                while True:
                    RevLoop()
                    sleep(10)
            except KeyboardInterrupt:
                pass
        elif i == 'Q':
            CurrentCard = load(Path)
            OverdueCardList, TaciturnCardList = Calculate(CurrentCard)
            save(OverdueCardList, Path)
            CurrentCard = load(Path)
            save(CurrentCard + TaciturnCardList, Path)
            break
