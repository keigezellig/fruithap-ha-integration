from base64 import b64encode

import appdaemon.appapi as appapi

#
# State Change Pusher App
#
# This app will push HA state changes of sensors to the message queue to be picked up by the FruitHap notifier app
#
# Args:
# topic: Message queue topic
# camera_refresh: The refresh rate of cameras in seconds

import datetime
import json
import requests


class StateChangePusher(appapi.AppDaemon):
    def initialize(self):
        self.log(self.config)
        self.__topic = self.args["topic"]
        self.__camera_refresh = self.args["camera_refresh"]
        self.listen_state(self.on_switch_change, "switch")
        self.listen_state(self.on_switch_change, "light")
        self.listen_state(self.on_switch_change, "binary_sensor")
        self.run_every(callback=self.on_camera_change, start=self.datetime(), interval=self.__camera_refresh)

    def on_switch_change(self, entity, attribute, old, new, kwargs):
        device, entity_name = self.split_entity(entity)

        data = {"TimeStamp": self.get_state(entity_id=entity, attribute="last_updated"),
                "SensorName": entity_name,
                "Data":
                    {"Content":
                        {
                            "Value": self.__get_switch_state(new)
                        }
                    },
                "TypeName": "OnOffValue"
                }

        self.__send_message(data)

    def __send_message(self, data):
        msg = json.dumps(data)
        self.log(msg)
        self.call_service("mqtt/publish", topic=self.__topic, payload=msg)

    def on_camera_change(self, kwargs):

        self.log("camera refresh")
        cameras = self.get_state(entity_id="camera")
        for name, data in cameras.items():
            self.log(data)

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

            self.__send_message(message)

    def __get_switch_state(self, state):
        if state == 'off':
            return 1
        elif state == 'on':
            return 2
        else:
            return 0
