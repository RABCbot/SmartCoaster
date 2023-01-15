from machine import Pin, ADC, PWM, Timer
import time

PIN_ADC = 27
PIN_RED = 13
PIN_GREEN = 12
PIN_BLUE = 11
PIN_BUZZER = 16
BUZZER_DUTY = 600
BUZZER_FREQ = 2500
ADC_LEVEL = 10000 # Analog threshold, how much light change to trigger detection

TIMER_TICK = 2000 # In Msecs
DRINK_TICKS = 900 # In terms of timer tick period (30 minutes * 60 secs/min div 1 msec = 900)

class SmartCoaster:
    def __init__(self):
      self.value = 0
      self.ticks = 0
      self.double_ticks = 0
      self.blink = False
      self.init_pins()
      self.steady_green()
        
    def callback(self, timer):
      current_value = self.adc.read_u16()
      self.ticks = self.ticks + 1
      print(abs(current_value - self.value), self.ticks)

      # if not enough light change, assumes coaster is not used, not drinking
      if (
        abs(current_value - self.value) < ADC_LEVEL
        and DRINK_TICKS < self.ticks
        and self.ticks <= 2 * DRINK_TICKS 
        ):
        self.flash_blue()

      # Not enough light change for too long
      elif (
        abs(current_value - self.value) < ADC_LEVEL
        and self.ticks > 2 * DRINK_TICKS 
        ):
        self.steady_red()

      # Enough light change, assume drinking
      elif abs(current_value - self.value) >= ADC_LEVEL:
        self.steady_green()

      self.value = current_value
    
    def __call__(self, timer):
      self.callback(timer)

    def init_pins(self):
      self.adc = ADC(Pin(PIN_ADC, mode=Pin.IN))
      self.red = Pin(PIN_RED, mode=Pin.OUT)
      self.green = Pin(PIN_GREEN, mode=Pin.OUT)
      self.blue = Pin(PIN_BLUE, mode=Pin.OUT)
      self.buzzer = PWM(Pin(PIN_BUZZER))
      self.buzzer.freq(BUZZER_FREQ)
      self.buzzer.duty_u16(0)

    def steady_green(self):
      print(f"Got water {self.double_ticks}")
      self.ticks = 0
      self.buzzer.duty_u16(0)
      self.red.off()
      self.green.off()
      self.blue.off()
      self.blink = True
      time.sleep(1)
      self.green.on()
      self.double_ticks = self.double_ticks + 1

    def flash_blue(self):
      print("Need to drink water")
      self.green.off()
      if self.blink:
        self.blink = False
        self.blue.on()
        self.buzzer.duty_u16(BUZZER_DUTY)
      else:
        self.blink = True
        self.blue.off()
        self.buzzer.duty_u16(0)

    def steady_red(self):
      print("Need to drink more water")
      self.green.off()
      self.blue.off()
      self.red.on()
      self.buzzer.duty_u16(BUZZER_DUTY)
      self.blink = False

coaster = SmartCoaster()
Timer().init(mode=Timer.PERIODIC, period=TIMER_TICK, callback=coaster)

