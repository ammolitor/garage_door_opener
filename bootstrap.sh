#!/usr/bin/env bash

PV="3.7"
if ! pip${PV} -V | grep -q "${PV}"; then
    echo "please install python/pip ${PV}"
    exit 1
fi
command -v virtualenv || pip${PV} install virtualenv

# crude bootstrap script to enable development in a virtualenv
command -v virtualenv "$(command -v python${PV})" venv
. venv/bin/activate
pip${PV} install -r requirements.txt

echo "
to activate run:
    . venv/bin/activate
"
