from rest_framework import serializers
from rest_framework.request import Request

from .models import Post, PostLike, PostComment, CommentLike
from users.serializer import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)  # read_only -> not have to validate, it is weird but pay attention to that you have written author alson in meta fields
    post_likes_count = serializers.SerializerMethodField('get_post_likes_count')
    post_comments_count = serializers.SerializerMethodField('get_post_comments_count')
    me_liked = serializers.SerializerMethodField('get_me_liked')
    
    class Meta:
        model = Post
        fields = (
            'id',
            'author',
            'image',
            'caption',
            'created_time',
            'post_likes_count',
            'post_comments_count',

            # Why

            'me_liked'
        )

    @staticmethod
    def get_post_likes_count(obj):
        return obj.likes.count()

    @staticmethod
    def get_post_comments_count(obj):
        return obj.comments.count()
    
    def get_me_liked(self, obj):
        request: Request = self.context.get('request', None)

        if request and request.user.is_authenticated:
            post_like = PostLike.objects.filter(post=obj, author=request.user)
        
            return post_like.exists() # obj.likes.filter(author=request.user).exists()

        return False


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    # author = UserSerializer(read_only=True)
    # post = PostSerializer(required=False) # how
    # post_id = ch
    replies = serializers.SerializerMethodField('get_replies')
    me_liked = serializers.SerializerMethodField('get_me_liked')
    likes_count = serializers.SerializerMethodField('get_likes_count')
    parent_id = serializers.CharField(required=False)
    class Meta:
        model = PostComment
        fields = (
            'id',
            'comment',
            # 'author',
            'post',
            'created_time',
            'replies', # added by me,
            'me_liked',
            'likes_count',
            'parent_id'
            
        )
    
    

    def get_replies(self, obj):
        if obj.child.exists():
            serializer = __class__(obj.child.all(), many=True, context=self.context)
            return serializer.data
        
    def get_me_liked(self, obj: PostComment):
        request: Request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            return obj.likes.filter(author=request.user).exists()
        
        return False
    
    @staticmethod
    def get_likes_count(obj):
        return obj.likes.count()
    

class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = CommentLike
        fields = ('id', 'author', 'comment')


class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ('id', 'author', 'post')    