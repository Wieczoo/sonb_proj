
from django.urls import path
from .views import crc_view, test_crc_page

urlpatterns = [
    path('crc/', crc_view, name='crc_view'),
    path('test/', test_crc_page, name='test_crc_page'),
]
