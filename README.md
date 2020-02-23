## Python libraries required
- flask
- flask_cors
- requests
- scipy
- numpy
- pillow
- matplotlib
- pyproj
- cartopy

## Other requirements
Eccodes from https://confluence.ecmwf.int/display/ECC
CDO from https://code.mpimet.mpg.de/projects/cdo (CDO needs to be built with eccodes support)
Grid information file and weight files are automatically loaded. Readme: https://opendata.dwd.de/weather/lib/README.txt

## Old
Used to require basemap; took required functions and put them into basemap_func.py as basemap is deprecated but not all functions have been migrated to cartopy
