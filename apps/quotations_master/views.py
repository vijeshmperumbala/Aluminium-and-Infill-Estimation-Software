from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, JsonResponse

from apps.quotations_master.models import Quotations_Master
from apps.quotations_master.forms import GeneralQuotationMasterCreate, ShortQuotationMasterCreate
from amoeba.settings import PROJECT_NAME, TINYMC_API


@login_required(login_url='signin')
@permission_required(['quotations_master.view_quotations_master'], login_url='permission_not_allowed')
def list_quotations_master(request):
    """
    This function retrieves and sorts Quotations_Master objects and renders them in a template.
    
    :param request: The request object represents the HTTP request that the user has made to access a
    particular URL. It contains information about the user's request, such as the HTTP method used (GET,
    POST, etc.), any data submitted with the request, and the user's session information
    :return: a rendered HTML template with context variables including a list of all Quotations_Master
    objects, a list of short quotations, a list of general quotations, and a TinyMCE API key.
    """
    quotations_obj = Quotations_Master.objects.all().order_by('id')
    short_quotation = Quotations_Master.objects.filter(q_type=2).order_by('id')
    general_quotation = Quotations_Master.objects.filter(q_type=1).order_by('id')
    context = {
        'title': PROJECT_NAME + ' | General Quotation Templates ',
        'quotations_obj': quotations_obj,
        'short_quotation': short_quotation,
        'general_quotation': general_quotation,
        "tinymc_api": TINYMC_API,
    }
    return render(request, 'Master_settings/Quotation_Master/quotation_master.html', context)


@login_required(login_url='signin')
@permission_required(['quotations_master.add_quotations_master'], login_url='permission_not_allowed')
def create_short_quotation_template(request):
    """
    This function creates a short quotation template and saves it to the database.
    
    :param request: The request object represents the current HTTP request that the user has made to the
    server. It contains information about the user's request, such as the HTTP method used (GET, POST,
    etc.), any data submitted in the request, and the user's session information
    :return: a rendered HTML template with a context dictionary containing a form object and a boolean
    value for "create".
    """
    short_quotation_form = ShortQuotationMasterCreate()
    if request.method == 'POST':
        short_quotation_form = ShortQuotationMasterCreate(request.POST, request.FILES)
        if short_quotation_form.is_valid():
            form_obj = short_quotation_form.save(commit=False)
            form_obj.created_by = request.user
            form_obj.q_type = 2
            form_obj.save()
        return redirect('list_quotations_master')
    context = {
        "form": short_quotation_form,
        "create": True,
    }
    return render(request, 'Master_settings/Quotation_Master/short_quotation_template_modal.html', context)


@login_required(login_url='signin')
@permission_required(['quotations_master.change_quotations_master'], login_url='permission_not_allowed')
def edit_short_quotation_template(request, pk):
    """
    This function edits a short quotation template and saves the changes made by the user.
    
    :param request: The request object represents the current HTTP request that the user has made to
    access the view
    :param pk: pk is a parameter that represents the primary key of a Quotations_Master object, which is
    used to retrieve the specific object from the database
    :return: a rendered HTML template with a context dictionary containing a form, a quotation template,
    and a boolean value indicating whether the form is for creating a new quotation or editing an
    existing one.
    """
    quotation = Quotations_Master.objects.get(pk=pk)
    short_quotation_form = ShortQuotationMasterCreate(instance=quotation)
    if request.method == 'POST':
        short_quotation_form = ShortQuotationMasterCreate(
            request.POST, request.FILES, instance=quotation)
        if short_quotation_form.is_valid():
            form_obj = short_quotation_form.save(commit=False)
            form_obj.last_modified_by = request.user
            form_obj.last_modified_date = time()
            form_obj.save()
        return redirect('list_quotations_master')
    context = {
        "form": short_quotation_form,
        "quotation_template": quotation,
        "create": False,
    }
    return render(request, 'Master_settings/Quotation_Master/short_quotation_template_modal.html', context)


@login_required(login_url='signin')
@permission_required(['quotations_master.delete_quotations_master'], login_url='permission_not_allowed')
def delete_quotation_template(request, pk):
    """
    This function deletes a quotation template and displays a success message, or an error message if
    the template is already in use.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: pk stands for primary key. It is a unique identifier for a specific record in a database
    table. In this case, it is used to identify the specific Quotations_Master object that needs to be
    deleted from the database
    :return: a redirect to the 'list_quotations_master' URL.
    """
    quotation = Quotations_Master.objects.get(pk=pk)
    try:
        quotation.delete()
        messages.success(request, "Quotation Template Successfully Deleted.")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("Delete is not possible.")
    return redirect('list_quotations_master')


@login_required(login_url='signin')
@permission_required(['quotations_master.add_quotations_master'], login_url='permission_not_allowed')
def create_general_quotation_template(request):
    """
    This function creates a general quotation template and saves it to the database.
    
    :param request: The request parameter is an HttpRequest object that represents the current request
    made by the user. It contains information about the current request, such as the HTTP method used,
    the user agent, the requested URL, and any data submitted in the request
    :return: a rendered HTML template with a context dictionary containing a form object and a boolean
    value 'create'.
    """
    general_quotation_form = GeneralQuotationMasterCreate()
    if request.method == 'POST':
        general_quotation_form = GeneralQuotationMasterCreate(request.POST, request.FILES)
        if general_quotation_form.is_valid():
            form_obj = general_quotation_form.save(commit=False)
            form_obj.created_by = request.user
            form_obj.q_type = 1
            form_obj.save()
        return redirect('list_quotations_master')
    context = {
        "form": general_quotation_form,
        "create": True,
    }
    return render(request, 'Master_settings/Quotation_Master/general_quotation_template_modal.html', context)


@login_required(login_url='signin')
@permission_required(['quotations_master.change_quotations_master'], login_url='permission_not_allowed')
def edit_general_quotation_template(request, pk):
    """
    This function edits a general quotation template and saves the changes made by the user.
    
    :param request: The request object represents the current HTTP request that the user has made to
    access the view
    :param pk: pk is a parameter that represents the primary key of a Quotations_Master object. It is
    used to retrieve the specific object from the database and edit its details
    :return: a rendered HTML template with the context variables passed to it.
    """
    quotation = Quotations_Master.objects.get(pk=pk)
    general_quotation_form = GeneralQuotationMasterCreate(instance=quotation)
    if request.method == 'POST':
        general_quotation_form = GeneralQuotationMasterCreate(
            request.POST, request.FILES, instance=quotation)
        if general_quotation_form.is_valid():
            form_obj = general_quotation_form.save(commit=False)
            form_obj.last_modified_by = request.user
            form_obj.last_modified_date = time()
            form_obj.save()
        return redirect('list_quotations_master')
    context = {
        "form": general_quotation_form,
        "create": False,
        "quotation_template": quotation,
    }
    return render(request, 'Master_settings/Quotation_Master/general_quotation_template_modal.html', context)


@login_required(login_url='signin')
def get_short_quotation_template(request, pk):
    """
    This function retrieves a short quotation template from the database and returns its details as a
    JSON response.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the HTTP method, headers, and query parameters
    :param pk: pk is a parameter that represents the primary key of a Quotations_Master object. It is
    used to retrieve a specific quotation template from the database
    :return: a JSON response with the context dictionary containing the values of 'master_remarks',
    'short_terms_and_conditions', 'short_description', and 'template_id'. The status code of the
    response is 200.
    """
    quotation_template = Quotations_Master.objects.get(pk=pk)
    context = {
        'master_remarks': quotation_template.master_remarks,
        'short_terms_and_conditions': quotation_template.short_terms_and_conditions,
        'short_description': quotation_template.short_description,
        'template_id': quotation_template.id
    }
    return JsonResponse(context, status=200)

@login_required(login_url='signin')
def get_general_quotation_template(request, pk):
    """
    This function retrieves a quotation template from the database and returns its fields as a JSON
    response.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and query parameters
    :param pk: The primary key of the Quotations_Master object that we want to retrieve
    :return: a JSON response containing various fields of a Quotations_Master object identified by the
    primary key (pk) passed as an argument to the function. The fields being returned include
    general_terms_and_conditions, general_description, master_terms_of_payment, template_id,
    master_exclusions, q_type, master_remarks, short_terms_and_conditions, and short_description.
    """
    quotation_template = Quotations_Master.objects.get(pk=pk)
    context = {
        'general_terms_and_conditions': quotation_template.general_terms_and_conditions,
        'general_description': quotation_template.general_description,
        'master_terms_of_payment': quotation_template.master_terms_of_payment,
        'template_id': quotation_template.id,
        'master_exclusions': quotation_template.master_exclusions,
        'q_type': quotation_template.q_type,
        
        'master_remarks': quotation_template.master_remarks,
        'short_terms_and_conditions': quotation_template.short_terms_and_conditions,
        'short_description': quotation_template.short_description,
    }
    return JsonResponse(context, status=200, safe=True)

@login_required(login_url='signin')
def duplicate_quotation_master(request, pk):
    """
    This function duplicates a quotation template and saves it with a new primary key and creation date.
    
    :param request: The request object represents the current HTTP request that the user has made to the
    server. It contains information about the user's request, such as the HTTP method used (GET, POST,
    etc.), the URL requested, any data submitted in the request, and more
    :param pk: pk is a parameter that represents the primary key of a Quotations_Master object. It is
    used to retrieve the specific Quotations_Master object that needs to be duplicated
    :return: a redirect to the "list_quotations_master" URL after duplicating a quotation template and
    displaying a success message.
    """
    quotation_template = Quotations_Master.objects.get(pk=pk)
    quotation_template.pk = None
    quotation_template.created_by = request.user
    quotation_template.created_date = time()
    quotation_template.save()
    messages.success(request, "Successfully Duplicated Quotation Template")
    return redirect("list_quotations_master")