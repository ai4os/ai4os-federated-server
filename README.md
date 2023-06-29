# fedserver
[![Build Status](https://jenkins.indigo-datacloud.eu/buildStatus/icon?job=Pipeline-as-code/DEEP-OC-org/fedserver/master)](https://jenkins.indigo-datacloud.eu/job/Pipeline-as-code/job/DEEP-OC-org/job/fedserver/job/master)

Federated learning server with flower.

Launching the federated learning server:
```bash
git clone https://github.com/deephdc/federated-server
cd federated-server
pip install -e .
python3 fedserver/server.py
```
The associated Docker container for this module can be found in https://github.com/deephdc/DEEP-OC-federated-server.


```
