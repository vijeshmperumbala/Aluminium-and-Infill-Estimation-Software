from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse

from apps.project_specifications.forms import (
    CreateProjectSpecificationsForm, 
    EditProjectSpecificationsForm,
)
from apps.project_specifications.models import ProjectSpecifications

from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
def list_project_specifications(request, pk=None):
    """
    This function lists project specifications, allows for creating new specifications, and editing
    existing ones.
    
    """
    project_spec_obj = ProjectSpecifications.objects.all().order_by('id')
    create_form = CreateProjectSpecificationsForm()
    edit_form = EditProjectSpecificationsForm()
    if request.method == 'POST':
        if 'create_specification' in request.POST:
            create_form = CreateProjectSpecificationsForm(request.POST)
            if create_form.is_valid():
                create_obj = create_form.save(commit=False)
                create_obj.created_by = request.user
                create_obj.save()
                return redirect('list_project_specifications')
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditProjectSpecificationsForm(
                request.POST, instance=ProjectSpecifications.objects.get(pk=pk))
            if edit_form.is_valid():
                edit_obj = edit_form.save()
                edit_obj.last_modified_date = time()
                edit_obj.last_modified_by = request.user
                edit_obj.save()
                return redirect('list_project_specifications')
            else:
                messages.error(request, edit_form.errors)
    context = {
        "title": f'{PROJECT_NAME} | Project Specifications List',
        "create_form": create_form,
        "project_spec_obj": project_spec_obj,
        "edit_form": edit_form,
    }
    return render(request, 'Master_settings/Project_Specifications/list_project_spec.html', context)

@login_required(login_url='signin')
def project_spec_delete(request, pk):
    """
    This function deletes a project specification object and displays a success or error message
    depending on whether the object has been used in an application or not.
    
    """
    project_spec_obj = ProjectSpecifications.objects.get(pk=pk)
    if request.method == "POST":
        try:
            project_spec_obj.delete()
            messages.success(request, "Project Specifications Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_project_specifications')

    context = {"url": f"/Project_Specifications/project_spec_delete/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)
