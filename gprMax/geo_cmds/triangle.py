import numpy as np

from ..exceptions import CmdInputError
from ..utilities import round_value
from ..materials import Material
from ..geometry_primitives import build_triangle


def create_triangle(tmp, G):

    if tmp[0] == '#triangle:':
        if len(tmp) < 12:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires at least eleven parameters')

        # Isotropic case with no user specified averaging
        elif len(tmp) == 12:
            materialsrequested = [tmp[11]]
            averagetriangularprism = G.averagevolumeobjects

        # Isotropic case with user specified averaging
        elif len(tmp) == 13:
            materialsrequested = [tmp[11]]
            if tmp[12].lower() == 'y':
                averagetriangularprism = True
            elif tmp[12].lower() == 'n':
                averagetriangularprism = False
            else:
                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires averaging to be either y or n')

        # Uniaxial anisotropic case
        elif len(tmp) == 14:
            materialsrequested = tmp[11:]

        else:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' too many parameters have been given')

        x1 = round_value(float(tmp[1]) / G.dx) * G.dx
        y1 = round_value(float(tmp[2]) / G.dy) * G.dy
        z1 = round_value(float(tmp[3]) / G.dz) * G.dz
        x2 = round_value(float(tmp[4]) / G.dx) * G.dx
        y2 = round_value(float(tmp[5]) / G.dy) * G.dy
        z2 = round_value(float(tmp[6]) / G.dz) * G.dz
        x3 = round_value(float(tmp[7]) / G.dx) * G.dx
        y3 = round_value(float(tmp[8]) / G.dy) * G.dy
        z3 = round_value(float(tmp[9]) / G.dz) * G.dz
        thickness = float(tmp[10])

        if x1 < 0 or x2 < 0 or x3 < 0 or x1 > G.nx or x2 > G.nx or x3 > G.nx:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the one of the x-coordinates is not within the model domain')
        if y1 < 0 or y2 < 0 or y3 < 0 or y1 > G.ny or y2 > G.ny or y3 > G.ny:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the one of the y-coordinates is not within the model domain')
        if z1 < 0 or z2 < 0 or z3 < 0 or z1 > G.nz or z2 > G.nz or z3 > G.nz:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the one of the z-coordinates is not within the model domain')
        if thickness < 0:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for thickness')

        # Check for valid orientations
        # yz-plane triangle
        if x1 == x2 and x2 == x3:
            normal = 'x'
        # xz-plane triangle
        elif y1 == y2 and y2 == y3:
            normal = 'y'
        # xy-plane triangle
        elif z1 == z2 and z2 == z3:
            normal = 'z'
        else:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the triangle is not specified correctly')

        # Look up requested materials in existing list of material instances
        materials = [y for x in materialsrequested for y in G.materials if y.ID == x]

        if len(materials) != len(materialsrequested):
            notfound = [x for x in materialsrequested if x not in materials]
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' material(s) {} do not exist'.format(notfound))

        if thickness > 0:
            # Isotropic case
            if len(materials) == 1:
                averaging = materials[0].average and averagetriangularprism
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
        else:
            averaging = False
            # Isotropic case
            if len(materials) == 1:
                numID = numIDx = numIDy = numIDz = materials[0].numID

            # Uniaxial anisotropic case
            elif len(materials) == 3:
                # numID requires a value but it will not be used
                numID = None
                numIDx = materials[0].numID
                numIDy = materials[1].numID
                numIDz = materials[2].numID

        build_triangle(x1, y1, z1, x2, y2, z2, x3, y3, z3, normal, thickness, G.dx, G.dy, G.dz, numID, numIDx, numIDy, numIDz, averaging, G.solid, G.rigidE, G.rigidH, G.ID)

        if G.messages:
            if thickness > 0:
                if averaging:
                    dielectricsmoothing = 'on'
                else:
                    dielectricsmoothing = 'off'
                tqdm.write('Triangle with coordinates {:g}m {:g}m {:g}m, {:g}m {:g}m {:g}m, {:g}m {:g}m {:g}m and thickness {:g}m of material(s) {} created, dielectric smoothing is {}.'.format(x1, y1, z1, x2, y2, z2, x3, y3, z3, thickness, ', '.join(materialsrequested), dielectricsmoothing))
            else:
                tqdm.write('Triangle with coordinates {:g}m {:g}m {:g}m, {:g}m {:g}m {:g}m, {:g}m {:g}m {:g}m of material(s) {} created.'.format(x1, y1, z1, x2, y2, z2, x3, y3, z3, ', '.join(materialsrequested)))
