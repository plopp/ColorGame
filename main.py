#!/usr/bin/env python3

import sys
import asyncio
import time
import colorsys
from rgbmatrix5x5 import RGBMatrix5x5
import random
import RPi.GPIO as gpio
from plasma.gpio import PlasmaGPIO
from plasma import get_device
from subprocess import Popen, PIPE

"""
Färgspel - Lär dig färgerna
"""

__author__ = "Marcus Kempe"
__version__ = "0.1.0"
__license__ = "MIT"

BRIGHTNESS = 0.4

# Init PLASMA
NUM_LIGHTS = 6
Plasma, args = get_device("GPIO:15:14")
plasma = Plasma(NUM_LIGHTS, **args)
plasma.set_clear_on_exit()

# Init sCREEN
rgbmatrix5x5 = RGBMatrix5x5()
rgbmatrix5x5.set_clear_on_exit()
rgbmatrix5x5.set_brightness(BRIGHTNESS)

BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (127, 0, 255)
ORANGE = (255, 128, 0)
PINK = (255, 0, 255)
WHITE = (255, 255, 255)

BLACK = (0, 0, 0)

COLORS = [BLUE, GREEN, YELLOW, PURPLE, ORANGE, PINK, RED, WHITE]

FILES = {
    BLUE: "sound/sv-SE/blue.wav",
    GREEN: "sound/sv-SE/green.wav",
    YELLOW: "sound/sv-SE/yellow.wav",
    PURPLE: "sound/sv-SE/purple.wav",
    ORANGE: "sound/sv-SE/orange.wav",
    PINK: "sound/sv-SE/pink.wav",
    RED: "sound/sv-SE/red.wav",
    WHITE: "sound/sv-SE/white.wav",
}

CORRECT_ANSWER = BLUE

BUTTON1 = 5
BUTTON2 = 11
BUTTON3 = 8
BUTTON4 = 25
BUTTON5 = 9
BUTTON6 = 10
ANSWER = 0
BUTTONS = [BUTTON1, BUTTON2, BUTTON3, BUTTON4, BUTTON5, BUTTON6]


def handle_button(but):
    print(but)


gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(BUTTONS, gpio.IN, pull_up_down=gpio.PUD_UP)


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


async def set_volume(vol=40):
    await run("amixer cset numid=1 {vol}%".format(vol=vol))


async def play_sound(color):
    await run("aplay {file}".format(file=FILES[color]))


async def play_sound_beep():
    await run("aplay {file}".format(file="sound/correct_beep.wav"))


async def roll_colors():
    global CORRECT_ANSWER
    random.shuffle(COLORS)
    CORRECT_ANSWER = COLORS[random.randint(0, plasma.get_light_count() - 1)]


async def output_lights():
    for x in range(plasma.get_light_count()):
        print("Light", x, COLORS[x])
        plasma.set_light(x, *COLORS[x], brightness=BRIGHTNESS)
        plasma.show()


async def turn_off_light(num):
    if num < plasma.get_light_count():
        plasma.set_light(num, *BLACK)
        plasma.show()


async def turn_off_all_lights():
    plasma.set_all(*BLACK)
    plasma.show()


async def output_screen():
    print(*CORRECT_ANSWER)
    rgbmatrix5x5.set_all(*CORRECT_ANSWER)
    rgbmatrix5x5.show()


async def clear_screen():
    rgbmatrix5x5.set_all(*BLACK)
    rgbmatrix5x5.show()


async def click():
    global ANSWER
    while True:
        if (gpio.input(BUTTON1) == gpio.LOW):
            ANSWER = COLORS[0]
            break
        elif (gpio.input(BUTTON2) == gpio.LOW):
            ANSWER = COLORS[1]
            break
        elif (gpio.input(BUTTON3) == gpio.LOW):
            ANSWER = COLORS[2]
            break
        elif (gpio.input(BUTTON4) == gpio.LOW):
            ANSWER = COLORS[3]
            break
        elif (gpio.input(BUTTON5) == gpio.LOW):
            ANSWER = COLORS[4]
            break
        elif (gpio.input(BUTTON6) == gpio.LOW):
            ANSWER = COLORS[5]
            break
        await asyncio.sleep(0.05)


async def main():
    print("Färgspel!")

    # Game loop
    while True:
        await set_volume(50)
        await roll_colors()
        await asyncio.gather(output_lights(), output_screen())
        while True:
            await click()
            if (ANSWER == CORRECT_ANSWER):
                await asyncio.gather(turn_off_all_lights(), play_sound(CORRECT_ANSWER), play_sound_beep())
                await asyncio.sleep(0.2)
                await clear_screen()
                await asyncio.sleep(0.2)
                break
            else:
                await turn_off_light(COLORS.index(ANSWER))

if __name__ == "__main__":
    """ This is executed when run from the command line """
    asyncio.run(main())
