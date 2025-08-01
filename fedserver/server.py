import os
import ast
import flwr as fl
import tensorflow as tf
from flwr.common import ndarrays_to_parameters
from flwr.server.strategy import DifferentialPrivacyServerSideFixedClipping
from flwr.server.strategy import MetricDifferentialPrivacyServerSideFixedClipping
from codecarbon import OfflineEmissionsTracker
from fedavgopt import FedAvgOpt


FEDERATED_ROUNDS: int = int(os.environ['FEDERATED_ROUNDS'])
FEDERATED_METRIC = os.environ['FEDERATED_METRIC']
FEDERATED_MIN_FIT_CLIENTS: int = int(os.environ["FEDERATED_MIN_FIT_CLIENTS"])
FEDERATED_MIN_AVAILABLE_CLIENTS: int = int(os.environ["FEDERATED_MIN_AVAILABLE_CLIENTS"])
FEDERATED_STRATEGY: str = os.environ['FEDERATED_STRATEGY']
MU_FEDPROX = os.environ["MU_FEDPROX"]
FEDAVGM_SERVER_FL = os.environ["FEDAVGM_SERVER_FL"]
FEDAVGM_SERVER_MOMENTUM = os.environ["FEDAVGM_SERVER_MOMENTUM"]
DP_BOOL: bool = os.environ['DP']
NOISE_MULTIPLIER = os.environ["NOISE_MULT"]
CLIPPING_NORM = os.environ["CLIP_NORM"]
SAMPLED_CLIENTS = os.environ['SAMPLED_CLIENTS']
METRIC_PRIVACY = os.environ['METRIC_PRIVACY']
CODE_CARBON: bool = os.environ['CODE_CARBON']
DATA_CENTER = os.environ['NOMAD_DC']
if DATA_CENTER == 'iisas-ai4eosc':
    COUNTRY = 'SVK'
else:
    COUNTRY = 'ESP'


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
    if FEDAVGM_SERVER_MOMENTUM > 0:
        model = tf.keras.models.load_model('initial_model.keras')
        initial_parameters = ndarrays_to_parameters(model.get_weights())
        strategy = fl.server.strategy.FedAvgM(
        min_available_clients=FEDERATED_MIN_FIT_CLIENTS,
        min_fit_clients=FEDERATED_MIN_AVAILABLE_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
        server_learning_rate=FEDAVGM_SERVER_FL,
        server_momentum=FEDAVGM_SERVER_MOMENTUM,
        initial_parameters = initial_parameters
    )
    else:
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
elif FEDERATED_STRATEGY == "FedAvgOpt":
    strategy = FedAvgOpt(
        min_available_clients=FEDERATED_MIN_CLIENTS,
        min_fit_clients=FEDERATED_MIN_CLIENTS,
        evaluate_metrics_aggregation_fn=wavg_metric,
    )

class AggregateEmissions(type(strategy)):
    def __init__(self, strategy):
        params = strategy.__dict__
        super().__init__(**params)
        
    def aggregate_fit(self, server_round, results, failures):
        server_tracker = OfflineEmissionsTracker(
            country_iso_code=COUNTRY, save_to_file=False
        )
        server_tracker.start()
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results, failures)

        # Emissions from clients
        client_emissions = [res.metrics["emissions"] for _, res in results if "emissions" in res.metrics]
        total_client_emissions = sum(client_emissions) if client_emissions else 0.0
        
        # Server-side emissions
        server_emissions = server_tracker.stop()
        
        total_emissions = total_client_emissions + server_emissions
        print(f"ROUND {server_round}. Total Carbon Emissions (server and clients): {total_emissions} kg CO2")

        return aggregated_parameters, {"total_emissions": total_emissions}


class AggregateEmissionsDP(DifferentialPrivacyServerSideFixedClipping):
    def __init__(self, strategy):
        super().__init__(
            strategy, 
            noise_multiplier=float(NOISE_MULTIPLIER), 
            clipping_norm=float(CLIPPING_NORM), 
            num_sampled_clients=SAMPLED_CLIENTS
        )
        
    def aggregate_fit(self, server_round, results, failures):
        server_tracker = OfflineEmissionsTracker(
            country_iso_code=COUNTRY, save_to_file=False
        )
        server_tracker.start()
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results, failures)

        # Emissions from clients
        client_emissions = [res.metrics["emissions"] for _, res in results if "emissions" in res.metrics]
        total_client_emissions = sum(client_emissions) if client_emissions else 0.0
        
        # Server-side emissions
        server_emissions = server_tracker.stop()
        
        total_emissions = total_client_emissions + server_emissions
        print(f"ROUND {server_round}. Total Carbon Emissions (server and clients): {total_emissions} kg CO2")

        return aggregated_parameters, {"total_emissions": total_emissions}


class AggregateEmissionsMDP(MetricDifferentialPrivacyServerSideFixedClipping):
    def __init__(self, strategy):
        super().__init__(
            strategy, 
            noise_multiplier=float(NOISE_MULTIPLIER), 
            clipping_norm=float(CLIPPING_NORM), 
            num_sampled_clients=SAMPLED_CLIENTS
        )
        
    def aggregate_fit(self, server_round, results, failures):
        server_tracker = OfflineEmissionsTracker(
            country_iso_code=COUNTRY, save_to_file=False
        )
        server_tracker.start()
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results, failures)

        # Emissions from clients
        client_emissions = [res.metrics["emissions"] for _, res in results if "emissions" in res.metrics]
        total_client_emissions = sum(client_emissions) if client_emissions else 0.0
        
        # Server-side emissions
        server_emissions = server_tracker.stop()
        
        total_emissions = total_client_emissions + server_emissions
        print(f"ROUND {server_round}. Total Carbon Emissions (server and clients): {total_emissions} kg CO2")

        return aggregated_parameters, {"total_emissions": total_emissions}

        
if DP_BOOL is True:
    SAMPLED_CLIENTS = int(SAMPLED_CLIENTS)
    if METRIC_PRIVACY is True:
        if CODE_CARBON is True:
            fl.server.start_server(
                server_address="0.0.0.0:5000",
                config=fl.server.ServerConfig(num_rounds=FEDERATED_ROUNDS),
                strategy=AggregateEmissionsMDP(strategy),
            )
        else:    
            mdp_strategy = MetricDifferentialPrivacyServerSideFixedClipping(
                strategy, noise_multiplier=float(NOISE_MULTIPLIER), clipping_norm=float(CLIPPING_NORM), num_sampled_clients=SAMPLED_CLIENTS
            )
            fl.server.start_server(
                server_address="0.0.0.0:5000",
                config=fl.server.ServerConfig(num_rounds=FEDERATED_ROUNDS),
                strategy=mdp_strategy,
            )
    else:
        if CODE_CARBON is True:
            fl.server.start_server(
                server_address="0.0.0.0:5000",
                config=fl.server.ServerConfig(num_rounds=FEDERATED_ROUNDS),
                strategy=AggregateEmissionsDP(strategy),
            )
        else:
            dp_strategy = DifferentialPrivacyServerSideFixedClipping(
                strategy, noise_multiplier=float(NOISE_MULTIPLIER), clipping_norm=float(CLIPPING_NORM), num_sampled_clients=SAMPLED_CLIENTS
            
            )
            fl.server.start_server(
                server_address="0.0.0.0:5000",
                config=fl.server.ServerConfig(num_rounds=FEDERATED_ROUNDS),
                strategy=dp_strategy,
            )
else:
    if CODE_CARBON is True:
        fl.server.start_server(
            server_address="0.0.0.0:5000",
            config=fl.server.ServerConfig(num_rounds=FEDERATED_ROUNDS),
            strategy=AggregateEmissions(strategy),
        )
    else:
        fl.server.start_server(
            server_address="0.0.0.0:5000",
            config=fl.server.ServerConfig(num_rounds=FEDERATED_ROUNDS),
            strategy=strategy,
        )
