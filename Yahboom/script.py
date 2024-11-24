import smbus
import time
import os
import subprocess
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

bus = smbus.SMBus(1)

ADDR = 0x0d
FAN_REG = 0x08
RGB_OFF_REG = 0x07
MAX_LED = 3

fan_state = False
temp = 0
level_temp = 0

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

def getCPULoadRate():
    f1 = os.popen("cat /proc/stat", 'r')
    stat1 = f1.readline()
    count = 10
    data_1 = []
    for i  in range (count):
        data_1.append(int(stat1.split(' ')[i+2]))
    total_1 = data_1[0]+data_1[1]+data_1[2]+data_1[3]+data_1[4]+data_1[5]+data_1[6]+data_1[7]+data_1[8]+data_1[9]
    idle_1 = data_1[3]

    time.sleep(1)

    f2 = os.popen("cat /proc/stat", 'r')
    stat2 = f2.readline()
    data_2 = []
    for i  in range (count):
        data_2.append(int(stat2.split(' ')[i+2]))
    total_2 = data_2[0]+data_2[1]+data_2[2]+data_2[3]+data_2[4]+data_2[5]+data_2[6]+data_2[7]+data_2[8]+data_2[9]
    idle_2 = data_2[3]

    total = int(total_2-total_1)
    idle = int(idle_2-idle_1)
    usage = int(total-idle)
    # print("idle:"+str(idle)+"  total:"+str(total))
    usageRate = int(float(usage * 100  / total))
    return "CPU:"+str(usageRate)+"%"

def setRGB(num, r, g, b):
    if num >= MAX_LED:
        bus.write_byte_data(ADDR, 0x00, 0xff)
        bus.write_byte_data(ADDR, 0x01, r&0xff)
        bus.write_byte_data(ADDR, 0x02, g&0xff)
        bus.write_byte_data(ADDR, 0x03, b&0xff)
    elif num >= 0:
        bus.write_byte_data(ADDR, 0x00, num&0xff)
        bus.write_byte_data(ADDR, 0x01, r&0xff)
        bus.write_byte_data(ADDR, 0x02, g&0xff)
        bus.write_byte_data(ADDR, 0x03, b&0xff)

# Disable RBG
bus.write_byte_data(ADDR,RGB_OFF_REG,0x00)

while True:
    # Read temperature value
    cmd = os.popen('vcgencmd measure_temp').readline()
    CPU_TEMP = cmd.replace("temp=","").replace("'C\n","")
    temp = float(CPU_TEMP)

    if abs(temp - level_temp) >= 1:
        if temp <= 45:
            level_temp = 45
            setRGB(MAX_LED, 0x00, 0x00, 0xff)
        elif temp <= 47:
            level_temp = 47
            setRGB(MAX_LED, 0x1e, 0x90, 0xff)
        elif temp <= 49:
            level_temp = 49
            setRGB(MAX_LED, 0x00, 0xbf, 0xff)
        elif temp <= 51:
            level_temp = 51
            setRGB(MAX_LED, 0x5f, 0x9e, 0xa0)
        elif temp <= 53:
            level_temp = 53
            setRGB(MAX_LED, 0xff, 0xff, 0x00)
        elif temp <= 55:
            level_temp = 55
            setRGB(MAX_LED, 0xff, 0xd7, 0x00)
        elif temp <= 57:
            level_temp = 57
            setRGB(MAX_LED, 0xff, 0xa5, 0x00)
        elif temp <= 59:
            level_temp = 59
            setRGB(MAX_LED, 0xff, 0x8c, 0x00)
        elif temp <= 61:
            level_temp = 61
            setRGB(MAX_LED, 0xff, 0x45, 0x00)
        elif temp >= 63:
            level_temp = 63
            setRGB(MAX_LED, 0xff, 0x00, 0x00)

    if fan_state == False:
        if temp >= 65: 
            # enable fan
            bus.write_byte_data(ADDR, FAN_REG, 0x01)
            fan_state = True
    else:
        if temp < 60:
            # disable fan
            bus.write_byte_data(ADDR, FAN_REG, 0x00)
            fan_state = False


    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    
    # cmd = "top -bn1 | grep load | awk '{printf \"CPU:%.0f%%\", $(NF-2)*100}'"
    # CPU = subprocess.check_output(cmd, shell = True)
    CPU = getCPULoadRate()

    cmd = "free -m | awk 'NR==2{printf \"RAM:%s/%s MB \", $2-$3,$2}'"
    MemUsage = subprocess.check_output(cmd, shell = True )

    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk:%d/%dMB\", ($2-$3)*1024,$2*1024}'"
    Disk = subprocess.check_output(cmd, shell = True )

    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True )

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Write two lines of text.
    draw.text((x, top), str(CPU), font=font, fill=255)
    draw.text((x+56, top), str(CPU_TEMP), font=font, fill=255)
    draw.text((x, top+8), str(MemUsage),  font=font, fill=255)
    draw.text((x, top+16), str(Disk),  font=font, fill=255)
    draw.text((x, top+24), "wlan0:" + str(IP),  font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.5)
