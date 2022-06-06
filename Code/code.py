'''
import board
import digitalio
import time

led = digitalio.DigitalInOut(board.LED0)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
    print("DonE")
'''
'''
import gnss
import time

nav = gnss.GNSS([gnss.SatelliteSystem.GPS, gnss.SatelliteSystem.GLONASS])
last_print = time.monotonic()
while True:
    nav.update()
    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        if nav.fix is gnss.PositionFix.INVALID:
            print("Waiting for fix...")
            continue
        print("Latitude: {0:.6f} degrees".format(nav.latitude))
        print("Longitude: {0:.6f} degrees".format(nav.longitude))
        print("Altitude {0:.6f} meters".format(nav.altitude))
        print("Time: {} ".format(nav.timestamp))


'''

'''
read gps gsnss when True led on else blink

check if sd card is ready then
check read gps , 3d acc
write gps data  and 3 acc to  file on sd (get date? frommgps? use as file name)
(Structure of data as list,dic or json?)[time,latitude,longitude,Acceleration.X,Acceleration.Y,Acceleration.Z,Gyro.X,Gyro.Y,Gyro.Z,temperature]

loop

    read gps , 3d acc
    if  3d acc extrem  piezo on   (proof for change of acc in two axis , then switch the piezo of )
    write to sd
    after sec  start new read



'''
import random

import board
import storage
import time

import sdioio           #for sd card
import digitalio        #for led,piezo
import gnss             #for gps
import busio            #for i2c
#import adafruit_mpu6050 #for mpu6050

#define
led_sd = digitalio.DigitalInOut(board.LED0)
led_sd.direction = digitalio.Direction.OUTPUT
led_gps = digitalio.DigitalInOut(board.LED1)
led_gps.direction = digitalio.Direction.OUTPUT



#piezo = digitalio.DigitalInOut(pin22)??
#piezo.direction = digitalio.Direction.OUTPUT

i2c = board.I2C()  # uses board.SCL and board.SDA
#mpu = adafruit_mpu6050.MPU6050(i2c)

nav = gnss.GNSS([gnss.SatelliteSystem.GPS, gnss.SatelliteSystem.GLONASS])

try:

    sd = sdioio.SDCard(
        clock=board.SDIO_CLOCK,
        command=board.SDIO_COMMAND,
        data=board.SDIO_DATA,
        frequency=25000000)
    vfs = storage.VfsFat(sd)
    storage.mount(vfs, '/sd')
    led_sd.value = True

except:
    print("Error SD Card")
    led_sd.value = False



def write_data(data,file_name="track.txt"):

    #check if file exist
    #if not sd.exists(file_name):
    #    with open("/sd/" + file_name, "w") as f:
    #    print("Write to sd: {}".format(data))
    #    f.write(str(data)+"\r\n")

    with open("/sd/" + file_name, "a") as f:
        print("Write to sd: {}".format(data))
        f.write(str(data)+"\r\n")



def get_gps():

    if nav.fix is gnss.PositionFix.INVALID:
            print("Waiting for fix...")
            #return None
            return "Waiting for fix..."
    else:
        t = nav.timestamp[:6]
        lat = nav.latitude
        lon = nav.longitude
        alt = nav.altitude
        print("Latitude: {0:.6f} degrees".format(nav.latitude))
        print("Longitude: {0:.6f} degrees".format(nav.longitude))
        print("Altitude {0:.6f} meters".format(nav.altitude))
        print("Time: {} ".format(nav.timestamp[:6]))
    return t,lat,lon,alt


state_dic = {"gps": False , "piezo":False }

last_print = time.monotonic()
while True:

    nav.update()
    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        gps_data = get_gps()
        if gps_data == "Waiting for fix...":
            state_dic["gps"]= False

        write_data(gps_data)






    led_gps.value = state_dic["gps"]



    time.sleep(1)





