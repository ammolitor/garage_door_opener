#!/usr/bin/env python3
"""
    local api application entry point
"""
import argparse
import logging
import logging.config
import connexion
from flask_cors import CORS


def setup_logging(name, level):
    """
    setup logging
    :param name:
    :param level:
    :return:
    """
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format':
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': level,
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'tornado': {
                'level': 'ERROR'
            },
        },
        'root': {
            'handlers': ['console'],
            'level': level,
        },
        'incremental': False,
    })
    return logging.getLogger(name)


if __name__ == '__main__':
    LOG = setup_logging('door_api_main', logging.INFO)
    LOG.info('LOGGING SETUP')

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--port', type=int, default=5000)
    PARSER.add_argument('--bind', default='0.0.0.0')
    ARGUMENTS = PARSER.parse_args()

    try:
        LOG.info('CREATING APP')
        APP = connexion.App(__name__, specification_dir="./")
        LOG.info('CORSing APP')
        CORS(APP.app)
        LOG.info('ADDING SWAGGER')
        APP.add_api("swagger.yml")
        LOG.info('STARTING API SERVER WITH BIND: %s,  PORT: %s',
                 ARGUMENTS.bind, ARGUMENTS.port)
        APP.run(server='tornado',
                host=ARGUMENTS.bind,
                port=ARGUMENTS.port,
                debug=True)
    finally:
        LOG.info('SHUTTING DOWN')
