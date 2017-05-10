import numpy as np
from tqdm import tqdm

from ..exceptions import CmdInputError
from ..materials import Material
from ..utilities import round_value
from ..geometry_primitives import build_cylindrical_sector


def create_cylindrical_sector(tmp, G):
    if tmp[0] == '#cylindrical_sector:':
        if len(tmp) < 10:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires at least nine parameters')

        # Isotropic case with no user specified averaging
        elif len(tmp) == 10:
            materialsrequested = [tmp[9]]
            averagecylindricalsector = G.averagevolumeobjects

        # Isotropic case with user specified averaging
        elif len(tmp) == 11:
            materialsrequested = [tmp[9]]
            if tmp[10].lower() == 'y':
                averagecylindricalsector = True
            elif tmp[10].lower() == 'n':
                averagecylindricalsector = False
            else:
                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires averaging to be either y or n')

        # Uniaxial anisotropic case
        elif len(tmp) == 12:
            materialsrequested = tmp[9:]

        else:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' too many parameters have been given')

        normal = tmp[1].lower()
        ctr1 = float(tmp[2])
        ctr2 = float(tmp[3])
        extent1 = float(tmp[4])
        extent2 = float(tmp[5])
        thickness = extent2 - extent1
        r = float(tmp[6])
        sectorstartangle = 2 * np.pi * (float(tmp[7]) / 360)
        sectorangle = 2 * np.pi * (float(tmp[8]) / 360)

        if normal != 'x' and normal != 'y' and normal != 'z':
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the normal direction must be either x, y or z.')
        if ctr1 < 0 or ctr2 < 0:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the coordinates of the centre of the circle are not within the model domain.')
        if normal == 'x' and (ctr1 > G.ny or ctr1 > G.nz or ctr2 > G.ny or ctr2 > G.nz):
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the coordinates of the centre of the circle are not within the model domain.')
        elif normal == 'y' and (ctr1 > G.nx or ctr1 > G.nz or ctr2 > G.nx or ctr2 > G.nz):
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the coordinates of the centre of the circle are not within the model domain.')
        elif normal == 'z' and (ctr1 > G.nx or ctr1 > G.ny or ctr2 > G.nx or ctr2 > G.ny):
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the coordinates of the centre of the circle are not within the model domain.')
        if r <= 0:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the radius {:g} should be a positive value.'.format(r))
        if sectorstartangle >= 2 * np.pi or sectorangle >= 2 * np.pi:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the starting angle and sector angle must be less than 360 degrees.')

        # Look up requested materials in existing list of material instances
        materials = [y for x in materialsrequested for y in G.materials if y.ID == x]

        if len(materials) != len(materialsrequested):
            notfound = [x for x in materialsrequested if x not in materials]
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' material(s) {} do not exist'.format(notfound))

        if thickness > 0:
            # Isotropic case
            if len(materials) == 1:
                averaging = materials[0].averagable and averagecylindricalsector
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

        # yz-plane cylindrical sector
        if normal == 'x':
            ctr1 = round_value(ctr1 / G.dy) * G.dy
            ctr2 = round_value(ctr2 / G.dz) * G.dz
            level = round_value(extent1 / G.dx)

        # xz-plane cylindrical sector
        elif normal == 'y':
            ctr1 = round_value(ctr1 / G.dx) * G.dx
            ctr2 = round_value(ctr2 / G.dz) * G.dz
            level = round_value(extent1 / G.dy)

        # xy-plane cylindrical sector
        elif normal == 'z':
            ctr1 = round_value(ctr1 / G.dx) * G.dx
            ctr2 = round_value(ctr2 / G.dy) * G.dy
            level = round_value(extent1 / G.dz)

        build_cylindrical_sector(ctr1, ctr2, level, sectorstartangle, sectorangle, r, normal, thickness, G.dx, G.dy, G.dz, numID, numIDx, numIDy, numIDz, averaging, G.solid, G.rigidE, G.rigidH, G.ID)

        if G.messages:
            if thickness > 0:
                if averaging:
                    dielectricsmoothing = 'on'
                else:
                    dielectricsmoothing = 'off'
                tqdm.write('Cylindrical sector with centre {:g}m, {:g}m, radius {:g}m, starting angle {:.1f} degrees, sector angle {:.1f} degrees, thickness {:g}m, of material(s) {} created, dielectric smoothing is {}.'.format(ctr1, ctr2, r, (sectorstartangle / (2 * np.pi)) * 360, (sectorangle / (2 * np.pi)) * 360, thickness, ', '.join(materialsrequested), dielectricsmoothing))
            else:
                tqdm.write('Cylindrical sector with centre {:g}m, {:g}m, radius {:g}m, starting angle {:.1f} degrees, sector angle {:.1f} degrees, of material(s) {} created.'.format(ctr1, ctr2, r, (sectorstartangle / (2 * np.pi)) * 360, (sectorangle / (2 * np.pi)) * 360, ', '.join(materialsrequested)))