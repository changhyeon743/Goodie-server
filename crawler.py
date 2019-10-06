# Create your models here.
CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

MAX_COMMENTS = 20


import csv
import os
import pickle
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goodie.settings")
## 이제 장고를 가져와 장고 프로젝트를 사용할 수 있도록 환경을 만듭니다.
import django
django.setup()
from parsed_data.models import Video


import numpy as np
from sklearn.model_selection import train_test_split
import pandas as pd
from konlpy.tag import Okt

def get_noun(text):
    tokenizer = Okt()
    nouns = tokenizer.nouns(text)
    return [n for n in nouns]

filename = 'model.sav'
loaded_model = pickle.load(open(filename, 'rb'))

def predict(texts):
    return (loaded_model.predict(texts))

import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def write_to_csv(comments,name):
    with open(name, 'a') as comments_file:
        for row in comments:
            comments_file.write(row+"\n")

# def get_authenticated_service():
#     flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
#     credentials = flow.run_console()
#     return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def get_authenticated_service():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    #  Check if the credentials are invalid or do not exist
    if not credentials or not credentials.valid:
        # Check if the credentials have expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_console()

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)


def get_related_video(service, **kwargs):
    final_results = []
    results = service.search().list(**kwargs).execute()
    return results

def get_video_comments(service, **kwargs):
    comments = []
    try:
        results = service.commentThreads().list(**kwargs).execute()
    except HttpError:
        return []

    while results:
        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        if len(comments) > MAX_COMMENTS:
            break

        # Check if another page exists
        if 'nextPageToken' in results:
            kwargs['pageToken'] = results['nextPageToken']
            results = service.commentThreads().list(**kwargs).execute()
        else:
            break

        

    return comments


def get_video(service, **kwargs):
    results = service.videos().list(**kwargs).execute()
    return results



if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = get_authenticated_service()
    which = input('Search: 0\nComments: 1:\nAnalyze: 2: ')


    if which == '0':
        keyword = input("id")
        info = get_video(service,part='snippet,player,statistics',id=keyword)['items'][0]
        snippet = info["snippet"]
        Video(title=snippet["localized"]["title"],
        publisher=snippet["channelTitle"],
        publishedDate=snippet["publishedAt"],
        youtubeId=info["id"],
        thumbnail=snippet["thumbnails"]["default"]["url"],
        tags=','.join(snippet["tags"]),
        viewCount=info["statistics"]["viewCount"],
        likeCount=info["statistics"]["likeCount"],
        dislikeCount=info["statistics"]["dislikeCount"],
        commentCount=info["statistics"]["commentCount"],
        embedHtml=info["player"]["embedHtml"],).save()
    if which == '1':
        keyword = input('Type ID of video: ')
        #name = input('name of csv: ')
        
        comments = get_video_comments(service, part='snippet', videoId=keyword, textFormat='plainText')
        print(comments)
        #write_to_csv(comments,name)
    elif which == '2':
        keyword = input('Type ID of video(Start~~): ')
        strong_point = keyword
        final_videos = []
        cnt = 0;
        while len(final_videos) < 5:
            cnt+=1;
            print("analyzing start: ",len(final_videos),": ",keyword)
            comments = get_video_comments(service, part='snippet', videoId=keyword, textFormat='plainText')
            
            #final_videos contains self
            if (len(comments) > 0 and not(keyword in final_videos)):
                predicted = list(predict(comments))
                print({"id":keyword,"good": predicted.count(1), "bad": predicted.count(2)})
                if (predicted.count(1) > predicted.count(2)): #좋은 영상 발견
                    final_videos.append(keyword)
                    strong_point = keyword
                    cnt = 0
                    
                
            # 구렁텅이로 빠질 때, (게임쪽으로 빠졌을 때)
            # 물론 랜덤성이라는 돌연변이 성격에 의해 오랜 시간이 지나면 탈출하겠지만 quota가 부족한 점을 고려한다.
            # 거점은 첫 동영상을 시작으로 좋은 ㅇ여상을 찾을 때마다 업데이트 된다.
            if cnt < 5:
                keyword = get_related_video(service, part='id', relatedToVideoId=keyword,regionCode='KR', type='video')["items"]
                l = [i["id"]["videoId"] for i in keyword]
                keyword = random.choice(l)
            else:
                keyword = strong_point
                cnt=0

        for i in final_videos:
            info = get_video(service,part='snippet,player,statistics',id=i)['items'][0]
            snippet = info["snippet"]
            Video(title=snippet["localized"]["title"],
            publisher=snippet["channelTitle"],
            publishedDate=snippet["publishedAt"],
            youtubeId=info["id"],
            thumbnail=snippet["thumbnails"]["standard"]["url"],
            tags=','.join(snippet["tags"] or ""),
            viewCount=info["statistics"]["viewCount"],
            likeCount=info["statistics"]["likeCount"],
            dislikeCount=info["statistics"]["dislikeCount"],
            commentCount=info["statistics"]["commentCount"],
            embedHtml=info["player"]["embedHtml"],).save()
            print()

        
            
