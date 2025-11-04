from django.urls import path
from polls import views

app_name = "polls"

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('context/', views.show_context, name='show_context'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
    path('viewpolls/', views.index_view, name='index'),
    path('add/', views.add_question, name='add_question'),
    path('delete_selected/', views.delete_selected_polls, name='delete_selected'),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:question_id>/voters/", views.show_voters, name="show_users"),
    path("<int:question_id>/results/", views.results, name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
