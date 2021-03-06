# Self-Balancing-Robot
This repository contains code I wrote for a self-balancing robot using Raspberry pi and Python.

## RPi.GPIO
RPi.GPIO is a python library used commonly to communicate with Raspberry Pi.

### Installation 
Use the package manager [pip](https://pip.pypa.io/en/stable/) to installRPi.GPIO.
```bash
pip install RPi.GPIO
```
### Usage

```python
IO.setwarnings(False)           #do not show any warnings
IO.setmode (IO.BCM)         #we are programming the GPIO by BCM pin numbers. (PIN35 as ‘GPIO19’)
IO.setup(19,IO.OUT)           # initialize GPIO19 as an output.

IO.setup(13,IO.OUT)

p = IO.PWM(19,50)          #GPIO19 as PWM output, with 100Hz frequency
p1 = IO.PWM(13,50)
p.start(0)                              #generate PWM signal with 0% duty cycle
p1.start(0)

IO.setup(16,IO.OUT)
IO.setup(26,IO.OUT)
IO.setup(20,IO.OUT)
IO.setup(21,IO.OUT)
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
