from django.shortcuts import render
from .models import CarouselImage

def carousel_view(request):
    images = CarouselImage.objects.order_by('-created_at')
    return render(request, 'carousel.html', {'images': images})
