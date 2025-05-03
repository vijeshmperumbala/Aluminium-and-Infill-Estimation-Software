from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.sealant_types.models import Sealant_Types
from apps.sealant_types.forms import CreateSealantTypesForm, EditSealantTypesForm
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
@permission_required(['sealant_types.view_sealant_types', 'sealant_types.change_sealant_types', 'sealant_types.add_sealant_types'], login_url='permission_not_allowed')
def sealant_type_list(request, pk=None):
    """
    This function displays a list of sealant types and allows for the creation and editing of sealant
    types.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: pk is a parameter that represents the primary key of a specific Sealant_Types object. It
    is used to retrieve and edit a specific object in the database. If a pk value is provided in the
    URL, the view will use it to retrieve the corresponding object and populate the edit form with its
    data
    :return: an HTTP response with a rendered HTML template
    'Master_settings/Sealant_Types/sealant_types.html' along with some context variables such as
    'title', 'create_form', 'sealant_type_obj', and 'edit_form'.
    """
    sealant_type_obj = Sealant_Types.objects.all().order_by('id')
    create_form = CreateSealantTypesForm()
    edit_form = EditSealantTypesForm()
    if request.method == 'POST':
        if 'create_sealant_type' in request.POST:
            create_form = CreateSealantTypesForm(request.POST)
            if create_form.is_valid():
                create_obj = create_form.save(commit=False)
                create_obj.created_by = request.user
                create_obj.save()
                return redirect('sealant_type_list')
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditSealantTypesForm(
                request.POST, instance=Sealant_Types.objects.get(pk=pk))
            if edit_form.is_valid():
                edit_obj = edit_form.save()
                edit_obj.last_modified_date = time()
                edit_obj.last_modified_by = request.user
                edit_obj.save()
                return redirect('sealant_type_list')
            else:
                messages.error(request, edit_form.errors)
    context = {
        "title": PROJECT_NAME + " | Sealant Types List",
        "create_form": create_form,
        "sealant_type_obj": sealant_type_obj,
        "edit_form": edit_form,
    }
    return render(request, 'Master_settings/Sealant_Types/sealant_types.html', context)


@login_required(login_url='signin')
@permission_required(['sealant_types.delete_sealant_types'], login_url='permission_not_allowed')
def sealant_type_delete(request, pk):
    """
    This function deletes a sealant type object and displays a success message, or an error message if
    the object is already in use.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: pk stands for "primary key". In Django, every model has a primary key field that uniquely
    identifies each instance of the model. In this case, the pk parameter is used to retrieve a specific
    instance of the Sealant_Types model based on its primary key value
    :return: a redirect to the 'sealant_type_list' URL.
    """
    sealant_type_obj = Sealant_Types.objects.get(pk=pk)
    try:
        sealant_type_obj.delete()
        messages.success(request, "Sealant Type Successfully Deleted.")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("Delete is not possible.")
    return redirect('sealant_type_list')
