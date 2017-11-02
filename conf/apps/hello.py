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
     self.log("Hello from AppDaemon")
     self.log("You are now ready to run Apps!")
     
  def on_switch_change(self, entity, attribute, old, new, kwargs):
      device, entity_name = self.split_entity(entity)
      msg = device + " "+entity_name + " " +old + " "+new
      self.log(msg)
      self.call_service("mqtt/publish", topic = "events", payload = msg)
      
  def on_light_change(self, entity, attribute, old, new, kwargs):
      device, entity_name = self.split_entity(entity)
      msg = device + " "+entity_name + " " +old + " "+new
      self.log(msg)
      self.call_service("mqtt/publish", topic = "events", payload = msg)
      
      
