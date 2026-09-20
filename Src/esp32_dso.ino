#include <Arduino.h> // Brings in the standard Arduino toolset so we can use basic functions.

const int adcPin = 34; // Tells the board we are going to read the voltage on Pin 34.
volatile int lastAdcValue = 0; // A special variable to store the voltage reading. "Volatile" means it changes suddenly in the background.
volatile bool newData = false; // A simple "True/False" flag to tell us when a fresh reading is ready.

hw_timer_t * timer = NULL; // Creates a blank placeholder for our hardware timer (our "stopwatch").
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED; // Creates a "lock" to prevent the main code and the background code from crashing into each other.

// Use the new ISR attribute
void ARDUINO_ISR_ATTR onTimer() { // This is the background function (Interrupt Service Routine) that runs when the stopwatch goes off.
  portENTER_CRITICAL_ISR(&timerMux); // Locks the safe so the main loop can't mess with our variables right now.
  lastAdcValue = analogRead(adcPin); // Measures the voltage on Pin 34 and saves the number.
  newData = true; // Flips our flag to "True" to shout: "Hey, I have a new reading!"
  portEXIT_CRITICAL_ISR(&timerMux); // Unlocks the safe so the main loop can access the variables again.(rtos command)
}

void setup() { // The setup block runs once when the board turns on.
  Serial.begin(921600); // Opens the communication line to your computer at a very fast speed (921,600 bits per second).
  
  analogReadResolution(12); // Tells the chip to give us readings between 0 and 4095 (12-bit detail).
  analogSetAttenuation(ADC_11db); // Sets the voltage limit so the pin can safely read up to about 3.3 Volts.
  
  // NEW API: timerBegin(frequency_in_Hz)
  // We set it to 1MHz so that 1 "tick" = 1 microsecond
  timer = timerBegin(1000000); // Starts the stopwatch and sets it to tick 1,000,000 times per second (1 tick = 1 microsecond).

  // NEW API: timerAttachInterrupt(timer, function)
  timerAttachInterrupt(timer, &onTimer); // Connects our stopwatch to the "onTimer" function we wrote above.
  
  // NEW API: timerAlarm(timer, alarm_value, autoreload, reload_count)
  // 100 ticks = 100us = 10kHz sampling. 0 = unlimited reloads.
  timerAlarm(timer, 100, true, 0); // Tells the stopwatch to ring the alarm every 100 ticks, repeat forever, and never stop.
}

void loop() {
  if (newData) {
    portENTER_CRITICAL(&timerMux);
    int value = lastAdcValue; // Or smoothedValue if you added the moving average
    newData = false;
    portEXIT_CRITICAL(&timerMux);
    
    // Wrap the data in start '<' and end '>' markers
    Serial.print("<"); 
    Serial.print(value);
    Serial.println(">"); 
  }
}
