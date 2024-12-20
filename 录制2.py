# --*-- coding: utf-8 --*--
import pickle
import sys
import pynput
from pynput import *
import time
import os

keyboard_mouse_list = []  # 定义事件列表
mouse_click = pynput.mouse.Controller()
keyboard_press = pynput.keyboard.Controller()


def save_file(keyboard_mouse_list, file_name="keyboard_mouse_list.pkl"):  # 把时间列表存到pkl文件里面
    with open(file_name, "wb") as f:
        pickle.dump(keyboard_mouse_list, f)
        print(format(f"{file_name}文件已保存"))


def load_file(filename='keyboard_mouse_list.pkl'):  # 读取pkl文件里面的列表
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            keyboard_mouse_list = pickle.load(f)
        print(f"已从 {filename} 加载点击位置")
        return keyboard_mouse_list
    else:
        print(f"文件 {filename} 不存在。")
        return None


def key_mouse_event():
    global start_time
    start_time = time.time()  # 定义时间的开始时间

    def on_click(x, y, button, pressed):
        # time.sleep(1)
        if pressed:
            global start_time
            content_list = []
            end_time = time.time()  # 定义事件的结束时间
            delay_time = end_time - start_time  # 得到本次的思考时间
            # print(delay_time, x, y, button, pressed)
            start_time = end_time  # 重新定义开始时间
            content_list.append('click')  # 添加点击事件类型到列表
            content_list.append(x)  # 添加点击位置到列表
            content_list.append(y)
            content_list.append(button)  # 添加点击按钮到列表
            content_list.append(delay_time)  # 添加思考事件到列表
            keyboard_mouse_list.append(content_list)  # 把本次完整的数据添加到大的事件列表
            print(content_list)

    def on_release(x, y, button, released):
        # time.sleep(1)
        if released:
            global start_time
            content_list = []
            end_time = time.time()  # 定义事件的结束时间
            delay_time = end_time - start_time  # 得到本次的思考时间
            # print(delay_time, x, y, button, pressed)
            start_time = end_time  # 重新定义开始时间
            content_list.append('release')  # 添加点击事件类型到列表
            content_list.append(button)  # 添加点击按钮到列表
            content_list.append(delay_time)  # 添加思考事件到列表
            keyboard_mouse_list.append(content_list)  # 把本次完整的数据添加到大的事件列表
            print(content_list)

    def on_pressed(key):
        if key == keyboard.Key.esc:  # 判断是不是按了esc，如果按了就停止监听
            keyboard_listener.stop()  # 停止监听键盘
            mouse_listener.stop()  # 停止监听鼠标
            mouse_listener_rl.stop()
            save_file(keyboard_mouse_list, file_name="keyboard_mouse_list.pkl")  # 把事件列表存到文件里面
            # print(keyboard_mouse_list)
            return False
        else:
            global start_time  # 生声明事件的开始时间
            content_list = []  # 定义一个装事件的空列表
            end_time = time.time()  # 获取事件的结束时间
            delay_time = end_time - start_time  # 思考时间
            content_list.append('key')  # 添加时间类型到列表
            content_list.append(key)  # 添加功能键到列表
            content_list.append(delay_time)  # 添延迟示时间到列表
            keyboard_mouse_list.append(content_list)  # 添加整个事件到大列表
            start_time = end_time  # 重置开始时间
            # print(content_list)

    mouse_listener = mouse.Listener(on_click=on_click)  # 监听鼠标
    mouse_listener_rl = mouse.Listener(on_click=on_release)  # 监听鼠标
    keyboard_listener = keyboard.Listener(on_press=on_pressed)  # 监听键盘
    keyboard_listener.start()  # 启动监听程序
    mouse_listener_rl.start()
    mouse_listener.start()  # 启动监听程序
    mouse_listener.join()  # 线程阻塞持续监听
    mouse_listener_rl.join()
    keyboard_listener.join()  # 线程阻塞持续监听


# key_mouse_event()
# time.sleep(3)
switch_on = True


def listen_for_escape(key):
    global switch_on
    if key == keyboard.Key.esc:
        print("回放程序终止")
        switch_on = False
        app.toggle_recording()
        return


def callback_event(times):
    global switch_on
    keyboard_thread = keyboard.Listener(on_press=listen_for_escape)
    keyboard_thread.start()
    app.toggle_minimize()
    try:
        keyboard_mouse_list2 = load_file()  # 先读取文件内容
        for i in range(times):  # 循环的次数后面应用到界面程序
            times -= 1
            app.simulate_recording(times)
            time.sleep(1)
            if switch_on:
                for action_event in keyboard_mouse_list2:
                    if action_event[0] == 'click':  # 判断是不是鼠标的点击操作
                        mouse_click.position = (action_event[1], action_event[2])  # 提取鼠标移动的位置进行移动
                        mouse_click.press(action_event[3])  # 鼠标进行点击操作
                        app.update_logs(f"点击{action_event[3]}")
                        time.sleep(action_event[4])  # 思考时间的暂停操作
                    elif action_event[0] == 'release':
                        mouse_click.release(action_event[1])
                        app.update_logs(f"松开{action_event[1]}")
                        print(f"松开{action_event[1]}")
                        time.sleep(action_event[2])
                    elif action_event[0] == 'key':  # 判断是不是键盘的操作
                        keyboard_press.press(action_event[1])  # 进行键盘操作
                        app.update_logs(f"按下{action_event[1]}")
                        print(f"按下{action_event[1]}")
                        time.sleep(action_event[2])  # 思考时间暂停操作
                    else:
                        print("输入错误，程序终止")
                        return False
    except KeyboardInterrupt:
        app.toggle_recording()
        print("Loop terminated by KeyboardInterrupt")
    finally:
        app.toggle_recording()
        # 确保在程序退出时清理
        switch_on = True
    keyboard_thread.stop()


# callback_event()


import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class RecorderApp:
    def __init__(self, root):
        global times
        times = 0
        self.root = root
        self.root.geometry("600x660")
        self.root.title("录制与回放")
        self.root.attributes('-topmost', True)
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.X, padx=10, pady=10)
        # 输入框：提示输入次数
        self.entry_label = ttk.Label(frame, text="输入次数:")
        self.entry_label.grid(row=0, column=0, padx=25, pady=5, sticky=tk.W)  # sticky=tk.W表示靠左对齐
        self.entry = ttk.Entry(frame, width=10)  # 设置输入框宽度为10个字符
        self.entry.grid(row=0, column=1, padx=15, pady=5)

        # 显示框：显示剩余次数
        self.label_remaining = ttk.Label(frame, text="剩余次数: 0")
        self.label_remaining.grid(row=0, column=4, padx=5, pady=5)
        # 显示日志
        self.display_logs = tk.Text(root, width=50, height=38, padx=10, pady=10)
        self.display_logs.pack()
        self.minimize_var = tk.BooleanVar(value=False)
        self.minimize_checkbutton = tk.Checkbutton(root, text="最小化窗口", variable=self.minimize_var)
        self.minimize_checkbutton.pack(pady=20)
        # 开始录制按钮
        self.start_button = ttk.Button(frame, text="开始录制", command=key_mouse_event)
        self.start_button.grid(row=0, column=2, padx=5, pady=5)

        # 回放操作按钮（初始状态为禁用）
        self.replay_button = ttk.Button(frame, text="回放操作", command=self.replay_action)
        self.replay_button.grid(row=0, column=3, padx=5, pady=5)

        # 初始化录制次数
        self.recording_times = 0
        self.remaining_times = 0

    def toggle_minimize(self):
        if self.minimize_var.get():
            # 最小化窗口
            self.root.iconify()
            # 更新变量状态，表示窗口已最小化（在这个简单示例中，这一步是多余的，因为我们直接通过按钮状态判断）
            # self.minimize_var.set(True)  # 这行代码是多余的，因为点击按钮已经改变了变量的值

    def toggle_recording(self):
        # 还原窗口到原来的大小（在这个简单示例中，就是初始设置的大小）
        self.root.deiconify()
        self.root.update_idletasks()  # 确保窗口正确显示

    def simulate_recording(self, times):
        self.label_remaining.config(text="剩余次数: " + str(times))  # 更新剩余次数
        self.label_remaining.update()
        # print(times)

    def update_logs(self, logs):
        self.display_logs.insert(tk.END, f"{logs}\n")
        self.display_logs.update()
        # print(times)

    def replay_action(self):
        global times
        try:
            times = int(self.entry.get())
            if times <= 0:
                messagebox.showwarning("输入错误", "录制次数必须为正整数")
                return
        except ValueError:
            messagebox.showwarning("输入错误", "请输入有效的整数")
        # 模拟回放操作
        callback_event(times)


# 创建主窗口并运行应用程序
root = tk.Tk()
app = RecorderApp(root)
root.mainloop()
