from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models

class AgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="agent_profile")
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_typing = models.BooleanField(default=False)
    department = models.CharField(max_length=100, blank=True, null=True)

    ROLE_CHOICES = [
        ("agent", "Agent"),
        ("manager", "Manager"),
        ("support", "Support"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="agent")

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class AgentStatus(models.Model):
    agent = models.OneToOneField(AgentProfile, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agent.user.username} - {'Online' if self.is_online else 'Offline'}"
class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    user_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.session_id} ({self.user_name or 'Guest'})"


class Message(models.Model):
    sender = models.CharField(max_length=50)  # "user", "agent", "bot"
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(ChatSession, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.sender}: {self.content[:20]}"

class CarouselImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('banner', 'Banner'),
        ('post', 'Post'),
        ('others', 'Others'),
    ]
    image = models.ImageField(upload_to='carousel/')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    terms = models.TextField(blank=True, null=True)
    image_type = models.CharField(
        max_length=10,
        choices=IMAGE_TYPE_CHOICES,
        default='banner'
    )

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


class FAQ(models.Model):
    question = models.CharField(max_length=255, unique=True)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question
