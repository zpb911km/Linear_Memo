# 现在在上python课，太他妈无聊了，于是决定从此开始写注释
from math import log
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup
from random import randint, sample
import os
import sys
import enum
import unicodedata
from threading import Thread

try:
    import pyttsx3

    # 初始化发音引擎
    engine = pyttsx3.init()
    engine.setProperty("rate", 120)
    engine.setProperty("volume", 1.0)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", "english")
except Exception:
    print("pyttsx3模块未安装，发音功能不可用")
    engine = None

DTFormat = r"%Y/%m/%d %H:%M"  # 存储时间的文本的格式，excel同款
spliter = "\t"  # 存储文件的分隔符
Ω = 0.95  # 经验权重，常数
Rchecktime = 0  # R==1时，抽查底数（越大越不易出现，等于0关闭抽查复习）
MaxCalcLimit = 300  # R==1的判断条件
ForgetLine = 0.4  # 遗忘标准（可调）
NewCardAdd = 10000  # 每次计算推荐多少全新的卡片

if sys.platform.startswith("linux"):
    PATH = r"./"

    def clean_screen():
        os.system("clear")

elif sys.platform.startswith("win"):
    PATH = r"E:\ServerSyncFiles"

    def clean_screen():
        os.system("cls")

else:
    print("不支持的操作系统类型")
    input()
    exit()


def speak(text):
    engine.say(text)
    engine.runAndWait()


def file_noRpl(filePath):
    f = open(filePath, "r", encoding="UTF-8")
    t = f.read()
    ls = t.split("\n")
    o = ""
    for i in range(len(ls)):
        for j in range(i + 1, len(ls)):
            try:
                if ls[i].split("<br />")[0] == ls[j].split("<br />")[0]:
                    ls.remove(ls[j])
            except Exception:
                pass

    for i in ls:
        o += i + "\n"

    f = open(filePath, "w", encoding="UTF-8")
    f.write(o[:-1])


def len_str(text):
    out = sum(
        2 if unicodedata.east_asian_width(char) in "FW" else 1 for char in text
    )
    return out


def center_str(text: str, length: int):
    out = (
        " " * int((length - len_str(text)) / 2)
        + text
        + " " * (length - int((length - len_str(text)) / 2) - len_str(text))
    )
    return out


class CTKey(enum.Enum):
    UP = enum.auto()
    DOWN = enum.auto()
    RIGHT = enum.auto()
    LEFT = enum.auto()
    ESC = enum.auto()
    ENTER = enum.auto()
    DELETE = enum.auto()
    BACK = enum.auto()
    TAB = enum.auto()


def getch() -> CTKey | str: ...


def init_term() -> None:
    global getch

    import sys

    if sys.platform.startswith("win"):
        import msvcrt

        # Overwrite global function "getch"
        def getch() -> CTKey | str:
            key = msvcrt.getch()
            try:
                s = key.decode()
                match ord(s):
                    case 27:
                        return CTKey.ESC
                    case 13:
                        return CTKey.ENTER
                    case 9:
                        return CTKey.TAB
                    case 8:
                        return CTKey.BACK
                    case _:
                        return s
            except UnicodeDecodeError:
                key = key + msvcrt.getch()
                if key == b"\x00\x07":
                    return CTKey.ESC
                s = key.decode("gbk")
                match s:
                    case "郒":
                        return CTKey.UP
                    case "郟":
                        return CTKey.DOWN
                    case "郖":
                        return CTKey.LEFT
                    case "郙":
                        return CTKey.RIGHT
                    case "郤":
                        return CTKey.DELETE
                    case _:
                        return s

    elif sys.platform.startswith("linux"):
        import functools
        import selectors
        import termios
        import tty

        sel: selectors.DefaultSelector = selectors.DefaultSelector()
        sel.register(sys.stdin, selectors.EVENT_READ)

        old_attr = termios.tcgetattr(sys.stdin)

        def _getch_impl() -> CTKey | bytes:
            key: bytes = sys.stdin.buffer.raw.read(1)
            if key == b"\n":
                return CTKey.ENTER
            elif key == b"\t":
                return CTKey.TAB
            elif (key_code := ord(key)) == 127:
                return CTKey.BACK
            elif key_code == 27:
                if not sel.select(0):
                    return CTKey.ESC
                elif (ch := sys.stdin.buffer.raw.read(1)) != b"[":
                    return ch
                else:
                    if (ch2 := sys.stdin.buffer.raw.read(1)) == b"A":
                        return CTKey.UP
                    elif ch2 == b"B":
                        return CTKey.DOWN
                    elif ch2 == b"C":
                        return CTKey.RIGHT
                    elif ch2 == b"D":
                        return CTKey.LEFT
                    elif ch2 == b"3" and sys.stdin.buffer.raw.read(1) == b"~":
                        return CTKey.DELETE
                    else:
                        return ch2
            else:
                return key

        # Overwrite global function "getch"
        @functools.wraps(_getch_impl)
        def getch() -> CTKey | str:
            tty.setcbreak(sys.stdin)
            ret = _getch_impl()
            termios.tcsetattr(sys.stdin, termios.TCSANOW, old_attr)
            return ret.decode() if isinstance(ret, bytes) else ret

    else:
        assert False, "Unsupported operating system"


class TUI_Structure:
    def __init__(self) -> None:
        self.columns = os.get_terminal_size().columns
        self.lines = os.get_terminal_size().lines
        self.count = 0
        self.Overdue = 0
        self.Sum = 0
        self.Front = ""
        self.Back = ""
        self.percent = 0.4  # 用小数表示

    def show(self):
        if self.percent > 1:
            self.percent = 1
        elif self.percent < 0:
            self.percent = 0
        terminalText = "┏"
        terminalText += "━" * (self.columns - 2) + "┓"
        terminalText += "\n"
        # line 0
        line = (
            "┃"
            + center_str(str(self.count), int(self.columns / 4) - 1)
            + center_str(str(self.Overdue), int(self.columns / 4) - 1)
            + center_str(str(self.Sum), int(self.columns / 4) - 1)
        )
        line += (
            " " * (self.columns - len_str(line) - 5)
            + "{:.2f}".format(self.percent)
            + "┃"
        )
        if len_str(line) > self.columns:
            terminalText += "┃" + " " * (self.columns - 2) + "┃"
        else:
            terminalText += line
        terminalText += "\n"
        # line 1
        terminalText += "┠" + "─" * (self.columns - 4) + "┬─┨" + "\n"
        # line 2
        for i in range(int((self.lines - 5) / 2)):
            line = "┃"
            try:
                word = self.Front.split("\n")[i]
            except Exception:
                word = ""
            line += center_str(word, self.columns - 4)
            nowLevel = ((self.lines - 4) - i) / (self.lines - 4)
            if nowLevel <= self.percent:
                line += "│█┃"
            else:
                line += "│ ┃"
            terminalText += line + "\n"
        # line front
        terminalText += "┠" + "─" * (self.columns - 4) + "┤"
        nowLevel = (self.lines - 4 - i - 1) / (self.lines - 4)
        if nowLevel <= self.percent:
            terminalText += "█┃"
        else:
            terminalText += " ┃"
        terminalText += "\n"
        # line spliter
        tempB = ""
        for t in self.Back.split("\n"):
            i = 0
            j = 0
            while len_str(t) > self.columns - 5:  # 折行
                while len_str(t[:j]) < self.columns - 5:
                    j += 1
                tempB += t[:j] + "\n"
                t = t[j:]
            tempB += t + "\n"
        self.Back = tempB.replace("\n\n", "\n")
        if self.Back.endswith("\n"):
            self.Back = self.Back[:-1]
        for i in range(self.lines - len(terminalText.split("\n")) - 1):
            line = "┃"
            try:
                meaning = self.Back.split("\n")[i]
            except Exception:
                meaning = ""
            line += center_str(meaning, self.columns - 4)
            nowLevel = (self.lines - len(terminalText.split("\n")) - 1) / (
                self.lines - 4
            )
            if nowLevel <= self.percent:
                line += "│█┃"
            else:
                line += "│ ┃"
            terminalText += line + "\n"
        # line back
        terminalText += "┗" + "━" * (self.columns - 4) + "┷━┛"
        print(terminalText)


# 计算数列
def listcalc(l1, calc, l2) -> list:
    out = []
    if isinstance(l2, list):
        match calc:
            case "+":
                for num in range(len(l1)):
                    out.append(l1[num] + l2[num])
            case "-":
                for num in range(len(l1)):
                    out.append(l1[num] - l2[num])
            case "*":
                for num in range(len(l1)):
                    out.append(l1[num] * l2[num])
            case "/":
                for num in range(len(l1)):
                    out.append(l1[num] / l2[num])
    else:
        match calc:
            case "+":
                for num in range(len(l1)):
                    out.append(l1[num] + l2)
            case "-":
                for num in range(len(l1)):
                    out.append(l1[num] - l2)
            case "*":
                for num in range(len(l1)):
                    out.append(l1[num] * l2)
            case "/":
                for num in range(len(l1)):
                    out.append(l1[num] / l2)
            case "**":
                for num in range(len(l1)):
                    out.append(l1[num] ** l2)
    return out


def OLS(x, y) -> float:
    k = (sum(listcalc(x, "*", y)) - sum(x) * sum(y) / len(x)) / (
        sum(listcalc(x, "*", x)) - (sum(x) ** 2) / len(x)
    )
    b = sum(y) / len(y) - k * sum(x) / len(x)
    Rs = 1 - sum(
        listcalc(
            listcalc(y, "-", listcalc(listcalc(x, "*", k), "+", b)), "**", 2
        )
    ) / sum(listcalc(listcalc(y, "-", (sum(y) / len(y))), "**", 2))
    Ss = sum(
        listcalc(
            listcalc(y, "-", listcalc(listcalc(x, "*", k), "+", b)), "**", 2
        )
    ) / sum(listcalc(listcalc(y, "-", (sum(y) / len(y))), "**", 2))
    return k, b, Rs, Ss


class card:
    """
    方法:
        创建
        从文本读出
        输出为文本
        复习操作
        更改操作
        判过期
    """

    # 给card对象多一些抽象，方便表达
    def __init__(
        self,
        F: str = "",
        B: str = "",
        T: str = datetime.now().strftime(DTFormat),
        H: str = "{:.2f}".format(ForgetLine),
        S: float = 0.4,
        Δ: float = 1,
        R: int = 0,
    ) -> None:
        self.basedata = [F, B, T, H, S, Δ, R]
        # 对位：         0，1，2，3，4，5，6
        # 我也不想做如此愚蠢的操作啊

    def out_text(self) -> str:
        # 文本输出card，方便存储
        text = ""
        for i in self.basedata:
            text += str(i) + spliter
        return text[:-1]

    def read_text(self, text) -> None:
        # 从文件读取卡片信息
        templist = text.split(spliter)
        self.basedata[0] = templist[0]
        self.basedata[1] = templist[1]
        self.basedata[2] = templist[2]
        self.basedata[3] = templist[3]
        self.basedata[4] = float(templist[4])
        self.basedata[5] = float(templist[5])
        self.basedata[6] = int(templist[6])
        # 啊，真烦

    def is_overtime(self) -> bool:
        # 判断是否过期
        # 随机复习
        if self.basedata[6] == 1:
            if randint(0, Rchecktime) == 1:
                return True
            else:
                return False
        elif self.basedata[6] == 2:
            if randint(0, int(Rchecktime / 2)) == 1:
                return True
            else:
                return False
        # 超时判断
        period = datetime.now() - datetime.strptime(self.basedata[2], DTFormat)
        if period.days < self.basedata[5]:
            # 不超时就没过期，不用复习
            return False
        # 新卡片计数加入
        if len(self.basedata[3].split(",")) == 1 and self.basedata[4] == 0.4:
            global NewCardAdd
            if NewCardAdd > 0:
                NewCardAdd -= 1
                return True
            else:
                return False
        # 其它情况全部复习
        return True

    def front(self) -> str:
        return self.basedata[0].replace("<br />", "\n")

    def setFront(self, text) -> None:
        self.basedata[0] = text.replace("\n", "<br />")

    def back(self) -> str:
        text = self.basedata[1]
        meanings = text.split("<split>")[0].replace("<br />", "\n")
        try:
            examples = text.split("<split>")[1].split("<br />")
            example = examples[randint(0, len(examples) - 1)]
            text = meanings + "\n" + example
        except IndexError:
            text = meanings
        return text

    def setBack(self, text) -> None:
        self.basedata[1] = text.replace("\n", "<br />")

    def S(self) -> float:
        return self.basedata[4]

    def Δ(self) -> float:
        return self.basedata[5]

    def R(self) -> int:
        return self.basedata[6]

    def review(
        self, feedback: float
    ) -> tuple[float, float]:  # 返回值表示是否解除过期状态
        """feedback∈[0,100]"""
        if abs(feedback - 100) <= 0.00000000000001:
            self.basedata[6] = 2
            return (100, self.basedata[5])
        if abs(feedback - 0) <= 0.00000000000001:
            self.basedata[2] = datetime.now().strftime(DTFormat)
            self.basedata[5] = 1
            return (self.basedata[4] * 100, self.basedata[5])
        self.basedata[3] += ",{:.2f}".format(feedback / 100)
        # 线性回归求bias
        y = [float(i) for i in self.basedata[3].split(",")]
        if len(y) <= 20:  # 新卡片保护
            bias = 0
        else:
            x = [i / len(y) for i in range(1, len(y) + 1)]
            _, _, _, Ss = OLS(x, y)
            bias = (Ss - 0.5) * 0.1
            # os.system('mshta vbscript:msgbox("!!!!!卡片旧了!!!!!",16,"卡片烂了")(window.close)')
        # 线性回归求bias
        # 核心三句
        S = Ω * feedback + (1 - Ω) * self.basedata[4] * 100
        Δ = self.basedata[5] * log(ForgetLine + bias) / log(S / 100)
        T = datetime.now().strftime(DTFormat)
        if Δ > MaxCalcLimit:
            R = 1
        else:
            R = self.basedata[6]
        # 判断永久记忆是否退化
        if R == 1 and Δ < MaxCalcLimit * 0.8:
            R = 0
            S = 40
            Δ = 1
            self.basedata[4] = S / 100
            self.basedata[5] = Δ
            self.basedata[2] = T
            self.basedata[6] = R
        if R == 2 and feedback <= 40:
            R = 0
            S = 40
            Δ = 1
            self.basedata[4] = S / 100
            self.basedata[5] = Δ
            self.basedata[2] = T
            self.basedata[6] = R
        if Δ <= 0:
            Δ = -Δ + 0.01
        if Δ > 1:
            self.basedata[4] = S / 100
            self.basedata[5] = Δ
            self.basedata[2] = T
            self.basedata[6] = R
            return (S, Δ)
        else:
            self.basedata[4] = S / 100
            self.basedata[5] = Δ
            self.basedata[6] = R
            return (S, Δ)


def custom_sort_key(card: card):
    return (card.basedata[4], -card.basedata[5])


def bulk_load(path) -> tuple[list[card], list[card]]:
    # 批量导入数据
    with open(path, "r", encoding="UTF-8") as file:
        txt = file.read()
        lines = txt.split("\n")
    Ov = []
    Ta = []
    for line in lines:
        c = card()
        c.read_text(line)
        if c.is_overtime():
            Ov.append(c)
        else:
            Ta.append(c)
    Ov.sort(key=custom_sort_key)
    return (Ov, Ta)


def bulk_save(path, clist: list[card]):
    # 批量导出数据
    text = ""
    for c in clist:
        text += c.out_text() + "\n"
    with open(path, "w", encoding="UTF-8") as file:
        file.write(text[:-1])


def rev_loop(Ov: list[card], Ta: list[card]):
    # 复习
    for c in sample(Ov, len(Ov)):
        clean_screen()
        print(len(Ov), len(Ov) + len(Ta))
        print(c.front())
        input()
        clean_screen()
        print(len(Ov), len(Ov) + len(Ta))
        print(c.front() + "\n\n" + c.back())
        while True:
            feedback = float(input(":")) * 10
            if feedback > 100 or feedback < 0:
                continue
            else:
                break
        if c.review(feedback):
            Ta.append(c)
            Ov.remove(c)
    return Ov, Ta


def Replace(text):
    rpl = [
        ["，", ","],
        ["。", "."],
        ["：", ":"],
        ["；", ";"],
        ["（", "("],
        ["）", ")"],
        ["……", "..."],
        ["、", ","],
        ["！", "!"],
        ["？", "?"],
        ["“", '"'],
        ["”", '"'],
        ["【", "["],
        ["】", "]"],
        ["`", "·"],
        ["<=", "≤"],
        [">=", "≥"],
    ]
    for pair in rpl:
        text = text.replace(pair[0], pair[1])
    return text


def word_inquiry(word: str):
    # bing 查单词
    url = f"https://cn.bing.com/dict/search?q={word}"

    web = get(url)
    t = BeautifulSoup(web.content, "html.parser")
    ans = t.head.find_all("meta")[3].attrs["content"].split("，")

    word = ans[0].split("必应词典为您提供")[-1]
    word = word.split("的释义")[0]

    outputA = str("")
    outputA += word + "\t"

    try:
        meaning = (
            t.body.find("div", "contentPadding")
            .find("div", "content", "b_cards")
            .find("div", "rs_area", "b_cards")
            .find("div", "lf_area")
            .find("div", "qdef")
            .find("ul")
            .find_all("li")
        )
    except AttributeError:
        raise Exception("No such word!!")

    for line in meaning:
        prop = line.find("span", "pos").string.strip()
        mean = line.find("span", "def", "b_regtxt").find("span").string.strip()
        if "网" in prop:
            prop = "网:"
        if line == meaning[-1]:
            outputA += Replace(prop) + Replace(mean)
        else:
            outputA += Replace(prop) + Replace(mean) + "<br />"
    example_sentences = (
        t.body.find("div", "contentPadding")
        .find("div", "content", "b_cards")
        .find("div", "rs_area", "b_cards")
        .find("div", "lf_area")
        .find("div", "se_div")
        .find_all("div", "se_li")
    )
    sentences = []
    for sentence in example_sentences:
        sentence = sentence.find("div", "se_li1").find(
            "div", "sen_en", "b_regtxt"
        )
        en_sentence = ""
        for word in sentence:
            if word.text.strip() == "":
                continue
            if word.text.strip() in [
                "!",
                ".",
                ",",
                "?",
                ";",
                ":",
                '"',
                "'",
                "(",
                ")",
                "-",
                "_",
                "[",
                "]",
                "{",
                "}",
                "<",
                ">",
                "/",
            ]:
                en_sentence += word.text.strip()
            else:
                en_sentence += " " + word.text.strip()
        sentences.append(en_sentence[1:])
    outputA += "<split>"
    for s in sentences:
        outputA += Replace(s) + "<br />"
    return outputA[:-6]


def qetch():
    answer = getch()
    if answer == "q":
        raise KeyboardInterrupt
    else:
        return answer


def cardDBG(c: card):
    if 0:
        print("S=" + str(c.S()) + "\tΔ=" + str(c.Δ()))


if __name__ == "__main__":
    init_term()
    count = 0
    files = []
    for A, B, C in os.walk(PATH):
        for i in C:
            f = os.path.join(A, i)
            if f.endswith(".NMF"):
                files.append(f)
    for n, i in enumerate(files):
        print(n, ":", i)
    filePath = files[int(input(":"))]
    # filePath = files[0]
    file_noRpl(filePath)
    while True:
        print("\nAdd, Review or Quit[a/A/r/q]:", end="")
        i = getch()
        if i == "A":
            try:
                while True:
                    OverdueCardList, TaciturnCardList = bulk_load(filePath)
                    CardList = OverdueCardList + TaciturnCardList
                    F = input("\n-->")
                    B = input("\n==>")
                    New = CardList + [card(F, B)]
                    bulk_save(filePath, New)
            except KeyboardInterrupt:
                continue
        if i == "a":
            try:
                while True:
                    OverdueCardList, TaciturnCardList = bulk_load(filePath)
                    CardList = OverdueCardList + TaciturnCardList
                    word = input("-->")
                    try:
                        t = word_inquiry(word)
                    except Exception as e:
                        print("发生错误，大概是单词不存在：", e)
                        continue
                    F = t.split("\t")[0]
                    B = t.split("\t")[1]
                    print(F)
                    print(B)
                    New = CardList + [card(F, B)]
                    bulk_save(filePath, New)
            except KeyboardInterrupt:
                pass
        elif i == "r":
            OverdueCardList, TaciturnCardList = bulk_load(filePath)
            try:
                while len(OverdueCardList) > 0:
                    remove_flag = False
                    c = OverdueCardList[
                        randint(0, min(len(OverdueCardList) - 1, 3))
                    ]  # 前三个里边抽取
                    clean_screen()
                    win = TUI_Structure()
                    # win.lines -= 1
                    win.count = count
                    win.Overdue = len(OverdueCardList)
                    win.Sum = len(OverdueCardList) + len(TaciturnCardList)
                    win.Front = c.front()
                    win.show()
                    cardDBG(c)
                    lst = [
                        "a",
                        "s",
                        "d",
                        "f",
                        "g",
                        "h",
                        "j",
                        "k",
                        "l",
                        ";",
                        "'",
                    ]
                    # lst = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
                    feedback = 40
                    while True:
                        key = qetch()
                        if key == " ":
                            break
                        elif key == "`":
                            remove_flag = True
                            break
                        elif key in lst:
                            feedback = lst.index(key) * 10
                            if feedback > 100 or feedback < 0:
                                continue
                        elif key == "t":
                            task = Thread(
                                target=speak, args=[win.Front.split("\n")[0]]
                            )
                            task.run()
                        else:
                            if key == CTKey.UP:
                                feedback += 1
                            elif key == CTKey.DOWN:
                                feedback -= 1
                        win.percent = feedback / 100
                        clean_screen()
                        win.show()
                        cardDBG(c)
                    clean_screen()
                    win.Back = c.back()
                    win.show()
                    cardDBG(c)
                    while True:
                        key = qetch()
                        if key == " ":
                            break
                        elif key == "`":
                            remove_flag = True
                            break
                        elif key in lst:
                            feedback = lst.index(key) * 10
                            if feedback > 100 or feedback < 0:
                                continue
                        elif key == "t":
                            task = Thread(
                                target=speak, args=[win.Front.split("\n")[0]]
                            )
                            task.run()
                        else:
                            if key == CTKey.UP:
                                feedback += 1
                            elif key == CTKey.DOWN:
                                feedback -= 1
                        win.percent = feedback / 100
                        clean_screen()
                        win.show()
                        cardDBG(c)
                    if remove_flag:
                        OverdueCardList.remove(c)
                        continue
                    c.review(feedback)
                    bulk_save(filePath, OverdueCardList + TaciturnCardList)
                    OverdueCardList, TaciturnCardList = bulk_load(filePath)
                    count += 1
            except KeyboardInterrupt:
                clean_screen()
            finally:
                bulk_save(filePath, OverdueCardList + TaciturnCardList)
        elif i == "q":
            break
        else:
            break
