"""
多层短语爆炸特效程序
功能：中心短语变大，然后爆炸出十个短语，每个短语移动后再爆炸出十个短语
作者：RUN
版本：爆炸后立即消失版
"""

import tkinter as tk
import random
import math
import time

# 全局变量
active_windows = []
root = None  # 全局根窗口引用

class MultiLevelExplosion:
    """多层爆炸效果类"""
    def __init__(self, parent):
        global root
        # 保存根窗口引用
        self.root = parent
        
        # 获取屏幕尺寸
        self.screen_width = parent.winfo_screenwidth()
        self.screen_height = parent.winfo_screenheight()
        
        # 中心位置
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        
        # 创建中心窗口
        self.center_window = tk.Toplevel(parent)
        self.center_window.title('中心短语')
        self.center_window.geometry(f"600x200+{self.center_x-300}+{self.center_y-100}")
        self.center_window.overrideredirect(True)
        self.center_window.attributes('-topmost', True)
        self.center_window.attributes('-alpha', 1.0)
        self.center_window.attributes('-transparentcolor', 'black')
        
        # 创建画布
        self.center_canvas = tk.Canvas(
            self.center_window, 
            width=600, 
            height=200,
            highlightthickness=0,
            bg='black'
        )
        self.center_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 动画状态
        self.animation_running = True
        self.center_size = 40
        self.max_center_size = 120
        self.has_exploded = False
        
        # 初始短语
        self.initial_phrase = random.choice(phrases)
        self.initial_color = random.choice(text_colors)
        
        # 第一层爆炸短语
        self.first_level_particles = []
        
        # 第二层爆炸短语
        self.second_level_particles = []
        
        # 开始中心动画
        self.animate_center()
    
    def draw_center_phrase(self):
        """绘制中心短语"""
        self.center_canvas.delete("all")
        
        # 绘制中心短语
        self.center_canvas.create_text(
            300, 100,
            text=self.initial_phrase,
            fill=self.initial_color,
            font=("微软雅黑", int(self.center_size), "bold"),
            anchor=tk.CENTER
        )
    
    def create_first_explosion(self):
        """创建第一层爆炸效果"""
        # 创建10个随机短语向各个方向迸发
        for _ in range(10):
            phrase = random.choice(phrases)
            color = random.choice(text_colors)
            
            # 随机方向
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 10)
            
            particle = {
                'text': phrase,
                'color': color,
                'x': self.center_x,
                'y': self.center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 150,
                'max_life': 150,
                'size': random.randint(24, 32),
                'window': None,
                'has_exploded': False,
                'explosion_timer': random.randint(50, 80)
            }
            
            self.first_level_particles.append(particle)
        
        # 创建第一层爆炸短语窗口
        for particle in self.first_level_particles:
            self.create_particle_window(particle, 1)
    
    def create_second_explosion(self, particle):
        """创建第二层爆炸效果"""
        # 立即移除第一层粒子
        if particle['window'] and particle['window'].winfo_exists():
            particle['window'].destroy()
        if particle['window'] in active_windows:
            active_windows.remove(particle['window'])
        if particle in self.first_level_particles:
            self.first_level_particles.remove(particle)
        
        # 创建10个随机短语向各个方向迸发
        for _ in range(20):
            phrase = random.choice(phrases)
            color = random.choice(text_colors)
            
            # 随机方向
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(4, 8)
            
            second_particle = {
                'text': phrase,
                'color': color,
                'x': particle['x'],
                'y': particle['y'],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 120,  # 减少第二层生命周期，让它们更快消失
                'max_life': 120,
                'size': random.randint(14, 18),
                'window': None
            }
            
            self.second_level_particles.append(second_particle)
        
        # 创建第二层爆炸短语窗口
        for second_particle in self.second_level_particles[-10:]:
            self.create_particle_window(second_particle, 2)
    
    def create_particle_window(self, particle_data, level):
        """为每个爆炸短语创建独立窗口"""
        # 根据层级调整窗口大小
        if level == 1:  # 第一层
            window_width = 400
            window_height = 100
        else:  # 第二层
            window_width = 250
            window_height = 60
        
        # 确保坐标为整数
        window_x = int(particle_data['x'] - window_width // 2)
        window_y = int(particle_data['y'] - window_height // 2)
        
        # 使用根窗口作为父窗口，而不是中心窗口
        window = tk.Toplevel(self.root)
        window.title(f'爆炸短语-第{level}层')
        window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
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
            text=particle_data['text'],
            fill=particle_data['color'],
            font=("微软雅黑", particle_data['size']),
            anchor=tk.CENTER
        )
        
        particle_data['window'] = window
        particle_data['canvas'] = canvas
        particle_data['width'] = window_width
        particle_data['height'] = window_height
        active_windows.append(window)
    
    def update_particles(self, particles_list, is_first_level=False):
        """更新粒子位置"""
        for particle in particles_list[:]:
            # 更新位置
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # 如果是第一层粒子，减少爆炸计时器
            if is_first_level and not particle['has_exploded']:
                particle['explosion_timer'] -= 1
                
                # 检查是否应该爆炸
                if particle['explosion_timer'] <= 0 and not particle['has_exploded']:
                    particle['has_exploded'] = True
                    self.create_second_explosion(particle)
                    continue  # 跳过这个粒子的后续更新，因为它已经被移除
            
            # 更新生命值（所有粒子）
            particle['life'] -= 1.0  # 增加生命值减少速度
            
            # 减速效果
            particle['vx'] *= 0.98
            particle['vy'] *= 0.98
            
            # 重力效果
            particle['vy'] += 0.1
            
            # 更新窗口位置
            if particle['window'] and particle['window'].winfo_exists():
                # 确保坐标为整数
                window_x = int(particle['x'] - particle['width'] // 2)
                window_y = int(particle['y'] - particle['height'] // 2)
                
                particle['window'].geometry(
                    f"{particle['width']}x{particle['height']}+{window_x}+{window_y}"
                )
                
                # 根据生命周期设置透明度
                alpha = particle['life'] / particle['max_life']
                particle['window'].attributes('-alpha', max(0, alpha))
            
            # 如果生命周期结束，移除粒子
            if particle['life'] <= 0:
                if particle['window'] and particle['window'].winfo_exists():
                    particle['window'].destroy()
                if particle['window'] in active_windows:
                    active_windows.remove(particle['window'])
                particles_list.remove(particle)
    
    def animate_center(self):
        """中心动画"""
        if not self.animation_running:
            return
        
        # 增大字体
        self.center_size += 2.0
        
        # 绘制中心短语
        self.draw_center_phrase()
        
        # 检查是否达到最大尺寸
        if self.center_size >= self.max_center_size and not self.has_exploded:
            self.has_exploded = True
            self.start_first_explosion()
        
        # 如果还没有爆炸，继续动画
        if not self.has_exploded:
            self.center_window.after(30, self.animate_center)
        else:
            # 爆炸后，开始更新粒子
            self.animate_particles()
    
    def start_first_explosion(self):
        """开始第一层爆炸"""
        self.create_first_explosion()
        
        # 关闭中心窗口
        if self.center_window.winfo_exists():
            self.center_window.destroy()
        if self.center_window in active_windows:
            active_windows.remove(self.center_window)
    
    def animate_particles(self):
        """粒子动画"""
        if not self.animation_running:
            return
        
        # 更新第一层粒子
        self.update_particles(self.first_level_particles, is_first_level=True)
        
        # 更新第二层粒子
        self.update_particles(self.second_level_particles, is_first_level=False)
        
        # 如果还有粒子，继续动画
        if self.first_level_particles or self.second_level_particles:
            # 使用根窗口的after方法
            self.root.after(30, self.animate_particles)
        else:
            # 所有粒子消失，动画结束
            self.animation_running = False

def create_multi_level_explosion():
    """创建多层爆炸效果"""
    try:
        explosion = MultiLevelExplosion(root)
        active_windows.append(explosion.center_window)
        
        # 设置自动关闭
        def close_explosion():
            explosion.animation_running = False
            if explosion.center_window and explosion.center_window.winfo_exists():
                explosion.center_window.destroy()
            if explosion.center_window in active_windows:
                active_windows.remove(explosion.center_window)
            
            # 关闭所有粒子窗口
            for particle in explosion.first_level_particles[:]:
                if particle['window'] and particle['window'].winfo_exists():
                    particle['window'].destroy()
                if particle['window'] in active_windows:
                    active_windows.remove(particle['window'])
            
            for particle in explosion.second_level_particles[:]:
                if particle['window'] and particle['window'].winfo_exists():
                    particle['window'].destroy()
                if particle['window'] in active_windows:
                    active_windows.remove(particle['window'])
        
        root.after(15000, close_explosion)  # 减少自动关闭时间
        
    except Exception as e:
        print(f"创建多层爆炸时出错: {e}")
        import traceback
        traceback.print_exc()

def start_explosion_sequence():
    """开始爆炸序列"""
    print("开始多层短语爆炸效果...")
    create_multi_level_explosion()
    
    # 程序结束检查
    root.after(20000, check_if_all_closed)  # 减少程序运行时间

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

# 短语库
phrases = [
    "你是最棒的", "一切都会好的", "今天也要开心", "相信自己", "坚持下去",
    "你很特别",  "保持希望", "永不放弃",
    "梦想成真", "未来可期", "勇敢前行", "心存感恩", "珍惜当下",
    "简单快乐", "知足常乐", "温暖如初", "岁月静好", "平安喜乐",
    "万事胜意", "天天开心", "好运连连", "幸福满满", "心想事成",
    "健康平安", "笑口常开", "友谊长存", "爱情甜蜜",
    "家庭和睦", "工作顺利",  "美丽心情", "放松一下",
    "慢慢来", "别着急", "你可以的", "爱自己", "感恩有你",
    "享受生活", "拥抱阳光", "晚安好梦", "早安加油", "午安休息",
    "多喝热水", "记得吃饭", "天冷加衣", "照顾好自己", "别太累了",
    "休息一下", "放松心情", "保持微笑", "世界爱你", "宇宙祝福",
    "天使守护", "好运相伴", "幸福相随", "快乐永驻", "财源滚滚",
    "事业有成", "蔡徐坤", "爱情美满", "友谊万岁", "亲情永恒",
    "幸福安康", "吉祥如意", "寿比南山", "福如东海",
    "龙凤呈祥", "金玉满堂", "喜气洋洋", "欢天喜地", "油饼",
    "冬日暖阳", "厉不厉害你坤哥", "夏雨雨人", "秋风送爽", "冬温夏清"
]

# 文字颜色库
text_colors = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF', '#FF00FF',
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD',
    '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA',
    '#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C',
    '#E67E22', '#34495E', '#16A085', '#8E44AD', '#2C3E50', '#27AE60'
]

def main():
    """程序主入口"""
    global root
    
    root = tk.Tk()
    root.withdraw()
    
    print("多层短语爆炸特效程序已启动!")
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