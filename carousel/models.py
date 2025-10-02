from django.db import models
from django.utils import timezone
from django.db import models
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timesince import timesince


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
from django.utils import timezone
from django.utils.timesince import timesince
from datetime import timedelta

class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=5, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    closed = models.BooleanField(default=False)
    time_spent = models.DurationField(default=timedelta(0))

    def update_time_spent(self):
        """Update time spent dynamically"""
        self.time_spent = timezone.now() - self.created_at
        self.save()
        return self.time_spent

    def human_time_spent(self):
        """Return human readable time spent"""
        return timesince(self.created_at)

    @property
    def location(self):
        """Show country + state nicely"""
        if self.country and self.state:
            return f"{self.state}, {self.country}"
        elif self.country:
            return self.country
        return "Unknown"

    def __str__(self):
        return f"Session {self.session_id} ({self.country or 'Unknown'})"



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
