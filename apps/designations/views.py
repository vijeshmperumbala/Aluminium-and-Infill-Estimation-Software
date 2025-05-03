from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.designations.models import Designations
from apps.designations.forms import (
        CreateDesignationForm, 
        EditDesignationForm,
    )
from apps.product_master.models import Product
from amoeba.settings import PROJECT_NAME


@login_required(login_url="signin")
@permission_required(
    [
        'designations.view_designations', 
        'designations.add_designations', 
        'designations.change_designations',
    ], login_url='permission_not_allowed')
def list_add_designation(request, pk=None):
    """
    This function handles the creation and editing of designations and renders the corresponding HTML
    template.
    
    """
    designation_obj = Designations.objects.all().order_by('id')
    create_form = CreateDesignationForm()
    edit_form = EditDesignationForm()
    if request.method == 'POST':
        if 'create_designation' in request.POST:
            create_form = CreateDesignationForm(request.POST)
            if create_form.is_valid():
                create_obj = create_form.save(commit=False)
                create_obj.created_by = request.user
                create_obj.save()
                messages.success(request, "Designation Created Successfully")
                return redirect('list_add_designation')
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditDesignationForm(request.POST, instance=Designations.objects.get(pk=pk))
            if edit_form.is_valid():
                edit_obj = edit_form.save()
                edit_obj.last_modified_date = time()
                edit_obj.last_modified_by = request.user
                edit_obj.save()
                messages.success(request, "Designantion Updated Successfully")
                return redirect('list_add_designation')
            else:
                messages.error(request, edit_form.errors)
    context = {
        "title": f"{PROJECT_NAME} | Designation List",
        "create_form": create_form,
        "designation_obj": designation_obj,
        "edit_form": edit_form,
    }
    return render(request, 'Settings/Designation/designations.html', context)


@login_required(login_url='signin')
@permission_required(['designations.delete_designations'], login_url='permission_not_allowed')
def designation_delete(request, pk):
    """
    This function deletes a Designations object and displays a success or error message, depending on
    whether the object has been used in the application or not.
    
    """
    designation_obj = Designations.objects.get(pk=pk)
    try:
        designation_obj.delete()
        messages.success(request, "Designantion Deleted Successfully")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
    return redirect('list_add_designation')
