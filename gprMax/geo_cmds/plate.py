import tqdm

from ..exceptions import CmdInputError
from ..geometry_primitives import build_face_yz
from ..geometry_primitives import build_face_xz
from ..geometry_primitives import build_face_xy
from gprMax.utilities import round_value


def create_plate(tmp, G):

    if tmp[0] == '#plate:':
        if len(tmp) < 8:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires at least seven parameters')

        # Isotropic case
        elif len(tmp) == 8:
            materialsrequested = [tmp[7]]

        # Anisotropic case
        elif len(tmp) == 9:
            materialsrequested = [tmp[7:]]

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
        if xs > xf or ys > yf or zs > zf:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower coordinates should be less than the upper coordinates')

        # Check for valid orientations
        if xs == xf:
            if ys == yf or zs == zf:
                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the plate is not specified correctly')

        elif ys == yf:
            if xs == xf or zs == zf:
                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the plate is not specified correctly')

        elif zs == zf:
            if xs == xf or ys == yf:
                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the plate is not specified correctly')

        else:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the plate is not specified correctly')

        # Look up requested materials in existing list of material instances
        materials = [y for x in materialsrequested for y in G.materials if y.ID == x]

        if len(materials) != len(materialsrequested):
            notfound = [x for x in materialsrequested if x not in materials]
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' material(s) {} do not exist'.format(notfound))

        # yz-plane plate
        if xs == xf:
            # Isotropic case
            if len(materials) == 1:
                numIDx = numIDy = numIDz = materials[0].numID

            # Uniaxial anisotropic case
            elif len(materials) == 2:
                numIDy = materials[0].numID
                numIDz = materials[1].numID

            for j in range(ys, yf):
                for k in range(zs, zf):
                    build_face_yz(xs, j, k, numIDy, numIDz, G.rigidE, G.rigidH, G.ID)

        # xz-plane plate
        elif ys == yf:
            # Isotropic case
            if len(materials) == 1:
                numIDx = numIDy = numIDz = materials[0].numID

            # Uniaxial anisotropic case
            elif len(materials) == 2:
                numIDx = materials[0].numID
                numIDz = materials[1].numID

            for i in range(xs, xf):
                for k in range(zs, zf):
                    build_face_xz(i, ys, k, numIDx, numIDz, G.rigidE, G.rigidH, G.ID)

        # xy-plane plate
        elif zs == zf:
            # Isotropic case
            if len(materials) == 1:
                numIDx = numIDy = numIDz = materials[0].numID

            # Uniaxial anisotropic case
            elif len(materials) == 2:
                numIDx = materials[0].numID
                numIDy = materials[1].numID

            for i in range(xs, xf):
                for j in range(ys, yf):
                    build_face_xy(i, j, zs, numIDx, numIDy, G.rigidE, G.rigidH, G.ID)

        if G.messages:
            tqdm.write('Plate from {:g}m, {:g}m, {:g}m, to {:g}m, {:g}m, {:g}m of material(s) {} created.'.format(xs * G.dx, ys * G.dy, zs * G.dz, xf * G.dx, yf * G.dy, zf * G.dz, ', '.join(materialsrequested)))