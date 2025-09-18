from .models import CarouselImage, Message, AgentStatus, ChatSession, AgentStatus, AgentProfile
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CarouselImageForm, AgentRegisterForm
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import uuid
from django.db.models import Q
from django.db.models import Count


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.is_superuser:
                return redirect('superadmin')

            # agent check: does this user have an AgentProfile and which role
            if hasattr(user, 'agent_profile'):
                role = user.agent_profile.role
                # change redirects per role as needed
                if role == 'manager':
                    return redirect('manager_dashboard')   # create if needed
                return redirect('agent_dashboard')

            # normal client
            return redirect('carousel')  # existing client page

        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')




# 2. PUBLIC VIEW FOR CAROUSEL
def carousel_view(request):
    today = timezone.now().date()
    images = CarouselImage.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        image_type="banner"
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

def carousel_image_detail(request, image_id):
    # Yahan pk + image_type filter dono lagayenge
    image = get_object_or_404(CarouselImage, pk=image_id)
    
    return render(request, 'preview_terms.html', {'image': image})

def general_termscondition(request):
    return render(request, 'generalT&C.html')
def general_AboutUs(request):
    return render(request, 'AboutUs.html')
def promotion(request):
    return render(request, 'promotion.html')
def promotion1(request):
    return render(request, 'promotion1.html')
def promotionNFL(request):
    return render(request, 'promotionNFL.html')
def promotionRELOAD(request):
    return render(request, 'promotionRELOAD.html')
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
def post_3rdsection(request):
    images = CarouselImage.objects.filter(image_type="others").order_by('-created_at')
    return render(request, "3rdSection.html", {"images": images})

@csrf_exempt  # agar iframe/static me chalana ho
def chat_send(request):
    if request.method == "POST":
        session_id = request.POST.get("session_id") or str(uuid.uuid4())
        content = request.POST.get("content")

        # Save user message
        Message.objects.create(
            sender="user",
            content=content,
            session_id=session_id
        )

        # Dummy bot reply (aap chahe to AI/knowledge base se connect karna)
        reply = "Thanks! We'll get back to you soon."

        Message.objects.create(
            sender="bot",
            content=reply,
            session_id=session_id
        )

        return JsonResponse({
            "from": "Bot",
            "reply": reply
        })
    return JsonResponse({"error": "Invalid request"}, status=400)

def agent_register(request):
    if request.method == "POST":
        form = AgentRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")   # or redirect to agent_dashboard
    else:
        form = AgentRegisterForm()
    return render(request, "agent_register.html", {"form": form})

@login_required
@csrf_exempt
def agent_dashboard(request):
    # Get online status
    status, _ = AgentStatus.objects.get_or_create(agent__user=request.user)

    # Base queryset of chats excluding closed
    chats_qs = ChatSession.objects.filter(closed=False).annotate(
        total_messages=Count('message'),
        user_messages=Count('message', filter=Q(message__sender='user')),
        agent_messages=Count('message', filter=Q(message__sender='agent')),
    )

    # Active chats
    active_chats = chats_qs.filter(
        assigned_agent=request.user
    ).filter(
        Q(agent_messages__gte=1) | Q(agent_messages__gte=0, user_messages__gte=1)
    )

    # New chats
    new_chats = chats_qs.filter(
        Q(assigned_agent__isnull=True) | Q(assigned_agent=request.user) |
        Q(agent_messages=0, user_messages__gte=1)
    )

    # Total chats
    total_chats = active_chats.count() + new_chats.count()

    # Selected chat
    session_id = request.GET.get("chat")
    selected_chat = None
    if session_id:
        selected_chat = ChatSession.objects.filter(session_id=session_id).first()

    # 👉 If request is AJAX, return JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "status": {"is_online": status.is_online},
            "total_chats": total_chats,
            "active_chats": list(active_chats.values("session_id", "user_name")),
            "new_chats": list(new_chats.values("session_id", "user_name")),
        })

    # 👉 Otherwise render full page
    return render(request, "agent_dashboard.html", {
        "status": status,
        "active_chats": active_chats,
        "new_chats": new_chats,
        "total_chats": total_chats,
        "selected_chat": selected_chat,
    })


# ---------------- USER SIDE ----------------
@csrf_exempt
def send_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    session_id = request.POST.get("session_id") or str(uuid.uuid4())
    sender = request.POST.get("sender", "user")
    content = request.POST.get("content", "").strip()

    if not content:
        return JsonResponse({"error": "Empty message"}, status=400)

    # Get or create chat session
    chat, _ = ChatSession.objects.get_or_create(session_id=session_id)

    # Save user message
    msg = Message.objects.create(chat=chat, sender=sender, content=content)

    reply = None

    # Assign agent if none assigned
    if not chat.assigned_agent:
        online_agents = AgentStatus.objects.filter(is_online=True)
        if online_agents.exists():
            chat.assigned_agent = online_agents.first().agent.user
            chat.save()
        else:
            # Bot fallback
            keywords = {
                "price": "Our pricing details are available on the Pricing page.",
                "contact": "You can contact us via email support@example.com.",
                "refund": "Refunds are processed within 5-7 business days.",
            }
            reply = "Sorry, I don’t understand your question."
            for key, val in keywords.items():
                if key in content.lower():
                    reply = val
                    break
            Message.objects.create(chat=chat, sender="bot", content=reply)

    return JsonResponse({
        "status": "ok",
        "message": msg.content,
        "reply": reply,
        "session_id": chat.session_id,
    })


def get_messages(request, session_id):
    msgs = Message.objects.filter(chat__session_id=session_id).order_by("timestamp")
    data = [
        {"sender": m.sender, "content": m.content, "time": m.timestamp.strftime("%H:%M")}
        for m in msgs
    ]
    return JsonResponse(data, safe=False)


# ---------------- AGENT SIDE ----------------
@login_required
def agent_chat_view(request, session_id):
    chat = get_object_or_404(ChatSession, session_id=session_id)
    return render(request, "agent_chat.html", {"chat": chat})


@csrf_exempt
@login_required
def agent_send_message(request, session_id):
    if request.method == "POST":
        chat = get_object_or_404(ChatSession, session_id=session_id)
        content = request.POST.get("content")
        msg = Message.objects.create(chat=chat, sender="agent", content=content)
        return JsonResponse({"status": "ok", "message": msg.content})
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def agent_get_messages(request, session_id):
    chat = get_object_or_404(ChatSession, session_id=session_id)
    msgs = chat.message_set.order_by("timestamp")  # ← default reverse relation
    data = [
        {"sender": m.sender, "content": m.content, "time": m.timestamp.strftime("%H:%M")}
        for m in msgs
    ]
    return JsonResponse(data, safe=False)
@login_required
def close_chat(request, session_id):
    chat = get_object_or_404(ChatSession, session_id=session_id)
    
    # Only assigned agent can close
    if chat.assigned_agent == request.user:
        chat.closed = True
        chat.assigned_agent = None
        chat.save()
    
    return redirect('agent_dashboard')


# ✅ Get agent status
def agent_status(request):
    try:
        # Get all online agents
        online_agents = AgentStatus.objects.filter(agent__role="agent", is_online=True).select_related("agent__user")
        
        if online_agents.exists():
            names = [a.agent.user.username for a in online_agents]
            return JsonResponse({
                "names": names,
                "online": True,
                "typing": any(a.agent.is_typing for a in online_agents)
            })
        else:
            return JsonResponse({"names": [], "online": False, "typing": False})
    except Exception:
        return JsonResponse({"names": [], "online": False, "typing": False})



# ✅ Update online/offline (for agents)
@login_required
def set_online_status(request):
    if request.method == "POST":
        action = request.POST.get("action")
        agent = get_object_or_404(AgentProfile, user=request.user)
        status, _ = AgentStatus.objects.get_or_create(agent=agent)

        if action == "go_online":
            status.is_online = True
        elif action == "go_offline":
            status.is_online = False

        status.save()
        # redirect back to dashboard after update
        return redirect("agent_dashboard")

    return redirect("agent_dashboard")
# ✅ Update typing status (for agents)
@login_required
def set_typing_status(request):
    if request.method == "POST":
        typing = request.POST.get("typing") == "true"
        agent_profile = get_object_or_404(AgentProfile, user=request.user)
        agent_profile.is_typing = typing
        agent_profile.save()   # ✅ save profile

        return JsonResponse({"success": True, "typing": agent_profile.is_typing})

    return JsonResponse({"success": False})
def carousel_embed(request):
    images = CarouselImage.objects.all()
    return render(request, "carousel_embed.html", {"images": images})
