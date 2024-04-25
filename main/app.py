import os
import json
import boto3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = os.getenv('API_KEY', 'AIzaSyAVZhXNtFnRkq0Dzx8WZLTd4hxRo-w98q4')

def get_channel_id(channel_name):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    try:
        response = youtube.search().list(
            q=channel_name,
            part='id',
            maxResults=1,
            type='channel'
        ).execute()
        if 'items' in response and response['items']:
            return response['items'][0]['id']['channelId']
        else:
            return None
    except HttpError as e:
        print("An HTTP error occurred:", e)
        return None

def get_channel_info(channel_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    try:
        response = youtube.channels().list(
            part='statistics',
            id=channel_id
        ).execute()
        if 'items' in response and response['items']:
            return response['items'][0]['statistics']
        else:
            return None
    except HttpError as e:
        print("An HTTP error occurred:", e)
        return None

def get_total_likes(channel_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    try:
        response = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            order='rating',
            maxResults=50,
            type='video'
        ).execute()
        total_likes = 0
        for item in response['items']:
            video_id = item['id']['videoId']
            video_response = youtube.videos().list(
                part='statistics',
                id=video_id
            ).execute()
            like_count = video_response['items'][0]['statistics'].get('likeCount', 0)
            total_likes += int(like_count)
        return total_likes
    except HttpError as e:
        print("An HTTP error occurred:", e)
        return None

def compare_channel_stats(channel1_name, channel2_name):
    channel1_id = get_channel_id(channel1_name)
    channel2_id = get_channel_id(channel2_name)
    if channel1_id and channel2_id:
        channel1_info = get_channel_info(channel1_id)
        channel2_info = get_channel_info(channel2_id)
        if channel1_info and channel2_info:
            channel1_subscribers = int(channel1_info.get('subscriberCount', 0))
            channel2_subscribers = int(channel2_info.get('subscriberCount', 0))
            channel1_videos = int(channel1_info.get('videoCount', 0))
            channel2_videos = int(channel2_info.get('videoCount', 0))
            channel1_likes = get_total_likes(channel1_id)
            channel2_likes = get_total_likes(channel2_id)
            return {
                'channel1_name': channel1_name,
                'channel2_name': channel2_name,
                'channel1_subscribers': channel1_subscribers,
                'channel2_subscribers': channel2_subscribers,
                'channel1_videos': channel1_videos,
                'channel2_videos': channel2_videos,
                'channel1_likes': channel1_likes,
                'channel2_likes': channel2_likes
            }
    return None

def lambda_handler(event, context):
    if 'body' in event:
        data = json.loads(event['body'])
        channel1_name = data.get('channel1', '')
        channel2_name = data.get('channel2', '')
        
        result = compare_channel_stats(channel1_name, channel2_name)
        
        if result:
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Error comparing channels'})
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid request body'})
        }
        
if __name__ == '__main__':
    event = {
        'body': json.dumps({
            'channel1': 'tseries',
            'channel2': 'MrBeast'
        })
    }
    context = {}
    print(lambda_handler(event, context))