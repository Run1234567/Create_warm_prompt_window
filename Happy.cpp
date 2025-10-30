#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX_WINDOWS 200

// 使用英文避免编码问题
const char* tips[] = {
    "Hello!", "Keep smiling!", "Stay positive!",
    "Drink water!", "Take care!", "Be happy!",
    "You are awesome!", "Keep going!", "Believe in yourself!",
    "Have a nice day!", "Stay strong!", "You can do it!",
    "Take a break!", "Relax!", "Enjoy life!",
    "Keep learning!", "Stay curious!", "Dream big!"
};
int tipCount = 18;

int exitFlag = 0;
HWND windows[MAX_WINDOWS];
int windowCount = 0;

// 窗口过程函数
LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            
            // 设置鲜艳的背景颜色
            HBRUSH hBrush = CreateSolidBrush(RGB(255, 255, 200)); // 浅黄色背景
            FillRect(hdc, &ps.rcPaint, hBrush);
            DeleteObject(hBrush);
            
            // 设置醒目的文本颜色
            SetTextColor(hdc, RGB(255, 0, 0)); // 红色文本
            SetBkMode(hdc, TRANSPARENT);       // 透明背景
            
            // 创建更大的字体
            HFONT hFont = CreateFontA(
                28,                           // 字体高度
                0,                            // 宽度
                0,                            // 旋转角度
                0,                            // 方向
                FW_BOLD,                      // 粗体
                FALSE,                        // 斜体
                FALSE,                        // 下划线
                FALSE,                        // 删除线
                DEFAULT_CHARSET,              // 字符集
                OUT_DEFAULT_PRECIS,           // 输出精度
                CLIP_DEFAULT_PRECIS,          // 剪裁精度
                DEFAULT_QUALITY,              // 质量
                DEFAULT_PITCH | FF_SWISS,     // 间距和字体族
                "Arial"                       // 字体名称
            );
            HFONT hOldFont = (HFONT)SelectObject(hdc, hFont);
            
            // 获取窗口标题作为文本
            char text[100];
            GetWindowTextA(hwnd, text, sizeof(text));
            
            // 绘制文本
            RECT rect;
            GetClientRect(hwnd, &rect);
            
            // 添加黑色边框效果
            SetTextColor(hdc, RGB(0, 0, 0)); // 黑色边框
            for (int x = -2; x <= 2; x++) {
                for (int y = -2; y <= 2; y++) {
                    if (x != 0 || y != 0) {
                        RECT shadowRect = rect;
                        shadowRect.left += x;
                        shadowRect.top += y;
                        DrawTextA(hdc, text, -1, &shadowRect, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
                    }
                }
            }
            
            // 绘制主要文本
            SetTextColor(hdc, RGB(255, 0, 0)); // 红色文本
            DrawTextA(hdc, text, -1, &rect, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
            
            // 恢复原来的字体并删除新字体
            SelectObject(hdc, hOldFont);
            DeleteObject(hFont);
            
            EndPaint(hwnd, &ps);
            return 0;
        }
        
        case WM_ERASEBKGND:
            // 我们已经处理背景，不需要系统擦除
            return 1;
            
        case WM_KEYDOWN:
            if (wParam == VK_SPACE) {
                exitFlag = 1;
                PostQuitMessage(0);
                return 0;
            }
            break;
            
        case WM_DESTROY:
            // 从窗口列表中移除
            for (int i = 0; i < windowCount; i++) {
                if (windows[i] == hwnd) {
                    for (int j = i; j < windowCount - 1; j++) {
                        windows[j] = windows[j + 1];
                    }
                    windowCount--;
                    break;
                }
            }
            
            // 如果所有窗口都关闭了，退出程序
            if (windowCount == 0) {
                PostQuitMessage(0);
            }
            return 0;
            
        case WM_CLOSE:
            DestroyWindow(hwnd);
            return 0;
    }
    
    return DefWindowProcA(hwnd, uMsg, wParam, lParam);
}

// 创建飘字窗口
HWND CreateFloatingWindow(HINSTANCE hInstance, int index) {
    int textIndex = rand() % tipCount;
    
    // 计算随机位置
    int screenWidth = GetSystemMetrics(SM_CXSCREEN);
    int screenHeight = GetSystemMetrics(SM_CYSCREEN);
    int windowWidth = 400;  // 增大窗口宽度
    int windowHeight = 200; // 增大窗口高度
    int x = rand() % (screenWidth - windowWidth);
    int y = rand() % (screenHeight - windowHeight);
    
    // 创建窗口
    HWND hwnd = CreateWindowExA(
        WS_EX_TOPMOST | WS_EX_TOOLWINDOW,     // 顶层窗口，不在任务栏显示
        "FloatingTextClass",                  // 窗口类名
        tips[textIndex],                      // 窗口标题(即显示的文本)
        WS_POPUP | WS_VISIBLE | WS_BORDER,    // 弹出式窗口，可见，有边框
        x, y, windowWidth, windowHeight,      // 位置和大小
        NULL, NULL, hInstance, NULL           // 无父窗口，无菜单
    );
    
    if (hwnd) {
        // 设置窗口样式，去掉标题栏但保留边框
        SetWindowLongA(hwnd, GWL_STYLE, WS_POPUP | WS_VISIBLE | WS_BORDER);
        
        // 添加到窗口列表
        if (windowCount < MAX_WINDOWS) {
            windows[windowCount++] = hwnd;
        }
        
        // 强制重绘窗口
        InvalidateRect(hwnd, NULL, TRUE);
        UpdateWindow(hwnd);
        
        // 确保窗口可见
        ShowWindow(hwnd, SW_SHOW);
        BringWindowToTop(hwnd);
    }
    
    return hwnd;
}

// 关闭所有窗口
void CloseAllWindows() {
    for (int i = 0; i < windowCount; i++) {
        if (IsWindow(windows[i])) {
            DestroyWindow(windows[i]);
        }
    }
    windowCount = 0;
}

// 自动关闭窗口的线程函数
DWORD WINAPI AutoCloseThread(LPVOID lpParam) {
    HWND hwnd = (HWND)lpParam;
    
    // 等待10秒后关闭窗口
    Sleep(10000);
    
    if (IsWindow(hwnd) && !exitFlag) {
        DestroyWindow(hwnd);
    }
    
    return 0;
}

int main() {
    // 初始化随机数种子
    srand((unsigned int)time(NULL));
    HINSTANCE hInstance = GetModuleHandle(NULL);
    
    // 注册窗口类
    WNDCLASSA wc = {0};
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = "FloatingTextClass";
    wc.hbrBackground = NULL; // 我们自己在WM_PAINT中绘制背景
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hIcon = LoadIcon(NULL, IDI_APPLICATION);
    wc.style = CS_HREDRAW | CS_VREDRAW; // 窗口大小改变时重绘
    
    if (!RegisterClassA(&wc)) {
        printf("Window class registration failed!\n");
        return 1;
    }
    
    printf("===============================================\n");
    printf("          Floating Windows Program\n");
    printf("===============================================\n");
    printf("Will create up to %d windows\n", MAX_WINDOWS);
    printf("Each window will close after 10 seconds\n");
    printf("Press SPACE to close all windows and exit\n");
    printf("Starting in 3 seconds...\n");
    
    Sleep(3000);
    
    printf("Creating windows...\n");
    
    // 创建窗口
    for (int i = 0; i < MAX_WINDOWS && !exitFlag; i++) {
        HWND hwnd = CreateFloatingWindow(hInstance, i);
        if (hwnd) {
            // 创建自动关闭线程
            CreateThread(NULL, 0, AutoCloseThread, hwnd, 0, NULL);
            
            printf("Created window %d: %s\n", i + 1, tips[i % tipCount]);
            
            // 处理消息队列，防止界面卡死
            MSG msg;
            while (PeekMessageA(&msg, NULL, 0, 0, PM_REMOVE)) {
                TranslateMessage(&msg);
                DispatchMessageA(&msg);
            }
            
            // 1.5秒延迟
            Sleep(150);
        } else {
            printf("Failed to create window %d\n", i + 1);
        }
        
        if (exitFlag) break;
    }
    
    if (!exitFlag) {
        printf("Finished creating windows. Waiting for auto-close or press SPACE to exit...\n");
    }
    
    // 主消息循环
    MSG msg;
    while (!exitFlag && GetMessageA(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }
    
    // 关闭所有窗口
    CloseAllWindows();
    
    // 确保注销窗口类
    UnregisterClassA("FloatingTextClass", hInstance);
    
    printf("Program ended. Goodbye!\n");
    return 0;
}