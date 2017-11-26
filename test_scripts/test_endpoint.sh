#!/bin/sh

#curl -i -X POST -H "Content-Type: application/json" http://localhost:5000/api/appdaemon/test_endpoint -d '{"type": "Hello World Test"}'
curl -i -X POST -H "Content-Type: application/json" http://localhost:5000/api/appdaemon/$1 -d '$2'
