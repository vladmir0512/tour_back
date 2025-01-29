from django.http import JsonResponse
from django.views import View
import json
from conf.settings import FIREBASE_AUTH

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
                user = FIREBASE_AUTH.create_user_with_email_and_password(email=email, password=password)
                return JsonResponse({'message': 'Пользователь создан', 'data': user},status=200, safe=False, json_dumps_params={'ensure_ascii': False})
            except Exception as e:
                print('Ошибка при создании пользователя: ' + str(e))
                return JsonResponse({'error': 'Ошибка при создании пользователя: ' + str(e)}, status=400,safe=False, json_dumps_params={'ensure_ascii': False})

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
                return JsonResponse({'message': 'Привет, \n' + user["email"],
                                    'kind': kind,
                                    'localId': localId,
                                    'email': email,
                                    'displayName': displayName,
                                    'idToken': idToken,
                                    'registred': registred,
                                    'refreshToken': refreshToken,
                                    'expiresIn': expiresIn}, status=200, safe=False, json_dumps_params={'ensure_ascii': False})
            except Exception as e:
                if str(e)[213:237] == 'INVALID_LOGIN_CREDENTIAL':
                    return JsonResponse({'error': 'Неверный логин или пароль:'}, status=400, safe=False, json_dumps_params={'ensure_ascii': False})
                else:
                    print('Ошибка при входе: ' + str(e)[213:237])
                    return JsonResponse({'error': 'Ошибка при входе: ' + str(e)[180:]}, status=400, safe=False, json_dumps_params={'ensure_ascii': False})
