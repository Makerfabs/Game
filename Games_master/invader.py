

# 在这里写上你的代码 :-)
# invader.py  I2C
#
# ESP8266 (node MCU D1 mini)  micropython
# by Billy Cheung  2019 08 31
#

#
# I2C OLED SSD1306
# GPIO4   D2---  SDA OLED
# GPIO5   D1---  SCL  OLED
#
# Speaker
# GPIO15  D8     Speaker
#
#buttons
# GPIO12  D6——   Left  
# GPIO13  D7——   Right     
# GPIO14  D5——   UP    
# GPIO2   D4——   Down    
# GPIO0   D3——   A

#
import gc
import sys
gc.collect()
print (gc.mem_free())
import network
import utime
from utime import sleep_ms,ticks_ms, ticks_us, ticks_diff
from machine import Pin, I2C, PWM, ADC
from math import sqrt
import ssd1306
from random import getrandbits, seed

"""
btnL = Pin(12, Pin.IN, Pin.PULL_UP)
btnR = Pin(13, Pin.IN, Pin.PULL_UP)
btnU = Pin(14, Pin.IN, Pin.PULL_UP)
btnD = Pin(2, Pin.IN, Pin.PULL_UP)
btnA = Pin(0, Pin.IN, Pin.PULL_UP)
buzzer = Pin(15, Pin.OUT)
"""
btnL = Pin(13, Pin.IN, Pin.PULL_UP)
btnR = Pin(14, Pin.IN, Pin.PULL_UP)
btnU = Pin(15, Pin.IN, Pin.PULL_UP)
btnD = Pin(18, Pin.IN, Pin.PULL_UP)
btnA = Pin(19, Pin.IN, Pin.PULL_UP)
buzzer = Pin(25, Pin.OUT)
# configure oled display I2C SSD1306
i2c = I2C(-1, Pin(5), Pin(4))   # SCL, SDA
display = ssd1306.SSD1306_I2C(128, 64, i2c)
# ESP8266 ADC A0 values 0-1023
#adc = ADC(32)
adc = ADC(Pin(32))

def pressed (btn, wait_release=False) :
  if not btn.value():

    if btn.value():
      return False
    #wait for key release
    while wait_release and not btn.value() :
      sleep_ms (5)
    return True
  return False

#---buttons


#buzzer = Pin(15, Pin.OUT)
buzzer = Pin(25, Pin.OUT)
#adc = ADC(0)
adc = ADC(Pin(32))

def getPaddle () :
  return adc.read()




tones = {
    'c4': 262,
    'd4': 294,
    'e4': 330,
    'f4': 349,
    'f#4': 370,
    'g4': 392,
    'g#4': 415,
    'a4': 440,
    "a#4": 466,
    'b4': 494,
    'c5': 523,
    'c#5': 554,
    'd5': 587,
    'd#5': 622,
    'e5': 659,
    'f5': 698,
    'f#5': 740,
    'g5': 784,
    'g#5': 831,
    'a5': 880,
    'b5': 988,
    'c6': 1047,
    'c#6': 1109,
    'd6': 1175,
    ' ': 0
}


def playTone(tone, tone_duration, rest_duration=0):
  beeper = PWM(buzzer, freq=tones[tone], duty=512)
  utime.sleep_ms(tone_duration)
  beeper.deinit()
  utime.sleep_ms(rest_duration)

def playSound(freq, tone_duration, rest_duration=0):
  beeper = PWM(buzzer, freq, duty=512)
  utime.sleep_ms(tone_duration)
  beeper.deinit()
  utime.sleep_ms(rest_duration)



frameRate = 30
screenW = const(128)
screenH = const(64)
xMargin = const (5)
yMargin = const(10)
screenL = const (5)
screenR = const(117)
screenT = const (10)
screenB = const (58)
dx = 5
vc = 3
gunW= const(5)
gunH = const (5)
invaderSize = const(4)
invaders_rows = const(5)
invaders_per_row = const(11)



class Rect (object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.x2 = x + w - 1
        self.y2 = y + h - 1
    def move_ip (self, vx, vy) :
        self.x = self.x + vx
        self.y = self.y + vy
        self.x2 = self.x2 + vx
        self.y2 = self.y2 + vy

    def colliderect (self, rect1) :
      if (self.x2 >= rect1.x and
        self.x <= rect1.x2 and
        self.y2 >= rect1.y and
        self.y <= rect1.y2) :
        return True
      else:
        return False


def setUpInvaders ():
    y = yMargin
    while y < yMargin + (invaderSize+2) * invaders_rows :
      x = xMargin
      while x < xMargin + (invaderSize+2) * invaders_per_row :
        invaders.append(Rect(x,y,invaderSize, invaderSize))
        x = x + invaderSize + 2
      y = y + invaderSize + 2

def drawSpaceships (posture) :
  if posture :
    for i in spaceships :
      display.fill_rect(i.x+2, i.y, 5 , 3, 1)
      display.fill_rect(i.x, i.y+1, 9, 1, 1)
      display.fill_rect(i.x+1, i.y+1, 2, 1, 0)
  else :
    for i in spaceships :
      display.fill_rect(i.x+2, i.y, 5 , 3, 1)
      display.fill_rect(i.x, i.y+1, 9, 1, 1)
      display.fill_rect(i.x+5, i.y+1, 2, 1, 0)

def drawInvaders (posture) :
  if posture :
    for i in invaders :
        display.fill_rect(i.x, i.y, invaderSize , invaderSize, 1)
        display.fill_rect(i.x+1, i.y+2, invaderSize-2, invaderSize-2, 0)
  else :
      for i in invaders :
        display.fill_rect(i.x, i.y, invaderSize , invaderSize, 1)
        display.fill_rect(i.x+1, i.y, invaderSize-2, invaderSize-2, 0)
def drawGun () :
  display.fill_rect(gun.x+2, gun.y, 1, 2,1)
  display.fill_rect(gun.x, gun.y+2, gunW, 3,1)

def drawBullets () :
  for b in bullets:
    display.fill_rect(b.x, b.y, 1,3,1)

def drawAbullets () :
  for b in aBullets:
    display.fill_rect(b.x, b.y, 1,3,1)

def drawScore () :
  display.text('S:{}'.format (score), 0,0,1)
  display.text('L:{}'.format (level), 50,0,1)
  for i in range (0, life) :
    display.fill_rect(92 + (gunW+2)*i, 0, 1, 2,1)
    display.fill_rect(90 + (gunW+2)*i, 2, gunW, 3,1)

seed(ticks_us())

exitGame = False

while not exitGame:
  gameOver = False
  usePaddle = False
  demo = False
  life = 3
  display.fill(0)
  display.text('Invaders', 5, 0, 1)
  display.text('A = Button', 5, 20, 1)
  display.text('U = Paddle', 5,30,  1)
  display.text('D = Demo', 5, 40,  1)
  display.text('L = Exit', 5, 50,  1)
  display.show()

  #menu screen
  while True:

    if pressed(btnL,True) :
      gameOver = True
      exitGame = True
      break
    elif pressed(btnA,True) :
      usePaddle = False
      break
    elif pressed(btnU,True) :
      usePaddle = True
      break
    elif pressed(btnD,True) :
      demo = True
      usePddle = False
      wait_for_keys=False
      display.fill(0)
      display.text('DEMO', 5, 0, 1)
      display.text('A or B to Stop', 5, 30, 1)
      display.show()
      sleep_ms(2000)
      break

  #reset the game
  score = 0
  frameCount = 0
  level = 0
  loadLevel = True
  postureA = False
  postureS = False
  # Chance from 1 to 128
  aBulletChance = 1
  spaceshipChance = 1

  while not gameOver:

    timer = ticks_ms()
    lost = False
    frameCount = (frameCount + 1 ) % 120
    display.fill(0)

    if loadLevel :
      loadLevel = False
      spaceships = []
      invaders = []
      bullets = []
      aBullets = []
      setUpInvaders()
      gun = Rect(screenL+int((screenR-screenL)/2), screenB, gunW, gunH)
      aBulletChance = 50 + level * 10



    #generate space ships
    if getrandbits(8) < spaceshipChance and len(spaceships) < 1 :
      spaceships.append(Rect(0,9, 9, 9))

    if len(spaceships) :
      if not frameCount % 3 :
        postureS = not postureS
        # move spaceships once every 4 frames
        for i in spaceships:
          i.move_ip(2,0)
          if i.x >= screenR :
            spaceships.remove(i)
      if frameCount % 20 == 10 :
        playTone ('e5', 20)
      elif frameCount % 20 == 0 :
        playTone ('c5', 20)


    if not frameCount % 15 :
      postureA = not postureA
      # move Aliens once every 15 frames
      if postureA :
          playSound (80, 10)
      else:
          playSound (120, 10)
      for i in invaders:
        if i.x > screenR or i.x < screenL :
            dx = -dx
            for alien in invaders :
              alien.move_ip (0, invaderSize)
              if alien.y2 > gun.y :
                lost = True
                loadLevel = True
                playTone ('f4',300)
                playTone ('d4',100)
                playTone ('c5',100)
                break
            break

      for i in invaders :
        i.move_ip (dx, 0)


    # Fire
    if pressed(btnA) and len(bullets) < 2:
      bullets.append(Rect(gun.x+3, gun.y-1, 1, 3))
      playSound (200,5)
      playSound (300,5)
      playSound (400,5)
    # move gun
    if usePaddle :
      gun.x = int(getPaddle() / (1024/(screenR-screenL)))
      gun.x2 = gun.x+gunW-1
    else :
      if pressed(btnL) and gun.x - 3 > 0 :
        vc = -3
      elif pressed(btnR) and (gun.x + 3 + gunW ) < screenW :
        vc = 3
      else :
        vc = 0
      gun.move_ip (vc, 0)

    # move bullets

    for b in bullets:
      b.move_ip(0,-3)
      if b.y < 0 :
        bullets.remove(b)
      else :
        for i in invaders:
          if i.colliderect(b) :
            invaders.remove(i)
            bullets.remove(b)
            score +=1
            playTone ('c6',10)
            break
        for i in spaceships :
          if i.colliderect(b) :
            spaceships.remove(i)
            bullets.remove(b)
            score +=10
            playTone ('b4',30)
            playTone ('e5',10)
            playTone ('c4',30)
            break

    # Launch Alien bullets
    for i in invaders:
      if getrandbits(10) * len (invaders) < aBulletChance and len(aBullets) < 3 :
        aBullets.append(Rect(i.x+2, i.y, 1, 3))

    # move Alien bullets
    for b in aBullets:
      b.move_ip(0,3)
      if b.y > screenH  :
        aBullets.remove(b)
      elif b.colliderect(gun) :
        lost = True
        #print ('{} {} {} {} : {} {} {} {}'.format(b.x,b.y,b.x2,b.y2,gun.x,gun.y,gun.x2,gun.y2))
        aBullets.remove(b)
        playTone ('c5',30)
        playTone ('e4',30)
        playTone ('b4',30)
        break

    drawSpaceships (postureS)
    drawInvaders (postureA)
    drawGun()
    drawBullets()
    drawAbullets()
    drawScore()


    if len(invaders) == 0 :
      level += 1
      loadLevel = True
      playTone ('c4',100)
      playTone ('d4',100)
      playTone ('e4',100)
      playTone ('f4',100)
      playTone ('g4',100)

    if lost :
      lost = False;
      life -= 1
      if life < 0 :
        gameOver = True

    if gameOver :
      display.fill_rect (3, 15, 120,20,0)
      display.text ("GAME OVER", 5, 20, 1)
      playTone ('b4',300)
      playTone ('e4',100)
      playTone ('c4',100)
      display.show()

      sleep_ms(2000)

    display.show()

    timer_dif = int(1000/frameRate) - ticks_diff(ticks_ms(), timer)

    if timer_dif > 0 :
        sleep_ms(timer_dif)






