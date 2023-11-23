import os
import flwr as fl

FEDERATED_ROUNDS: int = int(os.environ['FEDERATED_ROUNDS'])
FEDERATED_METRIC: str = os.environ['FEDERATED_METRIC']
FEDERATED_MIN_CLIENTS: int = int(os.environ['FEDERATED_MIN_CLIENTS'])
FEDERATED_STRATEGY: str = os.environ['FEDERATED_STRATEGY']


# Values: fed_avg, fed_prox, fed_opt, fed_adam, fed_yogi


# Weighted average of the metric:
def wavg_metric(metrics):
    global FEDERATED_METRIC
    n = sum([i for i, _ in metrics])
    wavg_metric = sum([i * metric[FEDERATED_METRIC] / n for i, metric in metrics])
    return {FEDERATED_METRIC: wavg_metric}


if FEDERATED_STRATEGY == "Federated Averaging" or FEDERATED_STRATEGY is None:
    strategy = fl.server.strategy.FedAvg(
        min_available_clients=FEDERATED_MIN_CLIENTS,
        min_fit_clients=FEDERATED_MIN_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )
elif FEDERATED_STRATEGY == "Federated Optimization":
    strategy = fl.server.strategy.FedProx(
        min_available_clients=FEDERATED_MIN_CLIENTS,
        min_fit_clients=FEDERATED_MIN_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )
elif FEDERATED_STRATEGY == "Federated Optimization'":
    strategy = fl.server.strategy.FedOpt(
        min_available_clients=FEDERATED_MIN_CLIENTS,
        min_fit_clients=FEDERATED_MIN_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )
elif FEDERATED_STRATEGY == "Federated Optimization with Adam":
    strategy = fl.server.strategy.FedAdam(
        min_available_clients=FEDERATED_MIN_CLIENTS,
        min_fit_clients=FEDERATED_MIN_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )
elif FEDERATED_STRATEGY == "Adaptive Federated Optimization using Yogi":
    strategy = fl.server.strategy.FedYogi(
        min_available_clients=FEDERATED_MIN_CLIENTS,
        min_fit_clients=FEDERATED_MIN_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )

# Flower server:
fl.server.start_server(
    server_address="0.0.0.0:5000",
    config=fl.server.ServerConfig(num_rounds=FEDERATED_ROUNDS),
    strategy=strategy,
)
