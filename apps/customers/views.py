import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import (
        Paginator, 
        EmptyPage, 
        PageNotAnInteger,
    )

from apps.customers.models import (
        Customer_Log, 
        Customers, 
        Contacts,
    )
from apps.customers.forms import (
        CreateCustomerForm, 
        CreateContactForm, 
        EditCustomerForm, 
        EditContactForm,
    )
from apps.enquiries.forms import CreateCustomerEnquiryForm
from apps.enquiries.models import Enquiries, Estimations
from apps.helper import customer_logger
from apps.product_master.models import Product
from amoeba.settings import (
        ENQ_ID, 
        MEDIA_ROOT, 
        PROJECT_NAME, 
        MEDIA_URL,
    )
from apps.projects.models import ProjectsModel
from apps.user.models import User


@login_required(login_url='signin')
@permission_required(['customers.add_customers'], login_url='permission_not_allowed')
def list_add_customers(request):
    """
    This function lists all the customers in a paginated view and allows the user to add new customers.
    """
    customers_objs = Customers.objects.all().order_by('name')
    enquiries = Enquiries.objects.filter(Q(main_customer=customers_objs.first()) | Q(customers=customers_objs.first()))
    customer_form = CreateCustomerForm()
    contact_form = CreateContactForm()
    if request.method == 'POST':
        if 'add_customer' in request.POST:
            customer_form = CreateCustomerForm(request.POST)
            contact_form = CreateContactForm(request.POST)
            # search = request.POST.get('search_data')
            if customer_form.is_valid() and contact_form.is_valid():
                form_obj = customer_form.save(commit=False)
                form_obj.created_by = request.user
                form_obj.save()
                
                contact_form_obj = contact_form.save(commit=False)
                contact_form_obj.created_by = request.user
                contact_form_obj.customer = form_obj
                contact_form_obj.is_primary = True
                contact_form_obj.save()
                
                form_obj.represented_by = contact_form_obj
                form_obj.save()
                
                message = f'Created New Customer {form_obj.name}.'
                customer_logger(customer=form_obj, message=message, action=1, user=request.user)
                messages.success(request, "Customer Created Successfully.")
            else:
                messages.error(request, customer_form.errors)
                print("error==>", customer_form.errors)
            
        return redirect('list_add_customers')
    
    context = {
        "title": f'{PROJECT_NAME} | List Customers',
        "customer_form": customer_form,
        "customers_obj": customers_objs,
        "customer_obj": customers_objs,
        "enquiries": enquiries,
        # 'pagination_start_no':start_no,
        "contact_form": contact_form,
    }
    return render(request, 'Customers/customers/list_customers.html', context)


@login_required(login_url='signin')
@permission_required(['customers.view_customers'], login_url='permission_not_allowed')
def view_customer(request, pk):
    """
    This function displays the details of a customer, allows editing of customer information, creation
    of customer enquiries, and displays related enquiries and projects.
    """
    customers_objs = Customers.objects.all().order_by('name')
    customers_obj = Customers.objects.get(pk=pk)
    enquiries = Enquiries.objects.filter(Q(main_customer=customers_obj) | Q(customers=customers_obj)).distinct('id')
    edit_form = EditCustomerForm(instance=customers_obj)
    projects = ProjectsModel.objects.filter(project_customer=customers_obj).order_by('id')
    enquiry_form = CreateCustomerEnquiryForm()
    contact_form = CreateContactForm()
    contacts_obj = Contacts.objects.filter(customer=pk).order_by('id')
    
    if request.method == 'POST':
        if 'add_customer_enq' in request.POST:
            add_customer_enquiry(request, enquiry_form, customers_obj)
        else:
            update_customer_profile(request, edit_form, customers_obj)

        return redirect('view_customer', pk=customers_obj.id)

    context = {
        "title": f"{PROJECT_NAME} | View Customer",
        "edit_form": edit_form,
        "enquiries": enquiries,
        "customer_obj": customers_obj,
        "enq_form": enquiry_form,
        "projects": projects,
        "customers_obj": customers_objs,
        "contact_form": contact_form,
        "contacts_obj": contacts_obj,
    }
    return render(request, 'Customers/customers/customer_profile_page.html', context)
    # return render(request, 'Customers/customers/customer_details_page.html', context)


def add_customer_enquiry(request, enquiry_form, customers_obj):
    enquiry_form = CreateCustomerEnquiryForm(request.POST)
    if enquiry_form.is_valid():
        _extracted_from_add_customer_enquiry_4(enquiry_form, request, customers_obj)
    else:
        messages.error(request, enquiry_form.errors)
        print('enquiry form error==>', enquiry_form.errors)


def _extracted_from_add_customer_enquiry_4(enquiry_form, request, customers_obj):
    enq_obj = enquiry_form.save(commit=False)
    price_master = request.POST.get('price_master')
    price_per_kg = request.POST.get('price_per_kg')
    enq_obj.created_by = request.user
    enq_obj.main_customer = customers_obj
    enq_obj.price_per_kg = price_per_kg
    enq_obj.pricing_id = int(price_master)
    enq_obj.save()
    enq_obj.customers.add(customers_obj)
    for members in enquiry_form.cleaned_data['enquiry_members']:
        enq_obj.enquiry_members.add(members.id)

    enq_obj.save()
    message = f'Created new Enquiry {enq_obj.title} in {customers_obj.name}.'
    customer_logger(customer=customers_obj, message=message, action=1, user=request.user)
    messages.success(request, "Customer Enquiry Created Successfully.")
    folder_path = os.path.join(MEDIA_ROOT, 'Quotations', enq_obj.enquiry_id)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        print("error.....")


def update_customer_profile(request, edit_form, customers_obj):
    edit_form = EditCustomerForm(request.POST, request.FILES, instance=customers_obj)
    if edit_form.is_valid():
        _extracted_from_update_customer_profile_4(edit_form, request, customers_obj)
    else:
        messages.error(request, edit_form.errors)
        print('edit form error==>', edit_form.errors)


def _extracted_from_update_customer_profile_4(edit_form, request, customers_obj):
    edit_obj = edit_form.save()
    edit_obj.last_modified_date = time()  # Note: Please import the 'time' function if not already done
    edit_obj.last_modified_by = request.user
    edit_obj.save()
    message = f'Updated {customers_obj.name}.'
    customer_logger(customer=customers_obj, message=message, action=2, user=request.user)
    messages.success(request, "Customer Profile Updated Successfully.")


@login_required(login_url='signin')
@permission_required(['customers.add_contacts'], login_url='permission_not_allowed')
def list_contacts(request, pk):
    """
    This function lists contacts for a specific customer and allows for the creation of new contacts.
    
    """
    contacts_obj = Contacts.objects.filter(customer=pk).order_by('id')
    
    customers = Customers.objects.get(pk=pk)
    contact_form = CreateContactForm()
    if request.method == 'POST':
        contact_form = CreateContactForm(request.POST)
        if contact_form.is_valid():
            
            form_obj = contact_form.save(commit=False)
            form_obj.created_by = request.user
            form_obj.customer_id = pk
            form_obj.save()
            if form_obj.is_primary:
                for contact in contacts_obj:
                    if contact.is_primary and form_obj.id != contact.id:
                        contact.is_primary = False
                        contact.save()
                customers.represented_by = form_obj
                customers.save()
            message = f'Added New Contact {form_obj.first_name} {form_obj.last_name} in {customers.name}.'
            customer_logger(customer=customers, message=message, action=1, user=request.user)
            messages.success(request, "Customer Contact Created Successfully")
        else:
            messages.error(request, contact_form.errors)
            print("error==>", contact_form.errors)
        return redirect('view_customer', pk=customers.id)
    
    context = {
        "title": f"{PROJECT_NAME} | List Contacts",
        "contact_form": contact_form,
        "pk": pk,
        "contacts_obj": contacts_obj,
        "customer_obj": customers,
    }
    return render(request, 'Customers/customers/customer_view_contact_list.html', context)


@login_required(login_url='signin')
@permission_required(['customers.change_contacts'], login_url='permission_not_allowed')
def edit_contact(request, pk):
    """
    This function edits a contact for a customer and logs the changes made by the user.
    
    """
    contact = Contacts.objects.get(pk=pk)
    customer = Customers.objects.get(pk=contact.customer.id)
    edit_form = EditContactForm(instance=contact)
    if request.method == 'POST':
        try:
            primary_contacts = Contacts.objects.get(customer=contact.customer, is_primary=True)
        except Exception:

            primary_contacts = None

        edit_form = EditContactForm(request.POST, instance=contact)
        if edit_form.is_valid():
            if not primary_contacts or primary_contacts == contact:
                edit_form_obj = edit_form.save(commit=False)
                edit_form_obj.last_modified_date = time()
                edit_form_obj.last_modified_by = request.user
                edit_form_obj.save()
                # customer = Customers.objects.get(pk=contact.customer.id)
                customer.represented_by = contact if edit_form_obj.is_primary else None
                customer.save()
                message = f'Updated {contact.first_name} {contact.last_name} Contact in {contact.customer.name}'
                customer_logger(customer=contact.customer, message=message, action=2, user=request.user)
                messages.success(request, "Customer Contact Updated Successfully")
            else:
                messages.error(request, "You can't update the Primary Customer Details! Please Remove old Primary contact before it update")
        else:
            messages.error(request, edit_form.errors)
        return redirect('view_customer', pk=customer.id)

    context = {
        "title": f"{PROJECT_NAME} | Edit Contacts",
        "edit_form": edit_form,
        "contacts_obj": contact,
    }
    return render(request, 'Customers/customers/edit_contacts.html', context)


@login_required(login_url='signin')
@permission_required(['customers.delete_contacts'], login_url='permission_not_allowed')
def delete_contact(request, pk):
    """
    This function deletes a contact from the Contacts model and logs the action in the customer_logger,
    displaying a success message if the deletion is successful and an error message if it is not.
    """
    contact = Contacts.objects.get(pk=pk)
    customers = contact.customer
    try:
        contact.delete()
        message = f' Deleted Contact {contact.first_name} {contact.last_name} from {contact.customer.name}'
        customer_logger(customer=contact.customer, message=message, action=3, user=request.user)
        messages.success(request, "Customer Contact Deleted Successfully")
    except Exception as e:
        messages.error(request, "Delete is not possible.")
        print("Delete is not possible.")
    # return redirect('list_add_customers')
    return redirect('view_customer', pk=customers.id)

@login_required(login_url='signin')
@permission_required(['customers.view_contacts'], login_url='permission_not_allowed')
def search_customers(request):
    """
    This function searches for customers based on a given name and displays them in a paginated list
    along with their enquiries.
    
    """
    customers = Customers.objects.all().order_by('name')
    enquiries = Enquiries.objects.filter(customers=customers.first())
    customer_form = CreateCustomerForm()
    name = request.POST.get('search_data')
    if request.method == 'POST':
        customers = Customers.objects.filter(name__icontains=name).order_by('name')
        enquiries = Enquiries.objects.filter(customers=customers.first()).order_by('id')
        customer_form = CreateCustomerForm()
        rows_per_page = 16
        page = request.GET.get('page', 1)
        paginator = Paginator(customers, rows_per_page)
        page_start = int(page)-1
        start_no = int(page_start) * rows_per_page
        try:
            customers_obj = paginator.page(page)
        except PageNotAnInteger:
            customers_obj = paginator.page(1)
        except EmptyPage:
            customers_obj = paginator.page(paginator.num_pages)
        context = {
            "title": f"{PROJECT_NAME} | Search Customer",
            "customer_form": customer_form,
            "customers_obj": customers_obj,
            "customer_obj": customers,
            "enquiries": enquiries,
            'pagination_start_no': start_no,
        }
        return render(request, 'Customers/customers/list_customers.html', context)
    return redirect('list_add_customers')


@login_required(login_url='signin')
def customer_log_modal(request, pk):
    """
    This function retrieves customer logs based on the user's role and renders them in a modal.
    
    """
    user = User.objects.get(pk=pk)
    if user.is_superuser:
        log_objs = Customer_Log.objects.all().order_by('-id')
    else:
        log_objs = Customer_Log.objects.filter(created_by=user).order_by('-id')
        
    context = {
        "log_objs": log_objs,
    }
    return render(request, 'Enquiries/enquiry_log_modal.html', context)


@login_required(login_url='signin')
def get_enquiry_versions(request, enquiry_id, customer_id):
    versions = Estimations.objects.filter(enquiry=enquiry_id)
    customer_obj = Customers.objects.get(pk=customer_id)
    enquiry = Enquiries.objects.get(pk=enquiry_id)
    enquiries = Enquiries.objects.filter(customers=customer_obj)
    
    context = {
        "versions": versions,
        "customer_obj": customer_obj,
        "enquiries": enquiries,
        "enquiry": enquiry
    }
    return render(request, "Customers/customers/enquiry_versions.html", context)


@login_required(login_url='signin')
def version_quotation(request, enquiry_id, customer_id, version_id):
    
    version = Estimations.objects.get(pk=version_id)
    versions = Estimations.objects.filter(enquiry=enquiry_id)
    customer_obj = Customers.objects.get(pk=customer_id)
    enquiry = Enquiries.objects.get(pk=enquiry_id)
    enquiries = Enquiries.objects.filter(customers=customer_obj)

    if version.version.version == '0':
        version_name = 'Original'
    else:
        version_name = f'Revision {version.version.version}'

    directory = os.path.join(MEDIA_URL, 'Quotations')
    file_path = f'{str(version.enquiry.enquiry_id)}/{str(customer_obj.name)}/{str(version_name)}/'
    open_path = os.path.join(directory, file_path).replace("\\", '/')
    if os.path.exists(open_path):
        for root, dirs, files in os.walk(open_path):
            for file in files:
                file_path = os.path.join(root, file).replace("\\", '/')
    else:
        file_path = None
    context = {
        "versions": versions,
        "customer_obj": customer_obj,
        "enquiries": enquiries,
        "version": version,
        "domain": f'http://{str(request.get_host())}',
        "file_path": file_path,
        "enquiry": enquiry
        
    }
    return render(request, "Customers/customers/enquiry_versions.html", context)

@login_required(login_url='signin')
def edit_customer(request, pk):
    customers_obj = Customers.objects.get(pk=pk)
    try:
        contact = Contacts.objects.get(pk=customers_obj.represented_by.id)
    except Exception:
        contact = None
    customer_form = CreateCustomerForm(instance=customers_obj)
    if contact:
        contact_form = CreateContactForm(instance=contact)
    else:
        contact_form = CreateContactForm()
        
    if request.method == 'POST':
        if 'add_customer' in request.POST:
            customer_form = CreateCustomerForm(request.POST, instance=customers_obj)
            if contact:
                contact_form = CreateContactForm(request.POST, instance=contact)
            else:
                contact_form = CreateContactForm(request.POST)
                
            # search = request.POST.get('search_data')
            if customer_form.is_valid(): 
                form_obj = customer_form.save(commit=False)
                form_obj.last_modified_date = time()
                form_obj.last_modified_by = request.user
                form_obj.save()
                
                if contact_form.is_valid():
                    contact_form_obj = contact_form.save(commit=False)
                    contact_form_obj.last_modified_date = time()
                    contact_form_obj.last_modified_by = request.user
                    contact_form_obj.created_by = request.user
                    
                    contact_form_obj.customer = form_obj
                    contact_form_obj.is_primary = True
                    contact_form_obj.save()
                    
                    form_obj.represented_by = contact_form_obj
                    form_obj.save()
                    
                    message = f'Updated Customer {form_obj.name}.'
                    customer_logger(customer=form_obj, message=message, action=1, user=request.user)
                    messages.success(request, "Customer Updated Successfully.")
            else:
                messages.error(request, customer_form.errors)
                print("error==>", customer_form.errors)
            
        return redirect('list_add_customers')
    context = {
        "customer_form": customer_form,
        "customers_obj": customers_obj,
        "contact_form": contact_form,
    }
    return render(request, "Customers/customers/edit_customer.html", context)
    

@login_required(login_url='signin')
def delete_customer(request, pk):
    """
        The function `delete_base` deletes a Brands object with the specified primary key (pk) and displays
        a success message if the deletion is successful, otherwise it displays an error message.
       
    """
    if request.method == "POST":
        try:
            customers_obj = Customers.objects.get(pk=pk)
            customers_obj.delete()
            messages.success(request, "Customer Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_add_customers')

    context = {"url": f"/Customers/delete_customer/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)

