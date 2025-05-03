from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission, Group
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
import subprocess
from django.http import JsonResponse, FileResponse
import json

from apps.customers.forms import CreateCustomerForm
from apps.customers.models import Customers
from apps.enquiries.forms import CreateEnquiryForm
from apps.enquiries.models import Enquiries, Estimations
from apps.estimations.models import EstimationBuildings, EstimationMainProduct, Temp_EstimationBuildings, Temp_EstimationMainProduct
from apps.helper import reset_users
from apps.projects.models import ProjectsModel
from apps.user.forms import ChangePasswordFrom, CreateUser, CreateUserRoleForm

from apps.user.models import User
from amoeba.settings import PROJECT_NAME, DATABASES


# Basic Functions

def signin(request):
    """
    This function handles user authentication and login for a web application.
    """
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            return redirect('dashboard')
        username = request.POST.get('email')
        password = request.POST.get('password')
        if username == "" or password == "":
            print("password and username needed.")
            return redirect('signin')
        else:
            user = authenticate(
                request, username=username, password=password)
            if user is None:
                print('error')
                return redirect('signin')

            else:
                login(request, user)
                return redirect('dashboard')
    context = {"title": f"Login | {PROJECT_NAME}"}
    return render(request, 'signin.html', context)


def signout(request):
    """
    The function logs out the user and redirects them to the sign-in page.
    """
    logout(request)
    return redirect('signin')


def error_404_view(request, exception):
    """
    This is a view function in Django that renders a 404 error page.
    """
    return render(request, '404.html')


def permission_not_allowed(request):
    """
    This function returns a rendered 403.html page when a user does not have permission to access a
    certain page.
    """
    return render(request, '403.html')


def create_enquiry(request, enquiry_type):
    """
    This function creates an enquiry form and redirects to the dashboard if the form is valid, otherwise
    it displays an error message.
    """
    enquiry_form = CreateEnquiryForm(request.POST)
    if enquiry_form.is_valid():
        _extracted_from_create_enquiry_4(enquiry_form, request, enquiry_type)
    else:
        messages.error(request, enquiry_form.errors)
    return redirect('dashboard')


def _extracted_from_create_enquiry_4(enquiry_form, request, enquiry_type):
    """
    This function extracts data from an enquiry form, sets some fields, saves the form, and displays a
    success message.
    """
    form_obj = enquiry_form.save(commit=False)
    form_obj.created_by = request.user
    form_obj.users = request.user
    form_obj.price_per_kg = float(request.POST.get('price_per_kg'))
    form_obj.labour_percentage = int(request.POST.get('labour'))
    form_obj.overhead_percentage = int(request.POST.get('additional'))
    form_obj.pricing_id = int(request.POST.get('price_master'))
    form_obj.structural_price = form_obj.sealant_pricing.structural_price
    form_obj.weather_price = form_obj.sealant_pricing.weather_price
    form_obj.save()
    enquiry_form.save_m2m()
    if enquiry_type == '1':
        form_obj.main_customer = form_obj.customers.all().first()
    else:
        print("TENDER HAS NO MAIN CUSTOMER...")
    form_obj.save()
    messages.success(request, 'Enquiry created successfully.')


def create_customer(request):
    """
    This function creates a new customer object with data from a form submitted by a user and saves it
    to the database, with the user who created it being recorded, and displays a success message if
    successful or an error message if not.
    """
    customer_form = CreateCustomerForm(request.POST)
    if customer_form.is_valid():
        form_obj = customer_form.save(commit=False)
        form_obj.created_by = request.user
        form_obj.save()
        messages.success(request, 'Customer created successfully.')
    else:
        messages.error(request, customer_form.errors)
    return redirect('dashboard')


def user_rank_details():
    """
    This function retrieves the rank details of users based on their enquiry ratings.
    """
    enquiry_members = {
        member
        for enquiry in Enquiries.objects.all()
        for member in enquiry.enquiry_members.all()
    }
    
    user_rank = []
    for member in enquiry_members:
        data = {
            "name": None,
            "score": None,
            "enquiry": None,
            "user_id": None,
        }
        enquiries_list = Enquiries.objects.filter(Q(created_by=member.id) | Q(enquiry_members=member.id))
        user_data = User.objects.get(pk=member.id)
        rank = 0
        count = 0
        for enquiry in enquiries_list:
            if enquiry.rating:
                rank += enquiry.rating
                count += 1
        if count > 0:
            final_rank = rank / count
            data['score'] = float(final_rank)
            data['name'] = user_data
            data['enquiry'] = count
            data['user_id'] = user_data.id
            
        else:
            data['score'] = 0
            data['enquiry'] = 0
            data['name'] = user_data
            data['user_id'] = user_data.id

        user_rank.append(data)
    return sorted(user_rank, key=lambda x: x['score'], reverse=True)
    

# User related Functions
@login_required(login_url='signin')
def dashboard(request):
    """
    This function generates data for a dashboard page, including counts of various objects, rankings of
    users based on their involvement in enquiries, and forms for creating new enquiries and customers.
    
    """
    
    projects = ProjectsModel.objects.exclude(status=0).count()
    enquiries = Enquiries.objects.exclude(status=0)
    if request.user.is_superuser:
        review = enquiries.filter(status=9).count()
        estimating = enquiries.filter(status=2).count()
    else:
        review = enquiries.filter(Q(status=9) & Q(Q(enquiry_members__in=[request.user.id]) | Q(users=request.user.id) | Q(created_by=request.user.id))).count()
        estimating = enquiries.filter(Q(status__in=[1, 2]) & Q(Q(enquiry_members__in=[request.user.id]) | Q(users=request.user.id) | Q(created_by=request.user.id))).count()
        
        
    # send = Enquiries.objects.filter(status=10).count()
    # approvals = Enquiries.objects.filter(status=8).count()
    # pending_enquiries = enquiries.exclude(status__in=[6, 4, 7, 8]).count() - send
    
    customers = Customers.objects.all().count()

    user_rank = user_rank_details()
    
    enquiry_form = CreateEnquiryForm()
    customer_form = CreateCustomerForm()

    if request.method == 'POST':
        enquiry_type = request.POST.get('enquiry_type')
        if 'enquiry_create' in request.POST:
            create_enquiry(request, enquiry_type)
        elif 'create_customer' in request.POST:
            create_customer(request)
            
    
    # enquiry_objs = Enquiries.objects.all()
    # for  obj in enquiry_objs:
    #     buildings_objs = EstimationBuildings.objects.filter(estimation__enquiry=obj)
    #     for building in buildings_objs:
    #         products = EstimationMainProduct.objects.select_related('building').filter(building=building, product_index__isnull=True).order_by('associated_key', 'id')
    #         for i, pro in enumerate(products):
    #             if i == 0:
    #                 i += 1
                    
    #             pro.product_index = i
    #             pro.save()
            
    #     temp_buildings_objs = Temp_EstimationBuildings.objects.filter(estimation__enquiry=obj)
    #     for building in temp_buildings_objs:
    #         temp_products = Temp_EstimationMainProduct.objects.select_related('building').filter(building=building, product_index__isnull=True).order_by('associated_key', 'id')
    #         for j, tpro in enumerate(temp_products):
    #             if j == 0:
    #                 j += 1
    #             tpro.product_index = j
    #             tpro.save()
            
    
            
    context = {
        "title": f"Dashboard | {PROJECT_NAME}",
        "projects": projects,
        "enquiries": enquiries.count(),
        "customers": customers,
        # "approvals": approvals,
        # "pending_enquiries": pending_enquiries,
        "enquiry_form": enquiry_form,
        "customer_form": customer_form,
        "user_rank": user_rank,
        "review": review,
        "estimating": estimating,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='signin')
def side_settings_menu(request):
    """
    This function renders a settings menu page with a title using the Django render function.
    
    """
    context = {"title": f"{PROJECT_NAME} | Menu "}
    return render(request, 'settings_menu.html', context)


@login_required(login_url='signin')
@permission_required(['user.add_user'], login_url='permission_not_allowed')
def list_user_roles(request):
    """
    This function retrieves all user groups and renders them in a template for managing user roles.
    
    """
    groups = Group.objects.all().order_by('id')
    context = {"title": f"{PROJECT_NAME} | User Roles", "groups": groups}
    return render(request, 'Settings/User_Roles/user_roles.html', context)


@login_required(login_url='signin')
@permission_required(['user.add_user'], login_url='permission_not_allowed')
def create_uesr_role(request):
    """
    This function creates a user role with selected permissions and saves it to the database.
    
    """
    permissions = Permission.objects.filter(content_type__gt=5).order_by('content_type', 'id').exclude(content_type__in=[4, 5, 13, 67]).distinct('content_type')
    group_form = CreateUserRoleForm()

    if request.method == 'POST':
        group_form = CreateUserRoleForm(request.POST)
        if group_form.is_valid():
            try:
                group = group_form.save(commit=False)
                perms_codenames = [key.split('-')[-1] for key, value in request.POST.items() if key.startswith('user_role-')]
                perms_qs = Permission.objects.filter(codename__in=perms_codenames)
                group.permissions.add(*perms_qs)
                group.save()
                messages.success(request, 'User Role successfully created.')
                return redirect('list_user_roles')
            except Exception as e:
                messages.error(request, f"An error occurred while creating the user role: {e}")

        else:
            messages.error(request, 'Invalid form data. Please correct the errors and try again.')

    context = {
        "title": f"{PROJECT_NAME} | Create User Roles",
        "permissions": permissions,
        "group_form": group_form,
    }
    return render(request, "Settings/User_Roles/add_user_role_modal.html", context)


@login_required(login_url='signin')
@permission_required(['user.add_user'], login_url='permission_not_allowed')
def update_user_role(request, pk):
    """
    This function updates a user role with new permissions based on user input.
    
    """
    group = Group.objects.get(id=pk)
    group_form = CreateUserRoleForm(instance=group)
    old_permissions = group.permissions.all()
    permissions = Permission.objects.filter(content_type__gt=5).order_by('content_type', 'id').exclude(content_type__in=[4, 5, 13, 67 ]).distinct('content_type')

    if request.method == 'POST':
        group_form = CreateUserRoleForm(request.POST, instance=group)
        if group_form.is_valid():
            if old_permissions:
                group.permissions.clear()
            data = group_form.save()
            perms_codenames = [key.split(
                '-')[-1] for key, value in request.POST.items() if key.startswith('user_role-')]
            for perms_code in perms_codenames:
                perm = permissions.get(codename=perms_code)
                data.permissions.add(perm)
            data.save()
            messages.success(request, 'Role successfully updated.')
            return redirect('list_user_roles')
    context = {
        "title": f"{PROJECT_NAME} | Update Role",
        "group_form": group_form,
        'permissions': permissions,
        "old_permissions": old_permissions,
        "group": group,
    }
    return render(request, "Settings/User_Roles/add_user_role_modal.html", context)


@login_required(login_url='signin')
@permission_required(['user.view_user'], login_url='permission_not_allowed')
def view_role(request, pk):
    """
    This function retrieves a specific group object and renders a view_roles.html template with the
    group object as context.
    
    """
    group = Group.objects.get(id=pk)
    context = {"title": f"{PROJECT_NAME} | View Role", "group": group}
    return render(request, "Settings/User_Roles/view_roles.html", context)


@login_required(login_url='signin')
@permission_required('user.view_user', login_url='permission_not_allowed')
def list_users(request):
    """
    The function retrieves a list of users from the database and renders them in a template for viewing.
    
    """
    user_obj = User.objects.all().exclude(is_superuser=True).order_by('id')
    context = {"title": f"{PROJECT_NAME} | View Users", "user_obj": user_obj}
    return render(request, "Settings/User/list_user.html", context)


@login_required(login_url='signin')
@permission_required('user.add_user', login_url='permission_not_allowed')
def create_user(request):
    """
    This function creates a user with a specified role and saves it to the database.
    
    """
    group_obj = Group.objects.all().order_by('id')
    form = CreateUser()
    if request.method == "POST":
        # department = request.POST.get('department')
        department_estimation = request.POST.get('department_estimation')
        department_project = request.POST.get('department_project')
        department_production = request.POST.get('department_production')
        department_fabrication = request.POST.get('department_fabrication')
        department_qaqc = request.POST.get('department_qaqc')
        
        department_procurement = request.POST.get('department_procurement')
        department_delivery = request.POST.get('department_delivery')
        department_inspection = request.POST.get('department_inspection')
        
        
        if role := request.POST.get('user_role'):
            form = CreateUser(request.POST, request.FILES)
            if form.is_valid():
                user = form.save()
                role_data = group_obj.get(pk=role)
                user.groups.add(role_data)
                if department_estimation == 'on':
                    user.estimators = True
                if department_project == 'on':
                    user.project_eng = True
                if department_production == 'on':
                    user.production = True
                if department_fabrication == 'on':
                    user.fabrication = True
                if department_qaqc == 'on':
                    user.qaqc = True
                if department_procurement == 'on':
                    user.procurement = True
                if department_delivery == 'on':
                    user.delivery = True
                if department_inspection == 'on':
                    user.inspection = True
                else:
                    print("No Department.")
                user.save()
            else:
                messages.error(request, form.errors)
        else:
            form = CreateUser(request.POST, request.FILES)
            if form.is_valid():
                form.save()
            else:
                messages.error(request, form.errors)
        return redirect('list_users')
    context = {
        "title": f"{PROJECT_NAME} | Create Users",
        "form": form,
        "group_obj": group_obj,
    }
    return render(request, "Settings/User/add_user.html", context)


@login_required(login_url='signin')
@permission_required('user.view_user', login_url='permission_not_allowed')
def view_user_profile(request, pk):
    """
    This function retrieves a user object based on the primary key and renders a user profile page with
    the user's information.
    
    """
    user = User.objects.get(pk=pk)
    context = {"title": f"{PROJECT_NAME} | User Profile", "user": user}
    return render(request, "Settings/User/view_user.html", context)


@login_required(login_url='signin')
@permission_required('user.change_user', login_url='permission_not_allowed')
def update_user_details(request, pk):
    """
    This function updates user details and assigns a role to the user.
    
    """
    user_obj = User.objects.get(pk=pk)
    group_obj = Group.objects.all().order_by('id')
    form = CreateUser(instance=user_obj)
    if request.method == 'POST':
        role = request.POST.get('user_role')
        # department = request.POST.get('department')
        department_estimation = request.POST.get('department_estimation')
        department_project = request.POST.get('department_project')
        department_production = request.POST.get('department_production')
        department_fabrication = request.POST.get('department_fabrication')
        department_qaqc = request.POST.get('department_qaqc')
        
        department_procurement = request.POST.get('department_procurement')
        department_delivery = request.POST.get('department_delivery')
        department_inspection = request.POST.get('department_inspection')
        
        
        form = CreateUser(request.POST, request.FILES, instance=user_obj)
        user_obj.groups.clear()
        if form.is_valid():
            form_obj = form.save()
            if not user_obj.is_superuser:
                role_data = group_obj.get(pk=role)
                form_obj.groups.add(role_data)
                
            user_obj.estimators = False
            user_obj.project_eng = False
            user_obj.production = False
            user_obj.fabrication = False
            user_obj.qaqc = False
            user_obj.procurement = False
            user_obj.delivery = False
            user_obj.inspection = False
            
            if department_estimation == 'on':
                user_obj.estimators = True
            if department_project == 'on':
                user_obj.project_eng = True
            if department_production == 'on':
                user_obj.production = True
            if department_fabrication == 'on':
                user_obj.fabrication = True
            if department_qaqc == 'on':
                user_obj.qaqc = True
            if department_procurement == 'on':
                user_obj.procurement = True
            if department_delivery == 'on':
                user_obj.delivery = True
            if department_inspection == 'on':
                user_obj.inspection = True
            else:
                print("No Department.")
            user_obj.save()
            form_obj.save()
        else:
            messages.error(request, form.errors)
            print("errors==>", form.errors)
        return redirect('view_user_profile', pk=user_obj.id)
    context = {
        'title': f'{PROJECT_NAME} | Update User Details',
        'form': form,
        'user': user_obj,
        "group_obj": group_obj,
    }
    return render(request, "Settings/User/update_user_modal.html", context)


@login_required(login_url='signin')
@permission_required('user.change_user', login_url='permission_not_allowed')
def user_inactive(request, pk):
    """
    This function deactivates a user account by setting the "is_active" attribute to False.
    
    """
    user_obj = User.objects.get(pk=pk)
    user_obj.is_active = False
    user_obj.save()
    return JsonResponse({"success": True}, status=200)


@login_required(login_url='signin')
@permission_required('user.change_user', login_url='permission_not_allowed')
def user_active(request, pk):
    """
    This function activates a user account by setting the is_active attribute to True and returning a
    JSON response indicating success.
    
    """
    user_obj = User.objects.get(pk=pk)
    user_obj.is_active = True
    user_obj.save()
    return JsonResponse({"success": True}, status=200)


@login_required(login_url='signin')
@permission_required(['user.change_user'], login_url='permission_not_allowed')
def password_set(request, pk):
    """
    This function sets a new password for a user and displays a form to change the password.
    
    """
    user_obj = User.objects.get(pk=pk)
    form = ChangePasswordFrom(user=user_obj)
    
    if request.method == 'POST':
        form = ChangePasswordFrom(user=user_obj, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password Updated.")
        else:
            messages.error(request, form.errors)
        return redirect('view_user_profile', pk=user_obj.id)
    context = {
        'form': form,
        'user': user_obj,
    }
    return render(request, "Settings/User/user_password_set_modal.html", context)


# This function only for Testing anf Debugging purpose
def reset_data(request, str):
    reset_users(password=str)
    return redirect('signin')


def backup_database(request):
    dbname = DATABASES['default']['NAME']
    username = DATABASES['default']['USER']
    password = DATABASES['default']['PASSWORD']
    host = DATABASES['default']['HOST']
    port = DATABASES['default']['PORT']
    path = './database_backup.sql'
    #Production C:/Program Files/PostgreSQL/14/bin/pg_dump.exe
    #Local C:/Program Files/PostgreSQL/11/bin/pg_dump.exe
    command = [
        'C:/Program Files/PostgreSQL/14/bin/pg_dump.exe',
        '--dbname=postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
            user=username,
            password=password,
            host=host,
            port=port,
            dbname=dbname,
        ),
        '--file', path,
    ]
    
    try:
        # Execute the command and capture the output
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        
        # Create an HTTP response with the backup file as the content
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="database_backup.sql"'
        response.write(output)
        return response
    except subprocess.CalledProcessError as e:
        # Print the error output
        print(e.output)
        # Handle the error appropriately
        
    return HttpResponse('Backup failed')  # Handle backup failure case