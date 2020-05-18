import os
import requests
import time
from subprocess import call
import scipy.io as sio
import scipy.ndimage
import numpy as np
from basemap_func import shiftgrid, interp
from pyproj import Proj
from PIL import Image
from matplotlib import cm
import matplotlib._contour as _contour
import matplotlib as mpl

def _get_weight_target():
	if not os.path.exists('ICON_GLOBAL2WORLD_025_EASY'):
		r = requests.get('https://opendata.dwd.de/weather/lib/cdo/ICON_GLOBAL2WORLD_025_EASY.tar.bz2', stream=True)
		r.raise_for_status()
		with open('ICON_GLOBAL2WORLD_025_EASY.tar.bz2', 'wb') as fd:
			for block in r.iter_content(chunk_size=1024):
				fd.write(block)
		rt = call(['tar', 'xf', 'ICON_GLOBAL2WORLD_025_EASY.tar.bz2'])
		if rt != 0:
			raise "Error with tar"
		rt = call(['rm', 'ICON_GLOBAL2WORLD_025_EASY.tar.bz2'])
		if rt != 0:
			raise "Error with remove"
			
	targetfile = 'ICON_GLOBAL2WORLD_025_EASY/target_grid_world_025.txt'
	weightfile = 'ICON_GLOBAL2WORLD_025_EASY/weights_icogl2world_025.nc'
	return targetfile, weightfile

file_key = { 'temp': '2t', 'pressure': 'prmsl', 'geopotential': 'z' }

def get_weather_data(metric='temp', run='00', hours='000', level='500'):
	date = time.strftime("%Y%m%d", time.gmtime())
	filename = 'icon_global_'+date+run+'_'+hours+'_'+metric+'_'+level
	if not os.path.isfile(filename+'.nc'):
		url = 'https://opendata.dwd.de/weather/nwp/icon/grib/'+run
		if metric == 'temp':
			url += '/t_2m/icon_global_icosahedral_single-level_'+date+run+'_'+hours+'_T_2M.grib2.bz2'
		elif metric == 'pressure':
			url += '/pmsl/icon_global_icosahedral_single-level_'+date+run+'_'+hours+'_PMSL.grib2.bz2'
		elif metric == 'geopotential':
			url += '/fi/icon_global_icosahedral_pressure-level_'+date+run+'_'+hours+'_'+level+'_FI.grib2.bz2'
		else:
			raise NotImplementedError('Metric has not been implemented.')
		r = requests.get(url, stream=True)
		r.raise_for_status()
		with open(filename+'.grib2.bz2', 'wb') as fd:
			for block in r.iter_content(chunk_size=1024):
				fd.write(block)

		rt = call(['bzip2', '-d', filename+'.grib2.bz2'])
		if rt != 0:
			raise RuntimeError('Bzip2 failed.')
		rt = call(['cdo', '-f', 'nc', 'remap,'+targetfile+','+weightfile, filename+'.grib2', filename+'.nc'])
		if rt != 0:
			raise RuntimeError('CDO failed.')

def extractdata(filename, key):
    f = sio.netcdf_file(filename+'.nc')
    data = f.variables[key]
    if len(data.shape) == 3:
        data = np.array(data[0,:,:])
    elif len(data.shape) == 4:
        data = np.array(data[0,0,:,:])
    lons = np.array(f.variables['lon'][:])
    lats = np.array(f.variables['lat'][:])
    f.close()
    return (data, lats, lons)


def getimage(filename, key):
    data, lats, lons = extractdata(filename, key)
    data = data - data.min()
    data /= data.max()
    data, lons = shiftgrid(180., data, lons, start=False)

    p = Proj(init='epsg:3857')
    max_lat = np.rad2deg(2 * np.arctan(np.e**np.pi) - np.pi / 2)
    ll = p(-180, -max_lat)
    ur = p(180, max_lat)
    x_m, y_m = np.meshgrid(np.linspace(ll[0], ur[0], 1000, endpoint=True), np.linspace(ll[1], ur[1], 1000, endpoint=True))
    lon_out, lat_out = p(x_m, y_m, inverse=True)
    return interp(data, lons, lats, lon_out, lat_out)

def getcontour(filename, key, levels):
    data, lats, lons = extractdata(filename, key)
    data = data
    data, lons = shiftgrid(180., data, lons, start=False)
    data = scipy.ndimage.gaussian_filter(data, sigma=4, order=0)
    lons_m, lats_m = np.meshgrid(lons, lats)
    data = np.ma.asarray(data)
    data = np.ma.masked_invalid(data)
    _corner_mask = mpl.rcParams['contour.corner_mask']
    _mask = np.ma.getmask(data)
    generator = _contour.QuadContourGenerator(lats_m, lons_m, data, _mask,  _corner_mask, 0)
    contours = {}
    for level in levels:
        vertices = generator.create_contour(level)
        for i in range(len(vertices)):
            vertices[i] = vertices[i].tolist()
        contours[str(level)] = vertices
    return countours
