from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.invoice_settings.models import Invoice_Settings
from apps.invoice_settings.forms import CreateInvoiceSettingsForm, EditInvoiceSettingsForm
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
@permission_required(
    [
        'invoice_settings.view_invoice_settings', 
        'invoice_settings.add_invoice_settings', 
        'invoice_settings.change_invoice_settings',
    ], login_url='permission_not_allowed')
def invoice_settings_list(request, pk=None):
    """
    This function displays a list of invoice settings and allows the user to create new settings or edit
    existing ones.
    """
    invoice_settings_obj = Invoice_Settings.objects.all().order_by('id')
    create_form = CreateInvoiceSettingsForm()
    edit_form = EditInvoiceSettingsForm()
    if request.method == 'POST':
        if 'create_invoice_settings' in request.POST:
            create_form = CreateInvoiceSettingsForm(request.POST)
            if create_form.is_valid():
                create_obj = create_form.save(commit=False)
                create_obj.created_by = request.user
                create_obj.save()
                return redirect('invoice_settings_list')
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditInvoiceSettingsForm(request.POST, instance=Invoice_Settings.objects.get(pk=pk))
            if edit_form.is_valid():
                edit_obj = edit_form.save()
                edit_obj.last_modified_date = time()
                edit_obj.last_modified_by = request.user
                edit_obj.save()
                return redirect('invoice_settings_list')
            else:
                messages.error(request, edit_form.errors)
    context = {
        "title": PROJECT_NAME + " | Invoice Settings List",
        "create_form": create_form,
        "invoice_settings_obj": invoice_settings_obj,
        "edit_form": edit_form,
    }
    return render(request, 'Master_settings/Invoice_Settings/invoice_settings_list.html', context)


@login_required(login_url='signin')
@permission_required(['invoice_settings.delete_invoice_settings'], login_url='permission_not_allowed')
def invoice_settings_delete(request, pk):
    """
    This function deletes an invoice setting object and displays an error message if it is already in
    use.
    
    """
    invoice_settings_obj = Invoice_Settings.objects.get(pk=pk)
    try:
        invoice_settings_obj.delete()
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("Delete is not possible.")
    return redirect('invoice_settings_list')
