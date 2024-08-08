import ctypes, win32gui, struct
from ctypes import *
from ctypes import wintypes
from raylib import GetScreenHeight, GetScreenWidth

class Vec2(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float)
    ]


class Vec2_int(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int),
        ("y", ctypes.c_int)
    ]


class Vec3(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float)
    ]

class Vec3_int(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_int),
        ('y', ctypes.c_int),
        ('z', ctypes.c_int)
    ]

class WINDOWINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('rcWindow', wintypes.RECT),
        ('rcClient', wintypes.RECT),
        ('dwStyle', wintypes.DWORD),
        ('dwExStyle', wintypes.DWORD),
        ('dwWindowStatus', wintypes.DWORD),
        ('cxWindowBorders', wintypes.UINT),
        ('cyWindowBorders', wintypes.UINT),
        ('atomWindowType', wintypes.ATOM),
        ('wCreatorVersion', wintypes.WORD),
    ]

def get_window_info(title):
    hwnd = ctypes.windll.user32.FindWindowA(0, ctypes.c_char_p(title.encode()))
    win_info = WINDOWINFO()
    rect = wintypes.RECT()
    ctypes.windll.user32.GetWindowInfo(hwnd, ctypes.byref(win_info))
    ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
    return (win_info.rcClient.left, win_info.rcClient.top, rect.right, rect.bottom)

class VecMem:
    def read_vec3_int(addr, pm):
        entry = []
        bytes = 0
        for i in range(0, 3):
            vol=pm.read_int(addr + bytes)
            bytes += 4
            entry.append(vol)
        return Vec3_int(entry[0], entry[1], entry[2])

    def read_vec3_float(addr, pm):
        entry = []
        bytes = 0
        for i in range(0, 3):
            vol=pm.read_float(addr + bytes)
            bytes += 4
            entry.append(vol)
        return Vec3(entry[0], entry[1], entry[2])

    def read_vec2_int(addr, pm):
        entry = []
        bytes = 0
        for i in range(0, 2):
            vol=pm.read_int(addr + bytes)
            bytes += 4
            entry.append(vol)
        return Vec3_int(entry[0], entry[1])

    def read_vec2_float(addr, pm):
        entry = []
        bytes = 0
        for i in range(0, 2):
            vol=pm.read_float(addr + bytes)
            bytes += 4
            entry.append(vol)
        return Vec3(entry[0], entry[1])
    
    def read_4x4(addr, pm):
        entry = []
        bytes = 0
        for i in range(0, 16):
            vol=pm.read_float(addr + bytes)
            bytes += 4
            entry.append(vol)
        return entry
    
def reverse_int(m):
    x = 0
    n = m
    if m < 0 :
      n *= -1
    while n > 0 :
        x *= 10
        x += n % 10
        n /= 10
    if m < 0:
      #concatenate a - sign at the end
      return x + "-"
    return x

def is_window_active(window_title):
    window_handle = win32gui.FindWindow(None, window_title)
    if window_handle == 0:
        return False
    active_handle = win32gui.GetForegroundWindow()
    return window_handle == active_handle

def worldToScreen(matrix : Array, pos : Vec3, algo : int):
    clip = Vec3
    ndc = Vec2
    if algo == 0:
        clip.z = pos.x * matrix[3] + pos.y * matrix[7] + pos.z * matrix[11] + matrix[15]
        clip.x = pos.x * matrix[0] + pos.y * matrix[4] + pos.z * matrix[8] + matrix[12]
        clip.y = pos.x * matrix[1] + pos.y * matrix[5] + pos.z * matrix[9] + matrix[13]
    elif algo == 1:
        clip.z = pos.x * matrix[12] + pos.y * matrix[13] + pos.z * matrix[14] + matrix[15]
        clip.x = pos.x * matrix[0] + pos.y * matrix[1] + pos.z * matrix[2] + matrix[3]
        clip.y = pos.x * matrix[4] + pos.y * matrix[5] + pos.z * matrix[6] + matrix[7]

    if clip.z < 0.2:
       return None
    ndc.x = clip.x / clip.z
    ndc.y = clip.y / clip.z
    x = (GetScreenWidth() / 2 * ndc.x) + (ndc.x + GetScreenWidth() / 2)
    y = -(GetScreenHeight() / 2 * ndc.y) + (ndc.y + GetScreenHeight() / 2)
    return  [x, y]