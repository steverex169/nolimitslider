from django.db import models
from django.utils import timezone

class CarouselImage(models.Model):
    image = models.ImageField(upload_to='carousel/')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    terms = models.TextField(blank=True, null=True)

    @property
    def status(self):
        today = timezone.now().date()
        if self.start_date and self.end_date:
            if self.start_date <= today <= self.end_date:
                return "Active"
            elif today > self.end_date:
                return "Expired"
            else:
                return "Upcoming"
        return "No Schedule"
