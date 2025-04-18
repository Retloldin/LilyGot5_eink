import framebuf

def __get_icon():
  bitmap_data = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
  0x06, 0x00, 0x00, 0x00, 0x0F, 0xC0, 0x07, 0x00, 0x3E, 0xFE, 0x7F, 0x00, 
  0xFC, 0xFF, 0xFF, 0x03, 0xF8, 0xFF, 0xFF, 0x07, 0xE0, 0xFF, 0xFF, 0x1F, 
  0xCC, 0x07, 0xC0, 0x3F, 0x9E, 0x0F, 0x00, 0x7E, 0x3F, 0x1F, 0x00, 0xFC, 
  0x1F, 0xFC, 0x0F, 0xF0, 0x0E, 0xF8, 0x3F, 0xE0, 0x00, 0xF3, 0xFF, 0x00, 
  0x80, 0xC7, 0xFF, 0x01, 0xC0, 0x8F, 0xFF, 0x03, 0xC0, 0x0F, 0xDF, 0x07, 
  0x80, 0x03, 0xBE, 0x03, 0x00, 0x00, 0x78, 0x00, 0x00, 0x80, 0xF1, 0x01, 
  0x00, 0xC0, 0xE7, 0x03, 0x00, 0xE0, 0xCF, 0x07, 0x00, 0xE0, 0x0F, 0x1F, 
  0x00, 0xE0, 0x0F, 0x3E, 0x00, 0xE0, 0x07, 0x7C, 0x00, 0x80, 0x03, 0xF0, 
  0x00, 0x00, 0x00, 0xE0, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
  return framebuf.FrameBuffer(bitmap_data, 32, 32, framebuf.MONO_HMSB)