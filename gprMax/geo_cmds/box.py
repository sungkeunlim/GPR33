from tqdm import tqdm

from ..exceptions import CmdInputError
from ..materials import Material
from ..geometry_primitives import build_box
from ..utilities import round_value


def create_box(tmp, G):
    if tmp[0] == '#box:':
        if len(tmp) < 8:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires at least seven parameters')

        # Isotropic case with no user specified averaging
        elif len(tmp) == 8:
            materialsrequested = [tmp[7]]
            averagebox = G.averagevolumeobjects

        # Isotropic case with user specified averaging
        elif len(tmp) == 9:
            materialsrequested = [tmp[7]]
            if tmp[8].lower() == 'y':
                averagebox = True
            elif tmp[8].lower() == 'n':
                averagebox = False
            else:
                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires averaging to be either y or n')

        # Uniaxial anisotropic case
        elif len(tmp) == 10:
            materialsrequested = tmp[7:]

        else:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' too many parameters have been given')

        xs = round_value(float(tmp[1]) / G.dx)
        xf = round_value(float(tmp[4]) / G.dx)
        ys = round_value(float(tmp[2]) / G.dy)
        yf = round_value(float(tmp[5]) / G.dy)
        zs = round_value(float(tmp[3]) / G.dz)
        zf = round_value(float(tmp[6]) / G.dz)

        if xs < 0 or xs > G.nx:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower x-coordinate {:g}m is not within the model domain'.format(xs * G.dx))
        if xf < 0 or xf > G.nx:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper x-coordinate {:g}m is not within the model domain'.format(xf * G.dx))
        if ys < 0 or ys > G.ny:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower y-coordinate {:g}m is not within the model domain'.format(ys * G.dy))
        if yf < 0 or yf > G.ny:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper y-coordinate {:g}m is not within the model domain'.format(yf * G.dy))
        if zs < 0 or zs > G.nz:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower z-coordinate {:g}m is not within the model domain'.format(zs * G.dz))
        if zf < 0 or zf > G.nz:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper z-coordinate {:g}m is not within the model domain'.format(zf * G.dz))
        if xs >= xf or ys >= yf or zs >= zf:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower coordinates should be less than the upper coordinates')

        # Look up requested materials in existing list of material instances
        materials = [y for x in materialsrequested for y in G.materials if y.ID == x]

        if len(materials) != len(materialsrequested):
            notfound = [x for x in materialsrequested if x not in materials]
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' material(s) {} do not exist'.format(notfound))

        # Isotropic case
        if len(materials) == 1:
            averaging = materials[0].averagable and averagebox
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

        build_box(xs, xf, ys, yf, zs, zf, numID, numIDx, numIDy, numIDz, averaging, G.solid, G.rigidE, G.rigidH, G.ID)

        if G.messages:
            if averaging:
                dielectricsmoothing = 'on'
            else:
                dielectricsmoothing = 'off'
            tqdm.write('Box from {:g}m, {:g}m, {:g}m, to {:g}m, {:g}m, {:g}m of material(s) {} created, dielectric smoothing is {}.'.format(xs * G.dx, ys * G.dy, zs * G.dz, xf * G.dx, yf * G.dy, zf * G.dz, ', '.join(materialsrequested), dielectricsmoothing))
