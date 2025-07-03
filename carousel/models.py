# Create your models here.
from django.db import models

class CarouselImage(models.Model):
    image = models.ImageField(upload_to='carousel/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"
