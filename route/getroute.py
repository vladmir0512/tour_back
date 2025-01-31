import requests
import json
import polyline
import folium
from geopy.distance import geodesic

def get_route(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat, attractions=None):
    loc = "{},{};{},{}".format(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat)
    url = "http://router.project-osrm.org/route/v1/driving/"
    r = requests.get(url + loc)
    if r.status_code != 200:
        return None
    
    res = r.json()   
    routes = polyline.decode(res['routes'][0]['geometry'])
    start_point = [res['waypoints'][0]['location'][1], res['waypoints'][0]['location'][0]]
    end_point = [res['waypoints'][1]['location'][1], res['waypoints'][1]['location'][0]]
    distance = res['routes'][0]['distance']/1000  # Конвертация в километры
    
    return (
        start_point,
        end_point,
        routes,
        round(distance, 1)
    )
