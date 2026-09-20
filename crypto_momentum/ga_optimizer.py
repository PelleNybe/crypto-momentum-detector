import pandas as pd
import numpy as np
import random
import logging
from typing import Dict, List, Tuple
from crypto_momentum.signal_generator import SignalGenerator
from crypto_momentum.backtester import Backtester

logger = logging.getLogger(__name__)


class GeneticOptimizer:
    def __init__(
        self,
        data: pd.DataFrame,
        population_size: int = 20,
        generations: int = 5,
        mutation_rate: float = 0.1,
        elite_size: int = 2,
    ):
        self.data = data
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size

        # Define gene boundaries
        self.param_bounds = {
            "rsi_buy_min": (20, 45),
            "rsi_buy_max": (55, 80),
            "rsi_sell_min": (20, 45),
            "rsi_sell_max": (55, 80),
            "atr_sl_multiplier": (1.0, 3.0),
            "atr_tp_multiplier": (1.5, 4.0),
        }

    def _create_random_individual(self) -> Dict[str, float]:
        """Creates a random chromosome (set of parameters)."""
        ind = {}
        for key, bounds in self.param_bounds.items():
            if "multiplier" in key:
                ind[key] = round(random.uniform(bounds[0], bounds[1]), 1)
            else:
                ind[key] = random.randint(bounds[0], bounds[1])

        # Enforce logical constraints
        if ind["rsi_buy_min"] >= ind["rsi_buy_max"]:
            ind["rsi_buy_min"] = ind["rsi_buy_max"] - 10
        if ind["rsi_sell_min"] >= ind["rsi_sell_max"]:
            ind["rsi_sell_min"] = ind["rsi_sell_max"] - 10

        return ind

    def _fitness(self, individual: Dict[str, float]) -> float:
        """Evaluates an individual by running a fast backtest."""
        # Generate signals
        sg = SignalGenerator(
            data=self.data,
            rsi_buy_min=individual["rsi_buy_min"],
            rsi_buy_max=individual["rsi_buy_max"],
            rsi_sell_min=individual["rsi_sell_min"],
            rsi_sell_max=individual["rsi_sell_max"],
            atr_sl_multiplier=individual["atr_sl_multiplier"],
            atr_tp_multiplier=individual["atr_tp_multiplier"],
        )
        signals_df = sg.generate_signals()

        # Run fast backtest (no MC simulations)
        bt = Backtester(
            data=signals_df,
            initial_balance=10000.0,
            mc_simulations=0,
        )
        results = bt.run()

        # Fitness is based primarily on Return %, but could be Sharpe or Profit Factor
        # Using Return % for simplicity, penalizing negative returns heavily
        return_pct = results.get("Return %", -100.0)
        return return_pct

    def _crossover(
        self, parent1: Dict[str, float], parent2: Dict[str, float]
    ) -> Dict[str, float]:
        """Breeds two parents to create a child using uniform crossover."""
        child = {}
        for key in self.param_bounds.keys():
            if random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]

        # Enforce constraints after crossover
        if child["rsi_buy_min"] >= child["rsi_buy_max"]:
            child["rsi_buy_min"] = child["rsi_buy_max"] - 10
        if child["rsi_sell_min"] >= child["rsi_sell_max"]:
            child["rsi_sell_min"] = child["rsi_sell_max"] - 10

        return child

    def _mutate(self, individual: Dict[str, float]) -> Dict[str, float]:
        """Randomly mutates genes in an individual."""
        mutated = individual.copy()
        for key, bounds in self.param_bounds.items():
            if random.random() < self.mutation_rate:
                if "multiplier" in key:
                    mutated[key] = round(random.uniform(bounds[0], bounds[1]), 1)
                else:
                    mutated[key] = random.randint(bounds[0], bounds[1])

        # Enforce constraints
        if mutated["rsi_buy_min"] >= mutated["rsi_buy_max"]:
            mutated["rsi_buy_min"] = mutated["rsi_buy_max"] - 10
        if mutated["rsi_sell_min"] >= mutated["rsi_sell_max"]:
            mutated["rsi_sell_min"] = mutated["rsi_sell_max"] - 10

        return mutated

    def run_optimization(self) -> Dict:
        """Runs the genetic algorithm over N generations."""
        if self.data is None or len(self.data) < 50:
            logger.warning("Not enough data to run Genetic Optimizer.")
            return {}

        logger.info(
            f"Starting GA Optimization: {self.generations} gens, pop {self.population_size}"
        )

        # 1. Initialize Population
        population = [
            self._create_random_individual() for _ in range(self.population_size)
        ]

        best_overall = None
        best_fitness_overall = -float("inf")
        history = []

        # 2. Evolution Loop
        for gen in range(self.generations):
            # Evaluate fitness
            fitness_scores = [(ind, self._fitness(ind)) for ind in population]

            # Sort by highest fitness
            fitness_scores.sort(key=lambda x: x[1], reverse=True)

            # Track best
            current_best, current_best_score = fitness_scores[0]
            if current_best_score > best_fitness_overall:
                best_fitness_overall = current_best_score
                best_overall = current_best.copy()

            logger.info(f"Gen {gen+1}: Best Fitness = {current_best_score:.2f}%")

            # Save history
            history.append(
                {
                    "Generation": gen + 1,
                    "Best_Fitness": current_best_score,
                    "Average_Fitness": sum(score for _, score in fitness_scores)
                    / len(fitness_scores),
                    "Best_Params": current_best,
                }
            )

            # Next generation
            new_population = []

            # Elitism: Keep top X individuals untouched
            elites = [ind for ind, score in fitness_scores[: self.elite_size]]
            new_population.extend(elites)

            # Selection & Crossover (Tournament Selection)
            while len(new_population) < self.population_size:
                # Select parents
                tournament1 = random.sample(fitness_scores, 3)
                parent1 = max(tournament1, key=lambda x: x[1])[0]

                tournament2 = random.sample(fitness_scores, 3)
                parent2 = max(tournament2, key=lambda x: x[1])[0]

                # Crossover
                child = self._crossover(parent1, parent2)

                # Mutation
                child = self._mutate(child)

                new_population.append(child)

            population = new_population

        logger.info(f"GA Complete. Best overall fitness: {best_fitness_overall:.2f}%")

        # Run a full backtest with the absolute best parameters to get all metrics
        sg = SignalGenerator(data=self.data, **best_overall)
        final_signals = sg.generate_signals()
        bt = Backtester(data=final_signals)
        final_results = bt.run()

        return {
            "best_parameters": best_overall,
            "best_fitness": best_fitness_overall,
            "history": history,
            "final_backtest": final_results,
        }
