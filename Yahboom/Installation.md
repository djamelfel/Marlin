
# yahboom
## Installation
* Source code: git clone https://github.com/YahboomTechnology/Raspberry-Pi-RGB-Cooling-HAT/tree/master
* sudo pip install Adafruit-SSD1306
* sudo pip install smbus
* run sudo sh install.sh to install the script.py at startup

### Error correction
1. raise RuntimeError('Could not determine default I2C bus for platform.')

To get over this error I changed line 105 in file **/usr/local/lib/python3.9/dist-packages/Adafruit_GPIO/Platform.py**
```
Original:
    elif match.group(1) == 'BCM2835':

Changed:
    elif match.group(1) == 'BCM2711':
```
