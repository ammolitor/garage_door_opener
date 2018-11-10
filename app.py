'''
	Raspberry Pi GPIO Status and Control
'''
import time
import RPi.GPIO as GPIO
from flask import Flask, render_template
app = Flask(__name__)


def push_button():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(7, GPIO.OUT)
	GPIO.output(7, GPIO.LOW)
	time.sleep(0.5)
	GPIO.output(7, GPIO.HIGH)
	GPIO.cleanup()


@app.route("/")
def index():
	templateData = {
	'title' : 'Garage Door'
	}
	return render_template('index.html', **templateData)

@app.route("/button")
def push_button():
	templateData = {
	'title' : 'Garage Door'
	}
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(7, GPIO.OUT)
	GPIO.output(7, GPIO.LOW)
	time.sleep(0.5)
	GPIO.output(7, GPIO.HIGH)
	GPIO.cleanup()
	return render_template('index.html', **templateData)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80, debug=True)
