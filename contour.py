import scipy.io as sio
import numpy as np
import matplotlib._contour as _contour
import matplotlib as mpl
from mpl_toolkits.basemap import shiftgrid
import json

f = sio.netcdf_file("icon_global_icosahedral_single-level_2018111000_000_T_2M.nc")
data = f.variables['2t']
data = data[0,0,:,:] - 273.15
lons = np.array(f.variables['lon'][:])
lats = np.array(f.variables['lat'][:])
f.close()

data, lons = shiftgrid(180., data, lons, start=False)

lons_m, lats_m = np.meshgrid(lons, lats)
data = np.ma.asarray(data)
data = np.ma.masked_invalid(data)
_corner_mask = mpl.rcParams['contour.corner_mask']
_mask = np.ma.getmask(data)
generator = _contour.QuadContourGenerator(lats_m, lons_m, data, _mask,  _corner_mask, 0)
vertices = generator.create_contour(25)
for i in range(len(vertices)):
    vertices[i] = vertices[i].tolist()
with open('contour.json', 'w') as outfile:
    json.dump(vertices, outfile)

