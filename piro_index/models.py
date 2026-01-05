from django.db import models
from django.contrib.auth.models import User


class timeline(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='timelines', verbose_name='비디오') 
    timetag = models.IntegerField(verbose_name='타임태그' ,default = 0)
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(verbose_name='생성일자',auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일자',auto_now=True)

class video(models.Model):
    title = models.TextField()
    video_path = models.CharField(max_length=256)
    created_at = models.DateTimeField(verbose_name='생성일자',auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일자',auto_now=True)

class User(models.Model):
    login_id = models.CharField(max_length=32, unique =True)
    password = models.CharField(max_length=64)
    name = models.CharField(max_length=16)
    role = models.CharField(max_length=32)
    created_at = models.DateTimeField(verbose_name='생성일자',auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일자',auto_now=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    
    timetag = models.IntegerField()
    content = models.TextField()
    image_path = models.CharField(max_length=256, null=True, blank=True)
    like_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replies')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Save(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saves')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='saves')    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')    
    like_count = models.IntegerField(default=0)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

