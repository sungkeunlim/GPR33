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
from .multi_cmds.rx import create_receivers
from .multi_cmds.hertzian_dipole import create_hertzian_dipoles
from .multi_cmds.subgrid import create_subgrids
from .multi_cmds.voltage_source import create_voltage_sources
from .multi_cmds.material import create_materials
from .multi_cmds.snapshots import create_snapshots
from .multi_cmds.geometry_view import create_geometry_views
from .multi_cmds.magnetic_dipole import create_magnetic_dipoles
from .multi_cmds.transmission_line import create_transmission_lines
from .multi_cmds.waveform import create_waveforms
from .multi_cmds.receiver_array import create_receiver_arrays
from .multi_cmds.dispersion_debye import create_dispersion_debye
from .multi_cmds.dispersion_lorentz import create_dispersion_lorentz
from .multi_cmds.dispersion_drude import create_dispersion_drude
from .multi_cmds.soil_peplinski import create_soil_peplinski
from .multi_cmds.geometry_objects_write import create_geometry_objects_write
from .multi_cmds.pml_cfs import create_pml_cfs


def process_multicmds(multicmds, G):
    """
    Checks the validity of command parameters and creates instances of
        classes of parameters.

    Args:
        multicmds (dict): Commands that can have multiple instances in the
        model.
        G (class): Grid class instance - holds essential parameters describing
        the model.
    """

    create_subgrids(multicmds, G)
    create_waveforms(multicmds, G)
    create_voltage_sources(multicmds, G)
    create_hertzian_dipoles(multicmds, G)
    create_magnetic_dipoles(multicmds, G)
    create_transmission_lines(multicmds, G)
    create_receivers(multicmds, G)
    create_receiver_arrays(multicmds, G)
    create_snapshots(multicmds, G)
    create_materials(multicmds, G)
    create_dispersion_debye(multicmds, G)
    create_dispersion_lorentz(multicmds, G)
    create_dispersion_drude(multicmds, G)
    create_soil_peplinski(multicmds, G)
    create_geometry_views(multicmds, G)
    create_geometry_objects_write(multicmds, G)
    create_pml_cfs(multicmds, G)
