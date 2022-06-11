"""
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
"""
"""
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


"""

"""
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



"""


import board
import storage
import time

import sdioio  # for sd card
import digitalio  # for led,piezo
import gnss  # for gps
import busio  # for i2c
import adafruit_mpu6050  # for mpu6050
import adafruit_sdcard # better SD Card use

# define
led_sd = digitalio.DigitalInOut(board.LED0)
led_sd.direction = digitalio.Direction.OUTPUT
led_gps = digitalio.DigitalInOut(board.LED1)
led_gps.direction = digitalio.Direction.OUTPUT


piezo = digitalio.DigitalInOut(board.D10)
piezo.direction = digitalio.Direction.OUTPUT

i2c = busio.I2C(board.SCL, board.SDA)  # uses board.SCL and board.SDA
mpu = adafruit_mpu6050.MPU6050(i2c)
mpu.accelerometer_range = adafruit_mpu6050.Range.RANGE_2_G
mpu.gyro_range = adafruit_mpu6050.GyroRange.RANGE_250_DPS


nav = gnss.GNSS([gnss.SatelliteSystem.GPS, gnss.SatelliteSystem.GLONASS])

def mount_sd():

    try:

        sd = sdioio.SDCard(
            clock=board.SDIO_CLOCK,
            command=board.SDIO_COMMAND,
            data=board.SDIO_DATA,
            frequency=25000000,
        )

        vfs = storage.VfsFat(sd)
        storage.mount(vfs, "/sd")

        led_sd.value = True
        return True

    except:
        print("Error SD Card")
        led_sd.value = False
        time.sleep(1)
        return False


def write_data(data, file_name="track11.txt"):
    with open("/sd/" + file_name, "a") as f:
        print("Write to sd: {}".format(data))
        f.write(str(data) + "\r\n")



def get_gps():
    if nav.fix is gnss.PositionFix.INVALID:
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
    return t, lat, lon, alt


def mpu_dataframe():
    tp_mpu = mpu.acceleration + mpu.gyro
    gyro_sum_value = sum_gyro(tp_mpu[3:])
    print((gyro_sum_value,))

    data_string=""
    for elem in tp_mpu:
        data_string = data_string+"," + str(elem)
    data_string +=  "," + str(gyro_sum_value)
    #print(data_string)
    return [data_string , gyro_sum_value]

def piezo_on_off(state=None):
    if state == True:
        piezo.value = True
    else:
        piezo.value = False
        
        

def sum_gyro(tp_gyro):
    sum = 0.0
    for elem in tp_gyro:
        sum = sum + float(elem)
        if sum > 7 or sum < -7:
            print("Alert")
            piezo_on_off(True)
        
            
    return sum

sd_ready = False
#check for sd card , blink if a Error
while sd_ready == False:
    print("SD mount")
    led_sd.value = not led_sd.value
    sd_ready = mount_sd()
    time.sleep(1)


last_print = time.monotonic()
max_value = 0.0

while True:


    # this prints out all the values like a tuple which Mu's plotter prefer
    #print("(%.2f, %.2f, %.2f " % (mpu.acceleration), end=", ")
    #print("%.2f, %.2f, %.2f)" % (mpu.gyro))
    mpu_data = mpu_dataframe()
    
    if (max_value == 0.0 or float(mpu_data[1]) > max_value):
        max_value = float(mpu_data[1])
    time.sleep(0.1)

    nav.update()
    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        gps_data = get_gps()
        #if gps_data == "Waiting for fix...":
        #    pass

        write_data(gps_data + mpu_data[0] + "," +str(max_value))
        max_value = 0.0 #reset after write to sd
        if piezo.value == True:
            piezo.value = False
