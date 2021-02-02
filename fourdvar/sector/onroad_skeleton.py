import numpy as np
def onRoadSkeleton( countryMap, nationalEmissions, roads, population, nightLights):
    """ skeleton for quick&dirty downscaling of onroad emissions.
       arguments: countryMap: 2d array of integers listing the country index of each point, if we only have one country this needs only two values, 1 for the country and 0 for anything else
    nationalEmissions: array or list of onroad emissions for each country, probably taken from IEA data
    roads: 2d array of road length in each grid cell, same shape as countryMap
    population: population density in each grid cell, same shape as countryMap
    nightLights: nightlight intensity in each grid cell, same shape as countryMap.
    returns: 2d array of onroad emissions. these are different combinations of input fields
    e.g. roads*population*nightLights or roads*population ... here we give only one example"""
    result = np.zeros_like( nightLights)
    emissions = roads *population *nightLights
    countryIndexes = set( countryMap) # list of unique country ids
    for countryIndex in countryIndexes:
        if countryIndex == 0: pass # 0 means ocean or no country
        countryLoc = countryMap == countryIndex # array of points in country
        scaling = emissions[ countryLoc].sum() # un-normalised national sum
        result[ countryLoc] = nationalEmissions[ countryIndex]/scaling * emissions[ countryLoc]
    return result
