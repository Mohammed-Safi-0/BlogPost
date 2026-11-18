from django.contrib import admin
from django.urls import path
from posts import views as views 


urlpatterns = [
    path('',views.home, name='home'),
    path('blogposts',views.blogposts, name='blogposts'),
    path('create',views.create, name='create'),
    path('edit/<int:pk>',views.edit, name='edit'),
    path('delete/<int:pk>',views.delete, name='delete'),
    path('details/<int:pk>',views.details, name='details'),
    path('search', views.search, name='search'),
    path('react/<int:pk>', views.react, name='react'),
    path('report/<int:pk>', views.report_post, name='report_post'),
    path('comment/<int:pk>', views.add_comment, name='add_comment'),              
    path('comment/delete/<int:comment_id>', views.delete_comment, name='delete_comment'),
    path('manage-users', views.manage_users, name='manage_users'),
    path('manage-users/toggle/<int:user_id>', views.toggle_user_active, name='toggle_user_active'),
    path('manage-users/delete/<int:user_id>', views.delete_user, name='delete_user'),
    path("posts/<int:post_id>/summarize/", views.summarize_post, name="summarize_post"),
    path('video/<path:path>',views.stream_video,name='stream_video'),
]
