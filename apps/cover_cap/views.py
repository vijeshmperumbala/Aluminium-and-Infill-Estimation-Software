from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.cover_cap.models import CoverCap_PressurePlates
from apps.cover_cap.forms import CoverCapForm
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
def covercap_list(request):
    """
    This function displays a list of Cover Cap and Pressure Plate objects and allows the user to create
    new ones through a form.
    
    """
    cap_objects = CoverCap_PressurePlates.objects.all().order_by('id')
    forms = CoverCapForm()
    if request.method == "POST":
        forms = CoverCapForm(request.POST)
        if forms.is_valid():
            form_obj = forms.save(commit=False)
            form_obj.created_by = request.user
            form_obj.save()
            messages.success(request, "Successfully Created New Cover Cap/Pressure Plate.")
        else:
            messages.error(request, forms.errors)
        return redirect('covercap_list')
    context = {
        "title": f"{PROJECT_NAME} | Cover Cap & Pressure Plates",
        "cap_objects": cap_objects,
        "forms": forms,
    }
    return render(request, "Master_settings/CoverCap_and/covercap_and_pressureplate.html", context)

@login_required(login_url="signin")
def edit_covercap(request, pk):
    """
    This function edits a CoverCap or PressurePlate object and saves the changes made by the user.
    
    """
    covercap_item = CoverCap_PressurePlates.objects.get(pk=pk)
    form = CoverCapForm(instance=covercap_item)
    if request.method == "POST":
        form = CoverCapForm(request.POST, instance=covercap_item)
        if form.is_valid():
            form_obj = form.save()
            form_obj.last_modified_by = request.user
            form_obj.last_modified_date = time()
            form_obj.save()
            messages.success(request, "Successfully Updated Cover Cap/Pressure Plate Data.")
        else:
            messages.error(request, form.errors)
        return redirect('covercap_list')
    context = {
        "covercap_item": covercap_item,
        "forms": form,
    }
    return render(request, "Master_settings/CoverCap_and/edit_covercap.html", context)
    

def delete_covercap_pressure_plate(request, pk):
    """
    This function deletes a CoverCap_PressurePlates object and displays a success or error message.
    
    """
    covercap_items = CoverCap_PressurePlates.objects.get(pk=pk)
    if request.method == "POST":
        try:
            covercap_items.delete()
            messages.success(request, "Cover Cap/Pressure Plate Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Deletion is not possible.")
        return redirect('covercap_list')
    context = {
        "url": f"/CoverCap_and_PressurePlates/delete_covercap_pressure_plate/{str(pk)}/"
    }
    return render(request, "Master_settings/delete_modal.html", context)