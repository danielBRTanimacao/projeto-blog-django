from django.urls import path
from blog import views, post, page

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('post/', post, name='post'),
    path('page/', page, name='page'),
]
