import requests, win32gui, win32ui, win32con, pyautogui, keyboard, time
from PIL import ImageGrab
from pynput.mouse import Listener, Button
from pymem import Pymem
from pymem import *
from pymem.process import *
from helper import *
from pyray import *
from PIL import Image
import configparser
exc_name = 'csgo.exe'
exc_title = 'Counter-Strike: Global Offensive - Direct3D 9'
pm=Pymem(exc_name)
clientModule=module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
engineModule=module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll

config = configparser.ConfigParser()
config.read('config.ini')
retry_count = int(config.get('settings', 'retry_count'))
mem_offset_hexInt = int(config.get('settings', 'mem_offset_hexInt'))
starting_memory = int(config.get('memory', 'starting_memory'))

class pub:
    scan_geom_1 = None # Inp
    scan_geom_2 = None # Inp
    def get_number_offset(arg1, arg2):
        if arg1 > arg2:
            return arg1 - arg2
        else:
            return arg2 - arg1

class Offsets:
    def update():
        try:
            print("Downloading Offsets...")
            # Credits to https://github.com/frk1/hazedumper
            haze = requests.get(
                "https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json"
            ).json()

            [setattr(Offsets, k, v) for k, v in haze["signatures"].items()]
            [setattr(Offsets, k, v) for k, v in haze["netvars"].items()]
        except:
            sys.exit("Unable to fetch Hazedumper's Offsets")
class ui:
    def init():
        win = get_window_info(exc_title)
        set_trace_log_level(5)
        set_target_fps(0)
        set_config_flags(ConfigFlags.FLAG_WINDOW_UNDECORATED)
        set_config_flags(ConfigFlags.FLAG_WINDOW_MOUSE_PASSTHROUGH)
        set_config_flags(ConfigFlags.FLAG_WINDOW_TRANSPARENT)
        set_config_flags(ConfigFlags.FLAG_WINDOW_TOPMOST)
        init_window(win[2], win[3], "")
        set_window_position(win[0], win[1])

    def update_window_pos(exec_title):
        win = get_window_info(exec_title)
        set_window_position(win[0], win[1])

    def screenshot():
        while True:
            try:
                w = 1920 # set this
                h = 1080 # set this
                bmpfilenamename = "out.bmp" #set this       
                hwnd = win32gui.GetDesktopWindow()
                wDC = win32gui.GetWindowDC(hwnd)
                dcObj=win32ui.CreateDCFromHandle(wDC)
                cDC=dcObj.CreateCompatibleDC()
                dataBitMap = win32ui.CreateBitmap()
                dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
                cDC.SelectObject(dataBitMap)
                cDC.BitBlt((0,0),(w, h) , dcObj, (0,0), win32con.SRCCOPY)
                dataBitMap.SaveBitmapFile(cDC, bmpfilenamename)     
                # Free Resources
                dcObj.DeleteDC()
                cDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, wDC)
                win32gui.DeleteObject(dataBitMap.GetHandle())
                break
            except:
                pass

    def crop_screenshot(loc, geom1, geom2):
        image = Image.open(loc)
        # Crop the image based on the coordinates of the control clicks
        left = min(geom1[0], geom2[0])
        top = min(geom1[1], geom2[1])
        right = max(geom1[0], geom2[0])
        bottom = max(geom1[1], geom2[1])
        cropped_image = image.crop((left, top, right, bottom))
        image.close()
        return cropped_image

class device:
    def get_pos():
        def on_click(x, y, button, pressed):
            if pressed:
                if button == Button.left and keyboard.is_pressed('ctrl'):
                    current_mouse_cursor_pos = device.get_mouse_loc()
                    pub.scan_geom_1 = current_mouse_cursor_pos
                    print(f"Geom1: {pub.scan_geom_1}")

                if button == Button.right and keyboard.is_pressed('ctrl'):
                    current_mouse_cursor_pos = device.get_mouse_loc()
                    pub.scan_geom_2 = current_mouse_cursor_pos
                    print(f"Geom2: {pub.scan_geom_2}")

                if pub.scan_geom_1 != None and pub.scan_geom_2 != None:
                    listener.stop()

        with Listener(on_click=on_click) as listener:
            listener.join()
    def get_mouse_loc():
        return pyautogui.position()

# !CSGO RELATED STUFF TO GET PROPER CORDS, USUALLY REPLACE WITH YOUR OWN CODE OR PROVIDE MANUAL CORDS! #
# !CSGO RELATED STUFF TO GET PROPER CORDS, USUALLY REPLACE WITH YOUR OWN CODE OR PROVIDE MANUAL CORDS! #
# !CSGO RELATED STUFF TO GET PROPER CORDS, USUALLY REPLACE WITH YOUR OWN CODE OR PROVIDE MANUAL CORDS! #
# !CSGO RELATED STUFF TO GET PROPER CORDS, USUALLY REPLACE WITH YOUR OWN CODE OR PROVIDE MANUAL CORDS! #
class localPlayer:
    def __init__(self, mem : any, addr : any, module : any):
        self.addr = addr
        self.mem = mem
        self.module = module
    def flags(self):
        self.health = pm.read_int(self.addr + Offsets.m_iHealth)
        self.armor = pm.read_int(self.addr + Offsets.m_ArmorValue)
        self.team = pm.read_int(self.addr + Offsets.m_iTeamNum)

class entity:
    def __init__(self, mem, addr, module):
        self.wts = None # To Be Filled
        self.addr = addr
        self.mem = mem
        self.module = module
        self.health = pm.read_int(self.addr + Offsets.m_iHealth)
        self.armor = pm.read_int(self.addr + Offsets.m_ArmorValue)
        self.team = pm.read_int(self.addr + Offsets.m_iTeamNum)
        self.bone_base = pm.read_int(self.addr + Offsets.m_dwBoneMatrix)
        self.bDormant = pm.read_bool(self.addr + Offsets.m_bDormant)
    def bone_pos(self, bone_id):
        return Vec3(
            pm.read_float(self.bone_base + 0x30 * bone_id + 0x0C),
            pm.read_float(self.bone_base + 0x30 * bone_id + 0x1C),
            pm.read_float(self.bone_base + 0x30 * bone_id + 0x2C),
        )

def scan_for_green_pixels(image_path):
    try:
        # Open the image file
        image = Image.open(image_path)

        # Check if the image mode is RGB
        if image.mode != 'RGB':
            raise ValueError("Image must be in RGB mode")

        # Scan each pixel to find green pixels with full RGB value of 255
        for x in range(image.width):
            for y in range(image.height):
                r, g, b = image.getpixel((x, y))
                if g > 200 and r < 65 and b < 65:  # Green pixel with RGB value (0, 255, 0)
                    return True

        # If no green pixel with full RGB value of 255 is found, return False
        return False

    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("Started")
    mem_offset = 0
    add_offset = True
    retry = 0
    while not window_should_close():
        clear_background(BLANK)
        ui.update_window_pos(exc_title)
        begin_drawing()


        viewMatrix_starting_memory_addr = int(starting_memory)
        viewMemAddr = hex(viewMatrix_starting_memory_addr + mem_offset)
        viewMatrix = VecMem.read_4x4(addr=clientModule + viewMatrix_starting_memory_addr + mem_offset, pm=pm)


        # !CSGO RELATED STUFF TO GET PROPER CORDS, USUALLY REPLACE WITH YOUR OWN CODE OR PROVIDE MANUAL CORDS TO WORLD_TO_SCREEN! #
        local_addr = pm.read_int(clientModule + Offsets.dwLocalPlayer)
        if local_addr != None and local_addr != 0:
            local_class = entity(mem=pm, addr=local_addr, module=clientModule)
            for i in range(1, 32):
                entity_addr = pm.read_int(clientModule + Offsets.dwEntityList + i * 0x10)
                if entity_addr:
                    entity_class = entity(mem=pm, addr=entity_addr, module=clientModule)
                    if not entity_class.bDormant and entity_class.health > 0:
                        try:
                            chestpos = worldToScreen(viewMatrix, entity_class.bone_pos(bone_id=8), 1)
                            if chestpos != None:
                                draw_line_ex(Vector2(0, 0,), Vector2(int(chestpos[0]), int(chestpos[1])), 3, GREEN)
                        except:
                            pass
        SET="Assigned";WAIT="Waiting For Assignment"
        draw_text(viewMemAddr, 0, 0, 23, RED)
        # SCAN FOR CORRECT ARIAL #
        if add_offset == True:
            ui.screenshot()
            screenshot='out.bmp'
            if pub.scan_geom_1 is not None and pub.scan_geom_2 is not None:
                # Crop the image based on the control click positions
                cropped_image = ui.crop_screenshot(screenshot, pub.scan_geom_1, pub.scan_geom_2)
                cropped_image.save("out_resized.bmp")
                cropped_image.close()
            result = scan_for_green_pixels("out_resized.bmp")
            if result and add_offset:
                print(f"Possible ViewMatrix Found At: {viewMemAddr}")
                add_offset = False
        if not add_offset:
            if keyboard.is_pressed('alt') and keyboard.is_pressed('q'):
                add_offset = True
            if add_offset == True:
                print(mem_offset)
                retry=0
                mem_offset += mem_offset_hexInt
        else:
            if add_offset == True:
                print(mem_offset)
                if retry < retry_count:
                    retry+=1
                else:
                    mem_offset += mem_offset_hexInt
                    retry=0
        end_drawing()
if __name__=="__main__":
    Offsets.update()
    print("Done Downloading Offsets.")
    device.get_pos()
    ui.init()
    main()
