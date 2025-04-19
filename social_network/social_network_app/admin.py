from django.contrib import admin

from .models import Comment, Like, Post, PostImage

# Register your models here.

admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(Comment)
admin.site.register(Like)
