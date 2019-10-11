# Simple test for NeoPixels on Raspberry Pi
import time
from random import randint
from threading import Timer

import board
import neopixel

from blackbody import blackbody

PIN_PIXELS = board.D18
NUM_PIXELS = 8

def main():
    ### CPU LOAD
    last_idle = last_total = 0
    f_stat = open('/proc/stat')

    #### NETWORK THROUGHPUT
    # last_net = 0
    # last_time = time.time()
    # f_rx = open('/sys/class/net/eth0/statistics/rx_bytes')
    # f_tx = open('/sys/class/net/eth0/statistics/tx_bytes')

    # Initialise NeoPixel object
    pixels = neopixel.NeoPixel(
        PIN_PIXELS,
        NUM_PIXELS,
        brightness=0.1,
        auto_write=False,
        pixel_order=neopixel.GRB
    )

    while True:
        #### BEGIN - GET NETWORK THROUGHPUT
        # this_net = 0
        # this_time = time.time()
        # for f in [f_rx, f_tx]:
        #     f.seek(0)
        #     this_net += int(f.read())
        # bps = (this_net - last_net) / (this_time - last_time)
        # last_net = this_net
        # last_time = this_time
        #### END - GET NETWORK THROUGHPUT

        for _ in range(0, NUM_PIXELS):
            i = randint(0, NUM_PIXELS-1) # uncomment for random sparkles!

            #### BEGIN - GET CPU LOAD
            f_stat.seek(0)
            fields = [float(column) for column in f_stat.readline().strip().split()[1:]]
            idle, total = fields[3], sum(fields)
            idle_delta, total_delta = idle - last_idle, total - last_total
            last_idle, last_total = idle, total
            load = int(100 * (1.0 - idle_delta / total_delta))
            #### END - GET CPU LOAD

            # Update brightness
            #pixels.brightness = 0.05 + load/400

            # Set current pixel
            pixels[i] = blackbody[load]
            pixels.show()

            # Fade all pixels for next round
            for j in range(0, NUM_PIXELS):
                scale = max(pixels[i]) / 5
                pixels[j] = (
                    int(max(0, pixels[j][0] - scale)),
                    int(max(0, pixels[j][1] - scale)),
                    int(max(0, pixels[j][2] - scale)),
                )

            # Delay until next frame
            time.sleep(0.1)
            #time.sleep(min(0.2, max(0.05, 400/bps)))


if __name__ == '__main__':
    main()
