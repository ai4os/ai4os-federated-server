import flwr as fl

FEDERATED_ROUNDS: int = 2
FEDERATED_METRIC: str = "accuracy"
FEDERATED_MIN_CLIENTS: int = 2
FEDERATED_STRATEGY: str = "fed_avg"  # If None federated average is applied
# Values: fed_avg, fed_prox, fed_opt, fed_adam, fed_yogi


# Weighted average of the metric:
def wavg_metric(metrics):
    global FEDERATED_METRIC
    n = sum([i for i, _ in metrics])
    wavg_metric = sum([i * metric[FEDERATED_METRIC] / n for i, metric in metrics])
    return {FEDERATED_METRIC: wavg_metric}


if FEDERATED_STRATEGY == "fed_avg" or FEDERATED_STRATEGY == None:
    strategy = fl.server.strategy.FedAvg(
        min_available_clients=FEDERATED_MIN_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )
elif FEDERATED_STRATEGY == "fed_prox":
    strategy = flwr.server.strategy.FedProx(
        min_available_clients=FEDERATED_MIN_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )
elif FEDERATED_STRATEGY == "fed_opt":
    strategy = flwr.server.strategy.FedOpt(
        min_available_clients=FEDERATED_MIN_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )
elif FEDERATED_STRATEGY == "fed_adam":
    strategy = flwr.server.strategy.FedAdam(
        min_available_clients=FEDERATED_MIN_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )
elif FEDERATED_STRATEGY == "fed_yogi":
    strategy = flwr.server.strategy.FedYogi(
        min_available_clients=FEDERATED_MIN_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )

# Flower server:
fl.server.start_server(
    server_address="0.0.0.0:5000",
    config=fl.server.ServerConfig(num_rounds=FEDERATED_ROUNDS),
    strategy=strategy,
)

