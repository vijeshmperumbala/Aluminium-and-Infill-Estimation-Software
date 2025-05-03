from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.Categories.models import Category
from apps.Categories.forms import (
        CreateCategoryForm, 
        EditCategoryForm,
    )
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
@permission_required(['Categories.view_category', 'Categories.add_category'], login_url='permission_not_allowed')
def category_list(request):
    """
    This function displays a list of categories and allows the user to create a new category.
    """
    category_obj = Category.objects.all().order_by('id')
    create_form = CreateCategoryForm()
    if request.method == 'POST':
        create_form = CreateCategoryForm(request.POST, request.FILES)
        if create_form.is_valid():
            create_obj = create_form.save(commit=False)
            create_obj.created_by = request.user
            create_obj.save()
            messages.success(request, "Category Created Successfully")
            return redirect('category_list')
        else:
            messages.error(request, create_form.errors)
    context = {
        "title": f"{PROJECT_NAME} | Category List",
        "category_obj": category_obj,
        "create_form": create_form,
    }
    return render(request, 'Master_settings/Category_Master/master_categories.html', context)


@login_required(login_url='signin')
@permission_required(['Categories.view_category', 'Categories.change_category'], login_url='permission_not_allowed')
def edit_category(request, pk):
    """
    This function edits a category object and saves the changes made by the user.
    """
    category = Category.objects.get(pk=pk)
    edit_form = EditCategoryForm(instance=category)
    if request.method == 'POST':
        edit_form = EditCategoryForm(
            request.POST, request.FILES, instance=category)
        if edit_form.is_valid():
            edit_obj = edit_form.save(commit=False)
            edit_obj.last_modified_date = time()
            edit_obj.last_modified_by = request.user
            if not edit_obj.enable_internal_sealant:
                edit_obj.internal_sealant = None

            if not edit_obj.enable_external_sealant:
                edit_obj.external_sealant = None
            edit_obj.save()
            messages.success(request, "Category Updated Successfully")
            return redirect('category_list')
        else:
            messages.error(request, edit_form.errors)
    context = {
        "title": f"{PROJECT_NAME} | Category Edit",
        "edit_form": edit_form,
        "pk": pk,
    }
    return render(request, 'Master_settings/Category_Master/edit_category_model.html', context)


@login_required(login_url='signin')
@permission_required(['Categories.delete_category'], login_url='permission_not_allowed')
def category_delete(request, pk):
    """
    This function deletes a category object and displays a success message, or an error message if the
    object is already in use.
    """
    category_obj = Category.objects.get(pk=pk)
    
    try:
        category_obj.delete()
        messages.success(request, "Category Deleted Successfully")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
    return redirect('category_list')


