from django.conf import settings
from django.db import models
from django.utils import timezone


class Video(models.Model):
    title = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200, default="")
    publishedDate = models.DateTimeField(default=timezone.now)
    youtubeId = models.CharField(max_length=200)
    thumbnail = models.CharField(max_length=500)
    createdDate = models.DateTimeField(default=timezone.now)
    tags = models.CharField(max_length=500,default="")
    viewCount = models.BigIntegerField(default=0)
    likeCount = models.IntegerField(default=0)
    dislikeCount = models.IntegerField(default=0)
    commentCount = models.IntegerField(default=0)
    embedHtml = models.CharField(max_length=500, default="")
    

    def __str__(self):
        return self.title
   

