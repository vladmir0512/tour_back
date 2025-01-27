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
                return JsonResponse({'message': 'Пользователь создан', 'uid': user.uid})
            except Exception as e:
                return JsonResponse({'message': 'Пользователь с таким Email уже зарегистрирован.'})
            

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
               #print(user)
           
                print(user["email"])
                print(user["idToken"])
                print(user["localId"])
                print(user["refreshToken"])
                print(user["expiresIn"])
                return JsonResponse(user)
            except Exception as e:
                print(e)
                return JsonResponse({'message': str(e)})
        
