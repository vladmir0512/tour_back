from django.shortcuts import render
import folium
from route import getroute

def showmap(request):
    return render(request, 'showmap.html')

def showroute(request, lat1, long1, lat2, long2, attractions=None):
    # Главные достопримечательности Новочеркасска
    attractions = [
        ("47.41465709241513,40.10877591178936", "Pamyatnik Yermaku"),
        ("47.40964864620244,40.10130932945763",  " Fountain in front of the palace Chieftain"),
        ("47.41004133861746,40.10100290000992",  " Fontan V Skvere Imeni M.i. Platova"),
        ("47.40832849238213,40.10235142945763",  " Bol'shoy Fontan"),
        ("47.41127503864937,40.103805500009905",  " Fountain on the central square"),
        ("47.40908633859277,40.09673912945763",  " Pamyatnik Generalissimusu A.v.suvorovu"),
        ("47.418972438848364,40.02002422945763",  " Stella Novocherkassk"),
        ("47.70745374632344,40.21376582945763",  "Soldatu-Osvoboditelyu"),
        ("47.413097919126834,40.11076938515802",  "Pamyatnik Yakovu Petrovichu Baklanovu"),
        ("47.40942848480216,40.10157749654204",  "Atamanskiy Dvorets"),
        ("47.41232440559971,40.104141070551094",  "Museum of the History of the Don Cossacks"),
        ("47.41412297744595,40.110430000019825",  "Voznesenskiy Kafedral'nyy Sobor"),
        ("47.410524884839944,40.10146531781071",  "Monument to a Cossack"),
        ("47.42316668728757,40.102470290008945",  "Dom-Muzey M.b.grekova"),
        ("47.42218732290731,40.09404537387836",  "Памятник казакам-революционерам Ф.Г.Подтелкову и М.В.Кривошлыкову"),
        ("47.409424178417865,40.10349427132213",  "mound of Glory"),
        ("47.42236154099214,40.09387427132213",  "Poklonnyy Krest"),
        ("47.4144057398952,40.111293100158555",  "reconciliation and harmony Monument"),
        ("47.4218528,40.06920930015854",  "Monument to Cossack horses"),
        ("447.425399824236216, 40.082276515504205", "House-Museum of Ivan Krylov")

    ]
    
    attractions += request.GET.getlist('attractions')  # Получаем достопримечательности из параметров запроса
    figure = folium.Figure()
    lat1, long1, lat2, long2 = float(lat1), float(long1), float(lat2), float(long2)
    # get_route возвращает кортеж (start_point, end_point, routes, distance)
    route_data = getroute.get_route(long1, lat1, long2, lat2, attractions)
    start_point, end_point, routes, distance = route_data
    
    m = folium.Map(location=[start_point[0], start_point[1]], zoom_start=10)
    m.add_to(figure)
    folium.PolyLine(routes, weight=8, color='blue', opacity=0.6).add_to(m)
    
    # Добавляем маркеры для стартовой и конечной точек с подписями
    folium.Marker(location=start_point, icon=folium.Icon(icon='play', color='green'), popup='Старт').add_to(m)
    folium.Marker(location=end_point, icon=folium.Icon(icon='stop', color='red'), popup='Финиш').add_to(m)

    # Добавляем маркеры для достопримечательностей с названиями
    for attraction in attractions:
        lat, lon = map(float, attraction[0].split(','))
        if is_on_route(lat, lon, routes):
            folium.Marker(location=[lat, lon], icon=folium.Icon(color='orange'), popup=attraction[1]).add_to(m)

    figure.render()
    context = {
        'map': figure,
        'distance': distance  # Добавляем расстояние в контекст
    }
    return render(request, 'showroute.html', context)

def is_on_route(lat, lon, route):
    # Логика для проверки, находится ли точка (lat, lon) на маршруте
    for point in route:
        if distance(lat, lon, point[0], point[1]) <= 0.003:  # 3 метра
            return True
    return False

def distance(lat1, lon1, lat2, lon2):
    # Простейшая функция для вычисления расстояния между двумя точками
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
