from ..exceptions import CmdInputError
from ..materials import Material
from tqdm import tqdm


def create_dispersion_drude(multicmds, G):
    cmdname = '#add_dispersion_drude'
    if multicmds[cmdname] is not None:
        for cmdinstance in multicmds[cmdname]:
            tmp = cmdinstance.split()

            if len(tmp) < 5:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires at least five parameters')
            if int(tmp[0]) < 0:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires a positive value for number of poles')
            poles = int(tmp[0])
            materialsrequested = tmp[(3 * poles) + 1:len(tmp)]

            # Look up requested materials in existing list of material instances
            materials = [y for x in materialsrequested for y in G.materials if y.ID == x]

            if len(materials) != len(materialsrequested):
                notfound = [x for x in materialsrequested if x not in materials]
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' material(s) {} do not exist'.format(notfound))

            for material in materials:
                material.type = 'drude'
                material.poles = poles
                material.averagable = False
                for pole in range(1, 2 * poles, 2):
                    if float(tmp[pole]) > 0 and float(tmp[pole + 1]) > G.dt:
                        material.tau.append(float(tmp[pole]))
                        material.alpha.append(float(tmp[pole + 1]))
                    else:
                        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires positive values for the frequencies, and associated times that are greater than the time step for the model.')
                if material.poles > Material.maxpoles:
                    Material.maxpoles = material.poles

                if G.messages:
                    tqdm.write('Drude disperion added to {} with omega={} secs, and gamma={} secs created.'.format(material.ID, ', '.join('%4.3e' % tau for tau in material.tau), ', '.join('%4.3e' % alpha for alpha in material.alpha)))

