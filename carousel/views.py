from .models import CarouselImage
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CarouselImageForm
from django.utils import timezone

def carousel_view(request):
    today = timezone.now().date()
    images = CarouselImage.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).order_by('-created_at')
    
    return render(request, 'carousel.html', {'images': images})


def superadmib_view(request):
    images = CarouselImage.objects.all().order_by('-created_at')

    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('superadmib')
    else:
        form = CarouselImageForm()

    return render(request, 'superadmib.html', {
        'images': images,
        'form': form
    })

def delete_carousel_image(request, image_id):
    image = get_object_or_404(CarouselImage, id=image_id)
    image.delete()
    return redirect('superadmib')
