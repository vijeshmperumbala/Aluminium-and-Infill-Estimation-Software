from django.urls import path
from apps.file_manager import views
from django.urls import re_path as url

urlpatterns = [
    path('file_manager/', views.file_manager, name="file_manager"),
    # path('list_files/<str:path>/', views.list_files, name="list_files"),
    # path('list_files/<path:parent_path>/<path:path>/', views.list_files, name="list_files"),
    # path('invoice_settings_delete/<int:pk>/', views.invoice_settings_delete, name="invoice_settings_delete"),
    

    url(r'^list_files/(?P<parent_path>[^/]+|[^-]+)/(?P<path>[^/]+|[^-]+)/$',views.list_files, name='list_files'),
    url(r'^list_files/(?P<path>[^/]+|[^-]+)/$',views.list_files, name='list_files'),
    
    url(r'^folder_downloader/(?P<path>[^/]+|[^-]+)/(?P<parent_path>[^/]+|[^-]+)/(?P<filename>[^/]+|[^-]+)/$',views.folder_downloader, name='folder_downloader'),
    url(r'^file_download/(?P<path>[^/]+|[^-]+)/(?P<filename>[^/]+|[^-]+)/$',views.file_download, name='file_download'),
    
    url(r'^delete_file/(?P<path>[^/]+|[^-]+)/(?P<filename>[^/]+|[^-]+)/$',views.delete_file, name='delete_file'),
    
    # url(r'^folder_downloader/(?P<path>[^/]+|[^-]+)/$',views.folder_downloader, name='folder_downloader'),
    # url(r'^user_report/(?P<user>\d+)/(?P<date>\d{4}-\d{1,2}-\d{1,2})/$',views.user_report, name='user_report'),
    
    path('file_tree/', views.file_tree, name="file_tree"),
    path('open_file/', views.open_file, name="open_file"),
    # url(r'^file_tree/(?P<parent>[^/]+|[^-]+)/$',views.file_tree, name='file_tree'),
    
    
]
