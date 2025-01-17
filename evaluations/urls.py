from django.urls import path, include
from . import views

#API
from rest_framework.routers import DefaultRouter
from .views_api  import CourseViewSet, OptionViewSet, QuestionViewSet, EvaluationViewSet, AnswerViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'options', OptionViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'evaluations', EvaluationViewSet)
router.register(r'answers', AnswerViewSet)

#Urls http

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('questions/', views.QuestionListView.as_view(), name='question_list'),
    path('evaluations/', views.EvaluationListView.as_view(), name='evaluation_list'),
    path('take_evaluation/<int:pk>/', views.take_evaluation, name='take_evaluation'),
    path('evaluation_result/<int:pk>/', views.evaluation_result, name='evaluation_result'),
    path('view-answers/', views.view_answers, name='view_answers'),

    path('error/', views.error_view, name='error_view'),  # Define la URL y asigna un nombre a la vista

    #path('accounts/', include('django.contrib.auth.urls')),
    #path('register/', views.register, name='register'),
    #API
    path('restful/', include(router.urls)),
    path('qr_login/', views.qr_login, name='qr_login'),
    path('log_evaluation_event/', views.log_evaluation_event, name='log_evaluation_event'),
]
