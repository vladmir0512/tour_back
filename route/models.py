from django.db import models
from django.utils import timezone
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Route(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, default="Новый маршрут")
    comment = models.TextField(blank=False, null=False,default="Ваш комментарий")
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    distance = models.FloatField(default=0, validators=[MinValueValidator(0)])
    coords = models.CharField(max_length=1000, default="40.0,40.0,40.0,40.0")  
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    class Meta:
        db_table = "Маршрут"
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"
        
    def __str__(self):
        return f'Маршрут "{self.name}" для пользователя {self.user.username}'
