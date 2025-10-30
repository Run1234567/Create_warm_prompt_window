"""
多窗口温馨提醒程序
功能：在屏幕上以较慢的速度弹出温馨提醒窗口，每个窗口显示随机的温馨话语
作者：RUN
版本：5.0 
"""

import tkinter as tk
import random
import time
import sys

# 全局变量
exit_flag = False  # 程序退出标志
active_windows = []  # 跟踪所有活动窗口
window_queue = []  # 待创建的窗口队列
total_windows_created = 0  # 已创建窗口计数
max_windows = 400  # 最大窗口数量限制

# 可调整的运行参数
CREATE_DELAY = 100  # 窗口创建间隔(毫秒)
BATCH_SIZE = 50  # 每批添加到队列的窗口数量
WINDOWS_PER_BATCH = 2  # 每批实际创建的窗口数量
AUTO_CLOSE_TIME = 150000  # 窗口自动关闭时间(毫秒)
START_DELAY = 5000  # 程序启动延迟(毫秒)

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
            # 创建新窗口
            window = tk.Toplevel()
            active_windows.append(window)
            
            # 设置窗口属性
            window.title('温馨提示')
            window.geometry(f"{window_info['width']}x{window_info['height']}+{window_info['x']}+{window_info['y']}")
            window.resizable(False, False)
            
            # 创建显示文本的标签
            label = tk.Label(
                window,
                text=window_info['tip'],
                bg=window_info['bg_color'],
                font=('微软雅黑', 16),
                width=30,
                height=3,
                wraplength=230  # 文本自动换行
            )
            label.pack()
            
            # 窗口置顶显示
            window.attributes('-topmost', True)
            
            def on_space(event, win=window):
                """空格键事件：关闭所有窗口"""
                global exit_flag
                exit_flag = True
                close_all_windows()
            
            def on_escape(event, win=window):
                """ESC键事件：强制退出程序"""
                global exit_flag
                exit_flag = True
                close_all_windows()
                root.quit()
            
            def on_closing(win=window):
                """窗口关闭事件处理"""
                if win in active_windows:
                    active_windows.remove(win)
                win.destroy()
                # 检查是否所有窗口都已关闭且达到最大数量
                if len(active_windows) == 0 and total_windows_created >= max_windows:
                    root.quit()
            
            # 绑定键盘事件和关闭事件
            window.bind('<space>', on_space)
            window.bind('<Escape>', on_escape)
            window.protocol("WM_DELETE_WINDOW", lambda win=window: on_closing(win))
            
            # 设置自动关闭定时器
            window.after(AUTO_CLOSE_TIME, lambda win=window: on_closing(win))
            
            total_windows_created += 1
            print(f"已创建第 {total_windows_created} 个窗口: {window_info['tip']}")
            
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
    
    # 温馨话语库
    tips = [
        "多喝水哦~", "保持微笑呀", "每天都要元气满满", "记得吃水果", "保持好心情",
        "好好爱自己", "我想你了", "梦想成真", "期待下一次见面", "金榜题名",
        "顺顺利利", "早点休息", "愿所有烦恼都消失", "别熬夜", "今天过得开心嘛",
        "天冷了, 多穿衣服", "你是最棒的", "加油", "相信自己", "坚持就是胜利",
        "放松一下", "休息一会儿", "保持专注", "继续努力", "一切都会好的",
        "未来可期", "阳光总在风雨后", "微笑面对", "保持耐心", "慢慢来",
        "不着急", "享受当下", "感恩每一天", "珍惜时光", "活在当下",
        "今天也要开心", "记得按时吃饭", "照顾好自己", "你是独一无二的",
        "世界因你而美好", "做最真实的自己", "小小的进步也是进步",
        "每一步都算数", "慢慢来比较快", "累了就休息", "别太勉强自己",
        "你已经做得很好了", "今天也要努力呀", "困难只是暂时的", "明天会更好"
    ]
    
    # 背景颜色库
    bg_colors = [
        'lightpink', 'skyblue', 'lightblue', 'lightsteelblue', 'powderblue',
        'lightcyan', 'aliceblue', 'azure', 'lightgreen', 'lavender',
        'lightyellow', 'plum', 'coral', 'bisque', 'aquamarine',
        'mistyrose', 'honeydew', 'lavenderblush', 'oldlace',
        'seashell', 'mintcream', 'linen', 'whitesmoke',
        'peachpuff', 'papayawhip', 'blanchedalmond', 'antiquewhite',
        'lemonchiffon', 'lightgoldenrodyellow', 'palegoldenrod',
        'palegreen', 'lightgreen', 'springgreen', 'mintcream',
        'honeydew', 'lightcyan', 'paleturquoise', 'lightblue',
        'lavender', 'thistle', 'plum', 'pink', 'lightpink'
    ]
    
    # 生成窗口配置信息
    for _ in range(count):
        tip = random.choice(tips)
        bg_color = random.choice(bg_colors)
        
        # 计算随机窗口位置
        window_width = 250
        window_height = 60
        x = random.randrange(0, screen_width - window_width)
        y = random.randrange(0, screen_height - window_height)
        
        window_queue.append({
            'tip': tip,
            'bg_color': bg_color,
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
    print("已关闭所有窗口")

def start_creating_windows():
    """启动窗口创建流程"""
    print("开始创建窗口...")
    
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

def on_space(event):
    """全局空格键处理：停止创建并关闭所有窗口"""
    global exit_flag
    exit_flag = True
    close_all_windows()
    print("已停止创建新窗口，正在关闭所有窗口...")
    root.quit()

def on_escape(event):
    """全局ESC键处理：强制退出程序"""
    global exit_flag
    exit_flag = True
    close_all_windows()
    print("已停止创建新窗口，正在关闭所有窗口...")
    root.quit()

def main():
    """程序主入口"""
    global exit_flag, root
    
    # 初始化主窗口（隐藏）
    root = tk.Tk()
    root.withdraw()
    
    # 显示使用说明
    print("慢速版温馨提醒程序已启动!")
    print(f"将创建最多 {max_windows} 个窗口")
    print("窗口将以较慢的速度逐个显示")
    print("每个窗口会在15秒后自动关闭")
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
        print("程序已结束")

if __name__ == '__main__':
    main()