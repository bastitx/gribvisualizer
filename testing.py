import scipy.io as sio
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cartopy.crs as ccrs
import numpy as np

f = sio.netcdf_file('icon_global_icosahedral_single-level_2018111500_000_T_2M.nc')
temp = np.array(f.variables['2t'][0,0,:,:] - 273.15)
lons = np.array(f.variables['lon'][:])
lats = np.array(f.variables['lat'][:])
f.close()
f = sio.netcdf_file('icon_global_icosahedral_single-level_2018111500_000_PMSL.nc')
pressure = np.array(f.variables['prmsl'][0,:,:] - 273.15)
f.close()

ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([-45, 55, 20, 80], ccrs.PlateCarree())
ax.coastlines('10m')
ax.contourf(lons, lats, temp, 60, transform=ccrs.PlateCarree(), cmap="jet")
ax.contour(lons, lats, pressure, 30, transform=ccrs.PlateCarree(), colors="black")

plt.show()
