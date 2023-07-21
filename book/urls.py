
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import *


schema_view = get_schema_view(
    openapi.Info(
        title="Generateur d'histoire : Programme Backend",
        default_version='v1',
        description="Cette application est le générateur d'histoire coté backend",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="nganefabrice693@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # API URLs
    path('book', WriteBook.as_view()),
    #path('image', GenerateImageMidjourney.as_view()),
    path('image', GetWordToPicture.as_view()),
    path('image/generate', GetWordToPictureGenerate.as_view()),

    # Swagger documentation URLs
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]
