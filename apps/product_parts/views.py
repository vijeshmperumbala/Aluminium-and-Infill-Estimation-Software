from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.timezone import now as time

from apps.Categories.models import Category
from apps.brands.models import CategoryBrands
from apps.product_master.models import Product
from apps.product_parts.models import Parts, Profile_Kit, Profile_items
from apps.product_parts.forms import CreateProfilesKit, CreatePartsForm

from amoeba.settings import PROJECT_NAME
from apps.profiles.models import Profiles


@login_required(login_url='signin')
@permission_required(['product_parts.view_parts'], login_url='permission_not_allowed')
def list_parts(request):
    """
    This function retrieves a list of categories for parts and renders them in a template.
    
    """
    categories_obj = Category.objects.filter(
        Q(one_D=True) | (Q(one_D=True) & Q(two_D=True))).order_by('id')
    context = {
        "title": f'{PROJECT_NAME} | Parts List.',
        "categories_obj": categories_obj,
    }
    return render(request, "Master_settings/Product_Parts/list_parts.html", context)


@login_required(login_url='signin')
@permission_required(['product_parts.view_parts'], login_url='permission_not_allowed')
def list_parts_by_category(request, pk):
    """
    This function retrieves a list of parts filtered by a specific category and renders it in a template
    with additional context.
    
    """
    category = Category.objects.get(pk=pk)
    parts_obj = Parts.objects.filter(parts_category=category).order_by('id')
    categories_obj = Category.objects.filter(
        Q(one_D=True) | (Q(one_D=True) & Q(two_D=True))).order_by('id')
    context = {
        "title": f'{PROJECT_NAME} | Parts List.',
        "categories_obj": categories_obj,
        "parts_obj": parts_obj,
        "category": category,
    }
    return render(request, "Master_settings/Product_Parts/list_parts.html", context)

@login_required(login_url='signin')
@permission_required(['product_parts.add_parts'], login_url='permission_not_allowed')
def create_parts_data(request, pk):
    """
    This function creates new parts data for a specific category and saves it to the database.
    
    """
    category = Category.objects.get(pk=pk)
    form = CreatePartsForm()
    if request.method == "POST":
        form = CreatePartsForm(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.parts_category = category
            form_obj.created_by = request.user
            form_obj.save()
        else:
            messages.error(request, "Please Check All the fields.")
        return redirect('list_parts_by_category', pk=category.id)
    context = {
        "title": f'{PROJECT_NAME} | Add New Parts.',
        "form": form,
        "category": category,
    }
    return render(request, "Master_settings/Product_Parts/add_parts_modal.html", context)


@login_required(login_url='signin')
@permission_required(['product_parts.change_parts'], login_url='permission_not_allowed')
def edit_parts_data(request, pk):
    """
    This function edits parts data and saves the changes made by the user.
    
    """
    parts = Parts.objects.get(pk=pk)
    category = Category.objects.get(pk=parts.parts_category.id)
    form = CreatePartsForm(instance=parts)
    if request.method == "POST":
        form = CreatePartsForm(request.POST, instance=parts)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.last_modified_date = time()
            form_obj.last_modified_by = request.user
            form_obj.save()
        else:
            messages.error(request, "Please Check All the fields.")
        return redirect('list_parts_by_category', pk=category.id)
    context = {
        "title": f'{PROJECT_NAME} | Edit Parts.',
        "form": form,
        "category": category,
        "parts": parts,
    }
    return render(request, "Master_settings/Product_Parts/add_parts_modal.html", context)


@login_required(login_url='signin')
def delete_parts(request, pk):
    """
    This function deletes a Parts object and redirects to a list view of Parts objects by category.
    
    """
    item = Parts.objects.get(pk=pk)
    if request.method == "POST":
        try:
            item.delete()
            messages.success(request, f"Parts {item} Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_parts_by_category', pk=item.parts_category.id)

    context = {"url": f"/Parts/delete_parts/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)
        

@login_required(login_url='signin')
@permission_required(['product_parts.add_parts'], login_url='permission_not_allowed')
def create_parts_kit(request, pk):
    """
    This function creates a parts kit for a product and saves the data entered in the form.
    
    """
    product = Product.objects.get(pk=pk)
    parts_form = CreateProfilesKit()
    parts_kit_form = CreateProfilesKit(category=product.product_category)
    parts_kit_forms = modelformset_factory(Profile_items, form=parts_kit_form, extra=1, can_delete=True)
    parts_kit_formset = parts_kit_forms(queryset=Profile_items.objects.none(), prefix="parts_kit")
    if request.method == "POST":
        parts_form = CreateProfilesKit(request.POST)
        parts_kit_formset = parts_kit_forms(request.POST, queryset=Profile_items.objects.none(), prefix="parts_kit")
        if parts_form.is_valid():
            parts_obj = parts_form.save(commit=False)
            parts_obj.product = product
            parts_obj.save()
            for items in parts_kit_formset:
                if items.is_valid():
                    items_obj = items.save(commit=False)
                    items_obj.parts_kit = parts_obj
                    if items_obj.formula:
                        items_obj.save()
                else:
                    messages.error(request, "Error in one of the item.")
        else:
            messages.error(request, "Error in form save. Please Check Entered Data..")
        return redirect("product_profile", pk=product.id)
    context = {
        "title": f"{PROJECT_NAME} | Create Parts Kit",
        "parts_form": parts_form,
        "parts_kit_formset": parts_kit_formset,
        "product": product,
    }
    return render(request, "Master_settings/Product_Parts/create_parts_kit_modal.html", context)


@login_required(login_url='signin')
@permission_required(['product_parts.change_parts'], login_url='permission_not_allowed')
def series_kit_edit(request, pk):
    """
    This function edits a profile kit and its associated profile items for a given product.
    
    """
    kit = Profile_Kit.objects.get(pk=pk)
    product = Product.objects.get(pk=kit.product.id)
    parts_form = CreateProfilesKit(instance=kit)
    parts_kit_form = CreateProfilesKit(product.product_category)
    parts_kit_forms = modelformset_factory(Profile_items, form=parts_kit_form, extra=1,
                         can_delete=True)
    parts_kit_formset = parts_kit_forms(queryset=Profile_items.objects.filter(parts_kit=kit), prefix="parts_kit")
    systems = CategoryBrands.objects.filter(category=product.product_category).order_by('id')
    if request.method == "POST":
        parts_form = CreateProfilesKit(request.POST, instance=kit)
        parts_kit_formset = parts_kit_forms(request.POST, queryset=Profile_items.objects.filter(parts_kit=kit), prefix="parts_kit")
        if parts_form.is_valid():
            parts_obj = parts_form.save(commit=False)
            parts_obj.product = product
            parts_obj.save()
            for items in parts_kit_formset:
                if items.is_valid():
                    items_obj = items.save(commit=False)
                    if items_obj.formula:
                        items_obj.parts_kit = parts_obj
                        items_obj.save()
                else:
                    messages.error(request, "Error in one of the item.")
        else:
            messages.error(request, "Error in form save. Please Check Entered Data..")
        return redirect("product_profile", pk=product.id)
    context = {
        "title": f"{PROJECT_NAME} | Edit Parts Kit",
        "parts_form": parts_form,
        "parts_kit_formset": parts_kit_formset,
        "product": product,
        "kit": kit,
        "systems": systems,
    }
    return render(request, "Master_settings/Product_Parts/create_parts_kit_modal.html", context)


@login_required(login_url='signin')
@permission_required(['product_parts.delete_parts'], login_url='permission_not_allowed')
def delete_series_kit(request, pk):
    """
    This function deletes a kit and its associated items from the database, and redirects the user to a
    specific page.
    
    """
    kit = Profile_Kit.objects.get(pk=pk)
    try:
        item = Profile_items.objects.filter(profile_kit=kit)
        try:
            item.delete()
            kit.delete()
        except Exception as ee:
            print("EXcepTionSs==>", ee)
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("exception--===>", e)
    return redirect("configuration_brands", pk=kit.product.id)
    
    
@login_required(login_url='signin')
@permission_required(['profiles.view_profiles'], login_url='permission_not_allowed')
def get_profile_select(request, pk):
    """
    This function retrieves profiles filtered by brand and renders them in a dropdown menu.
    
    """
    profiles = Profiles.objects.filter(brand=pk).order_by('id')
    context = {
        "profiles": profiles
    }
    return render(request, "Master_settings/Product_Parts/system_dropdown.html", context)