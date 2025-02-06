from django.urls import path
from .views import *

urlpatterns = [
    path('login/', loginPage, name='login_page'),
    path('register/', registerPage, name='register_page'),
    path('logout/', logoutUser, name='logout_user'),
    
    path('', home, name='home'),
    path('rooms/<str:pk>', room, name='room_page'),
    path('create-room/', createRoom, name='create_room'),
    path('update-room/<str:pk>', updateRoom, name='update_room'),
    path('delete-room/<str:pk>', deleteRoom, name='delete_room'),
]
