from django import forms
import django
from django.contrib.auth import authenticate, login
from django.http import Http404
from django.contrib.auth.forms import UserCreationForm
from django.core import paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from home.models import Post, UserQuestionValue, Question
from home.forms import PostForm
from home.gcp_trainer_app import app


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 3)
    num_pagina = request.GET.get('page')
    pagina_actual = paginator.get_page(num_pagina)
    return render(request, 'index.html', {'posts': pagina_actual })

@login_required(login_url='login')
def crearPost(request):
    if request.method == 'POST':
        form =PostForm(request.POST, request.FILES)    
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
        return render(request, 'creacion.html', {'form': form})

@login_required(login_url='login')
def verPost(request, pk):
    # post = Post.objects.get(id=pk)
    post = get_object_or_404(Post, id=pk)
    tieneLike = request.user in post.likes.all()
    return render(request, 'post.html', {'post':post, 'likes': post.cantidad_likes(), 'tiene_like': tieneLike})

@login_required(login_url='login')
def actualizarPost(request, pk):
    # post = Post.objects.get(id=pk)
    post = get_object_or_404(Post, id=pk)
    if request.user == post.autor:
        if request.method == 'POST':
            form =PostForm(request.POST, request.FILES, instance=post)    
            if form.is_valid():
                post.save()
                return redirect('index')
        else:
            form = PostForm(instance=post)
            return render(request, 'creacion.html', {'form': form})
    else:
        return redirect(f'/post/{post.id}')

@login_required(login_url='login')
def eliminarPost(request, pk):
    # post = Post.objects.get(id=pk)
    post = get_object_or_404(Post, id=pk)
    if post.autor == request.user:
        if request.method == 'POST':
            post.delete()
            return redirect('index')
        
        return render(request, 'eliminar.html', {'post':post})
    else:
        return redirect(f'/post/{post.id}')

@login_required(login_url='login')
def darLike(request, pk):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=pk)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return redirect('/post/'+str(post.id))
    else:
        raise Http404()


def registrarUsuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)    
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            for question in Question.objects.all():
                UserQuestionValue.objects.create(user=user, question=question, value=10)  # Crea una instancia de UserQuestionValue para cada pregunta
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def dash_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    if pk == 3:
        return render(request, 'quiz_gcp_digital_leader.html')
    else:
        return render(request, 'quiz_no_disponible.html',{'post':post})