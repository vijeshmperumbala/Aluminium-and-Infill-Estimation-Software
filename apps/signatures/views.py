from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.signatures.models import Signatures
from apps.signatures.forms import CreateSignatureForm, EditSignatureForm

from amoeba.settings import PROJECT_NAME


@login_required(login_url="signin")
@permission_required(['signatures.view_signatures', 'signatures.add_signatures', 'signatures.change_signatures'], login_url='permission_not_allowed')
def list_signatures(request, pk=None):
    """
    It's a function that renders a template with a list of signatures, and a form to create a new
    signature.
    
    :param pk: The primary key of the object you want to edit
    :return: A list of signatures.
    """
    signatures = Signatures.objects.all().order_by('id')
    create_form = CreateSignatureForm()
    if pk:
        sign = Signatures.objects.get(pk=pk)
        edit_form = EditSignatureForm(instance=sign)
    else:
        edit_form = EditSignatureForm()

    if request.method == 'POST':
        if 'create_signature' in request.POST:
            create_form = CreateSignatureForm(request.POST, request.FILES)
            if create_form.is_valid():
                form_obj = create_form.save(commit=False)
                form_obj.user = request.user
                form_obj.created_by = request.user
                form_obj.save()
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditSignatureForm(
                request.POST, request.FILES, instance=Signatures.objects.get(pk=pk))
            if edit_form.is_valid():
                form_obj = edit_form.save(commit=False)
                form_obj.user = request.user
                form_obj.created_by = request.user
                form_obj.save()
                messages.success(request, 'Signature Successfully Deleted.')
                
            else:
                messages.error(request, edit_form.errors)

    context = {
        'title': PROJECT_NAME + ' | Signatures List',
        'signatures': signatures,
        'create_form': create_form,
        'edit_form': edit_form
    }
    return render(request, 'Master_settings/Signatures/signatures.html', context)

@login_required(login_url="signin")
def sign_edit(request, pk):
    """
    This function edits a signature object and saves the changes made by the user.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the user's session and any submitted data
    :param pk: pk stands for "primary key" and it is used to identify a specific object in a database
    table. In this case, it is used to retrieve a specific signature object from the Signatures table in
    the database
    :return: a rendered HTML template "update_signature.html" with the context variables "edit_form" and
    "signature".
    """
    sign = Signatures.objects.get(pk=pk)
    edit_form = EditSignatureForm(instance=sign)
    if request.method == 'POST':
        edit_form = EditSignatureForm(
            request.POST, request.FILES, instance=Signatures.objects.get(pk=pk))
        if edit_form.is_valid():
            form_obj = edit_form.save(commit=False)
            form_obj.user = request.user
            form_obj.created_by = request.user
            form_obj.save()
            messages.success(request, 'Signature Successfully Deleted.')
        else:
            messages.error(request, edit_form.errors)
        
    context = {
        "edit_form": edit_form,
        "signature": sign,
    }
    return render(request, "Master_settings/Signatures/update_signature.html", context)

@login_required(login_url='signin')
def delete_signature(request, pk):
    """
    This function deletes a signature object with a given primary key and displays a success message, or
    an error message if the object is already used in an application.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the user making the request and any data submitted with the request
    :param pk: pk stands for "primary key". In this context, it refers to the unique identifier of a
    specific Signature object in the database. The function is designed to delete the Signature object
    with the given primary key (pk) from the database
    :return: a redirect to the 'list_signatures' URL.
    """
    try:
        Signatures.objects.get(pk=pk).delete()
        messages.success(request, 'Signature Successfully Deleted.')
    except:
        messages.error(request, 'Unable to delete the data. Already used in application.')
        
    return redirect('list_signatures')