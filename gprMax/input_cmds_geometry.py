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


from .config import create_geometry_iterable

from .geo_cmds.geometry_objects_read import create_geometry_objects_read
from .geo_cmds.edge import create_edge
from .geo_cmds.plate import create_plate
from .geo_cmds.triangle import create_triangle
from .geo_cmds.box import create_box
from .geo_cmds.cylinder import create_cylinder
from .geo_cmds.cylindrical_sector import create_cylindrical_sector
from .geo_cmds.sphere import create_sphere
from .geo_cmds.fractal_box import create_fractal_box


def process_geometrycmds(geometry, G):
    """
    This function checks the validity of command parameters, creates instances
    of classes of parameters, and calls functions to directly set arrays
    solid, rigid and ID.

    Args:
        geometry (list): Geometry commands in the model
    """

    # Disable progress bar if on Windows as it does not update properly
    # when messages are printed

    geo_it = create_geometry_iterable(geometry)

    for object in geo_it:

        tmp = object.split()

        create_geometry_objects_read(tmp, G)
        create_edge(tmp, G)
        create_plate(tmp, G)
        create_triangle(tmp, G)
        create_box(tmp, G)
        create_cylinder(tmp, G)
        create_cylindrical_sector(tmp, G)
        create_sphere(tmp, G)
        create_fractal_box(tmp, G)
