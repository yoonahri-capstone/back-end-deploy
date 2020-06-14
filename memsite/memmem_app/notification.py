import requests
import json


def invitation_fcm(ids, name):
    # fcm 푸시 메세지 요청 주소
    url = 'https://fcm.googleapis.com/fcm/send'

    # 인증 정보(서버 키)를 헤더에 담아 전달
    headers = {
        'Authorization': 'key=AAAASoe0jvA:APA91bFVWB4yhPN1fyYyjiOoKOHxVQEsCyAGpgG1zrlvn_AuRKmxvXtcRJQQ9VYrj-KJN0_16kAA5ScMWL67Dss4D4C6LqxiE2PZdiQaVIu1BZn7HqDSGqhJlwr609BzXJGjZsMzGzYc',
        'Content-Type': 'application/json; UTF-8',
    }

    # 보낼 내용과 대상을 지정
    content = {
        'registration_ids': ids,
        'data':
            {
                'type' : "invite",
                'sharing': name
            }
    }

    # json 파싱 후 requests 모듈로 FCM 서버에 요청
    requests.post(url, data=json.dumps(content), headers=headers)


def scrap_fcm(ids, name, imgurl):
    url = 'https://fcm.googleapis.com/fcm/send'

    headers = {
        'Authorization': 'key=AAAASoe0jvA:APA91bFVWB4yhPN1fyYyjiOoKOHxVQEsCyAGpgG1zrlvn_AuRKmxvXtcRJQQ9VYrj-KJN0_16kAA5ScMWL67Dss4D4C6LqxiE2PZdiQaVIu1BZn7HqDSGqhJlwr609BzXJGjZsMzGzYc',
        'Content-Type': 'application/json; UTF-8',
    }

    content = {
        'registration_ids': ids,
        'data':
            {
                'type' : "upload",
                'image': imgurl,
                'sharing': name
            }
    }

    requests.post(url, data=json.dumps(content), headers=headers)