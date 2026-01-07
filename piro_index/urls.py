from django.urls import path
from . import views

app_name = 'piro_index'

urlpatterns = [
    #1. 로그인, 회원가입, 마이페이지 관련 주소
    path('login/', views.login, name='login'), # 로그인
    path('', views.login, name='root_login'),
    path('logout/', views.logout, name='logout'),
    path('signup/',views.signup, name= 'signup'),# 회원가입
    path('mypage/',views.mypage, name= 'mypage'), # 마이페이지
    # path('<int:pk>/delete/',views.delete, name='delete'), # 탈퇴하기


    # #2. 비디오 
    
    path('video/',views.video_list, name = 'video_list'), # 비디오리스트 - 메인페이지
    path('video/create',views.video_create, name = 'video_create'), # 비디오 등록
    path('video/<int:pk>/',views.video_detail, name = 'video_detail'), # 비디오 상세페이지
    path('video/<int:pk>/update/',views.video_update, name = 'video_update'), # 비디오 수정 -> 등록폼
    path('video/<int:pk>/delete/',views.video_delete, name = 'video_delete'), # 비디오 삭제 -> 리스트

    # #3 찜하기
    path('video/<int:pk>/save/',views.video_save_ajax, name = 'video_save_ajax'), # 비디오 찜하기

    # #4 댓글
    path('video/<int:pk>/comment/', views.video_comment_create_ajax, name='video_comment_create_ajax'), # 질문 등록 
    path('comment/<int:pk>/reply/', views.comment_reply_create_ajax, name='comment_reply_create_ajax'), # 대댓글 등록
    path('comment/<int:pk>/update/', views.video_comment_update, name= 'video_comment_update'), # 댓글 수정
    path('comment/<int:pk>/delete/', views.video_comment_delete, name='video_comment_delete'), # 댓글 삭제
    # #5 좋아요 == 저도 궁금해요
    path('comment/<int:pk>/like/', views.comment_like_ajax, name='comment_like_ajax'),

]