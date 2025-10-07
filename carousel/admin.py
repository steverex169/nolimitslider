# Register your models here.
from django.contrib import admin
from .models import CarouselImage, ChatSession, Message, AgentStatus, AgentProfile, FAQ

admin.site.register(CarouselImage)
admin.site.register(ChatSession)
admin.site.register(Message)
admin.site.register(AgentStatus)
admin.site.register(FAQ)

@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "get_is_active")
    search_fields = ("user__username", "user__email")

    def get_is_active(self, obj):
        return obj.user.is_active  # check the related User
    get_is_active.short_description = "Active"
    get_is_active.boolean = True  # shows green tick/red cross