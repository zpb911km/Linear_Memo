# Linear_Memo
A tool may assist your memory

## 原理

- 根据记忆半衰理论，代入点解出对应负指数函数，推算下一次复习时刻

## 优点 （相比Anki）

- 能够线性反馈记忆情况
- 无硬性复习安排

## 现状

- 开发未完成
- 缺乏数据与理论支撑

## 程序功能

- 若要在Windows平台使用GUI界面，运行display.py （依赖于controler.py和UI/）
- 若只在控制台运行，可以运行controler.py（没有依赖）
- 若要在控制台模拟UI（也就是TUI），运行TUI_fully.py（没有依赖）

## reqirements

- pySide6
- webbrowser
- pyttsx3
- bs4
- requests
