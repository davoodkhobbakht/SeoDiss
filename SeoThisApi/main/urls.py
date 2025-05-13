from django.urls import path
from .views import GenerateArticleAPIView, GenerateQnRAPIView, GenerateKeywordsAPIView, GenerateToneAPIView

urlpatterns = [
    path("generate-article/", GenerateArticleAPIView.as_view()),
    path("generate-qnr/", GenerateQnRAPIView.as_view()),
    path("generate-keywords/", GenerateKeywordsAPIView.as_view()),
    path("generate-tone/", GenerateToneAPIView.as_view()),
]
