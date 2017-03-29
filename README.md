Setup
-----

Checkout:
```
git clone https://github.com/bbvch/farbsort-websocket.git
```

Preparation:
```
sudo apt-get install python-tornado
```


Run
---

Run server:
```
sudo python server.py
```

Run server in simulation mode:
```
python server.py --simulate
```


Tests
-----

Run tests:
```
make tests
```

Run simulation test script:
```
./test-one-stone-at-a-time.sh | python server.py --simulate
```
