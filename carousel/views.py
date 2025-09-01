from .models import CarouselImage
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CarouselImageForm
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import logout

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('superadmin')
            else:
                return redirect('carousel')  # Or any other page for non-superusers
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')



# 2. PUBLIC VIEW FOR CAROUSEL
def carousel_view(request):
    today = timezone.now().date()
    images = CarouselImage.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).order_by('-created_at')
    
    return render(request, 'carousel.html', {'images': images})


@login_required(login_url='/login/')  # 👈 This will redirect unauthenticated users
def superadmin_view(request):
    images = CarouselImage.objects.all().order_by('-created_at')

    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES)
        if form.is_valid():
            if request.POST.get('action') == 'preview':
                # Store temporarily in session
                request.session['preview_data'] = {
                    'image': request.FILES['image'].name if 'image' in request.FILES else '',
                    'start_date': form.cleaned_data['start_date'].isoformat(),
                    'end_date': form.cleaned_data['end_date'].isoformat(),
                    'terms': form.cleaned_data['terms'],
                }
                request.session['preview_image'] = request.FILES['image'].read()
                request.session['preview_image_name'] = request.FILES['image'].name
                return redirect('preview_terms')
            else:
                form.save()
                return redirect('superadmin')
    else:
        form = CarouselImageForm()

    return render(request, 'superadmin.html', {
        'images': images,
        'form': form
    })



@login_required(login_url='/login/')  # 👈 Redirects to login if not logged in
def delete_carousel_image(request, image_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to delete images.")

    image = get_object_or_404(CarouselImage, id=image_id)
    image.delete()
    return redirect('superadmin')

def edit_carousel_image(request, image_id):
    image = get_object_or_404(CarouselImage, pk=image_id)

    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect('superadmin')  # redirect to your list page
    else:
        form = CarouselImageForm(instance=image)

    return render(request, 'carousel/edit_image.html', {'form': form, 'image': image})

def logout_view(request):
    logout(request)
    return redirect('login')

import base64

def preview_terms_view(request):
    data = request.session.get('preview_data')
    image_data = request.session.get('preview_image')
    image_name = request.session.get('preview_image_name')

    if not data or not image_data:
        return redirect('superadmin')

    image_base64 = base64.b64encode(image_data).decode('utf-8')
    mime_type = "image/jpeg" if image_name.lower().endswith(('jpg', 'jpeg')) else "image/png"

    return render(request, 'preview_terms.html', {
        'image_data_url': f"data:{mime_type};base64,{image_base64}",
        'start_date': data['start_date'],
        'end_date': data['end_date'],
        'terms_html': data['terms'],
    })
from django.shortcuts import render, get_object_or_404
from .models import CarouselImage

def carousel_image_detail(request, image_id):
    # Yahan pk + image_type filter dono lagayenge
    image = get_object_or_404(CarouselImage, pk=image_id, image_type="banner")
    
    return render(request, 'preview_terms.html', {'image': image})

def general_termscondition(request):
    return render(request, 'generalT&C.html')
def general_AboutUs(request):
    return render(request, 'AboutUs.html')
def promotion(request):
    return render(request, 'promotion.html')
def promotion1(request):
    return render(request, 'promotion1.html')
def promotion2(request):
    return render(request, 'promotion2.html')
def promotion3(request):
    return render(request, 'promotion3.html')
def promotion4(request):
    return render(request, 'promotion4.html')
def promotion5(request):
    return render(request, 'promotion5.html')
def promotion6(request):
    return render(request, 'promotion6.html')
def promotion7(request):
    return render(request, 'promotion7.html')
def promotion8(request):
    return render(request, 'promotion8.html')
def promotion9(request):
    return render(request, 'promotion9.html')
def promotion10(request):
    return render(request, 'promotion10.html')
def licence(request):
    return render(request, 'licence.html')

def post_gallery(request):
    images = CarouselImage.objects.filter(image_type="post").order_by('-created_at')
    return render(request, "post_gallery.html", {"images": images})
