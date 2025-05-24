from django.http import JsonResponse
from django.shortcuts import render
from route import getroute
from geopy.distance import geodesic
from math import radians, sin, cos, sqrt, atan2
from rest_framework.decorators import api_view
from .serializers import RouteSerializer
from users.models import User 
from rest_framework import status
from rest_framework.response import Response
from random import randint

import json
import logging
import numpy as np
import requests
import folium

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
    R = 6371  
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
    lat, lon = point
    lat1, lon1 = line_start
    lat2, lon2 = line_end
    vec_line = (lat2 - lat1, lon2 - lon1)
    vec_point = (lat - lat1, lon - lon1)
    line_length = sqrt(vec_line[0]**2 + vec_line[1]**2)
    if line_length == 0:
        return haversine_distance(lat, lon, lat1, lon1), (lat1, lon1)
    vec_line = (vec_line[0]/line_length, vec_line[1]/line_length)
    t = max(0, min(line_length, vec_point[0]*vec_line[0] + vec_point[1]*vec_line[1]))
    closest_lat = lat1 + t * vec_line[0]
    closest_lon = lon1 + t * vec_line[1]
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
        distance, nearest_point = point_to_line_distance(
            point_coords,
            point1,
            point2
        )
        if distance < min_distance:
            min_distance = distance
            closest_point = nearest_point
    return closest_point, min_distance

def showroute(request, uid, lat1, long1, lat2, long2, attractions=None):
    show_attractions = request.GET.get('show_attractions', 'true').lower() == 'true'
    show_hotels = request.GET.get('show_hotels', 'true').lower() == 'true'
    show_natural = request.GET.get('show_natural', 'true').lower() == 'true'
    try:
        min_distance_threshold = float(request.GET.get('min_distance', 1.0))
    except (ValueError, TypeError):
        min_distance_threshold = 1.0
    for coord_pair in [(lat1, long1, "начальной"), (lat2, long2, "конечной")]:
        is_valid, error_msg = validate_coordinates(coord_pair[0], coord_pair[1])
        if not is_valid:
            return render(request, 'error.html', 
                        {'error': f"Ошибка в координатах {coord_pair[2]} точки: {error_msg}"})
    hotels = [
        ("47.41722,40.10833", "Платов Отель"),
        ("47.41500,40.09722", "Отель Новочеркасск"),
        ("47.42056,40.09167", "Зеленый Отель"),
        ("47.41389,40.10556", "Отель Дон"),
        ("47.41944,40.10278", "Отель Ермак"),
        ("47.27571083974165, 39.83877501774771", "мотель Магнат N 1"),
        ("48.65490019818607, 44.44183567996033", "7 Королей - PrestigeHotel"),
        ("48.69272500484903, 44.48612171424022", "Estel Hotel"),
        ("48.695830812031566, 44.462016082897804", "Marton"),
        ("48.59416118300371, 44.39879102969111", "SQ Relax & Healthcare"),
        ("48.56933261803871, 44.44671504263903", "Гостиница \"Домус\""),
        ("48.800734822073686, 44.74822708956529", "Отель Milot"),
        ("48.78746095445953, 44.751868577278465", "Гостиница Ахтуба"),
        ("48.81432490190864, 44.83538002879013", "Гостиничный комплекс \"Арт-Волжский\""),
        ("48.69989351302465, 44.778087288803086", "База отдыха \"Солнечный остров\""),
        ("48.709185774780885, 44.77298920600464", "Душевный отдых в Осинках. Парк-отель."),
        ("48.70085486079875, 44.847032789479506", "Семейный дворик"),
        ("48.6250319263524, 44.863627999477345", "База отдыха \"Лесная дача\""),
        ("48.69075223462923, 44.98708450713608", "База отдыха Изумруд"),
        ("48.67645695052084, 44.96572079052075", "Турбаза Полигон"),
        ("50.11580711335525, 45.422400037866076", "Дмитриевская"),
        ("50.11444497559139, 45.41894062453855", "Гостиница Центр туризма"),
        ("50.08199070278138, 45.41324476488011", "Опава"),
        ("50.08310062665241, 45.406872161382054", "Запросто"),
        ("50.06366149428337, 45.39009694117034", "Волга")
    ]
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
        ("47.425399824236216,40.082276515504205", "Дом-музей Ивана крылова"),
        ("47.26407885009436, 39.66688657722957", "Соловьиная роща"),
        ("47.256659286525796, 39.67875619324099", "Родник Святого Павла"),
        ("47.22760699409996, 39.75340983078653", "Стела \"Освободителям Ростова\""),
        ("47.21864951350899, 39.72692940944788", "Парамоновские склады"),
        ("47.23049860030893, 39.715485758135785", "Проспект звезд"),
        ("47.21582958340725, 39.72264907381329", "Дон-батюшка"),
        ("47.21397236824416, 39.714175940874654", "Ростовчанка"),
        ("47.21749702511215, 39.71193035655353", "Кафедральный собор Рождества Пресвятой Богородицы"),
        ("47.150255531585934, 39.73543742253906", "Храм Святой Троицы"),
        ("47.128111388806836, 39.77473732732943", "Храм Иоганна Русского"),
        ("47.13090485200702, 39.738663534126324", "Сквер Авиаторов"),
        ("47.13797832837931, 39.74224925933398", "Городской музей истории г.Батайска"),
        ("47.139086366362775, 39.743878180725495", "Памятник Чернобыльцам"),
        ("47.15512695198033, 39.74039104597303", "Отель Энергия"),
        ("47.137818844322865, 39.70811334678066", "Гостиничный комплекс Александр"),
        ("47.27143063198079, 39.89180878762609", "Аксайский военно-исторический музей"),
        ("47.271755073298664, 39.89277412445577", "Аксайские Катакомбы"),
        ("47.268894704385836, 39.863311661564026", "Городской фонтан"),
        ("47.25686214623127, 39.789134256687255", "Парк Авиаторов"),
        ("47.2982028352345, 39.79350404194306", "Лесопарк Сосновый бор"),
        ("47.321077076244684, 39.01042514003377", "Мемориал Славы на Самбекских высотах"),
        ("47.11718908391659, 39.423472741927036", "Азовский Историко-Археологический И Палеонтологический Музей-Заповедник"),
        ("48.64840039374413, 44.87392768209971", "Сосновый бор"),
        ("48.70047071023023, 44.991414990233785", "Берег Ахтубы"),
        ("48.5552498852775, 45.30340452428997", "Осочный Лиман"),
        ("50.273708709666444, 45.672369307604995", "Бугор Степана Разина"),
        ("50.252749037981836, 45.64971000584327", "Ураков Бугор"),
        ("50.07852445923264, 45.411788169796054", "Камышинский историко-краеведческий музей"),
        ("47.27143063198079, 39.89180878762609", "Камышин, Стела"),
        ("51.512198830959036, 45.94987995694602", "Волга Стадион"),
        ("51.56014293562728, 46.066296100077714", "Саратовский Лимонарий"),
        ("51.54776533801214, 46.05027355413975", "Парк победы"),
        ("51.5354791167413, 46.00947582517831", "Детский парк"),
        ("51.52116854768777, 46.00295269285081", "Городской парк культуры и отдыха")
    ]
    natural_attractions = [
        ("47.234444, 39.712778", "Ботанический сад ЮФУ"),
        ("47.250000, 39.750000", "Парк имени Горького"),
        ("47.216667, 39.716667", "Парк имени Октябрьской революции"),
        ("47.233333, 39.733333", "Парк имени 1 Мая"),
        ("47.241667, 39.708333", "Парк имени Вити Черевичкина"),
        ("47.258333, 39.791667", "Парк имени Собино"),
        ("47.275000, 39.833333", "Парк имени Ленина"),
        ("47.291667, 39.875000", "Парк имени Кирова"),
        ("47.308333, 39.916667", "Парк имени Фрунзе"),
        ("47.325000, 39.958333", "Парк имени Дзержинского"),
        ("47.341667, 40.000000", "Парк имени Калинина"),
        ("47.358333, 40.041667", "Парк имени Куйбышева"),
        ("47.375000, 40.083333", "Парк имени Орджоникидзе"),
        ("47.391667, 40.125000", "Парк имени Ворошилова"),
        ("47.408333, 40.166667", "Парк имени Буденного"),
        ("47.425000, 40.208333", "Парк имени Ворошилова"),
        ("47.441667, 40.250000", "Парк имени Буденного"),
        ("47.458333, 40.291667", "Парк имени Ворошилова"),
        ("47.475000, 40.333333", "Парк имени Буденного"),
        ("47.491667, 40.375000", "Парк имени Ворошилова"),
        ("47.123456, 39.789012", "Природный парк Донской"),
        ("47.234567, 39.890123", "Заповедник Ростовский"),
        ("47.345678, 39.901234", "Озеро Маныч-Гудило"),
        ("47.456789, 39.912345", "Водопад на реке Дон"),
        ("47.567890, 39.923456", "Пещера Каменная"),
        ("47.678901, 39.934567", "Родник Святой"),
        ("47.789012, 39.945678", "Гора Долгая"),
        ("47.890123, 39.956789", "Лесной массив Донской"),
        ("47.901234, 39.967890", "Озеро Цимлянское"),
        ("47.012345, 39.978901", "Заказник Вешенский"),
        ("47.123456, 39.989012", "Природный памятник Каменная Балка"),
        ("47.234567, 39.990123", "Роща Дубовая"),
        ("47.345678, 39.991234", "Озеро Соленое"),
        ("47.456789, 39.992345", "Водопад на реке Северский Донец"),
        ("47.567890, 39.993456", "Пещера Медвежья")
    ]
    attractions += request.GET.getlist('attractions')
    figure = folium.Figure()
    lat1, long1, lat2, long2 = float(lat1), float(long1), float(lat2), float(long2)
    route_data = getroute.get_route(long1, lat1, long2, lat2, attractions)
    start_point, end_point, routes, distance = route_data
    m = folium.Map(location=[start_point[0], start_point[1]], zoom_start=10) 
    m.add_to(figure)
    route_points = []
    for i in range(len(routes)-1):
        point1 = routes[i]
        point2 = routes[i+1]
        route_points.extend([point1, point2])
        folium.PolyLine([point1, point2], weight=8, color='blue', opacity=0.6).add_to(m)
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
    nearby_natural = {}
    if show_attractions:
        attraction_counter = 1
        for attraction in attractions:
            coords = tuple(map(float, attraction[0].split(',')))
            closest_point, min_distance = find_closest_point_on_route(coords, routes)
            if "Stella Novocherkassk" in attraction[1]:
                logger.info(f"Стелла Новочеркасск: минимальное расстояние = {min_distance:.2f} км")
                folium.PolyLine(
                    locations=[coords, closest_point],
                    weight=2,
                    color='red',
                    opacity=0.8,
                    dash_array='5, 10',
                    popup=f'Минимальное расстояние: {min_distance:.2f} км'
                ).add_to(m)
            if min_distance <= min_distance_threshold:
                nearby_attractions[attraction[1]] = {
                    'name': attraction[1],
                    'distance': min_distance,
                    'coords': coords,
                    'id': f'marker-attraction-{attraction_counter}'
                }
                marker = folium.Marker(
                    location=[coords[0], coords[1]],
                    icon=folium.Icon(color='orange'),
                    popup=f"{attraction[1]} ({min_distance:.2f} км)",
                    html=f'<div class="marker-attraction" id="marker-attraction-{attraction_counter}"></div>'
                )
                marker.add_to(m)
                attraction_counter += 1
    if show_hotels:
        hotel_counter = 1
        for hotel in hotels:
            coords = tuple(map(float, hotel[0].split(',')))
            closest_point, min_distance = find_closest_point_on_route(coords, routes)
            if min_distance <= min_distance_threshold:
                nearby_hotels[hotel[1]] = {
                    'name': hotel[1],
                    'distance': min_distance,
                    'coords': coords,
                    'id': f'marker-hotel-{hotel_counter}'
                }
                marker = folium.Marker(
                    location=[coords[0], coords[1]],
                    icon=folium.Icon(color='purple', icon='home'),
                    popup=f"{hotel[1]} ({min_distance:.2f} км)",
                    html=f'<div class="marker-hotel" id="marker-hotel-{hotel_counter}"></div>'
                )
                marker.add_to(m)
                hotel_counter += 1
    if show_natural:
        natural_counter = 1
        for natural in natural_attractions:
            coords = tuple(map(float, natural[0].split(',')))
            closest_point, min_distance = find_closest_point_on_route(coords, routes)
            if min_distance <= min_distance_threshold:
                nearby_natural[natural[1]] = {
                    'name': natural[1],
                    'distance': min_distance,
                    'coords': coords,
                    'id': f'marker-natural-{natural_counter}'
                }
                marker = folium.Marker(
                    location=[coords[0], coords[1]],
                    icon=folium.Icon(color='green', icon='leaf'),
                    popup=f"{natural[1]} ({min_distance:.2f} км)",
                    html=f'<div class="marker-natural" id="marker-natural-{natural_counter}"></div>'
                )
                marker.add_to(m)
                natural_counter += 1
    try:
        m=m._repr_html_() 
        m = m.replace(
        '<div style="width:100%;"><div style="position:relative;width:100%;height:0;padding-bottom:60%;">', 
        '<div style="width:100%;"><div style="width:100%;height:0%;padding-bottom:60%;">', 
        1)
        dist = round(distance, 2)
        add_route(uid=uid, lat1=lat1, long1=long1, lat2=lat2, long2=long2,dist=dist)
        context = {
            'map': m,
            'distance': dist,
            'nearby_attractions': sorted(nearby_attractions.values(), key=lambda x: x['distance'])[:5],
            'nearby_hotels': sorted(nearby_hotels.values(), key=lambda x: x['distance'])[:5],
            'nearby_natural': sorted(nearby_natural.values(), key=lambda x: x['distance'])[:5],
            'min_distance': min_distance_threshold,
            'show_attractions': show_attractions,
            'show_hotels': show_hotels,
            'show_natural': show_natural
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
def add_route(uid, lat1, long1, lat2, long2, dist):
    coords = f"{lat1},{long1},{lat2},{long2}"
    if not uid:
        return JsonResponse({'error': 'userId not provided'}, status=400)
    try:
        user = User.objects.get(firebase_user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    data = {
        "name": f"Маршрут {randint(1000,100000)}",
        "firebase_user_id": f"{uid}",
        "coords": f"{coords}",
        "distance": f"{dist}"
    }
    url = "http://89.104.66.155/api/routes/create/"
    response = requests.post(url, json=data)
