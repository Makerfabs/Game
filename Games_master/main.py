
import os
import sys
import gc
from machine import Pin, I2C
from utime import sleep_ms, ticks_ms, ticks_diff
module_name = ""

def pressed (btn, wait_release=False) :
  if not btn.value():
    sleep_ms (30)
    if btn.value():
      return False
    #wait for key release
    while wait_release and not btn.value() :
      sleep_ms (5)
    return True
  return False
def do_menu () :
  global module_name
  """
  btnLeft = Pin(12, Pin.IN, Pin.PULL_UP)
  btnRight = Pin(13, Pin.IN, Pin.PULL_UP)
  btnUp = Pin(14, Pin.IN, Pin.PULL_UP)
  btnDown = Pin(2, Pin.IN, Pin.PULL_UP)
  """
  btnLeft = Pin(13, Pin.IN, Pin.PULL_UP)
  btnRight = Pin(14, Pin.IN, Pin.PULL_UP)
  btnUp = Pin(15, Pin.IN, Pin.PULL_UP)
  btnDown = Pin(18, Pin.IN, Pin.PULL_UP)
  import ssd1306

  # configure oled display I2C SSD1306
  i2c = I2C(-1, Pin(5), Pin(4))   # SCL, SDA
  display = ssd1306.SSD1306_I2C(128, 64, i2c)


  SKIP_NAMES = ("boot", "main", "menu")


  files = [item[0] for item in os.ilistdir(".") if item[1] == 0x8000]
        # print("Files: %r" % files)

  module_names = [
      filename.rsplit(".", 1)[0]
      for filename in files
      if (filename.endswith(".py") or  filename.endswith(".mpy") ) and not filename.startswith("_")
  ]
  module_names = [module_name for module_name in module_names if not module_name in SKIP_NAMES]
  module_names.sort()
  tot_file = len(module_names)
  tot_rows = const(5)
  screen_pos = 0
  file_pos = 0

  launched = False
  while not launched :
    gc.collect()
    display.fill(0)
    display.text(sys.platform + " " + str(gc.mem_free()), 5, 0, 1)
    i = 0
    for j in range (file_pos, min(file_pos+tot_rows, tot_file)) :
      current_row = 12 + 10 *i
      if i == screen_pos :
        display.fill_rect(5, current_row, 118, 10, 1)
        display.text(str(j) + " " + module_names[j], 5, current_row, 0)
      else:
        display.fill_rect(5, current_row, 118, 10, 0)
        display.text(str(j) + " " + module_names[j], 5, current_row, 1)
      i+=1

    if pressed(btnUp):
      if screen_pos > 0 :
        screen_pos -= 1
      else :
          if file_pos > 0 :
            file_pos = max (0, file_pos - tot_rows)
            screen_pos=tot_rows-1

    if pressed(btnDown):
      if screen_pos < min(tot_file - file_pos - 1, tot_rows -1) :
        screen_pos = min(tot_file-1, screen_pos + 1)
      else :
        if file_pos + tot_rows < tot_file :
          file_pos = min (tot_file, file_pos + tot_rows)
          screen_pos=0

    if pressed(btnRight):
      display.fill(0)
      display.text("launching " , 5, 20, 1)
      display.text(module_names[file_pos + screen_pos], 5, 40, 1)
      display.show()
      sleep_ms(1000)
      module_name = module_names[file_pos + screen_pos]
      return True

    if pressed(btnLeft):
      launched = True
      display.fill(0)
      display.text("exited ", 5, 24, 1)
      display.show()
      return False
    display.show()

go_on = True
while go_on :
  go_on = do_menu()
  if go_on :
    gc.collect()
    module = __import__(module_name)
    del sys.modules[module_name]
    gc.collect()



