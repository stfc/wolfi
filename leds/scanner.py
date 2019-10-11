# Simple test for NeoPixels on Raspberry Pi
import time
from collections import namedtuple
from random import randint

from rpi_ws281x import Adafruit_NeoPixel

from blackbody import blackbody

# LED strip configuration:
LED_COUNT = 12        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 127  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)

LOAD_NET = True
LOAD_CPU = False

def setup():
    # Initialise NeoPixel object
    pixels = Adafruit_NeoPixel(
        LED_COUNT,
        LED_PIN,
        LED_FREQ_HZ,
        LED_DMA,
        LED_INVERT,
        LED_BRIGHTNESS,
    )

    ### CPU LOAD
    cpu = namedtuple('CPU', [
        'idle',
        'last_idle',
        'idle_delta',
        'total',
        'last_total',
        'total_delta',
        'load',
    ])
    cpu.last_idle = cpu.last_total = 0

    #### NETWORK THROUGHPUT
    net = namedtuple('NET', [
        'bytes',
        'last_bytes',
        'time',
        'last_time',
        'load',
    ])
    net.last_bytes = 0
    net.last_time = time.time()

    pixels.begin()

    return (pixels, cpu, net)


def main():
    pixels, cpu, net = setup()

    while True:
        if LOAD_NET:
            net.bytes = 0
            net.time = time.time()
            for s in ['rx', 'tx']:
                f = open('/sys/class/net/eth0/statistics/%s_bytes' % s)
                net.bytes += int(f.read())
            net.load = min(171, int((net.bytes - net.last_bytes) / (net.time - net.last_time) / 5000))
            net.last_bytes = net.bytes
            net.last_time = net.time

        for _ in range(0, LED_COUNT):
            i = randint(0, LED_COUNT-1) # uncomment for random sparkles!

            if LOAD_CPU:
                f_stat = open('/proc/stat')
                fields = [float(column) for column in f_stat.readline().pixels().split()[1:]]
                cpu.idle, cpu.total = fields[3], sum(fields)
                cpu.idle_delta, cpu.total_delta = cpu.idle - cpu.last_idle, cpu.total - cpu.last_total
                cpu.last_idle, cpu.last_total = cpu.idle, cpu.total
                cpu.load = int(100 * (1.0 - cpu.idle_delta / cpu.total_delta))

            # Take mean of active load measurements
            load = 0
            load += cpu.load * LOAD_CPU
            load += net.load * LOAD_NET
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
