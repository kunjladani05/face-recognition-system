from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('', HomePage, name='home'),
    path('signup/', SignupPage, name='signup'),
    path('login/', LoginPage, name='login'),
    path('logout/', LogoutPage, name='logout'),
    path('dashboard/', Dashboard, name='dashboard'),
    path('user_details/', UserDetailsPage, name='user_details'),
    path('update_user/<int:user_id>/', UpdateUser, name='update_user'),
    path('delete_user/<int:user_id>/', DeleteUser, name='delete_user'),
    path('upload_photo/', UploadPhoto, name='upload_photo'),
    path('live_recognition/', LiveRecognition, name='live_recognition'),
    path('create/', create_profile, name='create_profile'),
    path('list/', ProfileListView.as_view(), name='profile_list'),
    path('profile/<int:pk>/images/', ProfileImagesView.as_view(), name='profile_images'),
    path('delete-profile/<int:pk>/', ProfileDeleteView.as_view(), name='delete_profile'),
    path('imagePreview/', imagePreview, name='imagePreview')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)