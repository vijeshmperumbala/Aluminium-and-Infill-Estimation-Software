"""amoeba URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
# from debug_toolbar.toolbar import debug_toolbar_urls


urlpatterns = [
    path('ameba_admin_page/', admin.site.urls),

    path('', include('apps.user.urls')),
    path('auth/', include('apps.auth_user.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    
    # UoM app urls
    path('UoM_master/', include('apps.UoM.urls')),
    # Category app url
    path('Categories_master/', include('apps.Categories.urls')),
    # Product Master app urls
    path('Products_master/', include('apps.product_master.urls')),
    # Brands app url
    path('Brands/', include('apps.brands.urls')),
    # Accessories app url
    path('Accessories/', include('apps.accessories_master.urls')),
    # Accessories kit app url
    path('Accessories_kit/', include('apps.accessories_kit.urls')),
    # Configuration app url
    path('Configuration/', include('apps.configuration_master.urls')),
    # Panels_and_others app urls
    path('Panels_and_others/', include('apps.panels_and_others.urls')),
    #  Addons app url
    path('Addons/', include('apps.addon_master.urls')),
    # Pricing app urls
    path('Pricing_Master/', include('apps.pricing_master.urls')),
    # Settings app urls
    path('Designations/', include('apps.designations.urls')),
    # Customers app urls
    path('Customers/', include('apps.customers.urls')),
    # Enquiries app url
    path('Enquiries/', include('apps.enquiries.urls')),
    # Estimation app url
    path('Estimation/', include('apps.estimations.urls')),
    # Signature app url
    path('Signatures/', include('apps.signatures.urls')),
    # Project app url
    path('Project/', include('apps.projects.urls')),
    # Suppliers app url
    path('Suppliers/', include('apps.suppliers.urls')),
    # Enquiry Type app url
    path('Enquiry_Types/', include('apps.enquiry_type.urls')),
    # Industry Type app url
    path('Industry_Types/', include('apps.industry_type.urls')),
    # Surface Finish app url
    path('Surface_Finish/', include('apps.surface_finish.urls')),
    # Sealant_Types app url 
    path('Sealant_Types/', include('apps.sealant_types.urls')),
    # Provisional app url
    path('Provisionals/', include('apps.provisions.urls')),
    # Quotation app url
    path('Quotations_Templates/', include('apps.quotations_master.urls')),
    # Invoice Settings app url
    path('Invoice_Settings/', include('apps.invoice_settings.urls')),
    # Company Settings app url
    path('Companies/', include('apps.companies.urls')),
    # Profiles Settings app url
    path('Profiles/', include('apps.profiles.urls')),
    # Prats Settings app url
    path('Parts/', include('apps.product_parts.urls')),
    # Profile Type app url
    path('Profile_Types/', include('apps.profile_types.urls')),
    # Cover Cap and Pressure Plates
    path('CoverCap_and_PressurePlates/', include('apps.cover_cap.urls')),
    # Tags app urls
    # path('Tags/', include('apps.tags.urls')),
    # Associated Product Master urls
    path('Associated_Products/', include('apps.associated_product.urls')),
    # Shopfloor apps urls
    path('ShopFloors/', include('apps.shopfloors.urls')),
    # Worksattion Urls
    path('Workstations/', include('apps.Workstations.urls')),
    # FileManager
    path('FileManager/', include('apps.file_manager.urls')),
    # ProhjectSpecifications
    path('Project_Specifications/', include('apps.project_specifications.urls')),
    path('vehicles_and_drivers/', include('apps.vehicles_and_drivers.urls')),
    # Rating Head 
    path('rating/', include('apps.rating.urls')),
    # Others 
    path('others/', include('apps.others.urls')),
    
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)