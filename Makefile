.PHONY: env
env:
	virtualenv venv --no-site-packages -p /usr/bin/python3 && . venv/bin/activate && python -m pip install -r requirements.txt

.PHONY: run
run:
	appdaemon -c conf/
