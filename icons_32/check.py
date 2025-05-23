import framebuf

def __get_icon():
  bitmap_data = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x70, 
  0x00, 0x00, 0x00, 0xF8, 0x00, 0x00, 0x00, 0xFC, 0x00, 0x00, 0x00, 0xFE, 
  0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x80, 0x7F, 0x00, 0x00, 0xC0, 0x3F, 
  0x00, 0x00, 0xE0, 0x0F, 0x00, 0x00, 0xF0, 0x07, 0x0F, 0x00, 0xFC, 0x03, 
  0x1F, 0x00, 0xFE, 0x01, 0x3F, 0x00, 0xFF, 0x00, 0x7F, 0x80, 0x7F, 0x00, 
  0xFF, 0xC1, 0x3F, 0x00, 0xFC, 0xE1, 0x1F, 0x00, 0xF8, 0xF7, 0x0F, 0x00, 
  0xF0, 0xFF, 0x07, 0x00, 0xE0, 0xFF, 0x03, 0x00, 0xC0, 0xFF, 0x01, 0x00, 
  0x80, 0xFF, 0x00, 0x00, 0x00, 0x7F, 0x00, 0x00, 0x00, 0x3E, 0x00, 0x00, 
  0x00, 0x1C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
  return framebuf.FrameBuffer(bitmap_data, 32, 32, framebuf.MONO_HMSB)