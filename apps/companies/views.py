from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse

from apps.companies.models import Companies
from apps.companies.forms import CreateCompanyForm

from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
@permission_required(['companies.view_companies'], login_url='permission_not_allowed')
def company_list(request):
    """
    This function retrieves a list of all companies from the database and renders it in a template.
    
    """
    compay_obj = Companies.objects.all().order_by('id')
    context = {
        'title': f'{PROJECT_NAME} | Company List',
        'company_obj': compay_obj,
    }
    return render(request, 'Settings/Companies/companies_list.html', context)


@login_required(login_url='signin')
def create_company(request):
    """
    This function creates a new company object and saves it to the database if the form is valid, and
    redirects to the company list page.
    
    """
    form = CreateCompanyForm()
    if request.method == 'POST':
        form = CreateCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully created company")
        else:
            messages.error(request, form.errors)
        return redirect('company_list')
    context = {
        'form': form,
    }
    return render(request, 'Settings/Companies/create_company_modal.html', context)


@login_required(login_url='signin')
@permission_required(['companies.change_companies'], login_url='permission_not_allowed')
def edit_company(request, pk):
    """
    This function edits a company object and saves the changes if the form is valid, otherwise it
    displays the form errors.
    
    """
    compay_obj = Companies.objects.get(pk=pk)
    form = CreateCompanyForm(instance=compay_obj)
    if request.method == 'POST':
        form = CreateCompanyForm(request.POST, request.FILES, instance=compay_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully Updated company")
        else:
            messages.error(request, form.errors)
        return redirect('company_list')
    context = {
        'form': form,
        'compay_obj': compay_obj
    }
    return render(request, 'Settings/Companies/create_company_modal.html', context)


@login_required(login_url='signin')
@permission_required(['companies.delete_companies'], login_url='permission_not_allowed')
def delete_comapny(request, pk):
    """
    This function deletes a company object and displays a success or error message depending on whether
    the deletion was successful or not.
    
    """
    company_obj = Companies.objects.get(pk=pk)
    if request.method == 'POST':
        try:
            company_obj.delete()
            messages.success(request, "Company Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")

        return redirect('company_list')

    context = {
            "url": f"/Companies/delete_comapny/{str(company_obj.id)}/"
        }
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
@permission_required(['companies.view_companies'], login_url='permission_not_allowed')
def get_company_details(request, pk):
    """
    This function retrieves details of a company object and returns them in a JSON response.
    
    """
    company_obj = Companies.objects.get(pk=pk)
    data = {
        'name': company_obj.company_name,
        'email': company_obj.company_email,
        'address': company_obj.company_address
    }
    return JsonResponse(data, status=200)
