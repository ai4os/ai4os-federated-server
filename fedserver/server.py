import os
import ast
import flwr as fl
import tensorflow as tf
from flwr.common import ndarrays_to_parameters


FEDERATED_ROUNDS: int = int(os.environ['FEDERATED_ROUNDS'])
FEDERATED_METRIC = os.environ['FEDERATED_METRIC']
FEDERATED_MIN_FIT_CLIENTS: int = int(os.environ["FEDERATED_MIN_FIT_CLIENTS"])
FEDERATED_MIN_AVAILABLE_CLIENTS: int = int(os.environ["FEDERATED_MIN_AVAILABLE_CLIENTS"])
FEDERATED_STRATEGY: str = os.environ['FEDERATED_STRATEGY']
MU_FEDPROX = os.environ["MU_FEDPROX"]
FEDAVGM_SERVER_FL = os.environ["FEDAVGM_SERVER_FL"]
FEDAVGM_SERVER_MOMENTUM = os.environ["FEDAVGM_SERVER_MOMENTUM"]


# Weighted average of the metric:
def wavg_metric(metrics):
    global FEDERATED_METRIC
    list_metrics = []
    try:
        list_metrics = ast.literal_eval(FEDERATED_METRIC)
    except ValueError:
        print("Only one metric has been entered.")
    if len(list_metrics) == 0:
        n = sum([i for i, _ in metrics])
        wavg_metric = sum([i * metric[FEDERATED_METRIC] / n for i, metric in metrics])
        return {FEDERATED_METRIC: wavg_metric}
    else:
        n = sum([i for i, _ in metrics])
        dict_metrics = {}
        for fed_metric in list_metrics:
            wavg_metric = sum([i * metric[fed_metric] / n for i, metric in metrics])
            dict_metrics[fed_metric] = wavg_metric
        return dict_metrics

if FEDERATED_STRATEGY == "Federated Averaging (FedAvg)" or FEDERATED_STRATEGY is None:
    strategy = fl.server.strategy.FedAvg(
        min_available_clients=FEDERATED_MIN_FIT_CLIENTS,
        min_fit_clients=FEDERATED_MIN_AVAILABLE_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )
elif FEDERATED_STRATEGY == "Federated Median (FedMedian)":
    strategy = fl.server.strategy.FedMedian(
        min_available_clients=FEDERATED_MIN_FIT_CLIENTS,
        min_fit_clients=FEDERATED_MIN_AVAILABLE_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )
elif FEDERATED_STRATEGY == "Federated Averaging with Momentum (FedAvgM)":
    FEDAVGM_SERVER_FL = float(FEDAVGM_SERVER_FL)
    FEDAVGM_SERVER_MOMENTUM = float(FEDAVGM_SERVER_MOMENTUM)
    strategy = fl.server.strategy.FedAvgM(
        min_available_clients=FEDERATED_MIN_FIT_CLIENTS,
        min_fit_clients=FEDERATED_MIN_AVAILABLE_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
        server_learning_rate=FEDAVGM_SERVER_FL,
        server_momentum=FEDAVGM_SERVER_MOMENTUM
    )
elif FEDERATED_STRATEGY == "FedProx strategy (FedProx)":
    MU_FEDPROX = float(MU_FEDPROX)
    strategy = fl.server.strategy.FedProx(
        min_available_clients=FEDERATED_MIN_FIT_CLIENTS,
        min_fit_clients=FEDERATED_MIN_AVAILABLE_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
        proximal_mu = MU_FEDPROX
    )
elif FEDERATED_STRATEGY == "Adaptive Federated Optimization (FedOpt)":
    model = tf.keras.models.load_model('initial_model.keras')
    initial_parameters = ndarrays_to_parameters(model.get_weights())
    strategy = fl.server.strategy.FedOpt(
        min_available_clients=FEDERATED_MIN_FIT_CLIENTS,
        min_fit_clients=FEDERATED_MIN_AVAILABLE_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
        initial_parameters = initial_parameters
    )
elif FEDERATED_STRATEGY == "Federated Optimization with Adam (FedAdam)":
    model = tf.keras.models.load_model('initial_model.keras')
    initial_parameters = ndarrays_to_parameters(model.get_weights())
    strategy = fl.server.strategy.FedAdam(
        min_available_clients=FEDERATED_MIN_FIT_CLIENTS,
        min_fit_clients=FEDERATED_MIN_AVAILABLE_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
        initial_parameters = initial_parameters
    )
elif FEDERATED_STRATEGY == "Adaptive Federated Optimization using Yogi (FedYogi)":
    model = tf.keras.models.load_model('initial_model.keras')
    initial_parameters = ndarrays_to_parameters(model.get_weights())
    strategy = fl.server.strategy.FedYogi(
        min_available_clients=FEDERATED_MIN_FIT_CLIENTS,
        min_fit_clients=FEDERATED_MIN_AVAILABLE_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
        initial_parameters = initial_parameters
    )

# Flower server:
fl.server.start_server(
    server_address="0.0.0.0:5000",
    config=fl.server.ServerConfig(num_rounds=FEDERATED_ROUNDS),
    strategy=strategy,
)
