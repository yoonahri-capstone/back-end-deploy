from django.urls import path, include
from .views import MyUserViewSet
from .views import RegistrationAPI
from .views import LoginAPI

from .views import FolderViewSet
from .views import FolderScrapsViewSet
#from .views import DefaultFolderScrapsViewSet

from .views import CreateFolderAPI
from .views import FolderDetail

from .views import ScrapAllViewSet
from .views import CheckScrapAPI
#from .views import ScrapViewSet
from .views import CreateScrapAPI
from .views import ScrapDetail
from .views import UpdateScrap
from .views import ReCrawling

from .views import CreateTagAPI
from .views import TagDetail

from .views import UserLocationAPI
from .views import UserFoodAPI

from .views import FindLocationAPI
from .views import FindFoodAPI

from .views import SearchUserAPI
from .views import CreateSharingAPI
from .views import JoinSharingAPI
from .views import SharingListViewSet
from .views import SharingViewSet

app_name = 'memmem_app'

# 막판에 깔끔하게 정리
user_list = MyUserViewSet.as_view({"get": "list"})
user_detail = MyUserViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)
user_folders = FolderViewSet.as_view({"get":"list"})
folder_scraps = FolderScrapsViewSet.as_view({"get":"list"})
#default_folder_scraps = DefaultFolderScrapsViewSet.as_view({"get": "list"})
user_scraps = ScrapAllViewSet.as_view({"get":"list"})
#scrap_detail = ScrapViewSet.as_view({"get": "retrieve", "patch": "partial_update"}) # 수정 필요

sharings = SharingViewSet.as_view({"get":"list"})
sharing_list = SharingListViewSet.as_view({"get":"list"})

urlpatterns = [
    path('auth/register/', RegistrationAPI.as_view()),
    path('auth/login/', LoginAPI.as_view()),
    #path('auth/user/', UserAPI.as_view()),

    path('users/', user_list),
    path('users/<int:pk>/', user_detail, name="note-detail"),
    path('users/<int:pk>/folders/', user_folders),
    #path('users/<int:pk>/folders/<int:folder_key>/', folder_scraps, name="folder_scraps"),
    path('users/<int:user>/folders/<int:pk>/', FolderDetail.as_view()),
    path('users/<int:pk>/folders/<int:folder_id>/listall/', folder_scraps, name="folder_scraps"),
    path('users/<int:pk>/sharings/', sharings),
    path('users/<int:pk>/listall/', user_scraps, name="user_scraps"),
    path('users/<int:pk>/checkall/', CheckScrapAPI.as_view()),

    path('addfolder/', CreateFolderAPI.as_view()),
    path('addscrap/', CreateScrapAPI.as_view()),
    path('addtag/', CreateTagAPI.as_view()),
    path('scrap/<int:pk>/', ScrapDetail.as_view()),
    path('updatescrap/<int:pk>/', UpdateScrap.as_view()),
    path('recrawling/', ReCrawling.as_view()),
    path('tag/<int:pk>/', TagDetail.as_view()),

    path('location/user/<int:pk>/', UserLocationAPI.as_view()),
    path('food/user/<int:pk>/', UserFoodAPI.as_view()),

    path('findlocation/user/<int:pk>/', FindLocationAPI.as_view()),
    path('findfood/user/<int:pk>/', FindFoodAPI.as_view()),

    path('search/', SearchUserAPI.as_view()),
    path('addsharing/', CreateSharingAPI.as_view()),
    path('users/<int:pk>/joinsharing/', JoinSharingAPI.as_view()),
    path('users/<int:pk>/sharinglist/', sharing_list),

    path('', include('rest_framework.urls', namespace='rest_framework_category')),
 ]