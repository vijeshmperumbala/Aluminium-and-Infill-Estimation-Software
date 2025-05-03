import io
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.utils.timezone import now as time
from django.template.loader import get_template
from amoeba.local_settings import STATIC_URL

from apps.accessories_kit.models import AccessoriesKit
from apps.brands.models import CategoryBrands
from apps.Categories.models import Category
from apps.profile_types.models import Profile_Types
from apps.profiles.forms import (
            CreateProfileForm, 
            CreateProfileMasterSeries, 
            CreateProfileMasterType,
)
from apps.profiles.models import (
            ProfileMasterSeries, 
            ProfileMasterType, 
            Profiles,
)
from apps.estimations.taskes import addons_data_export_shared, aluminium_data_export_shared

from xlsxwriter.workbook import Workbook
from wkhtmltopdf.views import PDFTemplateResponse
from amoeba.settings import MEDIA_URL, PROJECT_NAME


@login_required(login_url='signin')
@permission_required(['profiles.view_profiles'], login_url='permission_not_allowed')
def list_profiles_data(request):
    """
    This function retrieves categories data for profiles and renders it in a template.
    
    """
    categories_obj = Category.objects.filter(
        Q(one_D=True) | (Q(one_D=True) & Q(two_D=True))).order_by('id')

    context = {
        "title": f'{PROJECT_NAME} | Profiles List.',
        "categories_obj": categories_obj,
    }
    return render(request, "Master_settings/Profiles/profile_base.html", context)


@login_required(login_url='signin')
@permission_required(['profiles.view_profiles'], login_url='permission_not_allowed')
def profile_brands(request, cat_id):
    """
    This function retrieves a list of brands belonging to a specific category and renders them on a web
    page.
    
    """
    categories_obj = Category.objects.filter(
        Q(one_D=True) | (Q(one_D=True) & Q(two_D=True))).order_by('id')
    category = categories_obj.get(pk=cat_id)
    brands = CategoryBrands.objects.filter(category=cat_id).order_by('id')

    context = {
        "title": f'{PROJECT_NAME} | Profiles List',
        "categories_obj": categories_obj,
        "brands": brands,
        "category": category,
    }
    return render(request, "Master_settings/Profiles/profile_base.html", context)

@login_required(login_url='signin')
def list_profile_master_type(request, pk):
    """
    This function retrieves and displays a list of profile master types for a specific category brand.
    
    """
    brand = CategoryBrands.objects.get(pk=pk)
    profile_master_types = ProfileMasterType.objects.filter(profile_master_brand=brand).order_by('id')
    categories_obj = Category.objects.filter(Q(one_D=True) | (Q(one_D=True) & Q(two_D=True))).order_by('id')
    category = categories_obj.get(pk=brand.category.id)
    brands = CategoryBrands.objects.filter(category=brand.category.id).order_by('id')
    
    context = {
        "title": f'{PROJECT_NAME} | Profiles List',
        "categories_obj": categories_obj,
        "brands": brands,
        "category": category,
        "brand": brand,
        "profile_master_types": profile_master_types,
    }
    return render(request, "Master_settings/Profiles/profile_base.html", context)

@login_required(login_url='signin')
def create_profile_type(request, pk):
    """
    This function creates a profile master type object associated with a specific category brand and
    saves it to the database.
    
    """
    brand = CategoryBrands.objects.get(pk=pk)
    form = CreateProfileMasterType()
    if request.method == 'POST':
        form = CreateProfileMasterType(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.profile_master_category = brand.category
            form_obj.profile_master_brand = brand
            form_obj.save()
        else:
            messages.error(request, "Please Check all Fields..")
        return redirect('list_profile_master_type', pk=brand.id)
    context = {
        "form": form,
        "brand": brand
    }
    return render(request, "Master_settings/Profiles/add_profile_master_type.html", context)

@login_required(login_url='signin')
def delete_profile_type(request, pk):
    """
    This function deletes a profile type and displays a success or error message depending on whether
    the deletion was successful or not.
    """
    item = ProfileMasterType.objects.get(pk=pk)
    if request.method == "POST":
        try:
            item.delete()
            messages.success(
                request,
                f"Profile Type {item.profile_master_type.profile_type} Deleted Successfully",
            )
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.", e)
        return redirect('list_profile_master_type', pk=item.profile_master_brand.id)

    context = {"url": f"/Profiles/delete_profile_type/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)

@login_required(login_url='signin')
def list_profile_master_series(request, pk):
    """
    This function retrieves and displays a list of profile series based on the selected profile master
    type.
    
    """
    profile_master_type = ProfileMasterType.objects.get(pk=pk)
    profile_seriess = ProfileMasterSeries.objects.filter(profile_master_type=profile_master_type).order_by('id')
    brand = CategoryBrands.objects.get(pk=profile_master_type.profile_master_brand.id)
    profile_master_types = ProfileMasterType.objects.filter(profile_master_brand=brand).order_by('id')
    categories_obj = Category.objects.filter(Q(one_D=True) | (Q(one_D=True) & Q(two_D=True))).order_by('id')
    category = categories_obj.get(pk=brand.category.id)
    brands = CategoryBrands.objects.filter(category=brand.category.id).order_by('id')

    context = {
        "title": f'{PROJECT_NAME} | Profiles List',
        "categories_obj": categories_obj,
        "brands": brands,
        "category": category,
        "brand": brand,
        "profile_master_types": profile_master_types,
        "profile_master_type": profile_master_type,
        "profile_seriess": profile_seriess,
    }
    return render(request, "Master_settings/Profiles/profile_base.html", context)


@login_required(login_url='signin')
def create_profile_master_series(request, pk):
    """
    This function creates a new profile master series object associated with a specific profile master
    type object and saves it to the database.
    
    """
    profile_master_type = ProfileMasterType.objects.get(pk=pk)
    form = CreateProfileMasterSeries()
    if request.method == 'POST':
        form = CreateProfileMasterSeries(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.profile_master_type = profile_master_type
            form_obj.save()
        else:
            messages.error(request, "Please Check all Fields..")
        return redirect('list_profile_master_series', pk=profile_master_type.id)
    context = {
        "form": form,
        "profile_master_type": profile_master_type
    }
    return render(request, "Master_settings/Profiles/add_profile_master_series.html", context)


@login_required(login_url='signin')
def delete_profile_series(request, pk):
    """
    This function deletes a profile series object and displays a success or error message depending on
    whether the deletion was successful or not.
    
    """
    item = ProfileMasterSeries.objects.get(pk=pk)
    if request.method == "POST":
        try:
            item.delete()
            messages.success(
                request,
                f"Profile Series {item.profile_master_series} Deleted Successfully",
            )

        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_profile_master_series', pk=item.profile_master_type.id)

    context = {"url": f"/Profiles/delete_profile_series/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
@permission_required(['profiles.view_profiles'], login_url='permission_not_allowed')
def list_profile_items(request, pk):
    """
    This function retrieves and organizes data related to profile items for display on a web page.
    
    """
    profile_series = ProfileMasterSeries.objects.get(pk=pk)
    profile_master_type = ProfileMasterType.objects.get(pk=profile_series.profile_master_type.id)
    profile_seriess = ProfileMasterSeries.objects.filter(profile_master_type=profile_master_type).order_by('id')
    profile_master_types = ProfileMasterType.objects.filter(profile_master_brand=profile_series.profile_master_type.profile_master_brand).order_by('id')
    categories_obj = Category.objects.filter(
        Q(one_D=True) | (Q(one_D=True) & Q(two_D=True))).order_by('id')
    category = categories_obj.get(pk=profile_series.profile_master_type.profile_master_category.id)
    brands = CategoryBrands.objects.filter(category=profile_series.profile_master_type.profile_master_category).order_by('id')
    profiles_obj = Profiles.objects.filter(profile_master_series=profile_series).order_by('id')
    brand = CategoryBrands.objects.get(pk=profile_master_type.profile_master_brand.id)
    context = {
        "title": f'{PROJECT_NAME} | Profiles Type.',
        "categories_obj": categories_obj,
        "brands": brands,
        "category": category,
        "profiles_obj": profiles_obj,
        "profile_series": profile_series,
        "profile_master_type": profile_master_type,
        "profile_master_types": profile_master_types,
        "profile_seriess": profile_seriess,
        "brand": brand,
    }
    return render(request, "Master_settings/Profiles/profile_base.html", context)


@login_required(login_url='signin')
@permission_required(['profiles.add_profiles'], login_url='permission_not_allowed')
def create_profile_item(request, pk):
    """
    This function creates a profile item for a given profile series using a form and saves it to the
    database.
    
    """
    profile_series = ProfileMasterSeries.objects.get(pk=pk)
    form = CreateProfileForm(category=profile_series.profile_master_type.profile_master_category)
    if request.method == 'POST':
        form = CreateProfileForm(request.POST, category=profile_series.profile_master_type.profile_master_category)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.profile_master_series = profile_series
            form_obj.save()
        else:
            messages.error(request, "Please Check all Fields..")
        return redirect('list_profile_items', pk=profile_series.id)
    context = {
        "form": form,
        "profile_series": profile_series
    }
    return render(request, "Master_settings/Profiles/add_profile_modal.html", context)


@login_required(login_url='signin')
@permission_required(['profiles.change_profiles'], login_url='permission_not_allowed')
def edit_profile_item(request, pk):
    """
    This function edits a profile item and saves it to the database.
    
    """
    
    profile = Profiles.objects.get(pk=pk)
    profile_series = ProfileMasterSeries.objects.get(pk=profile.profile_master_series.id)
    form = CreateProfileForm(instance=profile, category=profile_series.profile_master_type.profile_master_category)
    if request.method == 'POST':
        form = CreateProfileForm(request.POST, instance=profile, category=profile_series.profile_master_type.profile_master_category)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.profile_master_series = profile_series
            form_obj.save()
        else:
            messages.error(request, "Please Check all Fields..")
        return redirect('list_profile_items', pk=profile_series.id)
    context = {
        "form": form,
        "profile": profile,
    }
    return render(request, "Master_settings/Profiles/add_profile_modal.html", context)

@login_required(login_url='signin')
def delete_profile_item(request, pk):
    """
    This function deletes a profile item and displays a success or error message depending on whether
    the deletion was successful or not.
    
    """
    item = Profiles.objects.get(pk=pk)
    if request.method == "POST":
        try:
            item.delete()
            messages.success(request, "Profile Item Deleted Successfully")

        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_profile_items', pk=item.profile_master_series.id)

    context = {"url": f"/Profiles/delete_profile_item/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
@permission_required(['profiles.view_profiles'], login_url='permission_not_allowed')
def get_profile_data(request, pk):
    """
    This function retrieves the thickness and weight per linear meter of a profile object and returns it
    as a JSON response.
    
    """
    profile = Profiles.objects.get(pk=pk)
    data = {
        'thickness': profile.thickness,
        'weight_per_lm': profile.weight_per_lm
    }
    return JsonResponse(data, status=200)


@login_required(login_url='signin')
def aluminium_database_list(request):
    """
    This function retrieves distinct aluminium profile data from the Profiles model and renders it in a
    template.
    
    """
    profiles = Profile_Types.objects.all()
    profile = Profiles.objects.all()
    categories = profile.distinct('profile_master_series__profile_master_type__profile_master_category')
    systems = profile.distinct('profile_master_series__profile_master_type__profile_master_brand__brands')
    context = {
        "title": f"{PROJECT_NAME} | Aluminium Database List",
        "profiles": profiles,
        "categories": categories,
        "systems": systems,
    }
    return render(request, "Master_settings/Profiles/aluminium_reference.html", context)


@login_required(login_url='signin')
def aluminium_filter(request, p_type=None, category=None, system=None):
    """
    The function filters and displays aluminium profiles based on a primary key value.
    
    """

    if p_type == '0' and category == '0' and system == '0':
        profiles = Profiles.objects.all().distinct('profile_master_series__profile_master_type__profile_master_type')
    elif p_type != '0' and category == '0' and system == '0':
        profiles = Profiles.objects.filter(profile_master_series__profile_master_type__profile_master_type=p_type).distinct('profile_master_series__profile_master_type__profile_master_type')
    elif category != '0' and p_type == '0' and system == '0':
        profiles = Profiles.objects.filter(profile_master_series__profile_master_type__profile_master_category=category).distinct('profile_master_series__profile_master_type__profile_master_type')
    elif system != '0' and p_type == '0' and category == '0':
        profiles = Profiles.objects.filter(profile_master_series__profile_master_type__profile_master_brand=system).distinct('profile_master_series__profile_master_type__profile_master_type')
    elif p_type != '0' and category != '0' and system == '0':
        profiles = Profiles.objects.filter(
                                    profile_master_series__profile_master_type__profile_master_type=p_type, 
                                    profile_master_series__profile_master_type__profile_master_category=category
                                    ).distinct('profile_master_series__profile_master_type__profile_master_type')
    else:
        profiles = Profiles.objects.filter(
            profile_master_series__profile_master_type__profile_master_type=p_type,
            profile_master_series__profile_master_type__profile_master_category=category,
            profile_master_series__profile_master_type__profile_master_brand=system,
        ).distinct('profile_master_series__profile_master_type__profile_master_type')

    profiless = [data.profile_master_series.profile_master_type.profile_master_type for data in profiles]
    context = {
        "title": f"{PROJECT_NAME} | Aluminium Database List",
        "profiles": profiless,
    }
    return render(request, "Master_settings/Profiles/aluminium_data_table.html", context)


@login_required(login_url='signin')
def aluminium_data_export(request, type):
    return aluminium_data_export_shared(request, type)


@login_required(login_url='signin')
def addons_data_export(request, type):
    return addons_data_export_shared(request, type)


@login_required(login_url='signin')
def accessories_database_list(request):
    
    categories_objs = AccessoriesKit.objects.distinct('product__product_category')
    
    # accessories_objs = AccessoriesKit.objects.all()
    
    # .distinct('product__product_category')
    
    
    context = {
        "title": f"{PROJECT_NAME} | Accessories Database List",
        # "accessories_objs": accessories_objs,
        "categories_objs": categories_objs,
    }
    return render(request, "Master_settings/Accessories_kit/accessories_database_list.html", context)