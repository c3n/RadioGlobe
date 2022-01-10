import json
from math import *
from scipy.spatial import KDTree

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

class Stations():
    def __init__(self):
        with open("stations.json") as f:
            sj=json.load(f)
        self.stations_list=list(sj.items())
        self.stations_coords=[[x[1]["coords"]["n"],x[1]["coords"]["e"]] for x in self.stations_list]
        self.stations_tree=KDTree(self.stations_coords)
    
    def query(self,lat,lon):
        dist,idx=self.stations_tree.query([lat,lon])
        dist_km=int(haversine(lat,lon,*self.stations_coords[idx]))
        return dist_km,self.stations_list[idx][0],self.stations_list[idx][1]["urls"]

