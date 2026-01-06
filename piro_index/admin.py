from django.contrib import admin
from .models import Profile

# 관리자 페이지에 Profile 테이블 등록
admin.site.register(Profile)