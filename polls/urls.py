from django.urls import path

from polls import views
app_name = "polls"
urlpatterns = [
    path('', views.index_view, name='index'),
    path('add/', views.add_question, name='add_question'),
    path('delete_selected/', views.delete_selected_polls, name='delete_selected'),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:question_id>/results/", views.results, name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]