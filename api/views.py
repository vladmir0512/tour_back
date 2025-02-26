from rest_framework.decorators import api_view
from rest_framework.response import Response
from route.models import Route, User
from rest_framework import serializers
from rest_framework import status
from .serializers import RouteSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from urllib.parse import quote_plus
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
import requests, time


#-----------------------ROUTES---------------------------------
#-info---------------------------------------------------------
@api_view(['GET'])
def ApiRouteOverview(request):
	api_urls = {
		'all_routes': '/list',
		'Add': '/create',
		'Update': '/update/pk',
		'Delete': '/route/pk/delete'
	}

	return Response(api_urls)

#-create-------------------------------------------------------
@api_view(['POST'])
def add_route(request):
    firebase_user_id = request.data.get('firebase_user_id')  # Получаем Firebase ID из запроса
    try:
        user = User.objects.get(firebase_user_id=firebase_user_id)  # Находим пользователя по firebase_user_id
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    # Создаем данные для маршрута
    route_data = {
        "name": request.data.get("name", "Новый маршрут"),
        "user": user.id,  # Используем только ID пользователя, а не сам объект
        "coords": request.data.get("coords", ""),
        "distance": request.data.get("distance", "")
    }

    route_serializer = RouteSerializer(data=route_data)
    if route_serializer.is_valid():
        route_serializer.save()
        return Response(route_serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(route_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#-update-------------------------------------------------------    
@api_view(['POST'])
def update_route(request, pk):
    route = Route.objects.get(pk=pk)
    data = RouteSerializer(instance=route, data=request.data)

    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

#-delete-------------------------------------------------------    
@api_view(['DELETE'])
def delete_route(request, pk):
    route = get_object_or_404(Route, pk=pk)
    route.delete()
    return Response(status=status.HTTP_202_ACCEPTED)
    
#-all----------------------------------------------------------    
@api_view(['GET'])
def view_routes(request):

    # checking for the parameters from the URL
    if request.query_params:
        route = Route.objects.filter(**request.query_params.dict())
    else:
        routes = Route.objects.all()

    # if there is something in items else raise error
    if routes:
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    


#-------------------------USERS--------------------------------
#-info---------------------------------------------------------
@api_view(['GET'])
def ApiUserOverview(request):
	api_urls = {
		'all_users': '/list',
		'Add': '/create',
		'Update': '/update/pk',
		'Delete': '/delete/pk'
	}

	return Response(api_urls)

#-create-------------------------------------------------------
@api_view(['POST'])
def add_user(request):
    user = UserSerializer(data=request.data)

    # validating for already existing data
    if User.objects.filter(**request.data).exists():
        raise serializers.ValidationError('This data already exists')

    if user.is_valid():
        user.save()
        return Response(user.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
#-update-------------------------------------------------------    
@api_view(['POST'])
def update_user(request, pk):
    user = User.objects.get(pk=pk)
    data = UserSerializer(instance=user, data=request.data)

    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

#-delete-------------------------------------------------------    
@api_view(['DELETE'])
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return Response(status=status.HTTP_202_ACCEPTED)
        
#-all----------------------------------------------------------        
@api_view(['GET'])
def view_users(request):

    # checking for the parameters from the URL
    if request.query_params:
        user = User.objects.filter(**request.query_params.dict())
    else:
        users = User.objects.all()

    # if there is something in items else raise error
    if users:
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    



#--------------------SEARCH_ADDRESS----------------------------
#-for-android-editText 
@api_view(['GET'])
def search_address(request):
    query = request.GET.get("query")  # Получаем параметр `query` из запроса
    api_key = 'pk.52083ea2e7c376a3859b2d5c34fee622'  # Вставьте свой API-ключ
    url = f'https://us1.locationiq.com/v1/search?key={api_key}&q={query}&format=json'
    
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and isinstance(data, list) and len(data) > 0:
            result = data[0]
            lat, lon = result["lat"], result["lon"]
            return Response({"lat": lat, "lon": lon, "address": result["display_name"]}, status=200)
        else:
            return Response({"error": "No results found"}, status=404)
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=500)
    
