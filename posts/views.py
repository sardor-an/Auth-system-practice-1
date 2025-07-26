from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from .models import Post, PostLike, PostComment, CommentLike
from .serializers import PostSerializer, CommentSerializer, CommentLikeSerializer, PostLikeSerializer
from .paginations import PostPagination

class PostListApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    serializer_class = PostSerializer
    pagination_class = PostPagination




    def get_queryset(self):
        return Post.objects.all()
    
    def perform_create(self, serializer): # what if i use save, and more perform_update/delete/retrive
        serializer.save(author=self.request.user)
    
class PostRetriveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def put(self, request, *args, **kwargs): # it can be done by parent-view, but we wanted to custumize the returning data
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'success': True,
            'data': serializer.data
        })
    

class PostCommentsApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    serializer_class = CommentSerializer
    pagination_class = PostPagination

    def get_queryset(self):
        post = Post.objects.filter(id=self.kwargs['pk'])

        if post.exists():
            return post.filter().first().comments.all()
        
        return []
    
class CommentComentApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer
    pagination_class = PostPagination

    def get_queryset(self):
        comment = PostComment.objects.all().filter(id=self.kwargs['pk'])
        if comment.exists():
            return comment.first().child.all()
        
        return []


class CommentPostCreateApiView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    # queryset = PostComment.objects.all()
    
    # def create(self, request, *args, **kwargs):
    #     return Response({'msg': 'Done'})

    def create(self, request, *args, **kwargs):
        data =  super().create(request, *args, **kwargs)
        extra_data = {
            'success': True,
            'message': 'Comment done for now'
        }
        data.data = {**extra_data, **data.data} # god practices
        return data

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=Post.objects.get(pk=self.request.data['post']))

class CommentCommenCreateApiView(generics.CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def perform_create(self, serializer: CommentSerializer):
        data = serializer.validated_data
        if data.get('parent_id', None):
            parent_comment = PostComment.objects.get(id=data['parent_id'])
            post = Post.objects.get(id=self.request.data['post'])

            if parent_comment in post.comments.all():
                print(post.comments)
                serializer.save(author=self.request.user, post=Post.objects.get(pk=self.request.data['post']), parent=parent_comment)
            else:
                raise ValidationError({
                    'success': False,
                    'message': 'Parent comment does not belong to the post'
                })
        
        else:
            serializer.save(author=self.request.user, post=Post.objects.get(pk=self.request.data['post']))

    
    def create(self, request, *args, **kwargs):
        data =  super().create(request, *args, **kwargs)
        extra_data = {
            'success': True,
            'message': 'Comment to comment has been created successfully'
        }

        data.data = {**extra_data, **data.data}
        return data

# comment likes
# post likes

class CreateDeletePostLikeApiView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostLikeSerializer

    def perform_create(self, serializer: PostLikeSerializer):
        # serializer.save(author=self.request.user, post="cfd9f0ff-f78c-4e0b-97dd-b64e7dbf3c96") # how id is being translated to instance in serializer
        

        data = serializer.validated_data

        like = Post.objects.get(id=self.request.data['post']).likes.filter(author=self.request.user)
        print(like)
        if like.exists():
            like.first().delete()
            return {'msg': 'Unliked true'}
        
        serializer.save(author=self.request.user)
        return {'msg': 'Liked true'}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        msg = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        data = {**msg, **serializer.data}
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class CreateDeleteCommentLikeApiView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentLikeSerializer

    def perform_create(self, serializer: PostLikeSerializer):
        # serializer.save(author=self.request.user, post="cfd9f0ff-f78c-4e0b-97dd-b64e7dbf3c96") # how id is being translated to instance in serializer
        

        like = PostComment.objects.get(id=self.request.data['comment']).likes.filter(author=self.request.user)
    
        if like.exists():
            like.first().delete()
            return {'msg': 'Unliked true'}
        
        serializer.save(author=self.request.user)
        return {'msg': 'Liked true'}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        msg = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        data = {**msg, **serializer.data}
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class CommentLikesListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentLikeSerializer
    pagination_class = PostPagination
    def get_queryset(self):
        return PostComment.objects.get(id=self.kwargs['pk']).likes.all()

class PostLikesListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostLikeSerializer

    def get_queryset(self):
        return Post.objects.get(id=self.kwargs['pk']).likes.all()






