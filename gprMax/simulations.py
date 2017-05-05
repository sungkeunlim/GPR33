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
import datetime
import os
import sys
from time import perf_counter

import numpy as np
import h5py

from .exceptions import GeneralError
from .model_build_run import run_model
from .utilities import get_terminal_width
from ._version import __version__


def create_simulation(config):
    """Fork into one of 3 operating modes"""
    if config.args.benchmark:
        sim = BenchmarkSim(config)         # Benchmarking simulation
    elif config.args.opt_taguchi:
        sim = TaguchiSim(config)           # Taguchi simulation
    else:
        sim = CPUSim(config)               # CPU simulation

    return sim


def time_sim(func):
    """Decorator to time simulation objects run time"""

    def func_wrapper(self):
        tsimstart = perf_counter()
        result = func(self)
        sim_time = perf_counter() - tsimstart
        self.sim_time = sim_time
        return result

    return func_wrapper


class Sim:

    def __init__(self, config):
        self.config = config
        self.sim_time = None

    @time_sim
    def run_mpi_sim(self, optparams=None):
        """
        Run mixed mode MPI/OpenMP simulation - MPI task farm for models with
        each model parallelised with OpenMP

        Args:
            args (dict): Namespace with command line arguments
            inputfile (object): File object for the input file.
            usernamespace (dict): Namespace that can be accessed by user in any
                    Python code blocks in input file.
            optparams (dict): Optional argument. For Taguchi optimisation it
                    provides the parameters to optimise and their values.
        """

        from mpi4py import MPI

        # Get name of processor/host
        name = MPI.Get_processor_name()

        args = self.config.args

        # Set range for number of models to run
        modelstart = args.restart if args.restart else 1
        modelend = modelstart + args.n
        self.config.modelend = modelend - 1

        # Number of workers and command line flag to indicate a spawned worker
        worker = '--mpi-worker'
        numberworkers = args.mpi - 1

        # Master process
        if worker not in sys.argv:

            print('MPI master rank (PID {}) on {} using {} workers'.format(os.getpid(), name, numberworkers))

            # Create a list of work
            worklist = []
            for model in range(modelstart, modelend):
                workobj = dict()
                workobj['currentmodelrun'] = model
                if optparams:
                    workobj['optparams'] = optparams
                worklist.append(workobj)
            # Add stop sentinels
            worklist += ([StopIteration] * numberworkers)

            # Spawn workers
            comm = MPI.COMM_WORLD.Spawn(sys.executable, args=['-m', 'gprMax', '-n', str(args.n)] + sys.argv[1::] + [worker], maxprocs=numberworkers)

            # Reply to whoever asks until done
            status = MPI.Status()
            for work in worklist:
                comm.recv(source=MPI.ANY_SOURCE, status=status)
                comm.send(obj=work, dest=status.Get_source())

            # Shutdown
            comm.Disconnect()

        # Worker process
        elif worker in sys.argv:

            # Connect to parent
            try:
                comm = MPI.Comm.Get_parent()  # get MPI communicator object
                rank = comm.Get_rank()        # rank of this process
            except:
                raise ValueError('Could not connect to parent')

            # Ask for work until stop sentinel
            for work in iter(lambda: comm.sendrecv(0, dest=0), StopIteration):
                currentmodelrun = work['currentmodelrun']
                self.config.currentmodelrun = currentmodelrun

                gpuinfo = ''
                print('MPI worker rank {} (PID {}) starting model {}/{}{} on {}'.format(rank, os.getpid(), currentmodelrun, numbermodelruns, gpuinfo, name))

                # If Taguchi optimistaion, add specific value for each parameter to
                # optimise for each experiment to user accessible namespace
                if 'optparams' in work:
                    optparams = work['optparams']
                    tmp = {}
                    tmp.update((key, value[currentmodelrun - 1]) for key, value in optparams.items())
                    self.config.usernamespace.update({'optparams': tmp})

                run_model(self.config)

            # Shutdown
            comm.Disconnect()

    def __str__(self):
        s = '\n=== Simulation completed in [HH:MM:SS]: {}'
        s = s.format(datetime.timedelta(seconds=self.sim_time))
        s = '{} {}\n'.format(s, '=' * (get_terminal_width() - 1 - len(s)))
        return s


class TaguchiSim(Sim):
    """Special case for MPI spawned workers - they do not need to enter
    the Taguchi optimisation mode"""

    def __init__(self, config):
        super().__init__(config)
        if config.args.mpi_worker:
            self.run_mpi_sim(config)
        else:
            from gprMax.optimisation_taguchi import run_opt_sim
            run_opt_sim(config)


class CPUSim(Sim):
    """Mixed mode MPI with OpenMP or CUDA - MPI task farm for models
    with each model parallelised with OpenMP (CPU) or CUDA (GPU)"""

    def __init__(self, config):
        super().__init__(config)
        args = config.args
        if args.mpi:
            if args.n == 1:
                er = ("MPI is not beneficial when there is only one model"
                      "to run")
                raise GeneralError(er)
            if args.task:
                er2 = 'MPI cannot be combined with job array mode'
                raise GeneralError(er2)
            self.type = 'mpi'
        # Standard behaviour - models run serially with each model parallelised
        # with OpenMP (CPU) or CUDA (GPU)
        else:
            er3 = 'Job array and restart modes cannot be used together'
            if args.task and args.restart:
                raise GeneralError(er3)
            self.type = 'std'

    def run(self):
        if self.type == 'std':
            self.run_std_sim()
        else:
            self.run_mpi_sim()

    def model_start_end(self):
        args = self.config.args
        # Set range for number of models to run
        if args.task:
            # Job array feeds args.n number of single tasks
            modelstart = args.task
            modelend = args.task + 1
        elif args.restart:
            modelstart = args.restart
            modelend = modelstart + args.n
        else:
            modelstart = 1
            modelend = modelstart + args.n

        return (modelstart, modelend)

    @time_sim
    def run_std_sim(self, optparams=None):
        """
        Run standard simulation - models are run one after another and each
        model is parallelised with OpenMP
        """
        config = self.config
        modelstart, modelend = self.model_start_end()

        config.n_models = modelend - 1

        from .config import ModelConfig

        for model_number in range(config.n_models):

            model_config = ModelConfig(config.inputfile, model_number,
                                       config.n_models)
            config.model_config = model_config
            config.model_number = model_number

            # If Taguchi optimistaion, add specific value for each parameter to
            # optimise for each experiment to user accessible namespace
            if optparams:
                tmp = {}
                tmp.update((key, value[currentmodelrun - 1]) for key, value in optparams.items())
                config.usernamespace.update({'optparams': tmp})

            run_model(config)

        return None


class BenchmarkSim(Sim):

    def __init__(self, config):
        super().__init__(config)

    def calc_threads_per_sim(self):
        # Number of CPU threads to benchmark - start from single thread and
        # double threads until maximum number of physical cores
        threads = 1
        maxthreads = self.config.host_info.physicalcores
        maxthreadspersocket = maxthreads / self.config.host_info.sockets
        cputhreads = np.array([], dtype=np.int32)
        while threads < maxthreadspersocket:
            cputhreads = np.append(cputhreads, int(threads))
            threads *= 2
        # Check for system with only single thread
        if cputhreads.size == 0:
            cputhreads = np.append(cputhreads, threads)
        # Add maxthreadspersocket and maxthreads if necessary
        if cputhreads[-1] != maxthreadspersocket:
            cputhreads = np.append(cputhreads, int(maxthreadspersocket))
        if cputhreads[-1] != maxthreads:
            cputhreads = np.append(cputhreads, int(maxthreads))
        cputhreads = cputhreads[::-1]

        return cputhreads

    @time_sim
    def run(self):

        cpu_threads = self.calc_threads_per_sim()
        number_model_runs = len(cpu_threads)
        cputimes = []

        self.config.usernamespace['number_model_runs'] = number_model_runs
        self.config.modelend = number_model_runs

        for i, n_threads in enumerate(cpu_threads):
            self.config.currentmodelrun = i + 1
            os.environ['OMP_NUM_THREADS'] = str(n_threads)
            cputimes.append(run_model(self.config))

        # Get model size (in cells) and number of iterations
        outputfile = os.path.splitext(self.config.args.inputfile)[0]
        if number_model_runs == 1:
            outputfile += '.out'
        else:
            outputfile += str(1) + '.out'

        f = h5py.File(outputfile, 'r')
        iterations = f.attrs['Iterations']
        numcells = f.attrs['nx, ny, nz']

        # Save number of threads and benchmarking times to NumPy archive
        np.savez(os.path.splitext(
                 self.config.inputfile.name)[0],
                 machineID=self.config.host_info.machineID_long,
                 gpuIDs=[],
                 cputhreads=cpu_threads,
                 cputimes=cputimes,
                 gputimes=[],
                 iterations=iterations,
                 numcells=numcells,
                 version=__version__)
