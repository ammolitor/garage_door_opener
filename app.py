"""
    Raspberry Pi GPIO Status and Control
"""
import time
import flask
import RPi.GPIO as GPIO

APP = flask.Flask(__name__)


@APP.route("/")
@APP.route("/index")
def index():
    """
    render the index page
    :return:
    """
    template_data = {
        'title': 'Garage Door'
    }
    return flask.render_template('index.html', **template_data)


@APP.route("/button")
def push_button():
    """
    handle the button press (activate the GPIO pin to trigger the relay)
    :return:
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(7, GPIO.OUT)
    GPIO.output(7, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(7, GPIO.HIGH)
    GPIO.cleanup()
    return flask.redirect(flask.url_for('index'))


if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=80, debug=False)
