"""
countries.py

Copyright 2020 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
"""

import sys
import os
import csv
import numpy as np
import numpy.ma as ma
import netCDF4 as nc4
import geopandas as gpd

#-- local packages
from pkglog import PkgLogger
from util import create_sha512
from area import area_on_earth
from grid import GridMap


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
from iso2iea import iso2iea # large dictionary for mapping country codes
#          CountryDesc
def get_country_extent( shapeFile, inclusionList=None, exclusionList=None):
    """ read country list from shapefile,
       loop over all countries to find the min and max lat and lon,
       If inclusionList is set then use it instead of all countries,
       do not consider countries on exclusion list,
       returns four elements, minlat,maxlat,minlon,maxlon"""
	     # Reading shapefile
    shp = gpd.read_file(r'C:\Users\mluqman\Documents\GitHub\py4dvar\fourdvar\data\vector\Countries_3.shp')
    combined_geom = None
    #if inclusionList has an arroy of country use it.
    if inclusionList is not None:
        for country in inclusionList:
            country_filtered = shp[shp['ISO3'] == country] # filtering counties from shapefile
            combined_geom = country_filtered if combined_geom is None else combined_geom.geometry.append(
                country_filtered.geometry) # Joining the Geom of all includeList  country's geometry
    #if excludeList has an arroy of country exclude them from countries.
    elif exclusionList is not None:
        for index, row in shp.iterrows(): #For  loop to get all the countries row by row
            if row['ISO3'] not in exclusionList:  # If a country in not in excludelist
                country_filtered = shp[shp['ISO3'] == row['ISO3']] # filtring country from shp one by one
                combined_geom = country_filtered if combined_geom is None else combined_geom.geometry.append(
                    country_filtered.geometry) # Combine all countries's geometries in one
    # if includeList and excludeList both are None, Then Use all counties in Shapefile
    else:
        for index, row in shp.iterrows():
            country_filtered = shp[shp['ISO3'] == row['ISO3']] # filtring country from shp one by one
            combined_geom = country_filtered if combined_geom is None else combined_geom.geometry.append(
                country_filtered.geometry) # Combine all countries's geometries in one

    wkt = combined_geom.unary_union.envelope.wkt # getting WKT(well know text) of union of all geometries
    print('WKT: ' + wkt) # Printing WKT to console
    bounds = combined_geom.unary_union.bounds # getting bounds of union of all geometries.
    # bounds[minx,miny,maxx,maxy]
    minx = bounds[0]
    miny = bounds[1]
    maxx = bounds[2]
    maxy = bounds[3]
    #returns four elements, minlat, maxlat, minlon, maxlon
    print('Bounds: ' + str(miny) + ',' + str(maxy) + ',' + str(minx) + ',' + str(maxx))
    return miny,maxy,minx,maxx


get_country_extent('Countries_3.shp')
	   inclusionList = ['Pakistan','India']
    return None,None,None,None # fill in
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Country(object):
    def __init__(self, icode, name, iso3, region):
        self.icode = icode
        self.name = name.strip()
        self.iso3 = iso3.lower()
        self.region = region.strip() if region!=None else region

    def __str__(self):
        pstr = self.name
        pstr += '['+self.iso3+','+str(self.icode)+']'
        return pstr



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
#          CountryWorldMap
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class CountryWorldMap(GridMap):

    def __init__(self, lutfile, shapefile, orientation=None):
        self.lut_fname = lutfile
        self.lut_sha512 = create_sha512(lutfile)
        self.shape_fname = shapefile
        self.shape_sha512 = create_sha512(shapefile)
        #-- setup list of country codes
        self._setup_lut()
        #-- setup country map
        self._setup_map(orientation=orientation)

    def _setup_lut(self):
        self.country_list = read_country_list(self.lut_fname)
        #-- really ensure countries are sorted according to country code
        self.country_list.sort(key=lambda x: x.icode)
        #-- ATTENTION: using 1-indexing here
        self.country_list = [None] + self.country_list
        msg = "country LUT has been read from file ***{}***, yielding {} countries.".format(
            self.lut_fname, len(self.country_list))
        PkgLogger.info(msg)
        cfirst = self.country_list[1]
        clast  = self.country_list[-1]
        msg = "Sorted by integer code, first_country={}({}) last_country={}({})".format(
            cfirst.get_iso3(), cfirst.get_name(), clast.get_iso3(), clast.get_name())
        PkgLogger.info(msg)

    #--
    def _setup_map(self, orientation=None):

        #-- setup grid-information first
        self.setup_grid_from_netcdf(self.shape_fname)
        nlat = self.get_nlat()
        nlon = self.get_nlon()

        #-- now access country codes
        try:
            ncfp = nc4.Dataset(self.shape_fname)
            msg = "determine country world-map from file ***{}***".format(self.shape_fname)
            PkgLogger.info(msg)
        except IOError:
            msg = "CountryWorldMap: datafile ***{}*** could not be opened.".format(self.shape_fname)
            raise RuntimeError(msg)

        #-- get country codes
        ccodes_in = ncfp.variables['country'][:].astype(int)
        nmiss = nlat-ccodes_in.shape[0]
        ccodes_fill = ncfp.variables['country'].getncattr('_FillValue')
        uq_ccodes_ = np.unique(ccodes_in[ccodes_in.mask==False])
        ncountries = uq_ccodes_.size
        msg = "detected {} different country codes, code_min={} code_max={}".format(
            ncountries, ccodes_in.min(), ccodes_in.max())
        PkgLogger.info(msg)
        self.fill_code = ncfp.variables['country'].getncattr('_FillValue').astype(np.int16)
        uq_ccodes_all = set(np.arange(uq_ccodes_.min(),uq_ccodes_.max()+1))
        codes_unmapped = uq_ccodes_all - set(uq_ccodes_)
        for i in codes_unmapped:
            msg = "unmapped country: icode={} country={}".format(i, self.country_list[i])
            PkgLogger.info(msg)

        #-- close file
        ncfp.close()


        #--
        self.country_map = np.empty((nlat,nlon), dtype=np.int16)
        if nmiss==0:
            self.country_map[:,:] = ccodes_in[:,:]
        elif self.is_declat(): #assume missing a
            self.country_map[nmiss:,:] = ccodes_in[:,:]
            self.country_map[nmiss:,:][ccodes_in.mask] = self.fill_code
            self.country_map[0:nmiss,:] = self.fill_code

    def get_country_list(self):
        return self.country_list[1:] #discard the 'None' entry put at front

    def country_by_iso3(self,iso3):
        cntry_desc = None
        for c in self.country_list:
            if c.iso3==iso3:
                country_desc = c
                break
        return cntry_desc

    def get_iso3(self,icode):
        return self.country_list[icode].get_iso3()

    #--
    def ncwrt_map(self, outname, **kwargs):
        import datetime as dtm
        try:
            ncfp = nc4.Dataset(outname, 'w')
        except IOError:
            msg = "ncwrt_map:: file ***{}*** could not be opened for writing".format(outname)
            raise RuntimeError(msg)

        zlev = kwargs['zlev'] if kwargs.has_key('zlev') else 4
        use_zlib = True if zlev>0 else False

        #-- create dimensions
        d1 = ncfp.createDimension('lon',self.lon_ctrs.size)
        d2 = ncfp.createDimension('lat',self.lat_ctrs.size)
        #-- longitude
        ncvar = ncfp.createVariable( 'lon', np.float64, ('lon',),
                                     zlib=use_zlib, complevel=zlev )
        ncvar.setncattr('standard_name','longitude')
        ncvar.setncattr('long_name','longitude')
        ncvar.setncattr('units','degrees_east')
        ncvar.setncattr('axis','X')
        ncvar.setncattr('comment','longitude of grid-cell centre')
        ncvar[:] = self.lon_ctrs[:]
        #-- latitude
        ncvar = ncfp.createVariable( 'lat', np.float64, ('lat',),
                                     zlib=use_zlib, complevel=zlev )
        ncvar.setncattr('standard_name','latitude')
        ncvar.setncattr('long_name','latitude')
        ncvar.setncattr('units','degrees_north')
        ncvar.setncattr('axis','Y')
        ncvar.setncattr('comment','latitude of grid-cell centre')
        ncvar[:] = self.lat_ctrs[:]
        #-- country code
        dtyp = self.country_map.dtype
        ncvar = ncfp.createVariable( 'country', dtyp, ('lat','lon'),
                                     fill_value=self.fill_code,
                                     zlib=use_zlib, complevel=zlev   )
        ncvar.setncattr('standard_name','country_code')
        ncvar.setncattr('long_name','integer country code according to ...')
        ncvar.setncattr('units','')
        if kwargs.has_key('only_country'):
            oc = kwargs['only_country']
            data = self.country_map[:,:]
            cnd_oc = data!=oc
            data[cnd_oc] = self.fill_code
            ncvar[:,:] = data
        else:
            ncvar[:,:] = self.country_map[:,:]
        #-- global attributes
        ncfp.setncattr('original_lut_file', self.lut_fname)
        ncfp.setncattr('original_lut_sha512', self.lut_sha512)
        ncfp.setncattr('original_shape_file', self.shape_fname)
        ncfp.setncattr('original_shape_sha512', self.shape_sha512)
        ncfp.setncattr('geospatial_lat_units', "degrees_north")
        ncfp.setncattr('geospatial_lat_resolution', self.get_dlat())
        ncfp.setncattr('geospatial_lat_min', self.get_latmin())
        ncfp.setncattr('geospatial_lat_max', self.get_latmax())
        ncfp.setncattr('geospatial_lon_units', "degrees_north")
        ncfp.setncattr('geospatial_lon_resolution', self.get_dlon())
        ncfp.setncattr('geospatial_lon_min', self.get_lonmin())
        ncfp.setncattr('geospatial_lon_max', self.get_lonmax())
        ncfp.setncattr('netcdf_libversion',"{}".format(nc4.__netcdf4libversion__))
        ncfp.setncattr('date_created',"{}".format(dtm.datetime.utcnow().isoformat()))

        #-- close file
        ncfp.close()
        
# %%%CountryWorldMap%%%


def read_country_list(csvfile, indexstart=0):
    """Function that returns list of CountryDesc instances read from csv file
    
    :csvfile:    fully qualified file name
    :indexstart: first index in list getting an entry
    :return:     list of CountryDesc instances
    :rtype: list
    """

    #-- create list
    clist = [None]*indexstart

    #-- read file line-by-line
    with open(csvfile,'r') as fp:
        #-- check first line
        first_line = fp.readline()
        #MVO::still to be done!!
        #-- reset file
        fp.seek(0)
        #-- assumes single header
        reader = csv.DictReader(fp)
        for row in reader:
            name = row['NAME']
            iso3 = row['GMI_CNTRY']
            region = row['REGION']
            icode = int(row['CODE'])
            clist.append( CountryDesc(icode, name, iso3, region) )

    #-- return generated list
    return clist
# ---read_country_list---


