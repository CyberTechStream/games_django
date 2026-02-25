from django import forms
from .models import Review, Profile
from django.contrib.auth.models import User

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text", "rating"]
        
class ProfileEditForm(forms.ModelForm):
    nickname = forms.CharField(
        max_length=50,
        required=True,
        label="Нікнейм",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Profile
        fields = ["avatar", "bio", "nickname"]
        widgets= {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Про себе...'})
        }
        
        
        
    
    