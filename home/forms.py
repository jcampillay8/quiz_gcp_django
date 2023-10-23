from django.forms import ModelForm, fields, models
from home.models import Post

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('titulo', 'descripcion', 'imagen')
        

