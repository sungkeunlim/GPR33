import os

import h5py
from tqdm import tqdm

from ..exceptions import CmdInputError
from ..utilities import round_value
from ..input_cmds_file import check_cmd_names
from ..input_cmds_multiuse import process_multicmds

from ..geometry_primitives import build_voxels_from_array


def create_geometry_objects_read(tmp, G):

    if tmp[0] == '#geometry_objects_read:':
        if len(tmp) != 6:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires exactly five parameters')

        xs = round_value(float(tmp[1]) / G.dx)
        ys = round_value(float(tmp[2]) / G.dy)
        zs = round_value(float(tmp[3]) / G.dz)
        geofile = tmp[4]
        matfile = tmp[5]

        # See if material file exists at specified path and if not try input file directory
        if not os.path.isfile(matfile):
            matfile = os.path.abspath(os.path.join(G.inputdirectory, matfile))

        matstr = os.path.splitext(os.path.split(matfile)[1])[0]
        numexistmaterials = len(G.materials)

        # Read materials from file
        with open(matfile, 'r') as f:
            # Strip out any newline characters and comments that must begin with double hashes
            materials = [line.rstrip() + '{' + matstr + '}\n' for line in f if(not line.startswith('##') and line.rstrip('\n'))]

        # Check validity of command names
        singlecmdsimport, multicmdsimport, geometryimport = check_cmd_names(materials, checkessential=False)

        # Process parameters for commands that can occur multiple times in the model
        process_multicmds(multicmdsimport, G)

        # Update material type
        for material in G.materials:
            if material.numID >= numexistmaterials:
                if material.type:
                    material.type += ',\nimported'
                else:
                    material.type = 'imported'

        # See if geometry object file exists at specified path and if not try input file directory
        if not os.path.isfile(geofile):
            geofile = os.path.abspath(os.path.join(G.inputdirectory, geofile))

        # Open geometry object file and read/check spatial resolution attribute
        f = h5py.File(geofile, 'r')
        dx_dy_dz = f.attrs['dx, dy, dz']
        if round_value(dx_dy_dz[0] / G.dx) != 1 or round_value(dx_dy_dz[1] / G.dy) != 1 or round_value(dx_dy_dz[2] / G.dz) != 1:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires the spatial resolution of the geometry objects file to match the spatial resolution of the model')

        data = f['/data'][:]

        # Should be int16 to allow for -1 which indicates background, i.e.
        # don't build anything, but AustinMan/Woman maybe uint16
        if data.dtype != 'int16':
            data = data.astype('int16')

        # Look to see if rigid and ID arrays are present (these should be
        # present if the original geometry objects were written from gprMax)
        try:
            rigidE = f['/rigidE'][:]
            rigidH = f['/rigidH'][:]
            ID = f['/ID'][:]
            G.solid[xs:xs + data.shape[0], ys:ys + data.shape[1], zs:zs + data.shape[2]] = data + numexistmaterials
            G.rigidE[:, xs:xs + rigidE.shape[1], ys:ys + rigidE.shape[2], zs:zs + rigidE.shape[3]] = rigidE
            G.rigidH[:, xs:xs + rigidH.shape[1], ys:ys + rigidH.shape[2], zs:zs + rigidH.shape[3]] = rigidH
            G.ID[:, xs:xs + ID.shape[1], ys:ys + ID.shape[2], zs:zs + ID.shape[3]] = ID + numexistmaterials
            if G.messages:
                tqdm.write('Geometry objects from file {} inserted at {:g}m, {:g}m, {:g}m, with corresponding materials file {}.'.format(geofile, xs * G.dx, ys * G.dy, zs * G.dz, matfile))
        except KeyError:
            averaging = False
            build_voxels_from_array(xs, ys, zs, numexistmaterials, averaging, data, G.solid, G.rigidE, G.rigidH, G.ID)
            if G.messages:
                tqdm.write('Geometry objects from file (voxels only) {} inserted at {:g}m, {:g}m, {:g}m, with corresponding materials file {}.'.format(geofile, xs * G.dx, ys * G.dy, zs * G.dz, matfile))
