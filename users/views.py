from django.http import JsonResponse
from django.views import View
import firebase_admin
from firebase_admin import auth

class RegisterView(View):
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = auth.create_user(email=email, password=password)
            return JsonResponse({'message': 'User  created successfully', 'uid': user.uid})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class LoginView(View):
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = auth.get_user_by_email(email)
            # Здесь вы можете добавить проверку пароля, но Firebase Admin SDK не поддерживает это
            return JsonResponse({'message': 'User  logged in successfully', 'uid': user.uid})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

