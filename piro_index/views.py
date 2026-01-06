from django.shortcuts import render, get_object_or_404, redirect
from .models import Video, Timeline, Comment, Profile, Reply, Save, Like
from django.db.models import Prefetch
from django.contrib import messages
import json
from django.db import transaction

def video_detail(request, pk):

    context = {
        'video': target_video,
        'comments': comments, 
        'timelines': timelines,
        'comment_count': comments.count(),
    }

    return render(request, 'video_detail.html', context)

def video_create(request):
    # 비디오 업로드 로직 구현
    if request.method == 'POST':
        # 기본 필드 받기
        title = request.POST.get('title')
        video_file= request.FILES.get('video_path')
        thumbnail = request.FILES.get('thumbnail')
        timeline_data = request.POST.get('timeline_data', '[]')  # JSON 형식의 타임라인 데이터
        if not title:
            messages.error(request, '세션 제목을 입력해주세요.')
            return render(request, 'video_create.html')
        
        if not video_file:
            messages.error(request, '비디오 파일을 업로드해주세요.')
            return render(request, 'video_create.html')
        
        try:

            video = Video.objects.create(
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
            return render(request, 'video_create.html')
    
    # GET 요청일 때는 빈 폼 렌더링
    return render(request, 'video_create.html')


def _seconds_to_hms(seconds: int) -> str:
    if seconds is None:
        return "00:00:00"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def video_update(request, pk):
    video = get_object_or_404(Video, pk=pk)

    if request.method == "POST":
        title = request.POST.get("title")
        new_video_file = request.FILES.get("video_path")  # name="video_path"
        new_thumbnail = request.FILES.get("thumbnail")    # name="thumbnail"
        timeline_data = request.POST.get("timeline_data", "[]")

        if not title:
            messages.error(request, "세션 제목을 입력해주세요.")
            return redirect("piro_index:video_update", pk=video.pk)

        try:
            with transaction.atomic():
                video.title = title

                # 파일은 선택된 경우에만 교체
                if new_video_file:
                    video.video_path = new_video_file

                if new_thumbnail:
                    video.thumbnail = new_thumbnail

                video.save()

                # 타임라인 업데이트
                try:
                    timelines = json.loads(timeline_data) if timeline_data else []
                except json.JSONDecodeError:
                    timelines = []
                    messages.warning(request, "타임라인 데이터 처리 중 오류가 발생했습니다.")

                if isinstance(timelines, list):
                    video.timelines.all().delete()
                    for item in timelines:
                        time = item.get("time")
                        tag = item.get("tag")
                        if isinstance(time, int) and isinstance(tag, str) and tag.strip():
                            Timeline.objects.create(
                                video=video,
                                timetag=time,
                                content=tag.strip()
                            )

            messages.success(request, "비디오가 성공적으로 수정되었습니다!")
            return redirect("piro_index:video_detail", pk=video.pk)

        except Exception as e:
            messages.error(request, f"수정 중 오류가 발생했습니다: {str(e)}")
            return redirect("piro_index:video_update", pk=video.pk)

    # GET: 프리필 데이터 구성
    timelines_qs = video.timelines.order_by("timetag", "id")
    timeline_list = [
        {"time": t.timetag, "tag": t.content, "timeStr": _seconds_to_hms(t.timetag)}
        for t in timelines_qs
    ]
    timeline_json = json.dumps(timeline_list, ensure_ascii=False)

    return render(request, "video_update.html", {
        "video": video,
        "timeline_json": timeline_json,
    })

def login(request):
    return render(request, 'login.html')
