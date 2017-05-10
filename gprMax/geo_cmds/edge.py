from ..exceptions import CmdInputError
from ..utilities import round_value

from gprMax.geometry_primitives import build_edge_x
from gprMax.geometry_primitives import build_edge_y
from gprMax.geometry_primitives import build_edge_z


def create_edge(tmp, G):
    if tmp[0] == '#edge:':
        if len(tmp) != 8:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires exactly seven parameters')

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

            material = next((x for x in G.materials if x.ID == tmp[7]), None)

            if not material:
                raise CmdInputError('Material with ID {} does not exist'.format(tmp[7]))

            # Check for valid orientations
            # x-orientated wire
            if xs != xf:
                if ys != yf or zs != zf:
                    raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the edge is not specified correctly')
                else:
                    for i in range(xs, xf):
                        build_edge_x(i, ys, zs, material.numID, G.rigidE, G.rigidH, G.ID)

            # y-orientated wire
            elif ys != yf:
                if xs != xf or zs != zf:
                    raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the edge is not specified correctly')
                else:
                    for j in range(ys, yf):
                        build_edge_y(xs, j, zs, material.numID, G.rigidE, G.rigidH, G.ID)

            # z-orientated wire
            elif zs != zf:
                if xs != xf or ys != yf:
                    raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the edge is not specified correctly')
                else:
                    for k in range(zs, zf):
                        build_edge_z(xs, ys, k, material.numID, G.rigidE, G.rigidH, G.ID)

            if G.messages:
                tqdm.write('Edge from {:g}m, {:g}m, {:g}m, to {:g}m, {:g}m, {:g}m of material {} created.'.format(xs * G.dx, ys * G.dy, zs * G.dz, xf * G.dx, yf * G.dy, zf * G.dz, tmp[7]))