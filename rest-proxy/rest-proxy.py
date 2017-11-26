import argparse
import json
import logging

import requests
from flask import Flask
from flask import Response

logger = logging.getLogger(__name__)
app = Flask(__name__)


def fill_in_urls(response):
    for item in response:
        logger.debug(item["SupportedOperations"])
        for operation in item["SupportedOperations"]:
            logger.debug(operation)
            item["SupportedOperations"][operation]="bla"

    logger.debug(response)

@app.route('/api/configuration/sensors', methods=['GET'], )
def get_configuration():
    url = app_daemon_url + "/config"
    data = {}
    r = requests.post(url, json=json.dumps(data))
    resp = fill_in_urls(r.json())
    logger.debug(resp)
    return Response(status=r.status_code, response=json.dumps(resp), content_type='text/json; charset=utf-8')



def create_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen_host",
                        default="0.0.0.0")
    parser.add_argument("--listen_port", default="5001")
    parser.add_argument("--ha_host",
                        default="localhost")
    parser.add_argument("--ha_port", default="5000")
    parser.add_argument("--loglevel", help="Minimum loglevel",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default="DEBUG")

    return parser


if __name__ == '__main__':
    argparser = create_argparser()
    args = argparser.parse_args()

    loglevel = getattr(logging, args.loglevel)
    logging.basicConfig(level=loglevel, format='%(asctime)s - %(levelname)s - %(message)s')

    logger.info("Settings: {settings} ".format(settings=args))

    app_daemon_url = "http://{host}:{port}/api/appdaemon".format(host=args.ha_host, port=args.ha_port)
    app.run(host=args.listen_host, port=args.listen_port)