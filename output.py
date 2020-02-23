import scipy.io as sio
import numpy as np
from PIL import Image
from matplotlib import cm
from pyproj import Proj
from mpl_toolkits.basemap import shiftgrid, interp

f = sio.netcdf_file("icon_global_icosahedral_single-level_2018111000_000_T_2M.nc")
data = f.variables['2t']
data = data[0,0,:,:]
data = data - data.min()
data /= data.max()
lons = np.array(f.variables['lon'][:])
lats = np.array(f.variables['lat'][:])
f.close()

data, lons = shiftgrid(180., data, lons, start=False)

p = Proj(init='epsg:3857')
max_lat = np.rad2deg(2 * np.arctan(np.e**np.pi) - np.pi / 2)
ll = p(-180, -max_lat)
ur = p(180, max_lat)
x_m, y_m = np.meshgrid(np.linspace(ll[0], ur[0], 1000, endpoint=True), np.linspace(ll[1], ur[1], 1000, endpoint=True))
lon_out, lat_out = p(x_m, y_m, inverse=True)
dataout = interp(data, lons, lats, lon_out, lat_out)
Image.fromarray(cm.jet(dataout[::-1], bytes=True)).save('output.png')
