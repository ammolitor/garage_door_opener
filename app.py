"""
    GPIO Garage Door Opener Control
"""
import datetime
import json
import logging
import time
import flask
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO

APP = flask.Flask(__name__)


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


def publish_event():
    """
    publish mqtt message
    :return:
    """
    message = {
        'timestamp':
        datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
        'event': 'door_activated'
    }
    topic = 'garage_door_opener/events'
    payload = json.dumps(message)
    qos = 1
    MQTT_CLIENT.publish(topic, payload, qos)
    LOG.info('Published Message: %s', message)


@APP.route("/")
@APP.route("/index")
def index():
    """
    render the index page
    :return:
    """
    LOG.debug('index rendered')
    template_data = {'title': 'Garage Door'}
    return flask.render_template('index.html', **template_data)


@APP.route("/button")
def push_button():
    """
    handle the button press (activate the GPIO pin to trigger the relay)
    :return:
    """
    LOG.debug('button activated')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(7, GPIO.OUT)
    GPIO.output(7, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(7, GPIO.HIGH)
    GPIO.cleanup()
    publish_event()
    return flask.redirect(flask.url_for('index'))


if __name__ == "__main__":
    LOG = setup_logging('garage_door_opener', logging.INFO)
    MQTT_LOG = setup_logging('AWSIoTPythonSDK.core', logging.INFO)

    CLIENT_ID = 'garage_door_opener'
    ENDPOINT = 'MYENDPOINT-ats.iot.us-east-1.amazonaws.com'
    CA_FILE_PATH = '/opt/aws/iot/root-CA.crt'
    PRIVATE_KEY_PATH = '/opt/aws/iot/garage_door_opener.private.key'
    CERTIFICATE_PATH = '/opt/aws/iot/garage_door_opener.cert.pem'

    MQTT_CLIENT = AWSIoTMQTTClient(CLIENT_ID)
    MQTT_CLIENT.configureEndpoint(ENDPOINT, 8883)
    MQTT_CLIENT.configureCredentials(CA_FILE_PATH, PRIVATE_KEY_PATH,
                                     CERTIFICATE_PATH)
    MQTT_CLIENT.configureAutoReconnectBackoffTime(1, 32, 20)
    MQTT_CLIENT.configureOfflinePublishQueueing(
        -1)  # Infinite offline Publish queueing
    MQTT_CLIENT.configureDrainingFrequency(2)  # Draining: 2 Hz
    MQTT_CLIENT.configureConnectDisconnectTimeout(10)  # 10 sec
    MQTT_CLIENT.configureMQTTOperationTimeout(5)  # 5 sec
    LOG.debug(
        'Connecting with CAFilePath: %s  KeyPath: %s  CertificatePath: %s',
        CA_FILE_PATH, PRIVATE_KEY_PATH, CERTIFICATE_PATH)
    MQTT_CLIENT.connect()

    APP.run(host='0.0.0.0', port=80, debug=False)
