"""
electricityGenerationSector.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.


"""

import numpy as np
import pandas as pd
from fourdvar.util.iso2iea import iso2iea

# from foudvar.params import config
# import baseSector
# class ElectricityGenerationSector( baseSector.BaseSector):
#     def __init__( self, initval):
#         baseSector.BaseSector.__init__( self)
#         self.val = initval
#         return
#     def readCarma():
#       carma = pd.read_csv('../data/carma.csv', encoding="ISO-8859-1")
#       # """ reads Carma database and creates instance variables for relevant fields from the file"""
#         # read csv from config.carmaFileName
#         # self.lats = ...
#         # likewise for other fields
#         return


csvs = pd.read_csv('../data/carma/CO2_predictions_FINAL.csv', encoding="ISO-8859-1")
carma = dict()
emis_year = 2014
iso3 = ''
emission1 = 0.0
emission = 0.0
csvs_trnd = pd.read_csv('../data/carma/elec_iea_14yrs_trends.csv', encoding="ISO-8859-1")
for i in range(csvs.shape[0]):
    # Check if iso3 code is empty in the csvs variable
    if list(csvs.iso3)[i] == '':
        print('carma plant of country %s missing iso3 code'% list(csvs.name)[0])
    else:           # Standarized the iso3 code for selected countries
        if (list(csvs.iso3)[i] == 'IMY')  :
            iso3 = 'imn'  # isle of man
        elif (list(csvs.iso3)[i] == 'WBG') :
            iso3 = 'gaz'  #  gaza strip
        elif (list(csvs.iso3)[i] == 'TMP') :
            iso3 = 'tls' #  east timor
        elif (list(csvs.iso3)[i] == 'ADO') :
            iso3 = 'and' #  andorra
        elif (list(csvs.iso3)[i] == 'ROU') :
            iso3 = 'rom'  #  romania;;;version 3 carma
        elif (list(csvs.iso3)[i] == 'COD') :
            iso3 = 'cog' #  Congo, Dem.Rep.;;;version 3 carma
        elif (list(csvs.iso3)[i] == 'XKX') :
            iso3 = 'alb' # assigning Kosovo to Albania!!!!;;;version 3 carma
        else:
            iso3 = list(csvs.iso3)[i]
        iso3 = iso3.lower()         #Changed all the code to lower case
        if iso2iea[iso3] == '':     # Check if iso3 code is present in countryiea array
            print('code '+iso3+' unmapped, will be neglected')
            iso3 =''
        else:                       # Calculating the emissions trends and uncertainty, and converting the tonns to mega tonns
            emission1 = list(csvs.carbon_2009)[i] * (1.03 ** (emis_year - 2009))
            uncer = (list(csvs.stderr_pred)[i] * 2.0) * 12. / 44. / 1e6

            try:
                index = list(csvs_trnd.iso3).index(iso3)        # Check iso3 code in csvs_trnd from electric generation data
                iea_elec_trends  = list(csvs_trnd.iea_elec_trends)[index]
                emission = ((1. + (iea_elec_trends / 100.)) **(emis_year - 2009))* emission1 #added to scale the priors by power-law trends to follow iea growth rate
                emission *= 12./44./1e6     #converting the tonns to mega tonns
            except:
                emission = 0.0
                emission1 = 0.0
            # Making list of all the available countries
            carma[i] = ({'name': str(list(csvs.name)[i]), 'lat': list(csvs.latitude)[i], 'lon': list(csvs.longitude)[i],
                         'iso3': iso3, 'iea_number': 1,
                         'emission1': emission1,
                         'emission': emission,
                         'unc':uncer})
print(carma)
# 1 variable (emis_year) and hashkey ?
# what is the return of this code?
# what is basesector for? Where to use this parameter?