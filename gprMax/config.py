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

from .utilities import get_host_info
from .utilities import human_size

from .constants import c
from .constants import e0
from .constants import m0
from .constants import z0


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
        self.inputfile = inputfile
        self.currentmodelrun = None
        self.modelend = None
