"""
文字雨温馨提醒程序 - 短语版
功能：创建文字雨效果，温馨短语从屏幕顶部下落到底部消失
作者：RUN
版本：9.1 短语文字雨版
"""

import tkinter as tk
import random
import time
import math
import colorsys
from PIL import Image, ImageDraw, ImageTk
import pygame
import os

# 全局变量
exit_flag = False
active_windows = []
total_windows_created = 0
max_windows = 200  # 减少数量以保证性能

# 运行参数
CREATE_DELAY = 80  # 创建间隔
AUTO_CLOSE_TIME = 8000  # 窗口自动关闭时间(毫秒)
START_DELAY = 3000  # 程序启动延迟(毫秒)

# 初始化pygame mixer
pygame.mixer.init() 

# 文字雨参数
FALL_SPEED_MIN = 1  # 最小下落速度
FALL_SPEED_MAX = 8  # 最大下落速度
ROTATION_SPEED_MIN = 0.1  # 最小旋转速度
ROTATION_SPEED_MAX = 5  # 最大旋转速度
TRAIL_LENGTH = 8  # 拖尾效果长度

class FallingTextWindow:
    """下落文字窗口类"""
    def __init__(self, parent, text, color):
        # 获取屏幕尺寸
        self.screen_width = parent.winfo_screenwidth()
        self.screen_height = parent.winfo_screenheight()
        
        # 文字属性
        self.text = text
        self.color = color
        
        # 根据文字长度调整字体大小
        text_length = len(text)
        if text_length <= 4:
            self.font_size = random.randint(20, 28)
        elif text_length <= 6:
            self.font_size = random.randint(18, 24)
        else:
            self.font_size = random.randint(16, 20)
            
        # 计算窗口大小
        self.window_width = max(150, text_length * self.font_size * 0.8)
        self.window_height = self.font_size * 3
        
        # 随机起始位置（顶部）
        self.start_x = random.randint(int(self.window_width/2), int(self.screen_width - self.window_width/2))
        self.x = self.start_x
        self.y = -self.window_height  # 从屏幕上方开始
        
        # 运动属性
        self.fall_speed = random.uniform(FALL_SPEED_MIN, FALL_SPEED_MAX)
        self.rotation_speed = random.uniform(ROTATION_SPEED_MIN, ROTATION_SPEED_MAX)
        self.rotation_angle = 0
        self.sway_amplitude = random.uniform(0, 2)  # 左右摇摆幅度
        self.sway_frequency = random.uniform(0.005, 0.02)  # 左右摇摆频率
        self.sway_offset = random.uniform(0, 2 * math.pi)  # 摇摆相位偏移
        
        # 拖尾效果
        self.trail_positions = []
        self.trail_alphas = []
        
        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title('温馨短语雨')
        self.window.geometry(f"{int(self.window_width)}x{int(self.window_height)}+{int(self.x - self.window_width/2)}+{int(self.y)}")
        self.window.overrideredirect(True)  # 无边框
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.0)  # 初始透明
        self.window.attributes('-transparentcolor', 'black')  # 设置黑色为透明色
        
        # 创建画布
        self.canvas = tk.Canvas(
            self.window, 
            width=self.window_width, 
            height=self.window_height,
            highlightthickness=0,
            bg='black'  # 黑色背景将被设为透明
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 动画状态
        self.animation_running = True
        
        # 绑定事件
        self.window.bind('<Button-1>', self.on_click)
        
        # 开始下落动画
        self.fall()
    
    def fall(self):
        """下落动画"""
        if not self.animation_running:
            return
            
        # 更新位置
        self.y += self.fall_speed
        
        # 左右摇摆效果
        self.x = self.start_x + math.sin(self.y * self.sway_frequency + self.sway_offset) * self.sway_amplitude
        
        # 更新旋转角度
        self.rotation_angle += self.rotation_speed
        
        # 更新拖尾效果
        self.trail_positions.append((self.x, self.y))
        self.trail_alphas.append(1.0)
        
        # 限制拖尾长度
        if len(self.trail_positions) > TRAIL_LENGTH:
            self.trail_positions.pop(0)
            self.trail_alphas.pop(0)
        
        # 更新拖尾透明度
        for i in range(len(self.trail_alphas)):
            self.trail_alphas[i] = max(0, self.trail_alphas[i] - 0.12)
        
        # 清除画布
        self.canvas.delete("all")
        
        # 绘制拖尾效果
        for i, (trail_x, trail_y) in enumerate(self.trail_positions):
            alpha = self.trail_alphas[i]
            if alpha > 0:
                # 创建带透明度的颜色
                r, g, b = self.canvas.winfo_rgb(self.color)
                trail_color = f'#{int(r*alpha//65535):02x}{int(g*alpha//65535):02x}{int(b*alpha//65535):02x}'
                
                # 计算拖尾字体大小
                trail_font_size = max(1, int(self.font_size * alpha * 0.8))
                
                # 绘制拖尾文字
                self.canvas.create_text(
                    self.window_width/2, self.window_height/2,
                    text=self.text,
                    fill=trail_color,
                    font=("微软雅黑", trail_font_size),
                    anchor=tk.CENTER
                )
        
        # 绘制主文字
        self.canvas.create_text(
            self.window_width/2, self.window_height/2,
            text=self.text,
            fill=self.color,
            font=("微软雅黑", self.font_size),
            anchor=tk.CENTER
        )
        
        # 更新窗口位置
        self.window.geometry(f"+{int(self.x - self.window_width/2)}+{int(self.y)}")
        
        # 设置透明度 - 根据位置调整
        if self.y < 100:  # 顶部淡入
            alpha = self.y / 100
        elif self.y > self.screen_height - 100:  # 底部淡出
            alpha = (self.screen_height - self.y) / 100
        else:  # 中间完全显示
            alpha = 1.0
            
        self.window.attributes('-alpha', alpha)
        
        # 检查是否到达底部
        if self.y > self.screen_height + 50:
            self.close_with_effect()
        else:
            # 继续动画
            self.window.after(30, self.fall)
    
    def on_click(self, event):
        """点击事件"""
        self.close_with_effect()
    
    def close_with_effect(self):
        """带效果的关闭"""
        self.animation_running = False
        self.window.destroy()

def create_falling_text():
    """创建下落文字"""
    global exit_flag, active_windows, total_windows_created
    
    # 检查退出条件
    if exit_flag or total_windows_created >= max_windows:
        if len(active_windows) == 0:
            root.quit()
        return
    
    try:
        # 随机选择文字
        text = random.choice(tips)
        
        # 随机选择颜色
        color = random.choice(text_colors)
        
        # 创建下落文字窗口
        falling_text = FallingTextWindow(root, text, color)
        active_windows.append(falling_text.window)
        
        total_windows_created += 1
        
        # 设置自动关闭定时器
        def close_window(win=falling_text):
            win.close_with_effect()
            if win.window in active_windows:
                active_windows.remove(win.window)
        
        falling_text.window.after(AUTO_CLOSE_TIME, close_window)
        

        
    except Exception as e:
        print(f"创建下落文字时出错: {e}")
    
    # 显示进度信息
    if total_windows_created % 20 == 0:
        print(f"已创建 {total_windows_created}/{max_windows} 个温馨短语")
    
    # 继续创建新的下落文字
    if not exit_flag and total_windows_created < max_windows:
        root.after(CREATE_DELAY, create_falling_text)
    elif total_windows_created >= max_windows:
        print(f"已达到最大短语数量 {max_windows}")
        root.after(10000, check_if_all_closed)

def check_if_all_closed():
    """检查所有窗口是否已关闭，用于程序结束判断"""
    if len(active_windows) == 0:
        print("所有温馨短语已消失，程序结束")
        root.quit()
    else:
        remaining = len(active_windows)
        print(f"还有 {remaining} 个短语未消失，等待中...")
        root.after(5000, check_if_all_closed)

def close_all_windows():
    """立即关闭所有活动窗口"""
    global active_windows
    windows_to_close = active_windows.copy()
    for window in windows_to_close:
        try:
            window.destroy()
        except:
            pass
    active_windows.clear()
    print("正在关闭所有窗口...")

def start_creating_text():
    """启动文字创建流程"""
    print("开始创建温馨短语雨...")
    

    
    # 开始创建下落文字
    root.after(100, create_falling_text)



def play_sound_effect():
    """播放音效"""
    try:
        # 创建简单的音效（如果没有音效文件）
        pygame.mixer.Sound.play(pygame.mixer.Sound(buffer=bytearray([0])))
    except:
        pass

def on_space(event):
    """全局空格键处理：停止创建并关闭所有窗口"""
    global exit_flag
    exit_flag = True
    close_all_windows()
    print("已停止创建新短语，正在关闭所有窗口...")
    # 停止音乐
    try:
        pygame.mixer.music.stop()
    except:
        pass

def on_escape(event):
    """全局ESC键处理：强制退出程序"""
    global exit_flag
    exit_flag = True
    close_all_windows()
    print("已停止创建新短语，正在关闭所有窗口...")
    # 停止音乐
    try:
        pygame.mixer.music.stop()
    except:
        pass
    root.quit()

# 温馨话语库 - 精心挑选的短语
tips = [
    "你是最棒的", "一切都会好的", "今天也要开心", "相信自己", "坚持下去",
    "你很特别", "鸡", "kun", "保持希望", "永不放弃",
    "梦想成真", "未来可期", "勇敢前行", "心存感恩", "珍惜当下",
    "简单快乐", "知足常乐", "温暖如初", "岁月静好", "平安喜乐",
    "万事胜意", "天天开心", "好运连连", "幸福满满", "心想事成",
    "健康平安", "鸡你太美", "笑口常开", "友谊长存", "爱情甜蜜",
    "家庭和睦", "工作顺利", "RUN好帅", "美丽心情", "放松一下",
    "慢慢来", "别着急", "你可以的", "爱自己", "感恩有你",
    "享受生活", "拥抱阳光", "晚安好梦", "早安加油", "午安休息",
    "多喝热水", "记得吃饭", "天冷加衣", "照顾好自己", "别太累了",
    "休息一下", "放松心情", "保持微笑", "世界爱你", "宇宙祝福",
    "天使守护", "好运相伴", "幸福相随", "快乐永驻", "财源滚滚",
    "事业有成", "蔡徐坤", "爱情美满", "友谊万岁", "亲情永恒",
    "幸福安康", "吉祥如意", "润哥哥最帅", "寿比南山", "福如东海",
    "龙凤呈祥", "金玉满堂", "喜气洋洋", "欢天喜地", "油饼",
    "冬日暖阳", "厉不厉害你坤哥", "夏雨雨人", "秋风送爽", "冬温夏清"
]

# 文字颜色库 - 鲜艳的颜色
text_colors = [
    '#FFFFFF', '#FFFF00', '#00FFFF', '#FF00FF', '#00FF00',
    '#FF9900', '#FF66CC', '#66FF66', '#66CCFF', '#CC66FF',
    '#FF6666', '#66FFCC', '#FFCC66', '#CCFF66', '#66FF99',
    '#FF99CC', '#99CCFF', '#CC99FF', '#FFCC99', '#99FFCC',
    '#FF6699', '#66FF99', '#9966FF', '#99FF66', '#FF9966',
    '#66FFFF', '#FF66FF', '#FFFF66', '#FF6666', '#6666FF',
    '#66FF66', '#FFCC66', '#CC66FF', '#66CCFF', '#FF66CC',
    '#CCFF66', '#FFCCCC', '#CCFFCC', '#CCCCFF', '#FFFFCC',
    '#FFCC99', '#99CCFF', '#FF99CC', '#CCFF99', '#FFCCFF',
    '#99FFCC', '#CC99FF', '#FFCC66', '#66CCFF', '#FF6699',
    '#FF33CC', '#33FFCC', '#CC33FF', '#33CCFF', '#FFCC33',
    '#CCFF33', '#FF3333', '#33FF33', '#3333FF', '#FFFF33',
    '#FF3333', '#33FFFF', '#FF33FF', '#33FF33', '#FFFF33',
    '#FF6633', '#33FF66', '#6633FF', '#33FF99', '#FF3366',
    '#66FF33', '#FF3399', '#99FF33', '#33FF99', '#FF9933'
]

def main():
    """程序主入口"""
    global exit_flag, root
    
    # 初始化主窗口（隐藏）
    root = tk.Tk()
    root.withdraw()
    
    # 显示使用说明
    print("温馨短语雨程序已启动!")
    print(f"将创建最多 {max_windows} 个温馨短语")
    print("短语将从屏幕顶部下落到底部消失")
    print("每个短语会在8秒后自动消失")
    print("点击短语可立即关闭")
    print("退出方式:")
    print("1. 按空格键 - 关闭所有窗口并退出")
    print("2. 按ESC键 - 关闭所有窗口并退出")
    print("3. 等待所有短语自动消失")
    print(f"程序将在{START_DELAY//1000}秒后开始显示短语雨...")
    
    # 注册全局键盘事件
    root.bind('<space>', on_space)
    root.bind('<Escape>', on_escape)
    
    # 延迟启动文字创建
    root.after(START_DELAY, start_creating_text)
    
    # 启动主事件循环
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        exit_flag = True
        close_all_windows()
        try:
            pygame.mixer.music.stop()
        except:
            pass
        print("程序已结束")

if __name__ == '__main__':
    main()