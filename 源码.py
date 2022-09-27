import time
import pygame
import pyttsx3
import PySimpleGUI as sg
from sys import exit
from threading import Thread
from os import remove, listdir
from tempfile import gettempdir


def init():
    """初始化窗口"""
    # 设置主题
    sg.theme("DarkAmber")

    # 设置菜单栏
    menu = [
        ["界面语言(&L)", ["中文", "---", "English"]],
    ]

    # 获取电脑中已有的语言包
    voices_list = get_voices()

    # 判断电脑中是否存在语言包
    if not voices_list:
        sg.PopupError("文件错误", "电脑中没有语言包，请下载后重试！")
        exit(1)

    # 窗口布局设置
    layout = [
        [sg.Menu(menu)],
        [sg.Text("请输入需要转换为语音的文字", key="T1")],
        [sg.Multiline("欢迎使用文字转语音工具，在这里输入文字即可！", size=(100, 10), key="textContent")],
        [sg.B("获取文件内容", key="get"), sg.In(key="-file_dir-", size=(78, 1)), sg.FileBrowse("选择文件", key="browse", file_types=(("*.txt", "*.txt"),))],
        [sg.Text("\n")],
        [sg.Text("\n调整语速：", key="T2"), sg.Slider(range=(100, 400), default_value=200, size=(50, 15), orientation="horizontal", font=("Helvetica", 12), key="rateNumber")],
        [sg.Text("\n调整音量：", key="T4"), sg.Slider(range=(0, 100), default_value=100, size=(50, 15), orientation="horizontal", font=("Helvetica", 12), key="volumeNumber")],
        [sg.Text("\n")],
        [sg.Text("语音选项", key="T3"), sg.Text("\t语音包选择：", key="T5")],
        [sg.Button("试听", key="audition"), sg.Button("生成语音", key="make_file"), sg.Drop(voices_list, text_color=" ", background_color=" ", default_value=voices_list[0], font=("Helvetica", 13), readonly=True, key="voices")]
    ]

    return layout


def main():
    """主逻辑"""
    # 事件循环
    while True:
        # 读取事件
        event, values = window.read()

        # 处理对应事件
        if not event:  # 窗口关闭事件
            return
        if event == "get":  # 打开文档事件
            get_content(values["-file_dir-"])
        if event == "audition":  # 试听事件
            audition(values["rateNumber"], values["volumeNumber"], values["voices"], values["textContent"])
        if event == "make_file":  # 生成文件事件
            make_file(values["textContent"], values["rateNumber"], values["volumeNumber"], values["voices"])
        if event == "English":  # 改为英文界面
            change_en()
        if event == "中文":  # 改为中文界面
            change_cn()


def change_en():
    """改为英文界面"""
    window["browse"].update("browse")
    window["textContent"].update("Welcome to use the text to speech tool, just enter the text here!")
    window["T1"].update("Please enter the text to be converted into speech")
    window["T2"].update("\nSpeed up:       ")
    window["T3"].update("Voice options")
    window["audition"].update("Audition")
    window["make_file"].update("Generate file")
    window["T4"].update("\nAdjust volume:")
    window["get"].update("Get file content")
    window["get"].update("Get file content")
    window["T5"].update("\t  Voice package selection:")


def change_cn():
    """改为中文界面"""
    window["browse"].update("选择文件")
    window["textContent"].update("欢迎使用文字转语音工具，在这里输入文字即可！")
    window["T1"].update("请输入需要转换为语音的文字")
    window["T2"].update("\n调整语速：")
    window["T3"].update("语音选项")
    window["audition"].update("试听")
    window["make_file"].update("生成语音")
    window["T4"].update("\n调整音量：")
    window["get"].update("获取文件内容")
    window["T5"].update("\t语音包选择：")


def get_content(file_dir):
    """获取文件内容"""
    try:
        with open(file_dir) as f:
            window["textContent"].update(f.read())
    except FileNotFoundError:
        sg.PopupError("获取错误", "路径错误或为空，获取失败！")


def get_voices():
    """获取电脑中的语言包"""
    global voices_id
    voices_id = {}
    voices_list = []
    try:
        voices = engine.getProperty('voices')

        for voice in voices:
            voices_id[voice.name] = voice.id
            voices_list.append(voice.name)

        return voices_list
    except:
        sg.PopupError("内部错误", "系统注册表文件异常，请重启电脑后再试！")
        exit(1)


def audition(new_rate, new_volume, voice_name, content):
    """试听"""
    # 设置语音，语速，声音大小
    message = ["加载中...", "请勿乱点我哟，\n否则会崩溃哦。"]
    if len(content) > 300:
        message[1] += "\n内容过多，请耐心等待"
    sg.PopupNoButtons(message[0], message[1], non_blocking=True, auto_close=True)
    engine.setProperty("voice", voices_id[voice_name])
    engine.setProperty("rate", new_rate)
    engine.setProperty("volume", new_volume/100)

    # 保存文件
    file_name = make_file(text=content, is_temp=True)

    # 开始播放
    try:
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()
    except pygame.error:
        sg.PopupError("播放错误", "该语音包无法播放此内容，\n请更换语音包后重试！")
        pygame.mixer.music.stop()
        file_list.append(file_name)
        return

    # 阻塞程序
    sg.Popup("加载成功！", "试听中...", "结束试听请按确定或关闭弹窗！")
    pygame.mixer.music.stop()  # 停止播放
    file_list.append(file_name)


def make_file(text, rate=None, volume=None, name=None, is_temp=False):
    """生成音频文件"""
    # 获取本地时间作为文件名
    file = time.strftime("%Y%m%d%H%M%S", time.localtime())

    # 如果是临时缓存的文件，则创建wma文件
    if is_temp:
        file_name = "{0}\\T{1}.wma".format(gettempdir(), file)
        engine.save_to_file(text, file_name)
        engine.runAndWait()

        return file_name

    # 非临时文件
    sg.PopupNoButtons("转换中...", "请勿乱点我哟，\n否则会崩溃哦。", non_blocking=True, auto_close=True)
    engine.setProperty("voice", voices_id[name])
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume/100)
    engine.save_to_file(text, file+".mp3")
    engine.runAndWait()
    sg.Popup("转换成功！", "在当前文件夹下的{}.mp3\n如果无法播放语音，则需更换语音包重试".format(file))


def remove_temp():
    """删除临时文件"""
    for fl in file_list:
        try:
            remove(fl)
        except PermissionError:
            continue


def clean_last_file():
    """清理上一次缓存的文件"""
    for fn in listdir(gettempdir()):
        if len(fn.split(".")) == 2 and fn.split(".")[1] == "wma":
            remove(gettempdir() + "\\" + fn)


if __name__ == '__main__':
    Thread(target=clean_last_file).start()  # 开启清理缓存的子线程
    file_list = []  # 缓存列表
    pygame.init()  # 初始化
    pygame.mixer.init()
    engine = pyttsx3.init()  # 初始化模块
    window = sg.Window("文字转语音工具", init())  # 初始窗口并创建窗口
    main()  # 执行主循环
    window.close()  # 关闭窗口
    pygame.mixer.quit()
    pygame.quit()  # 释放资源
    remove_temp()  # 删除所有临时文件
    exit(0)  # 退出程序
