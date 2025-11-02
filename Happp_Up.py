"""
短语上升爆炸特效程序
功能：大量短语从底部随机位置分批上升，到达指定高度后爆炸成多个随机短语
作者：RUN
版本：多批次大量短语版（修复不爆炸问题）
"""

import tkinter as tk
import random
import math
import time

# 全局变量
active_windows = []
phrase_instances = []

class RisingPhraseExplosion:
    """上升短语爆炸效果类"""
    def __init__(self, parent, phrase_index=None, batch_id=0):
        # 获取屏幕尺寸
        self.screen_width = parent.winfo_screenwidth()
        self.screen_height = parent.winfo_screenheight()
        
        # 随机初始位置（底部随机位置）
        self.start_x = random.randint(100, self.screen_width - 100)
        self.start_y = self.screen_height + random.randint(20, 100)
        
        # 目标高度范围（确保在屏幕可见区域内）
        self.target_min_y = self.screen_height // 4
        self.target_max_y = self.screen_height // 2
        self.target_y = random.randint(self.target_min_y, self.target_max_y)
        
        # 批次ID
        self.batch_id = batch_id
        
        # 创建主窗口
        self.window = tk.Toplevel(parent)
        self.window.title(f'短语上升爆炸-批次{batch_id}')
        self.window.geometry(f"400x100+{self.start_x-200}+{self.start_y-50}")
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 1.0)
        self.window.attributes('-transparentcolor', 'black')
        
        # 创建画布
        self.canvas = tk.Canvas(
            self.window, 
            width=400, 
            height=100,
            highlightthickness=0,
            bg='black'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 动画状态
        self.animation_running = True
        self.current_y = self.start_y
        self.speed = random.uniform(2, 4)  # 随机上升速度
        self.has_exploded = False
        self.explosion_triggered = False  # 新增：确保爆炸只触发一次
        
        # 初始短语
        if phrase_index is not None and phrase_index < len(phrases):
            self.initial_phrase = phrases[phrase_index]
        else:
            self.initial_phrase = random.choice(phrases)
        self.initial_color = random.choice(text_colors)
        self.initial_size = random.randint(20, 28)
        
        # 爆炸后的短语
        self.exploded_phrases = []
        
        # 添加到实例列表
        phrase_instances.append(self)
        
        # 开始上升动画
        self.animate_rise()
    
    def draw_initial_phrase(self):
        """绘制初始短语"""
        self.canvas.delete("all")
        
        # 绘制初始短语
        self.canvas.create_text(
            200, 50,
            text=self.initial_phrase,
            fill=self.initial_color,
            font=("微软雅黑", self.initial_size, "bold"),
            anchor=tk.CENTER
        )
    
    def create_explosion(self):
        """创建爆炸效果"""
        # 创建多个随机短语向各个方向迸发
        explosion_count = random.randint(15, 25)  # 随机爆炸短语数量
        for _ in range(explosion_count):
            phrase = random.choice(phrases)
            color = random.choice(text_colors)
            
            # 随机方向
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 10)
            
            exploded_phrase = {
                'text': phrase,
                'color': color,
                'x': self.start_x,
                'y': self.current_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(120, 150),
                'size': random.randint(14, 22),
                'window': None
            }
            
            self.exploded_phrases.append(exploded_phrase)
        
        # 创建爆炸后的短语窗口
        for phrase in self.exploded_phrases:
            self.create_phrase_window(phrase)
    
    def create_phrase_window(self, phrase_data):
        """为每个爆炸短语创建独立窗口"""
        window = tk.Toplevel(self.window)
        window.title('爆炸短语')
        window_width = random.randint(200, 400)
        window_height = random.randint(60, 100)
        window.geometry(f"{window_width}x{window_height}+{int(phrase_data['x']-window_width//2)}+{int(phrase_data['y']-window_height//2)}")
        window.overrideredirect(True)
        window.attributes('-topmost', True)
        window.attributes('-alpha', 1.0)
        window.attributes('-transparentcolor', 'black')
        
        canvas = tk.Canvas(
            window, 
            width=window_width, 
            height=window_height,
            highlightthickness=0,
            bg='black'
        )
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绘制短语
        canvas.create_text(
            window_width//2, window_height//2,
            text=phrase_data['text'],
            fill=phrase_data['color'],
            font=("微软雅黑", phrase_data['size']),
            anchor=tk.CENTER
        )
        
        phrase_data['window'] = window
        phrase_data['canvas'] = canvas
        phrase_data['width'] = window_width
        phrase_data['height'] = window_height
        active_windows.append(window)
    
    def update_exploded_phrases(self):
        """更新爆炸后的短语位置"""
        for phrase in self.exploded_phrases[:]:
            # 更新位置
            phrase['x'] += phrase['vx']
            phrase['y'] += phrase['vy']
            phrase['life'] -= 1
            
            # 减速效果
            phrase['vx'] *= 0.97
            phrase['vy'] *= 0.97
            
            # 重力效果
            phrase['vy'] += 0.1
            
            # 更新窗口位置
            if phrase['window'] and phrase['window'].winfo_exists():
                phrase['window'].geometry(
                    f"{phrase['width']}x{phrase['height']}+" +
                    f"{int(phrase['x']-phrase['width']//2)}+{int(phrase['y']-phrase['height']//2)}"
                )
                
                # 根据生命周期设置透明度
                alpha = phrase['life'] / 100
                phrase['window'].attributes('-alpha', max(0, alpha))
            
            # 如果生命周期结束，移除短语
            if phrase['life'] <= 0:
                if phrase['window'] and phrase['window'].winfo_exists():
                    phrase['window'].destroy()
                if phrase['window'] in active_windows:
                    active_windows.remove(phrase['window'])
                self.exploded_phrases.remove(phrase)
    
    def animate_rise(self):
        """上升动画"""
        if not self.animation_running:
            return
        
        # 更新位置
        self.current_y -= self.speed
        
        # 更新窗口位置
        self.window.geometry(f"400x100+{self.start_x-200}+{int(self.current_y-50)}")
        
        # 绘制短语
        self.draw_initial_phrase()
        
        # 修复：更准确的爆炸条件判断
        # 检查是否到达目标高度且没有爆炸过
        if (self.current_y <= self.target_y and not self.explosion_triggered) or (self.current_y <= 100 and not self.explosion_triggered):
            self.explosion_triggered = True
            self.has_exploded = True
            self.start_explosion()
        
        # 如果还没有爆炸且还在屏幕内，继续上升
        if not self.has_exploded and self.current_y > -100:
            self.window.after(30, self.animate_rise)
        elif self.has_exploded:
            # 爆炸后，继续更新爆炸短语
            self.animate_explosion()
    
    def start_explosion(self):
        """开始爆炸"""
        self.create_explosion()
    
    def animate_explosion(self):
        """爆炸动画"""
        if not self.animation_running:
            return
        
        # 更新爆炸后的短语位置
        self.update_exploded_phrases()
        
        # 如果还有爆炸短语，继续动画
        if self.exploded_phrases:
            self.window.after(30, self.animate_explosion)
        else:
            # 爆炸结束，关闭窗口
            self.animation_running = False
            if self.window.winfo_exists():
                self.window.destroy()
            if self.window in active_windows:
                active_windows.remove(self.window)
            if self in phrase_instances:
                phrase_instances.remove(self)

def create_rising_explosion(phrase_index=None, batch_id=0):
    """创建上升爆炸效果"""
    try:
        explosion = RisingPhraseExplosion(root, phrase_index, batch_id)
        active_windows.append(explosion.window)
        
        # 设置自动关闭
        def close_explosion():
            explosion.animation_running = False
            if explosion.window.winfo_exists():
                explosion.window.destroy()
            if explosion.window in active_windows:
                active_windows.remove(explosion.window)
            
            # 关闭所有爆炸短语窗口
            for phrase in explosion.exploded_phrases[:]:
                if phrase['window'] and phrase['window'].winfo_exists():
                    phrase['window'].destroy()
                if phrase['window'] in active_windows:
                    active_windows.remove(phrase['window'])
            
            # 从实例列表中移除
            if explosion in phrase_instances:
                phrase_instances.remove(explosion)
        
        explosion.window.after(15000, close_explosion)  # 延长自动关闭时间
        
    except Exception as e:
        print(f"创建上升爆炸时出错: {e}")

def create_batch(batch_id, batch_size=15):
    """创建一批上升爆炸效果"""
    print(f"创建第 {batch_id} 批短语，数量: {batch_size}")
    
    for i in range(batch_size):
        # 随机延迟开始
        delay = random.randint(0, 2000)
        # 选择短语索引
        phrase_idx = (batch_id * batch_size + i) % len(phrases)
        root.after(delay, lambda idx=phrase_idx, bid=batch_id: create_rising_explosion(idx, bid))

def start_explosion_sequence():
    """开始爆炸序列"""
    print("开始短语上升爆炸效果...")
    
    # 创建多个批次的短语
    batch_count = 5  # 批次数量
    batch_size = 4  # 每批短语数量
    
    for batch_id in range(batch_count):
        # 每批之间有一定延迟
        batch_delay = batch_id * 5000  # 每5秒一批
        root.after(batch_delay, lambda bid=batch_id: create_batch(bid, batch_size))
    
    # 程序结束检查
    root.after(40000, check_if_all_closed)

def check_if_all_closed():
    """检查所有窗口是否已关闭"""
    if len(active_windows) == 0:
        print("特效已结束")
        root.quit()
    else:
        root.after(1000, check_if_all_closed)

def close_all_windows():
    """立即关闭所有活动窗口"""
    global active_windows, phrase_instances
    
    # 关闭所有短语实例
    for instance in phrase_instances[:]:
        instance.animation_running = False
        if instance.window and instance.window.winfo_exists():
            instance.window.destroy()
        
        # 关闭所有爆炸短语窗口
        for phrase in instance.exploded_phrases[:]:
            if phrase['window'] and phrase['window'].winfo_exists():
                phrase['window'].destroy()
    
    # 关闭所有活动窗口
    for window in active_windows[:]:
        try:
            window.destroy()
        except:
            pass
    
    active_windows.clear()
    phrase_instances.clear()
    print("正在关闭所有窗口...")

def on_space(event):
    """全局空格键处理"""
    close_all_windows()
    print("已停止特效")

def on_escape(event):
    """全局ESC键处理"""
    close_all_windows()
    root.quit()

# 短语库
phrases = [
    "永远相信美好的事情即将发生",
    "生活不止眼前的苟且",
    "心中有光，脚下有路",
    "梦想不会发光，发光的是追梦的你",
    "每一天都是新的开始",
    "坚持就是胜利",
    "相信自己，你能做到",
    "微笑面对生活",
    "感恩每一个当下",
    "努力成为更好的自己",
    "阳光总在风雨后",
    "爱是唯一的答案",
    "简单生活，快乐相伴",
    "勇敢追逐你的梦想",
    "时光不负有心人",
    "心若向阳，无畏悲伤",
    "活在当下，珍惜拥有",
    "努力让未来更美好",
    "相信爱的力量",
    "每一天都值得珍惜",
    "成功源于不懈的努力",
    "心态决定一切",
    "善良是最好的投资",
    "快乐是一种选择",
    "知识改变命运",
    "行动胜过千言万语",
    "耐心等待美好的到来",
    "自律给我自由",
    "困难是成长的阶梯",
    "感恩生活中的小确幸",
    "做自己的太阳",
    "用心感受生活的美好",
    "保持好奇心，探索未知",
    "付出总会有回报",
    "珍惜眼前人",
    "不忘初心，方得始终",
    "平凡中见伟大",
    "真诚待人，用心做事",
    "乐观面对每一天",
    "勇敢做自己",
    "相信明天会更好",
    "用心聆听世界的声音",
    "让世界因你而不同",
    "坚持自己的梦想",
    "用心感受每一刻",
    "勇敢面对挑战",
    "珍惜每一次相遇",
    "用心创造美好",
    "保持谦逊，不断学习",
    "用心感受生命的意义"
]

# 文字颜色库
text_colors = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF', '#FF00FF',
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD',
    '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA',
    '#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C',
    '#E67E22', '#34495E', '#16A085', '#8E44AD', '#2C3E50', '#27AE60',
    '#D35400', '#C0392B', '#BDC3C7', '#7F8C8D', '#A569BD', '#48C9B0',
    '#F1948A', '#85C1E9', '#73C6B6', '#BB8FCE', '#F7DC6F', '#82E0AA'
]

def main():
    """程序主入口"""
    global root
    
    root = tk.Tk()
    root.withdraw()
    
    print("多批次短语上升爆炸特效程序已启动!")
    print(f"短语库包含 {len(phrases)} 个短语")
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