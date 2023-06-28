import flwr as fl
 
# Parameters to be customized by the user:
num_rounds = 10
 
# Weighted average of the accuracy:
def acc_wavg(metrics):
    n = sum([i for i, _ in metrics])
    acc = sum([i * metric["accuracy"] / n for i, metric in metrics])
    return {"accuracy": acc}
 
strategy = fl.server.strategy.FedAvg(
    min_available_clients=2,
    evaluate_metrics_aggregation_fn=acc_wavg
)
 
# Flower server:
fl.server.start_server(
    server_address="0.0.0.0:5000",
    config=fl.server.ServerConfig(num_rounds=num_rounds),
    strategy=strategy
)