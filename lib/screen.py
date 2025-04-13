'''
Screen Module
'''
from machine import SPI, Pin
import framebuf
from gdeh0213b73 import EPD, ROTATION_0, ROTATION_90, ROTATION_180, ROTATION_270
import coding, use_codecs

FNT_ASC16 = '/fonts/ASC16' # 8x16 16bytes
__UNI2GB2312 = '/fonts/unicode2gb2312.codec'
__SCREEN = None

def __get_gb2312_bytes(text):
    return use_codecs.convert_u8_gb2312(
        text.encode("utf8"),
        __UNI2GB2312,
    )

def __get_pure_ascii_bytes(text):
    byts = bytearray()
    for char in text.encode("utf8"):
        if char <= 126 and char >= 32: #32~126, all 94 character
            byts.append(char - 32)
        else:
            byts.append(0x0)
    return byts
    

def init(rotation=ROTATION_90):
    '''init built-in epaper screen'''
    global __SCREEN
    espi = SPI(2, baudrate=20000000, sck=Pin(18), mosi=Pin(23)
               , polarity=0, phase=0, firstbit=SPI.MSB)
    rst = Pin(16, Pin.OUT, value=1) # default: 1
    dc = Pin(17, Pin.OUT, value=1) # default: 1,
    cs = Pin(5, Pin.OUT, value=1) # default: 1
    busy = Pin(4, Pin.IN, value=0)
    __SCREEN = EPD(espi, cs, dc, rst, busy, rotation=rotation, invert=True)
    __SCREEN.fill(0) # clear

def get_framebuf():
    return __SCREEN

def update_fast():
    __SCREEN.hard_reset()
    __SCREEN.update_fast()
    __SCREEN.deep_sleep()
def update():
    __SCREEN.hard_reset()
    __SCREEN.update()
    __SCREEN.deep_sleep()

def clear():
    __SCREEN.fill(0)

def draw_text(text,x,y,scale=1):
    byts = text.encode("utf8")
    p = 0
    pf = open(FNT_ASC16, "rb")
    while x < __SCREEN.width and p < len(byts):
        char = byts[p]
        pf.seek(char * 16)
        data_buf = memoryview(bytearray(pf.read(16)))
        fb_char = framebuf.FrameBuffer(data_buf, 8, 16, framebuf.MONO_HLSB)
        draw_fb(fb_char,x,y,8,16,scale)
        x += int(8 * scale)
        p += 1
    pf.close()

def draw_fb(fb_icon,x_icon,y_icon,width=None,height=None,scale=1):
    if scale != 1 and scale > 0 and width != None and height != None:
        new_width = int(width * scale)
        new_height = int(height * scale)
        new_buffer = bytearray(int((width * scale) * (height * scale) / 8))
        fb_scaled = framebuf.FrameBuffer(new_buffer, new_width, new_height, framebuf.MONO_HMSB)

        for y in range(new_height):
            for x in range(new_width):
                src_x = int(x / scale)
                src_y = int(y / scale)
                pixel = fb_icon.pixel(src_x, src_y)
                if pixel:
                    fb_scaled.pixel(x, y, pixel)

    else:
        fb_scaled = fb_icon
    __SCREEN.blit(fb_scaled, x_icon, y_icon)