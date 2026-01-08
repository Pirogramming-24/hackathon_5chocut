from django.contrib import admin
from .models import Profile


# 관리자 페이지에서 Profile 목록을 볼 때, 어떤 항목을 보여줄지 설정
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('login_id', 'name', 'role', 'created_at') # 아이디, 이름, 역할, 가입일 표시
    search_fields = ('login_id', 'name') # 검색창 추가