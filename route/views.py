from django.shortcuts import render
import folium
from route import getroute
from geopy.distance import geodesic
import logging
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def showmap(request):
    return render(request, 'showmap.html')

def validate_coordinates(lat, lon):
    """Проверка валидности координат"""
    try:
        lat, lon = float(lat), float(lon)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False, "Координаты должны быть в диапазоне: широта [-90; 90], долгота [-180; 180]"
        return True, None
    except ValueError:
        return False, "Некорректный формат координат"

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Вычисляет расстояние между двумя точками на сфере (в километрах)
    используя формулу гаверсинусов.
    """
    R = 6371  # Радиус Земли в километрах

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def point_to_line_distance(point, line_start, line_end):
    """
    Вычисляет кратчайшее расстояние от точки до отрезка на сфере
    и возвращает это расстояние и ближайшую точку на отрезке
    """
    # Конвертируем координаты в радианы
    lat, lon = point
    lat1, lon1 = line_start
    lat2, lon2 = line_end
    
    # Находим вектора
    vec_line = (lat2 - lat1, lon2 - lon1)
    vec_point = (lat - lat1, lon - lon1)
    
    # Находим длину линии
    line_length = sqrt(vec_line[0]**2 + vec_line[1]**2)
    
    if line_length == 0:
        return haversine_distance(lat, lon, lat1, lon1), (lat1, lon1)
    
    # Нормализуем вектор линии
    vec_line = (vec_line[0]/line_length, vec_line[1]/line_length)
    
    # Проекция точки на линию
    t = max(0, min(line_length, vec_point[0]*vec_line[0] + vec_point[1]*vec_line[1]))
    
    # Находим ближайшую точку на линии
    closest_lat = lat1 + t * vec_line[0]
    closest_lon = lon1 + t * vec_line[1]
    
    # Вычисляем реальное расстояние на сфере
    distance = haversine_distance(lat, lon, closest_lat, closest_lon)
    
    return distance, (closest_lat, closest_lon)

def find_closest_point_on_route(point_coords, routes):
    """
    Находит ближайшую точку на маршруте и возвращает её координаты и расстояние
    """
    min_distance = float('inf')
    closest_point = None
    
    for i in range(len(routes)-1):
        point1 = routes[i]
        point2 = routes[i+1]
        
        # Вычисляем расстояние до отрезка маршрута
        distance, nearest_point = point_to_line_distance(
            point_coords,
            point1,
            point2
        )
        
        if distance < min_distance:
            min_distance = distance
            closest_point = nearest_point
            
    return closest_point, min_distance

def showroute(request, lat1, long1, lat2, long2, attractions=None):
    # Валидация входных координат
    for coord_pair in [(lat1, long1, "начальной"), (lat2, long2, "конечной")]:
        is_valid, error_msg = validate_coordinates(coord_pair[0], coord_pair[1])
        if not is_valid:
            return render(request, 'error.html', 
                        {'error': f"Ошибка в координатах {coord_pair[2]} точки: {error_msg}"})
    
    # Список отелей Новочеркасска
    hotels = [
        ("47.41722,40.10833", "Платов Отель"),
        ("47.41500,40.09722", "Hotel Novocherkassk"),
        ("47.42056,40.09167", "Green Hotel"),
        ("47.41389,40.10556", "Hotel Don"),
        ("47.41944,40.10278", "Hotel Ermak")
    ]

    # Главные достопримечательности Новочеркасска
    attractions = [
        ("47.41465,40.10877", "Pamyatnik Yermaku"),
        ("47.40964,40.10130", "Fountain in front of the palace Chieftain"),
        ("47.41004,40.10100", "Fontan V Skvere Imeni M.i. Platova"),
        ("47.40832,40.10235", "Bol'shoy Fontan"),
        ("47.41127,40.10380", "Fountain on the central square"),
        ("47.40908,40.09673", "Pamyatnik Generalissimusu A.v.suvorovu"),
        ("47.41897,40.02002", "Stella Novocherkassk"),  # Стелла Новочеркасск
        ("47.41309,40.11076", "Pamyatnik Yakovu Petrovichu Baklanovu"),
        ("47.40942,40.10157", "Atamanskiy Dvorets"),
        ("47.41232,40.10414", "Museum of the History of the Don Cossacks"),
        ("47.41412,40.11043", "Voznesenskiy Kafedral'nyy Sobor"),
        ("47.41052,40.10146", "Monument to a Cossack"),
        ("47.42316,40.10247", "Dom-Muzey M.b.grekova"),
        ("47.42218,40.09404", "Памятник казакам-революционерам"),
        ("47.40942,40.10349", "mound of Glory"),
        ("47.42236,40.09387", "Poklonnyy Krest"),
        ("47.41440,40.11129", "reconciliation and harmony Monument"),
        ("47.42185,40.06920", "Monument to Cossack horses"),
        ("47.42539,40.08227", "House-Museum of Ivan Krylov")
    ]
    
    attractions += request.GET.getlist('attractions')
    figure = folium.Figure()
    lat1, long1, lat2, long2 = float(lat1), float(long1), float(lat2), float(long2)
    
    route_data = getroute.get_route(long1, lat1, long2, lat2, attractions)
    start_point, end_point, routes, distance = route_data
    
    m = folium.Map(location=[start_point[0], start_point[1]], zoom_start=10)
    m.add_to(figure)
    
    # Добавляем маршрут на карту
    route_points = []
    for i in range(len(routes)-1):
        point1 = routes[i]
        point2 = routes[i+1]
        route_points.extend([point1, point2])
        folium.PolyLine([point1, point2], weight=8, color='blue', opacity=0.6).add_to(m)
    
    # Добавляем маркеры для стартовой и конечной точек
    folium.Marker(location=start_point, icon=folium.Icon(icon='play', color='green'), popup='Старт').add_to(m)
    folium.Marker(location=end_point, icon=folium.Icon(icon='stop', color='red'), popup='Финиш').add_to(m)

    nearby_attractions = {}
    nearby_hotels = {}
    
    # Обработка достопримечательностей
    for attraction in attractions:
        coords = tuple(map(float, attraction[0].split(',')))
        closest_point, min_distance = find_closest_point_on_route(coords, routes)
        
        # Особая обработка для Стеллы Новочеркасск
        if "Stella Novocherkassk" in attraction[1]:
            logger.info(f"Стелла Новочеркасск: минимальное расстояние = {min_distance:.2f} км")
            # Добавляем перпендикулярную линию от стеллы до ближайшей точки маршрута
            folium.PolyLine(
                locations=[coords, closest_point],
                weight=2,
                color='red',
                opacity=0.8,
                dash_array='5, 10',
                popup=f'Минимальное расстояние: {min_distance:.2f} км'
            ).add_to(m)
            
        # Если место находится в пределах 1 км от маршрута
        if min_distance <= 1:
            nearby_attractions[attraction[1]] = {
                'name': attraction[1],
                'distance': min_distance,
                'coords': coords
            }
            # Добавляем маркер на карту
            folium.Marker(
                location=[coords[0], coords[1]],
                icon=folium.Icon(color='orange'),
                popup=f"{attraction[1]} ({min_distance:.2f} км)"
            ).add_to(m)

    # Обработка отелей
    for hotel in hotels:
        coords = tuple(map(float, hotel[0].split(',')))
        closest_point, min_distance = find_closest_point_on_route(coords, routes)
        
        # Если отель находится в пределах 1 км от маршрута
        if min_distance <= 1:
            nearby_hotels[hotel[1]] = {
                'name': hotel[1],
                'distance': min_distance,
                'coords': coords
            }
            # Добавляем маркер отеля на карту
            folium.Marker(
                location=[coords[0], coords[1]],
                icon=folium.Icon(color='purple', icon='home'),
                popup=f"{hotel[1]} ({min_distance:.2f} км)"
            ).add_to(m)

    try:
        figure.render()
        context = {
            'map': figure,
            'distance': round(distance, 2),
            'nearby_attractions': sorted(nearby_attractions.values(), key=lambda x: x['distance'])[:5],
            'nearby_hotels': sorted(nearby_hotels.values(), key=lambda x: x['distance'])[:5]
        }
        return render(request, 'showroute.html', context)
    except Exception as e:
        logger.error(f"Ошибка при построении маршрута: {str(e)}")
        return render(request, 'error.html', 
                    {'error': f'Произошла ошибка при построении маршрута: {str(e)}'})

def is_on_route(lat, lon, route, max_distance=0.5):
    try:
        lat, lon = float(lat), float(lon)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False
        
        point_coords = (lat, lon)
        _, min_distance = find_closest_point_on_route(point_coords, route)
        return min_distance <= max_distance
        
    except (ValueError, TypeError):
        return False

def distance(lat1, lon1, lat2, lon2):
    try:
        return haversine_distance(float(lat1), float(lon1), float(lat2), float(lon2))
    except (ValueError, TypeError):
        return float('inf')
