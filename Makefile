.PHONY: run-server tests

run-server:
	sudo venv/bin/python server.py

tests:
	nosetests -v .
