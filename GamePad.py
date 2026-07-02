import time
import threading

import os
import datetime
import ctypes
from ctypes import windll, Structure, c_long, byref
from krita import *
import math

def debug_log(message):
    # 将日志文件保存在用户主目录下，方便查找
    log_path = os.path.join(os.path.expanduser("~"), "krita_plugin_debug.log")
    with open(log_path, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

class GamepadThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True
        self.error_message = None
        self._consecutive_errors = 0  # 添加连续错误计数器
        self._max_consecutive_errors = 10  # 最大连续错误次数
        self.key_action={}
        self.app=Krita.instance()
        self.lx=0
        self.ly=0
        self.rx=0
        self.ry=0
        self.deg=0

    def setKeyActionMap(self,key_action):
        self.key_action=key_action

    def run(self):
        while self.running:
            try:
                from .inputs import get_gamepad
                events = get_gamepad()
                # 成功获取事件，重置错误计数
                self._consecutive_errors = 0
                self.error_message = None

                for event in events:
                    if self.running:  # 检查是否仍在运行
                        self.process_event(event)

            except ImportError:
                self.error_message = "未安装 'inputs' 包。请安装后重试。"
                self._consecutive_errors += 1
                time.sleep(1)

            except Exception as e:
                self._consecutive_errors += 1
                if "No gamepad found" in str(e):
                    self.error_message = "未检测到手柄。请确保手柄已连接。"
                else:
                    self.error_message = f"手柄错误: {e}"
                time.sleep(0.5)  # 减少等待时间，提高响应速度

            # 如果连续错误次数过多，可能需要关闭控制
            if self._consecutive_errors >= self._max_consecutive_errors:
                self.error_message = "多次无法检测到手柄，已自动关闭控制。"
                break

    def process_event(self, event):
        """处理手柄事件"""
        # debug_log(f"{event.ev_type}, {event.code}, {event.state}")
        # ABS_Z ABS_RZ 0~255 BTN_ SELECT START TL TR THUMBL THUMBR WEST NORTH SOUTH EAST    
        if event.code in self.key_action.keys() and event.state!=0:
            v=self.key_action[event.code]
            if isinstance(v,str):
                self.app.action(v).trigger()
            else:
                v(self.app)
            return
        elif event.code == 'ABS_HAT0Y':#-1 up 1 down
            ud = event.state# -1 1
            if ud==-1:
                self.app.action("make_brush_color_saturated").trigger()
                return
            elif ud==1:
                self.app.action("make_brush_color_desaturated").trigger()
                return
        elif event.code == 'ABS_HAT0X':#-1 left 1 right
            lr = event.state# -1 1
            if lr==-1:
                self.app.action("make_brush_color_lighter").trigger()
                return
            elif lr==1:
                self.app.action("make_brush_color_darker").trigger()
                return
        if event.code == 'ABS_X':
            self.lx = event.state / 32768.0
        if event.code == 'ABS_Y':
            self.ly = event.state / 32768.0
        if event.code == 'ABS_RX':
            self.rx = event.state / 32768.0
        if event.code == 'ABS_RY':
            self.ry = event.state / 32768.0
        # debug_log(f"{self.lx},{self.ly}")
        self.hue_color()  
        self.grey_color()

    def hue_color(self):
        x=-self.ly
        y=-self.lx 
        radius=math.hypot(x,y)
        if radius>0.1:
            rad = math.atan2(y, x)
            self.deg = math.degrees(rad)
            r,g,b=HSV2RGB(self.deg,radius,1)
            set_color(r,g,b,self.app)

    def grey_color(self):
        radius=math.hypot(self.rx,self.ry)
        if radius>0.1:
            r,g,b=HSV2RGB(self.deg,abs(self.rx),(self.ry+1)*0.5)
            set_color(r,g,b,self.app)



class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def sample_color(app):
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    hdc = ctypes.windll.user32.GetDC(0)
    color = ctypes.windll.gdi32.GetPixel(hdc, pt.x, pt.y)
    ctypes.windll.user32.ReleaseDC(0, hdc)
    r = color & 0xFF
    g = (color >> 8) & 0xFF
    b = (color >> 16) & 0xFF
    set_color(r/255,g/255,b/255,app)

def set_color(r,g,b,app=Krita.instance()):
    activeView = app.activeWindow().activeView()
    colorRed = ManagedColor("RGBA", "U8", "")
    colorComponents = colorRed.components()
    colorComponents[0] = b # Blue
    colorComponents[1] = g # Green
    colorComponents[2] = r # Red
    colorComponents[3] = 1.0 # Alpha???
    colorRed.setComponents(colorComponents)
    activeView.setForeGroundColor(colorRed)

def eraser(app):
    app.action("KritaShape/KisToolBrush").trigger()    
    app.action("erase_action").trigger() 

def hue_color(x,y,app): 
    r=math.hypot(x,y)
    if r>0.1:
        rad = math.atan2(y, x)
        deg = math.degrees(rad)
        r,g,b=HSV2RGB(deg,r,1)
        set_color(r,g,b,app)



def HSV2RGB(h, s, v):# 360,1,1
    if s == 0:
        r = g = b = v
        return r, g, b
    h_norm = h / 60.0
    i = int(h_norm) % 6
    f = h_norm - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:  # i == 5
        r, g, b = v, p, q
    return r, g, b#0,1
