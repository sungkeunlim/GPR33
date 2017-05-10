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
from time import perf_counter

from .fields_outputs import store_outputs
from .fields_updates import update_electric
from .fields_updates import update_magnetic
from .fields_updates import update_electric_dispersive_multipole_A
from .fields_updates import update_electric_dispersive_multipole_B
from .fields_updates import update_electric_dispersive_1pole_A
from .fields_updates import update_electric_dispersive_1pole_B
from .materials import Material
from .snapshots import write_snapshots


class CPUSolver:

    def __init__(self, G, iterations):
        """
        Solving using FDTD method on CPU. Parallelised using Cython (OpenMP)
        for electric and magnetic field updates, and PML updates.

        Args:
            currentmodelrun (int): Current model run number.
            modelend (int): Number of last model to run.
            G (class): Grid class instance - holds essential parameters
            describing the model.

        Returns:
            tsolve (float): Time taken to execute solving
        """
        self.G = G
        self.iterations = iterations

    def update_magnetic(self):
        # Update magnetic field components
        G = self.G

        update_magnetic(G.nx, G.ny, G.nz, G.nthreads, G.updatecoeffsH,
                        G.ID, G.Ex, G.Ey, G.Ez, G.Hx, G.Hy, G.Hz)

        # Update magnetic field components with the PML correction
        for pml in G.pmls:
            pml.update_magnetic(G)

        # Update magnetic field components from sources
        for source in G.transmissionlines + G.magneticdipoles:
            source.update_magnetic(G.iteration, G.updatecoeffsH, G.ID, G.Hx,
                                   G.Hy, G.Hz, G)

    def update_electric(self):
        G = self.G

        # All materials are non-dispersive so do standard update
        if Material.maxpoles == 0:
            update_electric(G.nx, G.ny, G.nz, G.nthreads, G.updatecoeffsE,
                            G.ID, G.Ex, G.Ey, G.Ez, G.Hx, G.Hy, G.Hz)
        # Do 1st part of dispersive update. it is split into two parts as it
        # requires present and updated electric field values).
        elif Material.maxpoles == 1:
            update_electric_dispersive_1pole_A(G.nx,
                                               G.ny,
                                               G.nz,
                                               G.nthreads,
                                               G.updatecoeffsE,
                                               G.updatecoeffsdispersive,
                                               G.ID,
                                               G.Tx,
                                               G.Ty,
                                               G.Tz,
                                               G.Ex,
                                               G.Ey,
                                               G.Ez,
                                               G.Hx,
                                               G.Hy,
                                               G.Hz)
        elif Material.maxpoles > 1:
            update_electric_dispersive_multipole_A(G.nx,
                                                   G.ny,
                                                   G.nz,
                                                   G.nthreads,
                                                   Material.maxpoles,
                                                   G.updatecoeffsE,
                                                   G.updatecoeffsdispersive,
                                                   G.ID,
                                                   G.Tx,
                                                   G.Ty,
                                                   G.Tz,
                                                   G.Ex,
                                                   G.Ey,
                                                   G.Ez,
                                                   G.Hx,
                                                   G.Hy,
                                                   G.Hz)

        # Update electric field components with the PML correction
        for pml in G.pmls:
            pml.update_electric(G)

        # Update electric field components from sources
        # (update any Hertzian dipole sources last)
        sources = G.voltagesources + G.transmissionlines + G.hertziandipoles
        for source in sources:
            source.update_electric(G.iteration, G.updatecoeffsE,
                                   G.ID, G.Ex, G.Ey, G.Ez, G)

        # Do 2nd part of dispersive update. it is split into two parts as it
        # requires present and updated electric field values).Therefore it can
        # only be completely updated after the electric field has been updated
        # by the PML and source updates.
        if Material.maxpoles == 1:
            update_electric_dispersive_1pole_B(G.nx,
                                               G.ny,
                                               G.nz,
                                               G.nthreads,
                                               G.updatecoeffsdispersive,
                                               G.ID,
                                               G.Tx,
                                               G.Ty,
                                               G.Tz,
                                               G.Ex,
                                               G.Ey,
                                               G.Ez)
        elif Material.maxpoles > 1:
            update_electric_dispersive_multipole_B(G.nx,
                                                   G.ny,
                                                   G.nz,
                                                   G.nthreads,
                                                   Material.maxpoles,
                                                   G.updatecoeffsdispersive,
                                                   G.ID,
                                                   G.Tx,
                                                   G.Ty,
                                                   G.Tz,
                                                   G.Ex,
                                                   G.Ey,
                                                   G.Ez)

    def store_output_step(self):
        G = self.G
        store_outputs(G.iteration, G.Ex, G.Ey, G.Ez, G.Hx, G.Hy, G.Hz, G)

    def solve(self):
        """
        Solving using FDTD method on CPU. Parallelised using Cython (OpenMP)
        for electric and magnetic field updates, and PML updates.

            Args:
                currentmodelrun (int): Current model run number.
                modelend (int): Number of last model to run.
                G (class): Grid class instance - holds essential parameters
                describing the model.

            Returns:
                tsolve (float): Time taken to execute solving
        """

        tsolvestart = perf_counter()

        for iteration in self.iterations:

            self.G.iteration = iteration

            # Store field component values for every receiver and transmission
            # line
            self.store_output_step()
            write_snapshots(self.G)
            self.update_magnetic()
            self.update_electric()

        tsolve = perf_counter() - tsolvestart
        return tsolve

