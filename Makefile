.PHONY: run-server tests install

run-server:
	sudo venv/bin/python server.py

tests:
	nosetests -v .

install:
	cp farbsort-websocket.service /etc/systemd/system/
