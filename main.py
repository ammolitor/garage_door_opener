#!/usr/bin/env python3
"""
    local api application entry point
"""
import argparse
import logging
import connexion
from flask_cors import CORS


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


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--port', type=int, default=5000)
    PARSER.add_argument('--bind', default='0.0.0.0')
    ARGUMENTS = PARSER.parse_args()

    LOG = setup_logging('garage_door_opener', logging.INFO)

    try:
        APP = connexion.App(__name__, specification_dir="./")
        CORS(APP.app)
        APP.add_api("swagger.yml")
        LOG.info('STARTING API SERVER')
        APP.run(server='tornado',
                host=ARGUMENTS.bind,
                port=ARGUMENTS.port,
                debug=True)
    finally:
        LOG.info('SHUTTING DOWN')
