from django.shortcuts import render, get_object_or_404, redirect
from .models import Video, Timeline, Comment, Profile, Reply, Save, Like
from django.db.models import Prefetch

def video_detail(request, pk):

    context = {
        'video': target_video,
        'comments': comments, 
        'timelines': timelines,
        'comment_count': comments.count(),
    }

    return render(request, 'video_detail.html', context)

def login(request):
    return render(request, 'piro_index/login.html')