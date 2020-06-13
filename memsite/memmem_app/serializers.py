from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Client
from .models import Folder
from .models import Scrap
from .models import Memo
from .models import Tag
from .models import Place
from .models import Food


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class LoginDataSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    token = serializers.CharField()


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in")


# Folder
class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        #fields = ('folder_key', 'folder_name')
        fields = ('folder_id', 'folder_key', 'folder_name')


class FolderRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    folder_name = serializers.CharField()


# Create Folder
class CreateFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ('user', 'folder_name')

    def create(self, validated_data):
        return Folder.objects.create(**validated_data)


# Update Folder
class UpdateFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ('folder_id', 'folder_name')


# User's Folder List
class UserFolderSerializer(serializers.ModelSerializer):
    folders = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'folders')

    def get_folders(self, instance):
        folder = instance.folders.all()
        return FolderSerializer(folder, many=True).data


# Scrap List (in Folder)
class ScrapListSerializer(serializers.ModelSerializer):
    scraps = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        #fields = ('folder_key', 'folder_name', 'scraps')
        fields = ('folder_id', 'folder_name', 'scraps')

    def get_scraps(self, instance):
        scrap = instance.scraps.all().order_by('-scrap_id')
        return ScrapSerializer(scrap, many=True).data

'''
# Scrap List (in Default Folder)
class DefaultScrapListSerializer(serializers.ModelSerializer):
    list_all = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ('folder_key', 'folder_name', 'list_all')

    def get_list_all(self, instance):
        scrap = instance.list_all.all()
        return ScrapSerializer(scrap, many=True).data
'''


class MemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Memo
        fields = ('memo',)


class CreateMemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Memo
        fields = ('scrap',
                  'memo')

    def create(self, validated_data):
        return Memo.objects.create(**validated_data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tag_text',)
        #fields = ('tag_id', 'tag_text')


class CreateTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields=('scrap',
                'tag_text')

    def create(self, validated_data):
        return Tag.objects.create(**validated_data)


# scrap 1개 세부정보
class ScrapSerializer(serializers.ModelSerializer):
    memos = MemoSerializer(many=True)
    #tags = serializers.SerializerMethodField()
    #memos = CreateMemoSerializer(read_only=True, many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Scrap
        fields = ('scrap_id',
                  'folder',
                  'title',
                  'url',
                  'date',
                  'thumbnail',
                  'domain',
                  'memos',
                  'tags',
                  )

    def get_memos(self, instance):
        memo = instance.memos.all()
        return MemoSerializer(memo, many=True).data

    def get_tags(self, instance):
        tag = instance.tags.all()
        return TagSerializer(tag, many=True).data


class UpdateScrapSerializer(serializers.ModelSerializer):
    memos = MemoSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Scrap
        fields = ('scrap_id',
                  'folder',
                  'title',
                  'memos',
                  'tags',
                  )

    def get_memos(self, instance):
        memo = instance.memos.all()
        return MemoSerializer(memo, many=True).data

    def get_tags(self, instance):
        tag = instance.tags.all()
        return TagSerializer(tag, many=True).data

    def update(self, instance, validated_data):
        # get memo list
        memo_dict_list = validated_data.pop('memos')
        memo_list = []
        for i in range(0, len(memo_dict_list)):
            memo_list.append(memo_dict_list[i].get('memo'))

        # get tag list
        tag_dict_list = validated_data.pop('tags')
        text_list = []
        for i in range(0, len(tag_dict_list)):
            text_list.append(tag_dict_list[i].get('tag_text'))

        # scrap update info
        scrap_id = validated_data.get('scrap_id', instance.scrap_id)
        instance.scrap_id = scrap_id
        instance.folder = validated_data.get('folder', instance.folder)
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        # add memo
        for i in range(0, len(memo_dict_list)):
            memo = memo_list[i]

            if not Memo.objects.filter(scrap=scrap_id, memo=memo).exists():
                memo_data = dict(scrap=scrap_id,
                                 memo=memo)
                memo_serializer = CreateMemoSerializer(data=memo_data)
                memo_serializer.is_valid(raise_exception=True)
                memo_serializer.save()

        # delete memo
        for i in Memo.objects.filter(scrap=scrap_id):
            if i.memo not in memo_list:
                i.delete()

        # add tag
        for i in range(0, len(tag_dict_list)):
            tag_text = text_list[i]

            if not Tag.objects.filter(scrap=scrap_id, tag_text=tag_text).exists():
                tag_data = dict(scrap=scrap_id,
                                tag_text=tag_text)
                tag_serializer = CreateTagSerializer(data=tag_data)
                tag_serializer.is_valid(raise_exception=True)
                tag_serializer.save()

        # delete tag
        for i in Tag.objects.filter(scrap=scrap_id):
            if i.tag_text not in text_list:
                i.delete()

        return instance


class UrlRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    #folder_key = serializers.IntegerField()
    folder_id = serializers.IntegerField()
    url = serializers.CharField()


class CreateScrapSerializer(serializers.ModelSerializer):
    memos = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Scrap
        fields = ('folder',
                  'url',
                  'title',
                  'thumbnail',
                  'domain',
                  'memos',
                  'tags')

    def create(self, validated_data):
        return Scrap.objects.create(**validated_data)

    def get_memos(self, instance):
        memo = instance.memos.all()
        return MemoSerializer(memo, many=True).data

    def get_tags(self, instance):
        tag = instance.tags.all()
        return TagSerializer(tag, many=True).data


class AlarmPlaceSerializer(serializers.ModelSerializer):
    memos = MemoSerializer(many=True)
    tags = serializers.SerializerMethodField('get_tags')

    class Meta:
        model = Scrap
        fields = ('scrap_id',
                  'folder',
                  'title',
                  'url',
                  'date',
                  'thumbnail',
                  'domain',
                  'memos',
                  'tags',
                  )

    def get_memos(self, instance):
        memo = instance.memos.all()
        return MemoSerializer(memo, many=True).data

    def get_tags(self, instance):
        places = Place.objects.filter(tag__scrap=instance).values_list('tag', flat=True)
        tags = Tag.objects.none()
        for i in range(len(places)):
            tags |= Tag.objects.filter(tag_id=places[i])
        return TagSerializer(tags, many=True).data


class AlarmFoodSerializer(serializers.ModelSerializer):
    memos = MemoSerializer(many=True)
    tags = serializers.SerializerMethodField('get_tags')

    class Meta:
        model = Scrap
        fields = ('scrap_id',
                  'folder',
                  'title',
                  'url',
                  'date',
                  'thumbnail',
                  'domain',
                  'memos',
                  'tags',
                  )

    def get_memos(self, instance):
        memo = instance.memos.all()
        return MemoSerializer(memo, many=True).data

    def get_tags(self, instance):
        foods = Food.objects.filter(tag__scrap=instance).values_list('tag', flat=True)
        tags = Tag.objects.none()
        for i in range(len(foods)):
            tags |= Tag.objects.filter(tag_id=foods[i])
        return TagSerializer(tags, many=True).data


class IdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrap
        fields = ('scrap_id',)


class IdListSerializer(serializers.Serializer):
    id_list = IdSerializer(many=True)


class RecrawlingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrap
        fields = ('scrap_id',
                  'url',
                  'thumbnail',
                  'domain'
                  )


class UserLocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


class CreateSharingSerializer(serializers.Serializer):
    sharing_name = serializers.CharField()
    users = UsernameSerializer(many=True)


class JoinSharingSerializer(serializers.ModelSerializer):
    sharing_name = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ('sharing_name',)


class SharingSerializer(serializers.ModelSerializer):
    sharing_name = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ('id',
                  'sharing_name')
