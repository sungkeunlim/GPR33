from copy import deepcopy

from ..materials import Material
from ..exceptions import CmdInputError


def create_materials(multicmds, G):
    cmdname = '#material'
    if cmdname in multicmds:
        for params in multicmds[cmdname]:
            create_material(params, G)


def create_material(params, G):
    cmdname = '#material'
    tmp = params.split()
    es = '{}: {} '.format(cmdname, params)
    n = len(tmp)
    if n < 5:
        raise CmdInputError(es + 'requires five')
    if float(tmp[0]) < 0:
        raise CmdInputError(es + 'requires a positive value for static (DC) permittivity')
    if tmp[1] != 'inf':
        se = float(tmp[1])
        if se < 0:
            raise CmdInputError(es + 'requires a positive value for conductivity')
    else:
        se = float('inf')
    if float(tmp[2]) < 0:
        raise CmdInputError(es + 'requires a positive value for permeability')
    if float(tmp[3]) < 0:
        raise CmdInputError(es + 'requires a positive value for magnetic conductivity')
    if any(x.ID == tmp[4] for x in G.materials):
        raise CmdInputError(es + 'with ID {} already exists'.format(tmp[4]))

    # Create a new instance of the Material class material (start index after pec & free_space)
    m = Material(len(G.materials), tmp[4])
    # Relative permittivity
    m.er = float(tmp[0])
    # Conductivity
    m.se = se
    # Relative permeability
    m.mr = float(tmp[2])
    # Magnetic loss
    m.sm = float(tmp[3])

    if G.messages:
        print('Material {} with epsr={:g}, sig={:g} S/m; mur={:g}, sig*={:g} S/m created.'.format(m.ID, m.er, m.se, m.mr, m.sm))

    # Append the new material object to the materials list
    G.materials.append(m)

    # subgrids have different dl and dt therefore different fdtd coefficients
    # that must be handled.
    for sg in G.subgrids:
        m_copy = deepcopy(m)
        sg.materials.append(m_copy)
