from django import forms
from .models import CarouselImage, AgentProfile
from django.contrib.auth.models import User


class CarouselImageForm(forms.ModelForm):
    class Meta:
        model = CarouselImage
        fields = ['image', 'start_date', 'end_date', 'terms', 'image_type']  # ✅ include image_type
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'terms': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 4,
                'placeholder': 'Enter terms and conditions (HTML supported)'
            }),
            'image_type': forms.Select(attrs={'class': 'form-control form-control-sm'}),  # ✅ dropdown
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True  # 👈 makes all fields required

class AgentRegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = AgentProfile
        fields = ["phone", "department", "role"]   # 👈 role add kar diya
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),  # 👈 dropdown style
        }

    def save(self, commit=True):
        # pehle User banao
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
        )
        agent = super().save(commit=False)
        agent.user = user
        if commit:
            agent.save()
        return agent

