import flwr as fl
from typing import Dict, List, Optional, Tuple, Union
from flwr.common import (
    EvaluateIns,
    EvaluateRes,
    FitIns,
    FitRes,
    MetricsAggregationFn,
    NDArrays,
    Parameters,
    Scalar,
    ndarrays_to_parameters,
    parameters_to_ndarrays,
)
from flwr.server.client_proxy import ClientProxy
from flwr.common.logger import log
from logging import WARNING
from functools import reduce
from scipy.optimize import minimize
from numpy.linalg import norm
import numpy as np

class FedAvgOpt(fl.server.strategy.FedAvg):

    def __repr__(self) -> str:
        """Compute a string representation of the strategy."""
        rep = f"FedAvgOpt(accept_failures={self.accept_failures})"
        return rep
    
    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        
        fedavg_parameters_aggregated, metrics_aggregated = super().aggregate_fit(
            server_round=server_round, results=results, failures=failures
        )
        if fedavg_parameters_aggregated is None:
            return None, {}

        weights_results = [(parameters_to_ndarrays(fit_res.parameters), fit_res.num_examples)
            for _, fit_res in results
        ]

        num_clients = len([num_examples for (_, num_examples) in results])
        x0 = [1] * num_clients
        value = minimize(min_aggregation, x0, method='Nelder-Mead', args=weights_results)
        alpha = value['x']
        print(alpha)
        alpha = np.array(alpha)

        # FedAvgOpt strategy
        num_examples_total = sum(num_examples for (_, num_examples) in weights_results)

        # Create a list of weights, each multiplied by the related number of examples
        weighted_weights = [
            [layer * num_examples * alpha_i for layer in weights] 
            for (weights, num_examples), alpha_i in zip(weights_results, alpha)
        ]   
    
        # Compute average weights of each layer
        weights_aggregated: NDArrays = [
            reduce(np.add, layer_updates) / num_examples_total
            for layer_updates in zip(*weighted_weights)
        ]

        parameters_aggregated = ndarrays_to_parameters(weights_aggregated)

        metrics_aggregated = {}
        if self.fit_metrics_aggregation_fn:
            fit_metrics = [(res.num_examples, res.metrics) for _, res in results]
            metrics_aggregated = self.fit_metrics_aggregation_fn(fit_metrics)
        elif server_round == 1:  # Only log this warning once
            log(WARNING, "No fit_metrics_aggregation_fn provided")

        return parameters_aggregated, metrics_aggregated
        

def min_aggregation(alpha, weights_results):
    weighted_weights = [
            [layer * num_examples * alpha_i for layer in weights] 
            for (weights, num_examples), alpha_i in zip(weights_results, alpha)
        ]  

    num_examples_total = sum(num_examples for (_, num_examples) in weights_results)
    
    wg: NDArrays = [
            reduce(np.add, layer_updates) / num_examples_total
            for layer_updates in zip(*weighted_weights)
        ]

    agg_weights = 0
    for wj, _ in weights_results:
        agg_weights += norm([norm(a - b)/norm(a + b) for a, b in zip(wg, wj)])
    
    return agg_weights
