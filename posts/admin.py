from django.contrib import admin
from .models import Post, PostComment, PostLike, CommentLike

class PostLikeInline(admin.TabularInline):
    model = PostLike
    extra = 0
    readonly_fields = ['author', 'created_time']
    can_delete = False

class CommentInline(admin.TabularInline):
    model = PostComment
    extra = 0
    readonly_fields = ['author', 'comment', 'created_time']
    can_delete = False

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'caption_short', 'created_time', 'updated_time']
    list_filter = ['created_time', 'updated_time']
    search_fields = ['author__username', 'caption']
    ordering = ['-created_time']
    readonly_fields = ['created_time', 'updated_time']
    inlines = [PostLikeInline, CommentInline]

    def caption_short(self, obj):
        return (obj.caption[:75] + '...') if len(obj.caption) > 75 else obj.caption
    caption_short.short_description = 'Caption'


admin.site.register(PostComment)
# @admin.register(PostComment)
# class PostCommentAdmin(admin.ModelAdmin):
#     list_display = ['id', 'author', 'post', 'comment', 'parent', 'created_time']
#     list_filter = ['created_time']
#     search_fields = ['author__username', 'comment']
#     ordering = ['-created_time']
#     readonly_fields = ['created_time', 'updated_time']

#     def short_comment(self, obj):
#         return (obj.comment[:50] + '...') if len(obj.comment) > 50 else obj.comment
#     short_comment.short_description = 'Comment'

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'created_time']
    list_filter = ['created_time']
    search_fields = ['author__username', 'post__caption']
    ordering = ['-created_time']
    readonly_fields = ['created_time', 'updated_time']

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'comment', 'created_time']
    list_filter = ['created_time']
    search_fields = ['author__username', 'comment__comment']
    ordering = ['-created_time']
    readonly_fields = ['created_time', 'updated_time']
