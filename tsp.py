"""
    solution by Giuseppe Salvi s287583
    tsp solution using 2-opt search algorithm
    https://pypi.org/project/py2opt/
    2-opt is a simple local search algorithm with a special swapping mechanism that suits
    well to solve the traveling salesman problem
"""
# Copyright © 2021 Giovanni Squillero <squillero@polito.it>
# Free for personal or classroom use; see 'LICENCE.md' for details.
# https://github.com/squillero/computational-intelligence

import logging
from math import sqrt
from typing import Any
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from py2opt.routefinder import RouteFinder


NUM_CITIES = 23
STEADY_STATE = 1000


class Tsp:

    def __init__(self, num_cities: int, seed: Any = None) -> None:
        if seed is None:
            seed = num_cities
        self._num_cities = num_cities
        self._graph = nx.DiGraph()
        np.random.seed(seed)
        for c in range(num_cities):
            self._graph.add_node(
                c, pos=(np.random.random(), np.random.random()))

        # initialize vector with names of the cities, in this case numbers
        self.cities_names = [i for i in range(num_cities)]
        # initialize matrix of distances between cities
        self.dist_mat = []

        for c in range(num_cities):
            distances = []
            for d in range(num_cities):
                distances.append(self.distance(c, d))
            self.dist_mat.append(distances)

    def distance(self, n1, n2) -> int:
        pos1 = self._graph.nodes[n1]['pos']
        pos2 = self._graph.nodes[n2]['pos']
        return round(1_000_000 / self._num_cities * sqrt((pos1[0] - pos2[0])**2 +
                                                         (pos1[1] - pos2[1])**2))

    def evaluate_solution(self, solution: np.array) -> float:
        total_cost = 0
        tmp = solution.tolist() + [solution[0]]
        for n1, n2 in (tmp[i:i + 2] for i in range(len(tmp) - 1)):
            total_cost += self.distance(n1, n2)
        return total_cost

    def plot(self, path: np.array = None) -> None:
        if path is not None:
            self._graph.remove_edges_from(list(self._graph.edges))
            tmp = path.tolist() + [path[0]]
            for n1, n2 in (tmp[i:i + 2] for i in range(len(tmp) - 1)):
                self._graph.add_edge(n1, n2)
        plt.figure(figsize=(12, 5))
        nx.draw(self._graph,
                pos=nx.get_node_attributes(self._graph, 'pos'),
                with_labels=True,
                node_color='pink')
        if path is not None:
            plt.title(f"Current path: {self.evaluate_solution(path):,}")
        plt.show()

    @property
    def graph(self) -> nx.digraph:
        return self._graph


def tweak(solution: np.array, *, pm: float = .1) -> np.array:
    new_solution = solution.copy()
    p = None
    while p is None or p < pm:
        i1 = np.random.randint(0, solution.shape[0])
        i2 = np.random.randint(0, solution.shape[0])
        temp = new_solution[i1]
        new_solution[i1] = new_solution[i2]
        new_solution[i2] = temp
        p = np.random.random()
    return new_solution


def main():

    problem = Tsp(NUM_CITIES)

    solution = np.array(range(NUM_CITIES))
    np.random.shuffle(solution)
    solution_cost = problem.evaluate_solution(solution)
    problem.plot(solution)
    print("first random solution")
    print(f"solution cost: {solution_cost}")

    # try to find the best solution using py2opt algorithm
    route_finder = RouteFinder(
        problem.dist_mat, problem.cities_names, iterations=5)
    solution_cost, solution = route_finder.solve()

    problem.plot(np.array(solution))
    print("best solution using 5 iterations")
    print(f"solution cost: {solution_cost}")

    # more iterations: better solution
    route_finder = RouteFinder(
        problem.dist_mat, problem.cities_names, iterations=100)
    solution_cost, solution = route_finder.solve()

    problem.plot(np.array(solution))
    print("best solution using 100 iterations")
    print(f"solution cost: {solution_cost}")


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    logging.getLogger().setLevel(level=logging.INFO)
    main()
