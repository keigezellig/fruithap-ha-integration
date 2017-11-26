import appdaemon.appapi as appapi


#
# Hello World App
#
# Args:
#

class HelloWorld(appapi.AppDaemon):
    def initialize(self):
        self.listen_state(self.on_switch_change, "switch")
        self.listen_state(self.on_light_change, "light")
        self.listen_state(self.on_temp_counter_change, "sensor.temp_1_counter_value")
        self.listen_state(self.on_temp_counter_change, "sensor.humid_1_counter_value")
        self.log("Hello from AppDaemon")
        self.log("You are now ready to run Apps!")
        a = self.get_state(entity_id="switch.kaku_sw1")
        self.log(a)

    def on_switch_change(self, entity, attribute, old, new, kwargs):
        device, entity_name = self.split_entity(entity)
        msg = device + " " + entity_name + " " + old + " " + new
        self.log(msg)
        self.call_service("mqtt/publish", topic="events", payload=msg)

    def on_light_change(self, entity, attribute, old, new, kwargs):
        device, entity_name = self.split_entity(entity)
        msg = device + " " + entity_name + " " + old + " " + new
        self.log(msg)
        self.call_service("mqtt/publish", topic="events", payload=msg)

    def on_temp_counter_change(self, entity, attribute, old, new, kwargs):
        encoded_value = int(new)
        signbit = (encoded_value & 0x80000 != 0)
        qtytype = encoded_value >> 20
        abs_value = encoded_value & 0x7FFFF
        value = abs_value

        if signbit:
            value = -abs_value

        self.log(qtytype)
        self.log(value)

        value = value / 100

        if qtytype == 0:
            self.set_state(entity_id="sensor.temp1", state=12.3, unit_of_measurement='°C')
        else:
            self.set_state(entity_id="sensor.hum1", state=1.2, unit_of_measurement='%')
