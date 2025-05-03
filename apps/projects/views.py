import ast
from decimal import Decimal
import math
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import modelformset_factory
from django.http import JsonResponse, FileResponse
from django.db.models import Sum, Q, Count


from apps.associated_product.models import AssociatedProducts
from apps.enquiries.models import Enquiries, EnquirySpecifications, Estimations, Pricing_Summary
from apps.estimations.models import (
    EstimationBuildings, 
    EstimationMainProduct,
    EstimationVersions,
    MainProductAccessories,
    MainProductAddonCost, 
    MainProductAluminium, 
    MainProductGlass, 
    Quotations
)
from apps.functions import workstation_data
from apps.helper import sum_times
from apps.panels_and_others.models import PanelMasterSpecifications
from apps.pricing_master.models import Surface_finish_kit
from apps.product_master.models import Product_WorkStations

from apps.projects.forms import (
    AddSecondaryProductsForm,
    ApprovalNotesForm,
    Create_Project_WCR, 
    CreateDeductionPercentage, 
    CreateInvoicePercentage,
    CreateProject, 
    CreateProjectInvoice,
    CreateSalesItem, 
    DeliveryNoteForm, 
    DeliveryQuantityForm, 
    EPSProductDetails, 
    EPSProductForm, 
    EPSSubmitForm, 
    Fabrication_AttachmentsForms, 
    InstalledQuantityForm, 
    OutSourceSubmitForm,
    ProjectApprovalStatusForm,
    ProjectApprovalTypesForm,
    QAQCParametersFrom, 
    ReceiveOutsourceProduct, 
    ScheduleProductForm,
    SecOpenablePanelsForm,
    SecSpecSpandrelPanelsForm,
    SecSpecVisionPanelsForm,
    UpdatsalesSpecificationForm,
    WCR_Products,
    create_cumulative_invoice_form, 
    create_invoice_form, 
    eps_infill_details,
    eps_infill_temp,
    eps_openable_details,
    eps_openable_details_temp,
    eps_spandrel_details,
    eps_spandrel_details_temp,
    infillEPSform,
    # sec_infill_form
)
# from apps.projects.functions import chain_update_products

from apps.projects.models import (
    ApprovalNotes,
    CumulativeInvoiceProduct,
    Delivery_Note, 
    Delivery_Product_Cart_Associated, 
    Delivery_Product_Cart_Main, 
    Delivery_Product_Cart_infill,
    EPSBuildingsModel,
    ElevationModel, 
    Eps_Associated_Products, 
    Eps_Associated_sub_Products, 
    Eps_Outsource_items,
    Eps_Outsourced_Data, 
    Eps_Product_Details, 
    Eps_Products, 
    Eps_Products_For_Delivery, 
    Eps_QAQC, 
    Eps_ShopFloor_main_products, 
    Eps_ShopFloors, 
    Eps_infill_Details,
    Eps_infill_Temp, 
    Eps_main, 
    Fabrication_Attachments,
    FloorModel,
    InfillSchedule,
    Outsource_receive_items,
    # InfillSchedule, 
    Outsource_receive_recode,
    ProjectApprovalStatus,
    ProjectApprovalTypes, 
    ProjectContractItems, 
    ProjectDeductionPercentage, 
    ProjectDeliveryQuantity,
    ProjectEstimations, 
    ProjectInstalledQuantity,
    ProjectInvoices, 
    ProjectInvoicingPercentage, 
    ProjectInvoicingProducts,
    ProjectSepcificationsApproval,
    ProjectWCR, ProjectsModel, 
    QAQC_Associated_Product_History,
    QAQC_Infill_History, 
    QAQC_Main_Product_History,
    # QAQC_ProcessedHistory,
    QAQC_RatingHistory, 
    QAQC_infill_Products,
    QAQC_parameters,
    SalesOrderAccessories,
    SalesOrderAddons,
    SalesOrderGroups,
    SalesOrderInfill,
    SalesOrderItems,
    SalesOrderSpecification,
    SalesSecondarySepcPanels, 
    Schedule_Product, 
    ShopFloor_Doc,
    Temp_EPS_Products, 
    WCRProducts, 
    Workstation_Associated_Product_History, 
    Workstation_Associated_Products_Data, 
    Workstation_Data, 
    Workstation_History
)

from amoeba.settings import DN_ID, EPS_ID, MEDIA_URL, PROJECT_NAME
from apps.projects.templatetags.outsource_products import outsource_item_details, outsource_item_remaning
from apps.shopfloors.models import Shopfloors
from apps.surface_finish.models import SurfaceFinishColors


@login_required(login_url='signin')
@permission_required(['projects.view_projectsmodel'], login_url='permission_not_allowed')
def list_projects(request):
    """
    This function retrieves a list of projects from the ProjectsModel and renders them in a template
    along with a form to create new projects.
    
    """
    projects = ProjectsModel.objects.all().exclude(status=0).order_by('id')
    projects_enquiry = [enquiry.enquiry.id for enquiry in ProjectEstimations.objects.all()]
    enquiries = Enquiries.objects.filter(status=8).exclude(pk__in=projects_enquiry)
    form = CreateProject()
    
    context = {
        'title': f'{PROJECT_NAME} | List Projects',
        'projects': projects,
        'form': form,
        'enquiries': enquiries,
        
    }
    return render(request, 'Projects/list_projects.html', context)


@login_required(login_url='signin')
def get_enquiry_revisions(request, pk):
    """
    This function retrieves the latest estimation revisions for a given enquiry and returns the
    estimation ID and label.
    
    """
    estimations = Estimations.objects.filter(enquiry=pk, version__status=13).last()
    if estimations.version.version == '0':
        version_label = 'Original'
    else:
        version_label = f'Revision {estimations.version.version}'
    return JsonResponse({'estimation_id': estimations.id, 'estimation_label': version_label,})
    

@login_required(login_url='signin')
def enquiry_details(request, pk):
    try:
        enquiry_obj = Enquiries.objects.get(pk=pk)
        estimation_obj = Estimations.objects.filter(enquiry=pk, version__status=13).last()
        revision = 'Original' if estimation_obj.version.version == '0' else f"Revision {estimation_obj.version.version}"
        quotation_value = Pricing_Summary.objects.get(estimation=estimation_obj.id)
        return JsonResponse({'flag': True, 'enquiry_title': enquiry_obj.title, 'customer_name': enquiry_obj.main_customer.name, 'revision': revision, 'quotation_value': quotation_value.quotation})
    except Exception:
        return JsonResponse({'flag': False, 'enquiry_title': None, 'customer_name': None, 'revision': None, 'quotation_value': None})
        
    
@login_required(login_url='signin')
@permission_required(['projects.add_projectsmodel'], login_url='permission_not_allowed')
def create_project(request):
    """
    This function creates a project and saves it to the database, with the user who created it and
    displays a success message.
    
    """
    form = CreateProject()
    projects_enquiry = [enquiry.enquiry.id for enquiry in ProjectEstimations.objects.all()]
    enquiries = Enquiries.objects.filter(status=8).exclude(pk__in=projects_enquiry)
    
    if request.method == 'POST':
        enquiries = request.POST.getlist('enquiry_select')
        form = CreateProject(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.created_by = request.user
            # project_customer=
            form_obj.save()
            
            for enquiry in enquiries:
                enquiry_obj = Enquiries.objects.get(pk=enquiry)
                # if enquiry == enquiries.first():
                form_obj.project_title = enquiry_obj.title
                form_obj.save()
                    
                try:
                    estimations = Estimations.objects.get(enquiry=enquiry_obj.id, version__status=13)
                    quotation = Quotations.objects.get(estimations=estimations)
                except Exception as e:
                    print("EXCE==>", e)
                    estimations = None
                    quotation = None
                    
                if estimations:
                    project_estimation = ProjectEstimations(
                        project=form_obj,
                        enquiry=estimations.enquiry,
                        estimations_version=estimations,
                        quotation=quotation,
                    )
                    project_estimation.save()
                    
                    # quotation = estimations.estimation_quotations.first()
                    # form_obj.estimations_version = estimations
                    form_obj.project_customer = enquiry_obj.main_customer
                    print('enquiry_obj.main_customer==>', enquiry_obj.main_customer)
                    form_obj.save()
                # if quotation:
                #     form_obj.quotation.add(quotation)
            messages.success(request, "Successfully Created Project")
                # else:
                #     messages.error(request, "Error in creating the project. Please select a revision.")
            
            return redirect('list_projects')
        else:
            messages.error(request, form.errors)
            print('PROJECT ERROR==>', form.errors)
    context = {
        'form': form,
        "enquiries": enquiries,
    }
    return render(request, 'Projects/update_project.html', context)


@login_required(login_url='signin')
@permission_required(['projects.change_projectsmodel'], login_url='permission_not_allowed')
def update_project(request, pk):
    """
    This function updates a project instance with the data submitted through a form and saves the last
    modified date and user information.
    
    """
    project = ProjectsModel.objects.get(pk=pk)
    project_datas_obj = ProjectEstimations.objects.get(project=project)
    projects_enquiry = [enquiry.enquiry.id for enquiry in ProjectEstimations.objects.all().exclude(enquiry=project_datas_obj.enquiry)]
    enquiries = Enquiries.objects.filter(status=8).exclude(pk__in=projects_enquiry)
    
    form = CreateProject(instance=project)
    if request.method == 'POST':
        form = CreateProject(request.POST, instance=project)
        if form.is_valid():
            form_obj = form.save()
            form_obj.last_modified_date = time()
            form_obj.last_modified_by = request.user
            form_obj.save()
            messages.success(request, "Successfully Updated Project")
            return redirect('list_projects')
        else:
            messages.error(request, form.errors)
            print('PROJECT ERROR==>', form.errors)
    context = {
        'form': form,
        'project': project,
        'enquiries': enquiries,
        
        "project_datas_obj": project_datas_obj,
    }
    return render(request, 'Projects/update_project.html', context)


@login_required(login_url='signin')
@permission_required(['projects.view_projectsmodel'], login_url='permission_not_allowed')
def get_project_details(request, pk):
    """
    This function retrieves project details from the ProjectsModel and returns them as a JSON response.
    
    """
    projects = ProjectsModel.objects.get(pk=pk)
    data = {
        'created_date': projects.created_date,
        'due_date': projects.due_date,
        'project_id': projects.project_id
    }
    return JsonResponse(data, status=200)


@login_required(login_url='signin')
@permission_required(['projects.view_projectsmodel'], login_url='permission_not_allowed')
def assign_quotation_to_project(request, pk):
    """
    Quotation Assigning to a Project.
    
    """
    quotation = Quotations.objects.get(pk=pk)
    if request.method == 'POST':
        project = request.POST.get('selecte_project')
        projec_obj = ProjectsModel.objects.get(pk=project)
        projec_obj.project_customer = quotation.estimations.enquiry.main_customer
        projec_obj.estimations_version = quotation.estimations
        projec_obj.quotation.add(quotation)
        projec_obj.save()
        version = EstimationVersions.objects.get(pk=quotation.estimations.version.id)
        version.status = 13
        version.save()
        enquiry = Enquiries.objects.get(pk=quotation.estimations.enquiry.id)
        enquiry.status = 8
        enquiry.save()
        return redirect('list_projects')
    return redirect('list_projects')


@login_required(login_url='signin')
@permission_required(['projects.view_projectsmodel'], login_url='permission_not_allowed')
def project_profile(request, pk):
    """
    It gets the project object from the database and passes it to the template
    
    """
    projec_obj = ProjectsModel.objects.get(pk=pk)
    context = {
        "title": f'{PROJECT_NAME} | Project Profile',
        "project": projec_obj
    }
    return render(request, 'Projects/project_profile.html', context)


@login_required(login_url='signin')
@permission_required(['projects.view_projectsmodel'], login_url='permission_not_allowed')
def project_scop(request, pk):
    """
    get all the estimations from the quotations that are related to the project
    
    """
    projec_obj = ProjectsModel.objects.get(pk=pk)
    project_estimations = ProjectEstimations.objects.filter(project=projec_obj)
    sales_groups = SalesOrderGroups.objects.filter(enquiry_data__in=[data.enquiry for data in project_estimations])
    estimation_ids = []
    
    category_objs = SalesOrderSpecification.objects.filter(project=projec_obj).distinct('categories')
    
    elevation_objs = ElevationModel.objects.filter(building__project=projec_obj)
    building_objs = EPSBuildingsModel.objects.filter(project=projec_obj)
    floor_objs = FloorModel.objects.filter(elevation__building__project=projec_obj)
    
    uncategories_buildings = SalesOrderItems.objects.filter(
        specification_Identifier__project=projec_obj,
        building__isnull=True,
    )
    uncategories_elevations = SalesOrderItems.objects.filter(
        specification_Identifier__project=projec_obj,
        elevation__isnull=True,
    )
    uncategories_floors = SalesOrderItems.objects.filter(
        specification_Identifier__project=projec_obj,
        floor__isnull=True,
    )
    
    eps_products = Eps_Products.objects.filter(project=projec_obj, product_status=5, eps_data__isnull=True).order_by('id')
    
    # for estimation in project_estimations:
    #     estimation_id = EstimationBuildings.objects.filter(estimation=estimation.estimations_version.id).order_by('id')
    #     estimation_ids.append(estimation_id)
    
    context = {
        "title": f'{PROJECT_NAME} | Project Scope',
        "project": projec_obj,
        "estimation_ids": estimation_ids,
        "sales_groups": sales_groups,
        "category_objs": category_objs,
        "elevation_objs": elevation_objs,
        "building_objs": building_objs,
        "floor_objs": floor_objs,
        "uncategories_buildings": uncategories_buildings,
        "uncategories_elevations": uncategories_elevations,
        "uncategories_floors": uncategories_floors,
        "eps_products": eps_products,
    }
    return render(request, 'Projects/project_scope.html', context)


def all_zeros(lst):
    """
        The function checks if all elements in a list are equal to the string "0".
    """
    flag = True
    for item in lst:
        if item != str(0):
            flag = False
    return flag


@login_required(login_url='signin')
@permission_required(['projects.view_projectsmodel'], login_url='permission_not_allowed')
def proccess_quotation(request, pk):
    """
    This function processes a quotation request by retrieving project and product information,
    validating user input, and saving the data to the database.
    
    """
    project_obj = ProjectsModel.objects.get(pk=pk)
    associated_products = AssociatedProducts.objects.all().order_by("id")
    project_estimations = ProjectEstimations.objects.filter(project=project_obj)
    estimation_ids = []
    sales_groups = SalesOrderGroups.objects.filter(enquiry_data__in=[data.enquiry for data in project_estimations])
    # for estimation in project_estimations:
    #     estimation_id = EstimationBuildings.objects.filter(estimation=estimation.estimations_version.id).order_by('id')
    #     estimation_ids.append(estimation_id)
        
    if request.method == "POST":
        infill_qyt = request.POST.getlist('infill_qyt')
        product_item = request.POST.getlist('product')
        auth_qyt = request.POST.getlist('auth_qyt')
        processd_qty = request.POST.getlist('authorised_quantity')
        flag = all_zeros(auth_qyt)

        if not flag:
            project_contract_item_list = []
            for i, product_id in enumerate(product_item):
                infill = infill_qyt[i] or 0
                # auth = float(auth_qyt[i]) or 0
                auth = auth_qyt[i] if i < len(auth_qyt) else '0'
                process_qty = processd_qty[i] or 0
                try:
                    auth_decimal = Decimal(auth)
                except:
                    auth_decimal = Decimal('0')
                    
                try:
                    product_obj = SalesOrderItems.objects.get(pk=product_id)
                except:
                    product_obj = None
                 
                if auth != '0' and process_qty == '0.00':
                    if product_obj.product_type == 3:
                        auth_balance = float(product_obj.quantity) - float(auth)
                    else:
                        if product_obj.eps_uom == 1:
                            auth_balance = float(product_obj.quantity) - float(auth)
                        else:
                            auth_balance = float(product_obj.total_area) - float(auth)
                        
                    project_contract_item1 = ProjectContractItems(
                        product=product_obj, 
                        project=project_obj, 
                        infill_quantity=float(infill), 
                        authorised_quantity=float(auth),
                        auth_balance=float(auth_balance),
                        eps_balance=auth_decimal,
                        
                        )
                    project_contract_item1.save()
                    
                elif process_qty != '0.00' and auth != '0':
                    project_contract_item = ProjectContractItems.objects.get(product=product_obj, project=project_obj)
                    if product_obj.product_type == 3:
                        auth_balance = float(product_obj.quantity) - float(auth)
                    else:
                        if product_obj.eps_uom == 1:
                            auth_balance = float(product_obj.quantity) - float(project_contract_item.authorised_quantity)
                        else:
                            auth_balance = float(product_obj.total_area) - float(project_contract_item.authorised_quantity)
                    try:
                        project_contract_item.infill_quantity = float(infill)
                        project_contract_item.authorised_quantity = float(project_contract_item.authorised_quantity) + float(auth)
                        project_contract_item.auth_balance = float(auth_balance) - float(auth)
                        project_contract_item.eps_balance = float(project_contract_item.eps_balance) + float(auth)
                        project_contract_item.save()
                    except Exception as e:
                        print("EXCE===>", e)
                else:
                    pass
            messages.success(request, 'Successfully Added.')
        else:
            messages.error(request, 'Please ensure at least one product is selected before submitting.')
            
        return redirect('project_scop', pk=project_obj.id)
    context = {
        "title": f'{PROJECT_NAME} | Project Scope',
        "project": project_obj,
        "estimation_ids": estimation_ids,
        "associated_products": associated_products,
        "sales_groups": sales_groups,
    }
    return render(request, 'Projects/quotation_process/quotation_process.html', context)



@login_required(login_url='signin')
def delete_sales_item(request, pk):
    
    if request.method == "POST":
        
        try:
            sales_item = SalesOrderItems.objects.get(pk=pk)
            project_contract = ProjectContractItems.objects.filter(product=sales_item)

            if not project_contract:
                try:
                    SalesOrderInfill.objects.filter(product=sales_item).delete()
                except Exception as e:
                    print("EEE+===>", e)
                    
                try:
                    SalesOrderAccessories.objects.filter(product=sales_item).delete()
                except Exception as ee:
                    print("EIIEO==>", ee)
                    
                if sales_item.ref_product:
                    ref_product = EstimationMainProduct.objects.get(pk=sales_item.ref_product)
                    ref_product.convert_to_sales = False
                    ref_product.save()
                    
                sales_item.delete()
            messages.success(request, "Sales Item Deleted Successfully")
        except Exception as e:
            print("EEE==>", e)
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('project_scop', pk=sales_item.sales_group.project.id)

    context = {"url": f"/Project/delete_sales_item/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
def convert_to_contract_item(request, project, building, product_data):
    """
    This function converts product data into contract items and saves them to the database.
    
    """
    projec_obj = ProjectsModel.objects.get(pk=project)
    data_list = []
    for item in product_data.split(','):
        datas = list(item.split('-'))
        data_list.append(datas)
    for pro_data in data_list:
        associated_product_quantity = pro_data[0]
        infill_quantity = pro_data[1]
        auth_quantity = pro_data[2]
        
        product = EstimationMainProduct.objects.get(pk=int(pro_data[3]))


    item_obj = ProjectContractItems(product=product, project=projec_obj, associated_product_quantity=associated_product_quantity, 
                                    infill_quantity=infill_quantity, authorised_quantity=auth_quantity)
    item_obj.save()
    messages.success(request, "Successfully Added To Contract Items")

    return redirect("project_scop", pk=projec_obj.id)
    

@login_required(login_url='signin')
@permission_required(['projects.view_projectsmodel'], login_url='permission_not_allowed')
def project_budgeting(request, pk):
    """
    This function retrieves estimation IDs for a project's quotations and renders a project budgeting
    template with the project and estimation IDs as context.
    
    """
    projec_obj = ProjectsModel.objects.get(pk=pk)
    project_estimations = ProjectEstimations.objects.filter(project=projec_obj)
    sales_groups = SalesOrderGroups.objects.filter(enquiry_data__in=[data.enquiry for data in project_estimations])
    group_ids = [group.id for group in sales_groups]
    eps_products = Eps_Products.objects.filter(project=projec_obj, product_status=5, eps_data__isnull=True).order_by('id')
    # for quotations in projec_obj.quotation.all():
    #     estimation_id = EstimationBuildings.objects.filter(estimation=Quotations.objects.get(pk=quotations.id).estimations).order_by('id')
    #     estimation_ids.append(estimation_id)
    context = {
        "title": f'{PROJECT_NAME} | Project Budgeting',
        "project": projec_obj,
        "group_ids": group_ids,
        "sales_groups": sales_groups,
        "eps_products": eps_products,
    }
    return render(request, 'Projects/project_budgeting.html', context)


@login_required(login_url='signin')
@permission_required(['projects.view_projectsmodel'], login_url='permission_not_allowed')
def project_settings(request, pk, building_id=None, elevation=None):
    """
    This function retrieves project settings data and renders it in a template.
    
    """
    projec_obj = ProjectsModel.objects.get(pk=pk)
    invoice_percentages = ProjectInvoicingPercentage.objects.filter(project_id=projec_obj).order_by('id')
    deduction_percentage = ProjectDeductionPercentage.objects.filter(project_id=projec_obj).order_by('id')
    project_buildings = EPSBuildingsModel.objects.filter(project=projec_obj)
    
    eps_products = Eps_Products.objects.filter(project=projec_obj, product_status=5, eps_data__isnull=True).order_by('id')
    
    if building_id:
        elevations = ElevationModel.objects.filter(building=building_id)
        building_obj = EPSBuildingsModel.objects.get(pk=building_id)
    else:
        elevations = None
        building_obj = None
        
    if elevation:
        elevations_obj = ElevationModel.objects.get(pk=elevation)
        project_floors = FloorModel.objects.filter(elevation=elevation)
    else:
        project_floors = None
        elevations_obj = None
    
    context = {
        "title": f'{PROJECT_NAME} | Project Settings',
        "project": projec_obj,
        "invoice_percentages": invoice_percentages,
        "deduction_percentage": deduction_percentage,
        "elevations": elevations,
        "project_buildings": project_buildings,
        "project_floors": project_floors,
        "building_id": building_id,
        "elevation": elevation,
        "building_obj": building_obj,
        "elevations_obj": elevations_obj,
        "eps_products": eps_products,
    }
    return render(request, 'Projects/project_settings.html', context)


@login_required(login_url='signin')
def project_approval_settings(request):
    
    # ProjectApprovalTypesForm
    approval_objs = ProjectApprovalTypes.objects.all()
    approval_status_objs = ProjectApprovalStatus.objects.all()
    
    context = {
        "title": f"{PROJECT_NAME} | Project Approvals",
        "approval_objs": approval_objs,
        "approval_status_objs": approval_status_objs,
    }
    return render(request, "Master_settings/Projects/project_appproval_settings.html", context)


@login_required(login_url='signin')
def add_project_approvaltype(request):
    form = ProjectApprovalTypesForm()
    
    if request.method == 'POST':
        form = ProjectApprovalTypesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Added.')
        else:
            form_error = form.errors
            messages.error(request, f'{form_error}')
            
        return redirect('project_approval_settings')

    context = {
        "form": form,
        
    }
    return render(request, "Master_settings/Projects/approval_types_addmodel.html", context)


@login_required(login_url='signin')
def update_project_approvaltype(request, pk):
    approval_obj = ProjectApprovalTypes.objects.get(pk=pk)
    form = ProjectApprovalTypesForm(instance=approval_obj)
    
    if request.method == 'POST':
        form = ProjectApprovalTypesForm(request.POST, instance=approval_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Updated.')
        else:
            form_error = form.errors
            messages.error(request, f'{form_error}')
            
        return redirect('project_approval_settings')

    context = {
        "form": form,
        "approval_obj": approval_obj,
    }
    return render(request, "Master_settings/Projects/approval_types_addmodel.html", context)
        

@login_required(login_url='signin')
def delete_project_approvaltype(request, pk):
    approval_obj = ProjectApprovalTypes.objects.get(pk=pk)
    
    if request.method == "POST":
        try:
            approval_obj.delete()
            messages.success(request, "Deleted Successfully")
        except Exception as e:
            print("EEE==>", e)
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('project_approval_settings')

    context = {"url": f"/Project/delete_project_approvaltype/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)
    

@login_required(login_url='signin')
def project_approval_statusadd(request):
    form = ProjectApprovalStatusForm()
    if request.method == 'POST':
        form = ProjectApprovalStatusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Added.')
        else:
            form_error = form.errors
            messages.error(request, f'{form_error}')
            
        return redirect('project_approval_settings')

    context = {
        "form": form,
    }
    return render(request, "Master_settings/Projects/approval_status.html", context)


@login_required(login_url='signin')
def project_approval_statusupdate(request, pk):
    approve_status_obj = ProjectApprovalStatus.objects.get(pk=pk)
    form = ProjectApprovalStatusForm(instance=approve_status_obj)
    if request.method == 'POST':
        form = ProjectApprovalStatusForm(request.POST, instance=approve_status_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Updated.')
        else:
            form_error = form.errors
            messages.error(request, f'{form_error}')
            
        return redirect('project_approval_settings')

    context = {
        "form": form,
        "approve_status_obj": approve_status_obj,
    }
    return render(request, "Master_settings/Projects/approval_status.html", context)


@login_required(login_url='signin')
def delete_project_approvalstatus(request, pk):
    approve_status_obj = ProjectApprovalStatus.objects.get(pk=pk)
    
    if request.method == "POST":
        try:
            approve_status_obj.delete()
            messages.success(request, "Deleted Successfully")
        except Exception as e:
            print("EEE==>", e)
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('project_approval_settings')

    context = {"url": f"/Project/delete_project_approvalstatus/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)
   

@login_required(login_url='signin')
@permission_required(['projects.add_projectinvoicingpercentage'], login_url='permission_not_allowed')
def add_project_settings_invoice_percentage(request, pk):
    """
    This function adds an invoice percentage to a project and renders a form to input the percentage.
    
    """
    projec_obj = ProjectsModel.objects.get(pk=pk)
    form = CreateInvoicePercentage()
    if request.method == 'POST':
        form = CreateInvoicePercentage(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.project = projec_obj
            form_obj.save()
        else:
            messages.error(request, 'Error in save')
        return redirect('project_settings', pk=projec_obj.id)
    context = {
        "project": projec_obj,
        "form": form
    }
    return render(request, 'Projects/invoice/add_invoicing_modal.html', context)


@login_required(login_url='signin')
@permission_required(['projects.change_projectinvoicingpercentage'], login_url='permission_not_allowed')
def update_project_settings_invoice_percentage(request, pk):
    """
    This function adds an invoice percentage to a project and renders a form to input the percentage.
    
    """
    obj = ProjectInvoicingPercentage.objects.get(pk=pk)
    projec_obj = ProjectsModel.objects.get(pk=obj.project.id)
    form = CreateInvoicePercentage(instance=obj)
    if request.method == 'POST':
        form = CreateInvoicePercentage(request.POST, instance=obj)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.save()
            messages.success(request, 'Successfully Updated.')
        else:
            messages.error(request, 'Error in save')
        return redirect('project_settings', pk=projec_obj.id)
    context = {
        "project": projec_obj,
        "form": form
    }
    return render(request, 'Projects/invoice/add_invoicing_modal.html', context)


@login_required(login_url='signin')
@permission_required(['projects.add_projectdeductionpercentage'], login_url='permission_not_allowed')
def add_project_settings_deduction_percentage(request, pk):
    """
    This function adds a deduction percentage to a project and renders a form to input the percentage.
    
    """
    projec_obj = ProjectsModel.objects.get(pk=pk)
    form = CreateDeductionPercentage()
    if request.method == 'POST':
        form = CreateDeductionPercentage(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.project = projec_obj
            form_obj.save()
        else:
            messages.error(request, 'Error in save')
        return redirect('project_settings', pk=projec_obj.id)
    context = {
        "project": projec_obj,
        "form": form
    }
    return render(request, 'Projects/add_deduction_percentage_modal.html', context)


@login_required(login_url='signin')
@permission_required(['projects.add_projectdeductionpercentage'], login_url='permission_not_allowed')
def update_project_settings_deduction_percentage(request, pk):
    """
    This function adds a deduction percentage to a project and renders a form to input the percentage.
    
    """
    obj = ProjectDeductionPercentage.objects.get(pk=pk)
    projec_obj = ProjectsModel.objects.get(pk=obj.project.id)
    form = CreateDeductionPercentage(instance=obj)
    if request.method == 'POST':
        form = CreateDeductionPercentage(request.POST, instance=obj)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.project = projec_obj
            form_obj.save()
        else:
            messages.error(request, 'Error in save')
        return redirect('project_settings', pk=projec_obj.id)
    context = {
        "project": projec_obj,
        "form": form
    }
    return render(request, 'Projects/add_deduction_percentage_modal.html', context)


@login_required(login_url='signin')
@permission_required(['projects.view_projectsmodel'], login_url='permission_not_allowed')
def project_accounts(request, pk):
    """
    This function retrieves project accounts data and renders it to a template.
    """
    project_obj = ProjectsModel.objects.get(pk=pk)
    percentages = ProjectInvoicingPercentage.objects.filter(project_id=project_obj).order_by('id')
    project_estimations = ProjectEstimations.objects.filter(project=project_obj)
    sales_groups = SalesOrderGroups.objects.filter(enquiry_data__in=[data.enquiry for data in project_estimations])
    eps_products = Eps_Products.objects.filter(project=project_obj, product_status=5, eps_data__isnull=True).order_by('id')
    # estimation_ids = []
    # for quotations in project_obj.quotation.all():
    #     estimation_id = EstimationBuildings.objects.filter(
    #                                         estimation=Quotations.objects.get(pk=quotations.id).estimations).order_by('id')
    #     estimation_ids.append(estimation_id)
    
    context = {
        "title": f'{PROJECT_NAME} | Project Accounts',
        "project": project_obj,
        "sales_groups": sales_groups,
        "percentages": percentages,
        "eps_products": eps_products,
    }
    return render(request, 'Projects/project_accounts.html', context)


@login_required(login_url='signin')
def new_sales_item(request, pk):
    sales_group = SalesOrderGroups.objects.get(pk=pk)
    panel_data = SalesOrderSpecification.objects.filter(project=sales_group.project).distinct('panel_specification')
    product_form = CreateSalesItem(project_id=sales_group.project.id)
    
    # infill_form = sec_infill_form(sales_group.project.id)
    # infillForm = modelformset_factory(SalesOrderInfill, form=infill_form, extra=1, can_delete=True)
    # infill_formset = infillForm(queryset=SalesOrderInfill.objects.none(), prefix='sec_infill')
        
    if request.method == 'POST':
        product_form = CreateSalesItem(request.POST, project_id=sales_group.project.id)
        infill_product = request.POST.get('infill_product', None)
        # sec_infill_product = request.POST.getlist('sec_infill_product')
        # infill_formset = infillForm(request.POST, prefix='sec_infill')
        
        if product_form.is_valid():
            product_form_obj = product_form.save(commit=False)
            product_form_obj.total_area = float(product_form.cleaned_data['area']) * float(product_form.cleaned_data['quantity'])
            product_form_obj.total_price = float(product_form.cleaned_data['unit_price']) * float(product_form.cleaned_data['quantity'])
            product_form_obj.sales_group = sales_group
            product_form_obj.save()
            
            if infill_product:
                new_sales_infill = SalesOrderInfill(
                                                    product=product_form_obj, 
                                                    infill_specification_id=int(infill_product),
                                                    infill_area=float(product_form.cleaned_data['area']),
                                                    infill_primary=True,
                                                    infill_width=float(product_form.cleaned_data['width']),
                                                    infill_height=float(product_form.cleaned_data['height']),
                                                    infill_quantity=float(product_form.cleaned_data['quantity']),
                                                    panel_type = product_form_obj.panel_type
                                                )
                new_sales_infill.save()
                
                
            # for item in infill_formset:
            #     if item.is_valid():
            #         item_obj = item.save(commit=False)
            #         if item_obj.infill_quantity and item_obj.infill_area:
            #             item_obj.product = product_form_obj
            #             item_obj.infill_primary = False
            #             item_obj.save()
            #             product_form_obj.is_secondary_panels = True
            #             product_form_obj.save()
            #         else:
            #             print("Please Enter Infill Quantity.")
            #     else:
            #         print("Error in sub formset infill ==>", item.errors)
            #         messages.error(request, item.errors)
                        
            messages.success(request, "Successfully Added New Item.")
        return redirect('project_scop', pk=sales_group.project.id)
        
    context = {
        "sales_group": sales_group,
        "product_form": product_form,
        "project_obj": sales_group.project,
        "panel_data": panel_data,
        # "infill_formset": infill_formset,
    }
    return render(request, "Projects/Eps/add_sales_item.html", context)


@login_required(login_url='signin')
@permission_required(['projects.view_projectsmodel'], login_url='permission_not_allowed')
def project_invoices(request, pk):
    """
    This function retrieves project invoices for a specific project and renders them in a template.
    """
    project_obj = ProjectsModel.objects.get(pk=pk)
    invoice_obj = ProjectInvoices.objects.filter(project=project_obj.id).order_by('id')
    try:
        # cumulative_obj = CumulativeInvoiceProduct.objects.get(project=project_obj.id)
        invoice_products_obj = ProjectInvoicingProducts.objects.get(project=project_obj.id)
    except Exception as e:
        invoice_products_obj = None
    
    eps_products = Eps_Products.objects.filter(project=project_obj, product_status=5, eps_data__isnull=True).order_by('id')
    
    context = {
        "title": f'{PROJECT_NAME} | Project Invoices',
        "project": project_obj,
        "invoice_obj": invoice_obj,
        "invoice_products_obj": invoice_products_obj,
        "eps_products": eps_products,
        
    }
    return render(request, 'Projects/invoice/project_invoices.html', context)


@login_required(login_url='signin')
@permission_required(['projects.view_projectdeliveryquantity'], login_url='permission_not_allowed')
def get_product_delivery_quantity(request, project, pk):
    """
    This function calculates the balance quantity of a product for different stages of invoicing and
    delivery in a project.
    
    """
    
    sales_obj = SalesOrderItems.objects.get(pk=pk)
    
    product_data = ProjectDeliveryQuantity.objects.filter(
                                        product=pk,
                                        project=project
                                    ).aggregate(quantity=Sum('delivered_qunatity'))
    
    product_invoiced_quantity = ProjectInvoicingProducts.objects.filter(
                                        project=project,
                                        product=pk,
                                        # invoicing_stage__stage=1
                                        ).aggregate(invoiced_quantity=Sum('quantity'))
    
    product_qty_details = ProjectContractItems.objects.get(
        product=sales_obj
    )
    
    if sales_obj.eps_uom == 1:
        quantity = sales_obj.quantity
    else:
        quantity = sales_obj.total_area
        
    return JsonResponse(
        {
            "product_quantity": float(quantity),
            "eps_qty": float(product_qty_details.eps_issued),
            "delivery_qty": product_data['quantity'] if product_data['quantity'] else 0,
            "installed_qty": 0,
            "invoiced_quantity": float(product_invoiced_quantity['invoiced_quantity'] if product_invoiced_quantity['invoiced_quantity'] else 0),
            "success": True, 
            
            # "delivery_balance_quantity": delivery_balance_quantity,
            # "stage_1_balance_quantity": stage_1_balance_quantity,
            # "stage_2_balance_quantity": stage_2_balance_quantity,
            # "stage_3_balance_quantity": stage_3_balance_quantity,
        }, status=200)


@login_required(login_url='signin')
@permission_required(['projects.change_projectdeliveryquantity'], login_url='permission_not_allowed')
def update_delivery_qunatity(request, project, product):
    """
    This function updates the delivery quantity of a product in a project and saves it to the database.
    
    """
    project_obj = ProjectsModel.objects.get(pk=project)
    product = EstimationMainProduct.objects.get(pk=product)
    delivery_form = DeliveryQuantityForm()
    if request.method == 'POST':
        delivery_form = DeliveryQuantityForm(request.POST)
        if delivery_form.is_valid():
            form_obj = delivery_form.save(commit=False)
            form_obj.project = project_obj
            form_obj.product = product
            form_obj.delivered_not_invoiced = form_obj.delivery_qunatity
            form_obj.save()
        else:
            messages.error(request, delivery_form.errors)
            print("ERROR: ", delivery_form.errors)
        return redirect('project_scop', pk=project_obj.id)
    context = {
        "project": project_obj,
        "product": product,
        "form": delivery_form
    }
    return render(request, 'Projects/project_quantity_update_modal.html', context)


@login_required(login_url='signin')
@permission_required(['projects.change_projectinstalledquantity'], login_url='permission_not_allowed')
def update_installed_qunatity(request, project, product):
    """
    This function updates the installed quantity of a product in a project and renders a form to do so.
    
    """
    project_obj = ProjectsModel.objects.get(pk=project)
    product = EstimationMainProduct.objects.get(pk=product)
    delivery_form = InstalledQuantityForm()
    if request.method == 'POST':
        delivery_form = InstalledQuantityForm(request.POST)
        if delivery_form.is_valid():
            form_obj = delivery_form.save(commit=False)
            form_obj.project = project_obj
            form_obj.product = product
            form_obj.save()
            messages.success(request, "Successfully Updated.")
        else:
            messages.error(request, delivery_form.errors)
            print("ERROR: ", delivery_form.errors)
        return redirect('project_scop', pk=project_obj.id)
        
    context = {
        "project": project_obj,
        "product": product,
        "form": delivery_form
    }
    return render(request, 'Projects/project_quantity_update_modal.html', context)


@login_required(login_url='signin')
@permission_required(['projects.view_projectinvoicingpercentage'], login_url='permission_not_allowed')
def get_stage_percentage(request, pk):
    """
    This function retrieves the invoice percentage of a project and returns it as a JSON response.
    
    """
    percentage = ProjectInvoicingPercentage.objects.get(pk=pk)
    data = {'percentage': percentage.invoice_percentage,}
    return JsonResponse(data, status=200)


@login_required(login_url='signin')
@permission_required(['projects.view_projectinvoices'], login_url='permission_not_allowed')
def view_invoice_normal(request, pk):
    """
    This function retrieves and displays information related to a project invoice.
    
    """
    invoice_obj = ProjectInvoices.objects.get(pk=pk)
    invoice_products = ProjectInvoicingProducts.objects.filter(project=invoice_obj.project, invoice=invoice_obj).order_by('id')
    deductions_obj = ProjectDeductionPercentage.objects.filter(project=invoice_obj.project).order_by('id')
    
    context = {
        'title': f'{PROJECT_NAME} | View Invoice ',
        "invoice_obj": invoice_obj,
        "invoice_products": invoice_products,
        "deductions_obj": deductions_obj,
        "cumulative_invoice": False,

    }
    return render(request, 'Projects/invoice/view_invoice.html', context)


@login_required(login_url='signin')
@permission_required(['projects.change_projectinvoices'], login_url='permission_not_allowed')
def edit_project_invoice(request, pk):
    invoice_obj = get_object_or_404(ProjectInvoices, pk=pk)
    project_obj = get_object_or_404(ProjectsModel, pk=invoice_obj.project.id)
    invoice_products = ProjectInvoicingProducts.objects.filter(project=project_obj, invoice=invoice_obj).order_by('id')
    form = CreateProjectInvoice(instance=invoice_obj)
    product_data = ProjectDeliveryQuantity.objects.filter(project=project_obj.id).distinct('product')
    deductions_obj = ProjectDeductionPercentage.objects.filter(project=project_obj)
    product_form = create_invoice_form(project_obj)
    product_formset = modelformset_factory(ProjectInvoicingProducts, form=product_form, extra=1, can_delete=True)
    product_formsets = product_formset(queryset=ProjectInvoicingProducts.objects.none(), prefix="invoiced_products")
    
    if request.method == 'POST':
        form, product_formsets = process_invoice_form(request, invoice_obj, form, product_formsets)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.last_modified_by = request.user
            form_obj.last_modified_date = time()
            form_obj.save()
            save_invoice_products(product_formsets, project_obj, form_obj)
            messages.success(request, "Invoice Updated Successfully.")
            return redirect('project_invoices', pk=project_obj.id)
        else:
            messages.error(request, form.errors)
    
    context = {
        "title": f'{PROJECT_NAME} | Update Project Invoice',
        "project": project_obj,
        "form": form,
        'product_formset': product_formsets,
        "product_data": product_data,
        "deductions_obj": deductions_obj,
        "invoice_products": invoice_products,
        "invoice_obj": invoice_obj,
        "cumulative_invoice": False,
    }
    return render(request, 'Projects/invoice/edit_invoice.html', context)


def process_invoice_form(request, invoice_obj, form, product_formsets):
    """
    The function "process_invoice_form" takes in a request, an invoice object, a form, and product
    formsets, and returns the updated form and product formsets.
   
    """
    form = CreateProjectInvoice(request.POST, instance=invoice_obj)
    product_formsets = modelformset_factory(
        ProjectInvoicingProducts,
        form=create_invoice_form(invoice_obj.project),
        extra=1,
        can_delete=True,
    )(request.POST, prefix="invoiced_products")
    return form, product_formsets


def save_invoice_products(product_formsets, project_obj, form_obj):
    """
    The function saves invoice products if they have a quantity and invoicing stage, otherwise it prints
    an error message.
    
    """
    for item in product_formsets:
        if item.is_valid():
            item_obj = item.save(commit=False)
            if item_obj.quantity and item_obj.invoicing_stage:
                item_obj.project = project_obj
                item_obj.invoice = form_obj
                item_obj.save()
            else:
                print("No new product..")
        else:
            print("ERROR IN Item==>", item.errors)

@login_required(login_url='signin')
@permission_required(['projects.delete_projectinvoicingproducts'], login_url='permission_not_allowed')
def edit_product_delete(request, pk):
    """
    This function deletes a product from the database and returns a success message in JSON format.
    """
    product = ProjectInvoicingProducts.objects.get(pk=pk)
    product.delete()
    messages.success(request, "Successfully deleted")
    return JsonResponse({"success": True}, status=200)


@login_required(login_url='signin')
@permission_required(['projects.view_projectwcr'], login_url='permission_not_allowed')
def view_project_wcr(request, pk):
    """
    This function retrieves a project's work completion report (WCR) and renders it on a web page.
    
    """
    project_obj = ProjectsModel.objects.get(pk=pk)
    wcr_obj = ProjectWCR.objects.filter(project=project_obj).order_by('id')
    eps_products = Eps_Products.objects.filter(project=project_obj, product_status=5, eps_data__isnull=True).order_by('id')
    context = {
        'title': f'{PROJECT_NAME} | WCR ',
        "project": project_obj,
        'wcr_obj': wcr_obj,
        "eps_products": eps_products,
    }
    return render(request, 'Projects/wcr/project_wcr.html', context)


@login_required(login_url='signin')
@permission_required(['projects.add_projectwcr'], login_url='permission_not_allowed')
def create_project_wcr(request, pk):
    """
    The function `create_project_wcr` creates a new WCR (Work Completion Report) for a given project.
    """
    project_obj = get_object_or_404(ProjectsModel, pk=pk)
    data = retrieve_estimation_main_product_data(project_obj)
    form, product_formset = initialize_forms(project_obj)
    
    if request.method == 'POST':
        form, product_formset = process_wcr_form(request, form, product_formset)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.created_by = request.user
            form_obj.project = project_obj
            form_obj.save()
            save_wcr_products(product_formset, form_obj, project_obj)
            messages.success(request, "WCR Created Successfully.")
            return redirect('view_project_wcr', pk=project_obj.id)
        else:
            messages.error(request, form.errors)
    
    context = {
        'title': f'{PROJECT_NAME} | Create New WCR ',
        "project": project_obj,
        'form': form,
        'product_formset': product_formset,
        'product_data': data,
    }
    return render(request, 'Projects/wcr/new_wcr.html', context)


def retrieve_estimation_main_product_data(project_obj):
    """
    The function retrieves estimation main product data for a given project object.
    """
    # data = None
    # for quotations in project_obj.quotation.all():
    #     estimation_id = EstimationBuildings.objects.filter(estimation=Quotations.objects.get(pk=quotations.id).estimations).order_by('id')
    #     for estimation in estimation_id:
    #         data = EstimationMainProduct.objects.filter(building__estimation=estimation.estimation.id).order_by('id')
    data = SalesOrderItems.objects.filter(sales_group__project=project_obj.id)
    return data


def initialize_forms(project_obj):
    """
    The function initializes a form and a formset for a project object.
    """
    form = Create_Project_WCR()
    PRODUCTFORMSET = modelformset_factory(WCRProducts, form=WCR_Products, extra=1, can_delete=True)
    product_formset = PRODUCTFORMSET(queryset=WCRProducts.objects.none(), prefix="wcr_products")
    return form, product_formset


def process_wcr_form(request, form, product_formset):
    """
    The function "process_wcr_form" takes in a request, a form, and a product formset, and returns the
    processed form and product formset.
    
    """
    form = Create_Project_WCR(request.POST)
    product_formset = modelformset_factory(
        WCRProducts,
        form=WCR_Products,
        extra=1,
        can_delete=True,
    )(request.POST, prefix="wcr_products")
    return form, product_formset


def save_wcr_products(product_formset, form_obj, project_obj):
    """
    The function saves WCR products and their delivery and installation quantities to the database.
    
    """
    for item in product_formset:
        if item.is_valid():
            item_obj = item.save(commit=False)
            item_obj.wcr = form_obj
            if item_obj.delivery_qunatity != 0:
                item_obj.save()
                delivery_quantity = ProjectDeliveryQuantity(
                    project=project_obj,
                    wcr=form_obj,
                    product=item_obj.wcr_product,
                    delivered_qunatity=item_obj.delivery_qunatity,
                )
                delivery_quantity.save()
            
            if item_obj.installed_qunatity != 0:
                item_obj.save()
                installed_qunatity = ProjectInstalledQuantity(
                    project=project_obj,
                    wcr=form_obj,
                    product=item_obj.wcr_product,
                    installed_qunatity=item_obj.installed_qunatity,
                )
                installed_qunatity.save()
        else:
            print("ERROR IN Item==>", item.errors)


@login_required(login_url='signin')
@permission_required(['projects.view_projectwcr'], login_url='permission_not_allowed')
def view_wcr(request, pk):
    """
    This function retrieves a WCR object and its related project and products, and renders a view
    template with the retrieved data.
    
    """
    wcr_obj = ProjectWCR.objects.get(pk=pk)
    project_obj = ProjectsModel.objects.get(pk=wcr_obj.project.id)
    wcr_products = WCRProducts.objects.filter(wcr=wcr_obj).order_by('id')
    context = {
        'title': f'{PROJECT_NAME} | View WCR ',
        'wcr_obj': wcr_obj,
        "project": project_obj,
        'product_data': wcr_products,
    }
    return render(request, 'Projects/wcr/view_wcr.html', context)


@login_required(login_url='signin')
@permission_required(['projects.change_projectwcr'], login_url='permission_not_allowed')
def edit_project_wcr(request, pk):
    """
    This function edits a project's Work Completion Report (WCR) and saves the changes made to the WCR
    products.
    
    """
    wcr_obj = ProjectWCR.objects.get(pk=pk)
    wcr_products = WCRProducts.objects.filter(wcr=wcr_obj).order_by('id')
    
    project_obj = ProjectsModel.objects.get(pk=wcr_obj.project.id)
    projects_estimations = ProjectEstimations.objects.filter(project=project_obj)
    
    data = None
    for quotation in projects_estimations:
        estimation_id = EstimationBuildings.objects.filter(estimation=quotation.quotation.estimations).order_by('id')
        
        for estimation in estimation_id:
            data = EstimationMainProduct.objects.filter(building__estimation=estimation.estimation.id, disabled=False).order_by('id')
            
    form = Create_Project_WCR(instance=wcr_obj)
    PRODUCTFORMSET = modelformset_factory(WCRProducts, form=WCR_Products, extra=1, can_delete=True)
    product_formset = PRODUCTFORMSET(queryset=WCRProducts.objects.none(), prefix="wcr_products")
    
    if request.method == 'POST':
        form = Create_Project_WCR(request.POST, instance=wcr_obj)
        product_formset = PRODUCTFORMSET(request.POST, prefix="wcr_products")
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.last_modified_by = request.user
            form_obj.last_modified_date = time()
            form_obj.save()

            for item in product_formset:
                if item.is_valid():
                    item_obj = item.save(commit=False)
                    item_obj.wcr = wcr_obj
                    if item_obj.delivery_qunatity and item_obj.installed_qunatity:
                        item_obj.save()
                    
                        delivery_quantity = ProjectDeliveryQuantity(
                            project = project_obj,
                            wcr = wcr_obj,
                            product = item_obj.wcr_product,
                            delivered_qunatity = item_obj.delivery_qunatity,
                            delivered_not_invoiced = item_obj.delivery_qunatity
                        )
                        delivery_quantity.save()
                        installed_qunatity = ProjectInstalledQuantity(
                            project = project_obj,
                            wcr = wcr_obj,
                            product = item_obj.wcr_product,
                            installed_qunatity = item_obj.installed_qunatity,
                            installed_not_invoiced = item_obj.installed_qunatity,
                        )
                        installed_qunatity.save()
                    
                else:
                    print("ERROR IN Item==>", item.errors)
                    
            messages.success(request, "WCR Updated Successfully.")
        else:
            messages.error(request, form.errors)
        return redirect('view_project_wcr', pk=project_obj.id)
    context = {
        'title': f'{PROJECT_NAME} | Update WCR ',
        "project": project_obj,
        'form': form,
        'product_formset': product_formset,
        'product_data': data,
        'wcr_products': wcr_products,
        'wcr_obj': wcr_obj
    }
    return render(request, 'Projects/wcr/edit_wcr.html', context)


@login_required(login_url='signin')
@permission_required(['projects.delete_projectwcr'], login_url='permission_not_allowed')
def delete_wcr_product(request, pk):
    """
    This function deletes a WCR product and its associated delivery and installation quantities, and
    redirects to the edit page for the WCR.
    
    """
    product = WCRProducts.objects.get(pk=pk)
    ProjectDeliveryQuantity.objects.get(wcr=product.wcr).delete()
    ProjectInstalledQuantity.objects.get(wcr=product.wcr).delete()
    product.delete()
    return redirect('edit_project_wcr', pk=product.wcr.id)


@login_required(login_url='signin')
@permission_required(['projects.add_projectinvoices'], login_url='permission_not_allowed')
def create_project_invoice(request, pk):
    """
    This function creates a project invoice and saves it to the database along with the invoiced
    products.
    """
    project_obj = ProjectsModel.objects.get(pk=pk)
    project_data = ProjectEstimations.objects.filter(project=project_obj).first()
    
    form = CreateProjectInvoice()
    # product_data = ProjectDeliveryQuantity.objects.filter(project=project_obj.id)
    product_data = Eps_Products.objects.filter(eps_data__project=project_obj.id).distinct('eps_product')
   
    deductions_obj = ProjectDeductionPercentage.objects.filter(project=project_obj).order_by('id')
    PRODUCTFORM = create_invoice_form(project_obj)
    PRODUCTFORMSET = modelformset_factory(ProjectInvoicingProducts, form=PRODUCTFORM, extra=1, can_delete=True)
    product_formset = PRODUCTFORMSET(queryset=ProjectInvoicingProducts.objects.none(), prefix="invoiced_products")
    
    
    if request.method == 'POST':
        form = CreateProjectInvoice(request.POST)
        product_formset = PRODUCTFORMSET(request.POST, prefix="invoiced_products")
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.created_by = request.user
            form_obj.project = project_obj
            form_obj.invoice_type = 1
            form_obj.save()
            
            messages.success(request, "Invoice Created Successfully.")
            for item in product_formset:
                if item.is_valid():
                    item_obj = item.save(commit=False)
                    item_obj.project = project_obj
                    item_obj.invoice = form_obj
                    item_obj.save()
                    
                    # qunatity_update = ProjectDeliveryQuantity.objects.filter(project=project_obj.id).last()
                    # qunatity_update.delivered_not_invoiced = qunatity_update.delivered_qunatity - item_obj.quantity
                    # qunatity_update.save()
                    
                else:
                    print("ERROR IN Item==>", item.errors)
        else:
            messages.error(request, form.errors)
        return redirect('project_invoices', pk=project_obj.id)
        
    context = {
        "title": f'{PROJECT_NAME} | Create Project Invoice',
        "project": project_obj,
        "form": form,
        'product_formset': product_formset,
        "product_data": product_data,
        "deductions_obj": deductions_obj,
        "cumulative_invoice": False,
        "project_data": project_data,
    }
    return render(request, 'Projects/invoice/create_invoice.html', context)


@login_required(login_url="signin")
@permission_required(['projects.add_projectinvoices'], login_url='permission_not_allowed')
def cumulative_invoicing(request, pk):
    """
    This function creates a cumulative invoice for a project, allowing the user to select products and
    deductions to include in the invoice.
    
    """
    project_obj = ProjectsModel.objects.get(pk=pk)
    project_data = ProjectEstimations.objects.filter(project=project_obj).first()
    form = CreateProjectInvoice()
    # product_data = ProjectDeliveryQuantity.objects.filter(project=project_obj.id)
    product_data = Eps_Products.objects.filter(eps_data__project=project_obj.id).distinct('eps_product')
    
    invoiced_products = ProjectInvoicingProducts.objects.filter(project=project_obj.id).order_by('id')
    
    try:
        have_invoice_product = CumulativeInvoiceProduct.objects.filter(project=project_obj.id)
    except Exception as e:
        have_invoice_product = False
    
    old_invoice_obj = ProjectInvoices.objects.filter(project=project_obj)
    deductions_obj = ProjectDeductionPercentage.objects.filter(project=project_obj).order_by('id')
    PRODUCTFORM = create_cumulative_invoice_form(project_obj)
    PRODUCTFORMSET = modelformset_factory(CumulativeInvoiceProduct, form=PRODUCTFORM, extra=1, can_delete=True)
    product_formset = PRODUCTFORMSET(queryset=CumulativeInvoiceProduct.objects.none(), prefix="invoiced_products")
    
    if request.method == 'POST':
        form = CreateProjectInvoice(request.POST)
        product_formset = PRODUCTFORMSET(request.POST, prefix="invoiced_products")
        
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.created_by = request.user
            form_obj.project = project_obj
            form_obj.invoice_type = 2
            form_obj.save()
            
            # if item.is_valid():
            #     item_obj = item.save(commit=False)
                    
            #     item_obj.project = project_obj
            #     item_obj.invoice = form_obj
            #     item_obj.save()
            # else:
            #     print("ERROR IN Item==>", item.errors)
            
            messages.success(request, "Invoice Created Successfully.")
            print("have_invoice_product==>", have_invoice_product)
            
            # if not have_invoice_product:
            #     print("Q")
            #     # moving all products from invoice to cumulative
                 
            #     for invoiced_product in invoiced_products:
                    
            #         old_products = CumulativeInvoiceProduct(
            #             invoice=form_obj,
            #             product=invoiced_product.product,
            #             project=invoiced_product.project,
            #             invoice_percentage=invoiced_product.invoice_percentage,
            #             quantity=invoiced_product.quantity,
            #             total=invoiced_product.total,
            #         )
            #         old_products.save()
            
            #     for item in product_formset:
            #         if item.is_valid():
            #             item_obj = item.save(commit=False)
            #             try:
            #                 old_product = CumulativeInvoiceProduct.objects.get(project=project_obj.id, product=item_obj.product.id)
            #             except Exception as e:
            #                 old_product = None
                        
            #             if not old_product:
            #                 new_product_obj = CumulativeInvoiceProduct(
            #                     invoice=form_obj,
            #                     product=old_product.product,
            #                     project=old_product.project,
            #                     invoice_percentage=float(old_product.invoice_percentage)+float(item_obj.invoice_percentage),
            #                     quantity=float(old_product.quantity)+float(item_obj.quantity),
            #                     total=float(old_product.total)+float(item_obj.total),
            #                 )
                            
            #                 new_product_obj.save()
            #             else:
                            
            #                 item_obj.project = project_obj
            #                 item_obj.invoice = form_obj
            #                 item_obj.save()
            #         else:
            #             print("ERROR IN Item==>", item.errors)
            # else:
            #     # old_products = CumulativeInvoiceProduct.objects.filter(project=project_obj.id)
            #     for item in product_formset:
            #         if item.is_valid():
            #             item_obj = item.save(commit=False)
            #             try:
            #                 old_product = CumulativeInvoiceProduct.objects.get(project=project_obj.id, product=item_obj.product.id)
            #             except Exception as e:
            #                 old_product = None
                        
            #             if not old_product:
            #                 print("A")
            #                 new_product_obj = CumulativeInvoiceProduct(
            #                     invoice=form_obj,
            #                     product=old_product.product,
            #                     project=old_product.project,
            #                     invoice_percentage=float(old_product.invoice_percentage)+float(item_obj.invoice_percentage),
            #                     quantity=float(old_product.quantity)+float(item_obj.quantity),
            #                     total=float(old_product.total)+float(item_obj.total),
            #                 )
                            
            #                 new_product_obj.save()
                            
            #             else:
            #                 print("B")
            #                 item_obj.project = project_obj
            #                 item_obj.invoice = form_obj
            #                 item_obj.save()
            #         else:
            #             print("ERROR IN Item==>", item.errors)
                
            
        else:
            messages.error(request, form.errors)
        return redirect('project_invoices', pk=project_obj.id)
        
    context = {
        "title": f'{PROJECT_NAME} | Create Project Cumulative Invoice',
        "project": project_obj,
        "form": form,
        'product_formset': product_formset,
        "product_data": product_data,
        "deductions_obj": deductions_obj,
        "invoiced_products": invoiced_products,
        "cumulative_invoice": True,
        "old_invoice_obj": old_invoice_obj,
        "project_data": project_data,
        "have_invoice_product": have_invoice_product,
    }
    return render(request, 'Projects/invoice/create_invoice.html', context)


@login_required(login_url='signin')
@permission_required(['projects.view_projectinvoices'], login_url='permission_not_allowed')
def view_invoice_cumulative(request, pk):
    """
    This function retrieves and displays a cumulative invoice for a project, including invoice products
    and deductions.
    
    """
    invoice_obj = ProjectInvoices.objects.get(pk=pk)
    invoice_products = ProjectInvoicingProducts.objects.filter(project=invoice_obj.project, invoice__lte=invoice_obj.id).order_by('id')
    # invoice_products = CumulativeInvoiceProduct.objects.filter(project=invoice_obj.project, invoice__lte=invoice_obj.id).order_by('id')
    deductions_obj = ProjectDeductionPercentage.objects.filter(project=invoice_obj.project).order_by('id')
    context = {
        'title': f'{PROJECT_NAME} | View Culmulative Invoice ',
        "invoice_obj": invoice_obj,
        "invoice_products": invoice_products,
        "deductions_obj": deductions_obj,
        "cumulative_invoice": True,

    }
    return render(request, 'Projects/invoice/view_invoice.html', context)


@login_required(login_url='signin')
@permission_required(['projects.change_projectinvoices'], login_url='permission_not_allowed')
def edit_project_cumulative_invoice(request, pk):
    """
    This function edits a project invoice and its associated products.
    
    """
    invoice_obj = ProjectInvoices.objects.get(pk=pk)
    project_obj = ProjectsModel.objects.get(pk=invoice_obj.project.id)
    invoice_products = ProjectInvoicingProducts.objects.filter(project=project_obj, invoice__lte=invoice_obj.id).order_by('id')
    form = CreateProjectInvoice(instance=invoice_obj)
    product_data = ProjectDeliveryQuantity.objects.filter(project=project_obj.id).distinct('product')
    old_invoice_obj = ProjectInvoices.objects.filter(project=project_obj)
    deductions_obj = ProjectDeductionPercentage.objects.filter(project=project_obj).order_by('id')
    PRODUCTFORM = create_invoice_form(project_obj)
    PRODUCTFORMSET = modelformset_factory(ProjectInvoicingProducts, form=PRODUCTFORM, extra=1, can_delete=True)
    product_formset = PRODUCTFORMSET(queryset=ProjectInvoicingProducts.objects.none(), prefix="invoiced_products")
    
    if request.method == 'POST':
        form = CreateProjectInvoice(request.POST, instance=invoice_obj)
        product_formset = PRODUCTFORMSET(request.POST, prefix="invoiced_products")
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.last_modified_by = request.user
            form_obj.last_modified_date = time()
            form_obj.save()
            
            messages.success(request, "Invoice Updated Successfully.")
            for item in product_formset:
                if item.is_valid():
                    item_obj = item.save(commit=False)
                    if item_obj.quantity and item_obj.invoicing_stage:
                        item_obj.project = project_obj
                        item_obj.invoice = form_obj
                        item_obj.save()
                    else:
                        print("No new product..")
                else:
                    print("ERROR IN Item==>", item.errors)
        else:
            messages.error(request, form.errors)
        return redirect('project_invoices', pk=project_obj.id)
        
    context = {
        "title": f'{PROJECT_NAME} | Update Project Invoice',
        "project": project_obj,
        "form": form,
        'product_formset': product_formset,
        "product_data": product_data,
        "deductions_obj": deductions_obj,
        "invoice_products": invoice_products,
        "invoice_obj": invoice_obj,
        "cumulative_invoice": False,
        "old_invoice_obj": old_invoice_obj
    }
    return render(request, 'Projects/invoice/edit_invoice.html', context)


@login_required(login_url="signin")
@permission_required(['projects.add_projectinvoices'], login_url='permission_not_allowed')
def project_accounts_side_view(request, project, product):
    """
    This function renders a side view page for a project's invoice with invoicing percentages and
    product information.
    
    """
    percentages = ProjectInvoicingPercentage.objects.filter(project_id=project).order_by('id')
    context = {
        "title": f"{PROJECT_NAME} | Side View",
        "percentages": percentages,
        "product": product,
    }
    return render(request, "Projects/invoice/side_page.html", context)


@login_required(login_url="signin")
def project_lost(request, q_id):
    """
    This function updates the status of an estimation version to 11 and returns a JSON response
    indicating success.
    
    """
    quotation = Quotations.objects.get(pk=q_id)
    version = EstimationVersions.objects.get(pk=quotation.estimations.version.id)
    version.status = 11
    version.save()
    return JsonResponse({'success': True}, status=200)


@login_required(login_url='signin')
def project_eps(request, pk):
    """
    This function retrieves and displays various EPS (Expanded Polystyrene) data related to a specific
    project.
    
    """
    projec_obj = ProjectsModel.objects.get(pk=pk)
    initial_eps = Eps_main.objects.filter(project=projec_obj, status__in=[1, 2]).order_by('-id')
    completed_eps = Eps_main.objects.filter(project=projec_obj, status=3)
    
    processed_products = Eps_Products.objects.filter(Q(project=projec_obj.id) & Q(eps_data__isnull=True) & ~Q(product_status=5)).order_by('id')
    eps_products = Eps_Products.objects.filter(project=projec_obj, product_status=5, eps_data__isnull=True).order_by('id')
    
    # if Eps_Products.objects.filter(quantity__isnull=False, project=projec_obj, product_status=1, eps_data__isnull=True).count() == eps_products.count():
    
    if eps_products.count() == 0:
        submit_btn = True
    else:
        submit_btn = False

    eps_submit_form = EPSSubmitForm()

    if request.method == "POST":
        eps_submit_form = EPSSubmitForm(request.POST)
        eps_product_list = request.POST.getlist('eps_products')
        try:
            E_id = Eps_main.objects.all().last().eps_id
        except Exception as e:
            E_id = None

        eps_id = int(E_id)+1 if E_id else EPS_ID
        
        if eps_submit_form.is_valid():
            eps_submit_form_obj = eps_submit_form.save(commit=False)
            eps_submit_form_obj.created_by = request.user
            eps_submit_form_obj.project=projec_obj
            eps_submit_form_obj.eps_id=eps_id
            eps_submit_form_obj.save()


            for item in eps_product_list:
                product = Eps_Products.objects.get(pk=int(item))
                if product.quantity and product.quantity != '':
                    contract_item = ProjectContractItems.objects.get(pk=product.eps_product.id)
                    issued_quantity = float(contract_item.issued_quantity) + float(product.quantity)
                    contract_item.issued_quantity = issued_quantity
                    contract_item.auth_balance = float(contract_item.auth_balance) - float(issued_quantity)
                    product.eps_data = eps_submit_form_obj
                    product.save()
                    contract_item.save()
                    eps_submit_form_obj.eps_products.add(product)

                    for item in Eps_Product_Details.objects.filter(main_product__eps_product=contract_item):
                        associated = Eps_Associated_Products(product=item, eps_product=product)
                        associated.save()
                        if item.main_product.eps_product.product.product:
                            if item.main_product.eps_product.product.product.have_associated_product:
                                quantity = float(item.product_quantity)*float(item.main_product.eps_product.product.product.assocated_quantity)
                                associated_sub = Eps_Associated_sub_Products(
                                                        main_product=item, 
                                                        name=str(item.main_product.eps_product.product.product.associated_product)+' | '+str(item.product_code),
                                                        received_quantity=quantity,
                                                        remaining_quantity=quantity,
                                                        )
                                associated_sub.save()
                        else:
                            if item.main_product.eps_product.product.panel_product.have_associated_product:
                                quantity = float(item.product_quantity)*float(item.main_product.eps_product.product.panel_product.assocated_quantity)
                                associated_sub = Eps_Associated_sub_Products(
                                                        main_product=item, 
                                                        name=str(item.main_product.eps_product.product.panel_product.associated_product)+' | '+str(item.product_code),
                                                        received_quantity=quantity,
                                                        remaining_quantity=quantity,
                                                        )
                                associated_sub.save()
                    del_key = None
                else:
                    try:
                        del_key = eps_submit_form_obj.delete()
                    except Exception:
                        del_key = None
                    break
        else:
            del_key = None
            # print("Form__ error...==>", eps_submit_form.errors)
            
        if not del_key:
            messages.success(request, "Successfully Created EPS With ID EPS-"+str(eps_id))
        else:
            messages.error(request, 'Fill out All the Details')

        return redirect('project_eps', pk=projec_obj.id)
    context = {
        "title": f'{PROJECT_NAME} | Project EPS',
        "project": projec_obj,
        "initial_eps": initial_eps,
        "completed_eps": completed_eps,
        
        "eps_products": eps_products,
        "submit_btn": submit_btn,
        "eps_submit_form": eps_submit_form,
        "processed_products": processed_products,
    }
    return render(request, 'Projects/Eps/project_eps.html', context)


@login_required(login_url='signin')
def create_eps(request, pk):
    """
    This function creates an EPS (Engineering Procurement Service) for a project and saves the EPS
    details along with associated products and their details.
    
    """
    projec_obj = ProjectsModel.objects.get(pk=pk)
    eps_products = Eps_Products.objects.filter(project=projec_obj, product_status=1, eps_data__isnull=True).order_by('id')
    
    if Eps_Products.objects.filter(quantity__isnull=False, project=projec_obj, product_status=1, eps_data__isnull=True).count() == eps_products.count():
        submit_btn = True
    else:
        submit_btn = False

    eps_submit_form = EPSSubmitForm()
    

    if request.method == "POST":
        
        eps_product_list = [int(product) for product in request.POST.getlist('eps_products')]
        
        def single_eps(pk, product_list, eps_submit_form_obj):
            
            try:
                E_id = Eps_main.objects.all().order_by('-id')[1].eps_id
                # E_id = E_id.eps_id
            except Exception as e:
                E_id = None
                
            eps_id = int(E_id)+1 if E_id else EPS_ID
            
            eps_submit_form_obj.eps_id = eps_id
            eps_submit_form_obj.save()
            
            product = Eps_Products.objects.get(pk=int(pk))
            product_objs = Eps_Products.objects.filter(pk__in=product_list)
            if product.eps_product.product.product_type == 1:
                assoc_and_secondary_products = product_objs.filter(
                                                        eps_product__product__product_type__in=[2, 3], 
                                                        eps_product__product__main_product=product.eps_product.product.id
                                                        )
            else:
                assoc_and_secondary_products = product_objs.filter(
                                                    eps_product__product__product_type__in=[1], 
                                                    eps_product__product__main_product=product.eps_product.product.main_product.id
                                                    )
            
                
            if product.quantity and product.quantity != '':
                contract_item = ProjectContractItems.objects.get(pk=product.eps_product.id)
                issued_quantity = float(contract_item.issued_quantity) + float(product.quantity)
                    
                contract_item.issued_quantity = issued_quantity
                contract_item.eps_issued = float(issued_quantity)
                contract_item.eps_balance = float(contract_item.eps_balance) - float(product.quantity)
                
                product.eps_data = eps_submit_form_obj
                product.delivery_date = eps_submit_form_obj.expec_delivery_date
                product.save()
                contract_item.save()
                eps_submit_form_obj.eps_products.add(product)

                for item in Eps_Product_Details.objects.filter(main_product__eps_product=contract_item):
                    associated = Eps_Associated_Products(product=item, eps_product=product)
                    associated.save()
                    
                    if item.main_product.eps_product.product.product:
                        if item.main_product.eps_product.product.product.have_associated_product:
                            quantity = float(item.product_quantity)*float(item.main_product.eps_product.product.product.assocated_quantity)
                            
                            print("product_quantityB==>", item.product_quantity)
                            print("assocated_quantityB==>", item.main_product.eps_product.product.product.assocated_quantity)
                            print("quantityB==>", quantity)
                            
                            associated_sub = Eps_Associated_sub_Products(
                                                    main_product=item, 
                                                    name=str(item.main_product.eps_product.product.product.associated_product)+' | '+str(item.product_code),
                                                    received_quantity=quantity,
                                                    remaining_quantity=quantity,
                                                    )
                            associated_sub.save()
                    else:
                        if item.main_product.eps_product.product.panel_product.have_associated_product:
                            quantity = float(item.product_quantity)*float(item.main_product.eps_product.product.panel_product.assocated_quantity)
                            
                            print("product_quantityC==>", item.product_quantity)
                            print("assocated_quantityC==>", item.main_product.eps_product.product.panel_product.assocated_quantity)
                            print("quantityC==>", quantity)
                            
                            associated_sub = Eps_Associated_sub_Products(
                                                    main_product=item, 
                                                    name=str(item.main_product.eps_product.product.panel_product.associated_product)+' | '+str(item.product_code),
                                                    received_quantity=quantity,
                                                    remaining_quantity=quantity,
                                                    )
                            associated_sub.save()
                del_key = None
            else:
                try:
                    del_key = eps_submit_form_obj.delete()
                except Exception:
                    del_key = None
                
            if not del_key:
                messages.success(request, "Successfully Created EPS.")
            else:
                messages.error(request, 'Fill out All the Details')
                
                
            for product_obj in assoc_and_secondary_products: 
                # print("product_obj==>", product_obj)
                if product_obj.quantity and product_obj.quantity != '':
                    contract_item = ProjectContractItems.objects.get(pk=product_obj.eps_product.id)
                    issued_quantity = float(contract_item.issued_quantity) + float(product_obj.quantity)
                        
                    contract_item.issued_quantity = issued_quantity
                    contract_item.eps_issued = float(issued_quantity)
                    contract_item.eps_balance = float(contract_item.eps_balance) - float(product_obj.quantity)
                    
                    product_obj.eps_data = eps_submit_form_obj
                    product_obj.delivery_date = eps_submit_form_obj.expec_delivery_date
                    product_obj.save()
                    contract_item.save()
                    eps_submit_form_obj.eps_products.add(product_obj)

                    eps_product_list.remove(product_obj.id)
                    for item in Eps_Product_Details.objects.filter(main_product__eps_product=contract_item):
                        associated = Eps_Associated_Products(product=item, eps_product=product_obj)
                        associated.save()
                        if item.main_product.eps_product.product.product:
                            if item.main_product.eps_product.product.product.have_associated_product:
                                quantity = float(item.product_quantity)*float(item.main_product.eps_product.product.product.assocated_quantity)
                                print("product_quantity==>", item.product_quantity)
                                print("assocated_quantity==>", item.main_product.eps_product.product.product.assocated_quantity)
                                print("quantity==>", quantity)
                                
                                associated_sub = Eps_Associated_sub_Products(
                                                        main_product=item, 
                                                        name=str(item.main_product.eps_product.product.product.associated_product)+' | '+str(item.product_code),
                                                        received_quantity=quantity,
                                                        remaining_quantity=quantity,
                                                        )
                                associated_sub.save()
                        else:
                            if item.main_product.eps_product.product.panel_product.have_associated_product:
                                quantity = float(item.product_quantity)*float(item.main_product.eps_product.product.panel_product.assocated_quantity)
                                print("product_quantityA==>", item.product_quantity)
                                print("assocated_quantityA==>", item.main_product.eps_product.product.panel_product.assocated_quantity)
                                print("quantityA==>", quantity)
                                
                                associated_sub = Eps_Associated_sub_Products(
                                                        main_product=item, 
                                                        name=str(item.main_product.eps_product.product.panel_product.associated_product)+' | '+str(item.product_code),
                                                        received_quantity=quantity,
                                                        remaining_quantity=quantity,
                                                        )
                                associated_sub.save()
                    del_key = None
                else:
                    try:
                        del_key = eps_submit_form_obj.delete()
                    except Exception:
                        del_key = None
                        
                if not del_key:
                    messages.success(request, "Successfully Created EPS.")
                else:
                    messages.error(request, 'Fill out All the Details')
            
        for item in eps_product_list:
            eps_submit_form = EPSSubmitForm(request.POST)
            if eps_submit_form.is_valid():
                eps_submit_form_obj = eps_submit_form.save(commit=False)
                eps_submit_form_obj.created_by = request.user
                eps_submit_form_obj.project = projec_obj
                eps_submit_form_obj.save()
                single_eps(item, eps_product_list, eps_submit_form_obj)
            else:
                messages.error(request, 'Check The EPS Data')
              

        return redirect('project_eps', pk=projec_obj.id)
    context = {
        "title": f'{PROJECT_NAME} | Create EPS',
        "project": projec_obj,
        "eps_products": eps_products,
        "submit_btn": submit_btn,
        "eps_submit_form": eps_submit_form,
    }
    return render(request, 'Projects/Eps/create_eps.html', context)


@login_required(login_url='signin')
def create_glass_eps(request, pk):
    """
    This function creates an EPS (Engineering Procurement Service) for a project and saves the EPS
    details along with associated products and their details.
    
    """
    projec_obj = ProjectsModel.objects.get(pk=pk)
    eps_products = Eps_Products.objects.filter( Q(project=projec_obj, eps_data__isnull=False) 
                                               & Q(
                                                      (Q(Q(is_vp=True) & ~Q(remaining_vision_panel=0)) 
                                                    | Q(Q(is_sp=True) & ~Q(remaining_spandrel_panel=0)) 
                                                    | Q(Q(is_op=True) & ~Q(remaining_openable_panel=0)))
                                                    & Q(eps_data__eps_type=1) #& Q(eps_product__product__category__is_curtain_wall=True)
                                                   ) ).order_by('-id')
    
                                            # ).distinct('eps_product')
                                            # ).distinct('eps_data')
                                                    #   | Q(Q(is_op=True) & ~Q(remaining_openable_panel=0)) 
                                                    # & Q(eps_product__product__category__is_curtain_wall=True)
                    
    eps_submit_form = EPSSubmitForm()
    
    context = {
        "title": f'{PROJECT_NAME} | Create EPS',
        "project": projec_obj,
        "eps_products": eps_products,
        # "submit_btn": submit_btn,
        "eps_submit_form": eps_submit_form,
    }
    return render(request, 'Projects/Eps/create_eps.html', context)


@login_required(login_url='signin')
def add_eps_item(request, pk):
    """
    This function adds selected products to an EPS and redirects to the create EPS page.
    """
    sales_item = SalesOrderItems.objects.get(pk=pk)
    products = ProjectContractItems.objects.get(product=sales_item)
    
    try:
        old_eps_product = Eps_Products.objects.filter(eps_product=products, eps_data__isnull=True)
    except Exception as e:
        old_eps_product = None
    
    if not old_eps_product:
        eps_product = Eps_Products(eps_product=products, project=products.project, created=request.user)
        eps_product.save()
    else:
        print("ALREADY EXIST")
    
    # eps_product = Temp_EPS_Products(product=products, project=products.project)
    # eps_product.save()
    
    # messages.success(request, "Successfully Added to EPS.")
    # return redirect('project_scop', pk=products.project.id)
    return JsonResponse({'success': True})
    

@login_required(login_url='signin')
def add_eps_item_from_model(request, pk):
    """
    This function adds selected products to an EPS and redirects to the create EPS page.
    
    """
    projec_obj = ProjectsModel.objects.get(pk=pk)
    
    products = ProjectContractItems.objects.filter(project=projec_obj)
    
    buildings_ids = []
    for product in products:
        buildings = SalesOrderGroups.objects.get(pk=product.product.sales_group.id)
        buildings_ids.append(buildings)
        
    if request.method == "POST":
        products_to_eps = request.POST.getlist('selected_products')
        
        for item in products_to_eps:
            eps_product = Eps_Products(eps_product_id=int(item), project=projec_obj, created=request.user)
            # eps_product = Temp_EPS_Products(product_id=int(item), project=projec_obj)
            eps_product.save()
            messages.success(request, "Product Successfully Added to EPS.",)
        return redirect('project_eps', pk=projec_obj.id)
    context = {
        "title": f'{PROJECT_NAME} | Add EPS Items.',
        "project": projec_obj,
        "products": products,
        "buildings_ids": set(buildings_ids)
    }
    return render(request, 'Projects/Eps/add_eps_item.html', context)


@login_required(login_url='signin')
def delete_eps_item(request, pk):
    """
    This function deletes an EPS item and its associated details from the database and displays a
    success or error message.
    """
    eps_item = Eps_Products.objects.get(pk=pk)
    details = Eps_Product_Details.objects.filter(main_product=eps_item)
    eps_infill = Eps_infill_Details.objects.filter(main_product=eps_item)
    eps_infill_temp = Eps_infill_Temp.objects.filter(main_product=eps_item)
    
    if request.method == "POST":
        try:
            details.delete()
            eps_infill.delete()
            eps_infill_temp.delete()
            
            eps_item.delete()
            messages.success(request, "EPS Item Deleted Successfully")
        except Exception as e:
            print('E==>', e)
            messages.error(request, "Unable to delete the data. Already used in application.")
        return redirect('project_eps', pk=eps_item.project.id)
    context = {
                "url": f"/Project/delete_eps_item/{str(pk)}/"
              }
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
def eps_collaps_data(request, pk):
    """
    This function handles the creation and editing of EPS products, including their details and infill
    details, and renders the appropriate template based on the product category.
    """
    
    eps_item = Eps_Products.objects.get(pk=pk)
    product_obj = SalesOrderItems.objects.get(pk=eps_item.eps_product.product.id)
    project_item = ProjectContractItems.objects.get(product=product_obj)
    
    eps_history_objs = Eps_main.objects.filter(eps_products__eps_product__product=eps_item.eps_product.product)
    sales_accessories_objs = SalesOrderAccessories.objects.filter(product=product_obj)
    
    try:
        # pro_infill_details = SalesOrderInfill.objects.get(product=product_obj, infill_primary=True)
        # pro_sec_infill_details = SalesOrderInfill.objects.filter(product=product_obj, infill_primary=False)
        pro_infill_details = SalesOrderSpecification.objects.get(pk=product_obj.specification_Identifier.id)
        pro_sec_infill_details = SalesSecondarySepcPanels.objects.filter(specifications=product_obj.specification_Identifier.id)
        
        flag_vision_panel = None
        flag_spandrel_panel = None
        flag_openable_panel = None
        
        for pro_sec_infill in pro_sec_infill_details:
            if pro_sec_infill.panel_type == 1 and pro_infill_details.have_vision_panels:
                flag_vision_panel = True 
                
            if pro_sec_infill.panel_type == 2 and pro_infill_details.have_spandrel_panels:
                flag_spandrel_panel = True 
            if pro_sec_infill.panel_type == 3 and pro_infill_details.have_openable_panels:
                flag_openable_panel = True 
        
    except Exception as e:
        print("EE=>", e)
        pro_sec_infill_details = None
        
        flag_vision_panel = None
        flag_spandrel_panel = None
        flag_openable_panel = None

    eps_product_form = EPSProductForm(instance=eps_item)
    EPS_ProductDetalForm = EPSProductDetails(product_obj.category)
    PRODUCTDETAILFORMSET = modelformset_factory(Eps_Product_Details, form=EPS_ProductDetalForm, extra=1, can_delete=True)
    
    eps_infill_form = eps_infill_details(product_obj.specification_Identifier)
    EPSINFILLDETAILS = modelformset_factory(Eps_infill_Details, form=eps_infill_form, extra=1, can_delete=True)
    
    eps_spandrel_form = eps_spandrel_details(product_obj.specification_Identifier)
    EPSSPANDRELDETAILS = modelformset_factory(Eps_infill_Details, form=eps_spandrel_form, extra=1, can_delete=True)
    
    eps_openable_form = eps_openable_details(product_obj.specification_Identifier)
    EPSOPENALEDETAILS = modelformset_factory(Eps_infill_Details, form=eps_openable_form, extra=1, can_delete=True)
    
    try:
        details = Eps_Product_Details.objects.filter(main_product=eps_item)
    except Exception:
        details = None
        
    if details:
        product_detail_formset = PRODUCTDETAILFORMSET(queryset=Eps_Product_Details.objects.filter(main_product=eps_item), prefix="eps_product_detail")
        infill_detail_formset = EPSINFILLDETAILS(queryset=Eps_infill_Details.objects.filter(main_product=eps_item, panel_type=1), prefix='eps_infill')
        spandrel_detail_formset = EPSSPANDRELDETAILS(queryset=Eps_infill_Details.objects.filter(main_product=eps_item, panel_type=2), prefix='eps_spandrel_panel')
        openable_panel = EPSOPENALEDETAILS(queryset=Eps_infill_Details.objects.filter(main_product=eps_item, panel_type=3), prefix='eps_openable_panel')
    else:
        product_detail_formset = PRODUCTDETAILFORMSET(queryset=Eps_Product_Details.objects.none(), prefix="eps_product_detail")
        infill_detail_formset = EPSINFILLDETAILS(queryset=Eps_infill_Details.objects.none(), prefix='eps_infill')
        spandrel_detail_formset = EPSSPANDRELDETAILS(queryset=Eps_infill_Details.objects.none(), prefix='eps_spandrel_panel')
        openable_panel = EPSOPENALEDETAILS(queryset=Eps_infill_Details.objects.none(), prefix='eps_openable_panel')
    
    
    if request.method == "POST":
        eps_product_form = EPSProductForm(request.POST, request.FILES, instance=eps_item)
        product_detail_formset = PRODUCTDETAILFORMSET(request.POST, prefix="eps_product_detail")
        infill_detail_formset = EPSINFILLDETAILS(request.POST, prefix='eps_infill')
        spandrel_detail_formset = EPSSPANDRELDETAILS(request.POST, prefix='eps_spandrel_panel')
        openable_panel = EPSOPENALEDETAILS(request.POST, prefix='eps_openable_panel')
        
        # eps_area = request.POST.get('id_eps_area')
        
        if eps_product_form.is_valid():
            eps_product_form.save()
            eps_item.remaining_vision_panel = eps_item.vision_panel
            eps_item.remaining_spandrel_panel = eps_item.spandrel_panel
            eps_item.remaining_openable_panel = eps_item.openable_panel
            # eps_item.eps_total_area = eps_area
            eps_item.save()
            
            for item in product_detail_formset:
                if item.is_valid():
                    item_obj = item.save(commit=False)
                    if item_obj.product_quantity:
                        item_obj.main_product = eps_item
                        item_obj.product_type = product_obj.product_code
                        item_obj.save()
                        eps_item.product_status = 1
                        eps_item.save()
                    else:
                        messages.error(request, "Please Enter Quantity.")
                        print('Please Enter PRODUCt Quantity')
                else:
                    print("Error in sub formset ==>", item.errors)
                    messages.error(request, item.errors)
            
            for item2 in infill_detail_formset:
                if item2.is_valid():
                    item_obj2 = item2.save(commit=False)
                    if item_obj2.infill_quantity:
                        item_obj2.main_product = eps_item
                        item_obj2.panel_type = 1
                        item_obj2.save()
                        
                    else:
                        # messages.error(request, "Please Enter Quantity.")
                        print("Please Enter Infill Quantity.")
                else:
                    print("Error in sub formset infill ==>", item2.errors)
                    messages.error(request, item2.errors)
            
            for item3 in spandrel_detail_formset:
                if item3.is_valid():
                    item_obj3 = item3.save(commit=False)
                    if item_obj3.infill_quantity:
                        item_obj3.main_product = eps_item
                        item_obj3.panel_type = 2
                        item_obj3.save()
                    else:
                        # messages.error(request, "Please Enter Quantity.")
                        print("Please Enter Spandrel Panel Quantity.")
                else:
                    print("Error in sub formset Spandrel ==>", item3.errors)
                    messages.error(request, item3.errors)
            
            for item4 in openable_panel:
                if item4.is_valid():
                    item_obj4 = item4.save(commit=False)
                    if item_obj4.infill_quantity:
                        item_obj4.main_product = eps_item
                        item_obj4.panel_type = 3
                        item_obj4.save()
                    else:
                        # messages.error(request, "Please Enter Quantity.")
                        print("Please Enter Openable Panel Quantity.")
                else:
                    print("Error in sub formset Openable ==>", item4.errors)
                    messages.error(request, item4.errors)
            
            
            
            sub_products = Eps_Product_Details.objects.filter(main_product=eps_item.id)
            area = 0
            
            for sub_product in sub_products:
                if sub_product.product_total_area:
                    area += float(sub_product.product_total_area)
                else:
                    area += 0
                    
            
            if not eps_item.infill_remaining_area:
                if eps_item.eps_area:
                    eps_item.infill_remaining_area = eps_item.eps_total_area
                else:
                    eps_item.infill_remaining_area = area
                    
                eps_item.save()
            
            messages.success(request, "Item Added Successfully to EPS Cart.")
        else:
            print("Error===>", eps_product_form.errors)
            messages.error(request, eps_product_form.errors)
            
        return redirect('project_eps', pk=eps_item.project.id)
    
    
    context = {
        "eps_item": eps_item,
        "product_obj": product_obj,
        # "product_details": product_details,
        "eps_product_form": eps_product_form,
        "product_detail_formset": product_detail_formset,
        # "pro_infill_details": pro_infill_details,
        "pro_sec_infill_details": pro_sec_infill_details,
        "infill_detail_formset": infill_detail_formset,
        "product_datas": details,
        "project_item": project_item,
        "eps_history_objs": eps_history_objs,
        "sales_accessories_objs": sales_accessories_objs,
        "spandrel_detail_formset": spandrel_detail_formset,
        "openable_panel": openable_panel,
        "flag_vision_panel": flag_vision_panel,
        "flag_spandrel_panel": flag_spandrel_panel,
        "flag_openable_panel": flag_openable_panel,
    }
    
    if product_obj.product_type == 3:
        
        if (product_obj.product.uom.uom).lower() == 'lm':
            return render(request,"Projects/Eps/eps_create_secondary_product_lm.html", context)
        else:
            return render(request,"Projects/Eps/eps_create_secondary_product.html", context)
        
    else:
        
        if product_obj.category.is_curtain_wall:
            return render(request,"Projects/Eps/eps_create_curtainwall_type.html", context)
        elif product_obj.category.handrail:
            return render(request,"Projects/Eps/eps_create_handrail_type.html", context)
        else:
            return render(request,"Projects/Eps/eps_create_window_door_type.html", context)
    
        
@login_required(login_url='signin')
def glass_eps_collaps_data(request, pk):
    """
    This function handles the creation and editing of EPS products, including their details and infill
    details, and renders the appropriate template based on the product category.
    
    """
    
    eps_item = Eps_Products.objects.get(pk=pk)
    product_obj = SalesOrderItems.objects.get(pk=eps_item.eps_product.product.id)
    project_item = ProjectContractItems.objects.get(product=product_obj)
    
    
    try:
        pro_infill_details = SalesOrderSpecification.objects.get(pk=product_obj.specification_Identifier.id)
        pro_sec_infill_details = SalesSecondarySepcPanels.objects.filter(specifications=product_obj.specification_Identifier.id)
        
        flag_vision_panel = None
        flag_spandrel_panel = None
        flag_openable_panel = None
        
        for pro_sec_infill in pro_sec_infill_details:
            if pro_sec_infill.panel_type == 1 and pro_infill_details.have_vision_panels:
                flag_vision_panel = True 
                
            if pro_sec_infill.panel_type == 2 and pro_infill_details.have_spandrel_panels:
                flag_spandrel_panel = True 
            if pro_sec_infill.panel_type == 3 and pro_infill_details.have_openable_panels:
                flag_openable_panel = True 
                
    except Exception as e:
        # pro_infill_details = None
        pro_sec_infill_details = None
        
        flag_vision_panel = None
        flag_spandrel_panel = None
        flag_openable_panel = None

    eps_product_note = eps_item.eps_product_note
    eps_item2_id = eps_item.id
    
    # eps_product_form = EPSProductForm(instance=eps_item)
    eps_product_form = infillEPSform(instance=eps_item)
    eps_product_form1 = infillEPSform(instance=eps_item)
    # eps_product_form = infillEPSform()
    eps_submit_form = EPSSubmitForm()
    # EPS_ProductDetalForm = EPSProductDetails(product_obj.category)
    # PRODUCTDETAILFORMSET = modelformset_factory(Eps_Product_Details, form=EPS_ProductDetalForm, extra=1, can_delete=True)
    
    eps_infill_form = eps_infill_details(product_obj.specification_Identifier)
    EPSINFILLDETAILS = modelformset_factory(Eps_infill_Details, form=eps_infill_form, extra=1, can_delete=True)
    
    eps_spandrel_form = eps_spandrel_details(product_obj.specification_Identifier)
    EPSSPANDRELDETAILS = modelformset_factory(Eps_infill_Details, form=eps_spandrel_form, extra=1, can_delete=True)
    
    eps_openable_form = eps_openable_details(product_obj.specification_Identifier)
    EPSOPENALEDETAILS = modelformset_factory(Eps_infill_Details, form=eps_openable_form, extra=1, can_delete=True)
    
    try:
        details = Eps_Product_Details.objects.filter(main_product=eps_item)
    except Exception:
        details = None


    if details:
        # product_detail_formset = PRODUCTDETAILFORMSET(queryset=Eps_Product_Details.objects.filter(main_product=eps_item), prefix="eps_product_detail")
        infill_detail_formset = EPSINFILLDETAILS(queryset=Eps_infill_Details.objects.filter(main_product=eps_item, panel_type=1), prefix='eps_infill')
        spandrel_detail_formset = EPSSPANDRELDETAILS(queryset=Eps_infill_Details.objects.filter(main_product=eps_item, panel_type=2), prefix='eps_spandrel_panel')
        openable_panel = EPSOPENALEDETAILS(queryset=Eps_infill_Details.objects.filter(main_product=eps_item, panel_type=3), prefix='eps_openable_panel')
    
    else:
        # product_detail_formset = PRODUCTDETAILFORMSET(queryset=Eps_Product_Details.objects.none(), prefix="eps_product_detail")
        infill_detail_formset = EPSINFILLDETAILS(queryset=Eps_infill_Details.objects.none(), prefix='eps_infill')
        spandrel_detail_formset = EPSSPANDRELDETAILS(queryset=Eps_infill_Details.objects.none(), prefix='eps_spandrel_panel')
        openable_panel = EPSOPENALEDETAILS(queryset=Eps_infill_Details.objects.none(), prefix='eps_openable_panel')
        
    infill_total_area = 0
    
    if request.method == "POST":
        
        # eps_product_form = infillEPSform(request.POST)
        eps_submit_form = EPSSubmitForm(request.POST)
        infill_detail_formset = EPSINFILLDETAILS(request.POST, prefix='eps_infill')
        spandrel_detail_formset = EPSSPANDRELDETAILS(request.POST, prefix='eps_spandrel_panel')
        openable_panel = EPSOPENALEDETAILS(request.POST, prefix='eps_openable_panel')

        total_area_infills = request.POST.getlist('total_area_infill')

        if eps_submit_form.is_valid():
            eps_product_form1 = infillEPSform(request.POST, instance=eps_item)
            
            
            if eps_product_form1.is_valid():
                old_eps_product_obj = eps_product_form1.save()
                
            old_eps_product_obj.pk = None
            old_eps_product_obj.save()
            duplicated_eps_item = old_eps_product_obj
            
            eps_product_form = infillEPSform(request.POST, instance=duplicated_eps_item)
                
            if eps_product_form.is_valid():
                new_product_obj = eps_product_form.save()
            
            eps_submit_form_obj = eps_submit_form.save(commit=False)
            eps_submit_form_obj.created_by = request.user
            eps_submit_form_obj.project = product_obj.specification_Identifier.project
            eps_submit_form_obj.eps_type = 2
            eps_submit_form_obj.save()
            
            
            try:
                E_id = Eps_main.objects.all().order_by('-id')[1].eps_id
            except Exception as e:
                E_id = None
            
            eps_id = int(E_id)+1 if E_id else EPS_ID
            
            
            eps_submit_form_obj.eps_id = eps_id
            eps_submit_form_obj.eps_products.add(new_product_obj)
            eps_submit_form_obj.save()
            
            new_product_obj.eps_data = eps_submit_form_obj
            new_product_obj.product_status = 1
            new_product_obj.aluminium_status = 5
            new_product_obj.accessory_status = 5
            new_product_obj.infill_status = 1
            new_product_obj.shopfloor_status = 1
            new_product_obj.qaqc_status = None
            new_product_obj.inspection_status = 1
            new_product_obj.save()
        
            vision_panel_qty = 0
            spandrel_panel_qty = 0
            openable_panel_qty = 0
            
            eps_item2_obj = Eps_Products.objects.get(pk=eps_item2_id)
            eps_item2_obj.eps_product_note = eps_product_note
            # eps_item2_obj.save()
            
            for item2 in infill_detail_formset:
                print("A")
                if item2.is_valid():
                    print("A1")
                    item_obj2 = item2.save(commit=False)
                    if item_obj2.infill_quantity and item_obj2.infill:
                        print("A11")
                        vision_panel_qty += item_obj2.infill_quantity
                        item_obj2.main_product = eps_item
                        item_obj2.panel_type = 1
                        item_obj2.main_product = duplicated_eps_item
                        item_obj2.form_infill_eps = True
                        item_obj2.eps_ref=eps_submit_form_obj
                        item_obj2.save()
                        print('Vision Panel', item_obj2.infill_quantity)
                    else:
                        # messages.error(request, "Please Enter Quantity.")
                        print("Please Enter Infill Quantity.")
                else:
                    print("1 Error in sub formset infill ==>", item2.errors)
                    messages.error(request, item2.errors)
            
            for item3 in spandrel_detail_formset:
                print("B")
                if item3.is_valid():
                    print("B1")
                    item_obj3 = item3.save(commit=False)
                    if item_obj3.infill_quantity and item_obj3.infill:
                        print("B11")
                        spandrel_panel_qty += item_obj3.infill_quantity
                        item_obj3.main_product = eps_item
                        item_obj3.panel_type = 2
                        item_obj3.form_infill_eps = True
                        item_obj3.main_product = duplicated_eps_item
                        item_obj3.eps_ref=eps_submit_form_obj
                        item_obj3.save()
                        print('Spandrel Panel', item_obj3.infill_quantity)
                    else:
                        # messages.error(request, "Please Enter Quantity.")
                        print("Please Enter Spandrel Panel Quantity.")
                else:
                    print("2 Error in sub formset spandrel panel ==>", item3.errors)
                    messages.error(request, item3.errors)
            
            for item4 in openable_panel:
                if item4.is_valid():
                    item_obj4 = item4.save(commit=False)
                    if item_obj4.infill_quantity and item_obj4.infill:
                        openable_panel_qty += item_obj4.infill_quantity
                        item_obj4.main_product = eps_item
                        item_obj4.panel_type = 3
                        item_obj4.form_infill_eps = True
                        item_obj4.main_product = duplicated_eps_item
                        item_obj4.eps_ref = eps_submit_form_obj
                        item_obj4.save()
                        print('Openable Panel', item_obj4.infill_quantity)
                    else:
                        # messages.error(request, "Please Enter Quantity.")
                        print("Please Enter Openable Panel Quantity.")
                else:
                    print("3 Error in sub formset Openable Panel ==>", item4.errors)
                    messages.error(request, item4.errors)
                                        
                messages.success(request, "Successfully Added.")
            
            # Update the main item
            if eps_item.vision_panel and eps_item.remaining_vision_panel:
                v_qty = float(eps_item.remaining_vision_panel) - float(vision_panel_qty)
                eps_item.remaining_vision_panel = v_qty
                eps_item2_obj.remaining_vision_panel = v_qty
                eps_item.is_vp = v_qty != 0
                eps_item2_obj.is_vp = v_qty != 0

            if eps_item.spandrel_panel and eps_item.remaining_spandrel_panel:
                s_qty = float(eps_item.remaining_spandrel_panel) - float(spandrel_panel_qty)
                eps_item.remaining_spandrel_panel = s_qty
                eps_item2_obj.remaining_spandrel_panel = s_qty
                eps_item.is_sp = s_qty != 0
                eps_item2_obj.is_sp = s_qty != 0

            if eps_item.openable_panel and eps_item.remaining_openable_panel:
                o_qty = float(eps_item.remaining_openable_panel) - float(openable_panel_qty)
                eps_item.remaining_openable_panel = o_qty
                eps_item2_obj.remaining_openable_panel = o_qty
                eps_item.is_op = o_qty != 0
                eps_item2_obj.is_op = o_qty != 0

            for total_area_infill in total_area_infills:
                
                if total_area_infill:
                    infill_total_area += float(total_area_infill)
            
            
            remaining_infill_area = float(eps_item.infill_remaining_area) - float(infill_total_area)
            eps_item.save()
            eps_item2_obj.infill_remaining_area = remaining_infill_area
            eps_item2_obj.save()

            eps_item_objs = Eps_Products.objects.filter(
                                                    eps_product=eps_item2_obj.eps_product.id, 
                                                    vision_panel=eps_item2_obj.vision_panel, 
                                                    spandrel_panel=eps_item2_obj.spandrel_panel, 
                                                    openable_panel=eps_item2_obj.openable_panel
                                                ).exclude(pk__in=[eps_item.id, eps_item2_obj.id])
            for item in eps_item_objs:
                if item.vision_panel and item.remaining_vision_panel:
                    v_qty = float(item.remaining_vision_panel) - float(vision_panel_qty)
                    item.remaining_vision_panel = v_qty
                    item.is_vp = v_qty != 0

                if item.spandrel_panel and item.remaining_spandrel_panel:
                    s_qty = float(item.remaining_spandrel_panel) - float(spandrel_panel_qty)
                    item.remaining_spandrel_panel = s_qty
                    item.is_sp = s_qty != 0

                if item.openable_panel and item.remaining_openable_panel:
                    o_qty = float(item.remaining_openable_panel) - float(openable_panel_qty)
                    item.remaining_openable_panel = o_qty
                    item.is_op = o_qty != 0

                item.save()
            
            
            
        return redirect('create_glass_eps', pk=eps_item.project.id)
    
    context = {
        "eps_item": eps_item,
        "product_obj": product_obj,
        "eps_product_form": eps_product_form,
        "eps_submit_form": eps_submit_form,
        "pro_sec_infill_details": pro_sec_infill_details,
        "product_datas": details,
        "project_item": project_item,
        "infill_detail_formset": infill_detail_formset,
        "spandrel_detail_formset": spandrel_detail_formset,
        "openable_panel": openable_panel,
        "flag_vision_panel": flag_vision_panel,
        "flag_spandrel_panel": flag_spandrel_panel,
        "flag_openable_panel": flag_openable_panel,
    }
    
    return render(request,"Projects/Eps/infill_eps_create_view.html", context)
        

@login_required(login_url='signin')
def download_eps_attachments(request, path):
    """
    This function downloads an attachment file from a specified path and returns it as a FileResponse
    object.
    
    """
    file = open(f'media/{path}', 'rb')
    response = FileResponse(file)
    response['content_type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(path.split("/")[-1])
    return response


@login_required(login_url='signin')
def download_eps_fabrication(request, path):
    """
    This function downloads a file from a specified path and returns it as a response with the
    appropriate content type and content disposition headers.
    
    """
    file = open(f'media/{path}', 'rb')
    response = FileResponse(file)
    response['content_type'] = 'application/octet-stream'
    response[
        'Content-Disposition'
    ] = f'attachment; filename="{path.split("/")[-1]}"'
    return response


@login_required(login_url='signin')
def view_eps(request, eps, product=None):
    """
    This function retrieves and displays various details related to an EPS (Expanded Polystyrene)
    product.
    
    """
    eps_obj = Eps_main.objects.get(pk=eps)
    products_obj = Eps_Products.objects.filter(eps_data=eps_obj)
    if not product:
        product = products_obj.first()
    else:
        product = Eps_Products.objects.get(pk=product)

    product_data = SalesOrderItems.objects.get(pk=product.eps_product.product.id)
    # product_data = EstimationMainProduct.objects.get(pk=product.eps_product.product.id)
    # product_aluminium = MainProductAluminium.objects.get(estimation_product=product_data)

    eps_products_details = Eps_Product_Details.objects.filter(main_product=product)

    add_infill_btn = None
    for p in products_obj:
        if p.infill_status == 2:
            add_infill_btn = 1

    eps_infill_details = Eps_infill_Details.objects.filter(
        main_product=product
        ).distinct('infill__panel_specification__specifications')
    attachments = Fabrication_Attachments.objects.filter(eps_product=product)

    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(product=product)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None

    try:
        scedule_details = Schedule_Product.objects.get(product__main_products__main_product=product)
    except Schedule_Product.DoesNotExist:
        scedule_details = None

    qaqc_products_details = Workstation_Data.objects.filter(
        eps_product_id=product, product__main_products__main_product__eps_data=eps_obj)
    qaqc_associated_products = Workstation_Associated_Products_Data.objects.filter(
        eps_product_id=product, product__main_product__main_product__eps_data=eps_obj)
    qaqc_infills = QAQC_infill_Products.objects.filter(
        product__infill_product__main_product__eps_data=eps_obj)

    try:
        infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
        sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
        # infill_details = MainProductGlass.objects.get(estimation_product=product_data, glass_primary=True)
        # sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_data, glass_primary=False)
    except Exception as e:
        infill_details = None
        sec_infill_details = None

    delivery_notes = Delivery_Note.objects.filter(main_product__in=[data.id for data in qaqc_products_details])

    context = {
        'title': f'{PROJECT_NAME} | View EPS',
        'products_obj': products_obj,
        'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,
        'infill_details': infill_details,
        'sec_infill_details': sec_infill_details,
        'eps_products_details': eps_products_details,
        'eps_infill_details': eps_infill_details,
        'attachments': attachments,
        'add_infill_btn': add_infill_btn,
        'shopfloor_eps_data': shopfloor_eps_data,
        'shopfloor_attachments': shopfloor_attachments,
        'qaqc_products_details': qaqc_products_details,
        'qaqc_associated_products': qaqc_associated_products,
        'qaqc_infills': qaqc_infills,
        'delivery_notes': delivery_notes,
        'scedule_details': scedule_details,
    }
    return render(request,"Projects/Eps/EPS_View.html", context)


@login_required(login_url='signin')
def view_eps_product(request, pk):
    """
    This function retrieves and displays details of an EPS product for viewing.
    
    """
    product = Eps_Products.objects.get(pk=pk)
    eps_obj = Eps_main.objects.get(pk=product.eps_data.id)
    products_obj = Eps_Products.objects.filter(eps_data=eps_obj)
    product_data = SalesOrderItems.objects.get(pk=product.eps_product.product.id)
    # product_data = EstimationMainProduct.objects.get(pk=product.eps_product.product.id)
    # product_aluminium = MainProductAluminium.objects.get(estimation_product=product_data)
    
    eps_products_details = Eps_Product_Details.objects.filter(main_product=product)
    add_infill_btn = None
    for p in products_obj:
        if p.infill_status == 2:
            add_infill_btn = 1
    
    eps_infill_details = Eps_infill_Details.objects.filter(
        main_product=product
        ).distinct('infill__panel_specification__specifications')
    
    attachments = Fabrication_Attachments.objects.filter(
        eps_product=product)
    
    try:
        infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
        sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
        # infill_details = MainProductGlass.objects.get(estimation_product=product_data, glass_primary=True)
        # sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_data, glass_primary=False)
    except Exception as e:
        infill_details = None
        sec_infill_details = None
        
    context = {
        'title': f'{PROJECT_NAME} | View EPS',
        'products_obj': products_obj,
        'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,
        'infill_details': infill_details,
        'sec_infill_details': sec_infill_details,
        'eps_products_details': eps_products_details,
        'eps_infill_details': eps_infill_details,
        'attachments': attachments,
        'add_infill_btn': add_infill_btn
        
    }
    return render(request,"Projects/Eps/EPS_View.html", context)


@login_required(login_url='signin')
def eps_view_fabrications(request, pk):
    """
    This function retrieves and displays details of an EPS product and its associated data for viewing
    in a web page.
    
    """
    product = Eps_Products.objects.get(pk=pk)
    eps_obj = Eps_main.objects.get(pk=product.eps_data.id)
    products_obj = Eps_Products.objects.filter(eps_data=eps_obj)

    product_data = SalesOrderItems.objects.get(pk=product.eps_product.product.id)
    # product_data = EstimationMainProduct.objects.get(pk=product.eps_product.product.id)
    # product_aluminium = MainProductAluminium.objects.get(estimation_product=product_data)

    eps_products_details = Eps_Product_Details.objects.filter(main_product=product)
    eps_infill_details = Eps_infill_Details.objects.filter(
        main_product=product
        ).distinct('infill__panel_specification__specifications')
    attachments = Fabrication_Attachments.objects.filter(
        eps_product=product)
    try:
        infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
        sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
        # infill_details = MainProductGlass.objects.get(estimation_product=product_data, glass_primary=True)
        # sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_data, glass_primary=False)
    except Exception as e:
        infill_details = None
        sec_infill_details = None

    context = {
        'title': f'{PROJECT_NAME} | View EPS',
        'products_obj': products_obj,
        'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,
        'infill_details': infill_details,
        'sec_infill_details': sec_infill_details,
        'eps_products_details': eps_products_details,
        'eps_infill_details': eps_infill_details,
        'attachments': attachments,
    }
    return render(request,"Projects/Eps/eps_view/fabrication_view.html", context)


@login_required(login_url='signin')
def eps_production_view(request, pk):
    """
    This function retrieves data related to an EPS product and its components and renders it in a view.
    
    """
    product = Eps_Products.objects.get(pk=pk)
    eps_obj = Eps_main.objects.get(pk=product.eps_data.id)
    products_obj = Eps_Products.objects.filter(eps_data=eps_obj).order_by('-eps_data__created_date')
    
    # product_data = EstimationMainProduct.objects.get(pk=product.eps_product.product.id)
    # product_aluminium = MainProductAluminium.objects.get(estimation_product=product_data)
    
    product_data = SalesOrderItems.objects.get(pk=product.eps_product.product.id)
    project_item = ProjectContractItems.objects.get(product=product_data)
    eps_products_details = Eps_Product_Details.objects.filter(main_product=product)
    
    outsourced_infill = Eps_Outsource_items.objects.filter(infill_product__main_product=product, )
    
    if eps_obj.eps_type == 1:
        infill_schedule_obj = None
    else:
        try:
            infill_schedule_obj = InfillSchedule.objects.get(product=product)
        except Exception:
            infill_schedule_obj = None
        
    # eps_vision_panel_details = Eps_infill_Details.objects.filter(
    #     main_product=product,
    #     panel_type=1
    #     ).distinct('infill__panel_specification__specifications')
    # eps_pandrel_panel_details = Eps_infill_Details.objects.filter(
    #     main_product=product,
    #     panel_type=2
    #     ).distinct('infill__panel_specification__specifications')
    # eps_openable_panel_details = Eps_infill_Details.objects.filter(
    #     main_product=product,
    #     panel_type=3
    #     ).distinct('infill__panel_specification__specifications')
    
    attachments = Fabrication_Attachments.objects.filter(
        eps_product=product)
    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(product=product)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception as e:
        print("E==>", e)
        shopfloor_eps_data = None
        shopfloor_attachments = None
    
    
        
        
    try:
        # infill_details = MainProductGlass.objects.get(estimation_product=product_data, glass_primary=True)
        # sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_data, glass_primary=False)
        infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
        sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
    except Exception as e:
        infill_details = None
        sec_infill_details = None
    
    context = {
        'title': f'{PROJECT_NAME} | View EPS',
        'products_obj': products_obj,
        'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,
        'infill_details': infill_details,
        'sec_infill_details': sec_infill_details,
        'eps_products_details': eps_products_details,
        # 'eps_infill_details': eps_infill_details,
        # 'eps_vision_panel_details': eps_vision_panel_details,
        # 'eps_pandrel_panel_details': eps_pandrel_panel_details,
        # 'eps_openable_panel_details': eps_openable_panel_details,
        'infill_schedule_obj': infill_schedule_obj,
        'attachments': attachments,
        'shopfloor_eps_data': shopfloor_eps_data,
        'shopfloor_attachments': shopfloor_attachments,
        'outsourced_infill': outsourced_infill,
        'project_item': project_item,
    }
    return render(request,"Projects/Eps/eps_view/production_view.html", context)
    
    
@login_required(login_url='signin')
def eps_product_view(request, pk):
    """
    This function retrieves and displays details of a specific EPS product.
    
    """
    eps_item = Eps_Products.objects.get(pk=pk)
    # product_obj = EstimationMainProduct.objects.get(pk=eps_item.eps_product.product.id)
    product_obj = SalesOrderItems.objects.get(pk=eps_item.eps_product.product.id)
    products_details = Eps_Product_Details.objects.filter(main_product=eps_item)
    infill_details = Eps_infill_Details.objects.filter(main_product=eps_item)
    # product_details = MainProductAluminium.objects.get(estimation_product=product_obj)
    
    try:
        attachments = Fabrication_Attachments.objects.filter(eps_product=eps_item).last()
    except Exception:
        attachments = None
    
    try:
        pro_infill_details = SalesOrderInfill.objects.get(product=product_obj, infill_primary=True)
        pro_sec_infill_details = SalesOrderInfill.objects.filter(product=product_obj, infill_primary=False)
        # pro_infill_details = MainProductGlass.objects.get(estimation_product=product_obj, glass_primary=True)
        # pro_sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_obj, glass_primary=False)
    except Exception as e:
        pro_infill_details = None
        pro_sec_infill_details = None
    
    context = {
        "eps_item": eps_item,
        "product_obj": product_obj,
        # "product_details": product_details,
        "pro_sec_infill_details": pro_sec_infill_details,
        "pro_infill_details": pro_infill_details,
        "products_details": products_details,
        "infill_details": infill_details,
        "attachments": attachments,
    }
    return render(request, "Projects/Eps/product_detail_eps.html", context)


@login_required(login_url='signin')
def eps_product_product_view(request, pk):
    """
    This function displays the details of a specific EPS product and allows the user to add or edit
    infill details for the product.
    
    """
    eps_item = Eps_Products.objects.get(pk=pk)
    product_obj = SalesOrderItems.objects.get(pk=eps_item.eps_product.product.id)
    # product_obj = EstimationMainProduct.objects.get(pk=eps_item.eps_product.product.id)
    products_details = Eps_Product_Details.objects.filter(main_product=eps_item)
    infill_details = Eps_infill_Details.objects.filter(main_product=eps_item)
    # product_details = MainProductAluminium.objects.get(estimation_product=product_obj)
    add_infill_btn = any(product.infill_status for product in Eps_Products.objects.filter(eps_data=eps_item.eps_data.id))
    shopfloors = Shopfloors.objects.all().order_by('id')
    try:
        pro_infill_details = SalesOrderInfill.objects.get(product=product_obj, infill_primary=True)
        pro_sec_infill_details = SalesOrderInfill.objects.filter(product=product_obj, infill_primary=False)
        # pro_infill_details = MainProductGlass.objects.get(estimation_product=product_obj, glass_primary=True)
        # pro_sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_obj, glass_primary=False)
    except Exception:
        pro_infill_details = None
        pro_sec_infill_details = None
        
    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(eps=eps_item.eps_data, product=eps_item)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None
        
    eps_infill_form = eps_infill_details(product_obj)
    EPSINFILLDETAILS = modelformset_factory(Eps_infill_Details, form=eps_infill_form, extra=1, can_delete=True)
    infill_detail_formset = EPSINFILLDETAILS(queryset=Eps_infill_Details.objects.none(), prefix='eps_infill')
    
    # spandrel_detail_formset = EPSINFILLDETAILS(queryset=Eps_infill_Details.objects.filter(main_product=eps_item, panel_type=2), prefix='eps_spandrel_panel')
    # openable_panel = EPSINFILLDETAILS(queryset=Eps_infill_Details.objects.filter(main_product=eps_item, panel_type=3), prefix='eps_openable_panel')
    
    spandrel_detail_formset = EPSINFILLDETAILS(queryset=Eps_infill_Details.objects.none(), prefix='eps_spandrel_panel')
    openable_panel = EPSINFILLDETAILS(queryset=Eps_infill_Details.objects.none(), prefix='eps_openable_panel')
        
    if request.method == "POST":
        infill_detail_formset = EPSINFILLDETAILS(request.POST, prefix='eps_infill')
        
        spandrel_detail_formset = EPSINFILLDETAILS(request.POST, prefix='eps_spandrel_panel')
        openable_panel = EPSINFILLDETAILS(request.POST, prefix='eps_openable_panel')
    
        for item2 in infill_detail_formset:
            if item2.is_valid():
                item_obj2 = item2.save(commit=False)
                if item_obj2.infill_quantity and item_obj2.infill_area:
                    item_obj2.main_product = eps_item
                    item_obj2.panel_type = 1
                    item_obj2.save()
                    outsource_product = Eps_Outsource_items(infill_product=item_obj2, received_quantity=0)
                    outsource_product.save()
                else:
                    # messages.error(request, "Please Enter Quantity.")
                    print("Please Enter Infill Quantity.")
            else:
                print("Error in sub formset infill ==>", item2.errors)
                messages.error(request, item2.errors)
        
        
        for item3 in spandrel_detail_formset:
            if item3.is_valid():
                item_obj3 = item3.save(commit=False)
                if item_obj3.infill_quantity and item_obj3.infill_area:
                    item_obj3.main_product = eps_item
                    item_obj3.panel_type = 2
                    item_obj3.save()
                    outsource_product = Eps_Outsource_items(infill_product=item_obj3, received_quantity=0)
                    outsource_product.save()
                else:
                    # messages.error(request, "Please Enter Quantity.")
                    print("Please Enter Spandrel Panel Quantity.")
            else:
                print("Error in sub formset Spandrel Panel ==>", item3.errors)
                messages.error(request, item3.errors)
                
                
        for item4 in openable_panel:
            if item4.is_valid():
                item_obj4 = item4.save(commit=False)
                if item_obj4.infill_quantity and item_obj4.infill_area:
                    item_obj4.main_product = eps_item
                    item_obj4.panel_type = 3
                    item_obj4.save()
                    outsource_product = Eps_Outsource_items(infill_product=item_obj4, received_quantity=0)
                    outsource_product.save()
                else:
                    # messages.error(request, "Please Enter Quantity.")
                    print("Please Enter Openable Panel Quantity.")
            else:
                print("Error in sub formset Openable Panel ==>", item4.errors)
                messages.error(request, item4.errors)
                
                
        return redirect('eps_production_view', eps=eps_item.eps_data.id)
    
    context = {
        "eps_item": eps_item,
        "product_obj": product_obj,
        "pro_sec_infill_details": pro_sec_infill_details,
        "pro_infill_details": pro_infill_details,
        "products_details": products_details,
        "infill_details": infill_details,
        "infill_detail_formset": infill_detail_formset,
        "shopfloors": shopfloors,
        "spandrel_detail_formset": spandrel_detail_formset,
        "openable_panel": openable_panel,
        
        "shopfloor_eps_data": shopfloor_eps_data,
        "shopfloor_attachments": shopfloor_attachments,
        "add_infill_btn": add_infill_btn,
        
    }
    return render(request, "Projects/Eps/eps_view/production_product_details.html", context)


def infill_outsource_btn(request, pk):
    """
    This function toggles the "is_outsourced" field of an Eps_infill_Details object and creates or
    deletes an associated Eps_Outsource_items object accordingly.
    
    """
    infill_data = Eps_infill_Details.objects.get(pk=pk)
    if infill_data.is_outsourced:
        infill_data.is_outsourced = False
        flag = 0
        try:
            outsource_data = Eps_Outsource_items.objects.get(infill_product=infill_data).delete()
        except Exception as e:
            print('Exception in outsource Delete==>', e)
            messages.error(request, "This Infill is Under Outsourcing  Process.")
    else:
        infill_data.is_outsourced = True
        outsource_product = Eps_Outsource_items(infill_product=infill_data, received_quantity=0, remaining_quantity=infill_data.infill_quantity)
        outsource_product.save()
        flag = 1
    infill_data.save()
    return JsonResponse({'success': True, 'flag': flag})


def update_infill_details(request, pk):
    """
    This function updates EPS infill details using a formset and redirects to the EPS production view
    page.
    
    """
    infill_data = Eps_infill_Details.objects.get(pk=pk)
    eps_infill_form = eps_infill_details(infill_data.main_product.eps_product.product)
    EPSINFILLDETAILS = modelformset_factory(Eps_infill_Details, form=eps_infill_form, extra=0)
    infill_detail_formset = EPSINFILLDETAILS(queryset=Eps_infill_Details.objects.filter(pk=pk), prefix='eps_infill')
    
    if request.method == "POST":
        infill_detail_formset = EPSINFILLDETAILS(request.POST, prefix='eps_infill')
        for item2 in infill_detail_formset:
            if item2.is_valid():
                item_obj2 = item2.save(commit=False)
                if item_obj2.infill_quantity and item_obj2.infill_area:
                    item_obj2.save()
                else:
                    print("Please Enter Infill Quantity.")
            else:
                print("Error in sub formset infill ==>", item2.errors)
                messages.error(request, item2.errors)
        
        return redirect('eps_production_view', pk=infill_data.main_product.id)
    context = {
        "infill_data": infill_data,
        "infill_detail_formset": infill_detail_formset,
    }
    return render(request, "Projects/Eps/eps_view/infill_data_update.html", context)


@login_required(login_url='signin')
def infill_delete(request, pk):
    """
    This function deletes a specific infill data and redirects to the EPS production view page while
    displaying success or error messages.
    
    """
    url = f"/Project/infill_delete/{str(pk)}/"
    if request.method == "POST":
        try:
            infill_data = Eps_infill_Details.objects.get(pk=pk)
            infill_data.delete()
            messages.success(request, "Infill Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")

        return redirect('eps_production_view', pk=infill_data.main_product.id)

    context = {
        "url": url,
    }
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
def eps_outsource_view(request, eps, product=None):
    """
    This function renders a view for an EPS object with information about its products and outsourced
    items.
    
    """
    if product:
        product = Eps_Products.objects.get(pk=product)
        eps_obj = Eps_main.objects.get(pk=product.eps_data.id)
    else:
        eps_obj = Eps_main.objects.get(pk=eps)
        # if eps_obj.eps_type == 1:
        product = Eps_Products.objects.filter(eps_data=eps_obj).first()
        # else:
            # product = InfillSchedule.objects.filter(eps=eps_obj).last().product
        
    products_obj = Eps_Products.objects.filter(eps_data=eps_obj)
    product_data = SalesOrderItems.objects.get(pk=product.eps_product.product.id)
    eps_products_details = Eps_Product_Details.objects.filter(main_product=product)   
    
    outsourced_product_objs = Eps_Outsource_items.objects.filter(
                Q(infill_product__main_product__eps_data=eps) & 
                ~Q(remaining_quantity=0)
            ).order_by('id')
    
    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(product=product)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None
        
    try:
        schedule_infill_obj = InfillSchedule.objects.get(eps=eps_obj, product=product)
    except Exception:
        schedule_infill_obj = None
        
    
    eps_vision_panel_details = Eps_infill_Details.objects.filter(
        main_product=product,
        panel_type=1
        ).distinct('infill__panel_specification__specifications')
    eps_spandrel_panel_details = Eps_infill_Details.objects.filter(
        main_product=product,
        panel_type=2
        ).distinct('infill__panel_specification__specifications')
    eps_openable_panel_details = Eps_infill_Details.objects.filter(
        main_product=product,
        panel_type=3
        ).distinct('infill__panel_specification__specifications')
    
        
    outsource_items = Eps_Outsource_items.objects.filter(
        infill_product__main_product__eps_data=eps_obj,
        infill_product__is_outsourced=True).distinct('infill_product__infill__panel_specification__specifications')
    
    outsource_items_not_send = Eps_Outsource_items.objects.filter(
        infill_product__main_product__eps_data=eps_obj,
        infill_product__is_outsourced=True,
        out_source_batch__isnull=True,
        ).distinct('infill_product__infill__panel_specification__specifications')
    
    
    context = {
        'title': f'{PROJECT_NAME} | View EPS',
        'products_obj': products_obj,
        'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,        
        'outsource_items': outsource_items,
        'outsource_items_not_send': outsource_items_not_send,
        "shopfloor_eps_data": shopfloor_eps_data,
        "shopfloor_attachments": shopfloor_attachments,
        "eps_products_details": eps_products_details,
        "eps_vision_panel_details": eps_vision_panel_details,
        "eps_spandrel_panel_details": eps_spandrel_panel_details,
        "eps_openable_panel_details": eps_openable_panel_details,
        "schedule_infill_obj": schedule_infill_obj,
        "outsourced_product_objs": outsourced_product_objs,
    }
    
    return render(request,"Projects/Eps/eps_view/outsource_view.html", context)
    

def set_batch_number(pk):
    project_obj = ProjectsModel.objects.get(pk=pk)
    outsource_objs = Eps_Outsourced_Data.objects.filter(eps__project=pk)
    if outsource_objs:
        outsource_objs.count()
        batch_number = f'{project_obj.project_id}-B-{outsource_objs.count()}'
    else:
        batch_number = f'{project_obj.project_id}-B-1'
        
    return batch_number


def set_os_number():
    outsource_objs = Eps_Outsourced_Data.objects.all()
    return f'OS-{outsource_objs.count()}'


@login_required(login_url='signin')
def outsource_product(request, infill, eps_product):
    """
    This function handles the submission of an outsource request for EPS products.
    
    """
    eps_product_obj = Eps_Products.objects.get(pk=eps_product)
    infill_objs = Eps_infill_Details.objects.filter(
        infill__panel_specification=infill,
        main_product=eps_product_obj,
        eps_ref=eps_product_obj.eps_data,
        is_outsourced=True,
        status__in=[1, 2],
    )
    
    
        
            
    forms = OutSourceSubmitForm()
    if request.method == "POST":
        forms = OutSourceSubmitForm(request.POST)
        infill_list = request.POST.getlist('infill_product')
        outsource_qty = request.POST.getlist('outsource_qty')
        
        if forms.is_valid():
            
            form_obj = forms.save(commit=False)
            form_obj.eps_id = eps_product_obj.eps_data.id
            form_obj.outsource_date = time()
            form_obj.save()
            
            
            for i, infill in enumerate(infill_list):
                index = infill.split('-')[0]
                product = infill.split('-')[1]
               
                infill_product_obj = infill_objs.get(pk=product)
                outsource_item = Eps_Outsource_items(
                        infill_product=infill_product_obj,
                        received_quantity=0,
                        actual_quantity=outsource_qty[int(index)],
                        remaining_quantity=outsource_qty[int(index)],
                        out_source_batch=form_obj,
                        outsource_area=float(infill_product_obj.infill_area)*float(outsource_qty[int(index)]),
                    )
                    
                outsource_item.save()
                qty_datas = outsource_item_details(product)
                if qty_datas['outsource_qty'] == infill_product_obj.infill_quantity:
                    infill_product_obj.status = 3
                else:
                    infill_product_obj.status = 2
                    
                infill_product_obj.save()
                
                form_obj.products.add(outsource_item.id)
            
            form_obj.batch_number = set_batch_number(eps_product_obj.eps_data.project.id)
            form_obj.outsource_number = set_os_number()
            form_obj.save()
            
            eps_infill_objs = Eps_infill_Details.objects.filter(
                                    infill__panel_specification=product,
                                    main_product=eps_product_obj,
                                    eps_ref=eps_product_obj.eps_data,
                                )
            
            completed_outsourced_items = Eps_Outsourced_Data.objects.filter(
                                            products__infill_product__main_product=eps_product_obj
                                        ).distinct('products__infill_product')
        
            eps_infill_count = eps_infill_objs.count()
            completed_outsourced_count = completed_outsourced_items.count()

            eps_product_obj.infill_status = 2 if eps_infill_count == completed_outsourced_count else 3
            eps_product_obj.save()
            messages.success(request, f"Successfully Outsourced the Infill's")
            
        else:
            messages.error(request, forms.errors)
        
        return redirect('eps_outsource_view', eps=eps_product_obj.eps_data.id)        
            
    context = {
        'eps_product': eps_product_obj,
        'eps': eps_product_obj.eps_data,
        'infill_objs': infill_objs,
        'forms': forms,
        'infill': infill,
    }
    return render(request, "Projects/Eps/eps_view/submit_outsource.html", context)
    
    
@login_required(login_url='signin')
def os_recive(request, items, eps):
    """
    This function receives data from a form, filters products based on certain criteria, and distributes
    the received quantity among the filtered products.
    """
    products_obj = Eps_Outsource_items.objects.filter(
                Q(infill_product__infill__panel_specification=items) &
                Q(infill_product__main_product__eps_data=eps) & 
                ~Q(remaining_quantity=0)
            ).order_by('id')
    form = ReceiveOutsourceProduct()
    if request.method == "POST":
        form = ReceiveOutsourceProduct(request.POST)
        receive_quantity = request.POST.getlist('receive_quantity')
        receive_product = request.POST.getlist('receive_product')
        
        if form.is_valid():
            for product_list in receive_product:
                index = product_list.split('-')[0]
                product_id = product_list.split('-')[1]
                qty = receive_quantity[int(index)]
                
                form_obj = form.save(commit=False)
                product = Eps_Outsource_items.objects.get(pk=product_id)
                
                quantity = float(qty)
                out_data = distribute_quantity(request, product, quantity)
                form_obj.save()
                
                if out_data:
                    recvd_product_obj = Outsource_receive_items(
                        receive_quantity=float(qty),
                        item=out_data,
                        received_batch=form_obj,
                        received_area=float(product.infill_product.infill_area)*float(qty),
                    )
                    recvd_product_obj.save()
                    form_obj.received_items.add(out_data.id)
                    form_obj.save()
                    
                messages.success(request, "Successfully recorded the received items")
                # else:
                #     messages.error(request, "Check the Quantity Entered")
                
        else:
            messages.error(request, form.errors)
        return redirect('eps_outsource_view', eps=eps)
                    
    context = {
        'eps': eps,
        'forms': form,
        'items': int(items),
        'products': products_obj,
    }           
    return render(request, "Projects/Eps/eps_view/update_received_data.html", context)       


@login_required(login_url='signin')
def distribute_quantity(request, product, quantity):
    """
        This function distributes a given quantity of products among available products and updates their
        status and remaining quantity accordingly.
    """
    if quantity < 1:
        return False
    else:
        
        if not product.remaining_quantity == '0.00':
            if product.remaining_quantity >= quantity:
                product.received_quantity = float(product.received_quantity) + float(quantity)
                product.status = 3
                eps_product = Eps_Products.objects.get(pk=product.infill_product.main_product.id)
                eps_product.infill_status = 3
                eps_product.save()
                product.remaining_quantity = float(product.remaining_quantity) - float(quantity)
                
                if product.remaining_quantity == 0:
                    # product.status = 4
                    eps_product.infill_status = 4
                    qaqc_infill_product = QAQC_infill_Products(
                                                product=product, 
                                                received_quantity=float(product.received_quantity), 
                                                remaining_quantity=float(product.received_quantity)
                                            )
                    qaqc_infill_product.save()
                    eps_product.save()
                product.save()
                # remaining_data = outsource_item_remaning(product.infill_product.id)
                qty_data = outsource_item_details(product.infill_product.id)
                infill_product = Eps_infill_Details.objects.get(pk=product.infill_product.id)
                
                if qty_data['recvd_qty'] == infill_product.infill_quantity:
                    infill_product.recv_status = 3
                    eps_product.qaqc_status = 1
                    if not Eps_QAQC.objects.filter(panel_product=eps_product):
                            qaqc_data = Eps_QAQC(
                                created_by=request.user, panel_product=eps_product)
                            qaqc_data.save()
                    eps_product.save()
                else:
                    infill_product.recv_status = 2
                    
                infill_product.save()
                    
                return product
            else:
                distribute_quantity(request, product, quantity/2)
        else:
            return False


@login_required(login_url='signin')
def received_info(request, items):
    """
    This function receives information and items as input, converts the items to a Python object,
    filters the Outsource_receive_recode objects based on the items, and returns a rendered HTML
    template with the filtered data and items as context.
    
    """
    items = ast.literal_eval(items)
    info_data = Outsource_receive_recode.objects.filter(item__in=items)
    context = {
        "info_data": info_data,
        "items": items,
    }
    return render(request, "Projects/Eps/eps_view/received_outsource_info.html", context)


@login_required(login_url='signin')
def eps_shopfloor_view(request, pk):
    """
    This function displays the details of a specific EPS product on the shop floor view page.
    
    """
   
    product = Eps_Products.objects.get(pk=pk)
    eps_obj = Eps_main.objects.get(pk=product.eps_data.id)
    shopfloor = Eps_ShopFloors.objects.filter(shopfloor=Eps_ShopFloors.objects.filter(product=product).first().shopfloor)
    temp = Eps_ShopFloor_main_products.objects.filter(main_products__main_product__in=[item.product for item in shopfloor])
    products_obj = Eps_Products.objects.filter(pk__in=[product.main_products.main_product.id for product in temp])

    product_data = SalesOrderItems.objects.get(pk=product.eps_product.product.id)
    # product_data = EstimationMainProduct.objects.get(pk=product.eps_product.product.id)
    # product_aluminium = MainProductAluminium.objects.get(estimation_product=product_data)

    eps_products_details = Eps_Product_Details.objects.filter(main_product=product)
    eps_infill_details = Eps_infill_Details.objects.filter(
        main_product=product, is_outsourced=True
        ).distinct('infill__panel_specification__specifications')

    attachments = Fabrication_Attachments.objects.filter(
        eps_product=product)
    try:
        scedule_details = Schedule_Product.objects.get(product__main_products__main_product=product)
    except Schedule_Product.DoesNotExist:
        scedule_details = None

    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(product=product)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None
    try:
        # infill_details = MainProductGlass.objects.get(estimation_product=product_data, glass_primary=True)
        # sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_data, glass_primary=False)
        infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
        sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
    except Exception:
        infill_details = None
        sec_infill_details = None
    
    context = {
        'title': f'{PROJECT_NAME} | View EPS',
        'products_obj': products_obj,
        'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,
        'infill_details': infill_details,
        'sec_infill_details': sec_infill_details,
        'eps_products_details': eps_products_details,
        'eps_infill_details': eps_infill_details,
        'attachments': attachments,
        'shopfloor_eps_data': shopfloor_eps_data,
        'shopfloor_attachments': shopfloor_attachments,
        'scedule_details': scedule_details
    }
    return render(request,"Projects/Eps/eps_view/shopfloor_view.html", context)


@login_required(login_url='signin')
def shopfloor_product_details(request, pk):
    """
    This function retrieves and displays details of a product for the shop floor in an EPS project.
    
    """
    eps_item = Eps_Products.objects.get(pk=pk)
    
    product_obj = SalesOrderItems.objects.get(pk=eps_item.eps_product.product.id)
    # product_obj = EstimationMainProduct.objects.get(pk=eps_item.eps_product.product.id)
    products_details = Eps_ShopFloor_main_products.objects.filter(main_products__main_product=eps_item)
    infill_details = Eps_Outsource_items.objects.filter(infill_product__main_product=eps_item).distinct('infill_product')
    # product_details = MainProductAluminium.objects.get(estimation_product=product_obj)
    products_obj = Eps_ShopFloor_main_products.objects.filter(main_products__main_product=eps_item)
    
    try:
        scedule_details = Schedule_Product.objects.get(product__main_products__main_product=eps_item)
    except Schedule_Product.DoesNotExist:
        scedule_details = None
    
    try:
        pro_infill_details = SalesOrderInfill.objects.get(product=product_obj, infill_primary=True)
        pro_sec_infill_details = SalesOrderInfill.objects.filter(product=product_obj, infill_primary=False)
        # pro_infill_details = MainProductGlass.objects.get(estimation_product=product_obj, glass_primary=True)
        # pro_sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_obj, glass_primary=False)
    except Exception as e:
        pro_infill_details = None
        pro_sec_infill_details = None
        
    try:
        attachments = Fabrication_Attachments.objects.filter(eps_product=eps_item).last()
    except Exception:
        attachments = None
    associated_products = Eps_Associated_Products.objects.filter(eps_product=eps_item, eps_product__eps_product__product=product_obj)
    
    associated_products = Eps_Associated_sub_Products.objects.filter(main_product__main_product=eps_item)
    context = {
        "eps_item": eps_item,
        "product_obj": product_obj,
        "products_obj": products_obj,
        # "product_details": product_details,
        "products_details": products_details,
        "infill_details": infill_details,
        "pro_infill_details": pro_infill_details,
        "pro_sec_infill_details": pro_sec_infill_details,
        "attachments": attachments,
        "associated_products": associated_products,
        "scedule_details": scedule_details,
    }
    return render(request, "Projects/Eps/eps_view/shopfloor_product_details.html", context)


@login_required(login_url='signin')
def schedule_product(request, pk):
    """
    This function schedules a product for production and updates the associated workstations and
    products.
    
    """
    eps_item = Eps_Products.objects.get(pk=pk)
    associated_products = Eps_ShopFloor_main_products.objects.filter(main_products__main_product=eps_item)
    form = ScheduleProductForm()
    if request.method == 'POST':
        form = ScheduleProductForm(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.product = associated_products.first()
            form_obj.eps = associated_products.first().main_products.main_product.eps_data
            form_obj.save()
            
            for product in associated_products:
                if product.main_products.main_product.eps_product.product.product:
                    init_workstation = Product_WorkStations.objects.filter(
                                            product=product.main_products.main_product.eps_product.product.product.id
                                        ).first()
                else:
                    init_workstation = Product_WorkStations.objects.filter(
                                            product=product.main_products.main_product.eps_product.product.panel_product.id
                                        ).first()
                    
                add_to_workstation = Workstation_Data(
                                            created_by=request.user, 
                                            product=product, 
                                            received_quantity=product.product_quantity, 
                                            remaining_quantity=product.product_quantity, 
                                            workstation=init_workstation.workstation,
                                            eps_product_id=eps_item
                                        )
                add_to_workstation.save()
                
                for associated_product in Eps_Associated_sub_Products.objects.filter(main_product=product.main_products):
                    workstation_associated_product = Workstation_Associated_Products_Data(
                                                                    created_by=request.user, 
                                                                    product=associated_product,
                                                                    received_quantity=associated_product.received_quantity, 
                                                                    remaining_quantity=associated_product.remaining_quantity,
                                                                    workstation=init_workstation.workstation,
                                                                    eps_product_id=eps_item
                                                                )
                    workstation_associated_product.save()
                
            eps_item.shopfloor_status = 2
            eps_item.save()
            messages.success(request, "Successfully scheduled product.")
        else:
            messages.error(request, form.errors)
        return redirect('eps_shopfloor_view', pk=eps_item.id)
        
            
    context = {
        'form': form,
        'product': eps_item,
        'associated_products': associated_products,
        
    }
    return render(request, 'Projects/Eps/eps_view/schedule_product.html', context)
        
        
@login_required(login_url='signin')
def schedule_product_edit(request, pk, re_path=None):
    """
    This function updates a schedule product form and redirects to the EPS shop floor view.
    
    """
    main_product = Schedule_Product.objects.get(pk=pk)
    form = ScheduleProductForm(instance=main_product)
    if request.method == "POST":
        form = ScheduleProductForm(request.POST, instance=main_product)
        if form.is_valid():
            form_obj = form.save(commit=False)
            if form_obj.shopfloor_status == 2:
                form_obj.shopfloor_status = 1
            form_obj.save()
            messages.success(request, "Successfully Updated Product Schedule")
        else:
            messages.error(request, form.errors)
        if re_path == 'shopfloor_list':
            return redirect('general_shopfloor_view', status=1)
        else:
            return redirect('eps_shopfloor_view', pk=main_product.product.main_products.main_product.id)
            
    context = {
        'form': form,
        'product': main_product,
        're_path': re_path,
    }
    return render(request, 'Projects/Eps/eps_view/schedule_product.html', context)
    
         
@login_required(login_url='signin')
def workstaions_view(request, pk):
    """
        This function retrieves and displays various details related to a specific EPS product for viewing
        in a web page.
    """
    product = Eps_Products.objects.get(pk=pk)
    eps_obj = Eps_main.objects.get(pk=product.eps_data.id)
    
    try:
        shopfloors = Eps_ShopFloors.objects.get(product=product)
    except Exception as e:
        shopfloors = None
    
    if shopfloors:
        shopfloor = Eps_ShopFloors.objects.filter(shopfloor=shopfloors.shopfloor)
    else:
        shopfloor = None
    
    
    if shopfloor:
        shopfloor_products = [item.product for item in shopfloor]
        scheduled_products1 = Schedule_Product.objects.filter(product__main_products__main_product__in=shopfloor_products)
        products_obj = Eps_Products.objects.filter(pk__in=[product.product.main_products.main_product.id for product in scheduled_products1])
    else:
        temp = None
        products_obj = None
    
    product_data = SalesOrderItems.objects.get(pk=product.eps_product.product.id)
    # product_data = EstimationMainProduct.objects.get(pk=product.eps_product.product.id)
    # product_aluminium = MainProductAluminium.objects.get(estimation_product=product_data)
    
    eps_products_details = Eps_Product_Details.objects.filter(main_product=product)   
    
    scheduled_products = Schedule_Product.objects.filter(
        Q(product__main_products__main_product__eps_data=eps_obj.id) 
    )
    
    eps_infill_details = Eps_infill_Details.objects.filter(
        main_product=product, is_outsourced=True
        ).distinct('infill__panel_specification__specifications')
    
    attachments = Fabrication_Attachments.objects.filter(
        eps_product=product)
    try:
        scedule_details = Schedule_Product.objects.get(product__main_products__main_product=product)
    except Schedule_Product.DoesNotExist:
        scedule_details = None
    
    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(product=product)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None
    try:
        # infill_details = MainProductGlass.objects.get(estimation_product=product_data, glass_primary=True)
        # sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_data, glass_primary=False)
        infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
        sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
    except Exception:
        infill_details = None
        sec_infill_details = None

    context = {
        'title': f'{PROJECT_NAME} | View Workstation EPS ',
        'products_obj': products_obj,
        'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,
        'infill_details': infill_details,
        'sec_infill_details': sec_infill_details,
        'eps_products_details': eps_products_details,
        'eps_infill_details': eps_infill_details,
        'attachments': attachments,
        'shopfloor_eps_data': shopfloor_eps_data,
        'shopfloor_attachments': shopfloor_attachments,
        'scedule_details': scedule_details,
        'scheduled_products': scheduled_products,
    }
    return render(request,"Projects/Eps/eps_view/workstations_view.html", context)


@login_required(login_url='signin')
def workstation_side_data(request, pk):
    """
    This function retrieves data related to a scheduled product and its associated EPS and shopfloor,
    and renders it in a template.
    """
    scheduled_product = Schedule_Product.objects.get(pk=pk)
    shopfloor = Eps_ShopFloors.objects.filter(eps=scheduled_product.eps).last()
    
    context = {
        "scheduled_product": scheduled_product,
        "eps_obj": scheduled_product.product.main_products.main_product.eps_data,
        "shopfloor": shopfloor
    }
    
    return render(request,'Projects/Eps/eps_view/workstation_side_data.html', context)
    

@login_required(login_url='signin')
def workstation_side_data_cmpltd(request, pk):
    """
    This function retrieves data related to a scheduled product and its associated EPS and shopfloor,
    and renders it in a template for display.
    
    """
    scheduled_product = Schedule_Product.objects.get(pk=pk)
    shopfloor = Eps_ShopFloors.objects.filter(eps=scheduled_product.eps).last()
    
    context = {
        "scheduled_product": scheduled_product,
        "eps_obj": scheduled_product.product.main_products.main_product.eps_data,
        "shopfloor": shopfloor
    }
    
    return render(request,'Projects/Eps/eps_view/workstation_side_data.html', context)


@login_required(login_url='signin')
def workstation_product_details(request, pk):
    """
    This function retrieves details of a scheduled product and its associated EPS data and renders it in
    a template for viewing.
    
    """
    scheduled_product = Schedule_Product.objects.get(pk=pk)
    context = {
        "scheduled_product": scheduled_product,
        "eps_obj": scheduled_product.product.main_products.main_product.eps_data,
    }
    return render(request, "Projects/Eps/eps_view/workstation_details.html", context)
    

@login_required(login_url='signin')
def workstation_product_update(request, pk, associated=None, type=None):
    """
    This function updates the quantity of a product in a workstation and creates a new entry in the next
    workstation if necessary.
    
    """
    if not associated:
        data = Workstation_Data.objects.get(pk=pk)
        workstation_datas = workstation_data(
            pk=data.product.main_products.main_product.eps_product.product.product.id,
            current_workstation=data.workstation.id
        )
    else:
        data = Workstation_Associated_Products_Data.objects.get(pk=pk)
        workstation_datas = workstation_data(
            pk=data.product.main_product.main_product.eps_product.product.product.id,
            current_workstation=data.workstation.id
        )
    
    if not associated:
        product = Schedule_Product.objects.get(
            product__main_products__main_product=data.product.main_products.main_product)
    else:
        product = Schedule_Product.objects.get(
            product__main_products__main_product=data.product.main_product.main_product)

    if request.method == "POST":
        new_quantity = request.POST.get('new_quantity')
        if new_quantity != '':
            if float(new_quantity) <= data.remaining_quantity:
                if not associated:
                    history_data = Workstation_History(
                        created_by=request.user, workstation_data=data, received_quantity=float(new_quantity))
                    history_data.save()
                else:
                    history_data = Workstation_Associated_Product_History(
                        created_by=request.user, workstation_data=data, received_quantity=float(new_quantity))
                    history_data.save()

                data.completed_quantity = float(
                    data.completed_quantity) + float(new_quantity)
                data.remaining_quantity = float(
                    data.remaining_quantity) - float(new_quantity)
                data.save()

                if workstation_datas['next_workstation']:
                    if not associated:
                        try:
                            flag = Workstation_Data.objects.get(eps_product_id=data.eps_product_id, workstation=workstation_datas['next_workstation'])
                        except:
                            flag = None
                    else:
                        try:
                            flag = Workstation_Associated_Products_Data.objects.get(eps_product_id=data.eps_product_id, workstation=workstation_datas['next_workstation'])
                        except:
                            flag = None
                    if not flag:
                        new_data = data
                        new_data.pk = None
                        new_data.received_quantity = new_data.completed_quantity
                        new_data.remaining_quantity = new_data.completed_quantity
                        new_data.completed_quantity = 0
                        new_data.workstation_id = workstation_datas['next_workstation']
                        new_data.save()
                    else:
                        flag.received_quantity = float(flag.received_quantity) + float(new_quantity)
                        flag.remaining_quantity = float(flag.remaining_quantity) + float(new_quantity)
                        flag.save()
                else:
                    if workstation_datas['final_workstation'] == data.workstation.id:
                        if not associated:
                            try:
                                flag2 = Workstation_Data.objects.get(eps_product_id=data.eps_product_id, is_completed=True, workstation=workstation_datas['final_workstation'])
                            except:
                                flag2 = None
                        else:
                            try:
                                flag2 = Workstation_Associated_Products_Data.objects.get(eps_product_id=data.eps_product_id, is_completed=True, workstation=workstation_datas['final_workstation'])
                            except:
                                flag2 = None
                        if not flag2:
                            new_data2 = data
                            new_data2.pk = None
                            new_data2.is_completed = True
                            
                            new_data2.received_quantity = data.completed_quantity
                            new_data2.remaining_quantity = data.completed_quantity
                            new_data2.qaqc_received_quantity = new_data2.completed_quantity
                            new_data2.qaqc_remaining_quantity = new_data2.completed_quantity
                            new_data2.save()
                        else:
                            flag2.received_quantity = float(flag2.received_quantity) + float(new_quantity)
                            flag2.remaining_quantity = float(flag2.remaining_quantity) - float(new_quantity)
                            flag2.completed_quantity = float(flag2.completed_quantity) + float(new_quantity)
                            flag2.save()

                        if not Eps_QAQC.objects.filter(product=product):
                            qaqc_data = Eps_QAQC(
                                created_by=request.user, product=product)
                            qaqc_data.save()

                    else:
                        print('Error in Completing ')
                messages.success(request, "Successfully Updated Quantity")
            else:
                messages.error(request, "Please check the entered quantity.")
        else:
            messages.error(request, "Please check the entered quantity.")
        if not type:
            return redirect('workstaions_view', eps=data.eps_product_id.eps_data.id)
        else:
            return redirect('workstation_product_detail_view', pk=product.id)
    context = {
        "data": data,
        "associated": associated,
        "type": type,
    }
    return render(request, "Projects/Eps/eps_view/update_workstation_quantity.html", context)


@login_required(login_url='signin')
def workstations_side_update(request):
    """
    This function updates the quantity and completion time of a workstation and its associated products
    based on user input.
    
    """
    if request.method == 'POST':
        new_quantity = request.POST.getlist('new_quantity')
        for item in new_quantity:
            split_item = item.split('-')
            pk = int(split_item[0])
            if split_item[3] == '1':
                associated = True
            else:
                associated = None
            time = split_item[2]
            quantity = float(split_item[1])
            
            if not quantity == 0:
                if not associated:
                    data = Workstation_Data.objects.get(pk=pk)
                    if data.product.main_products.main_product.eps_product.product.product:
                        product_id = data.product.main_products.main_product.eps_product.product.product.id
                    else:
                        product_id = data.product.main_products.main_product.eps_product.product.panel_product.id
                    workstation_datas = workstation_data(
                        pk=product_id,
                        current_workstation=data.workstation.id
                    )
                else:
                    data = Workstation_Associated_Products_Data.objects.get(pk=pk)
                    if data.product.main_product.main_product.eps_product.product.product:
                        product_id = data.product.main_product.main_product.eps_product.product.product.id
                    else:
                        product_id = data.product.main_product.main_product.eps_product.product.panel_product.id
                    workstation_datas = workstation_data(
                        pk=product_id,
                        current_workstation=data.workstation.id
                    )
                
                if not associated:
                    product = Schedule_Product.objects.get(
                        product__main_products__main_product=data.product.main_products.main_product)
                else:
                    product = Schedule_Product.objects.get(
                        product__main_products__main_product=data.product.main_product.main_product)
                
                if float(quantity) <= data.remaining_quantity:
                    if not associated:
                        history_data = Workstation_History(
                            created_by=request.user, workstation_data=data, received_quantity=float(quantity), completion_time=time)
                        history_data.save()
                    else:
                        history_data = Workstation_Associated_Product_History(
                            created_by=request.user, workstation_data=data, received_quantity=float(quantity), completion_time=time)
                        history_data.save()

                    data.completed_quantity = float(
                        data.completed_quantity) + float(quantity)
                    data.total_completion_time = sum_times([data.total_completion_time, time], types='workstation')
                    data.remaining_quantity = float(
                        data.remaining_quantity) - float(quantity)
                    data.save()

                    if workstation_datas['next_workstation']:
                        if not associated:
                            try:
                                flag = Workstation_Data.objects.get(eps_product_id=data.eps_product_id, prev_product=data.id, workstation=workstation_datas['next_workstation'])
                            except:
                                flag = None
                        else:
                            try:
                                flag = Workstation_Associated_Products_Data.objects.get(eps_product_id=data.eps_product_id, prev_product=data.id, workstation=workstation_datas['next_workstation'])
                            except:
                                flag = None
                        
                        if not flag:
                            if not associated:
                                new_data = Workstation_Data(
                                                created_by=data.created_by, 
                                                product=data.product, 
                                                received_quantity=data.completed_quantity, 
                                                remaining_quantity=data.completed_quantity, 
                                                completed_quantity=0, 
                                                workstation_id=workstation_datas['next_workstation'], 
                                                prev_product=data,
                                                eps_product_id=data.eps_product_id,
                                                total_completion_time='00:00',
                                            )
                                new_data.save()
                            else:
                                new_data = Workstation_Associated_Products_Data(
                                                created_by=data.created_by, 
                                                product=data.product, 
                                                received_quantity=data.completed_quantity, 
                                                remaining_quantity=data.completed_quantity, 
                                                completed_quantity=0, 
                                                workstation_id=workstation_datas['next_workstation'], 
                                                prev_product=data,
                                                eps_product_id=data.eps_product_id,
                                                total_completion_time='00:00',
                                            )
                                new_data.save()
                            
                        else:
                            flag.received_quantity = float(flag.received_quantity) + float(quantity)
                            flag.total_completion_time = sum_times([flag.total_completion_time, time], types='workstation')
                            flag.remaining_quantity = float(flag.remaining_quantity) + float(quantity)
                            flag.save()
                    else:
                        if workstation_datas['final_workstation'] == data.workstation.id:
                            if not associated:
                                try:
                                    flag2 = Workstation_Data.objects.get(eps_product_id=data.eps_product_id, is_completed=True, prev_product=data.id, workstation=workstation_datas['final_workstation'])
                                except:
                                    flag2 = None
                            else:
                                try:
                                    flag2 = Workstation_Associated_Products_Data.objects.get(eps_product_id=data.eps_product_id, is_completed=True, prev_product=data.id, workstation=workstation_datas['final_workstation'])
                                except:
                                    flag2 = None
                                    
                            if not flag2:
                                if not associated:
                                    new_data2  = Workstation_Data(
                                                created_by=data.created_by, 
                                                product=data.product, 
                                                received_quantity=data.completed_quantity, 
                                                remaining_quantity=data.completed_quantity, 
                                                completed_quantity=data.completed_quantity, 
                                                qaqc_received_quantity=data.completed_quantity,
                                                qaqc_remaining_quantity=data.completed_quantity,
                                                is_completed=True, 
                                                prev_product=data,
                                                eps_product_id=data.eps_product_id,
                                                workstation=data.workstation,
                                                total_completion_time=data.total_completion_time,
                                            )
                                    new_data2.save()
                                else:
                                    new_data2  = Workstation_Associated_Products_Data(
                                                created_by=data.created_by, 
                                                product=data.product, 
                                                received_quantity=data.completed_quantity, 
                                                remaining_quantity=data.completed_quantity, 
                                                completed_quantity=data.completed_quantity, 
                                                qaqc_received_quantity=data.completed_quantity,
                                                qaqc_remaining_quantity=data.completed_quantity,
                                                is_completed=True, 
                                                prev_product=data,
                                                eps_product_id=data.eps_product_id,
                                                workstation=data.workstation,
                                                total_completion_time=data.total_completion_time,
                                            )
                                    new_data2.save()
                            
                            else:
                                flag2.received_quantity = float(flag2.received_quantity) + float(quantity)
                                flag2.remaining_quantity = float(flag2.remaining_quantity) - float(quantity)
                                flag2.completed_quantity = float(flag2.completed_quantity) + float(quantity)
                                flag2.completed_quantity = sum_times([flag2.remaining_quantity, time], types='workstation')
                                flag2.save()

                            if not Eps_QAQC.objects.filter(product=product):
                                qaqc_data = Eps_QAQC(
                                    created_by=request.user, product=product)
                                qaqc_data.save()

                            main_product = Eps_Products.objects.get(pk=data.eps_product_id.id)
                            main_product.qaqc_status = 1
                            main_product.save()
                        else:
                            print('Error in Completing ')
                    messages.success(request, "Successfully Updated Quantity")
                else:
                    messages.error(request, "Please check the entered quantity.")
                    
    return redirect('general_workstation_view')


@login_required(login_url='signin')
def workstations_single_view_update(request, pk):
    """
    This function updates the quantity of a product in a workstation and handles the logic for moving
    the product to the next workstation or completing the process.
    
    """
    main_product = Eps_Products.objects.get(pk=pk)
    if request.method == 'POST':
        new_quantity = request.POST.getlist('new_quantity')
        for item in new_quantity:
            split_item = item.split('-')
            pk2 = int(split_item[0])
            if split_item[3] == '1':
                associated = True
            else:
                associated = None
            time = split_item[2]
            quantity = float(split_item[1])
            
            if not quantity == 0:
                if not associated:
                    data = Workstation_Data.objects.get(pk=pk2)
                    if data.product.main_products.main_product.eps_product.product.product:
                        product_id = data.product.main_products.main_product.eps_product.product.product.id
                    else:
                        product_id = data.product.main_products.main_product.eps_product.product.panel_product.id
                    workstation_datas = workstation_data(
                        pk=product_id,
                        current_workstation=data.workstation.id
                    )
                else:
                    data = Workstation_Associated_Products_Data.objects.get(pk=pk2)
                    if data.product.main_product.main_product.eps_product.product.product:
                        product_id = data.product.main_product.main_product.eps_product.product.product.id
                    else:
                        product_id = data.product.main_product.main_product.eps_product.product.panel_product.id
                    workstation_datas = workstation_data(
                        pk=product_id,
                        current_workstation=data.workstation.id
                    )
                
                if not associated:
                    product = Schedule_Product.objects.get(
                        product__main_products__main_product=data.product.main_products.main_product)
                else:
                    product = Schedule_Product.objects.get(
                        product__main_products__main_product=data.product.main_product.main_product)
                
                if float(quantity) <= data.remaining_quantity:
                    if not associated:
                        history_data = Workstation_History(
                            created_by=request.user, workstation_data=data, received_quantity=float(quantity), completion_time=time)
                        history_data.save()
                    else:
                        history_data = Workstation_Associated_Product_History(
                            created_by=request.user, workstation_data=data, received_quantity=float(quantity), completion_time=time)
                        history_data.save()

                    data.completed_quantity = float(
                        data.completed_quantity) + float(quantity)
                    data.total_completion_time = sum_times([data.total_completion_time, time], types=True)
                    data.remaining_quantity = float(
                        data.remaining_quantity) - float(quantity)
                    data.save()

                    if workstation_datas['next_workstation']:
                        if not associated:
                            try:
                                flag = Workstation_Data.objects.get(eps_product_id=data.eps_product_id, prev_product=data.id, workstation=workstation_datas['next_workstation'])
                            except:
                                flag = None
                        else:
                            try:
                                flag = Workstation_Associated_Products_Data.objects.get(eps_product_id=data.eps_product_id, prev_product=data.id, workstation=workstation_datas['next_workstation'])
                            except:
                                flag = None
                        if not flag:
                            if not associated:
                                new_data = Workstation_Data(
                                                created_by=data.created_by, 
                                                product=data.product, 
                                                received_quantity=data.completed_quantity, 
                                                remaining_quantity=data.completed_quantity, 
                                                completed_quantity=0, 
                                                workstation_id=workstation_datas['next_workstation'], 
                                                prev_product=data,
                                                eps_product_id=data.eps_product_id,
                                                total_completion_time='00:00',
                                            )
                                new_data.save()
                            else:
                                new_data = Workstation_Associated_Products_Data(
                                                created_by=data.created_by, 
                                                product=data.product, 
                                                received_quantity=data.completed_quantity, 
                                                remaining_quantity=data.completed_quantity, 
                                                completed_quantity=0, 
                                                workstation_id=workstation_datas['next_workstation'], 
                                                prev_product=data,
                                                eps_product_id=data.eps_product_id,
                                                total_completion_time='00:00',
                                            )
                                new_data.save()
                            
                        else:
                            flag.received_quantity = float(flag.received_quantity) + float(quantity)
                            
                            flag.total_completion_time = sum_times([flag.total_completion_time, time], types=True)
                            flag.remaining_quantity = float(flag.remaining_quantity) + float(quantity)
                            flag.save()
                    else:
                        if workstation_datas['final_workstation'] == data.workstation.id:
                            if not associated:
                                try:
                                    flag2 = Workstation_Data.objects.get(eps_product_id=data.eps_product_id, is_completed=True, prev_product=data.id, workstation=workstation_datas['final_workstation'])
                                except:
                                    flag2 = None
                            else:
                                try:
                                    flag2 = Workstation_Associated_Products_Data.objects.get(eps_product_id=data.eps_product_id, is_completed=True, prev_product=data.id, workstation=workstation_datas['final_workstation'])
                                except:
                                    flag2 = None
                                    
                            if not flag2:
                                if not associated:
                                    new_data2  = Workstation_Data(
                                                created_by=data.created_by, 
                                                product=data.product, 
                                                received_quantity=data.completed_quantity, 
                                                remaining_quantity=data.completed_quantity, 
                                                completed_quantity=data.completed_quantity, 
                                                qaqc_received_quantity=data.completed_quantity,
                                                qaqc_remaining_quantity=data.completed_quantity,
                                                is_completed=True, 
                                                prev_product=data,
                                                eps_product_id=data.eps_product_id,
                                                workstation=data.workstation,
                                                total_completion_time=data.total_completion_time,
                                            )
                                    new_data2.save()
                                else:
                                    new_data2  = Workstation_Associated_Products_Data(
                                                created_by=data.created_by, 
                                                product=data.product, 
                                                received_quantity=data.completed_quantity, 
                                                remaining_quantity=data.completed_quantity, 
                                                completed_quantity=data.completed_quantity, 
                                                qaqc_received_quantity=data.completed_quantity,
                                                qaqc_remaining_quantity=data.completed_quantity,
                                                is_completed=True, 
                                                prev_product=data,
                                                eps_product_id=data.eps_product_id,
                                                workstation=data.workstation,
                                                total_completion_time=data.total_completion_time,
                                            )
                                    new_data2.save()
                            
                            else:
                                flag2.received_quantity = float(flag2.received_quantity) + float(quantity)
                                flag2.remaining_quantity = float(flag2.remaining_quantity) - float(quantity)
                                flag2.completed_quantity = float(flag2.completed_quantity) + float(quantity)
                                flag2.total_completion_time = sum_times([flag2.total_completion_time, time], types=True)
                                flag2.save()

                            if not Eps_QAQC.objects.filter(product=product):
                                qaqc_data = Eps_QAQC(
                                    created_by=request.user, product=product)
                                qaqc_data.save()

                            main_product = Eps_Products.objects.get(pk=data.eps_product_id.id)
                            main_product.qaqc_status = 1
                            main_product.save()
                        else:
                            print('Error in Completing ')
                    messages.success(request, "Successfully Updated Quantity")
                else:
                    messages.error(request, "Please check the entered quantity.")
    return redirect('workstaions_view', pk=main_product.id)


@login_required(login_url='signin')
def worksation_history(request, pk, associated=None):
    """
    This function retrieves the history data for a workstation or associated product and renders it in a
    template.
    
    """
    if not associated:
        data = Workstation_Data.objects.get(pk=pk)
        history_datas = Workstation_History.objects.filter(
            workstation_data=data)
    else:
        data = Workstation_Associated_Products_Data.objects.get(pk=pk)
        history_datas = Workstation_Associated_Product_History.objects.filter(
            workstation_data=data)

    context = {
        'data': data,
        'history_datas': history_datas,
        'associated': associated
    }
    return render(request, "Projects/Eps/eps_view/workstation_history.html", context)


@login_required(login_url='signin')
def skip_workstation(request, pk, associated=None):
    """
    This function allows a user to skip a workstation in a production process and move to the next one.
    
    """
    if not associated:
        data = Workstation_Data.objects.get(pk=pk)
        workstation_datas = workstation_data(
            pk=data.product.main_products.main_product.eps_product.product.product.id,
            current_workstation=data.workstation.id
        )
    else:
        data = Workstation_Associated_Products_Data.objects.get(pk=pk)
        workstation_datas = workstation_data(
            pk=data.product.main_product.main_product.eps_product.product.product.id,
            current_workstation=data.workstation.id
        )
    if workstation_datas['next_workstation']:
        data.workstation_id = workstation_datas['next_workstation']
        content = {
            'success': True,
            "message": "Successfully Skiped"
        }
    else:
        if data.completed_quantity == data.received_quantity:
            if workstation_datas['final_workstation'] == data.workstation.id:
                data.is_completed = True
                content = {
                    'success': True,
                    "message": "Successfully Skiped"
                }
            else:
                print('Error in Completing ')
        else:
            print("Please Enter Before Move to Complete.")
            content = {
                'success': False,
                "message": "Please Enter Before Move to Complete."
            }
    data.save()
    return JsonResponse(content, status=200)


@login_required(login_url='signin')
def qaqc_view(request, pk):
    """
    This function retrieves and displays various details related to a specific EPS product for quality
    assurance and quality control purposes.
    """
    product = Eps_Products.objects.get(pk=pk)
    eps_obj = Eps_main.objects.get(pk=product.eps_data.id)
    products = [product.product.product.main_products.main_product.id for product in Eps_QAQC.objects.filter(product__product__main_products__main_product__eps_data=eps_obj)]

    products_obj = Eps_Products.objects.filter(pk__in=products)
    product_data = SalesOrderItems.objects.get(pk=product.eps_product.product.id)
    # product_data = EstimationMainProduct.objects.get(pk=product.eps_product.product.id)
    # product_aluminium = MainProductAluminium.objects.get(estimation_product=product_data)
    
    eps_products_details = Eps_Product_Details.objects.filter(main_product=product)
    eps_infill_details = Eps_infill_Details.objects.filter(
        main_product=product, is_outsourced=True
        ).distinct('infill__panel_specification__specifications')
    
    attachments = Fabrication_Attachments.objects.filter(
        eps_product=product)
    
    qaqc_products_details = Workstation_Data.objects.filter(
        eps_product_id=product, product__main_products__main_product=product, is_completed=True)
    qaqc_associated_products = Workstation_Associated_Products_Data.objects.filter(
        eps_product_id=product, 
        product__main_product__main_product=product, 
        is_completed=True)
    print("qaqc_associated_products==>", qaqc_associated_products)
    qaqc_vision_infills = QAQC_infill_Products.objects.filter(product__infill_product__main_product=product, product__infill_product__infill__panel_type=1)
    qaqc_spandrel_infills = QAQC_infill_Products.objects.filter(product__infill_product__main_product=product, product__infill_product__infill__panel_type=2)
    qaqc_openable_infills = QAQC_infill_Products.objects.filter(product__infill_product__main_product=product, product__infill_product__infill__panel_type=3)
    
    try:
        scedule_details = Schedule_Product.objects.get(product__main_products__main_product=product)
    except Schedule_Product.DoesNotExist:
        scedule_details = None
    
    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(product=product)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except:
        shopfloor_eps_data = None
        shopfloor_attachments = None
        
    try:
        # infill_details = MainProductGlass.objects.get(estimation_product=product_data, glass_primary=True)
        # sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_data, glass_primary=False)
        infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
        sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
    except Exception as e:
        infill_details = None
        sec_infill_details = None
    
    context = {
        'title': f'{PROJECT_NAME} | View EPS',
        'products_obj': products_obj,
        'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,
        'infill_details': infill_details,
        'sec_infill_details': sec_infill_details,
        'eps_products_details': eps_products_details,
        'eps_infill_details': eps_infill_details,
        'attachments': attachments,
        'shopfloor_eps_data': shopfloor_eps_data,
        'shopfloor_attachments': shopfloor_attachments,
        'scedule_details': scedule_details,
        
        'qaqc_products_details': qaqc_products_details,
        'qaqc_associated_products': qaqc_associated_products,
        'qaqc_vision_infills': qaqc_vision_infills,
        'qaqc_spandrel_infills': qaqc_spandrel_infills,
        'qaqc_openable_infills': qaqc_openable_infills,
    }
    
    return render(request, "Projects/Eps/eps_view/QAQC_view.html", context)

@login_required(login_url='signin')
def qaqc_detail_view(request, pk):
    """
    This function retrieves and organizes various details related to a specific EPS product for display
    in a QAQC details view.
    
    """
    eps_item = Eps_Products.objects.get(pk=pk)

    product_obj = SalesOrderItems.objects.get(
        pk=eps_item.eps_product.product.id)
    # product_obj = EstimationMainProduct.objects.get(
    #     pk=eps_item.eps_product.product.id)
    
    qaqc_products_details = Workstation_Data.objects.filter(
        eps_product_id=eps_item, product__main_products__main_product=eps_item, is_completed=True)
    qaqc_associated_products = Workstation_Associated_Products_Data.objects.filter(
        eps_product_id=eps_item, product__main_product__main_product=eps_item, is_completed=True)

    infill_details = Eps_Outsource_items.objects.filter(
        infill_product__main_product=eps_item).distinct('infill_product')
    # product_details = MainProductAluminium.objects.get(
    #     estimation_product=product_obj)
    products_obj = Eps_ShopFloor_main_products.objects.filter(
        main_products__main_product=eps_item)

    qaqc_infills = QAQC_infill_Products.objects.filter(
        product__infill_product__main_product=eps_item)

    try:
        attachments = Fabrication_Attachments.objects.filter(
            eps_product=eps_item).last()
    except:
        attachments = None
    try:
        pro_infill_details = SalesOrderInfill.objects.get(
            product=product_obj, infill_primary=True)
        pro_sec_infill_details = SalesOrderInfill.objects.filter(
            product=product_obj, infill_primary=False)
        # pro_infill_details = MainProductGlass.objects.get(
        #     estimation_product=product_obj, glass_primary=True)
        # pro_sec_infill_details = MainProductGlass.objects.filter(
        #     estimation_product=product_obj, glass_primary=False)
    except Exception as e:
        pro_infill_details = None
        pro_sec_infill_details = None

    context = {
        "eps_item": eps_item,
        "product_obj": product_obj,
        "products_obj": products_obj,
        # "product_details": product_details,
        "qaqc_products_details": qaqc_products_details,
        "infill_details": infill_details,
        "attachments": attachments,
        "pro_infill_details": pro_infill_details,
        "pro_sec_infill_details": pro_sec_infill_details,
        "qaqc_associated_products": qaqc_associated_products,
        "qaqc_infills": qaqc_infills,
    }
    return render(request, "Projects/Eps/eps_view/QAQC_details.html", context)


@login_required(login_url='signin')
def qaqc_quantity_update(request, pk, associated=None):
    """
    This function updates the QAQC quantity of a product and saves the history of the update.
    
    """
    
    if not associated:
        product = Workstation_Data.objects.get(pk=pk)
    else:
        product = Workstation_Associated_Products_Data.objects.get(pk=pk)
    
    other_products = Workstation_Data.objects.filter(eps_product_id__eps_data=product.eps_product_id.eps_data)
    eps_data = Eps_main.objects.get(pk=product.eps_product_id.eps_data.id)
    qaqc_parameter_objs = QAQC_parameters.objects.all()
    main_rating = 0
    
    if request.method == 'POST':
        new_quantity = request.POST.get('new_quantity')
        qaqc_status = request.POST.get('qaqc_status')
        rating_parameters = request.POST.getlist('rating__parameters')
        total_rating = request.POST.get('total_rate')
        
        
        
        qaqc_rating = 0
        
        if not product.qaqc_remaining_quantity == 0:
            
            if qaqc_status == '1':
                product.qaqc_completed_quantity = float(product.qaqc_completed_quantity) + float(new_quantity)
                product.qaqc_remaining_quantity = float(product.qaqc_remaining_quantity) - float(new_quantity)
                product.qaqc_status = qaqc_status
                product.save()
            
                if not associated:
                    history_data = QAQC_Main_Product_History(
                        product=product, 
                        created_by=request.user, 
                        quantity=float(new_quantity),
                        # specification = specification,
                        # appearance = appearance,
                        # functional = functional,
                        # labeling = labeling,
                        # joiners = joiners,
                        rating = total_rating,
                        )
                    history_data.save()
                    qaqc_data = QAQC_Main_Product_History.objects.filter(product=product)
                    # for rating_parameter in rating_parameters:
                    for qaqc_parameter_obj in qaqc_parameter_objs:
                        rating = request.POST.get(f'rating__{qaqc_parameter_obj.id}')
                        qaqc_rate_obj = QAQC_RatingHistory(
                            product_item=product.product.main_products,
                            rate=rating,
                            qaqc_process_data=history_data,
                        )
                        qaqc_rate_obj.save()
                else:
                    history_data = QAQC_Associated_Product_History(
                                            product=product, 
                                            created_by=request.user, 
                                            quantity=float(new_quantity),
                                            # specification = specification,
                                            # appearance = appearance,
                                            # functional = functional,
                                            # labeling = labeling,
                                            # joiners = joiners,
                                            rating = total_rating,
                                        )
                    history_data.save()
                    # for rating_parameter in rating_parameters:
                    for qaqc_parameter_obj in qaqc_parameter_objs:
                        rating = request.POST.get(f'rating__{qaqc_parameter_obj.id}')
                        qaqc_rate_obj = QAQC_RatingHistory(
                            product_item=product.product.main_product,
                            rate=rating,
                            qaqc_associated_process_data=history_data,
                        )
                        qaqc_rate_obj.save()
                    qaqc_data = QAQC_Associated_Product_History.objects.filter(product=product)
                    
                    # for rating_parameter in rating_parameters:
                    #     for qaqc_parameter_obj in qaqc_parameter_objs:
                    #         rating = request.POST.get(f'rating__{qaqc_parameter_obj.id}')
                    #         qaqc_rate_obj = QAQC_RatingHistory(
                    #             product_item=product.product.main_products,
                    #             rate=rating,
                    #             qaqc_process_data=history_data,
                    #         )
                    #         qaqc_rate_obj.save()
                    
                if not product.qaqc_completed_quantity == 0:
                    main_product = Schedule_Product.objects.get(
                        product__main_products__main_product=product.eps_product_id)
                    product.delivery_remaining_quantity =  float(product.qaqc_completed_quantity)
                    if qaqc_data:
                        qaqc_count = qaqc_data.count()
                        for qaqc_item in qaqc_data:
                            qaqc_rating = float(qaqc_rating) + float(qaqc_item.rating)
                        final_rating = float(qaqc_rating)/qaqc_count
                        product.rating = math.ceil(final_rating)
                    
                    product.save()
                    if not Eps_Products_For_Delivery.objects.filter(product=main_product):
                        delivery_product = Eps_Products_For_Delivery(
                            created_by=request.user,
                            product=main_product
                        )
                        delivery_product.save()
                    
                    for other_product in other_products:
                        main_rating = float(main_rating)+float(other_product.rating)
                        main_rating_total = float(main_rating)/other_products.count()
                        eps_data.rating = math.ceil(main_rating_total)
                        eps_data.save()
                        # other_product.save()
                        
                        
                if product.qaqc_received_quantity == product.qaqc_completed_quantity:
                    product.is_qaqc_completed = True
                    product.save()
                    eps_product = Eps_Products.objects.get(pk=product.eps_product_id.id)
                    eps_product.qaqc_status = 2
                    eps_product.save()
            else:
                product.qaqc_status = qaqc_status
                product.save()
            
                
        if not associated:
            return redirect('qaqc_view', pk=product.product.main_products.main_product.id)
        else:
            return redirect('qaqc_view', pk=product.product.main_product.main_product.id)

    context = {
        "product": product,
        "associated": associated,
        "qaqc_parameter_objs": qaqc_parameter_objs,
    }
    return render(request, "Projects/Eps/eps_view/qaqc_product_update.html", context)


@login_required(login_url='signin')
def qaqc_quantity_history(request, pk, associated=None):
    """
    This function retrieves the quantity update history for a product or an associated product and
    renders it in a template.
    
    """

    if not associated:
        product = Workstation_Data.objects.get(pk=pk)
        history_datas = QAQC_Main_Product_History.objects.filter(product=pk)
    else:
        product = Workstation_Associated_Products_Data.objects.get(pk=pk)
        history_datas = QAQC_Associated_Product_History.objects.filter(
            product=pk)

    context = {
        "product": product,
        "history_datas": history_datas,
        "associated": associated,
    }
    return render(request, "Projects/Eps/eps_view/qaqc_quantity_update_history.html", context)
    

@login_required(login_url="signin")
def qaqc_infill_quantity_update(request, pk):
    """
    This function updates the quantity of a QAQC infill product and saves the changes to the database.
    
    """
    qaqc_infill = QAQC_infill_Products.objects.get(pk=pk)
    # other_products = Workstation_Data.objects.filter(eps_product_id__eps_data=qaqc_infill.product.infill_product.main_product.eps_data)
    eps_data = Eps_main.objects.get(pk=qaqc_infill.product.infill_product.main_product.eps_data.id)
    qaqc_parameter_objs = QAQC_parameters.objects.all()
    main_rating = 0
    
    if request.method == 'POST':
        new_quantity = request.POST.get('new_quantity')
        rating = request.POST.get('total_rate')
        # specification = request.POST.get('specification')
        # appearance = request.POST.get('appearance')
        # functional = request.POST.get('functional')
        # labeling = request.POST.get('labeling')
        # joiners = request.POST.get('joiners')
        qaqc_rating = 0
        if not qaqc_infill.remaining_quantity == 0:
            
            qaqc_infill.completed_quantity = float(qaqc_infill.completed_quantity) + float(new_quantity)
            qaqc_infill.remaining_quantity = float( qaqc_infill.remaining_quantity) - float(new_quantity)
            # qaqc_infill.delivery_remaining_quantity = float(qaqc_infill.completed_quantity) - float(qaqc_infill.delivery_completed_quantity)
            qaqc_infill.delivery_remaining_quantity =  float(qaqc_infill.completed_quantity)
            qaqc_infill.save()

            history_data = QAQC_Infill_History(
                                    product=qaqc_infill, 
                                    created_by=request.user, 
                                    quantity=float(new_quantity),
                                    # specification = specification,
                                    # appearance = appearance,
                                    # functional = functional,
                                    # labeling = labeling,
                                    # joiners = joiners,
                                    rating = rating,
                                    )
            history_data.save()
            qaqc_data = QAQC_Infill_History.objects.filter(product=qaqc_infill)
            if not qaqc_infill.completed_quantity == 0:
                for qaqc_parameter_obj in qaqc_parameter_objs:
                    rating = request.POST.get(f'rating__{qaqc_parameter_obj.id}')
                    qaqc_rate_obj = QAQC_RatingHistory(
                        infill_product_item=qaqc_infill,
                        rate=rating,
                        qaqc_process_infill_data=history_data,
                    )
                    qaqc_rate_obj.save()
                        
                # main_product = Schedule_Product.objects.get(
                #     product__main_products__main_product=qaqc_infill.product.infill_product.main_product)
                # qaqc_infill.delivery_remaining_quantity = float(qaqc_infill.completed_quantity)
                
                if qaqc_data:
                    qaqc_count = qaqc_data.count()
                    for qaqc_item in qaqc_data:
                        qaqc_rating = float(qaqc_rating) + float(qaqc_item.rating)
                    final_rating = float(qaqc_rating)/qaqc_count
                    qaqc_infill.rating = math.ceil(final_rating)
                qaqc_infill.save()
                
                
                if not Eps_Products_For_Delivery.objects.filter(
                        Q(outsourced_product__product__infill_product__main_product=qaqc_infill.product.infill_product.main_product)
                    ):
                    delivery_product = Eps_Products_For_Delivery(
                        created_by=request.user,
                        outsourced_product=qaqc_infill
                    )
                    delivery_product.save()
                    
                # for other_product in other_products:
                #     main_rating = float(main_rating)+float(other_product.rating)
                #     main_rating_total = float(main_rating)/other_products.count()
                #     eps_data.rating = math.ceil(main_rating_total)
                #     eps_data.save()
                
            if qaqc_infill.received_quantity == qaqc_infill.completed_quantity:
                qaqc_infill.is_qaqc_completed = True
                qaqc_infill.save()

                
        return redirect('qaqc_view', pk=qaqc_infill.product.infill_product.main_product.id)

    context = {
        "product": qaqc_infill,
        "qaqc_parameter_objs": qaqc_parameter_objs,
    }
    return render(request, "Projects/Eps/eps_view/qaqc_product_update.html", context)


@login_required(login_url='signin')
def qaqc_infill_quantity_history(request, pk):
    """
    This function retrieves the history of quantity updates for a specific product and renders it in a
    template.
    
    """
    product = QAQC_infill_Products.objects.get(pk=pk)
    history_datas = QAQC_Infill_History.objects.filter(product=pk)

    context = {
        "product": product,
        "history_datas": history_datas,
    }
    return render(request, "Projects/Eps/eps_view/qaqc_quantity_update_history.html", context)
    

@login_required(login_url='signin')
def products_for_delivery_view(request, eps):
    """
    This function retrieves and displays a list of products for delivery associated with a specific EPS
    object.
    
    """
    eps_obj = Eps_main.objects.get(pk=eps)
    # products = Eps_Products_For_Delivery.objects.filter(
    #                     (Q(product__product__main_products__main_product__eps_data=eps_obj)) | 
    #                     (Q(outsourced_product__product__infill_product__main_product__eps_data=eps_obj) & ~Q(outsourced_product__delivery_remaining_quantity=0))
    #                 )
    products = Eps_Products_For_Delivery.objects.filter(
                                                    Q(product__product__main_products__main_product__eps_data=eps_obj) |
                                                    (
                                                        Q(outsourced_product__product__infill_product__main_product__eps_data=eps_obj) 
                                                        # & 
                                                        # ~Q(outsourced_product__delivery_remaining_quantity=0)
                                                    )
                                                )

    
    
    context = {
        'title': f'{PROJECT_NAME} | View EPS',
        'products_obj': products,
        'eps_obj': eps_obj,
    }
    return render(request, "Projects/Eps/eps_view/products_for_delivery_view.html", context)


@login_required(login_url='signin')
def product_for_delivery_details(request, pk):
    """
    This function retrieves various details related to a product for delivery and renders them in a
    template.
    
    """
    eps_item = Eps_Products.objects.get(pk=pk)
    product_obj = SalesOrderItems.objects.get(pk=eps_item.eps_product.product.id)
    # product_obj = EstimationMainProduct.objects.get(
    #     pk=eps_item.eps_product.product.id)
    qaqc_products_details = Workstation_Data.objects.filter(
                                            Q(eps_product_id=eps_item) &
                                            Q(product__main_products__main_product=eps_item) &
                                            Q(is_completed=True) &
                                            ~Q(qaqc_completed_quantity=0)
                                        )
    
    qaqc_associated_products = Workstation_Associated_Products_Data.objects.filter(
                                            Q(eps_product_id=eps_item) &
                                            Q(product__main_product__main_product=eps_item) &
                                            Q(is_completed=True) & 
                                            ~Q(qaqc_completed_quantity=0)
                                        )

    infill_details = Eps_Outsource_items.objects.filter(
        infill_product__main_product=eps_item).distinct('infill_product')
    # product_details = MainProductAluminium.objects.get(
    #     estimation_product=product_obj)
    products_obj = Eps_ShopFloor_main_products.objects.filter(
        main_products__main_product=eps_item)

    # qaqc_infills = QAQC_infill_Products.objects.filter(
    #                                     product__infill_product__main_product=eps_item, 
    #                                     is_qaqc_completed=True
    #                                     # is_completed=True
    #                                     )
    
    qaqc_vision_infills = QAQC_infill_Products.objects.filter(
                                        Q(product__infill_product__main_product=eps_item) &
                                        Q(product__infill_product__infill__panel_type=1) & 
                                        ~Q(delivery_remaining_quantity=0)
                                    )
    qaqc_spandrel_infills = QAQC_infill_Products.objects.filter(
                                        Q(product__infill_product__main_product=eps_item) &
                                        Q(product__infill_product__infill__panel_type=2) &
                                        ~Q(delivery_remaining_quantity=0)
                                    )
    qaqc_openable_infills = QAQC_infill_Products.objects.filter(
                                        Q(product__infill_product__main_product=eps_item) &
                                        Q(product__infill_product__infill__panel_type=3)  & 
                                        ~Q(delivery_remaining_quantity=0)
                                    )
  

    cart_main_product = Delivery_Product_Cart_Main.objects.filter(
        product__eps_product_id__eps_data=eps_item.eps_data)
    cart_associated_product = Delivery_Product_Cart_Associated.objects.filter(
        product__eps_product_id__eps_data=eps_item.eps_data)
    cart_infill_product = Delivery_Product_Cart_infill.objects.filter(
        product__product__infill_product__main_product__eps_data=eps_item.eps_data)

    try:
        attachments = Fabrication_Attachments.objects.filter(
            eps_product=eps_item).last()
    except:
        attachments = None
        
    try:
        pro_infill_details = SalesOrderInfill.objects.get(
            product=product_obj, infill_primary=True)
        pro_sec_infill_details = SalesOrderInfill.objects.filter(
            product=product_obj, infill_primary=False)
        # pro_infill_details = MainProductGlass.objects.get(
        #     estimation_product=product_obj, glass_primary=True)
        # pro_sec_infill_details = MainProductGlass.objects.filter(
        #     estimation_product=product_obj, glass_primary=False)
    except Exception as e:
        pro_infill_details = None
        pro_sec_infill_details = None

    context = {
        "eps_item": eps_item,
        "product_obj": product_obj,
        "products_obj": products_obj,
        # "product_details": product_details,
        "qaqc_products_details": qaqc_products_details,
        "infill_details": infill_details,
        "attachments": attachments,
        "pro_infill_details": pro_infill_details,
        "pro_sec_infill_details": pro_sec_infill_details,
        "qaqc_associated_products": qaqc_associated_products,
        "qaqc_vision_infills": qaqc_vision_infills,
        "qaqc_spandrel_infills": qaqc_spandrel_infills,
        "qaqc_openable_infills": qaqc_openable_infills,

        "cart_main_product": cart_main_product,
        "cart_associated_product": cart_associated_product,
        "cart_infill_product": cart_infill_product,
    }
    return render(request, "Projects/Eps/eps_view/products_for_delivery_details.html", context)


@login_required(login_url="signin")
def delivery_quantity_update(request, pk, associated=None):
    """
    This function updates the delivery quantity of a product and adds it to the delivery cart.
    
    """
    if not associated:
        product = Workstation_Data.objects.get(pk=pk)
    else:
        product = Workstation_Associated_Products_Data.objects.get(pk=pk)

    if request.method == 'POST':
        new_quantity = request.POST.get('new_quantity')

        if float(new_quantity) <= product.delivery_remaining_quantity and float(new_quantity) >= 0:
            product.delivery_remaining_quantity = float(
                product.delivery_remaining_quantity)-float(new_quantity)
            product.delivery_completed_quantity = float(
                product.delivery_completed_quantity)+float(new_quantity)
            if product.qaqc_completed_quantity == product.delivery_completed_quantity:
                product.is_delivered = True
            product.save()

            if not associated:
                try:
                    cart_item = Delivery_Product_Cart_Main.objects.get(
                        product=product)
                except:
                    cart_item = None
                if not cart_item:
                    cart_product = Delivery_Product_Cart_Main(
                        created_by=request.user, product=product, quantity=float(new_quantity))
                    cart_product.save()
                else:
                    cart_item.quantity = float(
                        cart_item.quantity) + float(new_quantity)
                    cart_item.save()
            else:
                try:
                    cart_item = Delivery_Product_Cart_Associated.objects.get(
                        product=product)
                except:
                    cart_item = None
                if not cart_item:
                    cart_product = Delivery_Product_Cart_Associated(
                        created_by=request.user, product=product, quantity=float(new_quantity))
                    cart_product.save()
                else:
                    cart_item.quantity = float(
                        cart_item.quantity) + float(new_quantity)
                    cart_item.save()
        else:
            messages.error(request, "Check Entered Quantity.")
        return redirect('products_for_delivery_view', eps=product.eps_product_id.eps_data.id)
            

    context = {
        "product": product,
        "associated": associated,
    }
    return render(request, "Projects/Eps/eps_view/delivery_quantity_update.html", context)


@login_required(login_url="signin")
def delivery_infill_quantity_update(request, pk, type=None):
    """
    This function updates the delivery quantity of a product and adds it to the delivery cart if the
    entered quantity is valid.
    
    """
    product = QAQC_infill_Products.objects.get(pk=pk)
    if request.method == 'POST':
        new_quantity = request.POST.get('new_quantity')
        try:
            cart_item = Delivery_Product_Cart_infill.objects.get(
                product=product)
        except:
            cart_item = None
        if float(new_quantity) <= product.delivery_remaining_quantity and float(new_quantity) >= 0:
            product.delivery_remaining_quantity = float(
                product.delivery_remaining_quantity)-float(new_quantity)
            product.delivery_completed_quantity = float(
                product.delivery_completed_quantity)+float(new_quantity)
            if product.completed_quantity == product.delivery_completed_quantity:
                product.is_delivered = True
            product.save()

            if not cart_item:
                cart_product = Delivery_Product_Cart_infill(
                    created_by=request.user, product=product, quantity=float(new_quantity))
                cart_product.save()
            else:
                cart_item.quantity = float(
                    cart_item.quantity) + float(new_quantity)
                cart_item.save()
        else:
            messages.error(request, "Check Entered Quantity.")
        if not type:
            return redirect('products_for_delivery_view', eps=product.product.infill_product.main_product.eps_data.id)
        else:
            return redirect('product_for_delivery_product_detail_view', pk=product.product.infill_product.main_product.id)
    context = {
        "product": product,
        "type":type,
    }
    return render(request, "Projects/Eps/eps_view/delivery_quantity_update.html", context)


@login_required(login_url="signin")
def cart_delete(request, pk, type):
    """
    This function deletes a product from a cart and updates the product's delivery quantity.
    
    """
    if type == "main":
        cart_item = Delivery_Product_Cart_Main.objects.get(pk=pk)
        product = Workstation_Data.objects.get(pk=cart_item.product.id)
        eps = product.eps_product_id.eps_data
    elif type == "associated":
        cart_item = Delivery_Product_Cart_Associated.objects.get(pk=pk)
        product = Workstation_Associated_Products_Data.objects.get(
            pk=cart_item.product.id)
        eps = product.eps_product_id.eps_data
    elif type == 'infill':
        cart_item = Delivery_Product_Cart_infill.objects.get(pk=pk)
        product = QAQC_infill_Products.objects.get(pk=cart_item.product.id)
        eps = product.product.infill_product.main_product.eps_data
    else:
        cart_item = None

    if cart_item:
        revert_quantity = cart_item.quantity
        product.delivery_remaining_quantity = float(
            product.delivery_remaining_quantity) + float(revert_quantity)
        product.delivery_completed_quantity = float(
            product.delivery_completed_quantity)-float(revert_quantity)
        product.save()
        cart_item.delete()
        messages.success(request, 'Successfully deleted Product From Cart.')
        return JsonResponse({'success': True, 'eps_id': eps.id})
    else:
        messages.success(request, 'Check After Some time.')
        return JsonResponse({'success': True, 'eps_id': eps.id})
        
        
@login_required(login_url='signin')
def create_delivery_note(request, eps):
    """
    This function creates a delivery note for a given EPS object and saves the associated products and
    quantities.
    
    """
    eps_obj = Eps_main.objects.get(pk=eps)
    form = DeliveryNoteForm()
    
    # tem_product = Eps_Products.objects.filter(eps_data=eps_obj).last()
    
    cart_main_product = Delivery_Product_Cart_Main.objects.filter(
        product__eps_product_id__eps_data=eps_obj)
    cart_associated_product = Delivery_Product_Cart_Associated.objects.filter(
        product__eps_product_id__eps_data=eps_obj)
    cart_infill_product = Delivery_Product_Cart_infill.objects.filter(
        product__product__infill_product__main_product__eps_data=eps_obj)

    delivery_note_id = Delivery_Note.objects.all().last()
    if delivery_note_id:
        new_dn_id = int(delivery_note_id.delivery_note_id)+1
    else:
        new_dn_id = DN_ID

    if request.method == 'POST':
        form = DeliveryNoteForm(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.created_by = request.user
            form_obj.eps = eps_obj
            form_obj.delivery_note_id = new_dn_id
            form_obj.save()

            quantity = 0
            if form_obj is not None:
                main_product = Workstation_Data.objects.filter(pk__in=[product.product.pk for product in cart_main_product])
                form_obj.main_product.set(main_product)
                
                for workstation_data in main_product:
                    quantity += workstation_data.delivery_completed_quantity
                    
                associated_product = Workstation_Associated_Products_Data.objects.filter(
                    pk__in=[product.product.pk for product in cart_associated_product])
                form_obj.associated_product.set(associated_product)
                
                for associated_data in associated_product:
                    quantity += associated_data.delivery_completed_quantity

                infill_product = QAQC_infill_Products.objects.filter(
                    pk__in=[product.product.pk for product in cart_infill_product])
                form_obj.infill_product.set(infill_product)
                
                for infill_data in infill_product:
                    quantity += infill_data.delivery_completed_quantity
                form_obj.total_quantity = quantity
                form_obj.save()
                
                messages.success(request, "Successfully Created Delivery Note DN-" + str(new_dn_id))
                
                cart_main_product.delete()
                cart_associated_product.delete()
                cart_infill_product.delete()
                return redirect('products_for_delivery_view', eps=eps_obj.id)
            else:
                messages.error(request, "Failed to create delivery note")
        else:
            messages.error(request, form.errors)
        return redirect('products_for_delivery_view', eps=eps_obj.id)
            

    context = {
        "eps_obj": eps_obj,
        "form": form,
    }
    return render(request, "Projects/Eps/eps_view/delivery_note_create.html", context)


@login_required(login_url="signin")
def inspection_view(request, pk):
    """
    This function renders a view for inspecting EPS products and their details.
    
    """
    product_item = Workstation_Data.objects.get(pk=pk)
    product = Eps_Products.objects.get(pk=product_item.eps_product_id.id)
    eps_obj = Eps_main.objects.get(pk=product.eps_data.id)
    products = []
    for delivery_note in Delivery_Note.objects.filter(status=2):
        for product_item in delivery_note.main_product.all():
            products.append(product_item.product.main_products.main_product)
    products_obj = products
    
    product_data = SalesOrderItems.objects.get(pk=product.eps_product.product.id)
    # product_data = EstimationMainProduct.objects.get(pk=product.eps_product.product.id)
    # product_aluminium = MainProductAluminium.objects.get(estimation_product=product_data)
    
    eps_products_details = Eps_Product_Details.objects.filter(main_product=product)
    
    outsourced_infill = Eps_Outsource_items.objects.filter(infill_product__main_product=product)
    
    eps_infill_details = Eps_infill_Details.objects.filter(
        main_product=product
        ).distinct('infill__panel_specification__specifications')
    
    attachments = Fabrication_Attachments.objects.filter(
        eps_product=product)
    try:
        scedule_details = Schedule_Product.objects.get(product__main_products__main_product=product)
    except Schedule_Product.DoesNotExist:
        scedule_details = None
        
    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(product=product)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except:
        shopfloor_eps_data = None
        shopfloor_attachments = None
    try:
        # infill_details = MainProductGlass.objects.get(estimation_product=product_data, glass_primary=True)
        # sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_data, glass_primary=False)
        infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
        sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
    except Exception as e:
        infill_details = None
        sec_infill_details = None
        
    delivery_notes = Delivery_Note.objects.filter(main_product=product_item)
    
    context = {
        'title': f'{PROJECT_NAME} | View EPS',
        'products_obj': products_obj,
        'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,
        'infill_details': infill_details,
        'sec_infill_details': sec_infill_details,
        'eps_products_details': eps_products_details,
        'eps_infill_details': eps_infill_details,
        'attachments': attachments,
        'shopfloor_eps_data': shopfloor_eps_data,
        'shopfloor_attachments': shopfloor_attachments,
        'outsourced_infill': outsourced_infill,
        'scedule_details': scedule_details,
        'delivery_notes': delivery_notes,
        'product_item': product_item,
    }
    
    return render(request, "Projects/Eps/eps_view/inspection_view.html", context)


@login_required(login_url="signin")
def eps_side_details(request, pk, product=None):
    eps_obj = Eps_main.objects.get(pk=pk)
    products_obj = Eps_Products.objects.filter(eps_data=eps_obj)
    
    if not product:
        product = products_obj.first()
    else:
        product = Eps_Products.objects.get(pk=product)

    product_data = SalesOrderItems.objects.get(pk=product.eps_product.product.id)
    # product_data = EstimationMainProduct.objects.get(pk=product.eps_product.product.id)
    # product_aluminium = MainProductAluminium.objects.get(estimation_product=product_data)

    eps_products_details = Eps_Product_Details.objects.filter(main_product=product)
    

    add_infill_btn = None
    for p in products_obj:
        if p.infill_status == 2:
            add_infill_btn = 1

    eps_vision_panel_details = Eps_infill_Details.objects.filter(
        main_product=product,
        infill__panel_type=1
        ).distinct('infill__panel_specification__specifications')
    
    eps_spandrel_panel_details = Eps_infill_Details.objects.filter(
        main_product=product,
        infill__panel_type=2
        ).distinct('infill__panel_specification__specifications')
    
    eps_openable_panel_details = Eps_infill_Details.objects.filter(
        main_product=product,
        infill__panel_type=3
        ).distinct('infill__panel_specification__specifications')
    
    attachments = Fabrication_Attachments.objects.filter(eps_product=product)

    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(product=product)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None

    try:
        scedule_details = Schedule_Product.objects.get(product__main_products__main_product=product)
    except Schedule_Product.DoesNotExist:
        scedule_details = None

    qaqc_products_details = Workstation_Data.objects.filter(
        eps_product_id=product, product__main_products__main_product__eps_data=eps_obj)
    
    qaqc_associated_products = Workstation_Associated_Products_Data.objects.filter(
        eps_product_id=product, product__main_product__main_product__eps_data=eps_obj)
    qaqc_infills = QAQC_infill_Products.objects.filter(
        product__infill_product__main_product__eps_data=eps_obj)

    # try:
    #     infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
    #     sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
    #     # infill_details = MainProductGlass.objects.get(estimation_product=product_data, glass_primary=True)
    #     # sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_data, glass_primary=False)
    # except Exception as e:
    #     infill_details = None
    #     sec_infill_details = None

    delivery_notes = Delivery_Note.objects.filter(main_product__in=[data.id for data in qaqc_products_details])
    context = {
        "eps_obj": eps_obj,
        "products_obj": products_obj,
        # 'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,
        # 'infill_details': infill_details,
        # 'sec_infill_details': sec_infill_details,
        
        'eps_products_details': eps_products_details,
        'eps_infill_details': eps_infill_details,
        'attachments': attachments,
        'add_infill_btn': add_infill_btn,
        'shopfloor_eps_data': shopfloor_eps_data,
        'shopfloor_attachments': shopfloor_attachments,
        'qaqc_products_details': qaqc_products_details,
        'qaqc_associated_products': qaqc_associated_products,
        'qaqc_infills': qaqc_infills,
        'delivery_notes': delivery_notes,
        'scedule_details': scedule_details,
        
        'eps_vision_panel_details': eps_vision_panel_details,
        'eps_spandrel_panel_details': eps_spandrel_panel_details,
        'eps_openable_panel_details': eps_openable_panel_details,
        
    }
    return render(request,"Projects/Eps/eps_side_data.html", context)


@login_required(login_url='signin')
def eps_history_view(request, pk, product):
    eps_obj = Eps_main.objects.get(pk=pk)
    products_obj = Eps_Products.objects.get(eps_data=eps_obj, eps_product__product=product)
    
    # if not product:
    # product = products_obj.first()
    # else:
        # product = Eps_Products.objects.get(pk=product)

    product_data = SalesOrderItems.objects.get(pk=product)
    # product_data = EstimationMainProduct.objects.get(pk=product.eps_product.product.id)
    # product_aluminium = MainProductAluminium.objects.get(estimation_product=product_data)

    eps_products_details = Eps_Product_Details.objects.filter(main_product=products_obj)
    

    add_infill_btn = None
    # for p in products_obj:
    if products_obj.infill_status == 2:
        add_infill_btn = 1

    eps_infill_details = Eps_infill_Details.objects.filter(
        main_product=product
        ).distinct('infill__panel_specification__specifications')
    attachments = Fabrication_Attachments.objects.filter(eps_product=product)

    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(product=product)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None

    try:
        scedule_details = Schedule_Product.objects.get(product__main_products__main_product=product)
    except Schedule_Product.DoesNotExist:
        scedule_details = None

    try:
        infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
        sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
        # infill_details = MainProductGlass.objects.get(estimation_product=product_data, glass_primary=True)
        # sec_infill_details = MainProductGlass.objects.filter(estimation_product=product_data, glass_primary=False)
    except Exception as e:
        infill_details = None
        sec_infill_details = None
    
    context = {
        "eps_obj": eps_obj,
        "products_obj": products_obj,
        'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,
        'infill_details': infill_details,
        'sec_infill_details': sec_infill_details,
        'eps_products_details': eps_products_details,
        'eps_infill_details': eps_infill_details,
        'attachments': attachments,
        'add_infill_btn': add_infill_btn,
        'shopfloor_eps_data': shopfloor_eps_data,
        'shopfloor_attachments': shopfloor_attachments,
        # 'qaqc_products_details': qaqc_products_details,
        # 'qaqc_associated_products': qaqc_associated_products,
        # 'qaqc_infills': qaqc_infills,
        # 'delivery_notes': delivery_notes,
        'scedule_details': scedule_details,
    }
    return render(request,"Projects/Eps/eps_history_view.html", context)


@login_required(login_url='signin')
def import_from_scope(request, pk):
    prodjct_obj = ProjectsModel.objects.get(pk=pk)
    project_enquirys = ProjectEstimations.objects.filter(project=prodjct_obj)
    buildings_objs = EstimationBuildings.objects.filter(
                        estimation__in=[estimation.estimations_version.id for estimation in project_enquirys],
                        created_by__created_by_estimation__convert_to_sales=False
                    ).distinct('id')
    
    
    if request.method == 'POST':
        products = request.POST.getlist('product')    
        width = request.POST.getlist('width')    
        height = request.POST.getlist('height')    
        quantity = request.POST.getlist('quantity')    
        area = request.POST.getlist('area')    
        
        
        flag = True
        if len(products) == EstimationMainProduct.objects.filter(pk__in=list(map(lambda x: int(x), products)), product_type=2, disabled=False).count():
            products_objs = EstimationMainProduct.objects.get(pk=int(products[0]))
            if products_objs.product_type == 2:
                flag = False
        if flag:
            for i, product in enumerate(products):
                products_obj = EstimationMainProduct.objects.get(pk=int(product))
                aluminium_data = MainProductAluminium.objects.get(estimation_product=product)
                infill_objs = MainProductGlass.objects.filter(estimation_product=product)
                accessory_objs = MainProductAccessories.objects.filter(estimation_product=product)
                addons_objs = MainProductAddonCost.objects.filter(estimation_product=product)
                
                try:
                    sales_group = SalesOrderGroups.objects.get(enquiry_data=products_obj.building.estimation.enquiry.id, group_name=products_obj.building.building_name)
                except Exception as e:
                    sales_group = None
                try:
                    sales_order_specification = SalesOrderSpecification.objects.get(reference_specification=products_obj.specification_Identifier)
                except Exception as e:
                    sales_order_specification = None

                if not sales_group:
                    building = EstimationBuildings.objects.get(pk=products_obj.building.id)
                    sales_group = SalesOrderGroups(group_name=building.building_name, enquiry_data=building.estimation.enquiry, project=prodjct_obj)
                    sales_group.save()
                    
                if not sales_order_specification:
                    specification_objs = EnquirySpecifications.objects.get(pk=products_obj.specification_Identifier.id)
                    sales_order_specification = SalesOrderSpecification(
                        reference_specification=specification_objs,
                        identifier=specification_objs.identifier,
                        categories=specification_objs.categories,
                        aluminium_products=specification_objs.aluminium_products,
                        aluminium_system=specification_objs.aluminium_system,
                        aluminium_specification=specification_objs.aluminium_specification,
                        aluminium_series=specification_objs.aluminium_series,
                        panel_category=specification_objs.panel_category,
                        panel_brand=specification_objs.panel_brand,
                        panel_series=specification_objs.panel_series,
                        panel_specification=specification_objs.panel_specification,
                        panel_product=specification_objs.panel_product,
                        surface_finish=specification_objs.surface_finish,
                        project=prodjct_obj,
                        have_vision_panels= True if specification_objs.panel_specification else False,
                    )
                    sales_order_specification.save()
                    
                    
                
                if products_obj.product_type == 1:
                    sales_product = SalesOrderItems(
                                        ref_product=products_obj, 
                                        width=width[i],
                                        height=height[i],
                                        quantity=quantity[i],
                                        area=area[i],
                                        total_area=(float(area[i])*float(quantity[i])),
                                        # specification_Identifier=product.specification_Identifier,
                                        category=products_obj.category,
                                        product=products_obj.product,
                                        panel_product=products_obj.panel_product,
                                        # main_product=product.main_product,
                                        brand=products_obj.brand,
                                        series=products_obj.series,
                                        panel_brand=products_obj.panel_brand,
                                        panel_series=products_obj.panel_series,
                                        
                                        product_code=aluminium_data.product_type,
                                        product_type=products_obj.product_type,
                                        product_description=aluminium_data.product_description,
                                        unit_price=products_obj.product_unit_price,
                                        sales_group=sales_group,
                                        is_sourced=products_obj.is_sourced,
                                        supplier=products_obj.supplier,
                                        surface_finish=aluminium_data.surface_finish,
                                        total_price=(float(products_obj.product_unit_price)*float(quantity[i])),
                                        is_accessory=products_obj.is_accessory,
                                        uom=products_obj.uom,
                                        price_per_sqm=products_obj.product_sqm_price,
                                        accessory_quantity=products_obj.accessory_quantity,
                                        accessory_total=products_obj.accessory_total,
                                        enable_addons=products_obj.enable_addons,
                                    )
                    sales_product.save()
                    sales_product.main_product = sales_product
                    sales_product.save()
                    prev_main_id = sales_product
                else:
                    sales_product = SalesOrderItems(
                                        ref_product=products_obj, 
                                        width=width[i],
                                        height=height[i],
                                        quantity=quantity[i],
                                        area=area[i],
                                        total_area=(float(area[i])*float(quantity[i])),
                                        # specification_Identifier=product.specification_Identifier,
                                        category=products_obj.category,
                                        product=products_obj.product,
                                        panel_product=products_obj.panel_product,
                                        main_product=prev_main_id,
                                        brand=products_obj.brand,
                                        series=products_obj.series,
                                        panel_brand=products_obj.panel_brand,
                                        panel_series=products_obj.panel_series,
                                        
                                        product_code=aluminium_data.product_type,
                                        product_type=products_obj.product_type,
                                        product_description=aluminium_data.product_description,
                                        unit_price=products_obj.product_unit_price,
                                        sales_group=sales_group,
                                        is_sourced=products_obj.is_sourced,
                                        supplier=products_obj.supplier,
                                        surface_finish=aluminium_data.surface_finish,
                                        total_price=(float(products_obj.product_unit_price)*float(quantity[i])),
                                        is_accessory=products_obj.is_accessory,
                                        uom=products_obj.uom,
                                        price_per_sqm=products_obj.product_sqm_price,
                                        accessory_quantity=products_obj.accessory_quantity,
                                        accessory_total=products_obj.accessory_total,
                                        enable_addons=products_obj.enable_addons,
                                    )
                    sales_product.save()
                
                sales_product.specification_Identifier = sales_order_specification
                sales_product.save()
                
                # for infill_obj in infill_objs:
                #     try:
                #         old_panels = SalesSecondarySepcPanels.objects.get(
                #             specifications=sales_order_specification,
                #             panel_type=1,
                #             panel_category=infill_obj.glass_specif.series.brands.panel_category.id,
                #             panel_brand=infill_obj.glass_specif.series.brands.id,
                #             panel_series=infill_obj.glass_specif.series.id,
                #             panel_product=infill_obj.estimation_product.panel_product.id,
                #             panel_specification=infill_obj.glass_specif.id
                #         )
                #     except Exception:
                #         old_panels = None
                    
                    
                #     if not old_panels:
                #         sales_order_infill = SalesSecondarySepcPanels(
                #             specifications=sales_order_specification,
                #             panel_type=1,
                #             panel_category=infill_obj.glass_specif.series.brands.panel_category,
                #             panel_brand=infill_obj.glass_specif.series.brands,
                #             panel_series=infill_obj.glass_specif.series,
                #             panel_product=infill_obj.estimation_product.panel_product,
                #             panel_specification=infill_obj.glass_specif
                #         )
                #         sales_order_infill.save()
                    
                for accessory_obj in accessory_objs:
                    sales_accessory = SalesOrderAccessories(
                                                    product=sales_product,
                                                    accessory_item=accessory_obj.accessory_item,
                                                    accessory_item_quantity=accessory_obj.accessory_item_quantity,
                                                    accessory_item_price=accessory_obj.accessory_item_price,
                                                    accessory_item_total=accessory_obj.accessory_item_total,
                                                )
                    sales_accessory.save()
                    
                for addons_obj in addons_objs:
                    sales_addons = SalesOrderAddons(
                                    product=sales_product,
                                    addons=addons_obj.addons,
                                    pricing_type=addons_obj.pricing_type,
                                    base_rate=addons_obj.base_rate,
                                    addon_quantity=addons_obj.addon_quantity,
                    )
                    sales_addons.save()
                    
                products_obj.convert_to_sales = True
                products_obj.save()
                
            for sales_spec in SalesOrderSpecification.objects.filter(project=prodjct_obj):
                for approval_type in ProjectApprovalTypes.objects.all():
                    project_approval_obj = ProjectSepcificationsApproval(
                        specification=sales_spec,
                        approve_type=approval_type,
                        status=ProjectApprovalStatus.objects.first(),
                    )
                    project_approval_obj.save()
                    
            messages.success(request, "Successfully Imported Products From Scope.")
        else:
            messages.error(request, "Not Allowed Associated Product Only adding.")
            
        return redirect('project_scop', pk=prodjct_obj.id)
        
    context = {
        "prodjct_obj": prodjct_obj,
        "buildings_objs": buildings_objs,
    }
    return render(request, "Projects/import_form_sope.html", context)


@login_required(login_url='signin')
def sales_item_duplicate(request, pk):
    sales_item_obj = SalesOrderItems.objects.get(pk=pk)
    sales_infill = SalesOrderInfill.objects.filter(product=sales_item_obj)
    sales_accessories = SalesOrderAccessories.objects.filter(product=sales_item_obj)
    
    buildings_objs = EPSBuildingsModel.objects.filter(project=sales_item_obj.specification_Identifier.project).order_by('id')
    elevations_objs = ElevationModel.objects.filter(building__project=sales_item_obj.specification_Identifier.project).order_by('id')
    floor_objs = FloorModel.objects.filter(elevation__building__project=sales_item_obj.specification_Identifier.project).order_by('id')
    
    if request.method == "POST":
        width = request.POST.get('width', None)
        height = request.POST.get('height', None)
        area = request.POST.get('area', None)
        quantity = request.POST.get('quantity', None)
        
        unit_price = request.POST.get('unit_price', None)
        product_code = request.POST.get('product_code', None)
        product_description = request.POST.get('product_description', None)
        
        if width and height and quantity:
            new_sales_item_obj = sales_item_obj
            new_sales_item_obj.pk=  None
            new_sales_item_obj.width = float(width)
            new_sales_item_obj.height = float(height)
            new_sales_item_obj.area = float(area)
            new_sales_item_obj.quantity = float(quantity)
            new_sales_item_obj.total_area = float(area) * float(quantity)
            new_sales_item_obj.unit_price = float(unit_price)
            new_sales_item_obj.total_price = float(unit_price) * float(quantity)
            new_sales_item_obj.product_type = 1
            new_sales_item_obj.product_code = product_code
            new_sales_item_obj.product_description = product_description
            new_sales_item_obj.ref_product = None
            new_sales_item_obj.save()
            
            new_sales_item_obj.main_product = new_sales_item_obj
            new_sales_item_obj.save()
            
            for infill in sales_infill:
                if infill.infill_primary:
                    new_infill = infill
                    new_infill.pk = None
                    new_infill.infill_width = float(width)
                    new_infill.infill_height = float(height)
                    new_infill.infill_area = float(area)
                    new_infill.product = new_sales_item_obj
                    new_infill.infill_primary = True
                    new_infill.save()
                else:
                    new_infill = infill
                    new_infill.pk = None
                    # new_infill.infill_width = float(width)
                    # new_infill.infill_height = float(height)
                    # new_infill.infill_area = float(area)
                    new_infill.product = new_sales_item_obj
                    new_infill.infill_primary = False
                    new_infill.save()
            for sales_accessory in sales_accessories:
                
                new_sales_accessory = sales_accessory
                new_sales_accessory.pk = None
                new_sales_accessory.product = new_sales_item_obj
                new_sales_accessory.save()
                
        return redirect('project_scop', pk=sales_item_obj.sales_group.project.id)
    
    context = {
        "sales_item_obj": sales_item_obj,
        "sales_group": sales_item_obj.sales_group.id,
        "buildings_objs": buildings_objs,
        "elevations_objs": elevations_objs,
        "floor_objs": floor_objs,
    }
    return render(request, "Projects/Eps/sales_item_duplicate.html", context)


@login_required(login_url='signin')
def update_salesItem(request, pk):
    sales_item_obj = SalesOrderItems.objects.get(pk=pk)
    product_form = CreateSalesItem(project_id=sales_item_obj.sales_group.project.id, instance=sales_item_obj)
    panel_data = SalesOrderSpecification.objects.filter(project=sales_item_obj.sales_group.project).distinct('panel_specification')
    
    elevations_objs = ElevationModel.objects.filter(building__project=sales_item_obj.specification_Identifier.project.id)
    
    
    try:
        sales_infill = SalesOrderInfill.objects.get(product=sales_item_obj, infill_primary=True)
    except Exception:
        sales_infill = None
        
    vision_panels_details = SalesSecondarySepcPanels.objects.filter(specifications=sales_item_obj.specification_Identifier, panel_type=1)
    spandrel_panels_details = SalesSecondarySepcPanels.objects.filter(specifications=sales_item_obj.specification_Identifier, panel_type=2)
    openable_panels_details = SalesSecondarySepcPanels.objects.filter(specifications=sales_item_obj.specification_Identifier, panel_type=3)
    
    
        
    if request.method == "POST":
        
        product_form = CreateSalesItem(request.POST, project_id=sales_item_obj.sales_group.project.id, instance=sales_item_obj)
        elevation_type = request.POST.get('elevation_type', None)
        
        try:
            elevation_obj = ElevationModel.objects.get(pk=int(elevation_type))
        except Exception:
            elevation_obj = None
        
        if product_form.is_valid():
            product_obj = product_form.save()
            total_price = float(product_obj.unit_price) * float(product_obj.quantity)
            product_obj.total_price = total_price
            if product_obj.unit_price:
                product_obj.price_per_sqm = float(product_obj.unit_price) / float(product_obj.area)
            if elevation_obj:
                product_obj.elevation = elevation_obj
            product_obj.save()
            

            messages.success(request, "Successfully Updated Sales Item.")
        else:
            messages.error(request, f'Error:{product_form.errors}')
        return redirect('project_scop', pk=sales_item_obj.sales_group.project.id)
    
    context = {
        "sales_item_obj": sales_item_obj,
        "product_form": product_form,
        "panel_data": panel_data,
        "sales_infill": sales_infill,
        "elevations_objs": elevations_objs,
        "project_obj": sales_item_obj.sales_group.project,
        "sales_group": sales_item_obj.sales_group,
        # "infill_formset": infill_formset,
        "vision_panels_details": vision_panels_details,
        "spandrel_panels_details": spandrel_panels_details,
        "openable_panels_details": openable_panels_details,
        
    }
    return render(request, "Projects/Eps/add_sales_item.html", context)


@login_required(login_url='signin')
def salesItem_specifications(request, pk):
    projec_obj = ProjectsModel.objects.get(pk=pk)
    project_estimation_obj = ProjectEstimations.objects.get(project=projec_obj)
    sales_specifications = SalesOrderSpecification.objects.filter(project=projec_obj).order_by('id')
    approval_type_objs = ProjectApprovalTypes.objects.all()
    status_objs = ProjectApprovalStatus.objects.all()
    eps_products = Eps_Products.objects.filter(project=projec_obj, product_status=5, eps_data__isnull=True).order_by('id')
    # SalesOrderItems.objects.filter()
    # specifications = EnquirySpecifications.objects.filter(estimation=version)

    context = {
        "title": f'{PROJECT_NAME} | Project Specifications',
        "project": projec_obj,
        "sales_specifications": sales_specifications,
        "project_estimation_obj": project_estimation_obj,
        "approval_type_objs": approval_type_objs,
        "status_objs": status_objs,
        "eps_products": eps_products,
    }
    return render(request, 'Projects/project_specifications.html', context)


@login_required(login_url='signin')
def project_approvals(request, pk):
    projec_obj = ProjectsModel.objects.get(pk=pk)
    project_estimation_obj = ProjectEstimations.objects.get(project=projec_obj)
    sales_specifications = SalesOrderSpecification.objects.filter(project=projec_obj)
    approval_type_objs = ProjectApprovalTypes.objects.all()
    status_objs = ProjectApprovalStatus.objects.all()
    eps_products = Eps_Products.objects.filter(project=projec_obj, product_status=5, eps_data__isnull=True).order_by('id')
    # for sales_spec in SalesOrderSpecification.objects.filter(project=projec_obj):
    #     for approval_type in ProjectApprovalTypes.objects.all():
    #         project_approval_obj = ProjectSepcificationsApproval(
    #             specification=sales_spec,
    #             approve_type=approval_type,
    #             status=ProjectApprovalStatus.objects.first(),
    #         )
    #         project_approval_obj.save()
    
    context = {
        "title": f'{PROJECT_NAME} | Project Specifications',
        "project": projec_obj,
        "sales_specifications": sales_specifications,
        "project_estimation_obj": project_estimation_obj,
        "approval_type_objs": approval_type_objs,
        "status_objs": status_objs,
        "eps_products": eps_products,
    }
    return render(request, 'Projects/project_approvals.html', context)


@login_required(login_url='signin')
def update_approval_notes(request, pk): 
    note_obj = ApprovalNotes.objects.get(pk=pk)
    spec_obj = SalesOrderSpecification.objects.get(pk=note_obj.specification.id)
    
    form = ApprovalNotesForm(instance=note_obj)           
    if request.method == 'POST':
        form = ApprovalNotesForm(request.POST, instance=note_obj)
        if form.is_valid():
            form_obj = form.save(commit=True)
            # form_obj.specification = spec_obj
            form_obj.modified_time = time()
            form_obj.save()
            messages.success(request, "Successfully Updated.")
        else:
            messages.error(request, form.errors)
        return redirect('salesItem_specifications', pk=spec_obj.project.id)
    context = {
        "spec_obj": spec_obj,
        "note_obj": note_obj,
        "form": form,
    }
    return render(request, "Projects/utils/approval_notes.html", context)


@login_required(login_url='signin')
def eps_quotation_view(request, pk):
    projec_obj = ProjectsModel.objects.get(pk=pk)
    project_estimation_obj = ProjectEstimations.objects.get(project=projec_obj)
    # quotation_obj = Quotations.objects.get(estimations=project_estimation_obj.)
    # sales_specifications = SalesOrderSpecification.objects.filter(project=projec_obj)

    directory = os.path.join(MEDIA_URL, 'Quotations')
    
    if project_estimation_obj.estimations_version.version.version == '0':
        version_name = 'Original'
    else:
        version_name = 'Revision '+str(project_estimation_obj.estimations_version.version.version)
        
    if project_estimation_obj.enquiry.enquiry_type == 1:
        customer_name = project_estimation_obj.quotation.quotation_customer.name
    else:
        if project_estimation_obj.quotation.prepared_for.first():
            customer_name = project_estimation_obj.quotation.prepared_for.first().name
        else:
            customer_name = 'None'
            
    file_path = str(project_estimation_obj.enquiry.enquiry_id)+'/'+str(customer_name)+'/'+str(version_name)
    
    open_path = os.path.join(directory, file_path).replace("\\", '/')
    if os.path.exists(open_path):
        for root, dirs, files in os.walk(open_path):
            for file in files:
                file_path = os.path.join(root, file).replace("\\", '/')
    else:
        file_path = None
        
    context = {
        "title": f'{PROJECT_NAME} | Project Specifications',
        "project": projec_obj,
        # "sales_specifications": sales_specifications,
        "project_estimation_obj": project_estimation_obj,
        "file_path": file_path,
        "domain": 'http://'+str(request.get_host()),
    }
    return render(request, 'Projects/General/eps_quotation_view.html', context)


@login_required(login_url='signin')
def sales_specification_udate(request, pk):
    specification = SalesOrderSpecification.objects.get(pk=pk)
    category = specification.categories
    
    project_details = ProjectEstimations.objects.get(project=specification.project.id)
    
    if specification.surface_finish:
        form = UpdatsalesSpecificationForm(surface_finish_kit_id=specification.surface_finish.master.id, instance=specification)
    else:
        form = UpdatsalesSpecificationForm(surface_finish_kit_id=project_details.enquiry.surface_finish_price.id, instance=specification)
    
    notes_form = ApprovalNotesForm()
    
    secVisionPanelForm = modelformset_factory(SalesSecondarySepcPanels, form=SecSpecVisionPanelsForm, extra=1, can_delete=True)
    if SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=1):
        secvpanel_formset = secVisionPanelForm(queryset=SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=1), prefix='sec_v_panel')
    else:
        secvpanel_formset = secVisionPanelForm(queryset=SalesSecondarySepcPanels.objects.none(), prefix='sec_v_panel')
    
    specSpandrelPanelForm = modelformset_factory(SalesSecondarySepcPanels, form=SecSpecSpandrelPanelsForm, extra=1, can_delete=True)
    if SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=1):
        secspanel_formset = specSpandrelPanelForm(queryset=SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=2), prefix='sec_s_panel')
    else:
        secspanel_formset = specSpandrelPanelForm(queryset=SalesSecondarySepcPanels.objects.none(), prefix='sec_s_panel')
    
    specOpenablePanelForm = modelformset_factory(SalesSecondarySepcPanels, form=SecOpenablePanelsForm, extra=1, can_delete=True)
    if SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=1):
        secopanel_formset = specOpenablePanelForm(queryset=SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=3), prefix='sec_o_panel')
    else:
        secopanel_formset = specOpenablePanelForm(queryset=SalesSecondarySepcPanels.objects.none(), prefix='sec_o_panel')
    
    if request.method == 'POST':
        if specification.surface_finish:
            form = UpdatsalesSpecificationForm(request.POST, surface_finish_kit_id=specification.surface_finish.master.id, instance=specification)
        else:
            form = UpdatsalesSpecificationForm(request.POST, surface_finish_kit_id=project_details.enquiry.surface_finish_price.id, instance=specification)
        
        secvpanel_formset = secVisionPanelForm(request.POST, prefix='sec_v_panel')
        secspanel_formset = specSpandrelPanelForm(request.POST, prefix='sec_s_panel')
        secopanel_formset = specOpenablePanelForm(request.POST, prefix='sec_o_panel')
        notes_form = ApprovalNotesForm(request.POST)
        surface_finish_color = request.POST.get('surface_finish_color')
        
        if form.is_valid() and notes_form.is_valid():
            form_obj = form.save(commit=False)
            
            # form_obj.categories = category
            # form_obj.aluminium_products = aluminium_products
            # form_obj.panel_category = panel_category
            # form_obj.panel_product = panel_product
            
            form_obj.reset_status = True
            form_obj.save()
            
            
            salesorderitems = SalesOrderItems.objects.filter(specification_Identifier=specification)
            
            for sales_item in salesorderitems:
                sales_item.category = form_obj.categories
                sales_item.surface_finish = form_obj.surface_finish if sales_item.surface_finish else None
                sales_item.brand = form_obj.aluminium_system if sales_item.brand else None
                sales_item.series = form_obj.aluminium_series if sales_item.series else None
                sales_item.panel_brand = form_obj.panel_brand if sales_item.panel_brand else None
                sales_item.panel_series = form_obj.panel_series if sales_item.panel_series else None
                sales_item.panel_product = form_obj.panel_product if sales_item.panel_product else None
                form_obj.surface_finish_color__id = surface_finish_color
                # sales_item.panel_specification = form_obj.panel_specification if sales_item.panel_specification else None
                sales_item.save()
            
            notes_obj = notes_form.save(commit=False)
            if notes_obj.notes:
                notes_obj.specification = specification
                notes_obj.user = request.user
                notes_obj.save()
            
            for item in secvpanel_formset:
                if item.is_valid():
                    item_obj = item.save(commit=False)
                    if specification.have_vision_panels:
                        if item_obj.panel_category and item_obj.panel_brand and item_obj.panel_series and item_obj.panel_product:
                            item_obj.specifications = specification
                            # item_obj.primary_panel = False
                            item_obj.panel_type = 1
                            item_obj.save()
                        else:
                            print("Please Check The Vision Panel.")
                else:
                    print("Error in sub formset Panel ==>", item.errors)
                    messages.error(request, item.errors)
                    
            for item1 in secspanel_formset:
                if item1.is_valid():
                    item_obj1 = item1.save(commit=False)
                    if specification.have_spandrel_panels:
                        if item_obj1.panel_category and item_obj1.panel_brand and item_obj1.panel_series and item_obj1.panel_product:
                            item_obj1.specifications = specification
                            # item_obj.primary_panel = False
                            item_obj1.panel_type = 2
                            item_obj1.save()
                        else:
                            print("Please Check The spandrel Panel.")
                else:
                    print("Error in sub formset Panel ==>", item1.errors)
                    messages.error(request, item1.errors)
                    
            for item2 in secopanel_formset:
                if item2.is_valid():
                    item_obj2 = item2.save(commit=False)
                    if specification.have_openable_panels:
                        if item_obj2.panel_category and item_obj2.panel_brand and item_obj2.panel_series and item_obj2.panel_product:
                            item_obj2.specifications = specification
                            # item_obj.primary_panel = False
                            item_obj2.panel_type = 3
                            item_obj2.save()
                        else:
                            print("Please Check The Openable Panel.")
                else:
                    print("Error in sub formset infill ==>", item2.errors)
                    messages.error(request, item2.errors)
            
            
            if not specification.have_vision_panels:
                specification.vision_panels = None
                filter_vp_objs = SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=1).delete()
                
            if not specification.have_spandrel_panels:
                specification.spandrel_panels = None
                filter_sp_objs = SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=2).delete()
    
            if not specification.have_openable_panels:
                specification.openable_panels = None
                filter_op_objs = SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=3).delete()
                
            specification.save()
            
            #product Update by changeing specifications
            chain_update_products(specification.id) 
            messages.success(request, "Successfully Updated")
        else:
            print("Error", form.errors)
            
            messages.error(request, "Error in Specification Updated")
        
        return redirect('salesItem_specifications', pk=specification.project.id)

    context = {
        "specification": specification,
        "form": form,
        "notes_form": notes_form,
        "enquiry_obj": project_details.enquiry,
        "secvpanel_formset": secvpanel_formset,
        "secspanel_formset": secspanel_formset,
        "secopanel_formset": secopanel_formset,
    }
    return render(request, "Projects/Eps/update_sales_specifications.html", context)


@login_required(login_url='signin')
def clear_panel_details(request, pk):
    
    specification = SalesOrderSpecification.objects.get(pk=pk)
    
    filter_vp_objs = SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=1).delete()
    
    filter_sp_objs = SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=2).delete()

    filter_op_objs = SalesSecondarySepcPanels.objects.filter(specifications=specification, panel_type=3).delete()

    return JsonResponse({"success": True}, status=200)


@login_required(login_url='signin')
def delete_specification_secondary_panels(request, pk):
    
    sec_panel_obj = SalesSecondarySepcPanels.objects.get(pk=pk)
    try:
        sec_panel_obj.delete()
    except Exception:
        print("Error in deleting secondary panel")
    return JsonResponse({'success': True}, status=200)
    

@login_required(login_url='signin')
def salesorderitem_side_view(request, pk):
    sales_item_obj = SalesOrderItems.objects.get(pk=pk)
    
    context = {
        "product_obj": sales_item_obj,
    }
    return render(request, "Projects/utils/SalesOrderItem_SideView.html", context)


@login_required(login_url='signin')
def add_secondary_product(request, pk):
    sales_item_obj = SalesOrderItems.objects.get(pk=pk)
    
    form = AddSecondaryProductsForm(project_id=sales_item_obj.specification_Identifier.project.id)
    if request.method == 'POST':
        form = AddSecondaryProductsForm(request.POST, project_id=sales_item_obj.specification_Identifier.project.id)
        form_obj = form.save(commit=False)
        form_obj.main_product = sales_item_obj
        form_obj.product_type = 3
        form_obj.category = sales_item_obj.category
        form_obj.sales_group = sales_item_obj.sales_group
        form_obj.specification_Identifier = sales_item_obj.specification_Identifier
        form_obj.save()
        messages.success(request, "Successfully Added Secondary Product")
        
        return redirect('project_scop', pk=sales_item_obj.specification_Identifier.project.id)
        
    else:
        messages.error(request, form.errors)
        print('Secondary ERROR==>', form.errors)
    
    context = {
        "product_obj": sales_item_obj,
        "form": form,
    }
    
    return render(request, "Projects/utils/add_secondary_products.html", context)


@login_required(login_url='signin')
def update_secondary_product(request, pk):
    
    # secondary_product_obj = SalesOrderItems_Secondary_Product.objects.get(pk=pk)
    secondary_product_obj = SalesOrderItems.objects.get(pk=pk)
    form = AddSecondaryProductsForm(project_id=secondary_product_obj.specification_Identifier.project.id, 
                                    instance=secondary_product_obj)
    
    if request.method == 'POST':
        form = AddSecondaryProductsForm(request.POST, 
                                        project_id=secondary_product_obj.specification_Identifier.project.id, 
                                        instance=secondary_product_obj)
        if form.is_valid():
            
            form.save()
            messages.success(request, "Successfully Updated Secondary Product")
        else:
            print("Error==>", form.errors())
        return redirect('project_scop', pk=secondary_product_obj.specification_Identifier.project.id)
        
    else:
        messages.error(request, form.errors)
        print('Secondary ERROR==>', form.errors)
    
    context = {
        "form": form,
        "secondary_product_obj": secondary_product_obj,
    }
    
    return render(request, "Projects/utils/add_secondary_products.html", context)


@login_required(login_url='signin')
def delete_secondary_product(request, pk):
    
    # secondary_product_obj = SalesOrderItems_Secondary_Product.objects.get(pk=pk)
    secondary_product_obj = SalesOrderItems.objects.get(pk=pk)
    if request.method == "POST":
        try:
            secondary_product_obj.delete()
            messages.success(request, "Secondary Product Deleted Successfully")
        except Exception as e:
            print("EEE==>", e)
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")

        return redirect('project_scop', pk=secondary_product_obj.specification_Identifier.project.id)

    context = {"url": f"/Project/delete_secondary_product/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
def get_surfacefinish_color(request, pk):
    surface_finish_obj = Surface_finish_kit.objects.get(pk=pk)
    colors_objs = SurfaceFinishColors.objects.filter(surface_finish=surface_finish_obj.surface_finish)
    context = {
        "colors_objs": colors_objs,
    }
    return render(request, "Projects/utils/surfacefinish_colors.html", context)


@login_required(login_url='signin')
def update_project_approval_status(request, pk, status):
    
    project_approval_obj = ProjectSepcificationsApproval.objects.get(pk=pk)
    try:
        status_obj = ProjectApprovalStatus.objects.get(pk=status)
    except:
        status_obj = None
    
    project_approval_obj.status = status_obj
    project_approval_obj.save()
    
    return redirect('project_approvals', pk=project_approval_obj.specification.project.id)


# @login_required(login_url='signin')
def chain_update_products(pk):
    specification = SalesOrderSpecification.objects.get(pk=pk)
    sales_items_objs = SalesOrderItems.objects.filter(specification_Identifier=specification)
    
    for sales_items_obj in sales_items_objs:
        sales_items_obj.category = specification.categories
        sales_items_obj.product = specification.aluminium_products
        # sales_items_obj.panel_product = specification.panel_product
        sales_items_obj.brand = specification.aluminium_system
        sales_items_obj.series = specification.aluminium_series
        # sales_items_obj.panel_brand = specification.panel_brand
        # sales_items_obj.panel_series = specification.panel_series
        sales_items_obj.surface_finish = specification.surface_finish
        sales_items_obj.save()


@login_required(login_url='signin')
def sales_order_specification_duplicate(request, pk):
    specification = SalesOrderSpecification.objects.get(pk=pk)
    
    if request.method == 'POST':
        identifier = request.POST.get('identifier', None)
        if identifier:
            dup_specification_obj = specification
            dup_specification_obj.pk = None
            dup_specification_obj.identifier = identifier
            dup_specification_obj.save()
            
            messages.success(request, "Successfully Duplicated the Specifications")
        else:
            messages.error(request, "Please Check the Identifier")
            
        return redirect('salesItem_specifications', pk=specification.project.id)

    context = {
        "specification": specification,
       
    }
    return render(request, "Projects/utils/spec_duplicate.html", context)
    
    
@login_required(login_url='signin')
def qaqc_functional_parameters(request):
    parameter_objs = QAQC_parameters.objects.all()
    context = {
        "title": f'{PROJECT_NAME} | QAQC Functional Parameters.',
        "parameter_objs": parameter_objs,
    }
    return render(request, "Master_settings/Projects/QAQC_parameters_list.html", context)


@login_required(login_url='signin')
def add_qaqc_param(request):
    form = QAQCParametersFrom()
    if request.method == 'POST':
        form = QAQCParametersFrom(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully Added QAQC Parameter.")
        else:
            messages.error(request, form.errors)

        return redirect('qaqc_functional_parameters')
        
    context = {
        "form": form,

    }
    return render(request, "Master_settings/Projects/add_qaqc_parameters.html", context)


@login_required(login_url='signin')
def update_qaqc_param(request, pk):
    qaqc_param_obj = QAQC_parameters.objects.get(pk=pk)
    form = QAQCParametersFrom(instance=qaqc_param_obj)
    
    if request.method == 'POST':
        form = QAQCParametersFrom(request.POST, instance=qaqc_param_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully Updated QAQC Parameter.")
        else:
            messages.error(request, form.errors)

        return redirect('qaqc_functional_parameters')
        
    context = {
        "form": form,
        "qaqc_param_obj": qaqc_param_obj,
    }
    return render(request, "Master_settings/Projects/add_qaqc_parameters.html", context)


@login_required(login_url='signin')
def delete_qaqc_param(request, pk):
    
    qaqc_param_obj = QAQC_parameters.objects.get(pk=pk)
    if request.method == "POST":
        try:
            qaqc_param_obj.delete()
            messages.success(request, "QAQC Parameter Deleted Successfully")
        except Exception as e:
            print("EEE==>", e)
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")

        return redirect('qaqc_functional_parameters')

    context = {"url": f"/Project/delete_qaqc_param/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


