from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.enquiry_type.models import EnquiryTypeModal
from apps.enquiry_type.forms import (
        CreateEnquiryTypeForm, 
        EditEnquiryTypeForm,
    )
from apps.product_master.models import Product
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
@permission_required(
    [
        'enquiry_type.view_enquirytypemodal', 
        'enquiry_type.add_enquirytypemodal', 
        'enquiry_type.change_enquirytypemodal',
    ], login_url='permission_not_allowed')
def enquiry_type_list(request, pk=None):
    """
    This function displays a list of enquiry types and allows the user to create or edit enquiry types.
    """
    enq_type_obj = EnquiryTypeModal.objects.all().order_by('id')
    create_form = CreateEnquiryTypeForm()
    edit_form = EditEnquiryTypeForm()
    if request.method == 'POST':
        if 'create_enquiry_type' in request.POST:
            create_form = CreateEnquiryTypeForm(request.POST)
            if create_form.is_valid():
                create_obj = create_form.save(commit=False)
                create_obj.save()
                messages.success(request, "Enquiry Type Created Successfully")
                return redirect('enquiry_type_list')
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditEnquiryTypeForm(request.POST, instance=EnquiryTypeModal.objects.get(pk=pk))
            if edit_form.is_valid():
                edit_obj = edit_form.save()
                edit_obj.last_modified_date = time()
                edit_obj.last_modified_by = request.user
                edit_obj.save()
                messages.success(request, "Enquiry Type Updated Successfully")
                return redirect('enquiry_type_list')
            else:
                messages.error(request, edit_form.errors)
    context = {
        "title": f'{PROJECT_NAME} | Enquiry Type List',
        "create_form": create_form,
        "enq_type_obj": enq_type_obj,
        "edit_form": edit_form,
    }
    return render(request, 'Master_settings/Enquiry_Types/enquiry_type_settings.html', context)


@login_required(login_url='signin')
@permission_required(['enquiry_type.delete_enquirytypemodal'], login_url='permission_not_allowed')
def enquiry_type_delete(request, pk):
    """
    This function deletes an EnquiryTypeModal object and displays a success message, or an error message
    if the object is already in use.
    
    """
    enquiry_type_obj = EnquiryTypeModal.objects.get(pk=pk)
    try:
        enquiry_type_obj.delete()
        messages.success(request, "Enquiry Type Deleted Successfully")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("Delete is not possible.")
    return redirect('enquiry_type_list')