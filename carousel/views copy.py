from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import *
import uuid
from django.utils import timezone
from django.shortcuts import redirect
import requests
from urllib.parse import urlencode
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import unquote
from django.urls import reverse
from rest_framework import status
import stripe
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.db.models import Q, Sum, Count
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from datetime import datetime, timedelta
from .send_mail import *
import random
import uuid
import string
from django.core.mail import send_mail
import threading
import json
from django.db.models import Count
from django.shortcuts import render
from .models import Product, Category
from datetime import datetime
from collections import defaultdict
from django.db.models import Q
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.timezone import now
from django.shortcuts import render, redirect
from .models import Contact
from .models import Product
from django.db.models import Count

# Telegram settings
BOT_TOKEN = "7950411129:AAF2_3BdK3b7ECeWYujpbkjojRlQwngoZ5A"
CHANNEL_ID = -1002720699144

def post_to_channel(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    try:
        response = requests.post(url, data=data).json()
        print("Telegram response:", response)
        if not response.get("ok"):
            print("Telegram Error:", response)
    except Exception as e:
        print("Telegram message failed:", e)

ADMIN_EMAIL = "joeytunes2@gmail.com"


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        user = request.user
        user.last_visit = datetime.now()
        user.save()
        
    # products = Product.objects.all()
    latest_message = None
    if Config.objects.get(key='SESSIONS_STATE').value == 'ON':    
        latest_message = Message.objects.last()
        
    try:
        feedme = Feedme.objects.get()
    except:
        feedme = Feedme.objects.create()
        feedme.save()
    
    if request.session.get("visited"):
        last_visited = request.session.get("last_visited")
        last_visited_datetime = datetime.strptime(last_visited, "%Y-%m-%d %H:%M:%S")
        datetime_now = datetime.now()
        
        if (datetime_now - last_visited_datetime).seconds >= 60*1:
            feedme.visitors += 1
            feedme.save()
        
            now = datetime.now()
            week_of_year = now.isocalendar()[1]
            month_of_year = now.month
            year = now.year
            
            weeklyVisitors = WeeklyVisitors.objects.get_or_create(
                week = week_of_year,
                month = month_of_year,
                year = year
            )
            weeklyVisitors = weeklyVisitors[0]
            weeklyVisitors.visitors += 1
            weeklyVisitors.save()
            
            request.session['last_visited'] = str(datetime.now()).split(".")[0]
        
    else:
        request.session['last_visited'] = str(datetime.now()).split(".")[0]
        
        feedme.visitors += 1
        feedme.save()
        
        now = datetime.now()
        week_of_year = now.isocalendar()[1]
        month_of_year = now.month
        year = now.year
        
        weeklyVisitors = WeeklyVisitors.objects.get_or_create(
            week = week_of_year,
            month = month_of_year,
            year = year
        )
        weeklyVisitors = weeklyVisitors[0]
        weeklyVisitors.visitors += 1
        weeklyVisitors.save()
        
    request.session['visited'] = "Yes"
    
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    context = {
        'latest_message': latest_message,
        'products': products,
        }
    return render(request, 'home.html', context=context)

def shop(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'shop.html', {'products': products})

def home2(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'home2.html', {'products': products})



def aboutdetail1(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'aboutdetial1.html',{'products': products})



def aboutdetail2(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'aboutdetial2.html', {'products': products})



def down(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'down.html', {'products': products})

def fetch_latest_news_tweets(request):
    newstweets = Tweet.objects.filter(group__group="Latest News").order_by('-created_at')[:3]
    news_list = [
        {
            'tweet_url': tweet.tweet_url,
            'tweet_text': tweet.tweet_text,
        }
        for tweet in newstweets
    ]
    return JsonResponse({'newstweets': news_list})

from datetime import datetime, timedelta, date
from django.db.models import Max
from django.utils.timezone import localdate

def home3(request):
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)

    latest_messages = []
    last_message = None

    if not Config.objects.filter(key='SESSIONS_STATE').exists():
        Config.objects.create(key='SESSIONS_STATE', value='OFF')

    latest_date = Message.objects.filter(results="pending", is_free=True).aggregate(
        max_date=Max('created_at')
    )['max_date']
    
    latest_messages = []
    
    if latest_date:
        # Step 2: Get all messages created on that latest date
        latest_messages = Message.objects.filter(
            results="pending",
            is_free=True,
            created_at__date=latest_date.date()
        ).order_by('-created_at')


    try:
        feedme = Feedme.objects.get()
    except:
        feedme = Feedme.objects.create()

    if request.session.get("visited"):
        last_visited = request.session.get("last_visited")
        last_visited_datetime = datetime.strptime(last_visited, "%Y-%m-%d %H:%M:%S")
        datetime_now = datetime.now()
        
        if (datetime_now - last_visited_datetime).seconds >= 60*1:
            feedme.visitors += 1
            feedme.save()

            now = datetime.now()
            week_of_year = now.isocalendar()[1]
            month_of_year = now.month
            year = now.year

            if request.session.get("last_daily_reset") != str(date.today()):
                # New day – reset daily counter
                feedme.daily_visitors = 1
                request.session["last_daily_reset"] = str(date.today())
            else:
                feedme.daily_visitors += 1

            feedme.save()
            
            weeklyVisitors = WeeklyVisitors.objects.get_or_create(
                week=week_of_year,
                month=month_of_year,
                year=year
            )
            weeklyVisitors = weeklyVisitors[0]
            weeklyVisitors.visitors += 1
            weeklyVisitors.save()
            
            request.session['last_visited'] = str(datetime.now()).split(".")[0]
        
    else:
        request.session['last_visited'] = str(datetime.now()).split(".")[0]
        feedme.visitors += 1
        feedme.save()

        now = datetime.now()
        week_of_year = now.isocalendar()[1]
        month_of_year = now.month
        year = now.year
        
        weeklyVisitors = WeeklyVisitors.objects.get_or_create(
            week=week_of_year,
            month=month_of_year,
            year=year
        )
        weeklyVisitors = weeklyVisitors[0]
        weeklyVisitors.visitors += 1
        weeklyVisitors.save()

    request.session['visited'] = "Yes"

    # ✅ Sports Betting Logic (Merged)
    full_records = SportsBet.objects.filter(date__year=2025).exclude(result="pending").order_by('date')

    total_losses_by_sport = defaultdict(int)
    total_wins_by_sport = defaultdict(int)
    total_sport = {}

    for record in full_records:
        if len(record.sport.strip()) <= 1:
            continue
        sport = record.sport.upper()
        if sport not in total_sport:
            total_sport[sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units': 0}

        if record.result.lower() == 'loss':
            total_losses_by_sport[sport] += 1
            total_sport[sport]['loss'] += 1
        elif record.result.lower() == 'win':
            total_wins_by_sport[sport] += 1
            total_sport[sport]['win'] += 1

        if record.total_earn is not None and record.risk:
            try:
                risk = float(record.risk)
                if risk == 0:
                    risk = 1
                roi = float(record.total_earn) / risk
                total_units = float(record.total_earn) / 100

                total_sport[sport]['roi'] += round(roi, 2)
                total_sport[sport]['total_units'] += round(total_units, 2)
            except ValueError:
                # skip this record if risk or total_earn is not a valid float
                pass

        total_sport[sport]['roi'] = round(total_sport[sport]['roi'], 2)
        total_sport[sport]['total_units'] = round(total_sport[sport]['total_units'], 2)

    # Add missing sports
    for key in set(total_losses_by_sport) | set(total_wins_by_sport):
        total_sport.setdefault(key, {'loss': 0, 'win': 0, 'roi': 0, 'total_units': 0})

    total_losses_by_sport = dict(sorted(total_losses_by_sport.items()))
    total_wins_by_sport = dict(sorted(total_wins_by_sport.items()))

    today = datetime.today().date()
    session_records = full_records.filter(date=today)
    session_total_wins = sum(1 for r in session_records if r.result.lower() == 'win')
    session_total_losses = sum(1 for r in session_records if r.result.lower() == 'loss')
    session_total = session_total_wins + session_total_losses or 1

    session_stats = {
        'win_percentage': round((session_total_wins / session_total) * 100, 1),
        'loss_percentage': round((session_total_losses / session_total) * 100, 1)
    }

    roi_values = [s['roi'] for s in total_sport.values() if s['roi'] != 0]
    global_stats = {
        'roi': round(sum(roi_values) / len(roi_values), 2) if roi_values else 0,
        'total_units': round(sum(s['total_units'] for s in total_sport.values()), 2),
        'total_wins': sum(s['win'] for s in total_sport.values()),
        'total_losses': sum(s['loss'] for s in total_sport.values())
    }

    tweets = Tweet.objects.order_by('-created_at')[:200]

    context = {
        'latest_messages': latest_messages,
        'products': products,
        'tweets': tweets,
        'global_stats': global_stats,
        'session_stats': session_stats,
        'records': full_records,
        'total_sports': total_sport,
        'year': '2025',
        'total_losses_by_sport': total_losses_by_sport,
        'total_wins_by_sport': total_wins_by_sport,
    }

    return render(request, 'home3.html', context)




def about2(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'about2.html', {'products': products})



# def shop2(request):
#     products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
#     categories = Category.objects.all()  # ✅ Categories bhi bhej dein

#     return render(request, 'shop2.html', {'products': products, 'categories': categories})  # ✅ Sirf ek dictionary pass karein

def shop2(request):
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    categories = Category.objects.all()

    user_group = Tweet.objects.first()

    if user_group and user_group.group and user_group.group.group:
        group_part = user_group.group.group.strip("-").lower().split(" ")[0]
        print("konsa group in if", group_part)
    else:
        group_part = ""
        print("konsa group", group_part)



    user_ids = FilterRecord.objects.filter(
        group__icontains=group_part
    ).values_list('user__id', flat=True)

    print(f"Filtered User IDs: {user_ids}")

    target_users = [str(user_id) for user_id in user_ids]
    print(f"Target Users: {target_users}")
    

    # ✅ Group categories by `main_catagory`
    grouped_categories = defaultdict(list)
    for category in categories:
        grouped_categories[category.main_catagory].append(category)

    return render(request, 'shop2.html', {
        'products': products,
        'grouped_categories': dict(grouped_categories)  # ✅ Convert defaultdict to normal dict
    })


def productDetail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.exclude(id = product_id)
    return render(request, 'shopdetail2.html', {'product': product, 'related_products': related_products})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def contact2(request):
    if request.method == 'POST':
        ip = get_client_ip(request)
        cache_key = f"contact_form_{ip}"

        if cache.get(cache_key):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'You have already submitted today.'})
            return render(request, 'contact2.html', {'error': 'You have already submitted today.'})

        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        Contact.objects.create(name=name, email=email, message=message)
        cache.set(cache_key, True, timeout=86400)

        # ✅ Return JSON for AJAX, redirect only for normal form
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        else:
            return redirect('home3')

    # GET request
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    return render(request, 'contact2.html', {'products': products})


def forget(request):
    return render(request, 'forgetpassword.html')

def CBD(request):
    products = Product.objects.filter(category=Category.objects.get(name='CBD'))
    return render(request, 'CBD.html', {'products': products})

def about(request):
    return render(request, 'about.html')

def loginPage(request):
    context = {}
    if request.method == "POST":
        print("its post")
        
        username = request.POST.get('username')
        print("its post name", request.POST.get('username'))
        password = request.POST.get('password')
        print("its post name", request.POST.get('password'))
        
        username = username.strip()
        password = password.strip()
        
        # username = username.lower()
        print("detail", username, password, username)
        
        user = authenticate(request,username=username,password=password)

        print("usre is", user)
        
        if user is not None:
            auth_login(request, user)
            if user.is_superuser:
                return redirect("dashboard")
            return redirect('home3')
            # If authentication is successful, log the user in
        else:
            context = {
                "error": "Incorrect Username or Password"
            }        
        
    return render(request, 'loginPage.html', context)

def login(request):
    
    if request.method == "POST":
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        username = username.strip()
        password = password.strip()
        
        username = username.lower()
        
        user = authenticate(request,username=username,password=password)
        if user is not None:
            # If authentication is successful, log the user in
            auth_login(request, user)
            return redirect('BOT2')
        
    return redirect('home')

def chat(request):
    print(Config.objects.get(key='SESSIONS_STATE').value)
    state = True if Config.objects.get(key='SESSIONS_STATE').value == 'ON' else False
    messages = Message.objects.filter(is_free=True).order_by('-created_at')
    print(state)
    return render(request, 'chat.html', {'messages': messages, 'state': state})

from django.contrib import messages as django_messages
@login_required
def premiumchat(request):
    try:
        # Get SESSIONS_STATE config and determine if sessions are enabled
        config = Config.objects.get(key='SESSIONS_STATE')
        state = config.value == 'ON'
    except Config.DoesNotExist:
        state = False
        django_messages.error(request, "Configuration for SESSIONS_STATE not found.")
    
    try:
        user_instance = UserModel.objects.get(username=request.user)
    except UserModel.DoesNotExist:
        django_messages.error(request, "User does not exist.")
        return render(request, 'premiumplays.html', {'messages': [], 'state': state})


    # Fetch messages based on the user's plan
    plan = user_instance.plays_plan
    messages_queryset = Message.objects.none()
    if plan == 'full_yearly':
        messages_queryset = Message.objects.filter(
            Q(is_nfl=True) | Q(is_cfb=True)
        )
    elif plan == 'monthly':
        messages_queryset = Message.objects.filter(is_monthly=True,)
    elif plan == 'seasonal_nfl':
        messages_queryset = Message.objects.filter(is_nfl=True,)
    elif plan == 'seasonal_cfb':
        messages_queryset = Message.objects.filter(is_cfb=True,)
    elif plan == 'seasonal_both':
        messages_queryset = Message.objects.filter(Q(is_nfl=True) | Q(is_cfb=True))

    messages_queryset = messages_queryset.order_by('-created_at')

    if user_instance.plays_start_date and user_instance.plays_pkg_days > 0:
        expiry_date = user_instance.plays_start_date + timedelta(days=user_instance.plays_pkg_days)
        if date.today() > expiry_date:
            user_instance.plays_pkg_days = 0
            user_instance.save()

    return render(request, 'premiumplays.html', {
        'messages': messages_queryset,
        'state': state
    })
# def register(request):
#     return render(request, 'register.html')

def product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product.html', {'product': product})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

def product_list(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'product_list.html', {'products': products})

def contact(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        message = request.POST.get('message')

        Contact.objects.create(email=email, name=name, message=message)

        # send_email('feedme@feedme.bet', email, name, message)
        # send_email('devmustafa4@gmail.com', email, name, message)
        return redirect('home')
    return render(request, 'contact.html')

def ourteam(request):
    return render(request, 'ourteam.html')

def record2020(request):
    records = SportsBet.objects.filter(date__year=2020).order_by('-date')
    # Create dictionaries to store total losses and wins for each sport
    total_losses_by_sport = defaultdict(int)
    total_wins_by_sport = defaultdict(int)
    total_roi_by_sport = defaultdict(int)
    total_sport = {}

    for record in records:
        if len(record.sport) <= 1:
            continue
        if record.result.lower() == 'loss':
            total_losses_by_sport[record.sport] += 1
            
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['loss'] += 1
        elif record.result.lower() == 'win':
            total_wins_by_sport[record.sport] += 1
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['win'] += 1
            
        total_sport[record.sport]['roi'] += round( float(record.total_earn) /(float(record.risk) - 1) ,2)
        total_sport[record.sport]['total_units'] += round(float(record.total_earn)/100 ,2)
        total_sport[record.sport]['total_units'] = round(total_sport[record.sport]['total_units'],2)

        total_roi_by_sport[record.sport] =  round((float(record.total_earn) / float(record.risk))*100 ,0)
        total_sport[record.sport]['roi'] = round(total_sport[record.sport]['roi'],2)

    for key,value in total_losses_by_sport.items():
        if key not in total_wins_by_sport:
            total_wins_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            
    for key,value in total_wins_by_sport.items():
        if key not in total_losses_by_sport:
            total_losses_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}

    for key,value in total_sport.items():
        # calculate win percentage
        total_sport[key]['win_percentage'] = round((total_sport[key]['win'] / (total_sport[key]['win'] + total_sport[key]['loss'])) * 100, 1)

    # sort the dictionaries by keys (sport names) in alphabetical order
    total_losses_by_sport = sorted(total_losses_by_sport.items(), key=lambda x: x[0])
    total_wins_by_sport = sorted(total_wins_by_sport.items(), key=lambda x: x[0])
    total_roi_by_sport = sorted(total_roi_by_sport.items(), key=lambda x: x[0])
    
    return render(request, 'record.html', {'records': records, 'total_roi_by_sport': dict(total_roi_by_sport), 'year': '2020', 'total_sport': total_sport, 'total_losses_by_sport': dict(total_losses_by_sport), 'total_wins_by_sport': dict(total_wins_by_sport)})


def record2021(request):
    records = SportsBet.objects.filter(date__year=2021).order_by('-date')
    # Create dictionaries to store total losses and wins for each sport
    total_losses_by_sport = defaultdict(int)
    total_wins_by_sport = defaultdict(int)
    total_roi_by_sport = defaultdict(int)
    total_sport = {}

    for record in records:
        if len(record.sport) <= 1:
            continue
        if record.result.lower() == 'loss':
            total_losses_by_sport[record.sport] += 1
            
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['loss'] += 1
        elif record.result.lower() == 'win':
            total_wins_by_sport[record.sport] += 1
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['win'] += 1
            
        total_sport[record.sport]['roi'] += round( float(record.total_earn) /(float(record.risk) - 1) ,2)
        total_sport[record.sport]['total_units'] += round(float(record.total_earn)/100 ,2)
        total_sport[record.sport]['total_units'] = round(total_sport[record.sport]['total_units'],2)

            
        total_roi_by_sport[record.sport] =  round((float(record.total_earn) / float(record.risk))*100 ,0)
        total_sport[record.sport]['roi'] = round(total_sport[record.sport]['roi'],2)

    for key,value in total_losses_by_sport.items():
        if key not in total_wins_by_sport:
            total_wins_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            
    for key,value in total_wins_by_sport.items():
        if key not in total_losses_by_sport:
            total_losses_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}

    for key,value in total_sport.items():
        # calculate win percentage
        total_sport[key]['win_percentage'] = round((total_sport[key]['win'] / (total_sport[key]['win'] + total_sport[key]['loss'])) * 100, 1)
    
    # sort the dictionaries by keys (sport names) in alphabetical order
    total_losses_by_sport = sorted(total_losses_by_sport.items(), key=lambda x: x[0])
    total_wins_by_sport = sorted(total_wins_by_sport.items(), key=lambda x: x[0])
    total_roi_by_sport = sorted(total_roi_by_sport.items(), key=lambda x: x[0])
    
    return render(request, 'record.html', {'records': records, 'total_roi_by_sport': dict(total_roi_by_sport),  'year': '2021', 'total_sport': total_sport, 'total_losses_by_sport': dict(total_losses_by_sport), 'total_wins_by_sport': dict(total_wins_by_sport)})


def record2022(request):
    records = SportsBet.objects.filter(date__year=2022).order_by('-date')
    # Create dictionaries to store total losses and wins for each sport
    total_losses_by_sport = defaultdict(int)
    total_wins_by_sport = defaultdict(int)
    total_roi_by_sport = defaultdict(int)
    total_sport = {}

    for record in records:
        if len(record.sport) <= 1:
            continue
        if record.result.lower() == 'loss':
            total_losses_by_sport[record.sport] += 1
            
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['loss'] += 1
        elif record.result.lower() == 'win':
            total_wins_by_sport[record.sport] += 1
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['win'] += 1
            
        total_sport[record.sport]['roi'] += round( float(record.total_earn) /(float(record.risk) - 1) ,2)
        total_sport[record.sport]['total_units'] += round(float(record.total_earn)/100 ,2)
        total_sport[record.sport]['total_units'] = round(total_sport[record.sport]['total_units'],2)
            
        total_roi_by_sport[record.sport] =  round((float(record.total_earn) / float(record.risk))*100 ,2)

        total_sport[record.sport]['roi'] = round(total_sport[record.sport]['roi'],2)

    for key,value in total_losses_by_sport.items():
        if key not in total_wins_by_sport:
            total_wins_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            
    for key,value in total_wins_by_sport.items():
        if key not in total_losses_by_sport:
            total_losses_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}

    for key,value in total_sport.items():
        # calculate win percentage
        total_sport[key]['win_percentage'] = round((total_sport[key]['win'] / (total_sport[key]['win'] + total_sport[key]['loss'])) * 100, 1)
    
    # sort the dictionaries by keys (sport names) in alphabetical order
    total_losses_by_sport = sorted(total_losses_by_sport.items(), key=lambda x: x[0])
    total_wins_by_sport = sorted(total_wins_by_sport.items(), key=lambda x: x[0])
    total_roi_by_sport = sorted(total_roi_by_sport.items(), key=lambda x: x[0])
    
    return render(request, 'record.html', {'records': records, 'total_sport': total_sport, 'total_roi_by_sport': dict(total_roi_by_sport),   'year': '2022', 'total_losses_by_sport': dict(total_losses_by_sport), 'total_wins_by_sport': dict(total_wins_by_sport)})


def lifetime(request):
    records = SportsBet.objects.all().order_by('-date')
    # Create dictionaries to store total losses and wins for each sport
    total_losses_by_sport = defaultdict(int)
    total_wins_by_sport = defaultdict(int)
    total_roi_by_sport = defaultdict(int)
    total_sport = {}

    for record in records:
        if len(record.sport) <= 1:
            continue
        if record.result.lower() == 'loss':
            total_losses_by_sport[record.sport] += 1
            
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['loss'] += 1
        elif record.result.lower() == 'win':
            total_wins_by_sport[record.sport] += 1
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['win'] += 1
            
        # check if value is not none
        if record.total_earn and record.risk:
            total_sport[record.sport]['roi'] += round( float(record.total_earn) /(float(record.risk) - 1) ,0)
            total_sport[record.sport]['total_units'] += round(float(record.total_earn)/100 ,2)
            total_sport[record.sport]['total_units'] = round(total_sport[record.sport]['total_units'],2)
        print(record.total_earn , record.risk)

            
        total_roi_by_sport[record.sport] = 3

    for key,value in total_losses_by_sport.items():
        if key not in total_wins_by_sport:
            total_wins_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            
    for key,value in total_wins_by_sport.items():
        if key not in total_losses_by_sport:
            total_losses_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}

    for key,value in total_sport.items():
        # calculate win percentage
        total_sport[key]['win_percentage'] = round((total_sport[key]['win'] / (total_sport[key]['win'] + total_sport[key]['loss'])) * 100, 1)
        
    # sort the dictionaries by keys (sport names) in alphabetical order
    total_losses_by_sport = sorted(total_losses_by_sport.items(), key=lambda x: x[0])
    total_wins_by_sport = sorted(total_wins_by_sport.items(), key=lambda x: x[0])
    total_roi_by_sport = sorted(total_roi_by_sport.items(), key=lambda x: x[0])
    
    return render(request, 'record.html', {'records': records, 'total_roi_by_sport': dict(total_roi_by_sport),   'year': 'all', 'total_sport': total_sport, 'total_losses_by_sport': dict(total_losses_by_sport), 'total_wins_by_sport': dict(total_wins_by_sport)})


def send_email(recipient, email, name, message):
    try:
        print("Sending email to " + recipient)
        subject = 'Contact Form Submission'
        from django.core.mail import send_mail

        send_mail(
            subject,
            f'User {name} with email {email} sent the following message:\n{message}',
            'Feedme Contact Form <feedme@feedme.bet>',
            [recipient],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Could not send email: {e}")


def cart(request): 
    cart = request.session.get('cart')
    if cart is None:
        cart = {}

    total = 0
    cart_items_list = []  # ✅ initialize before loop

    for key in cart:
        value = ProductVariation.objects.get(id=key)
        print("yaha kya  a raha h", value)
        image = ProductImage.objects.filter(product__id=value.product.id).first()
        print("yaha kya  a raha h", image)

        image_url = image.image.url if image else ""  # handle case when no image found

        value = value.to_json()
        quantity = 1
        if isinstance(cart[key], dict) and cart[key].get('quantity'):
            quantity = cart[key]['quantity']
        
        cart[key] = {
            'image': image_url,
            'quantity': quantity,
            'product': value,
            'size': cart[key]['size'],
            'total': float(value['price']) * float(quantity)
        }
        cart_items_list.append(cart[key])  # ✅ append each item

        total += float(cart[key]['total'])

    request.session['cart'] = cart
    return render(
        request, 
        'cart.html', 
        {'cart_items': cart, 'total': total, 'cart_items_list': cart_items_list}
    )


def add_to_cart(request):
    if request.method == 'POST':
        variation = request.POST.get('variation')
        quantity = int(request.POST.get('quantity', 1))  # convert to int
        size = request.POST.get('size', 'M')
        product = ProductVariation.objects.get(id=variation).to_json()
        
        cart = request.session.get('cart', {})

        if variation in cart:
            cart[variation]['quantity'] += quantity
        else:
            cart[variation] = {
                'quantity': quantity,
                'product': product,
                'size': size,
                'total': float(product['price']) * quantity
            }

        request.session['cart'] = cart
        return redirect('cart')

    return redirect('cart')



@csrf_exempt
def create_tweet(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        tweet_text = request.POST.get('tweet_text')
        tweet_url = request.POST.get('tweet_url')
        group_url = request.POST.get('group_url')
        group_name = request.POST.get('group_name')

        existing_tweet = Tweet.objects.filter(tweet_url=tweet_url).first()
        if existing_tweet:
            return JsonResponse({'message': 'Tweet already exists'}, status=400)

        # Get or create group safely
        group = Group.objects.filter(group_link=group_url).first()
        if not group:
            group = Group.objects.create(group=group_name, group_link=group_url, is_running = True)
        else:
            group.is_running = True
            group.save()
        Tweet.objects.create(
            user_name=user_name,
            tweet_text=tweet_text,
            tweet_url=tweet_url,
            group=group
        )

        for u in group.user_groups.all():
            TweetNotification.objects.create(
                user=u.user_id,
                content=tweet_text
            )

        return JsonResponse({'message': 'Tweet created successfully'}, status=201)

    return JsonResponse({'message': 'Invalid request method'}, status=400)

# NewsFeed Payment 
from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from urllib.parse import quote_plus
def venmo_payment_feedme(request):
    plays_type = request.GET.get('type', 'monthly').strip().lower()
    card_type = request.GET.get('plan', 'monthly').strip().lower()
    price = request.GET.get('price', '5000').strip()
    email = request.GET.get('email', '').strip()
    name = request.GET.get('name', '').strip()
    groups = request.GET.get('groups', '0').strip()

    try:
        amount = float(price)
    except ValueError:
        amount = 5000.00

    venmo_username = "JoeyTunes2_"  # Your Venmo username

    # Build query params for success page
    query_params = {
        'type': plays_type,
        'card': card_type,
        'amount': int(amount),
        'groups': groups,
        'email': email,
        'name': name,
    }

    return_url = request.build_absolute_uri(reverse('venmo_payment_success')) + '?' + urlencode(query_params)

    # Save return_url if needed later
    request.session['venmo_return_url'] = return_url

    # Venmo pay URL
    
    note = f"JoeyTunes-{card_type}-Subscription"
    note_encoded = quote_plus(note)  # properly encodes spaces etc.
    
    venmo_url = f"https://venmo.com/{venmo_username}?txn=pay&amount={amount:.2f}&note={note_encoded}"


    # Render instruction page instead of direct redirect
    return render(request, 'venmo_redirect.html', {
        'venmo_url': venmo_url,
        'return_url': return_url
    })

def venmo_payment_success(request):
    amount = request.GET.get("amount")
    email = request.GET.get("email", "").strip()
    name = request.GET.get("name", "").strip()
    plan_type = request.GET.get("type", "monthly").strip()
    plan_card = request.GET.get("card", "monthly").strip()
    groups = request.GET.get("groups", "0").strip()

    if not email or not amount:
        return JsonResponse({"error": "Missing required data."}, status=400)

    try:
        amount = int(float(amount))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid amount format."}, status=400)

    userinstance, created = UserModel.objects.get_or_create(
        email=email,
        defaults={"username": email, "name": name}
    )

    pkg_days = 30 if plan_type.lower() == 'monthly' else 365 if plan_type.lower() == 'yearly' else 0

    # Update user data

    userinstance.start_date = datetime.now().date()
    userinstance.name = name
    userinstance.username = email
    userinstance.package = plan_type
    userinstance.pkg_days = pkg_days
    userinstance.num_groups = int(groups) if groups.isdigit() else 0
    userinstance.plan = plan_card
    userinstance.plan_price = amount
    userinstance.user_type = 'FEEDMEUSER'
    userinstance.payment_type = 'Venmo'
    userinstance.save()

    # Log subscription
    SubscriptionRecords.objects.create(
        user_id=userinstance,
        amount=amount,
        session_id=f"venmo_{random.randint(100000, 999999)}",
        date_time=datetime.now()
    )

    # Notify admins

    try:
        send_reg_mail(
            email=['aliashrafmirza169@gmail.com', 'saherriaz78@gmail.com'],
            subject="NewsFeed Subscription via Venmo",
            message = (
                f"Payment received from {email} via Venmo for the NewsFeed subscription. "
                f"Please verify the payment and approve the user from the admin panel."
                f"Amount: ${amount:.2f}"
            )

        )
    except Exception as e:
        print(f"[Admin Email Error] {e}")
        # Send email to user (under review message)
    try:
        if created:
            # New user email
            send_reg_mail(
                email=[email],
                subject="FeedMe: Your Account is Under Review",
                message=(
                    f"Hi {name or email},\n\n"
                    f"Your FeedMe NewsFeed account has been created successfully.\n"
                    f"Your payment via Venmo (${amount}) is under review.\n\n"
                    f"Our support team will verify the payment and confirm your access shortly.\n"
                    f"You will receive a confirmation email once approved.\n\n"
                    f"Thank you for your patience.\n\n"
                    f"— FeedMe Team"
                )
            )
        else:
            # Existing user email
            send_reg_mail(
                email=[email],
                subject="FeedMe: Payment Under Review",
                message=(
                    f"Hi {name or email},\n\n"
                    f"We've received your payment via Venmo for the FeedMe NewsFeed subscription.\n"
                    f"Your account is under review.\n\n"
                    f"Our customer support team will verify your payment shortly.\n"
                    f"You will receive a confirmation email once your subscription is approved.\n\n"
                    f"— FeedMe Team"
                )
            )
            userinstance.payment_status = False
            userinstance.save()
    except Exception as e:
        print(f"[User Email Error] {e}")
    return render(request, 'Venmopayment-notify.html', {"user": userinstance, "amount": amount})

# stripe.api_key = settings.STRIPE_SECRET_KEY

def subscription_fee(request):
    item = []

    # Get parameters from URL
    plan_card = request.GET.get('card', '').strip()     # e.g., "Basic"
    plan_type = request.GET.get('type', '').strip()     # e.g., "monthly"
    plan_price = request.GET.get('price', '').strip()   # e.g., "60"
    groups = request.GET.get('groups', '0').strip()
    email = request.GET.get('email', '').strip()

    # Determine customer's email
    if request.user.is_authenticated:
        customer_email = request.user.email
    else:
        customer_email = email or None

    # Default group number
    try:
        num_groups = int(groups)
    except ValueError:
        num_groups = 2  # fallback

    # Safe float conversion
    try:
        amount = float(plan_price)
    except (ValueError, TypeError):
        amount = 0

    # If price is missing or zero, fallback to known pricing
    monthly_payment = {2: 60, 4: 120, 6: 180, 8: 240, 10: 300}
    if amount == 0:
        if plan_type.lower() == 'yearly':
            base = monthly_payment.get(num_groups, 60)
            amount = base * 12 * 0.8  # 20% discount on yearly
        else:
            amount = monthly_payment.get(num_groups, 60)

    # Format name for Stripe
    plan_card = plan_card or f"{num_groups} Groups"
    plan_type = plan_type or "monthly"

    # Prepare Stripe line item
    item.append({
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': f"{plan_card} Plan ({plan_type})",
                'images': [],
            },
            'unit_amount': int(round(amount * 100)),  # Stripe expects cents
        },
        'quantity': 1,
    })

    # Create checkout session with metadata
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=item,
        mode="payment",
        customer_email=customer_email,
        success_url=request.build_absolute_uri(
            reverse('paypal_payments_success')
        ) + f"?amount={int(round(amount))}&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=request.build_absolute_uri(reverse('payment_failed')),
        locale='auto',
        metadata={
            'email': customer_email or '',
            'name': request.GET.get('name', '').strip(),
            'plan_card': plan_card,
            'plan_type': plan_type,
            'plan_price': plan_price,
            'groups': groups,
        }
    )

    return redirect(session.url, code=303)
# NewsFeed Success Messages
def paypal_payments_success(request):
    session_id = request.GET.get("session_id")
    amount = request.GET.get("amount")

    if not session_id:
        return render(request, "error.html", {"message": "No session ID provided."})

    # Retrieve session from Stripe
    session = stripe.checkout.Session.retrieve(session_id)

    # Get customer email and metadata
    customer_email = session.customer_email
    metadata = session.metadata or {}

    name = metadata.get('name', '')
    plan_card = metadata.get('plan_card', '')
    plan_type = metadata.get('plan_type', '')
    plan_price = metadata.get('plan_price', '')
    groups = metadata.get('groups', '0').strip()

    userinstance, created = UserModel.objects.get_or_create(
        email=customer_email,
        defaults={'username': customer_email, 'name': name}
    )

    # Determine subscription duration
    pkg_days = 30 if plan_type.lower() == 'monthly' else 365 if plan_type.lower() == 'yearly' else 0

    # Update user info
    userinstance.start_date = datetime.now().date()
    userinstance.name = name
    userinstance.username = customer_email
    userinstance.package = plan_type
    userinstance.pkg_days = pkg_days
    userinstance.num_groups = int(groups) if groups.isdigit() else 0
    userinstance.plan = plan_card
    userinstance.plan_price = plan_price
    userinstance.user_type = 'FEEDMEUSER'
    userinstance.payment_type = 'Stripe'
    userinstance.payment_status = True
    userinstance.save()

    # Record subscription
    SubscriptionRecords.objects.create(
        user_id=userinstance,
        amount=int(float(amount)),
        session_id=session_id,
        date_time=datetime.now()
    )

    if created:
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        userinstance.set_password(random_password)
        userinstance.user_password = random_password
        userinstance.save()

        try:
            registration_email(
                email=customer_email,
                subject="Feedme Registration",
                template_name="./email_template.html",
                context={'username': customer_email, 'password': random_password}
            )
        except Exception as e:
            print(f"[Email Error] Failed to send registration email: {e}")

    # Notify admin
    admin_email = UserModel.objects.filter(is_superuser=True).values_list('email', flat=True).first()
    if admin_email:
        try:
            send_reg_mail(
                email=[admin_email, 'aliashrafmirza169@gmail.com', 'saherriaz78@gmail.com'],
                subject="NewsFeed Subscription",
                message=f"{customer_email} paid a NewsFeed subscription fee via Stripe: ${amount}"
            )
        except Exception as e:
            print(f"[Admin Email Error] {e}")
    is_new_user = created

    return render(request, 'NewsFeedcheckout_success.html', {
        "user": userinstance,
        "amount": amount,
        "is_new_user": is_new_user  # <-- Add this line
    })

import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode


def subscription_fee_paypal(request):
    plan_card = request.GET.get('card', '').strip()
    plan_type = request.GET.get('type', '').strip()
    plan_price = request.GET.get('price', '').strip()
    email = request.GET.get('email', '').strip()
    name = request.GET.get('name', '').strip()
    groups = request.GET.get('groups', '0').strip()

    # If custom plan with direct values
    if plan_card and plan_type and plan_price:
        try:
            amount = float(plan_price)
        except ValueError:
            amount = 100  # fallback
    else:
        # Fallback to user saved plan
        package_type = getattr(request.user, "package", "")
        num_groups = getattr(request.user, "num_groups", 0)

        monthly_payment = {2: 60, 4: 120, 6: 180, 8: 240, 10: 300}

        if package_type.strip().lower() == 'yearly':
            amount = monthly_payment.get(num_groups, 100) * 12 * 0.8
        else:
            amount = monthly_payment.get(num_groups, 100)

        plan_card = f"{num_groups} Groups"
        plan_type = package_type

    # Map to readable label
    product_name_map = {
        "Premium": "Premium Plan",
        "Basic": "Basic Plan",
        "Custom": "Custom Plan"
    }
    product_name = product_name_map.get(plan_card, f"{plan_type} Subscription")

    # --- Choose Sandbox or Live ---
    PAYPAL_MODE = getattr(settings, "PAYPAL_MODE", "sandbox")  # sandbox OR live
    if PAYPAL_MODE == "live":
        PAYPAL_API_BASE = "https://api-m.paypal.com"
        PAYPAL_CLIENT_ID = settings.PAYPAL_LIVE_CLIENT_ID
        PAYPAL_SECRET = settings.PAYPAL_LIVE_SECRET
    else:
        PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"
        PAYPAL_CLIENT_ID = settings.PAYPAL_SANDBOX_CLIENT_ID
        PAYPAL_SECRET = settings.PAYPAL_SANDBOX_SECRET

    # ✅ 1. Get PayPal Access Token
    try:
        auth_response = requests.post(
            f"{PAYPAL_API_BASE}/v1/oauth2/token",
            headers={
                'Accept': 'application/json',
                'Accept-Language': 'en_US'
            },
            data={'grant_type': 'client_credentials'},
            auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
        )
        auth_response.raise_for_status()
        access_token = auth_response.json().get('access_token')
    except Exception as e:
        return JsonResponse({'error': 'Failed to authenticate with PayPal', 'details': str(e)}, status=400)

    if not access_token:
        return JsonResponse({'error': 'No access token received from PayPal'}, status=400)

    # ✅ 2. Build return URL with proper encoding
    custom_id_value = f"{email}|{name}|{groups}|{plan_card}|{plan_type}"
    params = {
        "type": plan_type,
        "card": plan_card,
        "amount": int(amount),
        "custom_id": custom_id_value,
    }
    if email:
        params["email"] = email
    if name:
        params["name"] = name
    if groups:
        params["groups"] = groups

    return_url = request.build_absolute_uri(reverse('feedmepaypal_payments_success')) + "?" + urlencode(params)
    cancel_url = request.build_absolute_uri(reverse('payment_failed'))

    # ✅ 3. Create PayPal Order
    create_order_url = f"{PAYPAL_API_BASE}/v2/checkout/orders"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": f"{amount:.2f}"
            },
            "description": f"Joey Tunes: {product_name}",
            "custom_id": custom_id_value,
        }],
        "application_context": {
            "return_url": return_url,
            "cancel_url": cancel_url,
            "brand_name": "JoeyTunes",
            "landing_page": "BILLING",
            "user_action": "PAY_NOW"
        }
    }

    try:
        response = requests.post(create_order_url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        return JsonResponse({'error': 'PayPal order creation failed', 'details': str(e)}, status=400)

    # ✅ 4. Redirect to PayPal approval
    for link in result.get("links", []):
        if link["rel"] == "approve":
            return redirect(link["href"])

    return JsonResponse({'error': 'No approval link found from PayPal', 'details': result}, status=400)

def feedmepaypal_payments_success(request):
    from datetime import datetime
    import random, string, requests
    from django.conf import settings
    from django.shortcuts import render
    from django.http import JsonResponse
    from your_app.models import UserModel, SubscriptionRecords
    from your_app.utils import send_reg_mail, registration_email

    amount = request.GET.get("amount")
    custom_id = request.GET.get("custom_id")
    order_id = request.GET.get("token")  # PayPal Order ID

    if not custom_id or not order_id:
        return JsonResponse({"error": "Missing order_id or custom_id in PayPal response."}, status=400)

    # --- Step 1: Get Access Token ---
    PAYPAL_MODE = getattr(settings, "PAYPAL_MODE", "sandbox")
    PAYPAL_API_BASE = "https://api-m.paypal.com" if PAYPAL_MODE == "live" else "https://api-m.sandbox.paypal.com"
    PAYPAL_CLIENT_ID = settings.PAYPAL_LIVE_CLIENT_ID if PAYPAL_MODE == "live" else settings.PAYPAL_SANDBOX_CLIENT_ID
    PAYPAL_SECRET = settings.PAYPAL_LIVE_SECRET if PAYPAL_MODE == "live" else settings.PAYPAL_SANDBOX_SECRET

    try:
        auth_response = requests.post(
            f"{PAYPAL_API_BASE}/v1/oauth2/token",
            headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
            data={'grant_type': 'client_credentials'},
            auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
        )
        access_token = auth_response.json().get('access_token')
        if not access_token:
            return JsonResponse({'error': 'PayPal access token not received.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'PayPal Auth Failed', 'details': str(e)}, status=400)

    # --- Step 2: Capture Payment ---
    capture_url = f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}

    try:
        capture_response = requests.post(capture_url, headers=headers)
        capture_data = capture_response.json()
        if capture_response.status_code != 201 or capture_data.get("status") != "COMPLETED":
            return JsonResponse({'error': 'Payment not completed', 'details': capture_data}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Payment capture failed', 'details': str(e)}, status=400)

    # --- Step 3: Extract Metadata ---
    try:
        email, name, groups, plan_card, plan_type = custom_id.split("|")
    except ValueError:
        return JsonResponse({"error": "Invalid metadata format in custom_id."}, status=400)

    # --- Step 4: Create or Update User ---
    userinstance, created = UserModel.objects.get_or_create(
        email=email,
        defaults={'username': email, 'name': name}
    )

    pkg_days = 30 if plan_type.lower() == 'monthly' else 365 if plan_type.lower() == 'yearly' else 0

    # Save or update user details in both cases
    userinstance.start_date = datetime.now().date()
    userinstance.name = name
    userinstance.username = email
    userinstance.package = plan_type
    userinstance.pkg_days = pkg_days
    userinstance.num_groups = int(groups) if groups.isdigit() else 0
    userinstance.plan = plan_card
    userinstance.plan_price = amount
    userinstance.user_type = 'FEEDMEUSER'
    userinstance.payment_type = 'Paypal'
    userinstance.payment_status = True

    # --- Step 5: Send Email if New ---
    if created:
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        userinstance.set_password(random_password)
        userinstance.user_password = random_password
        userinstance.save()

        try:
            registration_email(
                email=email,
                subject="Feedme Registration",
                template_name="./email_template.html",
                context={'username': email, 'password': random_password}
            )
        except Exception as e:
            print(f"[Email Error] Failed to send registration email: {e}")
    else:
        try:
            send_reg_mail(
                email=email,
                subject="Thank You for Updating Your Feedme Subscription",
                message=(
                    f"Dear {name},\n\n"
                    f"Thank you for updating your Feedme subscription.\n"
                    f"Your plan: {plan_type.capitalize()} — Amount paid: ${amount}\n\n"
                    f"We appreciate your continued support.\n\n"
                    f"Warm regards,\nFeedme Team"
                )
            )
        except Exception as e:
            print(f"[Email Error] Failed to send thank-you update email: {e}")

    # Save the user after email logic (just to be safe)
    userinstance.save()

    # --- Step 6: Save Subscription Record ---
    SubscriptionRecords.objects.create(
        user_id=userinstance,
        amount=int(float(amount)),
        session_id=f"paypal_{random.randint(100000,999999)}",
        date_time=datetime.now()
    )

    # --- Step 7: Notify Admins ---
    admin_email = UserModel.objects.filter(is_superuser=True).values_list('email', flat=True).first()
    if admin_email:
        try:
            send_reg_mail(
                email=[admin_email, 'aliashrafmirza169@gmail.com', 'saherriaz78@gmail.com'],
                subject="NewsFeed Subscription",
                message=f"{email} paid a NewsFeed subscription fee via PayPal: ${amount}"
            )
        except Exception as e:
            print(f"[Admin Email Error] {e}")
    is_new_user = created

    return render(request, 'NewsFeedcheckout_success.html', {
        "user": userinstance,
        "amount": amount,
        "is_new_user": is_new_user  # <-- Add this line
    })



def payment_success(request):
    user_instance = UserModel.objects.get(username=request.user)
    package = user_instance.package

    if package == 'monthly':
        user_instance.pkg_days = 30
    elif package == 'yearly':
        user_instance.pkg_days = 365

    user_instance.start_date = datetime.now().date()
    user_instance.save()

    SubscriptionRecords.objects.create(
        user_id=user_instance,
        amount=int(request.GET.get('amount')),
        session_id=request.GET.get("session_id"),
        date_time=datetime.now()
    )

    # Get admin email
    admin_email = UserModel.objects.values_list('email', flat=True).filter(is_superuser=True).first()

    if admin_email:
        send_reg_mail(
            email=[admin_email, 'aliashrafmirza169@gmail.com'],
            subject="NewsFeed Subscription",
            message=f"{request.user.username} paid a subscription fee: {request.GET.get('amount')}"
        )

    return render(request, 'checkout_success.html')
    

# Plays Payments
# venmo
def venmo_payment(request):
    plays_type = request.GET.get('type', 'monthly').strip().lower()
    card_type = request.GET.get('card', 'monthly').strip().lower()
    price = request.GET.get('price', '5000').strip()
    name = request.GET.get('name', '').strip()
    email = request.GET.get('email', '').strip()
    code = request.GET.get('code', '').strip()
    try:
        amount = float(price)
    except ValueError:
        amount = 5000.00

    venmo_username = "JoeyTunes2_"

    # ✅ Properly build return URL with parameters
    query_params = {
        'type': plays_type,
        'card': card_type,
        'amount': int(amount),
    }
    if name:
        query_params['name'] = name
    if email:
        query_params['email'] = email

    return_url = request.build_absolute_uri(reverse('playsvemno_payment_success')) + '?' + urlencode(query_params)

    # Optionally store session/cookie to track payment later
    request.session['plays_venmo_return_url'] = return_url

    note = f"JoeyTunes-{card_type}-Subscription"
    note_encoded = quote_plus(note)  # properly encodes spaces etc.
    
    venmo_url = f"https://venmo.com/{venmo_username}?txn=pay&amount={amount:.2f}&note={note_encoded}"

    return render(request, 'venmo_redirect.html', {
        'venmo_url': venmo_url,
        'return_url': return_url
    })
def playsvemno_payment_success(request):
    email = request.GET.get("email", "").strip()
    name = request.GET.get("name", "").strip()
    plan_type = request.GET.get("type", "monthly").strip()
    plan_card = request.GET.get("card", "monthly").strip()
    amount = request.GET.get("amount", "0").strip()
    code = request.GET.get('code', '').strip()

    if not email or not amount:
        return JsonResponse({"error": "Missing required data"}, status=400)

    try:
        amount = int(float(amount))
    except ValueError:
        return JsonResponse({"error": "Invalid amount format"}, status=400)

    # Get or create user
    userinstance, created = UserModel.objects.get_or_create(
        email=email,
        defaults={"username": email, "name": name}
    )

    # Plan durations
    pkg_days_map = {
        'monthly': 30,
        'full_yearly': 365,
        'seasonal_cfb': 149,
        'seasonal_nfl': 157,
        'seasonal_both': 170,
    }
    pkg_days = pkg_days_map.get(plan_card, 30)

    # Update user info
    userinstance.plays_package = plan_type
    userinstance.plays_plan = plan_card
    userinstance.store_plays_pkg_days = pkg_days
    userinstance.plays_price = amount
    userinstance.is_activate_playes = True
    userinstance.user_type = 'FEEDMEUSER'
    userinstance.plays_payment_type = 'Venmo'
    userinstance.refferal_code = code
    userinstance.plays_start_date = timezone.now().date()
    userinstance.save()

    # Log subscription
    SubscriptionRecords.objects.create(
        user_id=userinstance,
        amount=amount,
        session_id=f"venmo_{random.randint(100000, 999999)}",
        date_time=datetime.now()
    )

    # Send email to admin
    try:
        admin_email = UserModel.objects.filter(is_superuser=True).values_list('email', flat=True).first()
        recipients = ['aliashrafmirza169@gmail.com', 'saherriaz78@gmail.com']
        if admin_email and admin_email not in recipients:
            recipients.insert(0, admin_email)

        print(f"[Debug] Sending admin email to: {recipients}")

        send_reg_mail(
            email=recipients,
            subject="Plays Subscription via Venmo",
            # message=f"{email} paid a Plays subscription fee via Venmo: ${amount}"
            message = (
                f"Payment received from {email} via Venmo for the Plays subscription. "
                f"Please verify the payment and approve the user from the admin panel."
                f"Amount: ${amount:.2f}"
            )
        )

    except Exception as e:
        print(f"[Admin Email Error] {e}")

    # Send email to user (under review message)
    try:
        if created:
            # New user email
            send_reg_mail(
                email=[email],
                subject="FeedMe: Your Account is Under Review",
                message=(
                    f"Hi {name or email},\n\n"
                    f"Your FeedMe Plays account has been created successfully.\n"
                    f"Your payment via Venmo (${amount}) is under review.\n\n"
                    f"Our support team will verify the payment and confirm your access shortly.\n"
                    f"You will receive a confirmation email once approved.\n\n"
                    f"Thank you for your patience.\n\n"
                    f"— FeedMe Team"
                )
            )
        else:
            # Existing user email
            send_reg_mail(
                email=[email],
                subject="FeedMe: Payment Under Review",
                message=(
                    f"Hi {name or email},\n\n"
                    f"We've received your payment via Venmo for the FeedMe Plays subscription.\n"
                    f"Your account is under review.\n\n"
                    f"Our customer support team will verify your payment shortly.\n"
                    f"You will receive a confirmation email once your subscription is approved.\n\n"
                    f"— FeedMe Team"
                )
            )
            userinstance.plays_payment_status = False
            userinstance.save()
    except Exception as e:
        print(f"[User Email Error] {e}")

    return render(request, 'Venmopayment-notify.html', {"user": userinstance, "amount": amount})


# paypal
def subscription_playsfee_paypal(request):
    plays_type = request.GET.get('type', 'monthly').strip().lower()
    card_type = request.GET.get('card', 'monthly').strip().lower()
    price = request.GET.get('price', '5000').strip()
    email = request.GET.get('email', '').strip()
    name = request.GET.get('name', '').strip()

    try:
        amount = float(price)
    except ValueError:
        amount = 5000

    user = request.user if request.user.is_authenticated else None
    custom_id_value = f"{email}|{name}|{plays_type}|{card_type}|{price}"

    customer_email = ''
    if user and user.email:
        customer_email = user.email
    elif email:
        customer_email = email

    product_name_map = {
        'monthly': 'Monthly Subscription',
        'full_yearly': 'Full Yearly Subscription',
        'seasonal_nfl': 'NFL Season Subscription',
        'seasonal_cfb': 'CFB Season Subscription',
        'seasonal_both': 'CFB and NFL Season Subscription',
    }

    product_name = product_name_map.get(card_type, f"{plays_type.capitalize()} Subscription")

    # --- Choose Sandbox or Live ---
    PAYPAL_MODE = getattr(settings, "PAYPAL_MODE", "sandbox")  # sandbox OR live
    if PAYPAL_MODE == "live":
        PAYPAL_API_BASE = "https://api-m.paypal.com"
        PAYPAL_CLIENT_ID = settings.PAYPAL_LIVE_CLIENT_ID
        PAYPAL_SECRET = settings.PAYPAL_LIVE_SECRET
    else:
        PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"
        PAYPAL_CLIENT_ID = settings.PAYPAL_SANDBOX_CLIENT_ID
        PAYPAL_SECRET = settings.PAYPAL_SANDBOX_SECRET

    # Step 1: Get PayPal Access Token
    try:
        auth_response = requests.post(
            f"{PAYPAL_API_BASE}/v1/oauth2/token",
            headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
            data={'grant_type': 'client_credentials'},
            auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
        )
        auth_response.raise_for_status()
        access_token = auth_response.json().get('access_token')
    except Exception as e:
        return JsonResponse({'error': 'Failed to authenticate with PayPal', 'details': str(e)}, status=400)

    if not access_token:
        return JsonResponse({'error': 'No access token received from PayPal'}, status=400)

    # Step 2: Create Order
    create_order_url = f"{PAYPAL_API_BASE}/v2/checkout/orders"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    params = {
        "type": plays_type,
        "card": card_type,
        "amount": int(amount),
        "email": email,
        "name": name,
        "custom_id": custom_id_value,
    }

    return_url = request.build_absolute_uri(reverse('playspaypal_payments_success')) + "?" + urlencode(params)
    cancel_url = request.build_absolute_uri(reverse('payment_failed'))

    data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": f"{amount:.2f}"
            },
            "description": f"Joey Tunes: {product_name}",
            "custom_id": f"{email}|{name}|{plays_type}|{card_type}|{amount}",
        }],
        "application_context": {
            "return_url": return_url,
            "cancel_url": cancel_url,
            "brand_name": "JoeyTunes",
            "landing_page": "BILLING",
            "user_action": "PAY_NOW"
        }
    }

    response = requests.post(create_order_url, json=data, headers=headers)
    result = response.json()

    for link in result.get("links", []):
        if link["rel"] == "approve":
            return redirect(link["href"])

    return JsonResponse({'error': 'PayPal order creation failed', 'details': result}, status=400)

def playspaypal_payments_success(request):
    order_id = request.GET.get("token")  # PayPal returns 'token' as order ID
    if not order_id:
        return JsonResponse({"error": "Missing PayPal order token."}, status=400)

    # Get access token again (same as in order creation)
    PAYPAL_MODE = getattr(settings, "PAYPAL_MODE", "sandbox")
    if PAYPAL_MODE == "live":
        PAYPAL_API_BASE = "https://api-m.paypal.com"
        PAYPAL_CLIENT_ID = settings.PAYPAL_LIVE_CLIENT_ID
        PAYPAL_SECRET = settings.PAYPAL_LIVE_SECRET
    else:
        PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"
        PAYPAL_CLIENT_ID = settings.PAYPAL_SANDBOX_CLIENT_ID
        PAYPAL_SECRET = settings.PAYPAL_SANDBOX_SECRET

    try:
        auth_response = requests.post(
            f"{PAYPAL_API_BASE}/v1/oauth2/token",
            headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
            data={'grant_type': 'client_credentials'},
            auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
        )
        auth_response.raise_for_status()
        access_token = auth_response.json().get('access_token')
    except Exception as e:
        return JsonResponse({'error': 'Failed to authenticate with PayPal', 'details': str(e)}, status=400)

    # Step: Capture the payment
    capture_url = f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    capture_response = requests.post(capture_url, headers=headers)
    capture_data = capture_response.json()

    if capture_response.status_code != 201:
        return JsonResponse({'error': 'Payment capture failed', 'details': capture_data}, status=400)

    # Now extract metadata
    try:
        custom_id = capture_data['purchase_units'][0]['payments']['captures'][0]['custom_id']
    except Exception:
        return JsonResponse({"error": "Missing or invalid custom_id after capture"}, status=400)
    amount = request.GET.get("amount")
    code = request.GET.get('code', '').strip()
    custom_id = request.GET.get("custom_id")  # Pass this manually via return_url or fetch via PayPal API

    if not custom_id:
        return JsonResponse({"error": "Missing custom_id in PayPal response."}, status=400)

    # 🔓 Split and extract metadata
    try:
        email, name, plays_type, card_type, amount = custom_id.split("|")
    except ValueError:
        return JsonResponse({"error": "Invalid metadata format."}, status=400)

    userinstance, created = UserModel.objects.get_or_create(
        email=email,
        defaults={'username': email, 'name': name}
    )
        # Set package days based on plan
    pkg_days_map = {
        'monthly': 30,
        'full_yearly': 365,
        'seasonal_cfb': 149,
        'seasonal_nfl': 157,
    }
    pkg_days = pkg_days_map.get(card_type, 30)

    # ✅ Always update user info
    userinstance.plays_package = plays_type
    userinstance.plays_plan = card_type
    userinstance.plays_pkg_days = pkg_days
    userinstance.plays_price = amount
    userinstance.is_activate_playes = True
    userinstance.user_type = 'FEEDMEUSER'
    userinstance.plays_payment_status = True
    userinstance.plays_payment_type = "Paypal"
    userinstance.refferal_code = code
    userinstance.plays_start_date = timezone.now().date()
    userinstance.save()


    # Record subscription
    SubscriptionRecords.objects.create(
        user_id=userinstance,
        amount=int(float(amount)),
        session_id=f"paypal_{random.randint(100000,999999)}",
        date_time=datetime.now()
    )

    # Register if new
    if created:
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        userinstance.set_password(random_password)
        userinstance.user_password = random_password
        userinstance.save()

        try:
            registration_email(
                email=email,
                subject="Feedme Registration",
                template_name="./email_template.html",
                context={'username': email, 'password': random_password}
            )
        except Exception as e:
            print(f"[Email Error] Failed to send registration email: {e}")
    else:
        try:
            send_reg_mail(
                email=email,
                subject="Thank You for Updating Your Plays Subscription",
                message=(
                    f"Hi {name},\n\n"
                    f"Your Plays subscription has been updated successfully.\n"
                    f"Plan: {card_type.replace('_', ' ').title()} — Amount: ${amount}\n"
                    f"We appreciate your continued support.\n\n"
                    f"Warm regards,\nFeedme Team"
                )
            )

        except Exception as e:
            print(f"[Email Error] Update thank-you failed: {e}")


    # Notify Admins
    admin_email = UserModel.objects.filter(is_superuser=True).values_list('email', flat=True).first()
    if admin_email:
        try:
            send_reg_mail(
                email=[admin_email, 'aliashrafmirza169@gmail.com', 'saherriaz78@gmail.com'],
                subject="Plays Subscription",
                message=f"{email} paid a Plays subscription fee via PayPal: ${amount}"
            )
        except Exception as e:
            print(f"[Admin Email Error] {e}")
    is_new_user = created

    return render(request, "Playscheckout_success.html", {"is_new_user": is_new_user})


# stripe
def subscription_playsfee(request):
    plays_type = request.GET.get('type', 'monthly').strip().lower()  # monthly or yearly
    card_type = request.GET.get('card', 'monthly').strip().lower()
    name = request.GET.get('name', '').strip()
    email = request.GET.get('email', '').strip()
    price = request.GET.get('price', '5000').strip()

    try:
        amount = float(price)
    except ValueError:
        amount = 5000  # fallback default

    # Use request.user if authenticated, else fallback to provided name/email
    user = request.user if request.user.is_authenticated else None

    customer_email = ''
    if user and user.email:
        customer_email = user.email
    elif email:
        customer_email = email

    # You can optionally log or save name/email to a temporary record or session here
    print(f"Checkout initiated for: {name} ({email})")

    product_name_map = {
        'monthly': 'Monthly Subscription',
        'full_yearly': 'Full Yearly Subscription',
        'seasonal_nfl': 'NFL Season Subscription',
        'seasonal_cfb': 'CFB Season Subscription',
        'seasonal_both': 'CFB and NFL Season Subscription',
    }

    product_name = product_name_map.get(card_type, f"{plays_type.capitalize()} Subscription")
    print("Selected product:", product_name)

    item = [{
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': f"Joey Tunes: {product_name}",
                'images': [],
            },
            'unit_amount': int(amount * 100),
        },
        'quantity': 1,
    }]

    # Create Stripe Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=item,
        mode="payment",
        customer_email=customer_email,
        success_url=request.build_absolute_uri(reverse('plays_payment_success')) +
                     f"?amount={int(amount)}&session_id={{CHECKOUT_SESSION_ID}}&type={plays_type}&card={card_type}",
        cancel_url=request.build_absolute_uri(reverse('payment_failed')),
        locale='auto',
        metadata={
            'plays_type': plays_type or '',
            'name': request.GET.get('name', '').strip(),
            'card_type': card_type,
            'email': email,
            'price': price,
        }
    )

    return redirect(session.url, code=303)
def plays_payment_success(request):
    amount = request.GET.get('amount')
    session_id = request.GET.get("session_id")
    code = request.GET.get('code', '').strip()

    if not session_id:
       return render(request, "error.html", {"message": "No session ID provided."})

    # Retrieve session from Stripe
    session = stripe.checkout.Session.retrieve(session_id)

    # Get customer email and metadata
    customer_email = session.customer_email
    metadata = session.metadata or {}

    plays_type = metadata.get('plays_type', '')  # monthly or yearly
    card_type = metadata.get('card_type', '')
    name = metadata.get('name', '')
    email = metadata.get('email', '')
    price = metadata.get('price', '')
    print("email have in success message", email)

    # Set package days based on plan
    pkg_days_map = {
        'monthly': 30,
        'full_yearly': 365,
        'seasonal_cfb': 149,
        'seasonal_nfl': 157,
    }
    pkg_days = pkg_days_map.get(card_type, 30)

    # Get or create user
    userinstance, created = UserModel.objects.get_or_create(
        email=email,
        defaults={'username': email, 'name': name}
    )

    # If user was just created, set random password & send email
    if created:
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        userinstance.set_password(random_password)
        userinstance.user_password = random_password  # If you want to store it
        userinstance.save()

        try:
            registration_email(
                email=email,
                subject="Feedme Registration",
                template_name="./email_template.html",
                context={'username': email, 'password': random_password}
            )
        except Exception as e:
            print(f"[Email Error] Registration email failed: {e}")

    # Update user subscription info
    userinstance.plays_package = plays_type
    userinstance.plays_plan = card_type
    userinstance.plays_pkg_days = pkg_days
    userinstance.plays_price = amount
    userinstance.is_activate_playes = True
    userinstance.user_type = 'FEEDMEUSER'
    userinstance.plays_payment_status = True
    userinstance.plays_payment_type = "Strip"
    userinstance.refferal_code = code
    userinstance.plays_start_date = timezone.now().date()
    userinstance.save()

    # Record subscription
    try:
        SubscriptionRecords.objects.create(
            user_id=userinstance,
            amount=int(float(amount)),
            session_id=session_id,
            date_time=timezone.now()
        )
    except Exception as e:
        print(f"[DB Error] Failed to create SubscriptionRecords: {e}")

    # Notify admin
    admin_email = UserModel.objects.filter(is_superuser=True).values_list('email', flat=True).first()
    if admin_email:
        try:
            send_plays_mail(
                email=[admin_email, 'aliashrafmirza169@gmail.com'],
                subject="Plays Subscription",
                message=f"{userinstance.username} subscribed to ({plays_type}) for ${amount}"
            )
        except Exception as e:
            print(f"[Email Error] Admin notification failed: {e}")
    is_new_user = created

    return render(request, "Playscheckout_success.html", {"is_new_user": is_new_user})


def paypal_payment_success(request):
    user = request.user
    plays_type = request.GET.get('type', 'monthly')
    card_type = request.GET.get('card', 'monthly').strip().lower()   # card type (e.g. seasonal_nfl)
    amount = request.GET.get('amount')
    code = request.GET.get('code', '').strip()
    session_id = 123

    if card_type == 'monthly':
        plays_pkg_days = 30
    elif card_type == 'full_yearly':
        plays_pkg_days = 365
    elif card_type == 'seasonal_cfb':
        plays_pkg_days = 149
    elif card_type == 'seasonal_nfl':
        plays_pkg_days = 157
    userinstance = UserModel.objects.get(username = user)

    # Update plays-related fields
    userinstance.plays_package = plays_type
    userinstance.plays_plan = card_type
    userinstance.plays_pkg_days = plays_pkg_days
    userinstance.plays_price = amount
    userinstance.plays_payment_status = True,
    userinstance.plays_payment_type = "Paypal",
    userinstance.refferal_code = code
    userinstance.plays_start_date = datetime.now().date()  # Optional if you want to track this
    userinstance.save()

    # Optional: record it like other subscriptions
    SubscriptionRecords.objects.create(
        user_id=user,
        amount=int(amount),
        session_id=session_id,
        date_time=datetime.now()
    )
    admin_email = UserModel.objects.filter(is_superuser=True).values_list('email', flat=True).first()
    
    if admin_email:
        send_plays_mail(
            email=[admin_email, 'aliashrafmirza169@gmail.com'],
            subject="Plays Subscription",
            message=f"{user.username} subscribed to ({plays_type}) for ${amount}"
        )

    return render(request, 'checkout_success.html', {'amount': amount, 'plays_type': plays_type, 'card_type': card_type})
# product shipping payments

def venmo_payment_checkout(request):
    total_amount = 0.00
    cart = request.session.get('cart', {})
    note_parts = []

    for product in cart.values():
        try:
            price = float(product['product']['price'])
            quantity = int(product['quantity'])
            name = product['product']['full_name']
            total_amount += price * quantity
            note_parts.append(f"{name}x{quantity}")
        except (KeyError, ValueError, TypeError):
            continue  # skip any malformed items

    # Fallback if cart is empty
    if total_amount == 0:
        total_amount = 5000.00
        note_parts = ['Default']

    # Venmo username
    venmo_username = "JoeyTunes2_"  # Replace with your actual Venmo handle

    # Note for Venmo payment
    note = " | ".join(note_parts)  # e.g., "Taco Box x2 | Fries x1"

    # Build the deep link URL to Venmo
    venmo_url = f"https://venmo.com/{venmo_username}?txn=pay&amount={total_amount:.2f}&note={note}"

    return redirect(venmo_url)

def subscription_checkout_paypal(request):
    total_amount = 0.00
    cart = request.session.get('cart', {})
    note_parts = []
    session_id = str(uuid.uuid4())

    for product in cart.values():
        try:
            price = float(product['product']['price'])
            quantity = int(product['quantity'])
            name = product['product']['full_name']
            total_amount += price * quantity
            note_parts.append(f"{name}x{quantity}")
        except (KeyError, ValueError, TypeError):
            continue

    # Fallback if cart is empty
    if total_amount == 0:
        total_amount = 5000.00
        note_parts = ['Default']

    # Build product name/description
    product_name = " | ".join(note_parts)
    description_text = f"Joey Tunes: {product_name}"
    if len(description_text) > 127:
        description_text = description_text[:124] + "..."

    # --- Choose Sandbox or Live ---
    PAYPAL_MODE = getattr(settings, "PAYPAL_MODE", "sandbox")  # sandbox OR live
    if PAYPAL_MODE == "live":
        PAYPAL_API_BASE = "https://api-m.paypal.com"
        PAYPAL_CLIENT_ID = settings.PAYPAL_LIVE_CLIENT_ID
        PAYPAL_SECRET = settings.PAYPAL_LIVE_SECRET
    else:
        PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"
        PAYPAL_CLIENT_ID = settings.PAYPAL_SANDBOX_CLIENT_ID
        PAYPAL_SECRET = settings.PAYPAL_SANDBOX_SECRET

    # 1. Get PayPal Access Token
    try:
        auth_response = requests.post(
            f"{PAYPAL_API_BASE}/v1/oauth2/token",
            headers={
                'Accept': 'application/json',
                'Accept-Language': 'en_US'
            },
            data={'grant_type': 'client_credentials'},
            auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
        )
        auth_response.raise_for_status()
        access_token = auth_response.json().get('access_token')
    except Exception as e:
        return JsonResponse({'error': 'Failed to authenticate with PayPal', 'details': str(e)}, status=400)

    if not access_token:
        return JsonResponse({'error': 'No access token received from PayPal'}, status=400)

    # 2. Create PayPal Order
    create_order_url = f"{PAYPAL_API_BASE}/v2/checkout/orders"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": f"{total_amount:.2f}"
            },
            "description": description_text
        }],
        "application_context": {
            "return_url": request.build_absolute_uri(
                reverse('checkout_success')
            ) + f"?session_id={session_id}",
            "cancel_url": request.build_absolute_uri(reverse('payment_failed')),
            "brand_name": "JoeyTunes",
            "landing_page": "BILLING",
            "user_action": "PAY_NOW"
        }
    }

    try:
        response = requests.post(create_order_url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        return JsonResponse({'error': 'PayPal order creation failed', 'details': str(e)}, status=400)

    print("PayPal create order response:", json.dumps(result, indent=2))
    print("Status code:", response.status_code)

    # 3. Redirect user to PayPal approval page
    for link in result.get("links", []):
        if link["rel"] == "approve":
            return redirect(link["href"])

    return JsonResponse({'error': 'No approval link found from PayPal', 'details': result}, status=400)

def checkout(request):
    cart_items = []
    for product in request.session.get('cart').values():
        print(product.keys())
        cart_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product['product']['full_name'] + ' - Size "' + product['size'] + '"',
                    'images': [],  # change this to the image of the product
                },
                'unit_amount': int(float(product['product']['price']) * 100),
            },
            'quantity': product['quantity'],
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=cart_items,
        mode="payment",
        # success_url='http://feedme.bet/checkout_success?session_id={CHECKOUT_SESSION_ID}',    
        success_url = request.build_absolute_uri(
            reverse('checkout_success')
            )+"?session_id={CHECKOUT_SESSION_ID}",
        locale='auto',  # Set the locale to 'auto' to use the customer's browser language settings. 
        custom_fields=[
            {
            "key": "address",
            "label": {"type": "custom", "custom": "Shipping Address"},
            "type": "text",
            },
        ]
    )

    # so that we can retrieve the session ID in the success_bronze view
    session_id = session.stripe_id
    
    return redirect(session.url, code=303)



# Failed Payments

def payment_failed(request):
        return HttpResponse("PAYMENT FAILED<br/><a href='/'>back to Home Page </a>")



def update_cart(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == "remove":
            product_id = request.POST.get('product_id')
            cart = request.session.get('cart')
            if cart and product_id in cart:
                del cart[product_id]
                request.session['cart'] = cart
        if action == 'update':
            product_id = request.POST.get('product_id')
            cart = request.session.get('cart')
            quantity = request.POST.get('quantity')
            if cart and product_id in cart:
                
                cart[product_id]['quantity'] = int(quantity)
                value = ProductVariation.objects.get(id=product_id)
                value = value.to_json()
                cart[product_id]['total'] = float(value['price']) * float(quantity)
                
                request.session['cart'] = cart
            return JsonResponse({"success":True})
        return redirect('cart')
    return redirect('cart')


csrf_exempt
def emailSubscription(request):
    if request.method=="POST":
        email = request.POST.get('email')
        EmailSubscription.objects.get_or_create(email = email)
        
    return redirect("home3")


from collections import defaultdict

def del_chat(request, id):
    if not request.user.is_authenticated:
        return redirect('plays')

    message = Message.objects.get(id=id)
    message.delete()
    return redirect('plays')


def edit_chat(request, id):
    if not request.user.is_authenticated:
        print("Not authenticated")
        return redirect('plays')

    try:
        message = Message.objects.get(id=id)
        message.title = request.POST.get("title")
        message.body = request.POST.get("body")
        message.save()
        print("Saved")
    except Exception as e:
        print(e)
        pass
    return redirect('plays')


def record(request):
    records = SportsBet.objects.filter(date__year=2024).order_by('date')

    # Create dictionaries to store total losses and wins for each sport
    total_losses_by_sport = defaultdict(int)
    total_wins_by_sport = defaultdict(int)
    total_sport = {}

    for record in records:
        if len(record.sport) <= 1:
            continue
        if record.result == 'Loss':
            total_losses_by_sport[record.sport.upper()] += 1
            total_sport[record.sport.upper()]['loss'] += 1
        elif record.result == 'Win':
            total_wins_by_sport[record.sport] += 1
            total_sport[record.sport.upper()]['win'] += 1

    for key,value in total_losses_by_sport.items():
        if key not in total_wins_by_sport:
            total_wins_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            
    for key,value in total_wins_by_sport.items():
        if key not in total_losses_by_sport:
            total_losses_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
    
    # sort the dictionaries by keys (sport names) in alphabetical order
    total_losses_by_sport = sorted(total_losses_by_sport.items(), key=lambda x: x[0])
    total_wins_by_sport = sorted(total_wins_by_sport.items(), key=lambda x: x[0])
    
    return render(request, 'record.html', {'records': records, 'total_sports':total_sport, 'year': '2023', 'total_losses_by_sport': dict(total_losses_by_sport), 'total_wins_by_sport': dict(total_wins_by_sport)})


def record2023(request):
    records = SportsBet.objects.filter(date__year=2023).order_by('-date')

    # Create dictionaries to store total losses and wins for each sport
    total_losses_by_sport = defaultdict(int)
    total_wins_by_sport = defaultdict(int)
    total_roi_by_sport = defaultdict(int)

    total_sport = {}

    for record in records:

        if len(record.sport) <= 1:
            continue

        if record.result.lower() == 'loss':
            total_losses_by_sport[record.sport] += 1
            
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['loss'] += 1
        elif record.result.lower() == 'win':
            total_wins_by_sport[record.sport] += 1
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['win'] += 1
        else:
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
        
        if record.total_earn and record.risk:
            total_sport[record.sport]['roi'] += round( float(record.total_earn) /(float(record.risk)) ,2)
            total_sport[record.sport]['total_units'] += round(float(record.total_earn)/100 ,2)
            total_sport[record.sport]['total_units'] = round(total_sport[record.sport]['total_units'],2)

            total_sport[record.sport]['roi'] = round(total_sport[record.sport]['roi'],2)
        
            # print(record.total_earn , record.risk , total_sport[record.sport]['roi'])

            
            
        total_roi_by_sport[record.sport] =  3
        

    for key,value in total_losses_by_sport.items():
        if key not in total_wins_by_sport:
            total_wins_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            
    for key,value in total_wins_by_sport.items():
        if key not in total_losses_by_sport:
            total_losses_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}

    for key,value in total_sport.items():
        # calculate win percentage
        total_sport[key]['win_percentage'] = round((total_sport[key]['win'] / (total_sport[key]['win'] + total_sport[key]['loss'])) * 100, 1)
        
    # sort the dictionaries by keys (sport names) in alphabetical order
    total_losses_by_sport = sorted(total_losses_by_sport.items(), key=lambda x: x[0])
    total_wins_by_sport = sorted(total_wins_by_sport.items(), key=lambda x: x[0])
    total_roi_by_sport = sorted(total_roi_by_sport.items(), key=lambda x: x[0])
    
    return render(request, 'record.html', {'records': records, 'total_roi_by_sport': dict(total_roi_by_sport),  'total_sport':total_sport, 'year': '2023', 'total_losses_by_sport': dict(total_losses_by_sport), 'total_wins_by_sport': dict(total_wins_by_sport)})

def record2024(request):
    # Get all filter parameters
    year = request.GET.get("year")
    search_query = request.GET.get("search", "")
    sport_filter = request.GET.get("sport", "")
    start_date = request.GET.get("start_date")
    seasons = ["2021", "2022", "2023", "2024", "2025", "lifetime"]

    if not year:
        year = str(datetime.now().year)

    # Get full base queryset for total_sport calc (unfiltered)
    if year == "lifetime":
        full_records = SportsBet.objects.exclude(result="pending")
    else:
        full_records = SportsBet.objects.filter(date__year=year).exclude(result="pending")

    # Create total_sport from full records (no sport/date filter)
    total_sport = {}
    for record in full_records:
        if not record.sport or len(record.sport.strip()) <= 1:
            continue
        sport_name = record.sport.upper()
        if sport_name not in total_sport:
            total_sport[sport_name] = {
                'loss': 0,
                'win': 0,
                'roi': 0,
                'total_units': 0
            }

    # Now apply filters for the displayed records
    records = full_records
    if sport_filter:
        records = records.filter(sport__iexact=sport_filter)
    if start_date:
        records = records.filter(date=start_date)

    # Dictionaries to calculate per-sport stats for filtered records
    total_losses_by_sport = defaultdict(int)
    total_wins_by_sport = defaultdict(int)
    total_roi_by_sport = defaultdict(int)

    for record in records:
        sport_name = record.sport.upper()
        if sport_name not in total_sport:
            continue  # skip unknown sport

        if record.result.lower() == 'loss':
            total_losses_by_sport[sport_name] += 1
            total_sport[sport_name]['loss'] += 1
        elif record.result.lower() == 'win':
            total_wins_by_sport[sport_name] += 1
            total_sport[sport_name]['win'] += 1

        if record.total_earn is not None and record.risk:
            risk = float(record.risk) if float(record.risk) != 0 else 1
            roi = float(record.total_earn) / risk
            total_units = float(record.total_earn) / 100

            total_sport[sport_name]['roi'] += round(roi, 2)
            total_sport[sport_name]['total_units'] += round(total_units, 2)

        total_sport[sport_name]['roi'] = round(total_sport[sport_name]['roi'], 2)
        total_sport[sport_name]['total_units'] = round(total_sport[sport_name]['total_units'], 2)

    # Calculate win %
    for sport, data in total_sport.items():
        total = data['win'] + data['loss']
        total = total if total != 0 else 1
        data['win_percentage'] = round((data['win'] / total) * 100, 1)

    # Global stats
    total_wins = sum(s['win'] for s in total_sport.values())
    total_losses = sum(s['loss'] for s in total_sport.values())
    total_units = round(sum(s['total_units'] for s in total_sport.values()), 2)
    roi_values = [s['roi'] for s in total_sport.values() if s['roi'] != 0]
    overall_roi = round(sum(roi_values) / len(roi_values), 2) if roi_values else 0

    global_stats = {
        'roi': overall_roi,
        'total_units': total_units,
        'total_wins': total_wins,
        'total_losses': total_losses
    }

    # Session stats
    session_total_wins = sum(1 for r in records if r.result.lower() == 'win')
    session_total_losses = sum(1 for r in records if r.result.lower() == 'loss')
    session_total = session_total_wins + session_total_losses or 1

    session_stats = {
        'win_percentage': round((session_total_wins / session_total) * 100, 1),
        'loss_percentage': round((session_total_losses / session_total) * 100, 1)
    }

    return render(request, 'record.html', {
        'records': records,
        'total_sport': total_sport,
        'total_losses_by_sport': dict(total_losses_by_sport),
        'total_wins_by_sport': dict(total_wins_by_sport),
        'total_roi_by_sport': dict(total_roi_by_sport),
        'year': year,
        'global_stats': global_stats,
        'session_stats': session_stats,
        'seasons': seasons
    })




def add_message(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        if title and body:
            Message.objects.create(title=title, body=body)
        return redirect('plays')
    return redirect('plays')

def change_state(request):
    if request.method == 'POST':
        state = request.POST.get('status')
        print(state)
        if state:
            config = Config.objects.get(key='SESSIONS_STATE')
            config.value=state
            config.save()
        return redirect('plays')
    return redirect('plays')

def logout(request):
    auth_logout(request)
    return redirect('home3')


def BOT(request):
    if request.user.is_authenticated:
        user = request.user
        user.last_visit = datetime.now()
        user.save()
        
    search_input = ""
    sport = 'all'
    group = 'all'
    search_by = "filter"
    # if authenticated
    if request.user.is_authenticated:
        filter_record = FilterRecord.objects.get_or_create(user = request.user)
        filter_record = filter_record[0]
                
        #Get user groups
        groups = UserGroups.objects.filter(user_id__username = request.user)
        user_instance =  UserModel.objects.get(username = request.user) 
        is_available = len(groups) < user_instance.num_groups
        grup_ids = []
        for g in groups:
            grup_ids.append(g.group.id)
            
        try:
            is_packg_available = (datetime.now().date() - user_instance.start_date).days <= user_instance.pkg_days
        except:
            is_packg_available = False    
        tweets = Tweet.objects.filter(Q(group__id__in = grup_ids)).order_by('-created_at')
        # groups = Group.objects.all()
        if request.method == 'GET':
            
            search_input = request.GET.get('search_input')
            group = request.GET.get('groups')
            sport = request.GET.get('sports')
            search_by = request.GET.get('search_by')
            search_input = request.GET.get('search_input')
            
            if group is None and sport is None and search_input is None:
                group = request.session.get("group")
                search_by = request.session.get("search_by")
                sport = request.session.get("sport")
                search_input = request.session.get("search_term")
                
                
                group = filter_record.group
                search_by = filter_record.search_by
                sport = filter_record.sport
                search_input = filter_record.search_term
                
            
            group = "" if group == "all" or group is None else group
            sport = "" if sport == 'all' or sport is None else sport
            search_input = "" if search_input is None else search_input
            
            if search_by == 'filter':
                if group != "":
                    tweets = Tweet.objects.all().filter(
                    (Q(tweet_text__icontains = search_input) |
                        Q(user_name__icontains = search_input)) &
                        Q(tweet_text__icontains=sport) &
                        Q(group__group__icontains=group)&
                        Q(group__id__in =grup_ids)
                        ).order_by('-created_at')
                else:
                    tweets = Tweet.objects.all().filter(
                        Q(tweet_text__icontains=sport) &
                        (Q(tweet_text__icontains = search_input) | 
                        Q(user_name__icontains = search_input)) &Q(group__id__in =grup_ids)
                        ).order_by('-created_at')

            else:
                tweets = Tweet.objects.all().filter((Q(tweet_text__icontains = search_input) | Q(user_name__icontains = search_input)) & Q(group__id__in =grup_ids) ).order_by('-created_at')
        group = "all" if group == "" else group
        sport = "all" if sport == '' else sport
        # Add Search_by, group and sport in local storage
        filter_record.search_by = search_by
        filter_record.search_term = search_input
        filter_record.group = group
        filter_record.sport = sport
        filter_record.save()
        
        
        return render(request, 'BOT.html', {
            'tweets': tweets, 'groups':groups,
            "search_input": search_input,
            "group": group,
            "sports":sport,
            "is_available": is_available,
            'pkg_available':is_packg_available,
            'tweets_found':len(tweets),
            'search_by': search_by
        })
    else:
        # products = Product.objects.all()
        products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
        print(products)
        return render( request, 'BotHome.html', {"products": products})


def BOT_PUBLIC(request):
    if request.method == "POST":
        if request.user.is_authenticated and request.user.is_superuser:
            new_handle = request.POST.get("new_handle")
            PublicTweetHandle.objects.get_or_create(user_name = new_handle.strip())
            
    if request.GET.get("handle") != None and request.GET.get("handle").strip() != "":
        handle = request.GET.get("handle")
        handle = handle.strip()
        handles = PublicTweetHandle.objects.values("user_name").filter(user_name__iexact = handle)
    else:
        handles = PublicTweetHandle.objects.values("user_name").filter()
    
    handles = [h['user_name'] for h in handles]
    tweets = Tweet.objects.filter(user_name__in = handles).order_by("-created_at")
    
    all_handles = PublicTweetHandle.objects.all()
    all_handles = [h.user_name for h in all_handles]
    context = {
        'handles': all_handles,
        'tweets': tweets,
    }
    
    return render(request, 'BOT_PUBLIC.html', context)


def get_updated_tweets_public(request):
    
        prev_tweets = request.GET.get('previous_count')
        if request.GET.get("handle") != None and request.GET.get("handle").strip() != "":
            handle = request.GET.get("handle")
            handle = handle.strip()
            handles = PublicTweetHandle.objects.values("user_name").filter(user_name__iexact = handle)
        else:
            handles = PublicTweetHandle.objects.values("user_name").filter()
        
        handles = [h['user_name'] for h in handles]
        tweets = Tweet.objects.filter(user_name__in = handles).order_by("-created_at")
        
        
        # tweets = Tweet.objects.all().order_by('-created_at')
        html_content = render_to_string('tweets_partial.html', {'tweets': tweets, "tweets_found":len(tweets), "prev_tweets":-int(prev_tweets)})
        return JsonResponse({'html_content': html_content, 'tweets_found':tweets.count()})




def BOT_VIEW_ALL(request):
    search_input = ""
    sport = 'all'
    group = 'all'
# if authenticated
    if request.user.is_authenticated:
        #Get user groups
        groups = UserGroups.objects.filter(user_id__username = request.user)
        user_instance =  UserModel.objects.get(username = request.user) 
        is_available = len(groups) < user_instance.num_groups
        grup_ids = []
        for g in groups:
            grup_ids.append(g.group.id)
            
        try:
            is_packg_available = (datetime.now().date() - user_instance.start_date).days <= user_instance.pkg_days
        except:
            is_packg_available = False    
        tweets = Tweet.objects.filter(Q(group__id__in = grup_ids)).order_by('-created_at')
        # groups = Group.objects.all()
        print(len(tweets))
        
        if request.method == 'POST':
            search_input = request.POST.get('search_input')
            group = request.POST.get('groups')
            sport = request.POST.get('sports')
            
            group = "" if group == "all" else group
            sport = "" if sport == 'all' else sport

            if request.POST.get('search_by') == 'filter':
                if group != "":
                    tweets = Tweet.objects.all().filter(
                    (Q(tweet_text__icontains = request.POST.get('search_input')) |
                        Q(user_name__icontains = search_input)) &
                        Q(tweet_text__icontains=sport) &
                        Q(group__group__icontains=group)&
                        Q(group__id__in =grup_ids)
                        ).order_by('-created_at')
                else:
                    tweets = Tweet.objects.all().filter(
                        Q(tweet_text__icontains=sport) &
                        (Q(tweet_text__icontains = request.POST.get('search_input')) | 
                        Q(user_name__icontains = search_input)) &Q(group__id__in =grup_ids)
                        ).order_by('-created_at')

            else:
                tweets = Tweet.objects.all().filter((Q(tweet_text__icontains = request.POST.get('search_input')) | Q(user_name__icontains = search_input)) & Q(group__id__in =grup_ids) ).order_by('-created_at')
        group = "all" if group == "" else group
        sport = "all" if sport == '' else sport


        return render(request, 'BOT_view_all.html', {
            'tweets': tweets, 'groups':groups,
            "search_input": search_input,
            "group": group,
            "sports":sport,
            "is_available": is_available,
            'pkg_available':is_packg_available,
            'tweets_found':len(tweets),
        })
    else:
        return render( request, 'BotHome.html')

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        data = request.POST

        # Required fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()

        if not name or not email:
            return JsonResponse({'success': False, 'error': 'Name and Email are required.'})

        if UserModel.objects.filter(username=email).exists():
            return JsonResponse({'success': False, 'error': 'User already exists'})

        # Optional fields
        last_name = data.get('last_name', '')
        package = data.get('package')
        plan = data.get('plan')
        plan_price = data.get('plan_price')
        num_groups = data.get('num_groups') or 0
        pkg_days = data.get('pkg_days') or 0

        plays_package = data.get('plays_package')
        plays_plan = data.get('plays_plan')
        plays_price = data.get('plays_price')
        plays_pkg_days = data.get('plays_pkg_days') or 0
        is_activate_playes = data.get('is_activate_playes', 'false').lower() == 'true'

        # Generate random password
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        try:
            user = UserModel.objects.create(
                username=email,
                email=email,
                name=name,
                last_name=last_name,
                package=package,
                plan=plan,
                plan_price=plan_price,
                num_groups=int(num_groups),
                pkg_days=int(pkg_days),
                plays_package=plays_package,
                plays_plan=plays_plan,
                plays_price=plays_price,
                plays_pkg_days=int(plays_pkg_days),
                is_activate_playes=is_activate_playes,
                plays_start_date=datetime.now().date() if is_activate_playes else None,
                start_date=datetime.now().date(),
                user_type='FEEDMEUSER',
                plays_payment_status = True,
                plays_payment_type = "Crypto",
                payment_status = True,
                payment_type = "Crypto",
                user_password=random_password,
            )

            user.set_password(random_password)
            user.user_password = random_password
            user.save()

            # Email user
            registration_email(
                email=email,
                subject="Feedme Registration",
                template_name="./email_template.html",
                context={'username': email, 'password': random_password}
            )

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def register_playsuser(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        raw_email = request.POST.get('email', '')
        email = raw_email.strip()
        plan_type = request.POST.get('type', '')
        plan_card = request.POST.get('card', '')
        plan_price = request.POST.get('price', '')
        print("fields have in user registrations", plan_type, plan_card, plan_price, name, email)

        if not name or not email:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})

        if UserModel.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email already registered'})

        base_username = name.lower().replace(' ', '')
        username = base_username
        counter = 1
        while UserModel.objects.filter(username=email).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = None  # ✅ Define upfront to avoid NameError
        try:
            # Create user
            random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user = UserModel.objects.create(
                email=email.strip(),       
                username=email.strip(),
                name=name,
                last_name=name,
                user_type='FEEDMEUSER',
                is_activate_playes=True,
                plays_package=plan_type,
                plays_start_date=datetime.now().date(),
                plays_plan=plan_card,
                plays_price=plan_price,
                plays_pkg_days="365",
                user_password=random_password,
            )
            user.set_password(random_password)

            try:
                registration_email(
                    email=email,
                    subject="Feedme Registration",
                    template_name="./email_template.html",
                    context={'username': email, 'password': random_password}
                )
                                # Send admin notification
                admin_message = f"""
                New user registered:
                Name: {name}
                Email: {email}
                Type: {plan_type}
                Plays: {plan_card}
                Plays Price: {plan_price}
                """

                registration_email(
                    email="aliashrafmirza169@gmail.com",
                    subject="New Giveaways User Registered",
                    template_name=None,  # or you can create a new plain text template
                    context={"message": admin_message}
                )
                user.save()
                return JsonResponse({'success': True, 'message': 'User registered successfully'})  # ✅ success

            except Exception as e:
                user.delete()
                return JsonResponse({'success': False, 'error': 'Email sending failed: ' + str(e)})

        except Exception as e:
            if user:
                user.delete()
            return JsonResponse({'success': False, 'error': str(e)})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})




from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Tweet, UserGroups

def get_updated_tweets(request):
    group = request.GET.get('groups', 'all')
    sport = request.GET.get('sports', 'all')
    page = request.GET.get('page', 1)
    prev_tweets = request.GET.get('previous_count', 0)
    search_input = request.GET.get('search_input', '')

    group = "" if group == "all" else group
    sport = "" if sport == "all" else sport

    groups = UserGroups.objects.filter(user_id__username=request.user)

    # Then fetch the updated object to access its fields
    filter_record = FilterRecord.objects.get(user=request.user)
    print("UPDATE FILTE", filter_record.group)

    grup_ids = [g.group.id for g in groups]

    if group != "":
        tweets = Tweet.objects.filter(
            (Q(user_name__icontains=search_input) | Q(tweet_text__icontains=search_input)) &
            Q(tweet_text__icontains=sport) &
            Q(group__group__icontains=group) &
            Q(group__id__in=grup_ids)
        ).order_by('-created_at')
        print("filter tweets", tweets)
    else:
        tweets = Tweet.objects.filter(
            (Q(user_name__icontains=search_input) | Q(tweet_text__icontains=search_input)) &
            Q(tweet_text__icontains=sport) &
            Q(group__id__in=grup_ids)
        ).order_by('-created_at')
        print("filter tweets", tweets)

    # Find color from UserGroups if a specific group is selected
    # tweet_border_color = TweetConfigrations.objects.get(user_id__username=request.user, tweet_name=tweets.user_name)
    # Get all unique usernames in the current tweet set
    usernames = tweets.values_list('user_name', flat=True).distinct()

    # Get corresponding TweetConfigrations
    configs = TweetConfigrations.objects.filter(user_id__username=request.user, tweet_name__in=usernames)

    # Build a mapping of username → color
    tweet_border_colors = {config.tweet_name: config.color for config in configs}
    tweet_notification_sound = {
        config.tweet_name: config.notification_sound or 'video1.mp4'
        for config in configs
    }
    for username in usernames:
        if username not in tweet_notification_sound:
            tweet_notification_sound[username] = 'video1.mp4'

    paginator = Paginator(tweets, 150)
    page_obj = paginator.get_page(page)

    html_content = render_to_string('tweets_partial.html', {
        'tweets': page_obj,
        'page_obj': page_obj,
        'tweets_found': paginator.count,
        'prev_tweets': -int(prev_tweets),
        'tweet_border_colors': tweet_border_colors,
        'tweet_notification_sound': tweet_notification_sound,
    }, request=request)

    return JsonResponse({
        'html_content': html_content,
        'tweets_found': paginator.count,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'tweet_border_colors': tweet_border_colors,
        'tweet_notification_sound': tweet_notification_sound,
    })




def checkout_success(request):
    session_id = request.GET.get('session_id')
    # session = stripe.checkout.Session.retrieve(session_id)
    # print(session)
    # return render(request, 'checkout_success.html', {'session': session})
    
    checkout_session = stripe.checkout.Session.retrieve(session_id)
    payment_intent_id = checkout_session.payment_intent

    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

    # Now you can access payment details, such as amount, currency, status, etc.
    amount_paid = payment_intent.amount_received / 100  # Convert to dollars or your currency
    # Retrieve custom field values
    custom_fields = checkout_session.custom_fields
    customer_email = checkout_session['customer_details']['email']
    shipping_address = custom_fields[0]['text']['value']
    
    sale = Sale.objects.create(
        customer_email = customer_email,
        shipping_address = shipping_address,
        session_id = session_id,
        amount_paid = amount_paid,
    )
    
    subject = "New Order on Feedme.bet"
    body = "New order received on Feedme.bet"
    body2 = "New order placed on Feedme.bet"
    body += f"\r\nCustomer Email: {customer_email}"
    body += f"\r\nShipping Address: {shipping_address}"
    body += f"\r\nOrder Details:"
    
    body2 += f"\r\nCustomer Email: {customer_email}"
    body2 += f"\r\nShipping Address: {shipping_address}"
    body2 += f"\r\nOrder Details:"
    
    
    items = request.session.get('cart').values()
    for item in items:
        SaleItem.objects.create(
            sale = sale,
            product_name = item['product']['full_name'],
            size = item['size'],
            quantity = item['quantity']
            
        )
        body += f"\r\n - {item['product']['full_name']} {item['size']} ({item['quantity']})"
        body2 += f"\r\n - {item['product']['full_name']} {item['size']} ({item['quantity']})"
    
    body += "\r\n Total Amount: $" + str(amount_paid)
    body2 += "\r\n Total Amount: $" + str(amount_paid)
    # threading.Thread(target=send_mail, args=(subject, body, "Feedme <newsfeed@feedme.bet", ["joeytunes2@gmail.com", "aliashrafmirza169@gmail.com"], False)).start()
    # joeytunes2@gmail.com
    try:
        notification_mails = [ADMIN_EMAIL, "aliashrafmirza169@gmail.com"]
        threading.Thread(target=send_mail, args=(subject, body, "Feedme <newsfeed@feedme.bet>", notification_mails, False)).start()
    except:
        pass
    try:
        threading.Thread(target=send_mail, args=(subject, body2, "Feedme <newsfeed@feedme.bet>", [customer_email], False)).start()
    except:
        pass
    
    request.session['cart'] = { }
    
    return render(request, 'checkout_success.html')

def checkout_failed(request):
    return render(request, 'checkout_failed.html')


def add_tweet_group(request):
    if request.method == "POST":
        group_link = request.POST.get('group-url', '').strip()
        group_name = request.POST.get('group-name', '').strip()

        if not group_name or not group_link:
            # Optionally handle empty input
            return redirect("BOT2")

        # Create group if it doesn't exist
        group, created = Group.objects.get_or_create(
            group_link=group_link,
            defaults={'group': group_name}
        )

        if created:
            # # Send notification email to admins
            # send_reg_mail(
            #     ["aliashrafmirza169@gmail.com"],
            #     "New tweet group added",
            #     f"New Tweet Group added:\nName: {group_name}\nLink: {group_link}"
            # )
            send_reg_mail(
                email=['aliashrafmirza169@gmail.com'],
                subject="New tweet group added",
                message=f"New Tweet Group added:\nName: {group_name}\nLink: {group_link}"
            )

        # Add user to the group
        UserGroups.objects.get_or_create(
            group=group,
            user_id=UserModel.objects.get(username=request.user),
            defaults={'group_name': group_name}
        )

    return redirect("BOT2")


def delete_group(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)

    group_name = request.POST.get("group_name")

    if not group_name:
        return JsonResponse({"success": False, "error": "Missing group name"}, status=400)

    try:
        group_qs = UserGroups.objects.filter(user_id__username=request.user, group_name=group_name)
        if not group_qs.exists():
            return JsonResponse({"success": False, "error": "Group not found"}, status=404)

        group_qs.delete()
        filter_record = FilterRecord.objects.get(user=request.user)
        print("Before saving group:", filter_record.group)
        filter_record.group = "all"
        filter_record.save()
        print("After saving group:", FilterRecord.objects.get(user=request.user).group)

        return JsonResponse({"success": True})
    except Exception as e:
        logger.error("Error deleting group: %s", str(e))
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
@csrf_exempt
def delete_groupname(request):
    if request.method == "POST":
        group_name = request.POST.get("group_name")
        if group_name:
            try:
                groups = UserGroups.objects.filter(group_name=group_name)
                deleted_count = groups.count()
                groups.delete()
                return JsonResponse({"success": True, "deleted": deleted_count})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
        else:
            return JsonResponse({"success": False, "error": "Missing group_name"})
    return JsonResponse({"success": False, "error": "Invalid request method"})

@csrf_exempt
def delete_tweeturl(request):
    if request.method == "POST":
        tweeturl = request.POST.get("tweet_url", "").strip()
        print("terrt url", tweeturl)

        if tweeturl:
            try:
                tweet = Tweet.objects.filter(tweet_url__iexact=tweeturl)
                print("Filtered tweets:", tweet)
                deleted_count = tweet.count()
                tweet.delete()
                return JsonResponse({"success": True, "deleted": deleted_count})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
        else:
            return JsonResponse({"success": False, "error": "Missing tweet_url"})
    return JsonResponse({"success": False, "error": "Invalid request method"})


    
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def delete_a_group(request):
    if request.method != "DELETE":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        group_link = data.get("group_link")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    if not group_link:
        return JsonResponse({"success": False, "error": "Group link is required"}, status=400)

    # Sirf group_link se filter karo
    groups = Group.objects.filter(group_link=group_link)

    if not groups.exists():
        return JsonResponse({"success": False, "error": "Group not found"}, status=404)

    deleted_count = 0

    # -------- Part 1: group_name blank/null walon ko delete karo --------
    blank_groups = groups.filter(group__isnull=True) | groups.filter(group="")
    deleted_count += blank_groups.count()
    blank_groups.delete()

    # -------- Part 2: Jinke group_name hai, unka first chor ke baaki delete karo --------
    named_groups = groups.exclude(group__isnull=True).exclude(group="")

    if named_groups.count() > 1:
        first_named_group = named_groups.first()
        remaining_named_groups = named_groups.exclude(id=first_named_group.id)
        deleted_count += remaining_named_groups.count()
        remaining_named_groups.delete()

    return JsonResponse({"success": True, "deleted_count": deleted_count})    


def get_code(request):
    email = request.POST.get("email")
    verification_code = random.randint(10000,99999)
    try:
        user = UserModel.objects.get(email = email)
        user.verification_code = verification_code
        send_reg_mail(
            email=email,
            subject="Reset Password",
            message=f"Your verification code to reset password: {verification_code}",
        )
        user.save()
        return JsonResponse({"success":True})
    except Exception as e:
        return JsonResponse({"success":False,"error":e})


def reset_password(request):
    email = request.POST.get("email")
    verification_code = request.POST.get("verification_code")
    password1 = request.POST.get("password1")
    password2 = request.POST.get("password2")
    print(password1)

    if(password1 != password2):
        return JsonResponse({"success":False, 'msg':"Password Do not match"})

    user = UserModel.objects.get(email=email)
    verif_code = user.verification_code
    print(user)
    if int(verification_code) == verif_code:
        user.set_password(password1)
        user.save()
        return JsonResponse({"success":True})    
    else:
        return JsonResponse({"success":False, 'msg':"Verification Code is not correct"})


from datetime import datetime

def myPlan(request):
    if not request.user.is_authenticated:
        return redirect("home3")
    
    user_instance = UserModel.objects.get(username=request.user.username)

    success = False  # Flag for frontend

    # Password update
    if request.method == "POST":
        password = request.POST.get("newPassword")
        if password:
            user_instance.set_password(password)
            user_instance.save()
            success = True
            messages.success(request, "Password updated successfully!")

    # -------- NewsFeed Subscription --------
    total_days = user_instance.pkg_days or 0
    start_date = user_instance.start_date
    subscription_plan = user_instance.plan
    subscription_price = user_instance.plan_price

    if start_date:
        used_days = (datetime.now().date() - start_date).days
        if used_days > total_days:
            days_left = 0
            percentage = 100
        else:
            days_left = total_days - used_days
            percentage = round((days_left / total_days) * 100) if total_days else 0
    else:
        days_left = 0
        percentage = 0

    # -------- Plays Subscription --------
    plays_total_days = user_instance.plays_pkg_days or 0
    plays_start_date = user_instance.plays_start_date
    plays_subscription_plan = user_instance.plays_plan
    plays_subscription_price = user_instance.plays_price

    if plays_start_date:
        used_days = (datetime.now().date() - plays_start_date).days
        if used_days > plays_total_days:
            plays_days_left = 0
        else:
            plays_days_left = plays_total_days - used_days
    else:
        plays_days_left = 0

    return render(request, 'myPlan.html', {
        # NewsFeed
        "days_left": days_left,
        "subscription_price": subscription_price,
        "subscription_plan": subscription_plan,
        "start_date": start_date,
        "total_days": total_days,
        "percentage": percentage,

        # Plays
        "plays_days_left": plays_days_left,
        "plays_subscription_price": plays_subscription_price,
        "plays_subscription_plan": plays_subscription_plan,
        "plays_start_date": plays_start_date,
        "plays_total_days": plays_total_days,

        "success": success,
    })

from django.contrib import messages

@login_required
def update_profile(request):
    if request.method == "POST":
        user = request.user
        user.name = request.POST.get("name", user.name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save()
        messages.success(request, "Profile updated successfully.")
    return redirect("myProfile")







# dashboard
@login_required(login_url="loginPage")
def dashboard(request):
    try:
        feedme = Feedme.objects.get()
    except: 
        feedme = Feedme.objects.create()
    
    newsfeed_revenue = SubscriptionRecords.objects.all().aggregate(Sum('amount'))['amount__sum']
    revenue = Sale.objects.all().aggregate(Sum('amount_paid'))['amount_paid__sum']
    bots_running = Group.objects.filter(is_running = True).count()
    last_play = Message.objects.all().last().body
    
    # Weekly Visits and Subscriptions
    weekly_visitors = get_weekly_visits()
    weekly_subscriptions = get_weekly_subscriptions()
    # Monthly Visits and Subscriptions
    monthly_visitors = get_monthly_visits()
    monthly_subscriptions = get_monthly_subscriptions()
    
    context = {
        'feedme': feedme,
        'newsfeed_revenue':newsfeed_revenue,
        'revenue':revenue,
        'bots_running':bots_running,
        'last_play': last_play,
        'weekly_data': weekly_visitors,
        'monthly_data': monthly_visitors,
        'weekly_data_sub': weekly_subscriptions,
        'monthly_data_sub': monthly_subscriptions,
        }
    return render(request, 'admin/dashboard.html', context)


@login_required(login_url="loginPage")
def dasProducts(request):
    products = ProductVariation.objects.all()
    return render(request, 'admin/products.html',{'products':products})

@login_required(login_url="loginPage")
def dasRecords(request):
    from datetime import date
    today = date.today()
    cfb_enabled = not (date(today.year, 1, 19) <= today <= date(today.year, 8, 23))
    nfl_enabled = not (date(today.year, 2, 8) <= today <= date(today.year, 9, 4))
    if request.method == "POST":
        id = request.POST.get('id')
        result = request.POST.get("result")
        juice = request.POST.get("juice")
        risk = request.POST.get("risk")
        win = request.POST.get("win")
        play = request.POST.get("play")
        earn = request.POST.get("earn")
        is_free = request.POST.get('is_free') == '1'
        is_premium = request.POST.get('is_premium') == '1'
        is_nfl = request.POST.get('is_nfl') == '1'
        is_cfb = request.POST.get('is_cfb') == '1'
        is_monthly = request.POST.get('is_monthly') == '1'
        game_number = request.POST.get("game_number")


        from datetime import date
        if request.POST.get("action") == "delete":
            record = NewRecord.objects.get(id=id)

            if SportsBet.objects.filter(sport=record.sport, game_number=record.game_number, date=record.date).exists():
                SportsBet.objects.get(sport=record.sport, game_number=record.game_number, date=record.date).delete()

            # Also delete the related message if needed
            Message.objects.filter(title=record.sport, body__contains=record.game_number).delete()

            record.delete()

        else:
            record = NewRecord.objects.get(id=id)
            record.result = result
            record.juice = juice
            record.play = play
            record.win = win
            record.risk = risk
            record.total_earn = earn
            record.is_free = is_free
            record.is_premium = is_premium
            record.is_nfl = is_nfl
            record.is_cfb = is_cfb
            record.is_monthly = is_monthly
            record.game_number = game_number

            record.save()

            if SportsBet.objects.filter(sport=record.sport, game_number=record.game_number, date=record.date).exists():
                sports_bet = SportsBet.objects.get(sport=record.sport, game_number=record.game_number, date=record.date)
                sports_bet.result = result
                sports_bet.juice = juice
                sports_bet.play = play
                sports_bet.win = win
                sports_bet.risk = risk
                sports_bet.total_earn = earn
                sports_bet.game_number = game_number
                sports_bet.save()
            else:
                SportsBet.objects.create(
                    sport=record.sport,
                    game_number=record.game_number,
                    play=record.play,
                    juice=record.juice,
                    risk=record.risk,
                    win=record.win,
                    result=record.result,
                    total_earn=record.total_earn,
                    date=record.date,
                )

            # Create or update the message
            extra_field = record.juice or record.game_number or record.total_earn

            message_body = (
                f"{record.sport}"
                f" {extra_field if extra_field else ''}"
                f" {record.play}"
                " #FEEDME"
            )

            # Try to update the first matching message
            extra_field = record.juice or record.game_number or record.total_earn

            if extra_field:
                matching_messages = Message.objects.filter(
                    play_id=record.id,
                    title=record.sport,
                    body__contains=str(extra_field)
                )
            else:
                # Fallback: if none present, just match sport + play_id
                matching_messages = Message.objects.filter(
                    play_id=record.id,
                    title=record.sport
                )

            if matching_messages.exists():
                # Update first match
                msg = matching_messages.first()
                play_id=record.id,
                msg.body = message_body
                msg.is_free = record.is_free
                msg.is_premium = record.is_premium
                msg.is_cfb = record.is_cfb
                msg.is_nfl = record.is_nfl
                msg.is_monthly = record.is_monthly
                msg.results = record.result
                msg.save()
                print("Message updated:", msg)
            else:
                # Create new message
                extra_field = record.juice or record.game_number or record.total_earn

                message_text = (
                    f"{record.sport}"
                    f" {extra_field if extra_field else ''}\n"
                    f"{record.play}\n"
                    "#FEEDME"
                )
                msg = Message.objects.create(
                    play_id=record.id,
                    title=record.sport,
                    body=message_body,
                    is_free=record.is_free,
                    is_premium=record.is_premium,
                    is_cfb = record.is_cfb,
                    is_nfl = record.is_nfl,
                    is_monthly = record.is_monthly,
                    results = record.result
                )
                print("Message created:", msg, message_text)
                if not record.is_free:
                    post_to_channel(message_text)
                request.session['play_sound'] = True



    records = NewRecord.objects.all().order_by("-date")
    return render(request, 'admin/Records.html', {
        "records": records,
        "cfb_enabled": cfb_enabled,
        "nfl_enabled": nfl_enabled})


# addRecord

@login_required(login_url="loginPage")
def addRecord(request):
    if request.method == "POST":
        
        Date  = request.POST.get("Date")
        Juice = request.POST.get("Juice")
        Sport = request.POST.get("Sport")
        Risk = request.POST.get("Risk")
        Game  = request.POST.get("Game")
        Win  = request.POST.get("Win")
        Play  = request.POST.get("Play")
        Earning = request.POST.get("Earning")
        result = request.POST.get("result")
        is_free = request.POST.get('is_free') == '1'
        is_premium = request.POST.get('is_premium') == '1'
        is_nfl = request.POST.get('is_nfl') == '1'
        is_cfb = request.POST.get('is_cfb') == '1'
        is_monthly = request.POST.get('is_monthly') == '1'

        
        try:
            record = NewRecord.objects.create(
                date = datetime.strptime(Date,"%Y-%m-%d"),
                juice = Juice,
                sport = Sport,
                risk = Risk,
                game_number = Game,
                win = Win,
                play = Play,
                total_earn = Earning,
                result = result,
                is_free = is_free,
                is_premium = is_premium,
                is_nfl = is_nfl,
                is_cfb = is_cfb,
                is_monthly = is_monthly
            )
            # Pick one field in order: juice → game_number → total_earn
            extra_field = record.juice or record.game_number or record.total_earn

            message_text = (
                f"{record.sport}"
                f" {extra_field if extra_field else ''}\n"
                f"{record.play}\n"
                "#FEEDME"
            )

            giveaway = Message.objects.create(
                play_id=record.id,
                title=record.sport,
                is_free=is_free,
                is_premium=is_premium,
                is_nfl=is_nfl,
                is_cfb=is_cfb,
                is_monthly=is_monthly,
                results=result,
                body=(
                    f"{record.sport}"
                    f" {extra_field if extra_field else ''} "
                    f"{record.play} #FEEDME"
                )
            )

            print("Message created:", giveaway, message_text)
            if not is_free:
                post_to_channel(message_text)
            return redirect("dasaRecords")
        
        except Exception as e:
            return render(request, 'admin/AddRecord.html', {"error":e})
        
    return render(request, 'admin/AddRecord.html')

@login_required(login_url="loginPage")
def dasSales(request):
    if request.method == "POST":
        action = request.POST.get("action")
        status = request.POST.get("status")
        sale_id = request.POST.get("id")
        confirm_payment = request.POST.get("confirm_payment")  # <-- for checkbox

        if Sale.objects.filter(id=sale_id).exists():
            sale = Sale.objects.get(id=sale_id)

            if action == "update":
                sale.status = status
                sale.save()

                subject = "Order status update on Feedme.bet"
                body = f'Your Order Status is updated to {status}\r\n\nOrder Details:'
                body += f"\nOrder Date: {sale.date_time.strftime('%Y-%m-%d %H:%M')}"
                for item in sale.sale_items.all():
                    body += f"\r\n - {item.product_name} {item.size} ({item.quantity})"

                threading.Thread(
                    target=send_mail,
                    args=(subject, body, "Feedme <newsfeed@feedme.bet>", [sale.customer_email], False)
                ).start()

            # ✅ If admin confirms crypto payment
            if confirm_payment == "on" and sale.payment_method == "Crypto":
                subject = "Payment Confirmation - Feedme.bet"
                body = (
                    f"Dear Customer,\n\n"
                    f"We have received your crypto payment of ${sale.amount_paid}.\n"
                    f"Your order will be processed and delivered soon.\n\n"
                    f"Order Details:"
                )
                for item in sale.sale_items.all():
                    body += f"\r\n - {item.product_name} {item.size} ({item.quantity})"

                body += "\n\nThank you for shopping with us!\nSupport: support@feedme.bet"

                threading.Thread(
                    target=send_mail,
                    args=(subject, body, "Feedme <newsfeed@feedme.bet>", [sale.customer_email], False)
                ).start()

                # (Optional) also update status to Delivered
                sale.payment_status = True
                sale.save()

        return redirect("dasSales")

    sales = Sale.objects.all().order_by("-date_time")
    return render(request, "admin/Sales.html", {"sales": sales})



@login_required(login_url="loginPage")
def dasNewsFeed(request):
    if request.method=="POST":
        action = request.POST.get("action")
        if action == "update_group":
            id = request.POST.get("id")
            if Group.objects.filter(id = id).exists():
                group = Group.objects.get(id = id)
                group.is_running = not group.is_running
                group.save()
        elif action == "delete_user":
            id = request.POST.get('id')
            if UserModel.objects.filter(id = id).exists():
                UserModel.objects.get(id = id).delete()
                
    groups = Group.objects.all()
    users = UserModel.objects.filter().exclude(is_superuser = True)
    return render(request, "admin/NewsFeed.html", {'customers':users, 'groups':groups})

@login_required(login_url="loginPage")
def contactMessages(request):
    if request.method == "POST":
        id = request.POST.get('id')
        if Contact.objects.filter(id = id).exists():
            Contact.objects.get(id = id).delete()

            return redirect('contactMessages')
    latest_messages = Contact.objects.all().order_by("-id")[:2000]
    # Get IDs of these 2000 messages
    latest_ids = [msg.id for msg in latest_messages]

    # Delete all others not in latest 2000
    Contact.objects.exclude(id__in=latest_ids).delete()
    return render(request, 'admin/ContactMessages.html', {'messages': latest_messages})
# AddProduct

@csrf_exempt
def delete_all_messages(request):
    if request.method == 'POST' and request.POST.get('action') == 'delete_all':
        Contact.objects.all().delete()
    return redirect(request.META.get('HTTP_REFERER', 'contactMessages'))

@login_required(login_url="loginPage")
def addProduct(request):
    if request.method=="POST":
        print(request.POST)
        print(request.FILES)
        
        product_title = request.POST.get("product-title")
        category = request.POST.get('category')
        product_description = request.POST.get('product-desc')
        variations = request.POST.getlist('variationName')
        variation_prices = request.POST.getlist("variationPrice")
        thumbnail = request.FILES.get('thumbnail')
        images = request.FILES.getlist('images')
        
        category = Category.objects.get(id = category)
        product = Product.objects.get_or_create(
            category = category,
            title = product_title,
            description = product_description,
        )
        product = product[0]
        
        Thumbnail.objects.filter(product = product).delete()
        Thumbnail.objects.create(
            image = thumbnail,
            product=product
        )
        
        for img in images:
            ProductImage.objects.create(
                product = product,
                image = img
            )
            
        for i in range(len(variations)):
            ProductVariation.objects.get_or_create(
                product = product,
                name = variations[i],
                price = float(variation_prices[i])
            )
            
            
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'admin/AddProduct.html', context=context)


def addvariation(request):
    
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        product = request.POST.get("product")
        
        ProductVariation.objects.get_or_create(
            name = name,
            price = float(price),
            product = Product.objects.get(id = product)
        )
        
        return redirect('dasProducts')
    
    products = Product.objects.all()
    # products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, "admin/AddVariation.html", {"products":products})


def updateVariation(request, id):
    if ProductVariation.objects.filter(id = id).exists():
        variation = ProductVariation.objects.get(id = id)
        if request.method == "POST":
            if request.POST.get("action") == "delete":
                ProductVariation.objects.get(id = id).delete()
                return redirect("dasProducts")
            else:
                title = request.POST.get('product-title')
                category = request.POST.get("category")
                v_name = request.POST.get('name')
                v_price = request.POST.get('price')
                
                
                product = variation.product
                
                product.title = title
                product.category = Category.objects.get(id = category)
                
                variation.name = v_name
                variation.price = v_price
                
                product.save()
                variation.save()
                
                return redirect("dasProducts")
                
        
        categories = Category.objects.all()
        return render(request, "admin/UpdateVariation.html", {"variation":variation, 'categories':categories})
    return redirect("dasProducts")


import os
def OneSignalSDKWorker(request):
    # return the onesignalsdkworker.js The file must be served with a content-type of application/javascript; charset=utf-8.
    file_location = os.path.join(settings.BASE_DIR, 'OneSignalSDKWorker.js')
    with open(file_location, 'r') as file:
        data = file.read()
    return HttpResponse(data, content_type='application/javascript; charset=utf-8')




def get_weekly_visits():
    current_date = datetime.now()
    first_day_of_year = datetime(current_date.year, 1, 1)
    weekly_visits = WeeklyVisitors.objects.filter(year=current_date.year)
    weekly_data = {}
    
    for visit in weekly_visits:
        week = visit.week
        if week not in weekly_data:
            weekly_data[week] = visit.visitors
        else:
            weekly_data[week] += visit.visitors
    
    return weekly_data

def get_monthly_visits():
    current_date = datetime.now()
    one_year_ago = current_date - timedelta(days=365)
    monthly_visits = WeeklyVisitors.objects.filter(year__gte=one_year_ago.year, year__lte=current_date.year)
    monthly_data = {}
    
    for visit in monthly_visits:
        month = visit.month
        year = visit.year
        key = f"{month}/{year}"
        if key not in monthly_data:
            monthly_data[key] = visit.visitors
        else:
            monthly_data[key] += visit.visitors
    
    return monthly_data


def get_weekly_subscriptions():
    current_date = datetime.now()
    first_day_of_year = datetime(current_date.year, 1, 1)
    weekly_subscriptions = SubscriptionRecords.objects.filter(date_time__year=current_date.year)
    weekly_data = {}

    for sub in weekly_subscriptions:
        week = sub.date_time.isocalendar()[1]
        if week not in weekly_data:
            # weekly_data[week] = sub.amount
            weekly_data[week] = 1
        else:
            # weekly_data[week] += sub.amount
            weekly_data[week] += 1
    
    return weekly_data

def get_monthly_subscriptions():
    current_date = datetime.now()
    one_year_ago = current_date - timedelta(days=365)
    monthly_subscriptions = SubscriptionRecords.objects.filter(date_time__gte=one_year_ago)
    monthly_data = {}

    for sub in monthly_subscriptions:
        month = sub.date_time.month
        year = sub.date_time.year
        key = f"{month}/{year}"
        if key not in monthly_data:
            # monthly_data[key] = sub.amount
            monthly_data[key] = 1
        else:
            # monthly_data[key] += sub.amount
            monthly_data[key] += 1
    
    return monthly_data



def get_records_2024(request):
    records = SportsBet.objects.filter(date__year=2024).exclude(result="pending").order_by('-date')
    details = get_record_details(records)
    record_json = []
    for record in records:
        record_json.append(record.to_json())

    details['records'] = record_json
    details['year'] = '2024'
    return JsonResponse(details)

def get_records_2023(request):
    records = SportsBet.objects.filter(date__year=2023).exclude(result="pending").order_by('-date')
    details = get_record_details(records)
    record_json = []
    for record in records:
        record_json.append(record.to_json())

    details['records'] = record_json
    details['year'] = '2023'
    return JsonResponse(details)

def get_records_2022(request):
    records = SportsBet.objects.filter(date__year=2022).exclude(result="pending").order_by('-date')
    details = get_record_details(records)
    record_json = []
    for record in records:
        record_json.append(record.to_json())

    details['records'] = record_json
    details['year'] = '2022'
    return JsonResponse(details)

def get_records_2021(request):
    records = SportsBet.objects.filter(date__year=2021).exclude(result="pending").order_by('-date')
    details = get_record_details(records)
    record_json = []
    for record in records:
        record_json.append(record.to_json())

    details['records'] = record_json
    details['year'] = '2021'
    return JsonResponse(details)

def get_records_2020(request):
    records = SportsBet.objects.filter(date__year=2020).exclude(result="pending").order_by('-date')
    details = get_record_details(records)
    record_json = []
    for record in records:
        record_json.append(record.to_json())

    details['records'] = record_json
    details['year'] = '2020'
    
    return JsonResponse(details)

def get_records_lifetime(request):
    records = SportsBet.objects.filter().exclude(result="pending").order_by('-date')
    details = get_record_details(records)
    record_json = []
    for record in records:
        record_json.append(record.to_json())

    details['records'] = record_json
    details['year'] = 'lifetime'
    return JsonResponse(details)

def get_record_details(records):
    # Create dictionaries to store total losses and wins for each sport
    total_losses_by_sport = defaultdict(int)
    total_wins_by_sport = defaultdict(int)
    total_roi_by_sport = defaultdict(int)

    total_sport = {}

    for record in records:

        if len(record.sport) <= 1:
            continue

        if record.result.lower() == 'loss':
            total_losses_by_sport[record.sport] += 1
            
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['loss'] += 1
        elif record.result.lower() == 'win':
            total_wins_by_sport[record.sport] += 1
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            total_sport[record.sport]['win'] += 1
        else:
            if record.sport not in total_sport:
                total_sport[record.sport] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
        
        if record.total_earn and record.risk:
            desc = (float(record.risk))
            desc = 1 if desc == 0 else desc
            total_sport[record.sport]['roi'] += round( float(record.total_earn) / desc,2)
            total_sport[record.sport]['total_units'] += round(float(record.total_earn)/100 ,2)
            total_sport[record.sport]['total_units'] = round(total_sport[record.sport]['total_units'],2)

            total_sport[record.sport]['roi'] = round(total_sport[record.sport]['roi'],2)
        
            # print(record.total_earn , record.risk , total_sport[record.sport]['roi'])

            
            
        total_roi_by_sport[record.sport] =  3
        

    for key,value in total_losses_by_sport.items():
        if key not in total_wins_by_sport:
            total_wins_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}
            
    for key,value in total_wins_by_sport.items():
        if key not in total_losses_by_sport:
            total_losses_by_sport[key] = 0
        if key not in total_sport:
            total_sport[key] = {'loss': 0, 'win': 0, 'roi': 0, 'total_units':0}

    for key,value in total_sport.items():
        # calculate win percentage
        descrimator =  (total_sport[key]['win'] + total_sport[key]['loss'])
        descrimator = 1 if descrimator == 0 else descrimator
        
        total_sport[key]['win_percentage'] = round((total_sport[key]['win'] / descrimator) * 100, 1)
    
    
    
    return {'total_roi_by_sport': dict(total_roi_by_sport),  'total_sport':total_sport, 'year': '2024', 'total_losses_by_sport': dict(total_losses_by_sport), 'total_wins_by_sport': dict(total_wins_by_sport)}



@csrf_exempt
def add_order(request):
    sale_data = json.loads(request.body)
    example_format = {
        "customer_email":"EMAIL", 
        "shipping_address":"SHIPING ADDRESS", 
        "amount_paid":"232.32",
        "products": [
            {
                "product_name":"P1",
                "size":'M',
                "quantity":2
             },
            {
                "product_name":"P2",
                "size":'S',
                "quantity":1
             }
        ]
    }
    
    customer_email = sale_data['customer_email']
    shipping_address = sale_data['shipping_address']
    amount_paid = sale_data['amount_paid']
    products = sale_data['products']
    
    sale = Sale.objects.create(
        customer_email = customer_email,
        shipping_address = shipping_address,
        amount_paid = float(amount_paid),
    )
    for product in products:
        SaleItem.objects.create(
            product_name = product['product_name'],
            size = product['size'],
            quantity = product['quantity'],
            sale = sale
        )
    
    return JsonResponse({"Message": "Data Added Successfully"}, status = 200)

    
    
def get_products(request):
    products_list = []
    
    for product in Product.objects.all():
        variations = []
        for variation in product.variations.all():
            variations.append({
                "name": variation.name,
                "price": variation.price
            })
            
        products_list.append({
            "id": product.id,
            "title": product.title,
            'description': product.description,
            'category': product.category.name,
            'variations': variations,
            'images': [img.image.url for img in product.images.all()]
            
        })
        

    return JsonResponse({"products": products_list})


from django.core.paginator import Paginator
from django.db.models import Count, Q
from datetime import datetime
from django.shortcuts import render

def BOT2(request):
    if request.user.is_authenticated:
        user = request.user
        user.last_visit = datetime.now()
        user.save()

        products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)

        # Get the group, sport, and search term from the GET request
        group = request.GET.get('groups', 'all')
        sport = request.GET.get('sports', 'all')
        search_input = request.GET.get('search_input', '')
        print("What is in search input:", search_input)

        # Get or create the FilterRecord for the current user
        filter_record, created = FilterRecord.objects.get_or_create(user=request.user)
        user_instance = UserModel.objects.get(username=request.user)

        # Get the user's groups
        groups = UserGroups.objects.filter(user_id__username=request.user)
        is_available = len(groups) <= user_instance.num_groups
        grup_ids = [g.group.id for g in groups]
        saved_sound = user_instance.notification_sound  # Fetch the notification sound

        try:
            is_packg_available = (datetime.now().date() - user_instance.start_date).days <= user_instance.pkg_days
        except:
            is_packg_available = False

        # Inside your view after fetching user_instance
        try:
            if user_instance.plan == "custom":
                trialdaysleft = 0
            else:
                days_used = (datetime.now().date() - user_instance.start_date).days
                trial_days_total = 7
                trialdaysleft = max(trial_days_total - days_used, 0)
            print("left days", trialdaysleft)
        except:
            trialdaysleft = 0



        # If no group or sport is selected, fallback to session or saved filters
        if group == 'all' and sport == 'all':
            group = request.session.get("group", filter_record.group)
            sport = request.session.get("sport", filter_record.sport)
            search_input = request.session.get("search_term")

        # Apply the filters to the query
        group_filter = "" if group == "all" else group
        sport_filter = "" if sport == "all" else sport
        search_input = "" if search_input is None else search_input

        if Tweet.objects.count() > 5000:
            latest_ids = Tweet.objects.order_by('-created_at').values_list('id', flat=True)[:5000]
            Tweet.objects.exclude(id__in=list(latest_ids)).delete()

        # Update the filter_record with the new values
        filter_record.group = group
        filter_record.sport = sport
        filter_record.search_term = search_input
        filter_record.save()  # This saves the updated FilterRecord

        # Perform the tweet filtering
        if group != "all":
            tweets = Tweet.objects.filter(
                (Q(user_name__icontains=search_input) | Q(tweet_text__icontains=search_input)) &
                Q(tweet_text__icontains=sport_filter) &
                Q(group__group__icontains=group_filter) &
                Q(group__id__in=grup_ids)
            ).order_by('-created_at')
            print("filter tweets", tweets)
        else:
            tweets = Tweet.objects.filter(
                (Q(user_name__icontains=search_input) | Q(tweet_text__icontains=search_input)) &
                Q(tweet_text__icontains=sport_filter) &
                Q(group__id__in=grup_ids)
            ).order_by('-created_at')
            print("filter tweets", tweets)

        # Paginate the tweet results
        paginator = Paginator(tweets, 150)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        groups_all = Group.objects.all()
        # Get distinct tweet user_names
        tweet_usernames = list(Tweet.objects.values_list('user_name', flat=True).distinct())

        # Render the template with the updated filter values and tweets
        return render(request, 'bot2.html', {
            'page_obj': page_obj,
            'groups': groups,
            'group': group,
            'sports': sport,
            'is_available': is_available,
            'pkg_available': is_packg_available,
            'tweets_found': paginator.count,
            'saved_sound': saved_sound,  # Pass the saved sound to the template
            'savedgroup': filter_record.group,  # Ensure 'savedgroup' is always updated
            'trialdaysleft': trialdaysleft,
            'groups_all': groups_all,
            'tweet_usernames': tweet_usernames,  # Add this line

        })

    else:
        # If the user is not authenticated, show the pricing page
        products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
        return render(request, 'pricing.html', {'products': products})

def check_group_link(request):
    group_url = request.GET.get('group_url')
    try:
        group = Group.objects.get(group_link=group_url)
        return JsonResponse({'exists': True, 'group_name': group.group})
    except Group.DoesNotExist:
        return JsonResponse({'exists': False})

def pricing(request):
    try:
        products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
        return render(request, 'pricing.html', {'products': products})
    except Exception as e:
        print("not good:", e)
        return HttpResponse("Something went wrong while loading pricing.") 
def pricingPlays(request):
    try:
        # Products with variations
        products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)

        # SportsBet records for 2022 (exclude pending results)
        full_records = SportsBet.objects.filter(date__year=2023).exclude(result="pending").order_by('date')

        total_sport = defaultdict(lambda: {'loss': 0, 'win': 0, 'roi': 0, 'total_units': 0})

        # Loop through each record to calculate stats per sport
        for record in full_records:
            if len(record.sport.strip()) <= 1:
                continue

            sport = record.sport.upper()
            sport_data = total_sport[sport]

            result = record.result.lower()
            if result == 'loss':
                sport_data['loss'] += 1
            elif result == 'win':
                sport_data['win'] += 1

            if record.total_earn is not None and record.risk:
                try:
                    risk = float(record.risk) or 1
                    roi = float(record.total_earn) / risk
                    total_units = float(record.total_earn) / 100

                    sport_data['roi'] += round(roi, 2)
                    sport_data['total_units'] += round(total_units, 2)
                except ValueError:
                    continue

        # Final rounding after loop
        for sport_data in total_sport.values():
            sport_data['roi'] = round(sport_data['roi'], 2)
            sport_data['total_units'] = round(sport_data['total_units'], 2)

        # Session stats for today only
        today = datetime.today().date()
        session_records = full_records.filter(date=today)
        session_total_wins = sum(1 for r in session_records if r.result.lower() == 'win')
        session_total_losses = sum(1 for r in session_records if r.result.lower() == 'loss')
        session_total = session_total_wins + session_total_losses or 1

        session_stats = {
            'win_percentage': round((session_total_wins / session_total) * 100, 1),
            'loss_percentage': round((session_total_losses / session_total) * 100, 1)
        }

        # Global stats
        roi_values = [s['roi'] for s in total_sport.values() if s['roi'] != 0]
        global_stats = {
            'roi': round(sum(roi_values) / len(roi_values), 2) if roi_values else 0,
            'total_units': round(sum(s['total_units'] for s in total_sport.values()), 2),
            'total_wins': sum(s['win'] for s in total_sport.values()),
            'total_losses': sum(s['loss'] for s in total_sport.values())
        }

        # Get NFL and CFB units individually
        nfl_units = total_sport.get('NFL', {}).get('total_units', 0)
        cfb_units = total_sport.get('CFB', {}).get('total_units', 0)

        # Final context to pass to template
        context = {
            'products': products,
            'global_stats': global_stats,
            'session_stats': session_stats,
            'sport_breakdown': dict(total_sport),
            'nfl_units': nfl_units,
            'cfb_units': cfb_units,
        }

        return render(request, 'pricingPlays.html', context)

    except Exception as e:
        print("not good:", e)
        return HttpResponse("Something went wrong while loading pricing.")
    
def test(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'thankyou.html')




def registernews(request):
        # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)

    # Get query parameters from the URL
    plan_type = request.GET.get('type', '')
    plan_card = request.GET.get('plan', '')
    plan_price = request.GET.get('price', '')
    plan_groups = request.GET.get('group', '')

    context = {
        'products': products,
        'plan_type': plan_type,
        'plan_card': plan_card,
        'plan_price': plan_price,
        'plan_groups': plan_groups,

    }
    
    return render(request, 'registernews.html',context)


def terms(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'terms.html',{'products': products})
def paymentMethods(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)

    # Get query parameters from the URL
    plan_type = request.GET.get('type', '')
    plan_card = request.GET.get('plan', '')
    plan_price = request.GET.get('price', '')

    context = {
        'products': products,
        'plan_type': plan_type,
        'plan_card': plan_card,
        'plan_price': plan_price,
    }
    
    return render(request, 'paymentMethods.html',context)
def playspaymentMethods(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
        # Get query parameters from the URL
    plan_type = request.GET.get('type', '')
    plan_card = request.GET.get('card', '')
    plan_price = request.GET.get('price', '')

    context = {
        'products': products,
        'plan_type': plan_type,
        'plan_card': plan_card,
        'plan_price': plan_price,
    }
    
    return render(request, 'playspaymentMethods.html',context)
def merchpaymentMethods(request):
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)

    # Get query parameters from the URL
    name = request.GET.get('name', '')
    catagory = request.GET.get('catagory', '')
    price = request.GET.get('price', '')

    # Safely dump cart from session
    cart_data = request.session.get('cart', {})
    cart_json = json.dumps(cart_data)  # makes it valid JSON

    context = {
        'products': products,
        'name': name,
        'catagory': catagory,
        'price': price,
        'cart_json': cart_json,
    }

    return render(request, 'merchpaymentMethods.html', context)
def playsuser(request):
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
        # Get query parameters from the URL
    plan_type = request.GET.get('type', '')
    plan_card = request.GET.get('card', '')
    plan_price = request.GET.get('price', '')

    context = {
        'products': products,
        'plan_type': plan_type,
        'plan_card': plan_card,
        'plan_price': plan_price,
    }

    return render(request, 'registeruserforplays.html', context)


def blog(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'blog.html',{'products': products})

def privacy(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'privacy.html',{'products': products})



def refund(request):
    # products = Product.objects.all()
    products = Product.objects.annotate(num_variations=Count('variations')).filter(num_variations__gte=1)
    
    return render(request, 'refund.html',{'products': products})

@csrf_exempt
def delete_tweet(request):
    try:
        if request.method != "POST":
            return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

        # Get IDs of tweets to delete (after the first 5000)
        tweets_to_delete_ids = list(
            Tweet.objects.all().order_by('id')[5000:].values_list('id', flat=True)
        )

        # Delete those tweets
        deleted_count, _ = Tweet.objects.filter(id__in=tweets_to_delete_ids).delete()

        return JsonResponse({"success": True, "deleted": deleted_count})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def save_notification_sound(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        group_name = data.get('username')
        sound = data.get('sound')

        if not group_name or not sound:
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

        # Get or create the TweetConfigrations object
        group_obj, created = TweetConfigrations.objects.get_or_create(
            user_id=request.user,
            tweet_name=group_name,
            defaults={'notification_sound': sound}
        )

        # If it already existed, update the sound
        if not created:
            group_obj.notification_sound = sound
            group_obj.save()

        return JsonResponse({'status': 'ok', 'created': created})

    return JsonResponse({'status': 'unauthorized'}, status=403)


@csrf_exempt
def save_border_color(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        group_name = data.get('group_name')
        color = data.get('color', '#00AAEC')

        try:
            group_obj = TweetConfigrations.objects.get(user_id=request.user, tweet_name=group_name)
            group_obj.tweet_name = group_name
            group_obj.color = color
            group_obj.save()
            return JsonResponse({'status': 'ok'})
        except TweetConfigrations.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
        
    return JsonResponse({'status': 'unauthorized'}, status=403)
import json
from django.http import JsonResponse
from .models import TweetConfigrations

def save_border_color(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        group_name = data.get('group_name')
        color = data.get('color', '#00AAEC')

        # Get or create the TweetConfigrations object
        group_obj, created = TweetConfigrations.objects.get_or_create(
            user_id=request.user,
            tweet_name=group_name,
            defaults={'color': color}
        )

        # If it already existed, update the color
        if not created:
            group_obj.tweet_name = group_name
            group_obj.color = color
            group_obj.save()

        return JsonResponse({'status': 'ok', 'created': created})

    return JsonResponse({'status': 'unauthorized'}, status=403)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from appsrc.models import FilterRecord, UserModel  # Make sure the model paths are correct

@csrf_exempt
def update_group(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        group_value = data.get('group')

        if not group_value or group_value == "all":
            group_value = "all"
        try:
            user = UserModel.objects.get(id=user_id)
            print("getting user form usermode", user)
            filtergroup = FilterRecord.objects.update_or_create(
                user=user,
                defaults={'group': group_value}
            )
            print("data create or update in ", filtergroup)
            return JsonResponse({'status': 'success'})
        except UserModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=400)

    return JsonResponse({'status': 'invalid method'}, status=405)

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .serializers import BlogSerializer

def admin_blog_view(request):
    return render(request, 'admin/adminblog.html', {'blogs': blog})

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    return render(request, 'blogdetail.html', {'blog': blog})

@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
def blog_list_create(request):
    if request.method == 'GET':
        blogs = Blog.objects.all().order_by('-created_at')
        serializer = BlogSerializer(blogs, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BlogSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser])
def blog_update_delete(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == 'PUT':
        serializer = BlogSerializer(blog, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        blog.delete()
        return Response({'message': 'Deleted'}, status=204)
    
def load_latest_messages(request):
    messages = Message.objects.filter(is_free=True).order_by('-created_at')[:3]
    data = [{
        'title': msg.title,
        'body': msg.body,
    } for msg in messages]
    return JsonResponse({'messages': data})
def get_user_info(request, user_id):
    user = UserModel.objects.get(id=user_id)
    groups = list(user.groups.values_list('id', flat=True))
    return JsonResponse({
        'plan': user.plan,
        'plan_price': user.plan_price,
        'groups': groups,
    })

@csrf_exempt
def update_user(request):
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            subscription_plan = request.POST.grt('subscription-plan')
            plan = request.POST.get('plan')
            plan_price = request.POST.get('plan_price')
            groups = request.POST.getlist('editGroups')
            if plan == "custom":
                start_date = (datetime.now() - timedelta(days=8)).date()
                pkg_days = 0
            else:
                start_date = datetime.now().date()
                pkg_days = 7
            user = UserModel.objects.get(id=user_id)
            user.plan = plan
            user.package = subscription_plan
            user.plan_price = plan_price
            user.num_groups = groups
            user.start_date = start_date
            user.pkg_days = pkg_days
            user.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@login_required
def update_user_plan(request):
    user = request.user
    plan = request.GET.get('plan')
    plan_type = request.GET.get('type')  # 'monthly' or 'yearly'
    userinstance = UserModel.objects.get(username =user)
    # Define pricing and days (you can expand as needed)
    plan_config = {
        'basic': {'monthly': (60, 30), 'yearly': (576, 365)},     # 20% discount yearly
        'premium': {'monthly': (120, 30), 'yearly': (1152, 365)},
        'custom': {'monthly': (240, 30), 'yearly': (2304, 365)},
    }

    if plan not in plan_config or plan_type not in plan_config[plan]:
        return redirect('pricing')  # fallback if invalid

    price, days = plan_config[plan][plan_type]

    # Update UserModel fields
    userinstance.plan = plan
    userinstance.package = plan_type
    userinstance.plan_price = str(price)
    userinstance.start_date = datetime.now().date()
    userinstance.pkg_days = days
    userinstance.save()

    return redirect('registernews')  # or wherever you want to take them
def user_list_view(request):
    users = UserModel.objects.filter(user_type='FEEDMEUSER').order_by('-register_at')
    return render(request, 'admin/UserRecord.html', {'users': users})

@csrf_exempt
def update_all_bets_total_earn(request):
    updated = 0

    def update_model_records(queryset):
        nonlocal updated
        for bet in queryset:
            negative_value = None

            # Convert juice safely to float
            juice = None
            if bet.juice is not None:
                try:
                    juice = float(bet.juice)
                except (ValueError, TypeError):
                    juice = None

            # Convert risk safely to float
            risk = None
            if bet.risk is not None:
                try:
                    risk = float(bet.risk)
                except (ValueError, TypeError):
                    risk = None

            # Choose the negative value
            if juice is not None and juice < 0:
                negative_value = juice
            elif risk is not None and risk < 0:
                negative_value = risk

            # Apply logic based on result
            if negative_value is not None:
                if bet.result == 'loss':
                    bet.total_earn = -abs(negative_value)
                    bet.save()
                    updated += 1
                elif bet.result == 'win':
                    bet.total_earn = abs(negative_value)
                    bet.save()
                    updated += 1

    # Apply to both models
    update_model_records(SportsBet.objects.all())
    update_model_records(NewRecord.objects.all())

    return JsonResponse({'status': 'completed', 'updated_records': updated})

TEAM_MEMBERS = {
    "AliAshraf": {
        "name": "Ali Ashraf",
        "role": "Head of Technology As the Head of the Tech Team, I lead strategy, development, and execution across all technology initiatives. With a passion for building scalable solutions and empowering high-performing teams, I bridge the gap between vision and implementation. My focus is on leveraging emerging technologies to deliver value, streamline operations, and drive sustainable growth.",
    },
    "Lion": {
        "name": "Lion",
        "role": "Graduated from Ohio University in Sports Management. Previously a inplay trader for DonBest Sports & DraftKings. Manage daily trades & risk with the FeedMe team. Also, handle adding graphics/videos/news to social media with Tunes Twitter, FeedMeBet Instagram and searching for the news/info for the Telegram. Professionally contribute to the college football and NFL prep during the summer and week to week sheets for power numbers. Specialize in college football, NFL, college basketball & WNBA. Go Reds & Go Irish!",
    },
    "Dirk": {
        "name": "Dirk",
        "role": "Leads our in-house origination with a primary focus on college football. Builds and maintain quantitative models to derive edge against market lines. Maintains and develops internal dashboards, tools, and pipelines.",
    },
    "Zilla": {
        "name": "Zilla",
        "role": "Rayzilla handles various trading aspects at feedme.bet including hand betting and the operation of automation applications. He also specializes in hand trading props. Conducts day to day trading operations such as placing bets across multiple sportsbooks/exchanges, as well as optimizing market timing and staking",
    },
    "Mack": {
        "name": "Mack",
        "role": "Mack oversees all aspects of accounting, ensuring accurate financial reporting and compliance across operations. He plays a key role in onboarding new partners and accounts, helping establish seamless workflows and strong business relationships. Mack also manages payments and collections, maintaining healthy cash flow and resolving any issues with efficiency. Working closely with the #FeedMe team, he handles the day-to-day operational needs to keep everything running smoothly.",
    },
    "Spats": {
        "name": "Spats",
        "role": "In charge of Vegas office. Trades and bets in the grounds! Vice president to the vice president of New Jersey operations.",
    },
    "MapleSyrup": {
        "name": "Maple Syrup",
        "role": "Work on figures weekly Setting up accounts Entering accounting daily Solving any issues with partners Posting to social media News/Weather reports around the sports world Various other side tasks/data mining",
    },
    "BD": {
        "name": "BD",
        "role": "BD is the Head Trader for the FeedMe crew, where he leads the charge on building positions across all sports. He’s responsible for pricing opinions, managing risk, and finding edges—often ahead of market moves. Blending data, intuition, and a deep feel for how markets behave, BD works closely with the rest of the team to turn insights into profitable action. From overnight lines to live betting, he's at the center of fast, high-stakes decision-making where timing, precision, and risk control are everything.",
    },
    "Buc": {
        "name": "Buc",
        "role": "Helps with the daily trading and works with social media to grow reach and engagement",
    },
    "Jerms": {
        "name": "Jerms",
        "role": "Duties at Feedme office. Entail Daily accounting. Daily and weekly figures are to be ready ASAP to ensure any discrepancies and or issues are to be resolved in timely fashion. Another aspect is keeping on top of player accounts within computer software. Identifying any issues in software and resolving any error codes that may arise. Daily data entry for any plays that come in. Finally observing and studying UFC and line movements and finding best values on plays.",
    },
}

def team_detail(request, name):
    member = TEAM_MEMBERS.get(name)
    if not member:
        return render(request, '404.html')  # Or your custom not-found page

    return render(request, 'teaminfo.html', {
        'name': name,
        'member': member,
    })

@api_view(['DELETE'])
def delete_user(request, username):
    try:
        user = UserModel.objects.get(username=username)
        user.delete()
        return Response({"message": f"User '{username}' deleted successfully."}, status=status.HTTP_200_OK)
    except UserModel.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
def registerfortest(request):
    return render(request, 'Testingregister.html')  # Or whatever your template is
def feedme_menual_view(request):
    return render(request, 'feedmeuserguide.html', {'blogs': blog})
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json

from .models import Device, UserModel

@csrf_exempt
def save_fcm_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            email = data.get('email')

            if not token or not email:
                return JsonResponse({'error': 'Missing token or email'}, status=400)

            user = UserModel.objects.filter(email=email).first()
            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)

            # Create or update token
            device, created = Device.objects.get_or_create(token=token)
            device.user = user
            device.created_at = now()
            device.save()

            return JsonResponse({'message': 'Token saved successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST allowed'}, status=405)

@csrf_exempt
def approve_payment(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(UserModel, id=user_id)
        selected_type = request.POST.get("type")  # NewsFeed or Plays

        print(f"🔎 Approve Payment called for user {user.email}, type={selected_type}")
        print(f"🔎 User current payment_type={user.payment_type}, plays_payment_type={user.plays_payment_type}")

        # NEWSFEED PAYMENT
        if user.payment_type == "Venmo" and not user.payment_status and selected_type == "NewsFeed":
            print("✅ Entering NewsFeed payment block")

            user.payment_status = True
            if not user.user_password:
                random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                user.set_password(random_password)
                user.user_password = random_password
                try:
                    registration_email(
                        email=user.email,
                        subject="Feedme Registration",
                        template_name="./email_template.html",
                        context={'username': user.email, 'password': random_password}
                    )
                except Exception as e:
                    print(f"[Email Error] Registration email failed: {e}")
            else:
                try:
                    send_reg_mail(
                        email=[user.email],
                        subject="Feedme Payment Approved",
                        message=(
                            f"Hello {user.email},\n\n"
                            f"Your payment via Venmo has been approved.\n"
                            f"You can now access your NewsFeed at https://feedme.bet/.\n\n"
                            f"Thank you for subscribing to Feedme!"
                        )
                    )
                except Exception as e:
                    print(f"[Email Error] Confirmation email failed: {e}")

            user.save()
            print(f"✅ NewsFeed payment approved for {user.email}")
            messages.success(request, "NewsFeed payment approved and user notified.")

        # PLAYS PAYMENT
        elif user.plays_payment_type == "Venmo" and not user.plays_payment_status and selected_type == "Plays":
            print("✅ Entering Plays payment block")

            user.plays_payment_status = True
            user.plays_pkg_days = user.store_plays_pkg_days
            user.is_activate_playes = True
            if not user.plays_start_date:
                from datetime import date
                user.plays_start_date = date.today()

            print(f"🔎 Before Save: plays_pkg_days={user.plays_pkg_days}, status={user.plays_payment_status}")
            user.save()
            print(f"✅ After Save: plays_pkg_days={user.plays_pkg_days}, status={user.plays_payment_status}")

            if not user.user_password:
                random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                user.set_password(random_password)
                user.user_password = random_password
                user.save()
                try:
                    registration_email(
                        email=user.email,
                        subject="Feedme Registration",
                        template_name="./playsemail.html",
                        context={'username': user.email, 'password': random_password}
                    )
                except Exception as e:
                    print(f"[Email Error] Registration email failed: {e}")
            else:
                try:
                    send_reg_mail(
                        email=[user.email],
                        subject="Feedme Payment Approved",
                        message=(
                            f"Hello {user.email},\n\n"
                            f"Your payment via Venmo has been approved.\n"
                            f"You can now access your Plays at https://feedme.bet/.\n\n"
                            f"Thank you for subscribing to Feedme!"
                        )
                    )
                except Exception as e:
                    print(f"[Email Error] Confirmation email failed: {e}")

            messages.success(request, "Plays payment approved and user notified.")

        else:
            print("❌ No matching condition for this request")
            messages.error(request, "Invalid payment status or type.")

    return redirect(reverse('user_list'))



from django.shortcuts import render
from django import forms
from .models import Affiliate
class InlineAffiliateForm(forms.ModelForm):
    class Meta:
        model = Affiliate
        fields = ['name', 'email', 'phone', 'address', 'discount']
@login_required(login_url="loginPage")
def affiliate_page(request):
    form = InlineAffiliateForm()
    affiliates = Affiliate.objects.all()
    return render(request, 'admin/affiliate_register.html', {
        'form': form,
        'affiliates': affiliates
    })

@csrf_exempt
@login_required(login_url="loginPage")
def save_affiliate(request):
    if request.method == "POST":
        id = request.POST.get("id")
        if id:  # edit
            affiliate = get_object_or_404(Affiliate, id=id)
            form = InlineAffiliateForm(request.POST, instance=affiliate)
        else:  # new
            form = InlineAffiliateForm(request.POST)
        if form.is_valid():
            affiliate = form.save()
            return JsonResponse({'success': True, 'code': affiliate.code})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
from django.views.decorators.http import require_POST

@require_POST
@csrf_exempt
def delete_affiliate(request):
    from django.http import JsonResponse
    try:
        id = request.POST.get("id")
        Affiliate.objects.get(id=id).delete()
        return JsonResponse({'success': True})
    except Affiliate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Affiliate not found'})

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

@csrf_protect
@require_POST
def check_referral_code(request):
    try:
        data = json.loads(request.body)
        code = data.get("code", "").strip().upper()

        affiliate = Affiliate.objects.get(code__iexact=code)
        return JsonResponse({"valid": True, "discount": affiliate.discount})
    except Affiliate.DoesNotExist:
        return JsonResponse({"valid": False})
    except Exception as e:
        return JsonResponse({"valid": False, "error": str(e)})


@csrf_exempt
def clear_play_sound(request):
    if request.method == "POST":
        request.session.pop('play_sound', None)
        return JsonResponse({"status": "cleared"})


def get_new_messages(request):
    last_id = request.GET.get('last_id', 0)
    new_messages = Message.objects.filter(is_free=True, id__gt=last_id).order_by('created_at')
    
    messages_data = []
    for msg in new_messages:
        messages_data.append({
            'id': msg.id,
            'title': msg.title,
            'body': msg.body
        })
    
    return JsonResponse({'messages': messages_data})
from django.http import JsonResponse
from django.db.models import Q

def get_premium_messages(request):
    last_id = int(request.GET.get('last_id', 0))
    try:
        user_instance = UserModel.objects.get(username=request.user)
    except UserModel.DoesNotExist:
        return JsonResponse({'messages': []})

    plan = user_instance.plays_plan

    if plan == 'full_yearly':
        queryset = Message.objects.filter(
            Q(is_nfl=True) | Q(is_cfb=True)
        )
    elif plan == 'monthly':
        queryset = Message.objects.filter(is_monthly=True)
    elif plan == 'seasonal_nfl':
        queryset = Message.objects.filter(is_nfl=True)
    elif plan == 'seasonal_cfb':
        queryset = Message.objects.filter(is_cfb=True)
    elif plan == 'seasonal_both':
        queryset = Message.objects.filter(Q(is_nfl=True) | Q(is_cfb=True) | Q(is_nfl=True, is_cfb=True))
    else:
        queryset = Message.objects.none()

    if last_id == 0:
        messages = queryset.order_by('-created_at')[:10]
    else:
        messages = queryset.filter(id__gt=last_id).order_by('created_at')

    message_data = [{
        'id': msg.id,
        'title': msg.title,
        'body': msg.body
    } for msg in messages]

    return JsonResponse({'messages': message_data})


@login_required(login_url="loginPage")
def add_user_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "")
        last_name = request.POST.get("last_name", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")

        user = UserModel.objects.create_user(
            username=email.split('@')[0],
            email=email,
            name=name,
            last_name=last_name,
            user_password=password,
            user_type='FEEDMEUSER'
        )
        user.set_password(password)
        user.save()

        messages.success(request, "User created successfully.")
        return redirect('admin_subscriptions')  # update this to your actual list page name

    return redirect('admin_subscriptions')


@csrf_exempt
def create_crypto_sale(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            customer_email = data.get("customer_email")
            shipping_address = data.get("shipping_address")
            amount_paid = data.get("amount_paid")
            session_id = data.get("session_id")
            cart_items = data.get("cart_items", [])

            if not customer_email or not shipping_address:
                return JsonResponse({"error": "Email and Shipping Address are required"}, status=400)

            # Create Sale record
            sale = Sale.objects.create(
                customer_email=customer_email,
                shipping_address=shipping_address,
                session_id=session_id,
                amount_paid=amount_paid,
                status="Pending",
                payment_method="Crypto",
                payment_status=False
            )

            # Build email body with order details
            body = f"New Crypto Order received\n\nCustomer: {customer_email}\nAddress: {shipping_address}\n\nOrder Details:\n"
            for item in cart_items:
                product = item.get("product", {})
                product_name = product.get("full_name", "Unknown Product")

                SaleItem.objects.create(
                    sale=sale,
                    product_name=product_name,
                    size=item.get("size", "N/A"),
                    quantity=item.get("quantity", 1)
                )
                body += f"- {product_name} ({item.get('size','N/A')}) x {item.get('quantity',1)}\n"

            body += f"\nTotal Amount: ${amount_paid}"

            # --- Send admin email ---
            try:
                send_reg_mail(
                        email=["aliashrafmirza169@gmail.com", "saherriaz78@gmail.com"],
                        subject="New Crypto Order on Feedme.bet",
                        message=body
                    )
            except Exception as e:
                print(f"[Admin Email Error] {e}")

            # --- Send customer email ---
            try:
                customer_body = (
                    f"Hello,\n\n"
                    f"Thank you for your order!\n\n"
                    f"We received your request for the following products:\n\n"
                    f"{body}\n\n"
                    "Once your payment is confirmed, our admin will approve your product.\n"
                    "For support, please email support@feedme.bet\n\n"
                    "Regards,\nFeedme Team"
                )
                send_reg_mail(
                    email=[customer_email],
                    subject="Your Crypto Order on Feedme.bet",
                    message=customer_body
                )
            except Exception as e:
                print(f"[Customer Email Error] {e}")

            # Empty session cart
            request.session['cart'] = {}

            return JsonResponse({"success": True, "message": "Sale created successfully"})

        except Exception as e:
            print("[Crypto Sale Error]", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def crypto_initiate_view(request):
    amount = request.GET.get("price")
    email = unquote(request.GET.get("email", "").strip())
    name = unquote(request.GET.get("name", "").strip())
    plan_type = request.GET.get("type", "monthly").strip()
    plan_card = request.GET.get("card", "monthly").strip()
    groups = request.GET.get("group", "0").strip()

    if not email or not amount:
        return JsonResponse({"error": "Missing required data."}, status=400)

    try:
        amount = int(float(amount))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid amount format."}, status=400)

    existing_user = UserModel.objects.filter(email=email).first()
    if existing_user:
        # ✅ Update user record instead of creating
        existing_user.name = name or existing_user.name
        existing_user.package = plan_type
        existing_user.pkg_days = 30 if plan_type == 'monthly' else 365 if plan_type == 'yearly' else 0
        existing_user.num_groups = int(groups) if groups.isdigit() else existing_user.num_groups
        existing_user.plan = plan_card
        existing_user.plan_price = amount
        existing_user.payment_type = 'Crypto'
        existing_user.payment_status = False
        existing_user.start_date = datetime.now().date()
        existing_user.save()

        # Optional: log subscription update too
        SubscriptionRecords.objects.create(
            user_id=existing_user,
            amount=amount,
            session_id=f"crypto_{random.randint(100000, 999999)}",
            date_time=datetime.now()
        )

        return JsonResponse({
            "status": "Updated",
            "message": "This email was already registered. We’ve updated the subscription details.",
            "redirect": "/home3"
        })

    # ✅ Create new user
    userinstance = UserModel.objects.create(
        email=email,
        username=email,
        name=name,
        package=plan_type,
        pkg_days=30 if plan_type == 'monthly' else 365 if plan_type == 'yearly' else 0,
        num_groups=int(groups) if groups.isdigit() else 0,
        plan=plan_card,
        plan_price=amount,
        user_type='FEEDMEUSER',
        payment_type='Crypto',
        payment_status=False,
        start_date=datetime.now().date()
    )

    SubscriptionRecords.objects.create(
        user_id=userinstance,
        amount=amount,
        session_id=f"crypto_{random.randint(100000, 999999)}",
        date_time=datetime.now()
    )

    # Send email to user
    try:
        send_reg_mail(
            email=[email],
            subject="FeedMe: Subscription Initiated (Crypto)",
            message=(
                f"Hi {name},\n\n"
                f"Thank you for initiating your subscription to FeedMe.\n"
                f"Please send a crypto payment of ${amount:.2f} to the address provided.\n"
                f"After payment, send your transaction screenshot to support@feedme.bet.\n"
                f"Our team will confirm and share your account credentials.\n\n"
                f"Regards,\nFeedMe Team"
            )
        )
    except Exception as e:
        print(f"[User Email Error] {e}")

    # Notify admin
    try:
        send_reg_mail(
            email=['aliashrafmirza169@gmail.com', 'saherriaz78@gmail.com'],
            subject="FeedMe: Crypto Payment Initiated",
            message=(
                f"User {name} ({email}) has initiated a subscription via crypto.\n"
                f"Plan: {plan_card}, Type: {plan_type}, Groups: {groups}, Amount: ${amount}"
            )
        )
    except Exception as e:
        print(f"[Admin Email Error] {e}")

    return JsonResponse({"status": "Initiated", "email_sent": True})


@csrf_exempt
def approve_crypto_payment(request, user_id):
    if request.method not in ['GET', 'POST']:
        return JsonResponse({'error': 'Only GET or POST method allowed'}, status=405)

    user = get_object_or_404(UserModel, id=user_id)
    payment_type = request.GET.get("type") if request.method == "GET" else request.POST.get("type")
    payment_type = payment_type or "NewsFeed"

    # Make sure payment type is Crypto
    if user.payment_type != "Crypto" and user.plays_payment_type != "Crypto":
        return JsonResponse({'error': '❌ User did not pay with Crypto.'}, status=400)

    if payment_type == "NewsFeed" and not user.payment_status:
        user.payment_status = True
    elif payment_type == "Plays" and not user.plays_payment_status:
        user.plays_payment_status = True
    else:
        return JsonResponse({'error': '❌ Already approved or invalid type.'}, status=400)

    # Generate password if not set
    if not user.user_password:
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user.set_password(random_password)
        user.user_password = random_password

        # Choose email template based on payment_type
        template = "./email_template.html" if payment_type == "NewsFeed" else "./playsemail.html"

        try:
            registration_email(
                email=user.email,
                subject="Feedme Registration",
                template_name=template,
                context={'username': user.email, 'password': random_password}
            )
        except Exception as e:
            print(f"[Email Error] Failed to send registration email: {e}")
    else:
        try:
            send_reg_mail(
                email=[user.email],
                subject="Feedme Crypto Payment Approved",
                message=(
                    f"Hello {user.email},\n\n"
                    f"Your payment via Crypto has been approved for {payment_type}.\n"
                    f"You can now access your account at https://feedme.bet/.\n\n"
                    f"Thank you for subscribing to Feedme!"
                )
            )
        except Exception as e:
            print(f"[Email Error] Failed to send confirmation email: {e}")

    user.save()
    return JsonResponse({'success': f'✅ Crypto payment approved for {payment_type} and credentials sent.'})



def crypto_plays_initiate_view(request):
    email = request.GET.get("email", "").strip()
    name = request.GET.get("name", "").strip()
    plan_type = request.GET.get("type", "monthly").strip()
    plan_card = request.GET.get("card", "monthly").strip()
    amount = request.GET.get("price", "0").strip()
    code = request.GET.get('code', '').strip()

    if not email or not amount:
        return JsonResponse({"error": "Missing required data"}, status=400)

    try:
        amount = int(float(amount))
    except ValueError:
        return JsonResponse({"error": "Invalid amount format"}, status=400)

    # Get or create the user
    userinstance, created = UserModel.objects.get_or_create(
        email=email,
        defaults={"username": email, "name": name}
    )
    if not created:
        userinstance.plays_payment_status = False

    # Define plan durations
    pkg_days_map = {
        'monthly': 30,
        'full_yearly': 365,
        'seasonal_cfb': 149,
        'seasonal_nfl': 157,
        'seasonal_both': 170,
    }
    pkg_days = pkg_days_map.get(plan_card, 30)

    # Update user details
    userinstance.plays_package = plan_type
    userinstance.plays_plan = plan_card
    userinstance.plays_pkg_days = pkg_days
    userinstance.plays_price = amount
    userinstance.is_activate_playes = True
    userinstance.user_type = 'FEEDMEUSER'
    userinstance.plays_payment_type = 'Crypto' 
    userinstance.refferal_code = code
    userinstance.plays_start_date = timezone.now().date()
    userinstance.save()

    # Save in subscription records
    SubscriptionRecords.objects.create(
        user_id=userinstance,
        amount=amount,
        session_id=f"crypto_{random.randint(100000, 999999)}",
        date_time=datetime.now()
    )

    # Send email to user
    try:
        send_reg_mail(
            email=[email],
            subject="FeedMe: Subscription Initiated (Crypto)",
            message=(
                f"Hi {name},\n\n"
                f"Thank you for initiating your subscription to FeedMe.\n"
                f"Please send a crypto payment of ${amount:.2f} to the address provided.\n"
                f"After payment, send your transaction screenshot to support@feedme.bet.\n"
                f"Our team will confirm or share your account credentials if your are new.\n\n"
                f"Regards,\nFeedMe Team"
            )
        )
    except Exception as e:
        print(f"[User Email Error] {e}")

    # Notify admin
    try:
        admin_email = UserModel.objects.filter(is_superuser=True).values_list('email', flat=True).first()
        recipients = ['aliashrafmirza169@gmail.com', 'saherriaz78@gmail.com']
        if admin_email and admin_email not in recipients:
            recipients.insert(0, admin_email)

        send_reg_mail(
            email=recipients,
            subject="Plays Subscription via Crupto",
            message=f"{email} paid a Plays subscription fee via Crypto: ${amount}"
        )

    except Exception as e:
        print(f"[Admin Email Error] {e}")

    return JsonResponse({"status": "Initiated", "email_sent": True})

@csrf_exempt  # so you can test from Postman without CSRF token
@require_POST
def delete_message_by_title(request):
    try:
        data = json.loads(request.body)
        title = data.get('title')

        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)

        # Try to find the message
        message = Message.objects.filter(title=title).first()
        if not message:
            return JsonResponse({'error': 'Message not found'}, status=404)

        # Delete the message
        message.delete()
        return JsonResponse({'success': f'Message with title "{title}" deleted successfully'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)