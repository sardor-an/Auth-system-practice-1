from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator, FileExtensionValidator
from django.db.models import UniqueConstraint

from shared.models import Base

User = get_user_model()

class Post(Base):
    author = models.ForeignKey(to=User, related_name='posts', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='post_images', validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
        ])
    caption = models.TextField(validators=[
            MaxLengthValidator(2000, "You cannot write more than 2000 chars"),
            MinLengthValidator(5, "You must write 5 chars at least")])
    
    class Meta:
        db_table = 'posts'
        verbose_name = 'post',
        verbose_name_plural = 'posts'


    def __str__(self):
        return f"{self.author.username}'s post named {self.caption}"  

class PostComment(Base):
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    post = models.ForeignKey(to=Post, related_name='comments', on_delete=models.CASCADE)
    comment = models.TextField(validators=[
        MaxLengthValidator(5000, "You have reaached to the end of hate"),
        MinLengthValidator(5, "Further more abusive words to be calm down")
    ])

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="child",
        on_delete=models.CASCADE
    )

    def __str__(self):
        if self.parent:
            return f'{self.comment} to comment'
        return f'{self.comment} to post'

class PostLike(Base):
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    post = models.ForeignKey(to=Post, related_name='likes', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['post', 'author'],
                name='PostAuthor'
            )
        ]

    def __str__(self):
        return f'like by {self.author.username} to post {self.post.caption}'

class CommentLike(Base):
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    comment = models.ForeignKey(to=PostComment, related_name='likes', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['comment', 'author'],
                name='CommentAuthor'
            )
        ]
    def __str__(self):
        return f'like by {self.author.username} to comment {self.comment}'