from machine import Pin, ADC, PWM, Timer
import time

PIN_ADC = 27
PIN_RED = 11
PIN_GREEN = 12
PIN_BLUE = 13
PIN_BUZZER = 16
BUZZER_DUTY = 600
BUZZER_FREQ = 2500
ADC_LEVEL = 10000 # Analog threshold, how much light change to trigger detection

TIMER_PERIOD = 2500 # In Msecs
DRINK_TICKS = 480  # In terms of timer period (20 minutes * 60 secs/min div 2.5 msec = 480)

class SmartCoaster:
    def __init__(self):
      self.adc = ADC(Pin(PIN_ADC, mode=Pin.IN))
      self.buzzer = PWM(Pin(PIN_BUZZER))
      self.buzzer.freq(BUZZER_FREQ)
      self.buzzer.duty_u16(0)
      self.red = Pin(PIN_RED, mode=Pin.OUT)
      self.green = Pin(PIN_GREEN, mode=Pin.OUT)
      self.blue = Pin(PIN_BLUE, mode=Pin.OUT)
      self.value = 0
      self.ticks = 0
      self.blink = False
        
    def callback(self, timer):
      current_value = self.adc.read_u16()
      self.ticks = self.ticks + 1
      print(abs(current_value - self.value), self.ticks)
      # if light level does not changes enough, assumes coaster is not used, not drinking
      if abs(current_value - self.value) < ADC_LEVEL and self.ticks > DRINK_TICKS:
        print(f"Need to drink water")
        self.green.off()
        if self.ticks <= 2 * DRINK_TICKS:
          if self.blink:
            self.blink = False
            self.blue.on()
            self.buzzer.duty_u16(BUZZER_DUTY)
          else:
            self.blink = True
            self.blue.off()
            self.buzzer.duty_u16(0)

        if self.ticks > 2 * DRINK_TICKS:
          self.blue.off()
          self.red.on()
          self.buzzer.duty_u16(BUZZER_DUTY)
          self.blink = False

      elif abs(current_value - self.value) >= ADC_LEVEL:
        self.ticks = 0
        self.buzzer.duty_u16(0)
        self.red.off()
        self.green.off()
        self.blue.off()
        self.blink = True
        time.sleep(1)
        self.green.on()

      self.value = current_value
    
    def __call__(self, timer):
      self.callback(timer)
        

coaster = SmartCoaster()
Timer().init(mode=Timer.PERIODIC, period=TIMER_PERIOD, callback=coaster)
