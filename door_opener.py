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
ACTIVATE_GPIO = 7
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


def publish_event(timestamp, source):
    """
    publish mqtt message
    :return:
    """
    message = {
        'timestamp': timestamp,
        'event': 'door_activated',
        'source': source
    }
    topic = 'garage_door_opener/events'
    payload = json.dumps(message)
    qos = 1
    MQTT_CLIENT.publish(topic, payload, qos)
    LOG.info('Published Message: %s', message)


def callback(client, userdata, message):
    """
    custom callback for MQTT messages
    :param client:
    :param userdata:
    :param message:
    :return:
    """
    del client
    del userdata
    LOG.debug('raw message: %s', )
    LOG.info('received message: %s on topic: %s', message.payload,
             message.topic)
    event_ts = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    activate()
    publish_event(event_ts, 'mqtt')


def door_status():
    """
    fetch door status from GPIO pins (via reed switch)
    :return:
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSE_GPIO, GPIO.IN)
    ret_val = None
    LOG.debug('door_status: ********** GPIO %s is: %s **********', SENSE_GPIO, GPIO.input(SENSE_GPIO))
    if GPIO.input(SENSE_GPIO) == 1:
        LOG.info('door_status: DOOR OPEN')
        ret_val = ('CLOSE', 'DOOR IS OPEN')
    elif GPIO.input(SENSE_GPIO) == 0:
        LOG.info('door_status: DOOR CLOSED')
        ret_val = ('OPEN', 'DOOR IS CLOSED')
    else:
        LOG.error('door_status: UNABLE TO GET DOOR STATUS')
    GPIO.cleanup()
    return ret_val


def activate():
    """
    handle the button press (activate the GPIO pin to trigger the relay)
    :return:
    """
    LOG.info('activate: SWITCH ACTIVATED')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ACTIVATE_GPIO, GPIO.OUT)
    GPIO.output(ACTIVATE_GPIO, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(ACTIVATE_GPIO, GPIO.HIGH)
    GPIO.cleanup()


@APP.route('/')
@APP.route('/index')
def index():
    """
    render the index page
    :return:
    """
    status = door_status()
    if status[0] == 'OPEN':
        text_color = '#006600'
        bg_color = '#CCFFCC'
    elif status[0] == 'CLOSE':
        text_color = '#660000'
        bg_color = '#FFCCCC'
    else:
        text_color = '#333333'
        bg_color = '#EEEEEE'
    template_data = {
        'title': 'Garage Door',
        'button_text': status[0],
        'door_state': status[1],
        'color': text_color,
        'background': bg_color
    }
    return flask.render_template('index.html', **template_data)


@APP.route('/button')
def push_button():
    """
    handle the button press (activate the GPIO pin to trigger the relay)
    :return:
    """
    event_ts = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    activate()
    publish_event(event_ts, 'web interface')
    time.sleep(10)  # wait for door to close before returning
    return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
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
    MQTT_CLIENT.configureOfflinePublishQueueing(-1)
    MQTT_CLIENT.configureDrainingFrequency(2)
    MQTT_CLIENT.configureConnectDisconnectTimeout(10)
    MQTT_CLIENT.configureMQTTOperationTimeout(5)
    LOG.debug('CONNECT: CAFilePath: %s  KeyPath: %s  CertificatePath: %s',
              CA_FILE_PATH, PRIVATE_KEY_PATH, CERTIFICATE_PATH)
    MQTT_CLIENT.connect()
    # MQTT_CLIENT.subscribe('garage_door_opener/commands', 0, callback)

    try:
        APP.run(host='0.0.0.0', port=80, debug=False)
    finally:
        LOG.debug('CLEANING UP')
        GPIO.cleanup()
