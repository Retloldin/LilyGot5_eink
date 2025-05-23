import framebuf

def __get_icon():
  bitmap_data = bytearray([0x00, 0x80, 0x01, 0x00, 0x00, 0xC0, 0x03, 0x00, 0x00, 0xE0, 0x07, 0x00, 
  0x00, 0xE0, 0x07, 0x00, 0x00, 0xE0, 0x07, 0x00, 0x00, 0xE0, 0x07, 0x00, 
  0x00, 0xE0, 0x07, 0x00, 0x00, 0xE0, 0x07, 0x00, 0x00, 0xE0, 0x07, 0x00, 
  0xC0, 0xE0, 0x87, 0x03, 0xE0, 0xE3, 0xC7, 0x07, 0xF0, 0xE7, 0xE7, 0x07, 
  0xE0, 0xEF, 0xF7, 0x07, 0xE0, 0xEF, 0xFF, 0x07, 0xC0, 0xFF, 0xFF, 0x03, 
  0x80, 0xFF, 0xFF, 0x01, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0xFE, 0x7F, 0x00, 
  0x00, 0xFC, 0x3F, 0x00, 0x00, 0xF8, 0x1F, 0x00, 0x00, 0xF0, 0x0F, 0x00, 
  0x00, 0xE0, 0x07, 0x00, 0x00, 0xC0, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
  0xF8, 0xFF, 0xFF, 0x1F, 0xFC, 0xFF, 0xFF, 0x3F, 0xFC, 0xFF, 0xFF, 0x3F, 
  0xF8, 0xFF, 0xFF, 0x1F, 0xF8, 0xFF, 0xFF, 0x0F])
  return framebuf.FrameBuffer(bitmap_data, 32, 32, framebuf.MONO_HMSB)