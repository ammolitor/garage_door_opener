"""
    GPIO Garage Door Opener Control
"""
import datetime
import logging
import time
import RPi.GPIO as GPIO

ACTIVATE_GPIO = 7
SENSE_GPIO = 2


def door_status():
    """
    fetch door status from GPIO pins (via reed switch)
    :return:
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSE_GPIO, GPIO.IN)
    ret_val = None
    LOG.debug('door_status: ********** GPIO %s is: %s **********', SENSE_GPIO,
              GPIO.input(SENSE_GPIO))
    if GPIO.input(SENSE_GPIO) == 1:
        LOG.debug('door_status: DOOR OPEN')
        ret_val = 'OPEN'
    elif GPIO.input(SENSE_GPIO) == 0:
        LOG.debug('door_status: DOOR CLOSED')
        ret_val = 'CLOSED'
    else:
        LOG.error('door_status: UNABLE TO GET DOOR STATUS')
    GPIO.cleanup()
    return ret_val


def activate():
    """
    activate the GPIO pin to trigger the relay that activates the door
    :return:
    """
    LOG.info('activate: SWITCH ACTIVATED')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ACTIVATE_GPIO, GPIO.OUT)
    GPIO.output(ACTIVATE_GPIO, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(ACTIVATE_GPIO, GPIO.HIGH)
    GPIO.cleanup()


def status():
    """
    return door status as an object
    :return:
    """
    status_message = {
        'ts': datetime.datetime.utcnow(),
        'status': door_status()
    }
    return status_message


def open_door():
    """
    open the door if it is not
    :return:
    """
    if door_status() != 'OPEN':
        activate()


def close_door():
    """
    close the door if it is not
    :return:
    """
    if door_status() != 'CLOSED':
        activate()


LOG = logging.getLogger('door_api_door')
