from django.urls import path

from apps.product_master import views


urlpatterns = [
    path('products_list/', views.products_list, name="products_list"),
    path('products_add/<int:pk>/', views.products_create, name="products_create"),
    path('products_add2/<int:pk>/', views.products_add, name="products_add"),
    path('products_edit/<int:pk>/', views.products_edit, name="products_edit"),
    path('category_wise_products/<int:pk>/', views.category_wise_products, name="category_wise_products"),
    path('product_delete/<int:pk>/', views.product_delete, name="product_delete"),
    path('product_profile/<int:pk>/', views.product_profile, name="product_profile"),
    path('products_edit_profile/<int:pk>/', views.products_edit_profile, name="products_edit_profile"),
    path('create_product_accessory/<int:pk>/', views.create_product_accessory, name="create_product_accessory"),
    path('edit_product_accessory/<int:pk>/', views.edit_product_accessory, name="edit_product_accessory"),
    path('delete_product_accessories/<int:pk>/', views.delete_product_accessories, name="delete_product_accessories"),
    path('list_secondary_products/', views.list_secondary_products, name="list_secondary_products"),
    path('secondary_products_add/', views.secondary_products_add, name="secondary_products_add"),
    path('secondary_products_update/<int:pk>/', views.secondary_products_update, name="secondary_products_update"),
    path('secondary_product_delete/<int:pk>/', views.secondary_product_delete, name="secondary_product_delete"),
    
    # AJAX URL
    path('get_kit_data/<int:pk>/', views.get_kit_data, name="get_kit_data"),
    path('delete_accessory_from_bundle/<int:pk>/', views.delete_accessory_from_bundle, name="delete_accessory_from_bundle"),
]
