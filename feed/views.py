from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm

# Create your views here.

@login_required(login_url='register')
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    form = PostForm() if request.user.user_type == 'In' else None
    
    if request.method == 'POST' and request.user.user_type == 'In':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed:home')
            
    
        

    
    return render(request, 'feed/home.html', {
        'form': form,
        'posts': posts
    })
