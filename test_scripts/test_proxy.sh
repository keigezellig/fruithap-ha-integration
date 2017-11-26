#!/bin/sh

#curl -i -X POST -H "Content-Type: application/json" http://localhost:5000/api/appdaemon/test_endpoint -d '{"type": "Hello World Test"}'
curl -vvvv http://localhost:5001/api/configuration/sensors
