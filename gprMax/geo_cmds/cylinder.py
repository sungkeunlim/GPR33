import numpy as np
from tqdm import tqdm

from ..exceptions import CmdInputError
from ..geometry_primitives import build_cylinder
from ..utilities import round_value
from ..materials import Material


def create_cylinder(tmp, G):

    if tmp[0] == '#cylinder:':
        if len(tmp) < 9:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires at least eight parameters')

        # Isotropic case with no user specified averaging
        elif len(tmp) == 9:
            materialsrequested = [tmp[8]]
            averagecylinder = G.averagevolumeobjects

        # Isotropic case with user specified averaging
        elif len(tmp) == 10:
            materialsrequested = [tmp[8]]
            if tmp[9].lower() == 'y':
                averagecylinder = True
            elif tmp[9].lower() == 'n':
                averagecylinder = False
            else:
                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires averaging to be either y or n')

        # Uniaxial anisotropic case
        elif len(tmp) == 11:
            materialsrequested = tmp[8:]

        else:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' too many parameters have been given')

        x1 = round_value(float(tmp[1]) / G.dx) * G.dx
        y1 = round_value(float(tmp[2]) / G.dy) * G.dy
        z1 = round_value(float(tmp[3]) / G.dz) * G.dz
        x2 = round_value(float(tmp[4]) / G.dx) * G.dx
        y2 = round_value(float(tmp[5]) / G.dy) * G.dy
        z2 = round_value(float(tmp[6]) / G.dz) * G.dz
        r = float(tmp[7])

        if r <= 0:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the radius {:g} should be a positive value.'.format(r))

        # Look up requested materials in existing list of material instances
        materials = [y for x in materialsrequested for y in G.materials if y.ID == x]

        if len(materials) != len(materialsrequested):
            notfound = [x for x in materialsrequested if x not in materials]
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' material(s) {} do not exist'.format(notfound))

        # Isotropic case
        if len(materials) == 1:
            averaging = materials[0].averagable and averagecylinder
            numID = numIDx = numIDy = numIDz = materials[0].numID

        # Uniaxial anisotropic case
        elif len(materials) == 3:
            averaging = False
            numIDx = materials[0].numID
            numIDy = materials[1].numID
            numIDz = materials[2].numID
            requiredID = materials[0].ID + '+' + materials[1].ID + '+' + materials[2].ID
            averagedmaterial = [x for x in G.materials if x.ID == requiredID]
            if averagedmaterial:
                numID = averagedmaterial.numID
            else:
                numID = len(G.materials)
                m = Material(numID, requiredID)
                m.type = 'dielectric-smoothed'
                # Create dielectric-smoothed constituents for material
                m.er = np.mean((materials[0].er, materials[1].er, materials[2].er), axis=0)
                m.se = np.mean((materials[0].se, materials[1].se, materials[2].se), axis=0)
                m.mr = np.mean((materials[0].mr, materials[1].mr, materials[2].mr), axis=0)
                m.sm = np.mean((materials[0].mr, materials[1].mr, materials[2].mr), axis=0)

                # Append the new material object to the materials list
                G.materials.append(m)

        build_cylinder(x1, y1, z1, x2, y2, z2, r, G.dx, G.dy, G.dz, numID, numIDx, numIDy, numIDz, averaging, G.solid, G.rigidE, G.rigidH, G.ID)

        if G.messages:
            if averaging:
                dielectricsmoothing = 'on'
            else:
                dielectricsmoothing = 'off'
            tqdm.write('Cylinder with face centres {:g}m, {:g}m, {:g}m and {:g}m, {:g}m, {:g}m, with radius {:g}m, of material(s) {} created, dielectric smoothing is {}.'.format(x1, y1, z1, x2, y2, z2, r, ', '.join(materialsrequested), dielectricsmoothing))
