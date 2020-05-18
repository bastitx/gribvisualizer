from flask import Flask, request, send_from_directory
from flask_cors import CORS
import requests
from subprocess import call
import scipy.io as sio
import scipy.ndimage
import numpy as np
from PIL import Image
from matplotlib import cm
from pyproj import Proj
from basemap_func import shiftgrid, interp
import matplotlib._contour as _contour
import matplotlib as mpl
import json
import time
import os.path
import dwd_loader

DEV = True
app = Flask(__name__)
CORS(app, send_wildcard=True)

@app.route('/<metric>/<form>')
def getdata(metric, form):
    contour_start = request.args.get('cstart', 80000, type=int)
	contour_end = request.args.get('cend', 108000, type=int)
	contour_step = request.args.get('cstep', 200, type=int)
    data = dwd_loader.get_weather_data()
    if form == 'image':
        dataout = dwd_loader.getimage()
        filename_out = filename+'.png'
        Image.fromarray(cm.jet(dataout[::-1], bytes=True)).save(filename_out)
        return send_from_directory('./', filename_out)
    elif form == 'contour':
        levels = np.arange(contour_start, contour_end, contour_step)
        contours = getcontour(filename, file_key[metric], levels)
        filename_out = filename+'.json'
        with open(filename_out, 'w') as outfile:
            json.dump(contours, outfile)
        return send_from_directory('./', filename_out)
    else:
        return 'error'
