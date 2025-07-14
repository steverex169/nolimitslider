from django import forms
from .models import CarouselImage

class CarouselImageForm(forms.ModelForm):
    class Meta:
        model = CarouselImage
        fields = ['image', 'start_date', 'end_date', 'terms']  # ✅ include 'terms'
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'terms': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 4,
                'placeholder': 'Enter terms and conditions (HTML supported)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True  # 👈 makes all fields required
