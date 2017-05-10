from .cpu_solvers import CPUSolver
from ..utilities import get_iterations


def create_solver(G, config):

    iterations = get_iterations(config, G)
    solver = CPUSolver(G, iterations)

    return solver
