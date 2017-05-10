import numpy as np
import tqdm

from ..exceptions import CmdInputError
from ..materials import Material
from ..utilities import round_value
from ..geometry_primitives import build_sphere


def create_sphere(tmp, G):
    if tmp[0] == '#sphere:':
        if len(tmp) < 6:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires at least five parameters')

        # Isotropic case with no user specified averaging
        elif len(tmp) == 6:
            materialsrequested = [tmp[5]]
            averagesphere = G.averagevolumeobjects

        # Isotropic case with user specified averaging
        elif len(tmp) == 7:
            materialsrequested = [tmp[5]]
            if tmp[6].lower() == 'y':
                averagesphere = True
            elif tmp[6].lower() == 'n':
                averagesphere = False
            else:
                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires averaging to be either y or n')

        # Uniaxial anisotropic case
        elif len(tmp) == 8:
            materialsrequested = tmp[5:]

        else:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' too many parameters have been given')

        # Centre of sphere
        xc = round_value(float(tmp[1]) / G.dx)
        yc = round_value(float(tmp[2]) / G.dy)
        zc = round_value(float(tmp[3]) / G.dz)
        r = float(tmp[4])

        # Look up requested materials in existing list of material instances
        materials = [y for x in materialsrequested for y in G.materials if y.ID == x]

        if len(materials) != len(materialsrequested):
            notfound = [x for x in materialsrequested if x not in materials]
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' material(s) {} do not exist'.format(notfound))

        # Isotropic case
        if len(materials) == 1:
            averaging = materials[0].averagable and averagesphere
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

        build_sphere(xc, yc, zc, r, G.dx, G.dy, G.dz, numID, numIDx, numIDy, numIDz, averaging, G.solid, G.rigidE, G.rigidH, G.ID)

        if G.messages:
            if averaging:
                dielectricsmoothing = 'on'
            else:
                dielectricsmoothing = 'off'
            tqdm.write('Sphere with centre {:g}m, {:g}m, {:g}m, radius {:g}m, of material(s) {} created, dielectric smoothing is {}.'.format(xc * G.dx, yc * G.dy, zc * G.dz, r, ', '.join(materialsrequested), dielectricsmoothing))

