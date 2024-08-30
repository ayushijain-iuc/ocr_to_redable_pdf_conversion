from django.contrib import admin
from django.urls import path,include
from.views import OCRView


urlpatterns = [
    path('ocr/',OCRView.as_view()),
]