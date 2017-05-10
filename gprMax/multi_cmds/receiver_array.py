from ..exceptions import CmdInputError
from ..receivers import Rx
from .common import check_coordinates


def create_receiver_arrays(multicmds, G):
    # Receiver array
    cmdname = '#rx_array'
    if multicmds[cmdname] is not None:
        for cmdinstance in multicmds[cmdname]:
            tmp = cmdinstance.split()
            if len(tmp) != 9:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires exactly nine parameters')

            xs = G.calculate_coord('x', tmp[0])
            ys = G.calculate_coord('y', tmp[1])
            zs = G.calculate_coord('z', tmp[2])

            xf = G.calculate_coord('x', tmp[3])
            yf = G.calculate_coord('y', tmp[4])
            zf = G.calculate_coord('z', tmp[5])

            dx = G.calculate_coord('x', tmp[6])
            dy = G.calculate_coord('y', tmp[7])
            dz = G.calculate_coord('z', tmp[8])

            check_coordinates(xs, ys, zs, name='lower')
            check_coordinates(xf, yf, zf, name='upper')

            if xcoord < G.pmlthickness['x0'] or xcoord > G.nx - G.pmlthickness['xmax'] or ycoord < G.pmlthickness['y0'] or ycoord > G.ny - G.pmlthickness['ymax'] or zcoord < G.pmlthickness['z0'] or zcoord > G.nz - G.pmlthickness['zmax']:
                print(Fore.RED + "WARNING: '" + cmdname + ': ' + ' '.join(tmp) + "'" + ' sources and receivers should not normally be positioned within the PML.' + Style.RESET_ALL)
            if xs > xf or ys > yf or zs > zf:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the lower coordinates should be less than the upper coordinates')
            if dx < 0 or dy < 0 or dz < 0:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the step size should not be less than zero')
            if dx < G.dx:
                if dx == 0:
                    dx = 1
                else:
                    raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the step size should not be less than the spatial discretisation')
            if dy < G.dy:
                if dy == 0:
                    dy = 1
                else:
                    raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the step size should not be less than the spatial discretisation')
            if dz < G.dz:
                if dz == 0:
                    dz = 1
                else:
                    raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the step size should not be less than the spatial discretisation')

            if G.messages:
                print('Receiver array {:g}m, {:g}m, {:g}m, to {:g}m, {:g}m, {:g}m with steps {:g}m, {:g}m, {:g}m'.format(xs * G.dx, ys * G.dy, zs * G.dz, xf * G.dx, yf * G.dy, zf * G.dz, dx * G.dx, dy * G.dy, dz * G.dz))

            for x in range(xs, xf + 1, dx):
                for y in range(ys, yf + 1, dy):
                    for z in range(zs, zf + 1, dz):
                        r = Rx()
                        r.xcoord = x
                        r.ycoord = y
                        r.zcoord = z
                        r.xcoordorigin = x
                        r.ycoordorigin = y
                        r.zcoordorigin = z
                        r.ID = r.__class__.__name__ + '(' + str(x) + ',' + str(y) + ',' + str(z) + ')'
                        for key in Rx.defaultoutputs:
                            r.outputs[key] = np.zeros(G.iterations, dtype=floattype)
                        if G.messages:
                            print('  Receiver at {:g}m, {:g}m, {:g}m with output component(s) {} created.'.format(r.xcoord * G.dx, r.ycoord * G.dy, r.zcoord * G.dz, ', '.join(r.outputs)))
                        G.rxs.append(r)
