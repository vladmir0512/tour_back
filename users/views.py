import os
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
import json
from conf.settings import FIREBASE_AUTH
from route.models import Route, User 
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from .serializers import RouteSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

class RegisterView(View):
    def post(self, request):
        if request.method == 'POST':
            data = json.loads(request.body)
            # Обработка данных
            response_data = {
                'message': 'Данные получены',
                'received_data': data
            }
            print(response_data)

            email = data["email"]
            password = data["password"]

            # в firebase отправляем
            try:
                # Создаем пользователя в Firebase
                firebase_user = FIREBASE_AUTH.create_user_with_email_and_password(email=email, password=password)
                
                # Создаем пользователя в Django модели User
                django_user = User.objects.create(
                    email=email,
                    firebase_user_id=firebase_user['localId'],
                    username=email.split('@')[0]  # Используем часть email как username
                )
                
                return JsonResponse({
                    'message': 'Пользователь создан',
                    'data': {
                        'firebase': firebase_user,
                        'django_user_id': django_user.id
                    }
                }, status=200, safe=False, json_dumps_params={'ensure_ascii': False})
                
            except Exception as e:
                print('Ошибка при создании пользователя: ' + str(e))
                # Если пользователь был создан в Firebase, но не в Django - удаляем его из Firebase
                if 'firebase_user' in locals():
                    try:
                        FIREBASE_AUTH.delete_user_account(firebase_user['idToken'])
                    except Exception as fb_error:
                        print('Ошибка при откате создания пользователя в Firebase: ' + str(fb_error))
                
                return JsonResponse({
                    'error': 'Ошибка при создании пользователя: ' + str(e)
                }, status=400, safe=False, json_dumps_params={'ensure_ascii': False})


class LoginView(View):
    def post(self, request):
        if request.method == 'POST':
            data = json.loads(request.body)
            # Обработка данных
            print(data)
            response_data = {
                'message': 'Данные получены',
                'received_data': data
            }
            print(response_data)
            email = data["email"]
            password = data["password"]

            # в firebase отправляем
            try:
                user = FIREBASE_AUTH.sign_in_with_email_and_password(email, password)
                kind = user["kind"]
                localId = user["localId"]
                email = user["email"]
                displayName = user["displayName"]
                idToken = user["idToken"]
                registred = user["registered"]
                refreshToken = user["refreshToken"]
                expiresIn = user["expiresIn"]
                # Получаем соответствующего пользователя Django
                try:
                    django_user = User.objects.get(firebase_user_id=localId)
                except User.DoesNotExist:
                    return JsonResponse({
                        'error': 'Пользователь не найден в системе'
                    }, status=404)
                
                return JsonResponse({

                    'message': 'Привет, \n' + user["email"],
                    'kind': kind,
                    'localId': localId,
                    'email': email,
                    'displayName': displayName,
                    'idToken': idToken,
                    'registred': registred,
                    'refreshToken': refreshToken,
                    'expiresIn': expiresIn,
                    'django_user_id': django_user.id
                }, status=200, safe=False, json_dumps_params={'ensure_ascii': False})

            except Exception as e:
                if str(e)[213:237] == 'INVALID_LOGIN_CREDENTIAL':
                    return JsonResponse({'error': 'Неверный логин или пароль:'}, status=400, safe=False, json_dumps_params={'ensure_ascii': False})
                else:
                    print('Ошибка при входе: ' + str(e)[213:237])
                    return JsonResponse({'error': 'Ошибка при входе: ' + str(e)[180:]}, status=400, safe=False, json_dumps_params={'ensure_ascii': False})

class UploadAvatarView(View):
    def post(self, request):
        if 'avatar' not in request.FILES or 'userId' not in request.POST:
            return JsonResponse({'error ': 'Отсутствуют необходимые данные (аватар или ID пользователя)'}, status=400)
        
        avatar = request.FILES['avatar']
        user_id = request.POST['userId']
        print("USER_ID:", user_id)  # Должно быть НЕ пустым!

        print(f"FILES: {request.FILES}")
        print(f"POST: {request.POST}")
        
        try:
            user = User.objects.get(firebase_user_id=user_id)
            
            new_filename = f"{user.email}_{avatar.name}"  # Новый формат имени файла
            
            # Сохраняем аватар
            file_path = default_storage.save(f'avatars/{new_filename}', ContentFile(avatar.read()))
            user.avatar = file_path
            user.save()
            print(f"Файл сохранён: {user.avatar}")
            
            # Формируем абсолютный URL аватара
            avatar_url = None
            if user.avatar:
                try:
                    avatar_url = request.build_absolute_uri(user.avatar.url)
                except Exception as e:
                    print(f"Ошибка получения avatar_url: {e}")


            return JsonResponse({'message': 'Аватар успешно загружен', 'avatar_url': avatar_url}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Пользователь не найден'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Ошибка загрузки изображения: {str(e)}'}, status=500)


class GetUserAvatarView(View):
    def get(self, request):
        user_id = request.GET.get('user_id', '').strip()
        print(f"USER_ID: '{user_id}' (type: {type(user_id)})")  # Выведем, что реально пришло

        if not user_id:
            return JsonResponse({'error': 'Не передан user_id'}, status=400)

        try:
            user = User.objects.filter(firebase_user_id=user_id).first()  # Используем first(), чтобы избежать ошибки
            if not user:
                print(f"Пользователь с firebase_user_id='{user_id}' не найден")
                return JsonResponse({'error': 'Пользователь не найден'}, status=404)

            
            avatar_url = request.build_absolute_uri(user.avatar.url) if user.avatar else None

            return JsonResponse({
                'email': user.email,
                'avatar_url': avatar_url
            }, status=200)

        except Exception as e:
            print(f"Ошибка запроса к БД: {e}")
            return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)

    # def get(self, request):
    #     user_id = request.GET.get('user_id')
    #     print(f"USER_ID: {user_id} (type: {type(user_id)})")  # Отладочный вывод

    #     if not user_id or user_id.strip() == "":
    #         return JsonResponse({'error': 'Не передан user_id'}, status=400)

    #     try:
    #         user = User.objects.filter(firebase_user_id=user_id).first()
    #         if not user:
    #             return JsonResponse({'error': 'Пользователь не найден'}, status=404)
    #         avatar_url = request.build_absolute_uri(user.avatar.url) if user.avatar else None

    #         return JsonResponse({
    #             'email': user.email,
    #             'avatar_url': avatar_url
    #         }, status=200)

    #     except User.DoesNotExist:
    #         return JsonResponse({'error': 'Пользователь не найден'}, status=404)

    # """История маршрутов пользователя (5 последних)"""

    # def get(self, request):
    #     routes = Route.objects.filter(user=request.user).order_by("-created_at")[:5]
    #     data = [
    #         {
    #             "id": route.id,
    #             "name": route.name,
    #             "description": route.description,
    #             "created_at": route.created_at.isoformat()
    #         }
    #         for route in routes
    #     ]
    #     return JsonResponse(data, safe=False)
    
@api_view(['GET'])
def get_routes(request):
    routes = Route.objects.all().order_by('-created_at')
    serializer = RouteSerializer(routes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_rating(request):
    try:
        data = json.loads(request.body)
        route_id = data.get("route_id")
        new_rating = data.get("rating")

        route = Route.objects.get(id=route_id)
        route.rating = new_rating
        route.save()

        return JsonResponse({"message": "Рейтинг обновлен!"}, status=200)
    except Route.DoesNotExist:
        return JsonResponse({"error": "Маршрут не найден"}, status=404)
    except:
        return JsonResponse({"error": "Неверный метод"}, status=400)