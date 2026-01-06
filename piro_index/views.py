from django.shortcuts import render, get_object_or_404, redirect
from .models import Video, Timeline, Comment, Profile, Reply, Save, Like
from django.http import JsonResponse

    #비디오 상세 페이지 조회
    def video_detail(request, pk):
        target_video = get_object_or_404(Video, pk=pk)
        comments = Comment.objects.filter(video=target_video).order_by('-like_count', '-created_at') # 정렬 2 질문: 좋아요(like_count) 많은 순 정렬   
        for comment in comments:
            comment.replies_list = comment.replies.all().order_by('created_at') # 정렬1 대댓글: 오래된 순 정렬
        timelines = Timeline.objects.filter(video=target_video).order_by('timetag') # 북동쪽 타임라인 데이터 (시간순 정렬)
        context = {
            'video': target_video,
            'comments': comments,
            'timelines': timelines,
            'comment_count': comments.count(),}
            
        return render(request, 'video_detail.html', context)


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
