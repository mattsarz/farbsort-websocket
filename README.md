Setup
-----

Checkout:
```
git clone https://github.com/bbvch/farbsort-websocket.git
```

Preparation:
```
cd farbsort-websocket
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```


Run
---

Run server:
```
sudo venv/bin/python server.py
```

Run server in simulation mode:
```
sudo venv/bin/python server.py --simulate
```


Tests
-----

Run tests:
```
make tests
```

Run simulation test script:
```
./test-one-stone-at-a-time.sh | sudo venv/bin/python server.py --simulate
```
