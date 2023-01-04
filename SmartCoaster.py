from machine import Pin, ADC, Timer
import time

PIN_ADC = 27
PIN_RED = 11
PIN_GREEN = 12
PIN_BLUE = 13
ADC_LEVEL = 1000 # Analog threshold
TIMER_PERIOD = 2500 # In Msecs
DRINK_TICKS = 240  # In terms of timer period (10 minutes * 60 secs/min div 2.500 msec = 240)

class SmartCoaster:
    def __init__(self):
      self.adc = ADC(Pin(PIN_ADC, mode=Pin.IN))
      self.red = Pin(PIN_RED, mode=Pin.OUT)
      self.green = Pin(PIN_GREEN, mode=Pin.OUT)
      self.blue = Pin(PIN_BLUE, mode=Pin.OUT)
      self.value = 0
      self.ticks = 0
        
    def callback(self, timer):
      current_value = self.adc.read_u16()
      self.ticks = self.ticks + 1
      print(abs(current_value - self.value), self.ticks)
      # if light level does not changes enough, assumes coaster is not used, not drinking
      if abs(current_value - self.value) < ADC_LEVEL and self.ticks > DRINK_TICKS:
        print(f"Need to drink water")
        self.red.off()
        self.green.off()
        if self.ticks > 2*DRINK_TICKS:
          self.blue.off()
        else:
          self.blue.on()
        self.red.on()

      elif abs(current_value - self.value) >= ADC_LEVEL:
        self.ticks = 0
        self.red.off()
        self.green.on()
        self.blue.off()

      self.value = current_value
    
    def __call__(self, timer):
      self.callback(timer)
        

coaster = SmartCoaster()
Timer().init(mode=Timer.PERIODIC, period=TIMER_PERIOD, callback=coaster)
