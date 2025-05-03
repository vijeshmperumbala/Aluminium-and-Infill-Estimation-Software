
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.Categories.models import Category
from apps.addon_master.models import Addons
from apps.addon_master.forms import (
        CreateAddonForm, 
        EditAddonForm,
    )
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
@permission_required(['addon_master.change_addons'], login_url='permission_not_allowed')
def list_addons(request, pk=None):

    """
        UoM list/ create/ edit
        single view function for UoM list create and edit
        pk :: primary key of UoM for edit
    """
    
    addon_obj = Addons.objects.all().order_by('id')
    create_form = CreateAddonForm()
    edit_form = EditAddonForm()
    if request.method == 'POST':
        if 'create_addons' in request.POST:
            create_form = CreateAddonForm(request.POST)
            if create_form.is_valid():
                create_obj = create_form.save(commit=False)
                create_obj.created_by = request.user
                create_obj.save()
                messages.success(request, "Addon Created Successfully")
                return redirect('list_addons')
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditAddonForm(
                request.POST, instance=Addons.objects.get(pk=pk))
            if edit_form.is_valid():
                edit_obj = edit_form.save()
                edit_obj.last_modified_date = time()
                edit_obj.last_modified_by = request.user
                edit_obj.save()
                messages.success(request, "Addon Updated Successfully")
                return redirect('list_addons')
            else:
                messages.error(request, edit_form.errors)
    context = {
        "title": f"{PROJECT_NAME} | Addon List",
        "create_form": create_form,
        "addon_obj": addon_obj,
        "edit_form": edit_form,
    }
    return render(request, 'Master_settings/Addon_Master/addons.html', context)


@login_required(login_url='signin')
@permission_required(['addon_master.delete_addons'], login_url='permission_not_allowed')
def addon_delete(request, pk):
    """
    This function deletes an Addon object and displays a success message, or an error message if the
    object is already in use.
    """
    addon_obj = Addons.objects.get(pk=pk)
    try:
        addon_obj.delete()
        messages.success(request, "Addon Deleted Successfully")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("Delete is not possible.")
    return redirect('list_addons')


@login_required(login_url='signin')
@permission_required(['addon_master.view_addons'], login_url='permission_not_allowed')
def addon_data_estimation(request, pk):
    """
    The function returns JSON data containing information about a specific addon object.
    """
    addon_obj = Addons.objects.get(pk=pk)
    data = {
        'addons_lm': addon_obj.linear_meter,
        'addon_sqm': addon_obj.sqm,
        'addon_unit': addon_obj.unit
    }
    return JsonResponse(data, status=200)


@login_required(login_url='signin')
def addons_database_list(request):
    addons_objs = Addons.objects.filter(activated=True)
    context = {
        "title": f"{PROJECT_NAME} | Addons Database List",
        "addons_objs": addons_objs,
    }
    return render(request, "Master_settings/Profiles/addons_reference.html", context)




