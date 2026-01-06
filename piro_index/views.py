from django.shortcuts import render, get_object_or_404, redirect
from .models import Video, Timeline, Comment, Profile, Reply, Save, Like
from django.db.models import Prefetch

def video_detail(request, pk):
    target_video = get_object_or_404(Video, pk=pk)
    replies_order = Reply.objects.order_by('created_at') # 정렬1 대댓글: 오래된 순 정렬
    comments = Comment.objects.filter(video=target_video).order_by('-like_count', '-created_at') # 정렬 2 질문: 좋아요(like_count) 많은 순 정렬   
    timelines = Timeline.objects.filter(video=target_video).order_by('timetag') # 북동쪽 타임라인 데이터 (시간순 정렬)
    context = {
        'video': target_video,
        'comments': comments,
        'timelines': timelines,
        'comment_count': comments.count(),}
        
    return render(request, 'video_detail.html', context)