from rest_framework import viewsets, permissions, generics, status
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Profile, Folder, Scrap, Memo, Tag, Place, Food

from .serializers import UserSerializer
from .serializers import CreateUserSerializer
from .serializers import LoginUserSerializer
from .serializers import UserFolderSerializer
from .serializers import ScrapSerializer
from .serializers import ScrapListSerializer
#from .serializers import DefaultScrapListSerializer
from .serializers import UrlRequestSerializer
from .serializers import CreateScrapSerializer
from .serializers import CreateTagSerializer
from .serializers import MemoSerializer
from .serializers import TagSerializer
from .serializers import FolderRequestSerializer
from .serializers import CreateFolderSerializer
from .serializers import UpdateScrapSerializer
from .serializers import FolderSerializer
from .serializers import UpdateFolderSerializer
from .serializers import IdListSerializer
from .serializers import RecrawlingSerializer
from .serializers import UserLocationSerializer

# from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from knox.models import AuthToken
from .crawling import crawl_request
from .hashtag_classification import get_distance
from django.core.exceptions import ObjectDoesNotExist

from django.http import JsonResponse

import requests
import re
import json
import random


# register user
class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        # if 404 조건들 return Response(body, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        Profile.objects.get_or_create(user=user)
        Folder.objects.get_or_create(user=user, folder_key=0)

        return JsonResponse({'status': 200})


# login
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        # return Response(
        #     {
        #         'user': UserSerializer(
        #             user, context=self.get_serializer_context()
        #         ).data,
        #         # 'token': AuthToken.objects.create(user)[1]
        #     }
        # )

        return JsonResponse(
            {
                'status': 200,
                'id': UserSerializer(user, context=self.get_serializer_context()
                                     ).data['id']
            }
        )


'''
class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
'''


class MyUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Get User's Folder List
class FolderViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserFolderSerializer

    def get_queryset(self, *args, **kwargs):
        return User.objects.filter(id=self.kwargs['pk'])


# Get Scrap List (in Folder)
class FolderScrapsViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = ScrapListSerializer

    def get_queryset(self, *args, **kwargs):
        #return Folder.objects.filter(user_id=self.kwargs['pk'], folder_key=self.kwargs['folder_key'])
        return Folder.objects.filter(user_id=self.kwargs['pk'], folder_id=self.kwargs['folder_id'])

'''
# Get Scrap List (in Default Folder)
class DefaultFolderScrapsViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = DefaultScrapListSerializer

    def get_queryset(self, *args, **kwargs):
        return Folder.objects.filter(user_id=self.kwargs['pk'], folder_key=0)
'''


# Get User Scrap List
class ScrapAllViewSet(viewsets.ModelViewSet):
    queryset = Scrap.objects.all()
    serializer_class = ScrapSerializer

    def get_queryset(self, *args, **kwargs):
        return Scrap.objects.filter(folder__user=self.kwargs['pk']).order_by('-scrap_id')


class CheckScrapAPI(APIView):
    def get(self, *args, **kwargs):
        query = Scrap.objects.filter(folder__user=self.kwargs['pk']).order_by('-scrap_id')

        del_list = []
        for scrap in query:
            response = requests.get(scrap.url)
            print(response.status_code)
            if response.status_code != 200:
                del_list.append(scrap.title)
                scrap.delete()

        return JsonResponse(
            {
                'delete': del_list
            }
        )

'''
class ScrapViewSet(viewsets.ModelViewSet):
    queryset = Scrap.objects.all()
    serializer_class = ScrapSerializer

    def get_queryset(self, *args, **kwargs):
        #return Scrap.objects.filter(folder__user=self.kwargs['pk'], scrap_id=self.kwargs['scrap_pk'])
        return Scrap.objects.filter(scrap_id=self.kwargs['pk'])
'''

regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"


# ADD new url
class CreateScrapAPI(generics.GenericAPIView):
    #serializer_class = CreateScrapSerializer
    serializer_class = UrlRequestSerializer

    def post(self, request, *args, **kwargs):
        '''
        request = json.loads(request.body)
        user = request['id']
        #folder_key = request['folder_key']
        folder_id = request['folder_id']
        check = request['url']
        '''

        user = request.data['id']
        folder_id = request.data['folder_id']
        check = request.data['url']

        url = re.findall(regex, check)[0][0]

        response = requests.get(url)
        # print(response)# (status_code)

        if Scrap.objects.filter(folder__user=user, url=url).exists():
            return JsonResponse(
                {
                    'message': 'URL EXISTS',
                    'status': '403',
                    'scraps': {}
                }
            )

        if response.status_code == 200:
            # crawling = [URL, title, thumbnail, domain] + [tag list..]
            crawling = crawl_request(url)

            if crawling is None:
                return JsonResponse(
                    {
                        'message': 'CRAWLING EXCEPTION',
                        'status': '403',
                        'scraps': {}
                    }
                )
            else:
                crawl_list = []
                tags_list = []
                num = 0

                if len(crawling) > 4:
                    crawl_list = crawling[0:4]
                    tags_list = crawling[4:]
                    num = len(tags_list)
                else:
                    crawl_list = crawling

                # search folder id
                #folder_id = Folder.objects.filter(user=user, folder_key=folder_key).values_list('folder_id', flat=True)
                #folder_id = folder_id[0]
                
                crawl_data = dict(folder=folder_id,
                                  url=crawl_list[0],
                                  title=crawl_list[1],
                                  thumbnail=crawl_list[2],
                                  domain=crawl_list[3])

                serializer = CreateScrapSerializer(data=crawl_data)
                serializer.is_valid(raise_exception=True)
                scrap = serializer.save()

                if num > 0:
                    tag_to = Scrap.get_id(scrap)
                    for i in range(0, num):
                        tag_data = dict(scrap=tag_to,
                                        tag_text=tags_list[i])
                        tag_serializer = CreateTagSerializer(data=tag_data)
                        tag_serializer.is_valid(raise_exception=True)
                        tag = tag_serializer.save()

                return JsonResponse(
                    {
                        'message': 'SUCCESS',
                        'status': '200',
                        'scrap': ScrapSerializer(
                            scrap, context=self.get_serializer_context()
                        ).data
                    }
                )
        else:
            return JsonResponse(
                {
                    'message': 'CANNOT ACCESS',
                    'status': '403',
                    'scrap': {}
                }
            )


class CreateFolderAPI(generics.GenericAPIView):
    serializer_class = FolderRequestSerializer

    def post(self, request, *args, **kwargs):
        if not Folder.objects.filter(user=request.data['id'],
                                     folder_name=request.data['folder_name']).exists():
            folder_data = dict(user=request.data['id'],
                               folder_name=request.data['folder_name'])

            serializer = CreateFolderSerializer(data=folder_data)
            serializer.is_valid(raise_exception=True)
            folder = serializer.save()

            query = Folder.objects.filter(user=folder.user).order_by('folder_id')
            output_serializer = FolderSerializer(query, many=True)

            return JsonResponse(
                {
                    'message': 'SUCCESS',
                    'status': '200',
                    'folders': output_serializer.data
                }
            )
        else:
            return JsonResponse(
                {
                    'message': 'FOLDER NAME EXISTS',
                    'status': '403',
                    'folders': []
                })


class FolderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Folder.objects.all()
    serializer_class = UpdateFolderSerializer

    def delete(self, request, *args, **kwargs):
        obj = Folder.objects.get(folder_id=self.kwargs['pk'])

        scraps = Scrap.objects.filter(folder=obj.folder_id)
        new_folder = Folder.objects.get(user=self.kwargs['user'], folder_key=0)

        for scrap in scraps:
            scrap.folder = new_folder
            scrap.save()

        obj.delete()

        query = Folder.objects.filter(user=self.kwargs['user']).order_by('folder_id')
        output_serializer = FolderSerializer(query, many=True)

        return JsonResponse(
            {
                'folders': output_serializer.data
            },
            status=200
        )


class ScrapDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Scrap.objects.all()
    serializer_class = ScrapSerializer


class UpdateScrap(generics.RetrieveUpdateDestroyAPIView):
    queryset = Scrap.objects.all()
    serializer_class = UpdateScrapSerializer

    def update(self, request, *args, **kwargs):
        try:
            scrap = Scrap.objects.get(scrap_id=self.kwargs['pk'])
            serializer = UpdateScrapSerializer(scrap, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            update = serializer.save()

            return JsonResponse(
                {
                    'message': 'SUCCESS',
                    'status': '200',
                    'scrap': ScrapSerializer(
                        update, context=self.get_serializer_context()
                    ).data
                }
            )
        except ObjectDoesNotExist:
            return JsonResponse(
                {
                    'message': 'NOT EXISTS',
                    'status': '404',
                    'scrap': {}
                }
            )


class ReCrawling(generics.GenericAPIView):
    queryset = Scrap.objects.all()
    serializer_class = IdListSerializer

    def put(self, request):
        for element in request.data['id_list']:
            scrap = Scrap.objects.get(scrap_id=element['scrap_id'])

            response = requests.get(scrap.url)

            if response.status_code == 200:
                crawling = crawl_request(scrap.url)
                crawl_list = crawling[0:4]

                crawl_data = dict(scrap_id=scrap.scrap_id,
                                  url=crawl_list[0],
                                  thumbnail=crawl_list[2],
                                  domain=crawl_list[3])

                serializer = RecrawlingSerializer(scrap, data=crawl_data, partial=True)
                serializer.is_valid(raise_exception=True)
                update = serializer.save()

            else:
                scrap.delete()

        return JsonResponse({'status': 200})


class CreateTagAPI(generics.GenericAPIView):
    serializer_class = CreateTagSerializer

    def post(self, request, *args, **kwargs):
        serializer = CreateTagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tag = serializer.save()

        return JsonResponse(
            {
                'tag': TagSerializer(tag, context=self.get_serializer_context()
                                     ).data
            },
            status=200
        )


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserLocationAPI(generics.GenericAPIView):
    queryset = Place.objects.all()
    serializer_class = UserLocationSerializer

    def post(self, request, *args, **kwargs):
        places = Place.objects.filter(tag__scrap__folder__user=self.kwargs['pk'])

        latitude = float(request.data['latitude'])
        longitude = float(request.data['longitude'])

        scrap_list = []

        for place in places:
            distance = get_distance(latitude, longitude, place.latitude, place.longitude)
            if distance <= 1.0:
                scrap = Scrap.objects.get(scrap_id=place.tag.scrap.scrap_id)
                scrap_list.append(scrap)

        scrap_list = list(set(scrap_list))

        if len(scrap_list) == 0:
            return JsonResponse(
                {
                    'scrap': {}
                },
                status=204
            )

        elif len(scrap_list) == 1:
            return JsonResponse(
                {
                    'scrap': ScrapSerializer(
                        scrap_list[0], context=self.get_serializer_context()
                    ).data
                },
                status=200
            )

        else:
            i = random.randint(0, len(scrap_list)-1)
            return JsonResponse(
                {
                    'scrap': ScrapSerializer(
                        scrap_list[i], context=self.get_serializer_context()
                    ).data
                },
                status=200
            )


class UserFoodAPI(APIView):
    def get(self, request, *args, **kwargs):
        foods = Food.objects.filter(tag__scrap__folder__user=self.kwargs['pk'])

        scrap_list = []

        for food in foods:
            scrap = Scrap.objects.get(scrap_id=food.tag.scrap.scrap_id)
            scrap_list.append(scrap)

        scrap_list = list(set(scrap_list))

        if len(scrap_list) == 0:
            return JsonResponse(
                {
                    'scrap': {}
                },
                status=204
            )

        elif len(scrap_list) == 1:
            return JsonResponse(
                {
                    'scrap': ScrapSerializer(
                        scrap_list[0]
                    ).data
                },
                status=200
            )

        else:
            i = random.randint(0, len(scrap_list)-1)
            return JsonResponse(
                {
                    'scrap': ScrapSerializer(
                        scrap_list[i]
                    ).data
                },
                status=200
            )