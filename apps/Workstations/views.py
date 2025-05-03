from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.Workstations.models import Workstations
from apps.Workstations.forms import CreateWorkstationsForm, EditWorkstationsForm

from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
def list_workstations(request, pk=None):
    """
    This function lists workstations, creates new workstations, and edits existing workstations in a web
    application.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the HTTP method, headers, and data
    :param pk: pk is a parameter that represents the primary key of a specific Workstations object. It
    is used to retrieve and edit a specific Workstations object from the database
    :return: an HTTP response with a rendered HTML template
    'Master_settings/Workstations/workstations.html' along with some context variables such as the
    title, create_form, workstation_obj, and edit_form.
    """
    workstation_obj = Workstations.objects.all().order_by('id')
    create_form = CreateWorkstationsForm()
    edit_form = EditWorkstationsForm()
    if request.method == 'POST':
        if 'create_workstation' in request.POST:
            create_form = CreateWorkstationsForm(request.POST)
            if create_form.is_valid():
                create_obj = create_form.save(commit=False)
                create_obj.created_by = request.user
                create_obj.save()
                messages.success(request, "Workstation Created Successfully")
                return redirect('list_workstations')
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditWorkstationsForm(
                request.POST, instance=Workstations.objects.get(pk=pk))
            if edit_form.is_valid():
                edit_obj = edit_form.save()
                edit_obj.last_modified_date = time()
                edit_obj.last_modified_by = request.user
                edit_obj.save()
                messages.success(request, "Workstation Updated Successfully")
                return redirect('list_workstations')
            else:
                messages.error(request, edit_form.errors)
    context = {
        "title": PROJECT_NAME + " | Workstations List",
        "create_form": create_form,
        "workstation_obj": workstation_obj,
        "edit_form": edit_form,
    }
    return render(request, 'Master_settings/Workstations/workstations.html', context)


@login_required(login_url='signin')
def workstations_delete(request, pk):
    """
    This function deletes a workstation object and displays a success message, or an error message if
    the object is already in use.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: pk stands for primary key, which is a unique identifier for a specific record in a
    database table. In this case, it is used to identify the specific Workstations object that needs to
    be deleted from the database
    :return: a redirect to the 'list_workstations' URL.
    """
    workstation_obj = Workstations.objects.get(pk=pk)
    try:
        workstation_obj.delete()
        messages.success(request, "Workstations Deleted Successfully")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("Delete is not possible.")
    return redirect('list_workstations')
