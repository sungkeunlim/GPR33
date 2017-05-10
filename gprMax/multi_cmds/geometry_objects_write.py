from ..exceptions import CmdInputError
from ..geometry_outputs import GeometryObjects


def create_geometry_objects_write(multicmds, G):
    # Geometry object(s) output
    cmdname = '#geometry_objects_write'
    if multicmds[cmdname] is not None:
        for cmdinstance in multicmds[cmdname]:
            tmp = cmdinstance.split()
            if len(tmp) != 7:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires exactly seven parameters')

            xs = G.calculate_coord('x', tmp[0])
            ys = G.calculate_coord('y', tmp[1])
            zs = G.calculate_coord('z', tmp[2])

            xf = G.calculate_coord('x', tmp[3])
            yf = G.calculate_coord('y', tmp[4])
            zf = G.calculate_coord('z', tmp[5])

            check_coordinates(xs, ys, zs, name='lower')
            check_coordinates(xf, yf, zf, name='upper')

            if xs >= xf or ys >= yf or zs >= zf:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the lower coordinates should be less than the upper coordinates')

            g = GeometryObjects(xs, ys, zs, xf, yf, zf, tmp[6])

            if G.messages:
                print('Geometry objects in the volume from {:g}m, {:g}m, {:g}m, to {:g}m, {:g}m, {:g}m, will be written to {}, with materials written to {}'.format(xs * G.dx, ys * G.dy, zs * G.dz, xf * G.dx, yf * G.dy, zf * G.dz, g.filename, g.materialsfilename))

            # Append the new GeometryView object to the geometry objects to write list
            G.geometryobjectswrite.append(g)
