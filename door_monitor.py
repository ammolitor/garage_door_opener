#!/usr/bin/env python3
"""
    Script to monitor door status via GPIO pin
"""
import datetime
import json
import logging
import threading
import time
import requests
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


def setup_logging(name, level):
    """
    configure logger for module
    :param name:
    :param level:
    :return:
    """
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger(name)
    log.setLevel(level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)
    return log


def publish_event(timestamp, event):
    """
    publish mqtt message
    :return:
    """
    message = {
        'timestamp': timestamp,
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

    def __init__(self, interval=1):
        """
        Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
        self.state = None

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def callback(self, door_status, publish=True):
        """
        callback method for event detector
        :param door_status:
        :param publish:
        :return:
        """
        LOG.debug('********** Door.callback **********')
        event_ts = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        if door_status == 'OPEN':
            self.state = 'OPEN'
            LOG.info('DOOR IS NOW OPEN (1)')
            if publish:
                publish_event(event_ts, 'door_open')
        elif door_status == 'CLOSED':
            self.state = 'CLOSED'
            LOG.info('DOOR IS NOW CLOSED (0)')
            if publish:
                publish_event(event_ts, 'door_closed')
        else:
            LOG.error('unable to read %s', door_status)

    def run(self):
        """
            Method that runs forever
        """
        f_door_status = requests.get(
            'http://localhost:5000/status').json().get('status')
        self.callback(f_door_status, publish=False)
        while True:
            c_door_status = requests.get(
                'http://localhost:5000/status').json().get('status')
            if f_door_status != c_door_status:
                self.callback(c_door_status, publish=True)
                f_door_status = c_door_status
            time.sleep(self.interval)
            LOG.debug('.')


if __name__ == '__main__':
    LOG = setup_logging('door_monitor', logging.INFO)
    MQTT_LOG = setup_logging('AWSIoTPythonSDK.core', logging.INFO)

    CLIENT_ID = 'garage_door_opener'
    ENDPOINT = 'ad4bgf9zw53fx-ats.iot.us-east-1.amazonaws.com'
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
