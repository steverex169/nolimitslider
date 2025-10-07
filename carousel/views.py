from .models import CarouselImage, Message, AgentStatus, ChatSession, AgentStatus, AgentProfile, FAQ
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CarouselImageForm, AgentRegisterForm, FAQForm
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.gis.geoip2 import GeoIP2
from django.db.models import Exists, OuterRef
import uuid
import os
from django.db.models import Q
from django.db.models import Count
from django.contrib import messages
import difflib
from datetime import datetime
from django.views.decorators.http import require_http_methods


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

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from datetime import date, timedelta

@login_required
@csrf_exempt
def agent_dashboard(request):
    agent_profile = getattr(request.user, "agent_profile", None)
    if not agent_profile:
        agent_profile = AgentProfile.objects.create(user=request.user)

    status, _ = AgentStatus.objects.get_or_create(agent=agent_profile)

    # All open chat sessions
    chats_qs = ChatSession.objects.filter(closed=False)

    # Ongoing chats (all not closed sessions)
    ongoing_chats = chats_qs.count()

    # Logged in agents
    logged_agents = AgentStatus.objects.filter(is_online=True).count()
    total_agents = AgentStatus.objects.count()

    # Last 7 days chat counts
    today = date.today()
    last_7_days = [today - timedelta(days=i) for i in reversed(range(7))]

    chat_counts = []
    for d in last_7_days:
        count = chats_qs.filter(created_at__date=d).count()
        chat_counts.append(count)

    # Annotated chats
    chats_qs = chats_qs.annotate(
        total_messages=Count('message'),
        user_messages=Count('message', filter=Q(message__sender='user')),
        agent_messages=Count('message', filter=Q(message__sender='agent')),
    )

    # Active chats: agent sent at least 1 message
    active_chats = chats_qs.filter(
        assigned_agent=request.user,
        agent_messages__gte=1
    )

    
    # Customers online (users with active sessions)
    customers_online = active_chats.count()

    # New chats: no agent msg yet but user msg exists
    new_chats = chats_qs.filter(
        Q(assigned_agent__isnull=True) |
        Q(agent_messages=0, user_messages__gte=1)
    )

    total_chats = active_chats.count() + new_chats.count()

    # Optional: selected chat
    session_id = request.GET.get("chat")
    selected_chat = ChatSession.objects.filter(session_id=session_id).first() if session_id else None
    now = datetime.now().hour
    if now < 12:
        greeting = "Good Morning"
    elif 12 <= now < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    # Ajax request → return JSON only
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "status": {"is_online": status.is_online},
            "total_chats": total_chats,
            "active_chats": list(active_chats.values("session_id", "user_name")),
            "new_chats": list(new_chats.values("session_id", "user_name")),
            "chat_counts": chat_counts,
            "customers_online": customers_online,
            "ongoing_chats": ongoing_chats,
            "logged_agents": logged_agents,
            "total_agents": total_agents,
            "greeting": greeting,
        })

    # Normal render → pass to template
    return render(request, "agent/agent_dashboard.html", {
        "status": status,
        "active_chats": active_chats,
        "new_chats": new_chats,
        "total_chats": total_chats,
        "selected_chat": selected_chat,
        "chat_counts": chat_counts,
        "last_7_days_labels": [d.strftime("%a") for d in last_7_days],  # Mon..Sun
        "customers_online": customers_online,
        "ongoing_chats": ongoing_chats,
        "logged_agents": logged_agents,
        "total_agents": total_agents,
        "greeting": greeting,
    })




# ---------------- USER SIDE ----------------
FAQ_DATA = {
    "welcome_message": "Welcome to No Limit Bet! Our FAQs are here to guide you through every step of your gaming journey, whether you’re new to our platform or a seasoned player. Let’s dive into answers for your most common questions, organized by category for easy navigation. If you need extra help, our support team is ready to assist from 9am to 11pm (EST) via live chat or at support@nolimitbet.ag.",

    # General
    "How Do I Contact Customer Support?": "We’re here to help you whenever you need us! Our dedicated Customer Support team is available 7 days a week from 9am to 11pm (EST). Here’s how to reach us:\n\nLive Chat: If you’re logged into your account, look for the “Start Chat” button in the bottom right corner of the screen. Click it to connect with an agent instantly.\nEmail: Send us a message at support@nolimitbet.ag, and we’ll get back to you as quickly as possible.\nTip: Have your account details or a screenshot of any issue ready to help us resolve your query faster!",

    "How Do I Join No Limit Bet?": "Getting started with No Limit Bet is simple and fun! To create your account:\nClick the “REGISTER” button on our homepage.\nFill in a few basic details, like your name, email, and a secure password.\nConfirm you’re at least 18 years old and agree to our Terms & Conditions.\nSubmit your registration, and you’re ready to start your adventure!\nIf you run into any issues, reach out to us at support@nolimitbet.ag, and we’ll guide you through the process.",

    "Which Countries Are Eligible to Play?": "We welcome players from around the globe, including countries like Canada, Finland, India, New Zealand, South Africa, and many more! If you’re unsure whether your country is eligible, contact our support team, and we’ll confirm for you.",

    "Do New Players Receive a Welcome Offer?": "Absolutely! We love giving new players a warm welcome with exclusive Casino and Sports Welcome Bonuses. When you make your first deposit:\nChoose between our Casino or Sports Welcome Bonus.\nFollow the instructions in the “Cashier” section to claim your offer.\nStart playing with a boosted balance to kick off your No Limit Bet journey!\nCheck the “Promotions” page for details on each offer to pick the one that’s right for you.",

    "What Does GMT Mean?": "Our platform uses GMT (Greenwich Mean Time), also known as UTC (Coordinated Universal Time), for promotions and Responsible Gaming settings. This ensures consistency worldwide. To see how GMT aligns with your local time, try this World Clock (https://www.timeanddate.com/worldclock/). If you’re ever confused about timing, our support team can clarify!",

    "Where Can I Find Your Terms & Conditions?": "Our General Terms and Conditions are easy to find at the bottom of our website. They cover everything you need to know about playing with us. Note that the English version is the official one, and it takes precedence over any translations. For Sports betting, our General Terms supersede the Sports Terms & Betting Rules.",

    "Can I Find Specific Game Information?": "Every casino and live casino game has an in-game “Info” or “Help” button with details on how to play. Before trying a new game, click this button to learn the rules and features. It’s a great way to feel confident before you start!",

    "Can I Play in Practice Mode?": "Yes, you can try most Casino games in demo mode for free! Here’s how:\nSelect a Casino game (note: Live Casino games don’t offer demo mode).\nChoose “Practice Mode” to play with virtual credits.\nEnjoy the game without using real money. If your credits run low, just reload the game for more!\nThis is a perfect way to test games and build confidence before playing for real.",

    "Can I Bet If I’m Under 18?": "No, you must be at least 18 years old to use No Limit Bet. This is a strict rule to ensure a safe and responsible gaming environment. If you’re under 18, our platform and services are not available to you.",

    # Account
    "Why Can’t I Create a New Account?": "If you’re having trouble signing up, don’t worry—we’ll help you figure it out! Here are some common reasons:\nYou might already have an account with the email or details you’re using.\nThere could be a technical issue, like an incorrect format for your details.\nTry these steps:\nDouble-check that your email and password meet our requirements (e.g., no typos, valid email).\nIf you suspect an existing account, try logging in or resetting your password.\nIf the issue persists, email us at support@nolimitbet.ag with details or screenshots of the problem.\nOur team will respond quickly to get you started!",

    "I Can’t Log In. Can Someone Help?": "Logging in should be smooth, but if you’re stuck, let’s troubleshoot:\nCheck Your Details: Ensure your username and password are correct (they’re case-sensitive).\nReset If Needed: If you’ve forgotten your details, click “Forgot Password” on the login page or email support@nolimitbet.ag.\nContact Us: If you’re still unable to log in, use live chat or email us with details of the issue.\nWe’re here to get you back into your account as soon as possible!",

    "Can I Open Multiple Accounts?": "No, each player is allowed only one No Limit Bet account. If you’re unable to register, it might be because your email or details are already in our system. Try logging in instead. If you think someone else has used your details, contact us immediately at support@nolimitbet.ag to secure your information.",

    "Can I Change My Password and Username?": "Changing your password is easy:\nEmail support@nolimitbet.ag or use live chat to request a password reset.\nFollow the instructions we send to update your password securely.\nUsernames, however, cannot be changed for security reasons. If you have concerns about your account, reach out to our support team for assistance.",

    "My Account Has Been Closed—Can I Reopen It?": "If your account was closed, it depends on why:\nVoluntary Closure (Not Gambling-Related): You may be able to reopen it by contacting support@nolimitbet.ag.\nClosed Due to Problem Gambling: For your safety, we cannot reopen accounts closed for excessive gambling.\nEmail us with your account details, and we’ll guide you through the next steps.",

    # Responsible Gaming
    "How Do I Close My Account?": "If you’re considering closing your account, we’re here to support you. Here’s how:\nContact our support team via live chat or email at support@nolimitbet.ag.\nShare your reasons for closing—we value your feedback to improve.\nChoose between a temporary “Time Out” (short break), a Self-Exclusion period (6 months to 5 years), or permanent closure.\nOur team will process your request promptly and confirm once it’s complete.",

    "Can I Reopen My Account?": "Reopening depends on why your account was closed:\nPermanent Closure or Gambling Concerns: Accounts closed for these reasons cannot be reopened to ensure player safety.\nSelf-Exclusion: You must wait until the exclusion period ends before requesting to reopen.\nOther Closures: Email support@nolimitbet.ag to discuss reopening.\nContact us only when your exclusion period is over, as we cannot manually reopen active exclusions.",

    "Can I Withdraw Funds While Self-Excluded?": "During self-exclusion, your funds stay safe in your account, but you may need to verify your identity to withdraw. For a “Time Out” period, your balance remains accessible. To withdraw during a Time Out:\nEmail support@nolimitbet.ag with your request.\nOur Payments team will guide you through the process.\nWe’re committed to handling your funds securely and responsibly.",

    "Can I Keep Track of My Profit and Loss?": "Yes, you can easily monitor your spending:\nGo to “Balance” > “Transactions” in your account.\nSelect a time period from the drop-down menu.\nClick “Show” to see a summary of your deposits and withdrawals.\nThis helps you stay in control of your gaming budget. If you need help interpreting the data, reach out to our support team!",

    # Deposits
    "Which Deposit Methods Does No Limit Bet Accept?": "We currently accept cryptocurrency deposits for fast and secure transactions. To see your options:\nGo to the “Cashier” tab in your account.\nClick “Deposit” to view all available crypto payment methods.\nIf you’re new to crypto, don’t worry—our support team can guide you!",

    "Do You Have a Minimum Deposit Amount?": "Yes, each crypto payment method has a minimum and maximum deposit limit. To check:\nVisit Cashier > Deposit.\nSelect your preferred method to see the specific limits.\nLimits vary by method, so choose the one that works best for you.",

    "Where Can I See All My Previous Deposits?": "Your deposit history is always available:\nNavigate to “Balance” > “Transactions” in your account.\nChoose a time period from the drop-down menu.\nClick “Show” to view a summary of all your deposits.\nIf you have questions about a specific deposit, contact us with the details.",

    "Why Hasn’t My Deposit Been Credited?": "If your deposit hasn’t appeared, let’s troubleshoot:\nRefresh your account page to check your balance.\nIf it’s still missing, gather these details:\nDeposit method and amount.\nApproximate time of the deposit.\nWhether funds were deducted from your wallet.\nA screenshot, if possible.\nContact support@nolimitbet.ag with this information.\nOur team will investigate and resolve the issue quickly.",

    "Deposit Still ‘Pending’ But Funds Taken From My Wallet. Why?": "Sometimes, crypto transactions require extra security checks, causing a delay. Be patient, as most deposits are processed within hours. If it’s been over 7 days without confirmation, the deposit will be declined, and funds will return to your wallet. Contact us if you need assistance.",

    "Can I Deposit via a Third-Party Account?": "No, for your safety and to comply with regulations, deposits must come from a payment method in your name. Using someone else’s wallet is not allowed. If you’re unsure, reach out to our support team for guidance.",

    "How Do Cryptocurrency Deposits Work?": "Depositing with crypto is straightforward:\nGo to Cashier > Deposit.\nSelect your preferred crypto payment method.\nEnter the amount you want to deposit and click “Continue Deposit.”\nCopy the provided wallet address and send the funds from your crypto wallet.\nIf you’re new to crypto, our support team can walk you through the process!",

    "What Are the Fees for Deposits/Withdrawals?": "No Limit Bet doesn’t charge fees for deposits or withdrawals, but your crypto provider might. Check with your wallet provider for any transaction fees before depositing or withdrawing.",

    "Where Can I View Your Deposit Policy?": "Our full deposit policy is in the General Terms and Conditions, under “Section 3. Deposits and Withdrawals,” accessible at the bottom of our website.",

    # Withdrawals
    "How Do I Make a Withdrawal?": "Withdrawing your winnings is quick and easy! Follow these steps:\nLog into your No Limit Bet account.\nGo to “CASHIER” and click “Withdraw.”\nSelect your preferred cryptocurrency method (must be in your name).\nEnter the withdrawal amount and your wallet address carefully.\nClick “Withdraw” to submit your request.\nOur Payments team processes withdrawals within 48 hours (often faster), and crypto withdrawals typically arrive in your wallet within 10 minutes. You’ll get a confirmation email once approved. First time? We may need verification documents, but it’s usually a one-time step.",

    "How Long Do Withdrawals Take?": "Our team works hard to process withdrawals quickly, usually within 48 hours. Once approved, crypto withdrawals typically reach your wallet within 10 minutes. If it’s taking longer, check the “Payments” section of your account or contact support@nolimitbet.ag.",

    "Will I Be Informed My Withdrawal Is Successful?": "Yes! Once our Payments team approves your withdrawal, you’ll receive a confirmation email to your registered email address. Check your spam folder if you don’t see it.",

    "Can I Cancel My Withdrawal?": "If the withdrawal hasn’t been processed yet:\nGo to Cashier > Withdrawals.\nSelect “Cancel Withdrawal Request” to return funds to your balance.\nOnce the status changes to “Processing,” cancellation isn’t possible. Contact us if you need help.",

    "My Withdrawal Was Cancelled, Why?": "If your withdrawal was cancelled, we’ll send an email explaining why. Common reasons include:\nYour deposit hasn’t been wagered fully (see our rollover requirements).\nThe withdrawal method doesn’t match your deposit method.\nAccount verification is needed.\nThe withdrawal was requested to a third-party wallet.\nFollow the email’s instructions or contact support@nolimitbet.ag to resolve the issue.",

    "Why Is My Withdrawal Taking Too Long?": "Check the status in the “Payments” section of your account. If approved, allow up to 10 minutes for crypto withdrawals. If it’s delayed, email support@nolimitbet.ag with a screenshot of your wallet or bank statement to help us investigate.",

    "Do I Need to Send Documents for Each Withdrawal?": "Usually, you only need to verify your account once. However, we may request additional documents if you change payment methods or deposit significantly more. Our support team will guide you if needed.",

    "Can I Withdraw My Bonus?": "Bonuses can’t be withdrawn until you meet the wagering requirements. Check the “Bonuses” section of your account for details on your progress. If you have questions, contact support.",

    "Can I Withdraw My Money Without Bets?": "Each deposit has a 2x rollover requirement. This means you must bet an amount equal to twice your deposit before withdrawing. Check your wagering progress in the “Bonuses” section or contact support for clarification.",

    "Where Can I View Your Withdrawal Policy?": "Our full withdrawal policy is in the General Terms and Conditions, accessible at the bottom of our website.",

    # Sport
    "How Can I Place a Bet?": "Placing a bet is exciting and simple! For Sports bets:\nLog into your No Limit Bet account.\nBrowse the Sports section and click the odds for your desired outcome.\nEnter your bet amount in the bet slip.\nClick “Place Bet” to confirm.\nFor Casino or Live Casino bets:\nLog in and select a game or table.\nChoose your bet amount.\nClick “Spin” or “Place Bet” to play.\nDouble-check your selections before confirming, as bets cannot be cancelled.",

    "Can I Cancel a Bet?": "Once a bet is placed, it cannot be cancelled, even if the event hasn’t started. Our support team cannot manually refund bets, so please review your stake and selections carefully before clicking “Place Bet.”",

    "Can I Use Bet Builder?": "We don’t currently offer a Bet Builder option, but you can explore a wide range of betting markets in our Sports section. If you have ideas for new features, let us know at support@nolimitbet.ag!",

    "Why Hasn’t My Bet Been Settled?": "Most bets are settled shortly after the event ends, but some may take up to 30 minutes due to external operator confirmation. If it’s been longer, contact support@nolimitbet.ag with your Bet I.D. (found in “My Bets” > “View All My Bets”).",

    "I Need to Dispute an Existing Bet": "If you have concerns about a bet:\nFind the Bet I.D. in “My Bets” > “View All My Bets.”\nContact support@nolimitbet.ag, quoting the Bet I.D. and explaining the issue.\nWe’ll investigate and resolve your query as quickly as possible.",

    "Do You Have Betting Limits?": "Yes, the minimum bet is $1 (or equivalent in your currency) for any event, including system bets. Maximum bets vary by sport, event, and bet type. If you enter a stake above the maximum, the bet slip will notify you and adjust it. To place a higher bet, contact support@nolimitbet.ag, and we’ll pass your request to our traders.",

    # Bonuses
    "Do You Have a Bonus Policy?": "Our full bonus terms and conditions are available on the “Promotions” page. They outline everything you need to know about claiming and using bonuses.",

    "How Do I Claim a Bonus?": "Claiming a bonus is easy:\nMake a successful deposit in the “Cashier” section.\nSelect your preferred payment method and enter the bonus code (if required).\nClick “Continue Deposit” to activate your bonus instantly.\nCheck the “Promotions” page for specific offer details and codes.",

    "Why Was a Bonus Added When I Didn’t Opt-In?": "Some bonuses, like deposit boosts or free spins, are automatically applied during active promotions. If you don’t want a bonus:\nAvoid wagering until you contact support.\nEmail support@nolimitbet.ag to cancel the bonus.\nYou can opt back in anytime by letting us know!",

    "Why Did I Not Receive My Bonus?": "If you didn’t get a bonus, check:\nDid you meet the offer conditions (e.g., minimum deposit, minimum odds)?\nHas the promotion expired? All offers run on GMT/UTC time (see this World Clock: https://www.timeanddate.com/worldclock/).\nDo you have a pending withdrawal? This may make you ineligible.\nIf you’re still unsure, contact support@nolimitbet.ag with details of the offer.",

    "How Much Do I Need to Wager?": "Each bonus has specific wagering requirements, listed in the bonus terms on the “Promotions” page. Check the “Bonuses” section of your account to track your progress.",

    "How Much Rollover Do I Have Left Before I Can Withdraw My Winnings?": "Visit the “Bonuses” section of your account to see your remaining wagering requirements. If you need clarification, email support@nolimitbet.ag, and we’ll walk you through it.",

    "My Bonuses Keep Expiring, Why?": "Bonuses have a validity period (listed in the terms) and must be used before expiration. After the expiry date, bonuses are removed automatically. Check your active promotions regularly to avoid missing out.",

    # Security
    "How Do I Know My Account Is Safe?": "Your security is our priority. We use advanced encryption, secure servers, and strict account verification processes to keep your data and funds safe. Never share your login credentials with anyone.",

    "I Forgot My Password": "Click “Forgot Password” on the login page or email support@nolimitbet.ag. Follow the instructions to reset your password securely.",

    "How Do I Enable Two-Factor Authentication (2FA)?": "We currently do not offer 2FA, but your account is protected with encryption and secure login protocols. Always use a strong, unique password.",

    "What Should I Do If I Suspect Fraud?": "If you notice suspicious activity, immediately contact support@nolimitbet.ag. Our team will investigate and take action to secure your account.",

    # Technical Support
    "How Do I Send a Screenshot?": "To help our support team, attach screenshots showing the issue:\nTake a screenshot on your device.\nAttach it in an email to support@nolimitbet.ag or upload via live chat.\nInclude relevant details like account ID, time of issue, and error messages for faster resolution.",

    "What Does an Error In-Game Mean?": "In-game errors can occur due to network issues, server updates, or temporary glitches. Usually, they resolve after a refresh or a brief wait. If persistent, capture a screenshot and contact support.",

    "How Does a Lost Connection Affect My Game?": "If you lose connection during gameplay:\nCasino games usually resume from your last state or return funds for unplaced bets.\nSports bets remain confirmed once placed.\nFor live games, temporary disconnections may end the session, but we ensure fairness. Always check your account balance afterward.",

    "How Do I Speed Up the Website?": "For optimal performance:\nUse the latest browser version.\nClear cache and cookies regularly.\nClose unnecessary tabs or applications.\nCheck your internet speed; a stable connection of 5 Mbps+ is recommended.\nDisable VPN or firewall restrictions if issues persist.\nIf the site is still slow, contact support@nolimitbet.ag with your browser details.",
}


import os
import uuid
import geoip2.database
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

GEOIP_DB_PATH = r"C:\Users\Lenovo\Documents\nolimit\nolimitslider\geoip\GeoLite2-City.mmdb"


@csrf_exempt
def send_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    session_id = request.POST.get("session_id") or str(uuid.uuid4())
    sender = request.POST.get("sender", "user")
    content = request.POST.get("content", "").strip()

    if not content:
        return JsonResponse({"error": "Empty message"}, status=400)

    # Get client IP
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0] or request.META.get("REMOTE_ADDR")
    if ip == "127.0.0.1":
        ip = "103.198.154.240"  # test IP

    # GeoIP lookup
    country, state, country_code = "Unknown", "Unknown", ""
    try:
        reader = geoip2.database.Reader(GEOIP_DB_PATH)
        response = reader.city(ip)
        country = response.country.name or "Unknown"
        state = response.subdivisions.most_specific.name or "Unknown"
        country_code = response.country.iso_code or ""   # ✅ added
        reader.close()
    except Exception:
        pass

    # Get or create chat session
    chat, created = ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={
            "country": country,
            "country_code": country_code,
            "state": state
        }
    )

    # Optional update
    if not chat.country or not chat.state or not chat.country_code:
        chat.country = chat.country or country
        chat.country_code = chat.country_code or country_code
        chat.state = chat.state or state
        chat.save()

    # Save user message
    msg = Message.objects.create(chat=chat, sender=sender, content=content)

    reply = None

    # Assign agent if none
    if not chat.assigned_agent:
        online_agents = AgentStatus.objects.filter(is_online=True)
        if online_agents.exists():
            chat.assigned_agent = online_agents.first().agent.user
            chat.save()
        else:
            try:
                faq = FAQ.objects.filter(question__icontains=content).first()
                reply = faq.answer
            except FAQ.DoesNotExist:
                reply = "Sorry, I don’t have an answer. Contact support."
            Message.objects.create(chat=chat, sender="bot", content=reply)

    # ✅ update time spent
    chat.update_time_spent()

    return JsonResponse({
        "status": "ok",
        "message": msg.content,
        "reply": reply,
        "session_id": chat.session_id,
        "ip": ip,
        "country": chat.country,
        "country_code": chat.country_code,   # ✅ new field in response
        "state": chat.state,
        "time_spent": str(chat.time_spent)
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
    # Current session
    chat = get_object_or_404(ChatSession, session_id=session_id)

    # All sessions assigned to this agent
    my_chats = ChatSession.objects.filter(assigned_agent=request.user).order_by("-created_at")
    agent = AgentProfile.objects.get(user=request.user)
    status, _ = AgentStatus.objects.get_or_create(agent=agent)


    return render(
        request,
        "agent/agent_chat.html",
        {
            "chat": chat,
            "my_chats": my_chats,
            "status": status,
        }
    )

@login_required
def agent_chats(request):
    session_type = request.GET.get("type")  
    chats_qs = ChatSession.objects.filter(closed=False).order_by('-created_at')

    # All + New + Active
    all_chats = chats_qs
    active_chats = chats_qs.filter(assigned_agent=request.user)
    new_chats = chats_qs.filter(assigned_agent__isnull=True)

    # --- Custom filters ---
    # Chatting = assigned to this agent
    chatting_chats = active_chats  

    # Supervised = chats where this user has at least 1 reply
    supervised_chats = chats_qs.annotate(
        has_reply=Exists(
            Message.objects.filter(chat=OuterRef("pk"), sender=request.user)
        )
    ).filter(has_reply=True)

    # Waiting = only bot replied (no agent replies)
    waiting_chats = chats_qs.filter(assigned_agent__isnull=True)

    # Selection logic
    if session_type == "new":
        selected_chats = new_chats
    elif session_type == "active":
        selected_chats = active_chats
    elif session_type == "chatting":
        selected_chats = chatting_chats
    elif session_type == "supervised":
        selected_chats = supervised_chats
    elif session_type == "waiting":
        selected_chats = waiting_chats
    else:
        selected_chats = all_chats

    agent = AgentProfile.objects.get(user=request.user)
    status, _ = AgentStatus.objects.get_or_create(agent=agent)


    return render(request, "agent/agent_chats.html", {
        "session_type": session_type,
        "all_chats": all_chats,
        "active_chats": active_chats,
        "new_chats": new_chats,
        "chatting_chats": chatting_chats,
        "supervised_chats": supervised_chats,
        "waiting_chats": waiting_chats,
        "selected_chats": selected_chats,
        "status": status,
    })

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
    msgs = chat.message_set.order_by("timestamp")
    data = [
        {
            "sender": m.sender,
            "content": m.content,
            "time": m.timestamp.strftime("%Y-%m-%d %H:%M")  # full date + time
        }
        for m in msgs
    ]
    return JsonResponse(data, safe=False)

@login_required
def agent_chat_detail(request, session_id):
    chat = get_object_or_404(ChatSession, session_id=session_id)

    # Reuse same queryset logic
    chats_qs = ChatSession.objects.filter(closed=False).order_by('-created_at')
    active_chats = chats_qs.filter(assigned_agent=request.user)

    return render(request, "agent/agent_chat.html", {
        "chat": chat,
        "active_chats": active_chats,
    })


@login_required
def close_chat(request, session_id):
    chat = get_object_or_404(ChatSession, session_id=session_id)
    print("Deleting chat with session:", session_id)

    if request.method == "POST":
        # Guest ya koi bhi session (even "guest") delete ho jaye
        if not chat.assigned_agent or chat.assigned_agent == request.user or session_id == "guest":
            chat.delete()  # Messages bhi cascade se delete ho jayenge
            messages.success(request, f"Chat {session_id} closed and deleted successfully.")
        else:
            messages.error(request, "You are not allowed to close this chat.")

    return redirect("agent_chats")



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
@require_http_methods(["GET", "POST"])
def set_online_status(request):
    agent = get_object_or_404(AgentProfile, user=request.user)
    status, _ = AgentStatus.objects.get_or_create(agent=agent)

    action = request.POST.get("action") if request.method == "POST" else request.GET.get("action")

    if action == "go_online":
        status.is_online = True
    elif action == "go_offline":
        status.is_online = False

    status.save()

    return JsonResponse({
        "success": True,
        "is_online": status.is_online
    })
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
def faq_dashboard(request):
    faqs = FAQ.objects.all().order_by('-created_at')
    agent = AgentProfile.objects.get(user=request.user)
    status, _ = AgentStatus.objects.get_or_create(agent=agent)

    return render(request, "agent/faq_content.html", {"faqs": faqs, "status": status})

@csrf_exempt
def add_faq(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        if question and answer:
            faq = FAQ.objects.create(question=question, answer=answer)
            return JsonResponse({
                'success': True,
                'faq': {
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer
                }
            })
        return JsonResponse({'success': False, 'error': 'Both fields are required.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def delete_faq(request, faq_id):
    FAQ.objects.filter(id=faq_id).delete()
    return redirect('faq_dashboard')