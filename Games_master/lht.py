
# 在这里写上你的代码 :-)
# ESP8266 iot humdity temperature sensor with LED switch and pump switch , MQTT and  NTP time.
# press LEFT button to exit the program.

import machine
import network
import time
from time import sleep, sleep_ms, ticks_ms, ticks_diff
from machine import Pin, I2C

import os
import sys
import ssd1306

from struct import unpack as unp
"""
led = Pin(14, Pin.OUT)
pump = Pin(13, Pin.OUT)
btnLeft = Pin(12, Pin.IN, Pin.PULL_UP)
btnDown = Pin(2, Pin.IN, Pin.PULL_UP)
btnA = Pin(0, Pin.IN, Pin.PULL_UP)
buzzer = Pin(15, Pin.OUT)
"""
led = Pin(27, Pin.OUT)
pump = Pin(28, Pin.OUT)
btnLeft = Pin(13, Pin.IN, Pin.PULL_UP)
btnDown = Pin(18, Pin.IN, Pin.PULL_UP)
btnA = Pin(19, Pin.IN, Pin.PULL_UP)
buzzer = Pin(25, Pin.OUT)



i2c = I2C(-1, Pin(5), Pin(4))   # SCL, SDA
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# turn off everything
led.on()
pump.on()

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


reported_err = 0
measure_period_ms = const(20000)
display_period_ms = const(1000)
last_measure_ms = 0
last_display_ms = 0

ledOn = False
pumpOn = False
h = 72.5
h0 = 1.0
t = 28.3
t0 = 1.0
lux = 1000
lux0 = 0



# SHT20 default address
SHT20_I2CADDR = 64

# SHT20 Command
TRI_T_MEASURE_NO_HOLD = b'\xf3'
TRI_RH_MEASURE_NO_HOLD = b'\xf5'
READ_USER_REG = b'\xe7'
WRITE_USER_REG = b'\xe6'
SOFT_RESET = b'\xfe'

# SHT20 class to read temperature and humidity sensors
class SHT20(object):

    def __init__(self, scl_pin=5, sda_pin=4, clk_freq=100000):
        self._address = SHT20_I2CADDR

        pin_c = Pin(scl_pin)
        pin_d = Pin(sda_pin)
        self._bus = I2C(scl=pin_c, sda=pin_d, freq=clk_freq)

    def get_temperature(self):
        self._bus.writeto(self._address, TRI_T_MEASURE_NO_HOLD)
        sleep_ms(150)
        origin_data = self._bus.readfrom(self._address, 2)
        origin_value = unp('>h', origin_data)[0]
        value = -46.85 + 175.72 * (origin_value / 65536)
        return value

    def get_relative_humidity(self):
        self._bus.writeto(self._address, TRI_RH_MEASURE_NO_HOLD)
        sleep_ms(150)
        origin_data = self._bus.readfrom(self._address, 2)
        origin_value = unp('>H', origin_data)[0]
        value = -6 + 125 * (origin_value / 65536)
        return value

# BH1750fvi light meter sensor
OP_SINGLE_HRES1 = 0x20
OP_SINGLE_HRES2 = 0x21
OP_SINGLE_LRES = 0x23

DELAY_HMODE = 180  # 180ms in H-mode
DELAY_LMODE = 24  # 24ms in L-mode


def bh1750fvi (i2c, mode=OP_SINGLE_HRES1, i2c_addr=0x23):
    """
        Performs a single sampling. returns the result in lux
    """

    i2c.writeto(i2c_addr, b"\x00")  # make sure device is in a clean state
    i2c.writeto(i2c_addr, b"\x01")  # power up
    i2c.writeto(i2c_addr, bytes([mode]))  # set measurement mode

    time.sleep_ms(DELAY_LMODE if mode == OP_SINGLE_LRES else DELAY_HMODE)

    raw = i2c.readfrom(i2c_addr, 2)
    i2c.writeto(i2c_addr, b"\x00")  # power down again

    # we must divide the end result by 1.2 to get the lux
    return ((raw[0] << 24) | (raw[1] << 16)) // 78642


def fill_zero(n):
    if n < 10:
        return '0' + str(n)
    else:
        return str(n)

def fill_blank(n):
    if n<10:
        return ' ' + str(n)
    else:
        return str(n)




# WiFi connection information
WIFI_SSID = 'makerfabs'
WIFI_PASSWORD = '20160704'

# turn off the WiFi Access Point
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

# connect the device to the WiFi network
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)

# wait until the device is connected to the WiFi network
MAX_ATTEMPTS = 20
attempt_count = 0
while not wifi.isconnected() and attempt_count < MAX_ATTEMPTS:
    attempt_count += 1
    time.sleep(1)

if attempt_count == MAX_ATTEMPTS:
    print('could not connect to the WiFi network')
    sys.exit()


# set time using NTP server on the internet

import ntptime    #NTP-time (from pool.ntp.org)
import utime
ntptime.settime()
tm = utime.localtime(utime.mktime(utime.localtime()) + 8 * 3600)
tm=tm[0:3] + (0,) + tm[3:6] + (0,)
rtc = machine.RTC()
rtc.datetime(tm)



sht_sensor = SHT20()

while not pressed (btnLeft, True):

  if pressed(btnDown,True):
    #LED buttun pressed and released
    if ledOn :
      # if led is previously ON, now turn it off by outputing High voltage
      led.on()
      msg = "OFF"
      ledOn = False
    else :
      # if led is previously OFF, now turn it on by outputing Low voltage
      led.off()
      msg = "ON"
      ledOn = True

  # pump switch pressed
  if pressed(btnA,True):
  #LED button  pressed and released
    if pumpOn :
      # if pump was ON, turn it off by outputing High voltage
      pump.on()
      msg = "OFF"
      pumpOn = False
    else :
      # if pump was  OFF, now turn it on by outputing Low voltage
      pump.off()
      msg = "ON"
      pumpOn = True



  if ticks_diff(ticks_ms(), last_measure_ms ) >=  measure_period_ms :
    # time to take measurements
    lux = bh1750fvi(i2c)
    t = sht_sensor.get_temperature()
    h = sht_sensor.get_relative_humidity()

    if lux != lux0 :
        print('Publish:  lux = {}'.format(lux))
        lux0 = lux

    if h != h0 :
        print('Publish:  humidity = {}'.format(h))
        h0 = h

    msg = (b'{0:3.1f}'.format(t))
    if t != t0 :
        print('Publish:  airtemp = {}'.format(t))
        t0 = t

    last_measure_ms = ticks_ms()

  if ticks_diff(ticks_ms(), last_display_ms) >= display_period_ms :
    # time to display
    display.fill(0)
    Y,M,D,H,m,S,ms,W=utime.localtime()
    timetext ='%s-%s %s:%s:%s' % (fill_zero(M),fill_zero(D),fill_zero(H),fill_zero(m),fill_zero(S))
    display.text(timetext,0,0)
    display.text('Lux = {}'.format(lux), 0, 15)
    display.text(b'{0:3.1f} %'.format(h), 0, 30)
    display.text(b'{0:3.1f} C'.format(t), 64, 30)
    if ledOn :
        display.text("LED ON", 0, 48)
    else :
        display.text("LED OFF", 0, 48)

    if pumpOn :
        display.text("PUMP ON", 64, 48)
    else :
        display.text("PUMP OFF", 64, 48)

    display.show()
    last_display_ms = time.ticks_ms()





