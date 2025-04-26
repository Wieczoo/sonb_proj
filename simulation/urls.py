
from django.urls import path
from .views import (crc_view, test_crc_page,test_node_page,
                    test_master_page,simulate_transmission_view, test_simulation_page,create_node,get_all_nodes,ensure_ten_online_nodes,shutdown_master,shutdown_node)

urlpatterns = [
    path('crc/', crc_view, name='crc_view'),
    path('test/', test_crc_page, name='test_crc_page'),
    path('test/node/', test_node_page, name='test_node_page'),
    path('test/master/', test_master_page, name='test_master_page'),
    path('simulate/', simulate_transmission_view, name='simulate_transmission'),
    path('test/simulate/', test_simulation_page, name='test_simulation_page'),
    path('nodes/', get_all_nodes, name='get_all_nodes'),
    path('nodes/create/', create_node, name='create_node'),
    path('nodes/ensure_ten_online/', ensure_ten_online_nodes, name='ensure_ten_online_nodes'),
    path('shutdown_master/', shutdown_master, name='shutdown_master'),
    path('shutdown_node/', shutdown_node, name='shutdown_node'),

]
