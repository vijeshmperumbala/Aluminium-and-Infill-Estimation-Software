from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required
from django import forms

from apps.brands.models import AccessoriesBrands
from apps.accessories_master.models import Accessories
from apps.accessories_master.forms import (
        CreateAccessoriesForm, 
        EditAccessoriesForm,
    )
from apps.Categories.models import Category
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
@permission_required(['accessories_master.view_accessories'], login_url='permission_not_allowed')
def accessories_list(request):
    """
        Accessories listing page view function.
    """
    cat_name = Category.objects.all().order_by('id').first()
    if cat_name:
        count = Accessories.objects.filter(
            accessory_category_id=cat_name.id).order_by("id")
    else:
        count = Accessories.objects.all().order_by("id")

    category_obj = Category.objects.all().order_by('id')
    context = {
        "title": f"{PROJECT_NAME} | Accessories master",
        "accessories": count,
        "category_obj": category_obj,
        "cat_name": cat_name,
        "count": count.count(),
    }
    return render(request, 'Master_settings/Accessories_Master/accessories.html', context)


@login_required(login_url='signin')
@permission_required(['accessories_master.add_accessories'], login_url='permission_not_allowed')
def accessories_create(request, pk):
    """
        Accessory create view function
        pk: category id.
        the Accessory was creating under Current selected category
    """
    category_obj = Category.objects.get(pk=pk)
    form = CreateAccessoriesForm()
    form.fields['accessory_brand'] = forms.ModelChoiceField(
        queryset=AccessoriesBrands.objects.filter(
            category=category_obj.id
        ))
    form.fields['accessory_brand'].widget.attrs.update({
        'class': 'form-control mb-2',
        'data-control': 'select2',
        'data-placeholder': 'Select a brand'
    })
    if request.method == 'POST':
        form = CreateAccessoriesForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            obj.created_by = request.user
            obj.accessory_category = category_obj
            obj.save()
            messages.success(request, "Accessory Created Successfully")
            return redirect('category_wise_accessories', pk=pk)
        else:
            messages.error(request, form.errors)
        return redirect('category_wise_accessories', pk=pk)
    context = {
        "title": f"{PROJECT_NAME} | Accessory Create",
        "form": form,
        "pk": pk,
    }
    return render(request, 'Master_settings/Accessories_Master/accessories_add_drawer.html', context)


@login_required(login_url='signin')
@permission_required(['accessories_master.change_accessories'], login_url='permission_not_allowed')
def accessory_edit(request, pk):
    """
        Accessories edit function
        pk: accessory id.
    """
    accessories = Accessories.objects.get(pk=pk)
    form = EditAccessoriesForm(instance=accessories)
    if request.method == 'POST':
        form = EditAccessoriesForm(
            request.POST, request.FILES, instance=accessories)
        if form.is_valid():
            obj = form.save()
            obj.last_modified_by = request.user
            obj.last_modified_date = time()
            obj.save()
            messages.success(request, "Accessory Updated Successfully")
        else:
            messages.error(request, form.errors)
            print("errors==>", form.errors)
        return redirect('category_wise_accessories', pk=accessories.accessory_category.id)
    context = {
        "title": f"{PROJECT_NAME} | Accessory Edit",
        "form": form,
        "accessories": accessories,
    }
    return render(request, 'Master_settings/Accessories_Master/accessories_edit_drawer.html', context)


@login_required(login_url='signin')
@permission_required(['accessories_master.view_accessories'], login_url='permission_not_allowed')
def category_wise_accessories(request, pk):
    """
        Category wise accessory listing page view function
        pk: category id.
    """
    accessories = Accessories.objects.filter(
        accessory_category=pk).order_by("id")
    count = accessories.count()
    category_obj = Category.objects.all().order_by('id')
    cat_name = Category.objects.get(pk=pk)
    context = {
        "title": f"{PROJECT_NAME} | Accessory List",
        "accessories": accessories,
        "count": count,
        "category_obj": category_obj,
        "cat_name": cat_name,
    }
    return render(request, 'Master_settings/Accessories_Master/accessories.html', context)


@login_required(login_url='signin')
@permission_required(['accessories_master.delete_accessories'], login_url='permission_not_allowed')
def accessory_deletes(request, pk):
    """
        simple accessory delete view function.
        pk ==> id of accessory.
    """
    if request.method == "POST":
        try:
            accessory_obj = Accessories.objects.get(pk=pk)
            accessory_obj.delete()
            messages.success(request, "Accessory Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('category_wise_accessories', pk=accessory_obj.accessory_category.id)

    context = {
                "url": f"/Accessories/accessory_deletes/{str(pk)}/"
                }
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
def get_country_wise_brand(request, cat_id, pk):
    """
    This function retrieves a list of accessory brands based on a given category and country and renders
    it in a dropdown menu.
    """
    data_obj = AccessoriesBrands.objects.filter(category=cat_id, country=pk).order_by('id')
    return render(request, 'Master_settings/Accessories_Master/dropdown/brand_dropdown.html', {'data_obj': data_obj})
