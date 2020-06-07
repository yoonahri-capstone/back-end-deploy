from django.db import models
from django.contrib.auth.models import User
from .hashtag_classification import tag_classifier

'''
class MyUserManager(BaseUserManager):
    def create_user(self, name, email, password=None):
        """
        Creates and saves a User with the given name, email
        and password.
        """

        if not name:
            raise ValueError('User must have a name')
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=self.name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    name = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='user name')
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True
    )

    objects = MyUserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


    #USERNAME_FIELD = 'name' #unique=True
'''


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to='memmem_app/media')
    # image 형식 미정


class Folder(models.Model):
    folder_id = models.AutoField(primary_key=True)
    folder_key = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='folders')
    folder_name = models.CharField(max_length=50,
                                   blank=False,
                                   default='default folder')

    def __str__(self):
        return self.folder_name

    def create(self, validated_data):
        return Folder.objects.create(**validated_data)

    def save(self, *args, **kwargs):
        key = 0
        if not Folder.objects.filter(folder_id=self.folder_id).exists():
            present_keys = Folder.objects.filter(user=self.user).order_by('-folder_key').values_list('folder_key',
                                                                                                     flat=True)
            if present_keys:
                key = present_keys[0] + 1
            self.folder_key = key
        super(Folder, self).save(*args, **kwargs)


class Scrap(models.Model):
    scrap_id = models.AutoField(primary_key=True)
    folder = models.ForeignKey(Folder,
                               on_delete=models.CASCADE,
                               related_name='scraps')
    # default_folder = models.ForeignKey(Folder,
    #                                   on_delete=models.CASCADE,
    #                                   related_name='list_all')
    title = models.TextField()  # char->text 바꿈
    url = models.URLField(null=False)
    date = models.DateTimeField(auto_now_add=True,
                                auto_now=False)
    thumbnail = models.TextField(null=True)  # char->text 바꿈
    domain = models.CharField(max_length=50)

    def __str__(self):
        return self.url

    def create(self, validated_data):
        return Scrap.objects.create(**validated_data)

    def get_id(self):
        return self.scrap_id


class Memo(models.Model):
    memo_id = models.AutoField(primary_key=True)
    scrap = models.ForeignKey(Scrap,
                              on_delete=models.CASCADE,
                              related_name='memos')
    memo = models.TextField(null=True)

    def __str__(self):
        return self.memo

    def create(self, validated_data):
        return Memo.objects.create(**validated_data)


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    scrap = models.ForeignKey(Scrap,
                              on_delete=models.CASCADE,
                              related_name="tags")
    tag_text = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.tag_text

    def create(self, validated_data):
        return Tag.objects.create(**validated_data)

    def save(self, *args, **kwargs):
        super(Tag, self).save(*args, **kwargs)

        tag_text = self.tag_text.replace("#", "")
        classifier = tag_classifier(tag_text)

        if classifier is None:
            pass
        elif len(classifier) == 2:
            if classifier[1] is None:
                pass
            else:
                name = classifier[0]
                latitude = classifier[1][0]
                longitude = classifier[1][1]
                Place.objects.create(name=name,
                                     latitude=latitude,
                                     longitude=longitude,
                                     tag=self)
        elif len(classifier) == 1:
            Food.objects.create(tag=self)
        else:
            print('err')


class Place(models.Model):
    place_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            related_name="places")

    def __str__(self):
        return self.name

    def create(self, validated_data):
        return Place.objects.create(**validated_data)


class Food(models.Model):
    food_id = models.AutoField(primary_key=True)
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            related_name="food")

    def __str__(self):
        return self.tag.tag_text

    def create(self, validated_data):
        return Food.objects.create(**validated_data)


class Group(models.Model):
    group_id = models.AutoField(primary_key=True)
    sharing = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name="sharings")
    member = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="members")

    def __str__(self):
        group = self.sharing.username + ', ' + self.member.username
        return group

    def create(self, validated_data):
        return Group.objects.create(**validated_data)
