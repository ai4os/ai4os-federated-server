# Federated Learning Server
[![Build Status](https://jenkins.indigo-datacloud.eu/buildStatus/icon?job=Pipeline-as-code/DEEP-OC-org/federated-server/main)](https://jenkins.indigo-datacloud.eu/job/Pipeline-as-code/job/DEEP-OC-org/job/federated-server/job/main)

Federated learning server with [flower](https://github.com/adap/flower).

**Summary:** deploys a federated learning server to train machine/deep learning models on different clients following a federated learning architecture. Customization is allowed for the number of rounds the training is performed, the aggregation strategy used, the minimum number of clients, and the error metric to be used (aggregated) as validation.

Launching the federated learning server:
```bash
git clone https://github.com/deephdc/federated-server
cd federated-server
pip install -e .
python3 fedserver/server.py
```
Possible aggregation strategies introduced as *FEDERATED_STRATEGY* (see the implementation given in [flower strategies](https://flower.dev/docs/apiref-flwr.html#)):
* **Federated average:** *"fed_avg"*. [1]
* **FedProx strategy:** *"fed_prox"*. [2]
* **Adaptive Federated Optimization using Adam:** *"fed_adam"* [3]
* **Federated Optim strategy**: *"fed_opt"* [3]
* **Adaptive Federated Optimization using Yogi:** *"fed_yogi"* [3]

The associated Docker container for this module can be found in https://github.com/deephdc/DEEP-OC-federated-server.

We provide some [client examples](./fedserver/client_samples/) as a guide for users.
Users will need to adapt the `endpoint` in those samples to point to their deployed
Federated server.


### References

[1] McMahan, B., Moore, E., Ramage, D., Hampson, S., & y Arcas, B. A. (2017, April). Communication-efficient learning of deep networks from decentralized data. In Artificial intelligence and statistics (pp. 1273-1282). PMLR.

[2] Li, T., Sahu, A. K., Zaheer, M., Sanjabi, M., Talwalkar, A., & Smith, V. (2020). Federated optimization in heterogeneous networks. Proceedings of Machine learning and systems, 2, 429-450.

[3] Reddi, S., Charles, Z., Zaheer, M., Garrett, Z., Rush, K., Konečný, J., ... & McMahan, H. B. (2020). Adaptive federated optimization. arXiv preprint arXiv:2003.00295.
