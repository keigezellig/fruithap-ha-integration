import json
from base64 import b64encode

import appdaemon.appapi as appapi
import requests


class StateChangePusher(appapi.AppDaemon):
    def initialize(self):
        self.__topic = self.args["topic"]
        self.__camera_refresh = self.args["camera_refresh"]
        self.listen_state(self.on_switch_change, "switch")
        self.listen_state(self.on_switch_change, "light")
        self.listen_state(self.on_switch_change, "binary_sensor")
        self.run_every(callback=self.on_camera_change, start=self.datetime(), interval=self.__camera_refresh)

    def on_switch_change(self, entity, attribute, old, new, kwargs):

        message = self.__get_switch_value(entity, new)
        self.__send_message(message)

    def __send_message(self, data):
        msg = json.dumps(data)
        # self.log("Sending message")
        self.call_service("mqtt/publish", topic=self.__topic, payload=msg)

    def on_camera_change(self, kwargs):

        # self.log("camera refresh")
        cameras = self.get_state(entity_id="camera")
        for name, data in cameras.items():
            # self.log(data)

            message = self.__get_camera_value(data, name)

            self.__send_message(message)

    def __get_switch_value(self, switch, state):
        message = {"TimeStamp": self.get_state(entity_id=switch, attribute="last_updated"),
                   "SensorName": switch,
                   "Data":
                       {"Content":
                           {
                               "Value": self.__get_switch_state(state)
                           }
                       },
                   "TypeName": "OnOffValue"
                   }
        return message

    def __get_camera_value(self, data, name):
        url = self.config["HASS"]["ha_url"] + data["attributes"]["entity_picture"]
        resp = requests.get(url)
        imgdata = None
        if resp.status_code == 200:
            content = b64encode(resp.content)
            imgdata = content.decode('utf-8')

        message = {"TimeStamp": data["last_updated"],
                   "SensorName": name,
                   "Data":
                       {"Content":
                           {
                               "Value": imgdata
                           }
                       },
                   "TypeName": "ImageValue"
                   }
        return message

    def __get_switch_state(self, state):
        if state == 'off':
            return 1
        elif state == 'on':
            return 2
        else:
            return 0
