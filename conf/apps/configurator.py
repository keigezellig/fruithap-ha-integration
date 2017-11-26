import json
from base64 import b64encode

import appdaemon.appapi as appapi


#
# Fruithap configuration converter
#
# This app will provide endpoints to retrieve HA configuration in the FruitHAP configuration format
#
# Args:
#
import requests


class Configurator(appapi.AppDaemon):
    def initialize(self):
        self.register_endpoint(self.getConfig, 'config')
        self.register_endpoint(self.executeOperation, 'execute')

    def getConfig(self, data):
        config = []
        entities = self.get_state()
        for entity in entities:
            device, entity_name = self.split_entity(entity)
            if device == 'switch' or device == 'camera' or device == 'binary_sensor':
                entry = {"Name": entity,
                         "Description": self.get_state(entity_id=entity, attribute="friendly_name"),
                         "Category": device,
                         "ValueType": self.__getValueType(device),
                         "SupportedOperations": self.__getSupportedOperations(device)}

                config.append(entry)
                self.log(entry)

        return config, 200

    def executeOperation(self, data):
        if not data:
            return "No input data", 400

        operation = data["operationName"]

        if operation not in ["GetValue", "GetAllValues", "GetLastUpdateTime", "Initalize", "TurnOn", "TurnOff"]:
            return "Operation {operation} not supported".format(operation=operation), 400

        if operation in ["GetAllValues"]:
            return self.__getAllValues(), 200

        sensor = data["sensorName"]

        if (not self.get_state(entity_id=sensor)) and (operation not in ["GetAllValues"]):
            return "Entity {entity} not found".format(entity=sensor), 404

        device, name = self.split_entity(entity_id=sensor)
        if operation in ["TurnOn", "TurnOff"] and device != 'switch':
            return "Operation {operation} not supported on {sensor}".format(operation=operation, sensor=sensor), 400

        return self.__executeOperation(sensor, operation), 200



    def __getValueType(self, device):
        if device == 'camera':
            return "ImageValue"
        if device == 'switch' or device == 'binary_sensor':
            return "OnOffValue"

    def __getSupportedOperations(self, device):
        ops = {"GetValue": "", "GetLastUpdateTime": "", "Initialize": ""}

        if device == 'switch':
            ops["TurnOn"] = ""
            ops["TurnOff"] = ""

        return ops

    def __getAllValues(self):
        pass

    def __executeOperation(self, sensor, operation):

        if operation == "GetValue":
            return self.__getValue(sensor)
        if operation == "TurnOn":
            self.turn_on(entity_id=sensor)
            op_result = 2
        if operation == "TurnOff":
            self.turn_off(entity_id=sensor)
            op_result = 1
        if operation == "GetLastUpdateTime":
            op_result = self.get_state(entity_id=sensor, attribute="last_updated")
        if operation == "Initialize":
            op_result = None

        return self.__getCommandResult(sensor, operation, op_result)

    def __getValue(self, sensor):
        device, name = self.split_entity(entity_id=sensor)
        if device == "camera":
            return self.__get_camera_value(sensor)
        else:
            return self.__get_switch_value(sensor)



    def __getCommandResult(self, sensor, operation, op_result):
        return {"TimeStamp":self.time().isoformat(),
                "SensorName":sensor,
                "Data": {"Content":
                             {"OperationName":operation,
                              "Result":op_result
                              }
                         },
                "TypeName": "CommandResult"

                }

    def __get_switch_value(self, switch):
        message = {"TimeStamp": self.get_state(entity_id=switch, attribute="last_updated"),
                   "SensorName": switch,
                   "Data":
                       {"Content":
                           {
                               "Value": self.__get_switch_state(self.get_state(entity_id=switch))
                           }
                       },
                   "TypeName": "OnOffValue"
                   }
        return message

    def __get_camera_value(self, camera):

        last_updated = self.get_state(entity_id=camera, attribute="last_updated")
        url = self.config["HASS"]["ha_url"] + self.get_state(entity_id=camera, attribute="entity_picture")
        resp = requests.get(url)
        imgdata = None
        if resp.status_code == 200:
            content = b64encode(resp.content)
            imgdata = content.decode('utf-8')

        message = {"TimeStamp": last_updated,
                   "SensorName": camera,
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




