from django.db import models
from users.models import CustomUser, User
from django.utils import timezone


class Route(models.Model):
    name = models.CharField(max_length=20, blank=False, null=False, default="Новый маршрут")
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    distance = models.FloatField(max_length=10, default=0)
    coords = models.CharField(max_length=1000, default="40.0,40.0,40.0,40.0")
    
    class Meta:
        db_table = "Маршрут"
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"
    def __str__(self):
        return f'Маршрут \"{self.name}\"'
    
class Comment(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    text = models.TextField(default="Ваш комментарий")
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "Комментарий"
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
    def __str__(self):
        return f'Комментарий пользователя \"{self.user.username}\" на маршруте \"{self.route}\"'
    
