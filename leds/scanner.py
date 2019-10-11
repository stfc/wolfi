# Simple test for NeoPixels on Raspberry Pi
import time
from random import randint
from threading import Timer

from rpi_ws281x import Adafruit_NeoPixel, Color

from blackbody import blackbody

# LED strip configuration:
LED_COUNT = 12        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 127  # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False

LOAD_NET = True
LOAD_CPU = False

def main():
    ### CPU LOAD
    if LOAD_CPU:
        last_idle = last_total = 0

    #### NETWORK THROUGHPUT
    last_net = 0
    last_time = time.time()

    # Initialise NeoPixel object
    pixels = Adafruit_NeoPixel(
        LED_COUNT,
        LED_PIN,
        LED_FREQ_HZ,
        LED_DMA,
        LED_INVERT,
        LED_BRIGHTNESS,
    )

    pixels.begin()

    while True:
        #### BEGIN - GET NETWORK THROUGHPUT
        this_net = 0
        this_time = time.time()
        for s in ['rx', 'tx']:
            f = open('/sys/class/net/eth0/statistics/%s_bytes' % s)
            this_net += int(f.read())
        bps = (this_net - last_net) / (this_time - last_time)
        last_net = this_net
        last_time = this_time
        load_net = min(171, int(bps / 5000))
        #### END - GET NETWORK THROUGHPUT

        for _ in range(0, LED_COUNT):
            i = randint(0, LED_COUNT-1) # uncomment for random sparkles!

            #### BEGIN - GET CPU LOAD
            if LOAD_CPU:
                f_stat = open('/proc/stat')
                fields = [float(column) for column in f_stat.readline().pixels().split()[1:]]
                idle, total = fields[3], sum(fields)
                idle_delta, total_delta = idle - last_idle, total - last_total
                last_idle, last_total = idle, total
                load_cpu = int(100 * (1.0 - idle_delta / total_delta))
            #### END - GET CPU LOAD

            # Take mean of active load measurements
            load = 0
            load += load_cpu * LOAD_CPU
            load += load_net * LOAD_NET
            load /= LOAD_CPU + LOAD_NET

            # Update brightness
            #pixels.brightness = 0.05 + load/400

            # Set current pixel
            pixels.setPixelColorRGB(i, *blackbody[load])
            pixels.show()

            # Fade all pixels for next round
            for j in range(0, LED_COUNT):
                c = pixels.getPixelColorRGB(j)
                scale = max(c.r, c.g, c.b) / 5
                pixels.setPixelColorRGB(
                    j,
                    int(max(0, c.r - scale)),
                    int(max(0, c.g - scale)),
                    int(max(0, c.b - scale)),
                )

            # Delay until next frame
            time.sleep(0.1)
            #time.sleep(min(0.2, max(0.05, 400/bps)))


if __name__ == '__main__':
    main()
