from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.industry_type.models import IndustryTypeModal
from apps.industry_type.forms import CreateIndustryTypeForm, EditIndustryTypeForm
from apps.product_master.models import Product
from amoeba.settings import PROJECT_NAME


# Create your views here.
@login_required(login_url='signin')
@permission_required(
    [
        'industry_type.add_industrytypemodal', 
        'industry_type.view_industrytypemodal', 
        'industry_type.change_industrytypemodal',
    ], login_url='permission_not_allowed')
def industry_type_list(request, pk=None):
    """
    This function displays a list of industry types and allows for the creation and editing of industry
    types through forms.
    """
    ind_type_obj = IndustryTypeModal.objects.all().order_by('id')
    create_form = CreateIndustryTypeForm()
    edit_form = EditIndustryTypeForm()
    if request.method == 'POST':
        if 'create_industry_type' in request.POST:
            create_form = CreateIndustryTypeForm(request.POST)
            if create_form.is_valid():
                create_obj = create_form.save(commit=False)
                # create_obj.created_by = request.user
                create_obj.save()
                return redirect('industry_type_list')
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditIndustryTypeForm(request.POST, instance=IndustryTypeModal.objects.get(pk=pk))
            if edit_form.is_valid():
                edit_obj = edit_form.save()
                edit_obj.last_modified_date = time()
                edit_obj.last_modified_by = request.user
                edit_obj.save()
                return redirect('industry_type_list')
            else:
                messages.error(request, edit_form.errors)
    context = {
        "title": PROJECT_NAME + " | Industry Type List",
        "create_form": create_form,
        "ind_type_obj": ind_type_obj,
        "edit_form": edit_form,
    }
    return render(request, 'Master_settings/Industry_Type/industry_type_settings.html', context)


@login_required(login_url='signin')
@permission_required(['industry_type.delete_industrytypemodal'], login_url='permission_not_allowed')
def industry_type_delete(request, pk):
    """
    This function deletes an IndustryTypeModal object with the given primary key and returns a redirect
    to the industry type list page, but if the object is already used in an application, it displays an
    error message and does not delete the object.
    """
    industry_type_obj = IndustryTypeModal.objects.get(pk=pk)
    try:
        industry_type_obj.delete()
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("Delete is not possible.")
    return redirect('industry_type_list')