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
    # Получаем параметры видимости маркеров из запроса
    show_attractions = request.GET.get('show_attractions', 'true').lower() == 'true'
    show_hotels = request.GET.get('show_hotels', 'true').lower() == 'true'
    
    # Получаем минимальную дистанцию из параметров запроса или используем значение по умолчанию
    try:
        min_distance_threshold = float(request.GET.get('min_distance', 1.0))
    except (ValueError, TypeError):
        min_distance_threshold = 1.0
    
    # Валидация входных координат
    for coord_pair in [(lat1, long1, "начальной"), (lat2, long2, "конечной")]:
        is_valid, error_msg = validate_coordinates(coord_pair[0], coord_pair[1])
        if not is_valid:
            return render(request, 'error.html', 
                        {'error': f"Ошибка в координатах {coord_pair[2]} точки: {error_msg}"})
    
    # Список отелей Новочеркасска
    hotels = [
        ("47.41722,40.10833", "Платов Отель"),
        ("47.41500,40.09722", "Отель Новочеркасск"),
        ("47.42056,40.09167", "Зеленый Отель"),
        ("47.41389,40.10556", "Отель Дон"),
        ("47.41944,40.10278", "Отель Ермак")
    ]

    # Главные достопримечательности Новочеркасска
    attractions = [
            ("47.41465709241513,40.10877591178936", "Памятник Ермаку"),
        ("47.40964864620244,40.10130932945763",  "Фонтан перед атаманским дворцом"),
        ("47.41004133861746,40.10100290000992",  "Фонтан в сквере имени М.И. Платова"),
        ("47.40832849238213,40.10235142945763",  "Большой Фонтан"),
        ("47.41127503864937,40.103805500009905",  "Фонтан на центральной площади"),
        ("47.40908633859277,40.09673912945763",  "Памятник генералиссимусу А.В. Суворову"),
        ("47.418972438848364,40.02002422945763",  "Стелла Новочеркасск"),
        ("47.70745374632344,40.21376582945763",  "Солдату-Освободителю"),
        ("47.413097919126834,40.11076938515802",  "Памятник Я.П. Бакланову"),
        ("47.40942848480216,40.10157749654204",  "Атаманский Дворец"),
        ("47.41232440559971,40.104141070551094",  "Музей истории казаков"),
        ("47.41412297744595,40.110430000019825",  "Вознесенский Кафедральный собор"),
        ("47.410524884839944,40.10146531781071",  "Памятник Казаку"),
        ("47.42316668728757,40.102470290008945",  "Дом-музей М.Б. Грекову"),
        ("47.42218732290731,40.09404537387836",  "Памятник казакам-революционерам Ф.Г.Подтелкову и М.В.Кривошлыкову"),
        ("47.409424178417865,40.10349427132213",  "Курган Славы"),
        ("47.42236154099214,40.09387427132213",  "Поклонный крест"),
        ("47.4144057398952,40.111293100158555",  "Памятник примирению и гармонии"),
        ("47.4218528,40.06920930015854",  "Памятник казачьим коням"),
        ("47.425399824236216,40.082276515504205", "Дом-музей Ивана крылова")
    ]
    
    attractions += request.GET.getlist('attractions')
    figure = folium.Figure()
    logger.debug(f"Map figure created: {figure}")
    lat1, long1, lat2, long2 = float(lat1), float(long1), float(lat2), float(long2)
    
    route_data = getroute.get_route(long1, lat1, long2, lat2, attractions)
    logger.debug(f"Route data: {route_data}")  # Логирование данных маршрута
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
    folium.Marker(
        location=start_point,
        icon=folium.Icon(icon='play', color='green'),
        popup='Старт',
        html='<div class="marker-start"></div>'
    ).add_to(m)
    
    folium.Marker(
        location=end_point,
        icon=folium.Icon(icon='stop', color='red'),
        popup='Финиш',
        html='<div class="marker-end"></div>'
    ).add_to(m)

    nearby_attractions = {}
    nearby_hotels = {}
    
    # Обработка достопримечательностей
    if show_attractions:
        attraction_counter = 1
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
                
            # Если место находится в пределах заданной дистанции от маршрута
            if min_distance <= min_distance_threshold:
                nearby_attractions[attraction[1]] = {
                    'name': attraction[1],
                    'distance': min_distance,
                    'coords': coords,
                    'id': f'marker-attraction-{attraction_counter}'
                }
                # Добавляем маркер на карту с уникальным классом
                marker = folium.Marker(
                    location=[coords[0], coords[1]],
                    icon=folium.Icon(color='orange'),
                    popup=f"{attraction[1]} ({min_distance:.2f} км)",
                    html=f'<div class="marker-attraction" id="marker-attraction-{attraction_counter}"></div>'
                )
                marker.add_to(m)
                attraction_counter += 1

    # Обработка отелей
    if show_hotels:
        hotel_counter = 1
        for hotel in hotels:
            coords = tuple(map(float, hotel[0].split(',')))
            closest_point, min_distance = find_closest_point_on_route(coords, routes)
            
            # Если отель находится в пределах заданной дистанции от маршрута
            if min_distance <= min_distance_threshold:
                nearby_hotels[hotel[1]] = {
                    'name': hotel[1],
                    'distance': min_distance,
                    'coords': coords,
                    'id': f'marker-hotel-{hotel_counter}'
                }
                # Добавляем маркер отеля на карту с уникальным классом
                marker = folium.Marker(
                    location=[coords[0], coords[1]],
                    icon=folium.Icon(color='purple', icon='home'),
                    popup=f"{hotel[1]} ({min_distance:.2f} км)",
                    html=f'<div class="marker-hotel" id="marker-hotel-{hotel_counter}"></div>'
                )
                marker.add_to(m)
                hotel_counter += 1

    try:
        # No need to render the figure here
        m=m._repr_html_() #updated
        m = m.replace(
        '<div style="width:100%;"><div style="position:relative;width:100%;height:0;padding-bottom:60%;">', 
        '<div style="width:100%;"><div style="width:100%;height:0%;padding-bottom:60%;">', 
        1)
        context = {
            'map': m,
            'distance': round(distance, 2),
            'nearby_attractions': sorted(nearby_attractions.values(), key=lambda x: x['distance'])[:5],
            'nearby_hotels': sorted(nearby_hotels.values(), key=lambda x: x['distance'])[:5],
            'min_distance': min_distance_threshold,
            'show_attractions': show_attractions,
            'show_hotels': show_hotels
        }
        logger.debug(f"Context for rendering: {context}")
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
