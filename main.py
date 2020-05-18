#!/usr/bin/env micropython

import logging
from time import sleep
"""from smbus import SMBus"""

from ev3dev2.motor import MediumMotor, LargeMotor, SpeedPercent, MoveSteering, OUTPUT_A, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor, InfraredSensor
from ev3dev2.port import LegoPort
from ev3dev2.sound import Sound
from ev3dev2.button import Button

# Logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)5s: %(message)s')
log = logging.getLogger(__name__)
log.info("Starting")

# Configure brick variables
medium_motor = MediumMotor(OUTPUT_A)
right_motor = LargeMotor(OUTPUT_B)
left_motor = LargeMotor(OUTPUT_C)
"""Pixy2 = LegoPort(INPUT_1)
Pixy2.mode = 'other-i2c'
bus = SMBus(3)
address = 0x54
sigs = 1
data = [174, 193, 32, 2, sigs, 1]"""
touch_sensor = TouchSensor(INPUT_2)
color_sensor = ColorSensor(INPUT_3)
infrared_sensor = InfraredSensor(INPUT_4)
steering_drive = MoveSteering(OUTPUT_B, OUTPUT_C)
sound = Sound()
button = Button()

# Play startup sound
sound.play_file("/home/robot/sounds/Confirm.wav")

# Define functions


def grab():
    medium_motor.duty_cycle_sp = 70
    medium_motor.run_direct()
    touch_sensor.wait_for_pressed()
    medium_motor.stop()


def reset():
    grab()
    medium_motor.on_for_rotations(-50, 14.2)
    medium_motor.reset()


def release():
    log.info("starting release")
    medium_motor.duty_cycle_sp = -50
    medium_motor.run_direct()
    min_degrees = medium_motor.degrees
    iterations_at_min = 0
    while iterations_at_min < 10:
        # log.info("degrees: {:6.2f}".format(medium_motor.degrees))
        degrees = medium_motor.degrees
        if degrees < min_degrees:
            min_degrees = degrees
            iterations_at_min = 0
        else:
            iterations_at_min += 1

    medium_motor.stop()
    log.info("finished release")


def search():
    left_motor.reset()
    lowest = 26
    position = 0
    steering_drive.on(-100, SpeedPercent(30))
    while left_motor.degrees <= 1800:
        reading = abs(infrared_sensor.heading())
        degrees = left_motor.degrees
        if reading != 0 and reading < lowest:
            log.info("lowest: {:6.2f}, position: {:6.2f}".format(
                reading, degrees))
            lowest = reading
            position = degrees
            sound.play_tone(frequency=440, duration=0.1)
    steering_drive.on(100, SpeedPercent(30))
    while left_motor.degrees > position:
        pass
    steering_drive.off()


def safe_steering(steering: float) -> float:
    if steering > 100:
        return 100
    elif steering < -100:
        return -100
    else:
        return steering


# Start program
reset()
starting = True
while starting or infrared_sensor.distance() == None or infrared_sensor.distance() >= 50:
    starting = False
    search()
    steering_drive.on_for_rotations(
        steering=0, speed=SpeedPercent(75), rotations=4)

while infrared_sensor.distance() > 2:
    steering_drive.on(steering=(safe_steering(infrared_sensor.heading()
                                              * 5)), speed=SpeedPercent(50))
steering_drive.off()
sound.play_file("/home/robot/sounds/Detected.wav",
                play_type=sound.PLAY_WAIT_FOR_COMPLETE)
steering_drive.on_for_rotations(
    steering=0, speed=SpeedPercent(50), rotations=0.7)

grab()

sleep(2)

steering_drive.on_for_rotations(
    steering=100, speed=SpeedPercent(50), rotations=3)
steering_drive.on_for_rotations(
    steering=0, speed=SpeedPercent(50), rotations=2)

release()

steering_drive.on_for_rotations(
    steering=0, speed=SpeedPercent(-50), rotations=2)
steering_drive.off()
