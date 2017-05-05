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
import os
import sys

from tqdm import tqdm
from colorama import init, Fore, Style

from .utilities import get_host_info
from .utilities import human_size
from .utilities import get_terminal_width

from .constants import c
from .constants import e0
from .constants import m0
from .constants import z0

init()


# parameter for single model

# model_number
# input file
# input file path
# input file directory
# output file
# output file directory

# TO HAVE PROGRESS BARS OR NOT
TQDM = True


def get_iterations(config, G):
    if TQDM:
        # Main FDTD solving functions for either CPU or GPU
        desc = 'Running simulation, model {}/{}'
        desc = desc.format(str(config.model_config.model_number + 1),
                           str(config.n_models))
        iterations = tqdm(
                          range(G.iterations),
                          desc=desc,
                          ncols=get_terminal_width() - 1,
                          file=sys.stdout,
                          disable=G.tqdmdisable)
    else:
        iterations = range(G.iterations)
    return iterations


class MetaFile():

    def __init__(self, f):
        self.file = f
        self.file_name = f.name
        self.file_path = os.path.abspath(f.name)
        self.file_path_no_ext = self.file_path.split('.')[0]
        self.file_directory = os.path.dirname(os.path.abspath(f.name))
        self.file_ext = self.file_name.split('.')[1]


class ModelConfig:

    def __init__(self, inputfile, model_number, number_of_models):

        self.inputfile = inputfile
        self.model_number = model_number
        self.number_of_models = number_of_models
        self.s = '\n--- Model {}/{}, input file: {}'
        self.format_input_s()

        # When we are running more than one model we label any output files
        # by the 0 index of the models + 1
        if number_of_models > 1:
            self.p_model_number = str(self.model_number + 1)
        else:
            self.p_model_number = ''

        self.outputfile_path = self.inputfile.file_path_no_ext + self.p_model_number + '.out'

    def format_input_s(self):
        self.inputfilestr = self.s.format(
            self.model_number, self.number_of_models, self.inputfile.file_name)

    def __str__(self):
        s = Fore.GREEN
        s += '{} {}\n'
        mod = '-' * (get_terminal_width() - 1 - len(self.inputfilestr))
        s = s.format(self.inputfilestr, mod)
        s += Style.RESET_ALL
        return s


class ModelRunFixed(ModelConfig):

    def __init__(self, inputfile, currentmodelrun, modelend):
        super().__init__(inputfile, currentmodelrun, modelend)
        self.s = ("\n--- Model {}/{}, input file (not re-processed, i.e."
                  "geometry fixed): {}"
                  )
        self.format_input_s()


class HostInfo():

    def __init__(self):
        # Create a readible host information
        host_info = get_host_info()
        hp = ', {} cores with Hyper-Threading'  # does support hyperthreading?
        if host_info['hyperthreading']:
            hp = host_info['logicalcores']
        else:
            hp = ''

        s = '\nHost: {}; {} x {} ({} cores{}); {} RAM; {}'
        s = s.format(
                     host_info['machineID'],
                     host_info['sockets'],
                     host_info['cpuID'],
                     host_info['physicalcores'],
                     hp,
                     human_size(host_info['ram'],
                                a_kilobyte_is_1024_bytes=True),
                     host_info['osversion'])

        # Create a readible Machine ID
        machineID_long = '{}; {} x {} ({} cores{}); {} RAM; {}'
        machineID_long = machineID_long.format(
            host_info['machineID'],
            host_info['sockets'],
            host_info['cpuID'],
            host_info['physicalcores'],
            hp,
            human_size(host_info['ram'], a_kilobyte_is_1024_bytes=True),
            host_info['osversion'])

        self.machineID_long = machineID_long

        for k, v in host_info.items():  # copy over host info to class attribs
            setattr(self, k, v)

        self.desc = s

    def __str__(self):
        return self.desc


class TopLevelConfig:

    def __init__(self, args, inputfile):
        self.args = args
        self.host_info = HostInfo()
        # Create a separate namespace that users can access in any
        # Python code blocks in the input file
        self.usernamespace = {
                            'c': c,
                            'e0': e0,
                            'm0': m0,
                            'z0': z0,
                            'number_model_runs': args.n,
                            'inputfile': os.path.abspath(inputfile.name)
        }
        # input file provided by the user with additional path info
        self.inputfile = MetaFile(inputfile)
        # Total number of model required to run
        self.n_models = args.n
        # 0 index of the model the simulation is/will run
        self.model_number = None
        # Configuration for the current running model
        self.model_config = None
