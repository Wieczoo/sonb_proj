
from django.urls import path
from .views import crc_view, test_crc_page,test_node_page, test_master_page

urlpatterns = [
    path('crc/', crc_view, name='crc_view'),
    path('test/', test_crc_page, name='test_crc_page'),
    path('test/node/', test_node_page, name='test_node_page'),
    path('test/master/', test_master_page, name='test_master_page'),
]
