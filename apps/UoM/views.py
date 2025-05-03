from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.UoM.models import UoM
from apps.UoM.forms import CreateUoMForm, EditUoMForm
from apps.product_master.models import Product
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
@permission_required(['UoM.change_uom'], login_url='permission_not_allowed')
def uom_list(request, pk=None):
    """
    This function displays a list of units of measurement (UoM) and allows the user to create or edit
    UoM objects.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the HTTP method, headers, and any data submitted in the request
    :param pk: pk is a parameter that represents the primary key of a specific UoM object in the
    database. It is used to retrieve and edit a specific UoM object in the database. If pk is None, it
    means that no specific UoM object is being edited and the view is only displaying
    :return: an HTTP response with the rendered 'Master_settings/UoM/uom.html' template, along with a
    context dictionary containing the title, create_form, uom_obj, and edit_form variables.
    """
    uom_obj = UoM.objects.all().order_by('id')
    create_form = CreateUoMForm()
    edit_form = EditUoMForm()
    if request.method == 'POST':
        if 'create_uom' in request.POST:
            create_form = CreateUoMForm(request.POST)
            if create_form.is_valid():
                create_obj = create_form.save(commit=False)
                create_obj.created_by = request.user
                create_obj.save()
                messages.success(request, "UoM Created Successfully")
                return redirect('uom_list')
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditUoMForm(
                request.POST, instance=UoM.objects.get(pk=pk))
            if edit_form.is_valid():
                edit_obj = edit_form.save()
                edit_obj.last_modified_date = time()
                edit_obj.last_modified_by = request.user
                edit_obj.save()
                messages.success(request, "UoM Updated Successfully")
                return redirect('uom_list')
            else:
                messages.error(request, edit_form.errors)
    context = {
        "title": PROJECT_NAME + " | UoM List",
        "create_form": create_form,
        "uom_obj": uom_obj,
        "edit_form": edit_form,
    }
    return render(request, 'Master_settings/UoM/uom.html', context)


@permission_required(['UoM.change_uom'], login_url='permission_not_allowed')
@login_required(login_url='signin')
def uom_delete(request, pk):
    """
    This function deletes a UoM object and displays a success message, or an error message if the object
    is already in use.
    
    """
    uom_obj = UoM.objects.get(pk=pk)
    try:
        uom_obj.delete()
        messages.success(request, "UoM Deleted Successfully")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("Delete is not possible.")
    return redirect('uom_list')
