# models.py combinado
from django.contrib.auth.models import User
from django.db import models

class Post(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    titulo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=300)
    imagen = models.ImageField(upload_to='imagenes/', default='imagen')
    likes = models.ManyToManyField(User, related_name='post_likes')

    def cantidad_likes(self):
        return self.likes.count()

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    explanation = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)  # Agregamos una relación con Post

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

class UserQuestionValue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.IntegerField(default=10)
