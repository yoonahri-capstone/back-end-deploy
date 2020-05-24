from django.urls import path, include
from .views import MyUserViewSet
from .views import RegistrationAPI
from .views import LoginAPI

from .views import FolderViewSet
from .views import FolderScrapsViewSet
#from .views import DefaultFolderScrapsViewSet

from .views import CreateFolderAPI
from .views import CreateMenuFolderAPI
from .views import FolderDetail

from .views import ScrapAllViewSet
#from .views import ScrapViewSet
from .views import CreateScrapAPI
from .views import ScrapDetail
from .views import UpdateScrap

from .views import TagDetail

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
    path('users/<int:pk>/listall/', user_scraps, name="user_scraps"),

    path('addmenufolder/', CreateMenuFolderAPI.as_view()),
    path('addfolder/', CreateFolderAPI.as_view()),
    path('addscrap/', CreateScrapAPI.as_view()),
    path('scrap/<int:pk>/', ScrapDetail.as_view()),
    path('updatescrap/<int:pk>/', UpdateScrap.as_view()), #임시 update
    path('tag/<int:pk>/', TagDetail.as_view()),

    path('', include('rest_framework.urls', namespace='rest_framework_category')),
 ]
