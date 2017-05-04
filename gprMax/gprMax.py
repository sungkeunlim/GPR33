# Copyright (C) 2015-2017: The University of Edinburgh
#                 Authors: Craig Warren and Antonis Giannopoulos
#
# This file is part of gprMax.
#
# gprMax is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gprMax is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gprMax.  If not, see <http://www.gnu.org/licenses/>.

"""gprMax.gprMax: provides entry point main()."""

import argparse

from .utilities import logo
from .utilities import open_path_file
from .geometry_objects import write_scene
from .config import TopLevelConfig
from .simulations import create_simulation


def main():
    """This is the main function for gprMax."""
    # Print gprMax logo, version, and licencing/copyright information
    logo()

    # Parse command line arguments
    parser = argparse.ArgumentParser(prog='gprMax', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('inputfile', help='path to, and name of inputfile or file object')
    parser.add_argument('-n', default=1, type=int, help='number of times to run the input file, e.g. to create a B-scan')
    parser.add_argument('-task', type=int, help='task identifier (model number) for job array on Open Grid Scheduler/Grid Engine (http://gridscheduler.sourceforge.net/index.html)')
    parser.add_argument('-restart', type=int, help='model number to restart from, e.g. when creating B-scan')
    parser.add_argument('-mpi', type=int, help='number of MPI tasks, i.e. master + workers')
    parser.add_argument('--mpi-worker', action='store_true', default=False, help=argparse.SUPPRESS)
    parser.add_argument('-benchmark', action='store_true', default=False, help='flag to switch on benchmarking mode')
    parser.add_argument('--geometry-only', action='store_true', default=False, help='flag to only build model and produce geometry file(s)')
    parser.add_argument('--geometry-fixed', action='store_true', default=False, help='flag to not reprocess model geometry, e.g. for B-scans where the geometry is fixed')
    parser.add_argument('--write-processed', action='store_true', default=False, help='flag to write an input file after any Python code and include commands in the original input file have been processed')
    parser.add_argument('--opt-taguchi', action='store_true', default=False, help='flag to optimise parameters using the Taguchi optimisation method')
    parser.add_argument('--xdmf-output', action='store_true', default=False, help='store geometry view in XDMF Format')
    args = parser.parse_args()

    args.interface = 'cli'

    run_main(args)


def api(
    scene,
    n=1,
    task=None,
    restart=None,
    mpi=False,
    benchmark=False,
    geometry_only=False,
    geometry_fixed=False,
    write_processed=False,
    opt_taguchi=False,
    xdmf_output=False
):
    # Print gprMax logo, version, and licencing/copyright information
    logo()

    """If installed as a module this is the entry point."""

    fp = write_scene(scene)

    class ImportArguments:
        pass

    args = ImportArguments()

    args.inputfile = fp
    args.n = n
    args.task = task
    args.restart = restart
    args.mpi = mpi
    args.benchmark = benchmark
    args.geometry_only = geometry_only
    args.geometry_fixed = geometry_fixed
    args.write_processed = write_processed
    args.opt_taguchi = opt_taguchi
    args.xdmf_output = xdmf_output
    args.interface = 'api'

    run_main(args)


def run_main(args):
    """
    Top-level function that controls what mode of simulation
    (standard/optimsation/benchmark etc...) is run.

    Args:
        args (dict): Namespace with input arguments from command line or api.
    """
    with open_path_file(args.inputfile) as inputfile:

        config = TopLevelConfig(args, inputfile)      # Main configuration
        print(config.host_info)  # Print user system information

        sim = create_simulation(config)
        sim.run()   # Run the simulation
        print(sim)  # Print out some information about what happened
