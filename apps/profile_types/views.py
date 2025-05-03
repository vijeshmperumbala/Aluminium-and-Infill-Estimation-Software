from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.profile_types.models import Profile_Types
from apps.profile_types.forms import CreateProfileTypeForm, EditProfileTypeForm
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
@permission_required(['UoM.change_uom'], login_url='permission_not_allowed')
def profile_type_list(request, pk=None):
    """
    This function displays a list of profile types and allows the user to create and edit profile types.
    
    """
    profile_type_obj = Profile_Types.objects.all().order_by('id')
    create_form = CreateProfileTypeForm()
    edit_form = EditProfileTypeForm()
    if request.method == 'POST':
        if 'create_profile_type' in request.POST:
            create_form = CreateProfileTypeForm(request.POST)
            if create_form.is_valid():
                create_obj = create_form.save(commit=False)
                create_obj.created_by = request.user
                create_obj.save()
                return redirect('profile_type_list')
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditProfileTypeForm(request.POST, instance=Profile_Types.objects.get(pk=pk))
            if edit_form.is_valid():
                edit_obj = edit_form.save()
                edit_obj.last_modified_date = time()
                edit_obj.last_modified_by = request.user
                edit_obj.save()
                return redirect('profile_type_list')
            else:
                messages.error(request, edit_form.errors)
    context = {
        "title": f'{PROJECT_NAME} | Profile Type List',
        "create_form": create_form,
        "profile_type_obj": profile_type_obj,
        "edit_form": edit_form,
    }
    return render(request, 'Master_settings/Profile_Type/profile_type.html', context)


# @permission_required(['UoM.change_uom'], login_url='permission_not_allowed')
@login_required(login_url='signin')
def profile_type_delete(request, pk):
    """
    This function deletes a profile type object and displays an error message if it is already used in
    an application.
    
    """
    profile_type_obj = Profile_Types.objects.get(pk=pk)
    try:
        profile_type_obj.delete()
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("Delete is not possible.")
    return redirect('profile_type_list')