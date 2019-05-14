#!/usr/bin/env python3
"""
    Script to monitor door status via GPIO pin
"""
import datetime
import json
import logging
import threading
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO

SENSE_GPIO = 2


def setup_logging(name, level):
    """
    configure logger for module

    :param name:
    :param level:
    :return:
    """
    log = logging.getLogger(name)
    log.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    log.addHandler(console_handler)

    return log


def publish_event(event):
    """
    publish mqtt message
    :return:
    """
    message = {
        'timestamp':
        datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
        'event': event,
    }
    topic = 'garage_door_opener/events'
    payload = json.dumps(message)
    qos = 1
    MQTT_CLIENT.publish(topic, payload, qos)
    LOG.info('Published Message: %s', message)


class Door:
    """
    Door state class
    The run() method will be started and it will run in a background thread
    until the application exits.
    """

    def __init__(self, interval=5, channel=SENSE_GPIO):
        """
        Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        :type channel: int
        :param channel: GPIO (BCM mode) pin to watch
        """
        self.interval = interval
        self.state = None
        self.channel = channel

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def callback(self, channel, publish=True):
        """
        callback method for event detector
        :param channel:
        :param publish:
        :return:
        """
        LOG.debug('********** Door.callback **********')
        if GPIO.input(channel) == 1:
            self.state = 'OPEN'
            LOG.info('DOOR IS NOW OPEN (1)')
            if publish:
                publish_event('door_open')
        elif GPIO.input(channel) == 0:
            self.state = 'CLOSED'
            LOG.info('DOOR IS NOW CLOSED (0)')
            if publish:
                publish_event('door_closed')
        else:
            LOG.error('unable to read %s', channel)

    def run(self):
        """
            Method that runs forever
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SENSE_GPIO, GPIO.IN)
        self.callback(self.channel, publish=False)
        GPIO.add_event_detect(self.channel, GPIO.BOTH, callback=self.callback)
        while True:
            time.sleep(self.interval)
            LOG.debug('.')


if __name__ == '__main__':
    LOG = setup_logging('door_monitor', logging.INFO)
    MQTT_LOG = setup_logging('AWSIoTPythonSDK.core', logging.INFO)

    CLIENT_ID = 'garage_door_opener'
    ENDPOINT = 'MYENDPOINT.iot.us-east-1.amazonaws.com'
    CA_FILE_PATH = '/opt/aws/iot/root-CA.crt'
    PRIVATE_KEY_PATH = '/opt/aws/iot/garage_door_opener.private.key'
    CERTIFICATE_PATH = '/opt/aws/iot/garage_door_opener.cert.pem'

    MQTT_CLIENT = AWSIoTMQTTClient(CLIENT_ID)
    MQTT_CLIENT.configureEndpoint(ENDPOINT, 8883)
    MQTT_CLIENT.configureCredentials(CA_FILE_PATH, PRIVATE_KEY_PATH,
                                     CERTIFICATE_PATH)
    MQTT_CLIENT.configureAutoReconnectBackoffTime(1, 32, 20)
    MQTT_CLIENT.configureOfflinePublishQueueing(-1)
    MQTT_CLIENT.configureDrainingFrequency(2)
    MQTT_CLIENT.configureConnectDisconnectTimeout(10)
    MQTT_CLIENT.configureMQTTOperationTimeout(5)
    LOG.debug('CONNECT: CAFilePath: %s  KeyPath: %s  CertificatePath: %s',
              CA_FILE_PATH, PRIVATE_KEY_PATH, CERTIFICATE_PATH)
    MQTT_CLIENT.connect()
    try:
        print('STARTING DOOR MONITOR')
        DOOR = Door()
        while True:
            time.sleep(60)
    finally:
        LOG.info('EXITING, CLEANING UP')
        GPIO.cleanup()
