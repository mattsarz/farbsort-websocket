.PHONY: run-server tests install

run-server:
	sudo python server.py

tests:
	nosetests -v .

install:
	cp farbsort-websocket.service /etc/systemd/system/
