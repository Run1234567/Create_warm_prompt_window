"""
纯文字版极致温馨提醒程序
功能：在屏幕上以惊艳的动画效果弹出纯文字温馨提醒，无任何边框
作者：RUN
版本：8.0 纯文字震撼版
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
window_queue = []
total_windows_created = 0
max_windows = 200  # 减少数量但提高质量

# 运行参数
CREATE_DELAY = 150
BATCH_SIZE = 25
WINDOWS_PER_BATCH = 1
AUTO_CLOSE_TIME = 30000
START_DELAY = 5000

# 初始化pygame mixer
pygame.mixer.init()

# 震撼参数
PARTICLE_COUNT = 20  # 每个窗口的粒子数量
ANIMATION_DURATION = 250  # 动画持续时间(毫秒) 

class TextParticle:
    """文字粒子效果类"""
    def __init__(self, canvas, x, y, text, color, size):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.speed = random.uniform(1, 5)
        self.angle = random.uniform(0, 2 * math.pi)
        self.life = random.uniform(30, 60)
        self.id = None
        self.alpha = 1.0
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            if self.id:
                self.canvas.delete(self.id)
            return False
            
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # 逐渐消失
        self.alpha = max(0, self.life / 30)
        
        # 绘制文字粒子
        if self.id:
            self.canvas.delete(self.id)
            
        # 创建带透明度的颜色
        r, g, b = self.canvas.winfo_rgb(self.color)
        alpha_color = f'#{int(r*self.alpha//65535):02x}{int(g*self.alpha//65535):02x}{int(b*self.alpha//65535):02x}'
            
        self.id = self.canvas.create_text(
            self.x, self.y,
            text=self.text,
            fill=alpha_color,
            font=("微软雅黑", int(self.size)),
            anchor=tk.CENTER
        )
        
        return True

class PureTextWindow:
    """纯文字窗口类，无边框，只有文字和粒子效果"""
    def __init__(self, parent, tip, text_color, font, width, height, x, y):
        self.window = tk.Toplevel(parent)
        self.window.title('纯文字温馨提醒')
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.overrideredirect(True)  # 无边框
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.0)  # 初始透明
        self.window.attributes('-transparentcolor', 'black')  # 设置黑色为透明色
        
        self.tip = tip
        self.text_color = text_color
        self.font = font
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        
        # 创建黑色背景的画布（黑色会被设为透明）
        self.canvas = tk.Canvas(
            self.window, 
            width=width, 
            height=height,
            highlightthickness=0,
            bg='black'  # 黑色背景将被设为透明
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 粒子系统
        self.particles = []
        self.text_particles = []
        
        # 动画状态
        self.animation_step = 0
        self.animation_running = True
        self.animation_type = random.choice(["typing", "rainbow", "explode", "swirl", "glitch"])
        
        # 绑定事件
        self.window.bind('<Button-1>', self.on_click)
        self.window.bind('<Enter>', self.on_hover)
        self.window.bind('<Leave>', self.on_leave)
        
        # 开始动画
        self.animate_entrance()
        
    def animate_entrance(self):
        """入口动画"""
        if not self.animation_running:
            return
            
        self.animation_step += 1
        progress = min(1.0, self.animation_step / (ANIMATION_DURATION // 16))
        
        if self.animation_type == "typing":
            self.typing_animation(progress)
        elif self.animation_type == "rainbow":
            self.rainbow_animation(progress)
        elif self.animation_type == "explode":
            self.explode_animation(progress)
        elif self.animation_type == "swirl":
            self.swirl_animation(progress)
        elif self.animation_type == "glitch":
            self.glitch_animation(progress)
        
        if progress < 1.0:
            self.window.after(16, self.animate_entrance)
        else:
            self.start_text_particle_effect()
    
    def typing_animation(self, progress):
        """打字机效果动画"""
        # 清除画布
        self.canvas.delete("all")
        
        # 计算已显示的文字数量
        chars_to_show = int(progress * len(self.tip))
        displayed_text = self.tip[:chars_to_show]
        
        # 绘制文字
        self.canvas.create_text(
            self.width // 2, self.height // 2,
            text=displayed_text, fill=self.text_color,
            font=self.font, width=self.width - 40,
            justify=tk.CENTER
        )
        
        # 设置透明度
        alpha = min(1.0, progress * 1.5)
        self.window.attributes('-alpha', alpha)
    
    def rainbow_animation(self, progress):
        """彩虹文字效果动画"""
        # 清除画布
        self.canvas.delete("all")
        
        # 计算彩虹颜色
        hue = (progress * 3) % 1.0  # 循环色相
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
        rainbow_color = f'#{r:02x}{g:02x}{b:02x}'
        
        # 绘制文字
        self.canvas.create_text(
            self.width // 2, self.height // 2,
            text=self.tip, fill=rainbow_color,
            font=self.font, width=self.width - 40,
            justify=tk.CENTER
        )
        
        # 设置透明度
        alpha = min(1.0, progress * 1.2)
        self.window.attributes('-alpha', alpha)
    
    def explode_animation(self, progress):
        """文字爆炸效果动画"""
        # 清除画布
        self.canvas.delete("all")
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        # 爆炸效果 - 文字从中心向外扩散
        if progress < 0.5:
            # 第一阶段：文字从中心放大
            scale = progress * 2
            font_size = int(self.font[1] * (0.5 + scale * 1.5))
            current_font = (self.font[0], font_size, self.font[2] if len(self.font) > 2 else "")
            
            self.canvas.create_text(
                center_x, center_y,
                text=self.tip, fill=self.text_color,
                font=current_font, width=self.width - 40,
                justify=tk.CENTER
            )
        else:
            # 第二阶段：文字稳定显示
            self.canvas.create_text(
                center_x, center_y,
                text=self.tip, fill=self.text_color,
                font=self.font, width=self.width - 40,
                justify=tk.CENTER
            )
        
        # 设置透明度
        alpha = min(1.0, progress * 1.3)
        self.window.attributes('-alpha', alpha)
    
    def swirl_animation(self, progress):
        """漩涡文字效果动画"""
        # 清除画布
        self.canvas.delete("all")
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        # 漩涡效果 - 文字字符旋转
        chars = list(self.tip)
        radius = min(self.width, self.height) * 0.3
        angle_offset = progress * 10  # 旋转角度
        
        for i, char in enumerate(chars):
            angle = (i / len(chars)) * 2 * math.pi + angle_offset
            distance = radius * progress
            
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            
            # 字符大小随进度变化
            font_size = int(self.font[1] * (0.5 + progress * 0.5))
            char_font = (self.font[0], font_size, self.font[2] if len(self.font) > 2 else "")
            
            self.canvas.create_text(
                x, y, text=char, fill=self.text_color,
                font=char_font, anchor=tk.CENTER
            )
        
        # 当进度完成时，显示完整文字
        if progress >= 1.0:
            self.canvas.delete("all")
            self.canvas.create_text(
                center_x, center_y,
                text=self.tip, fill=self.text_color,
                font=self.font, width=self.width - 40,
                justify=tk.CENTER
            )
        
        # 设置透明度
        alpha = min(1.0, progress * 1.4)
        self.window.attributes('-alpha', alpha)
    
    def glitch_animation(self, progress):
        """故障效果动画"""
        # 清除画布
        self.canvas.delete("all")
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        # 故障效果 - 文字抖动和颜色偏移
        offset_x = random.randint(-5, 5) if progress < 0.9 else 0
        offset_y = random.randint(-3, 3) if progress < 0.9 else 0
        
        # 主文字
        self.canvas.create_text(
            center_x, center_y,
            text=self.tip, fill=self.text_color,
            font=self.font, width=self.width - 40,
            justify=tk.CENTER
        )
        
        # 故障效果 - 红色和蓝色偏移
        if progress < 0.9:
            # 红色偏移
            self.canvas.create_text(
                center_x + offset_x + 2, center_y + offset_y,
                text=self.tip, fill='red',
                font=self.font, width=self.width - 40,
                justify=tk.CENTER
            )
            
            # 蓝色偏移
            self.canvas.create_text(
                center_x - offset_x - 2, center_y - offset_y,
                text=self.tip, fill='blue',
                font=self.font, width=self.width - 40,
                justify=tk.CENTER
            )
        
        # 设置透明度
        alpha = min(1.0, progress * 1.2)
        self.window.attributes('-alpha', alpha)
    
    def start_text_particle_effect(self):
        """启动文字粒子效果"""
        # 创建文字粒子
        chars = list(self.tip)
        center_x = self.width // 2
        center_y = self.height // 2
        
        for char in chars:
            # 随机位置
            x = random.randint(center_x - 100, center_x + 100)
            y = random.randint(center_y - 50, center_y + 50)
            
            # 随机大小
            size = random.randint(10, 24)
            
            # 创建文字粒子
            particle = TextParticle(
                self.canvas, x, y, char,
                self.text_color, size
            )
            self.text_particles.append(particle)
        
        # 开始粒子动画
        self.animate_text_particles()
    
    def animate_text_particles(self):
        """文字粒子动画"""
        if not self.animation_running:
            return
            
        # 更新所有粒子
        self.text_particles = [p for p in self.text_particles if p.update()]
        
        # 如果还有存活的粒子，继续动画
        if self.text_particles:
            self.window.after(50, self.animate_text_particles)
        else:
            # 粒子全部消失后，重新创建
            self.window.after(1000, self.start_text_particle_effect)
    
    def on_click(self, event):
        """点击事件"""
        self.close_with_effect()
    
    def on_hover(self, event):
        """鼠标悬停事件"""
        # 放大效果
        self.window.attributes('-alpha', 0.9)
    
    def on_leave(self, event):
        """鼠标离开事件"""
        # 恢复透明度
        self.window.attributes('-alpha', 1.0)
    
    def close_with_effect(self):
        """带效果的关闭"""
        self.animation_running = False
        
        # 清除所有粒子
        for particle in self.text_particles:
            if particle.id:
                self.canvas.delete(particle.id)
        self.text_particles.clear()
        
        # 淡出动画
        self.fade_out()
    
    def fade_out(self):
        """淡出动画"""
        alpha = self.window.attributes('-alpha')
        alpha -= 0.05
        
        if alpha > 0:
            self.window.attributes('-alpha', alpha)
            self.window.after(30, self.fade_out)
        else:
            self.window.destroy()

def create_window_from_queue():
    """从队列中取出窗口信息并创建实际的GUI窗口"""
    global exit_flag, active_windows, window_queue, total_windows_created
    
    # 检查退出条件
    if exit_flag:
        window_queue.clear()
        if len(active_windows) == 0:
            root.quit()
        return
    
    # 从队列中取出窗口并创建
    windows_to_create = min(WINDOWS_PER_BATCH, len(window_queue))
    for _ in range(windows_to_create):
        if not window_queue or total_windows_created >= max_windows:
            break
            
        window_info = window_queue.pop(0)
        try:
            # 创建纯文字窗口
            text_window = PureTextWindow(
                root,
                window_info['tip'],
                window_info['text_color'],
                window_info['font'],
                window_info['width'],
                window_info['height'],
                window_info['x'],
                window_info['y']
            )
            
            active_windows.append(text_window.window)
            
            # 设置自动关闭定时器
            def close_window(win=text_window):
                win.close_with_effect()
                if win.window in active_windows:
                    active_windows.remove(win.window)
            
            text_window.window.after(AUTO_CLOSE_TIME, close_window)
            
            total_windows_created += 1
            print(f"已创建第 {total_windows_created} 个纯文字窗口: {window_info['tip']}")
            
            # 播放音效
            play_sound_effect()
            
        except Exception as e:
            print(f"创建窗口时出错: {e}")
    
    # 显示进度信息
    if total_windows_created < max_windows:
        print(f"已创建 {total_windows_created}/{max_windows} 个窗口")
    else:
        print(f"已达到最大窗口数量 {max_windows}")
        root.after(20000, check_if_all_closed)
    
    # 继续处理队列中的剩余窗口
    if window_queue and not exit_flag and total_windows_created < max_windows:
        root.after(CREATE_DELAY, create_window_from_queue)

def check_if_all_closed():
    """检查所有窗口是否已关闭，用于程序结束判断"""
    if len(active_windows) == 0:
        print("所有窗口已自动关闭，程序结束")
        root.quit()
    else:
        remaining = len(active_windows)
        print(f"还有 {remaining} 个窗口未关闭，等待中...")
        root.after(5000, check_if_all_closed)

def add_windows_to_queue(count):
    """生成指定数量的窗口配置信息并添加到队列"""
    global window_queue
    
    # 获取屏幕尺寸用于随机定位
    temp_root = tk.Tk()
    temp_root.withdraw()
    screen_width = temp_root.winfo_screenwidth()
    screen_height = temp_root.winfo_screenheight()
    temp_root.destroy()
    
    # 温馨话语库 - 精心挑选的短句
    tips = [
        "你是光✨", "世界因你而美好🌍", "今天也要爱自己💖",
        "梦想正在实现🌟", "你是无限可能🎯", "勇敢做自己🦸",
        "今天也要闪闪发光💎", "你是宇宙的奇迹🌌", "内心充满力量⚡",
        "每一天都是礼物🎁", "你是爱与光💫", "未来可期🚀",
        "做自己的英雄🏆", "生命因你而精彩🎉", "今天也要微笑😊",
        "你是最特别的存在🔮", "梦想的翅膀已展开🦋", "内心光芒万丈💡",
        "每一天都是新生🌱", "你是希望的象征🌈", "勇敢前行🛣️",
        "今天也要全力以赴💪", "你是生命的艺术家🎨", "内心平静强大🌀",
        "每一天都值得感恩🙏", "你是爱与光的化身🌟", "梦想永不熄灭🔥",
        "今天也要充满希望🌞", "你是独一无二的✨", "内心花园繁盛🌷",
        "每一天都是庆典🎊", "你是星辰大海🌠", "勇敢追梦🌠",
        "今天也要自信满满💯", "你是生命的诗人📝", "内心火焰燃烧🔥",
        "每一天都是传奇📖", "你是宇宙的礼物🎀", "梦想成真🏅",
        "今天也要快乐前行🎈", "你是生命的歌手🎤", "内心力量无穷🌊",
        "每一天都是乐章🎵", "你是希望的灯塔🗼", "勇敢飞翔🦅",
        "今天也要充满爱❤️", "你是生命的舞者💃", "内心花园美丽🌹",
        "每一天都是艺术🎭", "你是梦想的航海家⛵", "勇敢探索🗺️",
        "今天也要感恩生命🌻", "你是光的使者🌟", "内心平静祥和☮️",
        "每一天都是祝福🙌", "你是生命的建筑师🏗️", "勇敢创造🔨",
        "今天也要珍惜当下⏳", "你是爱的化身💝", "内心充满喜悦😄",
        "每一天都是奇迹🔮", "你是梦想的园丁🌻", "勇敢生长🌱",
        "今天也要拥抱生活🤗", "你是希望的种子🌱", "内心充满阳光☀️",
        "每一天都是礼物🎀", "你是生命的战士⚔️", "勇敢战斗🛡️",
        "今天也要保持善良🤝", "你是光的传播者💡", "内心充满和平🕊️",
        "每一天都是旅程🧳", "你是梦想的飞行员✈️", "勇敢飞翔🪂",
        "今天也要相信自己🌟", "你是生命的探险家🧭", "勇敢冒险🗿",
        "每一天都是发现🔍", "你是爱的接收器💞", "内心充满感恩💖",
        "今天也要传播快乐🎭", "你是光的反射器🔦", "内心充满光明💫",
        "每一天都是学习📚", "你是梦想的实现者🎖️", "勇敢成就🏅",
        "今天也要分享爱💗", "你是生命的守护者🛡️", "勇敢保护💪",
        "每一天都是成长📈", "你是希望的传播者📢", "内心充满信心💫",
        "今天也要创造美好🎨", "你是光的源泉💡", "内心充满能量⚡",
        "每一天都是祝福🌈", "你是梦想的守护者🔒", "勇敢坚持🛡️",
        "今天也要活在当下🎯", "你是爱的体现💖", "内心充满慈悲🙏",
        "每一天都是恩赐🎁", "你是光的化身🌟", "内心充满智慧📚",
        "今天也要享受生活🎊", "你是梦想的见证者👁️", "勇敢见证🔭",
        "每一天都是宝贵💎", "你是爱的证明💞", "内心充满勇气🦁",
        "今天也要庆祝生命🎉", "你是光的证明💫", "内心充满喜悦😊"
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
        '#99FFCC', '#CC99FF', '#FFCC66', '#66CCFF', '#FF6699'
    ]
    
    # 字体库
    fonts = [
        ('微软雅黑', 20, 'bold'),
        ('楷体', 22),
        ('黑体', 20, 'bold'),
        ('宋体', 21),
        ('Arial', 20, 'bold'),
        ('Comic Sans MS', 20),
        ('Times New Roman', 21)
    ]
    
    # 生成窗口配置信息
    for _ in range(count):
        tip = random.choice(tips)
        text_color = random.choice(text_colors)
        font = random.choice(fonts)
        
        # 计算随机窗口位置和大小
        window_width = random.randint(350, 450)
        window_height = random.randint(150, 200)
        x = random.randrange(0, max(1, screen_width - window_width))
        y = random.randrange(0, max(1, screen_height - window_height))
        
        window_queue.append({
            'tip': tip,
            'text_color': text_color,
            'font': font,
            'width': window_width,
            'height': window_height,
            'x': x,
            'y': y
        })

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

def start_creating_windows():
    """启动窗口创建流程"""
    print("开始创建纯文字窗口...")
    
    # 播放背景音乐
    play_background_music()
    
    # 分批将窗口添加到队列
    batch_count = max_windows // BATCH_SIZE
    
    for i in range(batch_count):
        if exit_flag:
            break
        
        add_windows_to_queue(BATCH_SIZE)
        progress = min((i + 1) * BATCH_SIZE, max_windows)
        print(f"已添加 {progress}/{max_windows} 个窗口到队列")
    
    print("所有窗口已添加到队列，等待创建...")
    root.after(1000, create_window_from_queue)

def play_background_music():
    """播放背景音乐"""
    try:
        # 尝试播放背景音乐
        pygame.mixer.music.load("bg_music.mp3")  # 需要有一个bg_music.mp3文件
        pygame.mixer.music.set_volume(0.3)  # 设置音量
        pygame.mixer.music.play(-1)  # 循环播放
        print("背景音乐开始播放")
    except Exception as e:
        print(f"无法播放背景音乐: {e}")

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
    print("已停止创建新窗口，正在关闭所有窗口...")
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
    print("已停止创建新窗口，正在关闭所有窗口...")
    # 停止音乐
    try:
        pygame.mixer.music.stop()
    except:
        pass
    root.quit()

def main():
    """程序主入口"""
    global exit_flag, root
    
    # 初始化主窗口（隐藏）
    root = tk.Tk()
    root.withdraw()
    
    # 显示使用说明
    print("纯文字版极致温馨提醒程序已启动!")
    print(f"将创建最多 {max_windows} 个纯文字窗口")
    print("窗口将以惊艳的动画效果显示，无任何边框")
    print("每个窗口会在30秒后自动关闭")
    print("点击窗口可立即关闭")
    print("鼠标悬停会有交互效果")
    print("退出方式:")
    print("1. 按空格键 - 关闭所有窗口并退出")
    print("2. 按ESC键 - 关闭所有窗口并退出")
    print("3. 等待所有窗口自动关闭")
    print(f"程序将在{START_DELAY//1000}秒后开始显示弹窗...")
    
    # 注册全局键盘事件
    root.bind('<space>', on_space)
    root.bind('<Escape>', on_escape)
    
    # 延迟启动窗口创建
    root.after(START_DELAY, start_creating_windows)
    
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