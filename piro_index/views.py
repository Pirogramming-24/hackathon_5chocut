from django.shortcuts import render, get_object_or_404, redirect
from .models import Video, Timeline, Comment, Profile, Reply, Save, Like
from django.db.models import Prefetch
from django.contrib import messages
import json

def video_detail(request, pk):

    context = {
        'video': target_video,
        'comments': comments, 
        'timelines': timelines,
        'comment_count': comments.count(),
    }

    return render(request, 'video_detail.html', context)

def video_upload(request):
    # 비디오 업로드 로직 구현
    if request.method == 'POST':
        # 기본 필드 받기
        title = request.POST.get('title')
        video_file= request.FILES.get('video_file')
        thumbnail = request.FILES.get('thumbnail')
        timeline_data = request.POST.get('timeline_data', '[]')  # JSON 형식의 타임라인 데이터
        if not title:
            messages.error(request, '세션 제목을 입력해주세요.')
            return render(request, 'video_upload.html')
        
        if not video_file:
            messages.error(request, '비디오 파일을 업로드해주세요.')
            return render(request, 'video_upload.html')
        
        try:

            video-Video.objects.create(
                title=title,
                video_file=video_file,
                thumbnail=thumbnail if thumbnail else None,
            )

            try:
                timelines = json.loads(timeline_data)
                for timeline_item in timelines:
                    Timeline.objects.create(
                        video=video,
                        timetag=timeline_item['time'],
                        content=timeline_item['tag']
                    )
            except json.JSONDecodeError:
                messages.warning(request, '타임라인 데이터 처리 중 오류가 발생했습니다.')
            
            messages.success(request, '비디오가 성공적으로 업로드되었습니다!')
            return redirect('piro_index:video_detail', pk=video.pk)
            
        except Exception as e:
            messages.error(request, f'업로드 중 오류가 발생했습니다: {str(e)}')
            return render(request, 'video_upload.html')
    
    # GET 요청일 때는 빈 폼 렌더링
    return render(request, 'video_upload.html')


def login(request):
    return render(request, 'login.html')
