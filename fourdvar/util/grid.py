#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
======================================================================
DESCRIPTION



EXAMPLES


EXIT STATUS

AUTHOR

Michael Vossbeck <Michael.Vossbeck(at)Inversion-Lab.com> and Peter Rayner <prayner@unimelb.edu.au>

======================================================================
"""

import numpy as np
import netCDF4 as nc4

#-- local packages
from pkglog import PkgLogger
from area import area_on_earth


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#          GridMap
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class GridMap(object):

    def __init__(self):
        pass

    def setup_regular_grid(self, resolution, declat=False):
        self.dlon = resolution
        self.dlat = resolution
        #--
        nlon = int(360./self.dlon)
        nlat = int(180./self.dlat)

        #-- internally store grid-cell centre on full global coverage
        self.lon_ctrs = np.linspace(-180., 180., num=nlon, endpoint=False) + self.dlon/2.
        self.lon_ctrs = np.round(self.lon_ctrs,decimals=2)

        if declat:
            self.lat_ctrs = np.linspace(90., -90., num=nlat, endpoint=False) - self.dlat/2.
            self.lat_ctrs = np.round(self.lat_ctrs,decimals=2)
        else:
            self.lat_ctrs = np.linspace(-90., 90., num=nlat, endpoint=False) - self.dlat/2.
            self.lat_ctrs = np.round(self.lat_ctrs,decimals=2)

        #-- store area for grid-cell per zonal band
        dlon = np.ones((nlat,))*self.dlon
        lat_sb = self.lat_ctrs - self.dlat/2.
        lat_nb = self.lat_ctrs + self.dlat/2.
        self.area_vec = np.vectorize(area_on_earth)(dlon, lat_sb, lat_nb, ERmeter=6.371e6)

    def setup_grid_from_netcdf(self, ncfname):
        try:
            ncfp = nc4.Dataset(ncfname)
            msg = "population density will be read from file ***{}***".format(ncfname)
            PkgLogger.info(msg)
        except IOError:
            msg = "PopDensityDataMap: datafile ***{}*** could not be opened.".format(
                self.fname)
            raise RuntimeError(msg)

        #-- lon/lat
        lon_ = ncfp.variables['longitude'][:].astype(np.float64)
        lat_ = ncfp.variables['latitude'][:].astype(np.float64)

        #-- north-to-south?
        is_declat = (lat_[1]<lat_[0])

        msg = "detected grid dimensions (nlat,nlon)=({},{})".format(lat_.size,lon_.size)
        if is_declat:
            msg += " latitude is *decreasing* with index"
        PkgLogger.info(msg)

        #-- determine grid-width:
        #   we are expecting 0.1 Degree resolution, there is some (numerical) spread
        #   in the coordinate values, but these should at least equal out after rounding
        #   to 3 digits after the dot
        uq_dlon = np.unique(np.round(lon_[1:]-lon_[0:-1],decimals=3))
        uq_dlat = np.unique(np.round(lat_[1:]-lat_[0:-1],decimals=3))

        if uq_dlon.size>1 or uq_dlat.size>1:
            msg = "expected regular grid, but there are varying differences"
            msg += " uq_dlon={} uq_dlat={}".format(uq_dlon,uq_dlat)
            raise RuntimeError(msg)
        self.dlon = uq_dlon[0]
        self.dlat = np.abs(uq_dlat[0])

        msg = "detected grid resolution is dlon={} dlat={}".format(self.dlon, self.dlat)
        PkgLogger.info(msg)

        #--
        nlon = int(360./self.dlon)
        nlat = int(180./self.dlat)

        #-- internally store grid-cell centre on full global coverage
        self.lon_ctrs = np.linspace(-180., 180., num=nlon, endpoint=False) + self.dlon/2.
        self.lon_ctrs = np.round(self.lon_ctrs,decimals=2)
        if lon_.size< nlon:
            msg = "dataset does not cover earth fully in West-East direction, "
            msg += "cannot yet handle!"
            PkgLogger.fatal(msg)
            raise RuntimeError(msg)

        if is_declat:
            self.lat_ctrs = np.linspace(90., -90., num=nlat, endpoint=False) - self.dlat/2.
            self.lat_ctrs = np.round(self.lat_ctrs,decimals=2)
            if lat_.size < nlat:
                latlb_ = lat_ - self.dlat/2.
                latub_ = lat_ + self.dlat/2.
                self.ilat_lo = np.where((self.lat_ctrs>=latlb_[0])&(self.lat_ctrs<=latub_[0]))[0][0]
                self.ilat_hi = np.where((self.lat_ctrs>=latlb_[-1])&(self.lat_ctrs<=latub_[-1]))[0][0]+1
            else:
                self.ilat_lo = 0
                self.ilat_hi = nlat
        else:
            self.lat_ctrs = np.linspace(-90., 90., num=nlat, endpoint=False) + self.dlat/2.
            self.lat_ctrs = np.round(self.lat_ctrs,decimals=2)
            msg = "increasing latitude dimensions in datafile not yet handled."
            raise RuntimeError(msg)

        #-- close file
        ncfp.close()

        #-- store area for grid-cell per zonal band
        dlon = np.ones((nlat,))*self.dlon
        lat_sb = self.lat_ctrs - self.dlat/2.
        lat_nb = self.lat_ctrs + self.dlat/2.
        self.area_vec = np.vectorize(area_on_earth)(dlon, lat_sb, lat_nb, ERmeter=6.371e6)

# %%%GridMap%%%
