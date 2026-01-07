from django.shortcuts import render, get_object_or_404, redirect
from .models import Video, Timeline, Comment, Profile, Reply, Save, Like
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.db.models import Count,Q
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.contrib import messages
import json

#비디오 상세 페이지 조회
def video_detail(request, pk):
        target_video = get_object_or_404(Video, pk=pk)
        comments = Comment.objects.filter(video=target_video).order_by('-like_count', '-created_at') # 정렬 2 질문: 좋아요(like_count) 많은 순 정렬   
        for comment in comments:
            comment.replies_list = comment.replies.all().order_by('created_at') # 정렬1 대댓글: 오래된 순 정렬
        timelines = Timeline.objects.filter(video=target_video).order_by('timetag') # 북동쪽 타임라인 데이터 (시간순 정렬)

        user_id = request.session.get('user_id')
        is_staff = False  # 기본값
    
        if user_id:
            try:
                profile = Profile.objects.get(id=user_id)
                if profile.role == "운영진":
                    is_staff = True
            except Profile.DoesNotExist:
                is_staff = False

        context = {
            'video': target_video,
            'comments': comments,
            'timelines': timelines,
            'comment_count': comments.count(),
            'is_staff' : is_staff,}
            
        return render(request, 'piro_index/video_detail.html', context)

def login(request):
    if request.method == 'POST':
        # 1. HTML에서 아이디/비번 가져오기
        login_id = request.POST.get('login_id')  # HTML input name과 맞춰야 함
        password = request.POST.get('password')

        # 2. 아이디가 있는지 확인
        try:
            user = Profile.objects.get(login_id=login_id)
        except Profile.DoesNotExist:
            user = None

        # 3. 비밀번호 검사 (암호화된 비번 vs 입력한 비번 비교)
        if user and check_password(password, user.password):
            request.session['user_id'] = user.id 
            
            # 4. 비디오 목록 페이지로 이동
            return redirect('piro_index:video_list')
        
        else:
            # 실패 시 에러 메시지 띄우기
            context = {'error': '아이디 또는 비밀번호가 잘못되었습니다.'}
            return render(request, 'piro_index/login.html', context)

    # GET 요청 (그냥 접속)
    return render(request, 'piro_index/login.html')

def logout(request):
    # 세션에 저장된 모든 정보(로그인 정보 포함)를 싹 지웁니다.
    request.session.flush() 
    
    # 로그아웃 후 다시 로그인 화면으로 보냅니다.
    return redirect('piro_index:login')
    
def signup(request):
    if request.method == 'POST':
        # 1. HTML에서 입력한 값들 꺼내오기 (name 속성과 일치해야 함)
        login_id = request.POST.get('login_id')
        raw_password = request.POST.get('password')
        name = request.POST.get('name')
        role = request.POST.get('role')

        # 2. 아이디 중복 체크 (선택사항이지만 필수적인 로직)
        if Profile.objects.filter(login_id=login_id).exists():
            return render(request, 'piro_index/signup.html', {'error': '이미 사용 중인 아이디입니다.'})

        # 3. DB에 저장 (CREATE)
        Profile.objects.create(
            login_id=login_id,
            password=make_password(raw_password), 
            name=name,
            role=role
        )

        # 4. 저장 완료 후 로그인 페이지로 이동
        return redirect('piro_index:login') # urls.py에 있는 로그인 url 이름

    # POST가 아닌 경우(그냥 페이지 접속)
    return render(request, 'piro_index/signup.html')

# 마이페이지 - 정보수정
def mypage(request):
    # 1. 로그인 여부 확인 (비로그인자가 들어오면 쫓아냄)
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('piro_index:login')
    
    # 2. 현재 로그인한 사용자 객체 가져오기
    try:
        user = Profile.objects.get(id=user_id)
    except Profile.DoesNotExist:
        return redirect('piro_index:login')

    if request.method == 'POST':
        # 1. 입력값 받아오기
        new_login_id = request.POST.get('login_id') # 아이디 변경 요청
        new_password = request.POST.get('password')
        name = request.POST.get('name')
        # role = request.POST.get('role')  <-- 삭제 (2번 요청)

        # 2. 아이디 중복 체크 (아이디를 변경했을 때만!)
        if new_login_id != user.login_id:
            if Profile.objects.filter(login_id=new_login_id).exists():
                # 이미 있는 아이디면 에러 메시지와 함께 다시 페이지 보여줌
                context = {
                    'user': user,
                    'comments': Comment.objects.filter(user=user).select_related('video').order_by('-created_at'),
                    'error': '이미 존재하는 아이디입니다.' # 에러 메시지 전달
                }
                return render(request, 'piro_index/mypage.html', context)
            else:
                user.login_id = new_login_id # 중복 없으면 아이디 변경

        # 3. 이름 변경
        user.name = name
        
        # 4. 역할 변경 코드 삭제함
        # user.role = role 

        # 5. 비밀번호 변경 (입력했을 때만)
        if new_password and new_password.strip():
            user.password = make_password(new_password)
        
        user.save() # 최종 저장
        
        return redirect('piro_index:mypage')
    # --- [조회 로직] ---
    # 3. 내가 쓴 댓글 가져오기 (최신순 정렬)
    # select_related('video')를 쓰면 비디오 제목 가져올 때 DB를 또 안 찔러서 성능이 좋아집니다.
    my_comments = Comment.objects.filter(user=user).select_related('video').order_by('-created_at')

    context = {
        'user': user,          # 내 정보
        'comments': my_comments # 내 댓글 리스트
    }
    return render(request, 'piro_index/mypage.html', context)


# 질문 등록(AJAX)
def video_comment_create_ajax(request, pk):
        if request.method == 'POST': #요청이 POST인지 확인
            target_video = get_object_or_404(Video, pk=pk) #video테이블에서 pk 내가 찾는거 가져오기
            
            # timetag와 content를 받아 저장 / commnet create 이건 장고 명령어로 데베에 한줄 저장
            new_comment = Comment.objects.create(
                user=request.user,
                video=target_video,
                content=request.POST.get('content'),
                timetag=request.POST.get('timetag', 0)
            )
            
            return JsonResponse({  #작업이 끝나면 필요한 데이터만 JSON에 담아 JS로 보내줌
                'status': 'success',
                'commentId': new_comment.pk,
                'content': new_comment.content,
                'timetag': new_comment.timetag,
                'user_name': request.user.name,
                'role': request.user.role # 부원/운영진 색 구분을 위한 데이터
            })
    

    # 대댓글(답글) 등록 (AJAX)
def comment_reply_create_ajax(request, pk):
        if request.method == 'POST':
            parent_comment = get_object_or_404(Comment, pk=pk) #댓글의 pk

            new_reply = Reply.objects.create( #Reply 테이블에 추가
                user=request.user,
                comment=parent_comment,
                video=parent_comment.video,
                content=request.POST.get('content')
            )
             
            return JsonResponse({ # 작업이 끝난 후 필요한 데이터만 JS에 보내줌
                'status': 'success',
                'content': new_reply.content,
                'user_name': request.user.name,
                'role': request.user.role # 답글도 작성자 역할에 따라 색 구분 가능
            })



    # 나도 궁금해요 토글
def comment_like_ajax(request, pk):
        
        comment = get_object_or_404(Comment, pk=pk) # 좋아요를 누른 댓글이 DB에 있는지 확인 후 담기
        
        like_obj, created = Like.objects.get_or_create( # Like 테이블에서 이 유저가 해당 댓글에 누른 기록이 있는지 확인, 객체, 새로 만들었다면 TRUE 이미 있어서 찾기만 했다면 FALSE가 저장 
            user=request.user, 
            comment=comment, 
            video=comment.video
        )
        
        if not created: # 이미 좋아요를 눌렀다면 취소
            like_obj.delete()
            comment.like_count -= 1
        else: # 처음 누르는 거라면 추가
            comment.like_count += 1
        
        comment.save()
        
        return JsonResponse({ 
            'status': 'success',
            'like_count': comment.like_count # 변경된 좋아요 수를 반환하여 실시간 업데이트 새로고침 없이
        })


    # 운영진 권한 기반 삭제 
def video_comment_delete(request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        
        # 유저의 role이 운영진인 경우에만 삭제가 가능하도록
        if request.user.role == '운영진':
            video_pk = comment.video.pk #댓글을 지우기 전에, 이 댓글이 달려있던 비디오의 번호를 미리 메모
            comment.delete()
            return redirect('piro_index:video_detail', pk=video_pk)
        
        # 운영진이 아닐 경우 에러 메시지 반환
        return JsonResponse({'status': 'error', 'message': '운영진만 삭제할 수 있습니다.'}, status=403)

    # 운영진 권한 기반 수정
def video_comment_update(request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        
        # 수정 또한 운영진 권한이 필요합니다.
        if request.user.role == '운영진' and request.method == 'POST':
            comment.content = request.POST.get('content')
            comment.save()
            return JsonResponse({'status': 'success', 'content': comment.content})
        
        return JsonResponse({'status': 'error'}, status=403)


def video_list(request):
    """비디오 리스트 페이지 - 메인 페이지"""
    # 정렬 기준 가져오기 (기본값: 빈 문자열)
    sort_by = request.GET.get('sort', '')
    
    # 검색어 가져오기
    search_query = request.GET.get('search', '')
    
    # 비디오 목록 가져오기
    videos = Video.objects.all()
    
    # 검색 필터 적용
    if search_query:
        videos = videos.filter(
            Q(title__icontains=search_query)
        )
    
    # 각 비디오의 찜하기 개수 추가
    videos = videos.annotate(save_count=Count('saves'))
    
    # 정렬 적용
    if sort_by == 'latest':
        videos = videos.order_by('-created_at')
    elif sort_by == 'oldest':
        videos = videos.order_by('created_at')
    elif sort_by == 'saves':
        videos = videos.order_by('-save_count')
    else:
        # 정렬 기준이 없으면 최신순으로 기본 정렬
        videos = videos.order_by('-created_at')
    
    # 페이지네이션 (한 페이지당 6개)
    paginator = Paginator(videos, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 현재 로그인한 사용자가 찜한 비디오 ID 목록
    user_id = request.session.get('user_id')
    saved_video_ids = []
    is_staff = False  # 기본값: 부원
    
    if user_id:
        try:
            user_profile = Profile.objects.get(id=user_id)
            saved_video_ids = list(Save.objects.filter(user=user_profile).values_list('video_id', flat=True))
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # role로 운영진/부원 구분 (비디오 등록 버튼 표시 여부)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            if user_profile.role == '운영진':
                is_staff = True
            else:
                is_staff = False
        except Profile.DoesNotExist:
            pass
    
    context = {
        'videos': page_obj,
        'sort_by': sort_by,
        'search_query': search_query,
        'saved_video_ids': saved_video_ids,
        'is_staff': is_staff,
    }
    
    return render(request, 'piro_index/video_list.html', context)

def video_save_ajax(request, pk):
    """찜하기 토글 (AJAX)"""
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        
        if not user_id:
            return JsonResponse({
                'success': False, 
                'message': '로그인이 필요합니다.'
            })
        
        try:
            user_profile = Profile.objects.get(id=user_id)
            video = get_object_or_404(Video, pk=pk)
            
            # 이미 찜했는지 확인
            save_obj = Save.objects.filter(user=user_profile, video=video).first()
            
            if save_obj:
                # 이미 찜한 경우 - 찜 취소
                save_obj.delete()
                is_saved = False
                message = '찜하기가 취소되었습니다.'
            else:
                # 찜하지 않은 경우 - 찜하기
                Save.objects.create(user=user_profile, video=video)
                is_saved = True
                message = '찜하기가 완료되었습니다.'
            
            # 현재 찜하기 개수
            save_count = Save.objects.filter(video=video).count()
            
            return JsonResponse({
                'success': True,
                'is_saved': is_saved,
                'save_count': save_count,
                'message': message
            })
            
        except Profile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '사용자 정보를 찾을 수 없습니다.'
            })
    
    return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'})

def video_create(request):
    """비디오 업로드 (운영진 전용)"""
    
    # 로그인 확인
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, '로그인이 필요합니다.')
        return redirect('piro_index:login')
    
    try:
        user_profile = Profile.objects.get(id=user_id)
        if user_profile.role != '운영진':
            messages.error(request, '운영진만 비디오를 등록할 수 있습니다.')
            return redirect('piro_index:video_list')
    except Profile.DoesNotExist:
        messages.error(request, '사용자 정보를 찾을 수 없습니다.')
        return redirect('piro_index:login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        
        # ⭐ HTML의 name="video_file"에 맞춰서!
        video_file = request.FILES.get('video_file')  # ← video_file!
        
        thumbnail = request.FILES.get('thumbnail')
        timeline_data = request.POST.get('timeline_data', '[]')
        
        if not title:
            messages.error(request, '세션 제목을 입력해주세요.')
            return render(request, 'piro_index/video_create.html')
        
        if not video_file:
            messages.error(request, '비디오 파일을 업로드해주세요.')
            return render(request, 'piro_index/video_create.html')
        
        try:
            # ⭐ 모델의 video_path 필드에 저장!
            video = Video.objects.create(
                title=title,
                video_path=video_file,  # ← video_path 필드에 저장!
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
            
            # ⭐ video_detail로 리다이렉트!
            return redirect('piro_index:video_list')
            
        except Exception as e:
            messages.error(request, f'업로드 중 오류가 발생했습니다: {str(e)}')
            return render(request, 'piro_index/video_create.html')
    
    return render(request, 'piro_index/video_create.html')

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


def video_delete(request, pk):
    target_video = get_object_or_404(Video, pk=pk)
    target_video.delete()
    return redirect('piro_index:video_list')
