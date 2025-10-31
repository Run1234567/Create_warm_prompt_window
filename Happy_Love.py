"""
简化版爱心爆炸特效程序
功能：基本的爱心爆炸效果，包含粒子爆炸特效
作者：RUN
版本：简化版（文字留存时间加长，无残影，全屏显示）
"""

import tkinter as tk
import random
import math

# 全局变量
active_windows = []

class SimpleHeartExplosion:
    """简化版爱心爆炸效果类"""
    def __init__(self, parent):
        # 获取屏幕尺寸
        self.screen_width = parent.winfo_screenwidth()
        self.screen_height = parent.winfo_screenheight()
        
        # 中心位置
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        
        # 创建全屏爱心窗口
        self.window = tk.Toplevel(parent)
        self.window.title('爱心爆炸')
        self.window.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.0)
        self.window.attributes('-transparentcolor', 'black')
        
        # 创建全屏画布
        self.canvas = tk.Canvas(
            self.window, 
            width=self.screen_width, 
            height=self.screen_height,
            highlightthickness=0,
            bg='black'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 动画状态
        self.animation_running = True
        self.animation_step = 0
        self.max_steps = 60  # 爱心动画总帧数
        
        # 文字列表
        self.exploding_texts = []
        
        # 开始爱心动画
        self.animate_heart()
    
    def draw_heart(self, progress):
        """绘制爱心"""
        self.canvas.delete("all")
        
        # 计算爱心大小（根据屏幕尺寸自适应）
        base_size = min(self.screen_width, self.screen_height) // 10
        max_size = min(self.screen_width, self.screen_height) // 3
        size = base_size + progress * (max_size - base_size)
        
        # 绘制爱心
        points = []
        for t in range(0, 360, 5):
            t_rad = math.radians(t)
            # 爱心参数方程
            x = 16 * (math.sin(t_rad) ** 3)
            y = 13 * math.cos(t_rad) - 5 * math.cos(2*t_rad) - 2 * math.cos(3*t_rad) - math.cos(4*t_rad)
            # 缩放和居中
            x = x * size / 16 + self.center_x
            y = -y * size / 16 + self.center_y
            points.append((x, y))
        
        # 绘制爱心轮廓
        if len(points) > 1:
            self.canvas.create_polygon(
                points, 
                fill='#FF1493', 
                outline='#FF69B4',
                width=3
            )
        
        # 设置透明度
        alpha = min(1.0, progress * 1.5)
        self.window.attributes('-alpha', alpha)
    
    def create_explosion(self):
        """创建爆炸效果"""
        # 创建文字向各个方向迸发
        for _ in range(120):  # 增加粒子数量以适应全屏
            text = random.choice(tips)
            color = random.choice(text_colors)
            
            # 随机方向
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(8, 20)  # 增加速度以适应全屏
            
            exploding_text = {
                'text': text,
                'color': color,
                'x': self.center_x,
                'y': self.center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 180,  # 增加生命周期
                'max_life': 180,  # 最大生命周期
                'size': random.randint(14, 24),  # 增加文字大小
                'canvas_id': None  # 存储画布上的文字ID
            }
            
            self.exploding_texts.append(exploding_text)
    
    def draw_explosion(self):
        """绘制爆炸文字"""
        # 先清除所有之前的爆炸文字
        for text in self.exploding_texts:
            if text['canvas_id'] is not None:
                self.canvas.delete(text['canvas_id'])
        
        # 绘制新的爆炸文字
        for text in self.exploding_texts:
            # 计算透明度（根据生命周期）
            alpha = text['life'] / text['max_life']
            
            # 创建带透明度的颜色
            r, g, b = self.hex_to_rgb(text['color'])
            text_color = f'#{int(r*alpha):02x}{int(g*alpha):02x}{int(b*alpha):02x}'
            
            # 直接在全屏画布上绘制，不需要坐标转换
            canvas_x = text['x']
            canvas_y = text['y']
            
            # 只在画布范围内绘制
            if -100 <= canvas_x <= self.screen_width + 100 and -100 <= canvas_y <= self.screen_height + 100:
                text_id = self.canvas.create_text(
                    canvas_x, canvas_y,
                    text=text['text'],
                    fill=text_color,
                    font=("微软雅黑", text['size']),
                    anchor=tk.CENTER
                )
                text['canvas_id'] = text_id
    
    def hex_to_rgb(self, hex_color):
        """将十六进制颜色转换为RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def animate_heart(self):
        """爱心动画"""
        if not self.animation_running:
            return
            
        self.animation_step += 1
        progress = self.animation_step / self.max_steps
        
        # 绘制爱心
        self.draw_heart(progress)
        
        if progress < 1.0:
            # 继续动画
            self.window.after(30, self.animate_heart)
        else:
            # 开始爆炸
            self.start_explosion()
    
    def start_explosion(self):
        """开始爆炸"""
        self.create_explosion()
        self.animate_explosion()
    
    def animate_explosion(self):
        """爆炸动画"""
        if not self.animation_running:
            return
            
        # 清除画布
        self.canvas.delete("all")
        
        # 更新所有文字位置
        for text in self.exploding_texts[:]:
            text['x'] += text['vx']
            text['y'] += text['vy']
            text['life'] -= 1
            
            # 减速效果
            text['vx'] *= 0.98
            text['vy'] *= 0.98
            
            # 如果生命周期结束或超出屏幕，移除文字
            if (text['life'] <= 0 or 
                text['x'] < -500 or text['x'] > self.screen_width + 500 or
                text['y'] < -500 or text['y'] > self.screen_height + 500):
                self.exploding_texts.remove(text)
        
        # 绘制所有文字
        self.draw_explosion()
        
        # 如果还有文字，继续动画
        if self.exploding_texts:
            self.window.after(30, self.animate_explosion)
        else:
            # 爆炸结束，关闭窗口
            self.animation_running = False
            self.window.destroy()

def create_heart_explosion():
    """创建爱心爆炸效果"""
    try:
        heart = SimpleHeartExplosion(root)
        active_windows.append(heart.window)
        
        # 设置自动关闭
        def close_heart():
            heart.animation_running = False
            if heart.window.winfo_exists():
                heart.window.destroy()
            if heart.window in active_windows:
                active_windows.remove(heart.window)
        
        heart.window.after(15000, close_heart)  # 增加显示时间
        
    except Exception as e:
        print(f"创建爱心爆炸时出错: {e}")

def start_explosion_sequence():
    """开始爆炸序列"""
    print("开始爱心爆炸效果...")
    create_heart_explosion()
    
    # 程序结束检查
    root.after(18000, check_if_all_closed)

def check_if_all_closed():
    """检查所有窗口是否已关闭"""
    if len(active_windows) == 0:
        print("特效已结束")
        root.quit()
    else:
        root.after(1000, check_if_all_closed)

def close_all_windows():
    """立即关闭所有活动窗口"""
    global active_windows
    for window in active_windows[:]:
        try:
            window.destroy()
        except:
            pass
    active_windows.clear()
    print("正在关闭所有窗口...")

def on_space(event):
    """全局空格键处理"""
    close_all_windows()
    print("已停止特效")

def on_escape(event):
    """全局ESC键处理"""
    close_all_windows()
    root.quit()

# 温馨话语库
tips = [
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
]

# 文字颜色库
text_colors = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF', '#FF00FF',
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD',
    '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA'
]

def main():
    """程序主入口"""
    global root
    
    root = tk.Tk()
    root.withdraw()
    
    print("全屏爱心爆炸特效程序已启动!")
    print("退出方式: 按ESC键或空格键")
    
    root.bind('<space>', on_space)
    root.bind('<Escape>', on_escape)
    
    root.after(1000, start_explosion_sequence)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        close_all_windows()
        print("程序已结束")

if __name__ == '__main__':
    main()