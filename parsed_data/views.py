from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Video
from .serializers import VideoSerializer

from collections import Counter,OrderedDict

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by('-createdDate')
    serializer_class = VideoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    @action(detail=False)
    def get_tags(self, request):
        tags = Video.objects.values_list('tags',flat=True)
        tags_list = list()
        for i in tags:
            for j in i.split(','):
                tags_list.append(j)

        #print(tags)
        #tags = Video.objects.all()
        # page = self.paginate_queryset(tags)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        # serializer = self.get_serializer(tags, many=True)
        res = sorted(Counter(tags_list).items(), key=(lambda x: x[1]), reverse = True)[:10]
        
        return Response(dict(res))
# def videos(request):
#     videos = Video.objects.all().order_by('-createdDate')[:5]
#     video_list = serializers.serialize('json', videos)
#     return HttpResponse(video_list, content_type="text/json-comment-filtered")

