

import io, os, shutil, random, re
from django.db.models import Q
from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now as time
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import modelformset_factory
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from django.template.loader import get_template

from openpyxl import Workbook
from apps.companies.models import Companies
from apps.cover_cap.models import CoverCap_PressurePlates
from apps.helper import associated_key_gen, enquiry_logger, sum_times
from apps.others.models import SubmittingParameters
# from apps.tags.models import Tags
from xlsxwriter.workbook import Workbook
from wkhtmltopdf.views import PDFTemplateResponse

from apps.customers.models import Contacts, Customers
from apps.enquiries.models import (
                                Enquiries, 
                                Enquiry_Discontinued_History, 
                                EnquirySpecifications,
                                EnquiryUser,
                                EstimationNotes, 
                                Estimations, 
                                Pricing_Summary, 
                                Temp_EnquirySpecifications, 
                                Temp_EstimationNotes, 
                                Temp_Estimations, 
                                Temp_Pricing_Summary
                            )
from apps.enquiries.forms import (
                                CreateEnquiryForm, 
                                CreateEstimationNotesForms, 
                                EditEnquiryForm,
                                EditMainEnquiryForm, 
                                EnquiryDiscontinuedHistoryForm, 
                                TempCreateEstimationNotesForms
                            )
from apps.estimations.forms import (
                                CreateQuotationNote, 
                                CreateQuotations_Provisions, 
                                CreateQuotationsForm, 
                                ProductComplaintsForm, 
                                Temp_CreateQuotationNote, 
                                TempCreateEnquirySpecificationForm, 
                                TempCreateQuotations_Provisions,
                                TempCreateQuotationsForm, 
                                # TempCreateShortQuotationsForm, 
                                TempEditEnquirySpecificationForm, 
                                TempProductComplaintsForm,
                                TempUpdateAluminiumPercentage, 
                                TempUpdateGlassPercentage, 
                                TempUpdateLabourAndOverhead,
                                TempUpdateTolerance,
                                UpdateLabourAndOverhead,
                                UpdateAluminiumPercentage, 
                                UpdateGlassPercentage,
                                # CreateShortQuotationsForm, 
                                CreateEnquirySpecificationForm, 
                                EditEnquirySpecificationForm,
                                UpdateTolerance,
                                
                            )
from apps.estimations.models import (
                                Deduction_Items, 
                                Estimation_GeneralNotes, 
                                Estimation_Rating,
                                Estimation_UserTimes, 
                                EstimationMainProductMergeData, 
                                EstimationManiVersion, 
                                EstimationProduct_Associated_Data,
                                EstimationProductComplaints, 
                                EstimationProjectSpecifications,
                                EstimationSubmitting_Hours, 
                                EstimationVersions, 
                                EstimationBuildings,
                                EstimationMainProduct, 
                                MainProductAccessories, 
                                MainProductSilicon,
                                ProductComments, 
                                Quotation_Notes, 
                                Quotation_Notes_Comments, 
                                Quotation_Provisions,
                                QuotationDownloadHistory,
                                Quotations, 
                                MainProductGlass,
                                MainProductAluminium, 
                                PricingOption, 
                                MainProductAddonCost, 
                                Quote_Send_Detail, 
                                Temp_Deduction_Items, 
                                Temp_Estimation_GeneralNotes,
                                Temp_Estimation_UserTimes,
                                Temp_EstimationBuildings,
                                Temp_EstimationMainProduct, 
                                Temp_EstimationMainProductMergeData,
                                Temp_EstimationProduct_Associated_Data, 
                                Temp_EstimationProductComplaints, 
                                Temp_EstimationProjectSpecifications,
                                Temp_MainProductAccessories, 
                                Temp_MainProductAddonCost, 
                                Temp_MainProductAluminium,
                                Temp_MainProductGlass, 
                                Temp_MainProductSilicon, 
                                Temp_PricingOption, 
                                Temp_ProductComments, 
                                Temp_Quotation_Notes, 
                                Temp_Quotation_Notes_Comments,
                                Temp_Quotation_Provisions, 
                                Temp_Quotations,
                                AuditLogModel,
                                Temp_AuditLogModel,
                                
                            )
from apps.panels_and_others.models import (
                                PanelMasterBrands,
                                PanelMasterConfiguration, 
                                PanelMasterSeries, 
                                PanelMasterSpecifications,
                                PanelMasterBase
                            )
from apps.pricing_master.models import (
        AdditionalandLabourPriceMaster, 
        PriceMaster, 
        Sealant_kit, 
        Surface_finish_Master,
)
from apps.product_master.models import Product
from apps.Categories.models import Category
from apps.functions import (
        clear_temp,
        estimation_ai_rating, 
        main_product_duplicate, 
        building_duplicate_function,
        min_price_setup,
        new_deduction_price,
        product_unit_price,
        set_index, 
        update_pricing_summary,
        )
from amoeba.settings import (
        ENQ_ID, 
        MEDIA_URL,
        PROJECT_NAME, 
        QUOTATION_ID, 
        TINYMC_API, 
        STATIC_URL, 
        MEDIA_ROOT
)
from apps.product_parts.models import Profile_Kit, Profile_items
from apps.projects.forms import CreateProject
from apps.projects.models import ProjectsModel
from apps.quotations_master.models import Quotations_Master
from apps.suppliers.models import BillofQuantity


@login_required(login_url='signin')
@permission_required(['enquiries.view_enquiries'], login_url='permission_not_allowed')
def list_add_enquiries(request):
    """
    This function retrieves a list of enquiries and related information to display on a webpage.
    
    """
    if request.user.is_superuser:
        enquiry_objs = Enquiries.objects.all().order_by(
            'enquiry_id').select_related('company')
        enquiry_members = set(
            [member for enquiry in enquiry_objs for member in enquiry.enquiry_members.all()])
    else:
        enquiry_objs = Enquiries.objects.filter(
                            Q(created_by=request.user) |
                            Q(enquiry_members=request.user)
                        ).order_by('enquiry_id').select_related('company').distinct()

        enquiry_members = [request.user]

    form = CreateEnquiryForm()
    estimating_count = Enquiries.objects.filter(status=2).count()
    context = {
        "title": f"{PROJECT_NAME} | List Enquiries",
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': {enquiry.company for enquiry in enquiry_objs},
        'company': 0,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
    }

    return render(request, "Enquiries/enquiry_list.html", context)


@login_required(login_url='signin')
@permission_required(['enquiries.add_enquiries'], login_url='permission_not_allowed')
def create_enquiry(request):
    """
    This function creates an enquiry object with various fields and saves it to the database.
    """
    if request.method == 'POST':
        form = CreateEnquiryForm(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.created_by = form_obj.users = request.user
            form_obj.price_per_kg = float(request.POST['price_per_kg'])
            form_obj.labour_percentage = float(request.POST['labour'])
            form_obj.overhead_percentage = float(request.POST['additional'])
            form_obj.pricing = PriceMaster.objects.get(
                pk=int(request.POST['price_master']))
            form_obj.price_per_kg_markup = form_obj.pricing.markup

            form_obj.surface_finish_price = Surface_finish_Master.objects.all().last()
            form_obj.save()
            form.save_m2m()

            if request.POST['enquiry_type'] == '1':
                form_obj.main_customer = form_obj.customers.first()
                form_obj.save()

                folder_path = os.path.join(
                    MEDIA_ROOT, 'Quotations', form_obj.enquiry_id, form_obj.main_customer.name, 'Original')
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                else:
                    print("error.....")
            else:
                for customer in form_obj.customers.all():
                    folder_path = os.path.join(
                        MEDIA_ROOT, 'Quotations', form_obj.enquiry_id, customer.name, 'Original')
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                    else:
                        print("error.....")
                print("TENDER HAS NO MAIN CUSTOMER...")

            enquiry_logger(
                enquiry=form_obj, message='Enquiry Created', action=1, user=request.user)
            messages.success(request, "Enquiry Created Successfully")
        else:
            print("errors =>", form.errors)
    else:
        form = CreateEnquiryForm()
    return redirect('list_add_enquiries')


@login_required(login_url='signin')
@permission_required(['enquiries.change_enquiries'], login_url='permission_not_allowed')
def edit_enquiry(request, pk):
    """
    This function edits an enquiry object and its related objects in the database based on user input
    from a form.
    """
    enq_obj = Enquiries.objects.get(pk=pk)
    edit_form = EditMainEnquiryForm(instance=enq_obj)
    disc_historys = Enquiry_Discontinued_History.objects.filter(
        enquiry=enq_obj).order_by('id')
    discontnue_form = EnquiryDiscontinuedHistoryForm(
        instance=disc_historys.last())
    # has_project = ProjectsModel.objects.filter(quotation__estimations__enquiry=enq_obj).order_by('id')
    # projec_obj = ProjectsModel.objects.get(quotation__estimations__enquiry=enq_obj) if has_project else None
    estimation = Estimations.objects.filter(
        enquiry=pk, version__status=12).first()
    note_form = CreateEstimationNotesForms(
    ) if estimation and estimation.version.status == 12 else None
    projects_obj = ProjectsModel.objects.all().exclude(status=0).order_by('id')
    assigned_customer = request.POST.get('assigned_customer')
    price_per_kg = request.POST.get('price_per_kg')
    labour = request.POST.get('labour')
    additional = request.POST.get('additional')
    price_master = request.POST.get('price_master')
    enquiry_type = request.POST.get('enquiry_type')
    status_update = request.POST.get('status_update')
    enqu_status_update = request.POST.get('status')
    project = request.POST.get('selecte_project')
    send_version = request.POST.get('send_version_select')
    
    # customers
    try:
        quotation = Quotations.objects.get(estimations=estimation)
    except Exception as e:
        print("e==>", e)
        quotation = None
    
    send_versions = Estimations.objects.filter(enquiry=enq_obj, version__status=12)
    
    if request.method == 'POST':
        edit_form = EditMainEnquiryForm(request.POST, instance=enq_obj)
        discontnue_form = EnquiryDiscontinuedHistoryForm(
            request.POST, instance=disc_historys.last())
        
        if estimation and estimation.version.status == 12:
            note_form = CreateEstimationNotesForms(request.POST)

        if status_update == '13' and estimation and estimation.enquiry.enquiry_type == 2:
            # quotation = Quotations.objects.get(estimations=estimation)
            assigned_customer = request.POST.get('assigned_customer')

        old_status_enquiry = enq_obj.status
        
        if edit_form.is_valid() and discontnue_form.is_valid():
            edit_form_obj = edit_form.save(commit=False)
            edit_form_obj.last_modified_by = request.user
            edit_form_obj.last_modified_date = time()
            edit_form_obj.price_per_kg = float(price_per_kg)
            edit_form_obj.labour_percentage = float(labour)
            edit_form_obj.overhead_percentage = float(additional)
            edit_form_obj.pricing_id = int(price_master)

            if estimation and estimation.version.status == 13:
                edit_form_obj.status = 8
                
            edit_form_obj.save()
            edit_form.save_m2m()
            edit_form.save()
            
            if enquiry_type == '1':
                edit_form_obj.main_customer = edit_form_obj.customers.all().first()
                # if quotation:
                #     quotation.
                    
                if note_form and note_form.is_valid():
                    note_form_obj = note_form.save(commit=False)
                    version = EstimationVersions.objects.get(
                        pk=estimation.version.id)
                    if not status_update:
                        note_form_obj.estimation = estimation
                        note_form_obj.created_by = request.user
                        note_form_obj.created_date = time()
                        edit_form_obj.status = old_status_enquiry
                        # edit_form_obj.save()
                    elif status_update == '13':
                        edit_form_obj.status = 8
                        edit_form_obj.save()
                        print("STATUS==>", edit_form_obj.status)
                        note_form_obj.note_status = 14
                        note_form_obj.created_by = request.user
                        note_form_obj.created_date = time()
                        note_form_obj.estimation = estimation
                        send_veriosn_obj = Estimations.objects.get(pk=send_version)
                        send_estimations = EstimationVersions.objects.get(pk=send_veriosn_obj.version.id)
                        send_estimations.status = 13
                        send_estimations.save()
                        # version.status = 13
                        # version.save()
                    else:
                        version.status = 11
                        edit_form_obj.status = 6
                        # edit_form_obj.save()
                        note_form_obj.note_status = 11
                        note_form_obj.created_by = request.user
                        note_form_obj.created_date = time()
                        note_form_obj.estimation = estimation
                        version.save()
                    
                    # edit_form_obj.save()
                    note_form_obj.management = True
                    note_form_obj.save()
                # elif not note_form:
                #     # edit_form_obj.status = old_status_enquiry
                #     edit_form_obj.save()
            else:
                if note_form and note_form.is_valid():
                    note_form_obj = note_form.save(commit=False)
                    version = EstimationVersions.objects.get(pk=estimation.version.id)
                    if not status_update:
                        note_form_obj.estimation = estimation
                        note_form_obj.created_by = request.user
                        note_form_obj.created_date = time()
                        edit_form_obj.status = old_status_enquiry
                        # edit_form_obj.save()
                        
                    elif status_update == '13':
                        edit_form_obj.status = 8
                        edit_form_obj.main_customer_id = int(assigned_customer)
                        
                        if quotation:
                            quotation.quotation_customer_id = int(assigned_customer)
                            quotation.save()
                        
                        # version.status = 13
                        send_veriosn_obj = Estimations.objects.get(pk=send_version)
                        send_estimation1 = EstimationVersions.objects.get(pk=send_veriosn_obj.version.id)
                        send_estimation1.status = 13
                        send_estimation1.save()
                        
                        # version.save()
                        note_form_obj.note_status = 14
                        note_form_obj.estimation = estimation
                        note_form_obj.created_by = request.user
                        note_form_obj.created_date = time()
                    else:
                        version.status = 11
                        edit_form_obj.status = 6
                        # edit_form_obj.save()
                        note_form_obj.note_status = 11
                        note_form_obj.created_by = request.user
                        note_form_obj.created_date = time()
                        note_form_obj.estimation = estimation
                        version.save()

                    note_form_obj.management = True
                    note_form_obj.save()
                elif not note_form:
                    edit_form_obj.status = old_status_enquiry
                    
            
            if enqu_status_update == '4' or enqu_status_update == '7':
                discontnued_obj = discontnue_form.save(commit=False)
                if discontnued_obj.discontinue_note:
                    discontnued_obj.created_by = request.user
                    discontnued_obj.enquiry = enq_obj
                    estimations = Estimations.objects.filter(enquiry=enq_obj).order_by('id')
                    
                    for estimation in estimations:
                        versions = EstimationVersions.objects.filter(pk=estimation.version.id).order_by('id')
                        for version in versions:
                            version.status = 7 if edit_form_obj.status == 4 else 5
                            version.save()
                            
                    discontnued_obj.save()
                    
            
            elif enqu_status_update == '1':
                estimations = Estimations.objects.filter(enquiry=enq_obj).order_by('id')
                for estimation in estimations:
                    versions = EstimationVersions.objects.filter(pk=estimation.version.id).order_by('id')
                    for version in versions:
                        version.status = 1
                        version.save()
                        
            elif (enqu_status_update == '0' or enqu_status_update is None) and enq_obj.status != 8:
                edit_form_obj.status = old_status_enquiry
            edit_form_obj.save()
            
            
            if enqu_status_update == '7':
                enq_obj.other_notes = discontnued_obj.discontinue_note
                enq_obj.status = 7
                enq_obj.save()
              
            enquiry_logger(
                            enquiry=enq_obj, 
                            message='Enquiry Updated',
                            action=2, 
                            user=request.user
                           )
            messages.success(request, "Enquiry Updated Successfully")

            
            if request.POST['enquiry_type'] == '1':
                edit_form_obj.main_customer = edit_form_obj.customers.first()
                edit_form_obj.save()

                folder_path = os.path.join(
                        MEDIA_ROOT, 'Quotations', edit_form_obj.enquiry_id, 
                        edit_form_obj.main_customer.name, 'Original'
                    )
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                
            else:
                for customer in edit_form_obj.customers.all():
                    folder_path = os.path.join(
                            MEDIA_ROOT, 'Quotations', edit_form_obj.enquiry_id, 
                            customer.name, 'Original'
                        )
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                    
        else:
            print("errorss==>", edit_form.errors)
            print("discontnue_form==>", discontnue_form.errors)
            messages.error(request, edit_form.errors)
        return redirect('list_add_enquiries')
    context = {
        "edit_form": edit_form,
        "enq_obj": enq_obj,
        "discontnue_form": discontnue_form,
        "disc_historys": disc_historys,
        "note_form": note_form,
        "projects_obj": projects_obj,
        # "has_project": has_project,
        # "projec_obj": projec_obj,
        "send_versions": send_versions,
    }
    return render(request, 'Enquiries/edit_enquiry.html', context)


@login_required(login_url='signin')
@permission_required(['enquiries.delete_enquiries'], login_url='permission_not_allowed')
def delete_enquiry(request, pk):
    """
    This function deletes an enquiry object and its associated folder if it exists, and returns a
    success or error message.
    
    """
    enq_obj = Enquiries.objects.get(pk=pk)
    try:
        folder_path = os.path.join(MEDIA_ROOT, 'Quotations', enq_obj.enquiry_id)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print("Folder deleted successfully!")
        else:
            print("Folder does not exist!")
            
        Estimation_GeneralNotes.objects.filter(estimations__enquiry=enq_obj).delete()
        enq_obj.delete()
        messages.success(request, "Successfully deleted enquiry.")
    except Exception as e:
        print("EXCE==>", e)
        messages.error(
            request, "Unable to delete the data. Already used in application.")
        print("Delete is not possible.")
    return redirect('list_add_enquiries')
   
    
@login_required(login_url='signin')
@permission_required(['enquiries.view_enquiries'], login_url='permission_not_allowed')
def enquiry_profile(request, pk, version=None):
    """
    This function retrieves and displays information related to an enquiry, including its versions,
    product, project specifications, quotations, and notes.
    """
    enquiry_obj = Enquiries.objects.get(pk=pk)
    remaining_days = enquiry_obj.get_days_remaining_and_delay()
    if version:
        versions = Estimations.objects.get(pk=version)
        product = EstimationMainProduct.objects.filter(
            building__estimation=versions.id, disabled=False).order_by('id')
        project_specifications = EstimationProjectSpecifications.objects.filter(
            estimations=versions)
        quotations = Quotations.objects.filter(
            estimations__enquiry=enquiry_obj).order_by('id')
        specification_obj = EnquirySpecifications.objects.filter(
            estimation=versions).order_by('categories__category')
    else:
        versions = Estimations.objects.filter(enquiry=enquiry_obj).first()
        project_specifications = EstimationProjectSpecifications.objects.filter(
            estimations=versions)
        product = None
        quotations = None
        specification_obj = None

    estim_versions = Estimations.objects.filter(
        enquiry=enquiry_obj).order_by('id')
    temp_estimations = Temp_Estimations.objects.filter(
        enquiry=enquiry_obj).order_by('id')
    notes_obj = EstimationNotes.objects.filter(
        estimation=versions).order_by('id')

    try:
        general_note = Estimation_GeneralNotes.objects.get(estimations=version)
    except Exception:
        general_note = None

    path = str(enquiry_obj.enquiry_id)
    parent_path = 'Quotations'
    ai_rating_label = estimation_ai_rating(enquiry_obj.id)

    context = {
        "title": f'{PROJECT_NAME}| Enquiry Profile',
        "enquiry_obj": enquiry_obj,
        "version": versions,
        "quotations": quotations,
        "product": product,
        "specification_obj": specification_obj,
        "estim_versions": estim_versions,
        "temp_estimations": temp_estimations,
        "notes_obj": notes_obj,
        "remaining_days": remaining_days,
        'folder_path': path,
        'parent_path': parent_path,
        'project_specifications': project_specifications,
        'general_note': general_note,
        'tinymc_api': TINYMC_API,
        'ai_rating_label': ai_rating_label,
    }
    return render(request, "Enquiries/enquiry_profile_pages/enquiry_profile.html", context)


@login_required(login_url='signin')
@permission_required(['enquiries.view_enquiries'], login_url='permission_not_allowed')
def tem_enquiry_profile(request, pk, version=None):
    """
    This function retrieves and displays information related to an enquiry, including its versions,
    quotations, products, specifications, and general notes.
    """
    
    enquiry_obj = Enquiries.objects.get(pk=pk)
    if version:
        versions = Temp_Estimations.objects.get(pk=version)
        product = Temp_EstimationMainProduct.objects.filter(
            building__estimation=versions.id, disabled=False).order_by('id')
        project_specifications = Temp_EstimationProjectSpecifications.objects.filter(estimations=versions)
        
    else:
        versions = Temp_Estimations.objects.filter(enquiry=enquiry_obj).first()
        product = None
        project_specifications = Temp_EstimationProjectSpecifications.objects.filter(estimations=versions)
    quotations = Temp_Quotations.objects.filter(estimations_id=versions.id).order_by('id')
    specification_obj = Temp_EnquirySpecifications.objects.filter(
        estimation_id=versions.id).order_by('categories__category')
    
    estim_versions = Estimations.objects.filter(enquiry=enquiry_obj).order_by('id')
    
    try:
        general_note = Temp_Estimation_GeneralNotes.objects.get(estimations=version)
    except:
        general_note = None
        
    path = str(enquiry_obj.enquiry_id)
    parent_path = 'Quotations'
    ai_rating_label = estimation_ai_rating(enquiry_obj.id)
    
    context = {
        "title": f'{PROJECT_NAME} | Enquiry Profile',
        "enquiry_obj": enquiry_obj,
        "version": versions,
        "quotations": quotations,
        "product": product,
        "specification_obj": specification_obj,
        "estim_versions": estim_versions,
        "temp_estimations": None,
        'folder_path': path,
        'parent_path': parent_path,
        'project_specifications': project_specifications,
        'general_note': general_note,
        'tinymc_api': TINYMC_API,
        'ai_rating_label': ai_rating_label,
    }
    return render(request, "Enquiries/enquiry_profile_pages/enquiry_profile.html", context)


@login_required(login_url='signin')
@permission_required(['estimations.change_mainproductaluminium', 'estimations.change_mainproductglass', 'estimations.change_estimationmainproduct'], login_url='permission_not_allowed')
def enquiry_import(request, pk):
    enquiry_obj = Enquiries.objects.get(pk=pk)
    enquiry_objs = Enquiries.objects.exclude(status=0, pk=pk)
    
    if request.method == 'POST':
        selected_enquiry = request.POST.get('selected_enquiry')
        selected_revision = request.POST.get('selected_revision')
        
        if selected_enquiry and selected_revision:
            selected_enquiry_obj = Enquiries.objects.get(pk=selected_enquiry)
            enquiry_obj.labour_percentage=selected_enquiry_obj.labour_percentage
            enquiry_obj.overhead_percentage=selected_enquiry_obj.overhead_percentage
            enquiry_obj.additional_and_labour=selected_enquiry_obj.additional_and_labour
            enquiry_obj.pricing=selected_enquiry_obj.pricing
            enquiry_obj.pricing_type_select=selected_enquiry_obj.pricing_type_select
            enquiry_obj.price_per_kg=selected_enquiry_obj.price_per_kg
            enquiry_obj.price_per_kg_markup=selected_enquiry_obj.price_per_kg_markup
            enquiry_obj.enquiry_active_status=selected_enquiry_obj.enquiry_active_status
            enquiry_obj.sealant_pricing=selected_enquiry_obj.sealant_pricing
            enquiry_obj.structural_price=selected_enquiry_obj.structural_price
            enquiry_obj.weather_price=selected_enquiry_obj.weather_price
            enquiry_obj.surface_finish_price=selected_enquiry_obj.surface_finish_price
            enquiry_obj.rating=selected_enquiry_obj.rating
            enquiry_obj.active_hrs=selected_enquiry_obj.active_hrs
            enquiry_obj.status=selected_enquiry_obj.status
            enquiry_obj.last_modified_date = time()
            enquiry_obj.last_modified_by = request.user
            enquiry_obj.save()

            main_version_obj = EstimationManiVersion(
                version_text='1.0',
            )
            main_version_obj.save()
            version_obj = EstimationVersions(
                            created_by=request.user,
                            version=0,
                            status=9,
                            main_version=main_version_obj,
                            )
            version_obj.save()
            
            estimation = Estimations.objects.get(pk=selected_revision)
            new_estimation_obj = Estimations(
                created_by=request.user,
                enquiry=enquiry_obj,
                version=version_obj,
            )
            new_estimation_obj.save()
            
            try:
                price_summary = Pricing_Summary.objects.get(estimation=estimation.id)
            except:
                price_summary = None
            if price_summary:
                temp_pricing_sumary = Pricing_Summary(
                                            estimation=new_estimation_obj,
                                            scope_of_work=price_summary.scope_of_work,
                                            product_summary=price_summary.product_summary,
                                            weightage_summary=price_summary.weightage_summary,
                                            material_summary=price_summary.material_summary,
                                            pricing_review_summary=price_summary.pricing_review_summary,
                                            quotation=0.00,
                                        )
                temp_pricing_sumary.save()
                
            estimation_project_spec = EstimationProjectSpecifications.objects.filter(estimations=estimation)
            for estimation_spec in estimation_project_spec:
                temp_estimation_spec = EstimationProjectSpecifications(
                    specification_header=estimation_spec.specification_header, 
                    estimations=new_estimation_obj, 
                    specification=estimation_spec.specification)
                temp_estimation_spec.save()
                
            estimation.temp_last_child = new_estimation_obj
            estimation.save()
            specification_obj = EnquirySpecifications.objects.filter(
                estimation=estimation).order_by('id')
            
            try:
                general_note = Estimation_GeneralNotes.objects.get(estimations=estimation)
                temp_general = Estimation_GeneralNotes(
                    estimations = new_estimation_obj,
                    general_notes = general_note.general_notes,
                    created_by = general_note.created_by,
                )
                temp_general.save()
            except Exception as e:
                general_note = None
                
            for spec in specification_obj:
                temp_specification = EnquirySpecifications(
                    created_by=spec.created_by,
                    estimation=new_estimation_obj,
                    identifier=spec.identifier,
                    categories=spec.categories,
                    aluminium_products=spec.aluminium_products,
                    aluminium_system=spec.aluminium_system,
                    aluminium_specification=spec.aluminium_specification,
                    aluminium_series=spec.aluminium_series,
                    panel_category=spec.panel_category,
                    panel_brand=spec.panel_brand,
                    panel_series=spec.panel_series,
                    panel_specification=spec.panel_specification,
                    surface_finish=spec.surface_finish,
                    specification_description=spec.specification_description,
                    panel_product=spec.panel_product,
                    specification_type=spec.specification_type,
                    minimum_price=spec.minimum_price,
                )
                temp_specification.save()
                
                try:
                    product_complance = EstimationProductComplaints.objects.get(
                        estimation=estimation, specification=spec.id)
                except Exception as e:
                    product_complance = None
                
                try:
                    temp_spc = EnquirySpecifications.objects.get(
                        estimation=new_estimation_obj, identifier=spec.identifier)
                except Exception as e:
                    temp_spc = None
                if product_complance:
                    temp_compnace = EstimationProductComplaints(
                        estimation=new_estimation_obj,
                        specification=temp_spc,
                        is_aluminium_complaint=product_complance.is_aluminium_complaint,
                        aluminium_complaint=product_complance.aluminium_complaint,
                        is_panel_complaint=product_complance.is_panel_complaint,
                        panel_complaint=product_complance.panel_complaint,
                        is_surface_finish_complaint=product_complance.is_surface_finish_complaint,
                        surface_finish_complaint=product_complance.surface_finish_complaint,
                    )
                    temp_compnace.save()

            buildings = EstimationBuildings.objects.filter(
                estimation=estimation).order_by('id')

            for build in buildings:
                temp_build = EstimationBuildings(
                    created_by=build.created_by, 
                    estimation=new_estimation_obj, 
                    building_name=build.building_name, 
                    no_typical_buildings=build.no_typical_buildings, 
                    typical_buildings_enabled=build.typical_buildings_enabled
                    )
                temp_build.save()
                main_product = EstimationMainProduct.objects.filter(
                    building=build, product_type=1, disabled=False).order_by('id', 'associated_key')
                prev_main_id = None
                
                for product in main_product:
                    
                    if not product.associated_key:
                        if product.product_type == 1:
                            try:
                                temp_product = EstimationMainProduct(
                                    building=temp_build,
                                    created_by=product.created_by,
                                    category=product.category,
                                    product=product.product,
                                    product_type=product.product_type,
                                    panel_product=product.panel_product,
                                    brand=product.brand,
                                    series=product.series,
                                    panel_brand=product.panel_brand,
                                    panel_series=product.panel_series,
                                    uom=product.uom,
                                    accessories=product.accessories,
                                    is_accessory=product.is_accessory,
                                    accessory_quantity=product.accessory_quantity,
                                    tolerance_type=product.tolerance_type,
                                    tolerance=product.tolerance,
                                    is_tolerance=product.is_tolerance,
                                    total_addon_cost=product.total_addon_cost,
                                    is_sourced=product.is_sourced,
                                    supplier=product.supplier,
                                    boq_number=product.boq_number,
                                    enable_addons=product.enable_addons,
                                    accessory_total=product.accessory_total,
                                    is_display_data=product.is_display_data,
                                    display_width=product.display_width,
                                    display_height=product.display_height,
                                    display_area=product.display_area,
                                    display_quantity=product.display_quantity,
                                    display_product_name=product.display_product_name,
                                    display_total_area=product.display_total_area,
                                    deduction_price=product.deduction_price,
                                    deduction_type=product.deduction_type,
                                    deduction_method=product.deduction_method,
                                    after_deduction_price=product.after_deduction_price,
                                    total_associated_area=product.total_associated_area,
                                    deducted_area=product.deducted_area,
                                    product_unit_price=product.product_unit_price,
                                    product_sqm_price=product.product_sqm_price,
                                    product_base_rate=product.product_base_rate,
                                    have_merge=product.have_merge,
                                    merge_price=product.merge_price,
                                    # associated_key=product.associated_key,
                                    product_sqm_price_without_addon=product.product_sqm_price_without_addon,
                                    hide_dimension=product.hide_dimension,
                                    minimum_price=product.minimum_price,
                                    product_index=product.product_index,
                                    disabled=product.disabled,
                                )
                                temp_product.save()
                                temp_product.main_product = temp_product
                                associated_key = associated_key_gen(product.building.estimation.enquiry.title)
                                temp_product.associated_key = str(associated_key)+str(temp_product.id)
                                temp_product.save()
                                prev_main_id = temp_product
                            except Exception as e:
                                print('EXCEPTIONS__1==>', e)
                        else:
                            print('error_1')
                        if product.product_type == 2:
                            try:
                                temp_product = EstimationMainProduct(
                                    building=temp_build,
                                    created_by=product.created_by,
                                    category=product.category,
                                    product=product.product,
                                    product_type=product.product_type,
                                    panel_product=product.panel_product,
                                    main_product=prev_main_id,
                                    brand=product.brand,
                                    series=product.series,
                                    panel_brand=product.panel_brand,
                                    panel_series=product.panel_series,
                                    uom=product.uom,
                                    accessories=product.accessories,
                                    is_accessory=product.is_accessory,
                                    is_tolerance=product.is_tolerance,
                                    tolerance_type=product.tolerance_type,
                                    tolerance=product.tolerance,
                                    total_addon_cost=product.total_addon_cost,
                                    is_sourced=product.is_sourced,
                                    supplier=product.supplier,
                                    boq_number=product.boq_number,
                                    enable_addons=product.enable_addons,
                                    accessory_total=product.accessory_total,
                                    is_display_data=product.is_display_data,
                                    display_width=product.display_width,
                                    display_product_name=product.display_product_name,
                                    display_height=product.display_height,
                                    display_area=product.display_area,
                                    display_quantity=product.display_quantity,
                                    display_total_area=product.display_total_area,
                                    deduction_price=product.deduction_price,
                                    deduction_type=product.deduction_type,
                                    deduction_method=product.deduction_method,
                                    after_deduction_price=product.after_deduction_price,
                                    total_associated_area=product.total_associated_area,
                                    
                                    deducted_area=product.deducted_area,
                                    product_unit_price=product.product_unit_price,
                                    product_sqm_price=product.product_sqm_price,
                                    product_base_rate=product.product_base_rate,
                                    # associated_key=product.associated_key,
                                    have_merge=product.have_merge,
                                    merge_price=product.merge_price,
                                    product_sqm_price_without_addon=product.product_sqm_price_without_addon,
                                    hide_dimension=product.hide_dimension,
                                    minimum_price=product.minimum_price,
                                    product_index=product.product_index,
                                    disabled=product.disabled,
                                    
                                )
                                temp_product.save()
                                associated_key = associated_key_gen(product.building.estimation.enquiry.title)
                                temp_product.associated_key = str(associated_key)+str(temp_product.id)
                                temp_product.save()

                            except Exception as e:
                                print("EXCEPTIONS__2==>", e)
                        else:
                            print('error_2')
                    else:
                        if product.product_type == 1:
                            # print("product==>", product.id)
                            associated_products = check_associated(product)
                            
                            try:
                                temp_product = EstimationMainProduct(
                                    building=temp_build,
                                    created_by=product.created_by,
                                    category=product.category,
                                    product=product.product,
                                    product_type=product.product_type,
                                    panel_product=product.panel_product,
                                    brand=product.brand,
                                    series=product.series,
                                    panel_brand=product.panel_brand,
                                    panel_series=product.panel_series,
                                    uom=product.uom,
                                    accessories=product.accessories,
                                    is_accessory=product.is_accessory,
                                    accessory_quantity=product.accessory_quantity,
                                    tolerance_type=product.tolerance_type,
                                    tolerance=product.tolerance,
                                    is_tolerance=product.is_tolerance,
                                    total_addon_cost=product.total_addon_cost,
                                    is_sourced=product.is_sourced,
                                    supplier=product.supplier,
                                    boq_number=product.boq_number,
                                    enable_addons=product.enable_addons,
                                    accessory_total=product.accessory_total,
                                    is_display_data=product.is_display_data,
                                    display_product_name=product.display_product_name,
                                    display_width=product.display_width,
                                    display_height=product.display_height,
                                    display_area=product.display_area,
                                    display_quantity=product.display_quantity,
                                    display_total_area=product.display_total_area,
                                    deduction_price=product.deduction_price,
                                    deduction_type=product.deduction_type,
                                    deduction_method=product.deduction_method,
                                    after_deduction_price=product.after_deduction_price,
                                    total_associated_area=product.total_associated_area,
                                    deducted_area=product.deducted_area,
                                    product_unit_price=product.product_unit_price,
                                    product_sqm_price=product.product_sqm_price,
                                    product_base_rate=product.product_base_rate,
                                    have_merge=product.have_merge,
                                    merge_price=product.merge_price,
                                    # associated_key=product.associated_key,
                                    product_sqm_price_without_addon=product.product_sqm_price_without_addon,
                                    hide_dimension=product.hide_dimension,
                                    minimum_price=product.minimum_price,
                                    product_index=product.product_index,
                                    
                                )
                                temp_product.save()
                                temp_product.main_product = temp_product
                                associated_key = associated_key_gen(product.building.estimation.enquiry.title)
                                temp_product.associated_key = str(associated_key)+str(temp_product.id)
                                temp_product.save()
                                prev_main_id = temp_product
                            except Exception as e:
                                print('EXCEPTIONS__1==>', e)
                            
                            if associated_products:
                                for associated_product in associated_products:
                                    assoc = EstimationMainProduct.objects.get(pk=associated_product.associated_product.id)
                                    
                                    try:
                                        temp_product1 = EstimationMainProduct(
                                            building=temp_build,
                                            created_by=assoc.created_by,
                                            category=assoc.category,
                                            product=assoc.product,
                                            product_type=assoc.product_type,
                                            panel_product=assoc.panel_product,
                                            main_product=prev_main_id,
                                            brand=assoc.brand,
                                            series=assoc.series,
                                            panel_brand=assoc.panel_brand,
                                            panel_series=assoc.panel_series,
                                            uom=assoc.uom,
                                            accessories=assoc.accessories,
                                            is_accessory=assoc.is_accessory,
                                            is_tolerance=assoc.is_tolerance,
                                            tolerance_type=assoc.tolerance_type,
                                            tolerance=assoc.tolerance,
                                            total_addon_cost=assoc.total_addon_cost,
                                            is_sourced=assoc.is_sourced,
                                            supplier=assoc.supplier,
                                            boq_number=assoc.boq_number,
                                            enable_addons=assoc.enable_addons,
                                            accessory_total=assoc.accessory_total,
                                            is_display_data=assoc.is_display_data,
                                            display_width=assoc.display_width,
                                            display_product_name=assoc.display_product_name,
                                            display_height=assoc.display_height,
                                            display_area=assoc.display_area,
                                            display_quantity=assoc.display_quantity,
                                            display_total_area=assoc.display_total_area,
                                            deduction_price=assoc.deduction_price,
                                            deduction_type=assoc.deduction_type,
                                            deduction_method=assoc.deduction_method,
                                            after_deduction_price=assoc.after_deduction_price,
                                            total_associated_area=assoc.total_associated_area,
                                            
                                            deducted_area=assoc.deducted_area,
                                            product_unit_price=assoc.product_unit_price,
                                            product_sqm_price=assoc.product_sqm_price,
                                            product_base_rate=assoc.product_base_rate,
                                            # associated_key=assoc.associated_key,
                                            have_merge=assoc.have_merge,
                                            merge_price=assoc.merge_price,
                                            product_sqm_price_without_addon=assoc.product_sqm_price_without_addon,
                                            hide_dimension=assoc.hide_dimension,
                                            minimum_price=assoc.minimum_price,
                                            product_index=product.product_index,
                                            disabled=product.disabled,
                                            
                                        )
                                        temp_product1.save()
                                        associated_key = associated_key_gen(assoc.building.estimation.enquiry.title)
                                        temp_product1.associated_key = str(associated_key)+str(temp_product1.id)
                                        temp_product1.save()

                                    except Exception as e:
                                        print("EXCEPTIONS__2==>", e)
                                    
                                    # print('assoc==>', assoc)
                                    
                                    enquiry_generate_product_data(assoc, temp_product1)
                                    
                    enquiry_generate_product_data(product, temp_product)
              
        estimation_obj = Estimations.objects.filter(enquiry=enquiry_obj).first()
        
        if estimation_obj:
            return redirect('enquiry_profile', pk=enquiry_obj.id, version=estimation_obj.id)      
        else:
            print('No version')
            return redirect('enquiry_profile', pk=enquiry_obj.id)      
            
    
    context = {
        "enquiry_obj": enquiry_obj,
        "enquiry_objs": enquiry_objs,
    }
    return render(request, "Enquiries/dropdowns/enquiry_import_modal.html", context)


@login_required(login_url='signin')
def list_revisions(request, pk):
    estimations_objs = Estimations.objects.filter(enquiry=pk)

    context = {
        "estimations_objs": estimations_objs,
    }
    return render(request, "Enquiries/dropdowns/revision_lists.html", context)


@login_required(login_url='signin')
def update_product_category_percentage(request, pk):
    """
    The function `update_product_category_percentage` updates the category percentage for a product in
    an estimation.
    """
    main_product = EstimationMainProduct.objects.get(pk=pk)
    aluminium = MainProductAluminium.objects.get(estimation_product=main_product)
    try:
        glass = MainProductGlass.objects.get(estimation_product=main_product, glass_primary=True)
        second_glass_obj = MainProductGlass.objects.filter(estimation_product=pk, glass_primary=False).order_by('id')
    except Exception as e:
        glass = None
        second_glass_obj = None
    labour_and_overhead = PricingOption.objects.get(estimation_product=main_product)
    pricing_master = AdditionalandLabourPriceMaster.objects.get(pk=main_product.building.estimation.enquiry.additional_and_labour.id)
    addons = MainProductAddonCost.objects.filter(estimation_product=main_product).order_by('id')
    try:
        silicon = MainProductSilicon.objects.get(estimation_product=main_product)
    except Exception as e:
        silicon = None

    main_form = UpdateLabourAndOverhead(instance=labour_and_overhead)
    tolerance_form = UpdateTolerance(instance=main_product)
    aluminium_form = UpdateAluminiumPercentage(instance=aluminium)

    try:
        glass_form = UpdateGlassPercentage(instance=glass)
    except Exception as e:
        glass_form = None

    if request.method == 'POST':
        return process_post_request(
                        request, 
                        main_product, 
                        labour_and_overhead, 
                        pricing_master, 
                        main_form, 
                        tolerance_form, 
                        aluminium_form, 
                        glass_form, 
                        aluminium, 
                        glass, 
                        second_glass_obj, 
                        addons, 
                        silicon
                    )
    context = {
        "main_product": main_product,
        "aluminium": aluminium,
        "glass": glass,
        "main_form": main_form,
        "aluminium_form": aluminium_form,
        "glass_form": glass_form,
        "addons": addons,
        "second_glass_obj": second_glass_obj,
        "silicon": silicon,
        "tolerance_form": tolerance_form,
    }
    return render(request, "Enquiries/category_summary_update.html", context)


def process_post_request(
                request, 
                main_product, 
                labour_and_overhead, 
                pricing_master, 
                main_form, 
                tolerance_form, 
                aluminium_form, 
                glass_form, 
                aluminium, 
                glass, 
                second_glass_obj, 
                addons, 
                silicon
                ):
    """
    The function processes a POST request and updates various forms and models based on the request
    data.
    """
    main_form = UpdateLabourAndOverhead(request.POST, instance=labour_and_overhead)
    tolerance_form = UpdateTolerance(request.POST, instance=main_product)
    aluminium_form = UpdateAluminiumPercentage(request.POST, instance=aluminium)
    alumini_final = request.POST.get('alumini_quoted')
    glass_final = request.POST.get('glass_quoted')
    try:
        glass_form = UpdateGlassPercentage(request.POST, instance=glass)
    except Exception as e:
        glass_form = None

    if aluminium_form.is_valid() and glass_form.is_valid() and main_form.is_valid() and tolerance_form.is_valid():
        return update_percentage_values(request, main_product, pricing_master, main_form, tolerance_form, aluminium_form, glass_form, aluminium, glass, second_glass_obj, addons, silicon, alumini_final, glass_final)
    messages.error(request, aluminium_form.errors, glass_form.errors)
    print('errors==>', main_form.errors, aluminium_form.errors, glass_form.errors, tolerance_form.errors)

    return redirect('product_category_summary', pk=main_product.building.estimation.id)


def update_percentage_values(
                                request, 
                                main_product, 
                                pricing_master, 
                                main_form, 
                                tolerance_form, 
                                aluminium_form, 
                                glass_form, 
                                aluminium, 
                                glass, 
                                second_glass_obj, 
                                addons, 
                                silicon, 
                                alumini_final, 
                                glass_final
                            ):
    """
    The function `update_percentage_values` updates various percentage values and saves the
    corresponding objects in the database.
    
    """
    if main_form.cleaned_data['overhead_perce'] >= pricing_master.minimum_overhead and \
        main_form.cleaned_data['labour_perce'] >= pricing_master.minimum_labour:
        main_form.save()
    else:
        if main_form.cleaned_data['overhead_perce'] < pricing_master.minimum_overhead:
            messages.error(
                request,
                f"Overhead Percentage not below {str(pricing_master.minimum_overhead)}%",
            )
        if main_form.cleaned_data['labour_perce'] < pricing_master.minimum_labour:
            messages.error(
                request,
                f"Labour Percentage not below {str(pricing_master.minimum_labour)}%",
            )

    if main_product.tolerance_type == 1:
        if int(tolerance_form.cleaned_data['tolerance']) < 0 or int(tolerance_form.cleaned_data['tolerance']) > 100:
            messages.error(request, "Tolerance Percentage not below 0 or greater than 100.")
        else:
            tolerance_obj = tolerance_form.save(commit=False)
            tolerance_obj.last_modified_by = request.user
            tolerance_obj.last_modified_date = time()
            tolerance_obj.save()
    else:
        tolerance_obj = tolerance_form.save(commit=False)
        tolerance_obj.last_modified_by = request.user
        tolerance_obj.last_modified_date = time()
        tolerance_obj.save()

    aluminium_obj = aluminium_form.save(commit=False)
    if alumini_final:
        aluminium_obj.al_quoted_price = float(alumini_final)
        aluminium_obj.last_modified_by = request.user
        aluminium_obj.last_modified_date = time()
    aluminium_obj.save()

    glass_obj = glass_form.save(commit=False)
    if glass_final:
        glass_obj.glass_quoted_price = float(glass_final)
        glass_obj.last_modified_by = request.user
        glass_obj.last_modified_date = time()
    else:
        print("NOT IN GLASS")
    glass_obj.save()

    if second_glass_obj:
        for second_glass in second_glass_obj:
            sec_glass_markup = request.POST.get(
                f'glass_markup_percentage_{str(second_glass.id)}'
            )
            sec_glass_final = request.POST.get('sec_glass_final_' + str(second_glass.id))
            if sec_glass_final:
                second_glass.glass_markup_percentage = float(sec_glass_markup)
                second_glass.glass_quoted_price = float(sec_glass_final)
                second_glass.last_modified_by = request.user
                second_glass.last_modified_date = time()
                second_glass.save()

    message = main_product.product.product_name + ' Update markups/Overhead/Labour Percentage in Original.' \
        if main_product.product else str(main_product.panel_product.product_name) + \
            ' Update markups/Overhead/Labour Percentage in Original.' if main_product.building.estimation.version.version == '0' \
        else main_product.product.product_name + ' Update markups/Overhead/Labour Percentage in Revision ' \
        + str(main_product.building.estimation.version) if main_product.product else \
        str(main_product.panel_product.product_name) + ' Update markups/Overhead/Labour Percentage in Revision ' \
        + str(main_product.building.estimation.version)
    enquiry_logger(enquiry=main_product.building.estimation.enquiry, message=message, action=2, user=request.user)
    messages.success(request, "Updated Successfully")

    return redirect('product_category_summary', pk=main_product.building.estimation.id)


@login_required(login_url='signin')
@permission_required(['estimations.change_estimationmainproduct'], login_url='permission_not_allowed')
def temp_update_product_category_percentage(request, pk):
    """
    The function `temp_update_product_category_percentage` updates the percentage values for various
    categories of a product in a temporary estimation.
    """
    main_product = Temp_EstimationMainProduct.objects.get(pk=pk)
    aluminium = Temp_MainProductAluminium.objects.get(
        estimation_product=main_product)
    try:
        glass = Temp_MainProductGlass.objects.get(
            estimation_product=main_product, glass_primary=True)
        second_glass_obj = Temp_MainProductGlass.objects.filter(
            estimation_product=pk, glass_primary=False).order_by('id')
    except Exception as e:
        glass = None
        second_glass_obj = None

    labour_and_overhead = Temp_PricingOption.objects.get(
        estimation_product=main_product)
    pricing_master = AdditionalandLabourPriceMaster.objects.get(
        pk=main_product.building.estimation.enquiry.additional_and_labour.id)
    addons = Temp_MainProductAddonCost.objects.filter(
        estimation_product=main_product).order_by('id')
    try:
        silicon = Temp_MainProductSilicon.objects.get(
            estimation_product=main_product)
    except Exception as e:
        silicon = None

    main_form = TempUpdateLabourAndOverhead(instance=labour_and_overhead)
    tolerance_form = TempUpdateTolerance(instance=main_product)

    aluminium_form = TempUpdateAluminiumPercentage(instance=aluminium)

    try:
        glass_form = TempUpdateGlassPercentage(instance=glass)
    except Exception as e:
        glass_form = None

    if request.method == 'POST':
        main_form = UpdateLabourAndOverhead(
            request.POST, instance=labour_and_overhead)
        tolerance_form = UpdateTolerance(request.POST, instance=main_product)
        aluminium_form = UpdateAluminiumPercentage(
            request.POST, instance=aluminium)
        alumini_final = request.POST.get('alumini_quoted')
        glass_final = request.POST.get('glass_quoted')
        try:
            glass_form = TempUpdateGlassPercentage(
                request.POST, instance=glass)
        except Exception as e:
            glass_form = None

        if aluminium_form.is_valid() and glass_form.is_valid() and main_form.is_valid() and tolerance_form.is_valid():
            if (main_form.cleaned_data['overhead_perce'] >= pricing_master.minimum_overhead) and (main_form.cleaned_data['labour_perce'] >= pricing_master.minimum_labour):
                main_form.save()
            else:
                if main_form.cleaned_data['overhead_perce'] < pricing_master.minimum_overhead:
                    messages.error(request, "Overhead Percentage not below " +
                                   str(pricing_master.minimum_overhead) + "%")

                if main_form.cleaned_data['labour_perce'] < pricing_master.minimum_labour:
                    messages.error(request, "Labour Percentage not below " +
                                   str(pricing_master.minimum_labour) + "%")

            if main_product.tolerance_type == 1:
                if int(tolerance_form.cleaned_data['tolerance']) < 0 or int(tolerance_form.cleaned_data['tolerance']) > 100:
                    messages.error(
                        request, "Tolerance Percentage not below 0 or grater than 100. ")
                else:
                    tolerance_obj = tolerance_form.save(commit=False)
                    tolerance_obj.last_modified_by = request.user
                    tolerance_obj.last_modified_date = time()
                    tolerance_obj.save()
            else:
                tolerance_obj = tolerance_form.save(commit=False)
                tolerance_obj.last_modified_by = request.user
                tolerance_obj.last_modified_date = time()
                tolerance_obj.save()

            aluminium_obj = aluminium_form.save(commit=False)
            if alumini_final:
                aluminium_obj.al_quoted_price = float(alumini_final)
                aluminium_obj.last_modified_by = request.user
                aluminium_obj.last_modified_date = time()
            aluminium_obj.save()

            glass_obj = glass_form.save(commit=False)
            if glass_final:
                glass_obj.glass_quoted_price = float(glass_final)
                glass_obj.last_modified_by = request.user
                glass_obj.last_modified_date = time()

            else:
                print("NOT IN GLASS")

            glass_obj.save()
            for second_glass in second_glass_obj:
                sec_glass_markup = request.POST.get(
                    'glass_markup_percentage_'+str(second_glass.id))
                sec_glass_final = request.POST.get(
                    'sec_glass_final_'+str(second_glass.id))
                second_glass.glass_markup_percentage = float(sec_glass_markup)
                second_glass.glass_quoted_price = float(sec_glass_final)
                second_glass.last_modified_by = request.uesr
                second_glass.last_modified_date = time()
                second_glass.save()

            main_form.save()
            message = main_product.product.product_name+' Update markups/Overhead/Labour Percentage in Original (Cart).' \
                if main_product.product else str(main_product.panel_product.product_name)+\
                    ' Update markups/Overhead/Labour Percentage in Original (Cart).' if main_product.building.estimation.version.version == '0' \
                        else main_product.product.product_name+' Update markups/Overhead/Labour Percentage in Revision '\
                            +str(main_product.building.estimation.version)+'(Cart).' if main_product.product else \
                                str(main_product.panel_product.product_name)+' Update markups/Overhead/Labour Percentage in Revision '\
                                    +str(main_product.building.estimation.version)+'(Cart).'
            enquiry_logger(enquiry=main_product.building.estimation.enquiry, message= message, action=2, user=request.user)
            messages.success(request, "Updated Successfully")
        else:
            messages.error(request, aluminium_form.errors, glass_form.errors)
            print('errors==>', main_form.errors, aluminium_form.errors,
                  glass_form.errors, tolerance_form.errors)

        return redirect('temp_product_category_summary', pk=main_product.building.estimation.id)
    context = {
        "main_product": main_product,
        "aluminium": aluminium,
        "glass": glass,
        "main_form": main_form,
        "aluminium_form": aluminium_form,
        "glass_form": glass_form,
        "silicon": silicon,
        "second_glass_obj": second_glass_obj,
        "addons": addons,
        "tolerance_form": tolerance_form
    }
    return render(request, "Enquiries/category_summary_update.html", context)


@login_required(login_url='signin')
@permission_required(['enquiries.add_estimations'], login_url='permission_not_allowed')
def estimation_submit(request, pk):
    """
    This function submits an estimation note form and updates various related models.
    """
    form = CreateEstimationNotesForms()
    estimation = Estimations.objects.get(pk=pk)
    parameters = SubmittingParameters.objects.all()
    if request.method == 'POST':
        form = CreateEstimationNotesForms(request.POST)
        
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.created_by = request.user
            form_obj.user = True
            form_obj.estimation_id = pk
            form_obj.created_date = time()

            version = EstimationVersions.objects.get(pk=estimation.version.id)
            version.status = 3
            
            form_obj.note_status = 3
            version.last_modified_date = time()
            version.last_modified_by = request.user
            version.save()
            estimation.last_modified_date = time()
            estimation.last_modified_by = request.user
            estimation.save()
            enquiry = Enquiries.objects.get(pk=estimation.enquiry.id)
            enquiry.status = 9
            enquiry.save()
            form_obj.save()
            
            for parameter in parameters:
                parameter_check = request.POST.get(f'parameter_check_{parameter.id}')
                parameter_input = request.POST.get(f'parameter_{parameter.id}')
                if parameter_check == 'on' and parameter_input:
                    try:
                        parameter_obj = EstimationSubmitting_Hours.objects.get(estimation=estimation, parameter=parameter)
                        parameter_obj.time_data = str(sum_times([str(parameter_obj.time_data), f'{parameter_input}:00']))
                        parameter_obj.save()
                    except Exception as e:
                        submit_obj = EstimationSubmitting_Hours(estimation=estimation, parameter=parameter, time_data=f'{parameter_input}:00')
                        submit_obj.save()
            
            messages.success(request, "Estimation Submited Successfully")
        return redirect('estimation_quotations_list', pk=estimation.id)
    context = {
        "estimation": estimation,
        "form": form,
        "parameters": parameters,
        "check_list": [1, 2, 3]
    }
    return render(request, 'Enquiries/quotations/management_review_sumbit_model.html', context)


@login_required(login_url='signin')
@permission_required(['enquiries.add_estimations'], login_url='permission_not_allowed')
def start_estimation(request, pk):
    """
    This function starts an estimation process for a given enquiry object and creates a new version of
    the estimation.
    """
    enquiry_obj = Enquiries.objects.get(pk=pk)
    enquiry_obj.status = 2
    enquiry_obj.save()
    main_version = EstimationManiVersion(version_text='1.0')
    main_version.save()
    version = EstimationVersions(
        created_by=request.user, version='0', status=2, main_version=main_version)
    version.save()
    estimation = Estimations(created_by=request.user, enquiry=enquiry_obj)
    estimation.version = version
    estimation.save()
    enquiry_logger(enquiry=enquiry_obj,
                   message='Estimation Original Started', action=1, user=request.user)
    messages.success(request, "Estimation Started Successfully")

    return redirect('enquiry_profile', pk=pk, version=estimation.id)


@login_required(login_url='signin')
@permission_required(['enquiries.add_enquiryspecifications'], login_url='permission_not_allowed')
def add_enquiry_specifications(request, pk):
    """
    This function adds an enquiry specification and complaint form to an estimation object and saves it
    to the database.
    """
    estimation = Estimations.objects.get(pk=pk)
    form = CreateEnquirySpecificationForm(kit_id=estimation.enquiry.surface_finish_price.id)
    complaint_form = ProductComplaintsForm()
    if request.method == "POST":
        form = CreateEnquirySpecificationForm(
            request.POST, kit_id=estimation.enquiry.surface_finish_price.id)

        complaint_form = ProductComplaintsForm(request.POST)
        if form.is_valid() and complaint_form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.created_by = request.user
            form_obj.estimation = estimation
            form_obj.save()
            obj = EnquirySpecifications.objects.get(pk=form_obj.id)
            complaint_form_obj = complaint_form.save(commit=False)
            if (complaint_form_obj.is_aluminium_complaint or complaint_form_obj.is_panel_complaint or complaint_form_obj.is_surface_finish_complaint):
                complaint_form_obj.specification = form_obj
                complaint_form_obj.estimation = estimation
                complaint_form_obj.save()

            specification = EnquirySpecifications.objects.all().exclude(pk=obj.id)
            for specifi in specification:
                if (form_obj.estimation == specifi.estimation) and \
                        (form_obj.identifier == specifi.identifier):
                    obj.delete()
                    messages.error(request, 'Same Identifier Already Exist.')
                    if obj.id:
                        if (form_obj.categories == specifi.categories) and \
                                (form_obj.aluminium_products == specifi.aluminium_products) and \
                                (form_obj.aluminium_system == specifi.aluminium_system) and \
                                (form_obj.alumini_specification == specifi.alumini_specification) and \
                                (form_obj.alumini_series == specifi.alumini_series) and \
                                (form_obj.panel_category == specifi.panel_category) and \
                                (form_obj.panel_brand == specifi.panel_brand) and \
                                (form_obj.panel_series == specifi.panel_series) and \
                                (form_obj.panel_specification == specifi.panel_specification) and \
                                (form_obj.created_by == specifi.created_by):

                            obj.delete()
                            messages.error(request, 'Already Exist.')
                            break

            message = obj.identifier+" | "+obj.aluminium_products.product_name+' Specification Added in Original.' \
                if obj.aluminium_products else obj.identifier+" | "+obj.panel_specification.specifications +\
                ' Specification Added in Original.' if estimation.version.version == '0' \
                else obj.identifier+" | "+obj.aluminium_products.product_name+' Specification Added in Revision ' +\
                str(estimation.version.version) if obj.aluminium_products else obj.identifier +\
                " | "+obj.panel_specification.specifications+' Specification Added in Revision ' +\
                str(estimation.version.version)
            enquiry_logger(enquiry=estimation.enquiry,
                           message=message, action=1, user=request.user)
            messages.success(request, "Specification Added Successfully")
        else:
            messages.error(request, form.errors)
            print("errors==>", form.errors)
            print("errors==>", complaint_form.errors)
        return redirect('enquiry_profile', pk=estimation.enquiry.id, version=estimation.id)

    context = {
        "title": f'{PROJECT_NAME} | Add Enquiry Specification',
        "form": form,
        "pk": pk,
        "complaint_form": complaint_form
    }
    return render(request, "Enquiries/add_enquiry_specification_modal.html", context)



@login_required(login_url='signin')
@permission_required(['enquiries.add_enquiryspecifications'], login_url='permission_not_allowed')
def temp_add_enquiry_specifications(request, pk):
    """
    This function adds an enquiry specification to a temporary estimation object and saves it to the
    database.
    """
    estimation = Temp_Estimations.objects.get(pk=pk)
    form = TempCreateEnquirySpecificationForm(
        kit_id=estimation.enquiry.surface_finish_price.id)
    complaint_form = ProductComplaintsForm()

    if request.method == "POST":
        form = TempCreateEnquirySpecificationForm(
            request.POST, kit_id=estimation.enquiry.surface_finish_price.id)
        complaint_form = TempProductComplaintsForm(request.POST)
        if form.is_valid() and complaint_form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.created_by = request.user
            form_obj.estimation = estimation
            form_obj.save()
            obj = Temp_EnquirySpecifications.objects.get(pk=form_obj.id)
            complaint_form_obj = complaint_form.save(commit=False)
            if (complaint_form_obj.is_aluminium_complaint or complaint_form_obj.is_panel_complaint or complaint_form_obj.is_surface_finish_complaint):
                complaint_form_obj.specification = form_obj
                complaint_form_obj.estimation = estimation
                complaint_form_obj.save()

            specification = Temp_EnquirySpecifications.objects.all().exclude(pk=obj.id)
            for specifi in specification:
                if (form_obj.estimation == specifi.estimation) and \
                        (form_obj.identifier == specifi.identifier):
                    obj.delete()
                    messages.error(request, 'Same Identifier Already Exist.')
                    if obj.id:
                        if (form_obj.categories == specifi.categories) and \
                                (form_obj.aluminium_products == specifi.aluminium_products) and \
                                (form_obj.aluminium_system == specifi.aluminium_system) and \
                                (form_obj.alumini_specification == specifi.alumini_specification) and \
                                (form_obj.alumini_series == specifi.alumini_series) and \
                                (form_obj.panel_category == specifi.panel_category) and \
                                (form_obj.panel_brand == specifi.panel_brand) and \
                                (form_obj.panel_series == specifi.panel_series) and \
                                (form_obj.panel_specification == specifi.panel_specification) and \
                                (form_obj.created_by == specifi.created_by):

                            obj.delete()
                            messages.error(request, 'Already Exist.')
                            break

            message = obj.identifier+" | "+obj.aluminium_products.product_name+' Specification Added in Original (Cart).' \
                if obj.aluminium_products else obj.identifier+" | "+obj.panel_specification.specifications +\
                ' Specification Added in Original (Cart).' if estimation.version.version == '0' \
                else obj.identifier+" | "+obj.aluminium_products.product_name+' Specification Added in Revision ' +\
                str(estimation.version.version)+'(Cart).' if obj.aluminium_products else obj.identifier +\
                " | "+obj.panel_specification.specifications+' Specification Added in Revision ' +\
                str(estimation.version.version)+'(Cart).'
            enquiry_logger(enquiry=estimation.enquiry,
                           message=message, action=1, user=request.user)
            messages.success(request, "Specification Added Successfully")
        else:
            messages.error(request, form.errors)
            print("errors==>", form.errors)
            print("errors==>", complaint_form.errors)
        return redirect('tem_enquiry_profile', pk=estimation.enquiry.id, version=estimation.id)
    context = {
        "title": PROJECT_NAME + " | Add Enquiry Specification",
        "form": form,
        "pk": pk,
    }
    return render(request, "Enquiries/add_enquiry_specification_modal.html", context)



def update_infill_product(infill_product_obj, specification_obj):
    infill_product_obj.glass_specif = specification_obj.panel_specification
    specification = PanelMasterConfiguration.objects.filter(
        panel_specification=specification_obj.panel_specification).last()
    infill_product_obj.glass_base_rate = specification.price_per_sqm
    infill_product_obj.glass_markup_percentage = specification.markup_percentage
    infill_product_obj.glass_quoted_price = (
        (float(specification.markup_percentage) / 100) * float(specification.price_per_sqm) +
        float(specification.price_per_sqm)) * float(infill_product_obj.total_area_glass)
    infill_product_obj.save()


def update_product_price(product, request):
    price_data = product_unit_price(request, pk=product.id)
    product.product_unit_price = price_data['unit_price']
    product.product_base_rate = price_data['product_base_rate']

    if product.deduction_method == 1:
        if product.after_deduction_price:
            deducted_data = new_deduction_price(
                price_data['unit_price'], product.id)
            product.after_deduction_price = deducted_data['new_deducted_price']
            product.product_sqm_price_without_addon = price_data['product_sqm_price_without_addon']
            product.product_sqm_price = deducted_data['new_sqm_price']
        else:
            product.product_sqm_price_without_addon = price_data['product_sqm_price_without_addon']
            product.product_sqm_price = price_data['rp_sqm']
    else:
        product.product_sqm_price = price_data['rp_sqm']
        product.product_sqm_price_without_addon = price_data['product_sqm_price_without_addon']

    product.save()


def update_infill_specification(request, specification_obj, infill_spec, edit_obj, product):
    if edit_obj.panel_specification:
        if infill_spec != edit_obj.panel_specification.id:
            product.panel_product = specification_obj.panel_product
            infill_product_objs = MainProductGlass.objects.filter(
                estimation_product=product, glass_specif=infill_spec)

            for infill_product_obj in infill_product_objs:
                update_infill_product(infill_product_obj, specification_obj)

            update_product_price(product, request)


def update_surface_finish(request, specification_obj, product):
    alumini_obj = MainProductAluminium.objects.get(estimation_product=product)
    alumini_obj.surface_finish = specification_obj.surface_finish

    if alumini_obj.surface_finish:
        al_quoted_price = (
            (float(alumini_obj.price_per_kg) * (float(alumini_obj.al_markup)) / 100) +
            float(alumini_obj.price_per_kg)) + float(specification_obj.surface_finish.surface_finish_price)

        if alumini_obj.aluminium_pricing == 1 and alumini_obj.al_weight_per_unit:
            alumini_obj.al_quoted_price = al_quoted_price
        elif alumini_obj.aluminium_pricing == 2 and alumini_obj.pricing_unit == 3:
            alumini_obj.al_quoted_price = al_quoted_price
        elif alumini_obj.aluminium_pricing == 4:
            alumini_obj.al_quoted_price = al_quoted_price

    alumini_obj.save()
    update_product_price(product, request)

def change_in_infill(request, specification_obj, infill_spec, edit_obj, surface_finish):
    if edit_obj:
        spec_products_objs = EstimationMainProduct.objects.filter(
            specification_Identifier=specification_obj.id, disabled=False
            # panel_product=specification_obj.panel_product
            )
        for product in spec_products_objs:
            update_infill_specification(request, specification_obj, infill_spec, edit_obj, product)
            
            if edit_obj.surface_finish:
                if surface_finish != edit_obj.surface_finish.id:
                    update_surface_finish(request, specification_obj, product)
                
        update_pricing_summary(request, specification_obj.estimation.id)
        
@login_required(login_url='signin')
@permission_required(['enquiries.change_enquiryspecifications'], login_url='permission_not_allowed')
def edit_enq_specifications(request, pk):
    """
    This function edits an enquiry specification and saves the changes made to the database.
    """

    specification_obj = EnquirySpecifications.objects.get(pk=pk)
    enquiry_id = specification_obj.estimation.enquiry.id
    if specification_obj.panel_specification:
        infill_spec = specification_obj.panel_specification.id
    else:
        infill_spec = None
        
    if specification_obj.surface_finish:
        surface_finish = specification_obj.surface_finish.id
    else:
        surface_finish = None
   
    try:
        compliancs = EstimationProductComplaints.objects.get(
            specification=specification_obj)
    except Exception as e:
        compliancs = None
    form = EditEnquirySpecificationForm(
        instance=specification_obj, kit_id=specification_obj.estimation.enquiry.surface_finish_price.id)
    
    complaint_form = ProductComplaintsForm(instance=compliancs)

    if request.method == 'POST':
        form = EditEnquirySpecificationForm(
            request.POST, instance=specification_obj, kit_id=specification_obj.estimation.enquiry.surface_finish_price.id)
        complaint_form = ProductComplaintsForm(
            request.POST, instance=compliancs)
        if form.is_valid():
            edit_obj = form.save(commit=False)
            edit_obj.last_modified_date = time()
            edit_obj.last_modified_by = request.user
            edit_obj.save()
            if edit_obj.specification_type == 2:
                edit_obj.aluminium_system = None
                edit_obj.aluminium_specification = None
                edit_obj.aluminium_series = None
                edit_obj.save()
            
            change_in_infill(request, specification_obj, infill_spec, edit_obj, surface_finish)
            messages.success(request, "Specification Updated Successfully")
            
        else:
            messages.errors(request, form.errors)

        if complaint_form.is_valid():
            complaint_form_obj = complaint_form.save(commit=False)
            complaint_form_obj.last_modified_date = time()
            complaint_form_obj.last_modified_by = request.user
            complaint_form_obj.estimation = specification_obj.estimation
            complaint_form_obj.specification = specification_obj
            complaint_form_obj.save()
            print("COMPLAINT FORM SAVE")
        else:
            messages.error(request, complaint_form.errors)
                    
        message = specification_obj.identifier+" | "+specification_obj.aluminium_products.product_name+' Specification Updated in Original.' \
            if specification_obj.aluminium_products else specification_obj.identifier+" | "+specification_obj.panel_specification.specifications +\
            ' Specification Updated in Original.' if specification_obj.estimation.version.version == '0' \
            else specification_obj.identifier+" | "+specification_obj.aluminium_products.product_name+' Specification Updated in Revision ' +\
            str(specification_obj.estimation.version.version) if specification_obj.aluminium_products else specification_obj.identifier +\
            " | "+specification_obj.panel_specification.specifications+' Specification Updated in Revision ' +\
            str(specification_obj.estimation.version.version)
        enquiry_logger(enquiry=specification_obj.estimation.enquiry,
                       message=message, action=2, user=request.user)
        return redirect('enquiry_profile', pk=enquiry_id, version=specification_obj.estimation.id)
    context = {
        "title": f'{PROJECT_NAME} | Edit Enquiry Specification',
        "edit_form": form,
        "pk": pk,
        "main": True,
        "enquiry_obj": specification_obj.estimation.enquiry,
        "complaint_form": complaint_form,
    }
    return render(request, "Enquiries/edit_enquiry_specification.html", context)


def temp_update_infill_specification(request, specification_obj, infill_spec, edit_obj, product):
    if edit_obj.panel_specification:
        if infill_spec != edit_obj.panel_specification.id:
            product.panel_product = specification_obj.panel_product
            infill_product_objs = Temp_MainProductGlass.objects.filter(
                estimation_product=product, glass_specif=infill_spec)
            for infill_product_obj in infill_product_objs:
                update_infill_product(infill_product_obj, specification_obj)

            update_product_price(product, request)


def temp_update_surface_finish(request, specification_obj, product):
    alumini_obj = Temp_MainProductAluminium.objects.get(estimation_product=product)
    alumini_obj.surface_finish = specification_obj.surface_finish

    if alumini_obj.surface_finish:
        al_quoted_price = (
            (float(alumini_obj.price_per_kg) * (float(alumini_obj.al_markup)) / 100) +
            float(alumini_obj.price_per_kg)) + float(specification_obj.surface_finish.surface_finish_price)

        if alumini_obj.aluminium_pricing == 1 and alumini_obj.al_weight_per_unit:
            alumini_obj.al_quoted_price = al_quoted_price
        elif alumini_obj.aluminium_pricing == 2 and alumini_obj.pricing_unit == 3:
            alumini_obj.al_quoted_price = al_quoted_price
        elif alumini_obj.aluminium_pricing == 4:
            alumini_obj.al_quoted_price = al_quoted_price

    alumini_obj.save()
    update_product_price(product, request)


def temp_change_in_infill(request, specification_obj, infill_spec, edit_obj, surface_finish):
    if edit_obj:
        spec_products_objs = Temp_EstimationMainProduct.objects.filter(
            specification_Identifier=specification_obj.id, disabled=False
            # panel_product=specification_obj.panel_product
            )

        for product in spec_products_objs:
            temp_update_infill_specification(request, specification_obj, infill_spec, edit_obj, product)
            if edit_obj.surface_finish:
                if surface_finish != edit_obj.surface_finish.id:
                    temp_update_surface_finish(request, specification_obj, product)
                
        update_pricing_summary(request, specification_obj.estimation.id)
    
    
@login_required(login_url='signin')
@permission_required(['enquiries.change_enquiryspecifications'], login_url='permission_not_allowed')
def temp_edit_enq_specifications(request, pk):
    """
    This function edits the specifications of a temporary enquiry and saves the changes made to the
    database.
    """
    specification_obj = Temp_EnquirySpecifications.objects.get(pk=pk)
    enquiry_id = specification_obj.estimation.enquiry.id
    if specification_obj.panel_specification:
        infill_spec = specification_obj.panel_specification.id
    else:
        infill_spec = None
        
    if specification_obj.surface_finish:
        surface_finish = specification_obj.surface_finish.id
    else:
        surface_finish = None
    
    try:
        compliancs = Temp_EstimationProductComplaints.objects.get(
            specification=specification_obj)
    except Exception as e:
        compliancs = None
    form = TempEditEnquirySpecificationForm(
        instance=specification_obj, kit_id=specification_obj.estimation.enquiry.surface_finish_price.id)

    complaint_form = ProductComplaintsForm(instance=compliancs)

    if request.method == 'POST':
        form = TempEditEnquirySpecificationForm(
            request.POST, instance=specification_obj, kit_id=specification_obj.estimation.enquiry.surface_finish_price.id)
        complaint_form = TempProductComplaintsForm(
            request.POST, instance=compliancs)
        if form.is_valid():
            edit_obj = form.save(commit=False)
            edit_obj.last_modified_date = time()
            edit_obj.last_modified_by = request.user
            edit_obj.save()
            if edit_obj.specification_type == 2:
                edit_obj.aluminium_system = None
                edit_obj.aluminium_specification = None
                edit_obj.aluminium_series = None
                edit_obj.save()
                
            temp_change_in_infill(request, specification_obj, infill_spec, edit_obj, surface_finish)
            messages.success(request, "Specification Updated Successfully")
        else:
            messages.errors(request, form.errors)

        if complaint_form.is_valid():
            complaint_form_obj = complaint_form.save(commit=False)
            complaint_form_obj.last_modified_date = time()
            complaint_form_obj.last_modified_by = request.user
            complaint_form_obj.estimation = specification_obj.estimation
            complaint_form_obj.specification = specification_obj
            complaint_form_obj.save()
            print("COMPLAINT FORM SAVE")
        else:
            messages.error(request, complaint_form.errors)
            print("complaint_form error==>", complaint_form.errors)
        message = specification_obj.identifier+" | "+specification_obj.aluminium_products.product_name+' Specification Updated in Original (Cart).' \
            if specification_obj.aluminium_products else specification_obj.identifier+" | "+specification_obj.panel_specification.specifications +\
            ' Specification Updated in Original (Cart).' if specification_obj.estimation.version.version == '0' \
            else specification_obj.identifier+" | "+specification_obj.aluminium_products.product_name+' Specification Updated in Revision ' +\
            str(specification_obj.estimation.version.version)+'(Cart).' if specification_obj.aluminium_products else specification_obj.identifier +\
            " | "+specification_obj.panel_specification.specifications+' Specification Updated in Revision ' +\
            str(specification_obj.estimation.version.version)+'(Cart).'
        enquiry_logger(enquiry=specification_obj.estimation.enquiry,
                       message=message, action=2, user=request.user)
        return redirect('tem_enquiry_profile', pk=enquiry_id, version=specification_obj.estimation.id)
    context = {
        "title": PROJECT_NAME + " | Edit Enquiry Specification",
        "edit_form": form,
        "pk": pk,
        "main": True,
        "enquiry_obj": specification_obj.estimation.enquiry,
        "complaint_form": complaint_form

    }
    return render(request, "Enquiries/edit_enquiry_specification.html", context)


@login_required(login_url='signin')
@permission_required(['enquiries.delete_enquiryspecifications'], login_url='permission_not_allowed')
def delete_enq_specifications(request, pk):
    """
    The function `delete_enq_specifications` deletes a specification object from the database if it is
    not associated with any products, and logs the deletion action.
    """
    
    specification_obj = EnquirySpecifications.objects.get(pk=pk)
    product = EstimationMainProduct.objects.filter(
        building__estimation=specification_obj.estimation.id, 
        specification_Identifier=specification_obj, 
        category=specification_obj.categories.id,
        disabled=False,
        ).order_by('id')
    if request.method == 'POST':
        try:
            if not product:
                specification_obj.delete()
                message = specification_obj.identifier+" | "+specification_obj.aluminium_products.product_name+' Specification Deleted From Original.' \
                    if specification_obj.aluminium_products else specification_obj.identifier+" | "+specification_obj.panel_specification.specifications+\
                        ' Specification Deleted From Original.' if specification_obj.estimation.version.version == '0' \
                            else specification_obj.identifier+" | "+specification_obj.aluminium_products.product_name+' Specification Deleted From Revision '+\
                                str(specification_obj.estimation.version.version) if specification_obj.aluminium_products else specification_obj.identifier+\
                                    " | "+specification_obj.panel_specification.specifications+' Specification Deleted From Revision '+\
                                        str(specification_obj.estimation.version.version)
                enquiry_logger(enquiry=specification_obj.estimation.enquiry, message=message, action=3, user=request.user)
                try:
                    EstimationProductComplaints.objects.filter(specification=specification_obj.id).delete()
                    messages.success(request, "Specification Deleted Successfully")
                except Exception as e:
                    print("Delete is not possible.")
            else:
                messages.error(request, "Unable to delete the data. Already used in application.")
                print("YES")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")

        return redirect('enquiry_profile', pk=specification_obj.estimation.enquiry.id, version=specification_obj.estimation.id)
    
    context = {
        "url": "/Enquiries/delete_enq_specifications/"+str(pk)+"/",
        "content": f'Specification {specification_obj.identifier} ' 
    }
    return render(request, "Master_settings/delete_modal.html", context)
    

@login_required(login_url='signin')
@permission_required(['enquiries.add_enquiryspecifications'], login_url='permission_not_allowed')
def specification_duplicate(request, pk):
    specification_obj = EnquirySpecifications.objects.get(pk=pk)
    
    specification_obj_new = specification_obj
    specification_obj_new.pk = None
    specification_obj_new.identifier = 'D'
    specification_obj_new.save()
    
    return redirect('enquiry_profile', pk=specification_obj.estimation.enquiry.id, version=specification_obj.estimation.id)


@login_required(login_url='signin')
@permission_required(['enquiries.add_enquiryspecifications'], login_url='permission_not_allowed')
def temp_specification_duplicate(request, pk):
    specification_obj = Temp_EnquirySpecifications.objects.get(pk=pk)
    
    specification_obj_new = specification_obj
    specification_obj_new.pk = None
    specification_obj_new.identifier = 'D'
    specification_obj_new.save()
    
    return redirect('tem_enquiry_profile', pk=specification_obj.estimation.enquiry.id, version=specification_obj.estimation.id)
    

@login_required(login_url='signin')
@permission_required(['enquiries.delete_enquiryspecifications'], login_url='permission_not_allowed')
def temp_delete_enq_specifications(request, pk):
    """
    The function `delete_enq_specifications` deletes a specification object from the database if it is
    not associated with any products, and logs the deletion action.
    """
    
    specification_obj = Temp_EnquirySpecifications.objects.get(pk=pk)
    product = Temp_EstimationMainProduct.objects.filter(
        building__estimation=specification_obj.estimation.id, 
        specification_Identifier=specification_obj, 
        category=specification_obj.categories.id,
        disabled=False,
        ).order_by('id')
    if request.method == 'POST':
        try:
            if not product:
                specification_obj.delete()
                message = specification_obj.identifier+" | "+specification_obj.aluminium_products.product_name+' Specification Deleted From Original (Cart).' \
                    if specification_obj.aluminium_products else specification_obj.identifier+" | "+specification_obj.panel_specification.specifications+\
                        ' Specification Deleted From Original (Cart).' if specification_obj.estimation.version.version == '0' \
                            else specification_obj.identifier+" | "+specification_obj.aluminium_products.product_name+' Specification Deleted From Revision '+\
                                str(specification_obj.estimation.version.version)+' (Cart).' if specification_obj.aluminium_products else specification_obj.identifier+\
                                    " | "+specification_obj.panel_specification.specifications+' Specification Deleted From Revision '+\
                                        str(specification_obj.estimation.version.version)+' (Cart).'
                enquiry_logger(enquiry=specification_obj.estimation.enquiry, message=message, action=3, user=request.user)
                try:
                    Temp_EstimationProductComplaints.objects.filter(specification=specification_obj.id).delete()
                    messages.success(request, "Specification Deleted Successfully")
                except Exception as e:
                    print("Delete is not possible.")
            else:
                messages.error(request, "Unable to delete the data. Already used in application.")
                print("YES")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")

        return redirect('tem_enquiry_profile', pk=specification_obj.estimation.enquiry.id, version=specification_obj.estimation.id)
    
    context = {
        "url": "/Enquiries/temp_delete_enq_specifications/"+str(pk)+"/",
        "content": f'Specification {specification_obj.identifier} ' 
    }
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
@permission_required(['enquiries.change_enquiryspecifications'], login_url='permission_not_allowed')
def enquiry_settings(request, pk, version=None):
    """
    The `enquiry_settings` function handles the updating of enquiry settings in a Django web
    application.
    """
    enquiry_obj = Enquiries.objects.get(pk=pk)
    form = EditEnquiryForm(instance=enquiry_obj)
    surface_finish_price = Surface_finish_Master.objects.all().order_by('-id')
    if version:
        versions = Estimations.objects.get(pk=version)
    else:
        versions = Estimations.objects.filter(enquiry=enquiry_obj).first()
    estimation = Estimations.objects.filter(enquiry=enquiry_obj).order_by('id')
    try:
        pricing_master = AdditionalandLabourPriceMaster.objects.get(
            pk=enquiry_obj.additional_and_labour.id)
    except Exception as e:
        print('Exception:', e)
        pass
    if request.method == 'POST':
        form = EditEnquiryForm(request.POST, instance=enquiry_obj)
        title = request.POST.get('title')
        received_date = request.POST.get('received_date')
        due_date = request.POST.get('due_date')
        status = request.POST.get('status')
        labour_percentage = request.POST.get('labour_percentage')
        overhead_percentage = request.POST.get('overhead_percentage')
        price_per_kg = request.POST.get('price_per_kg')
        sealant_pricing = request.POST.get('sealant_pricing')
        price_per_kg_markup = request.POST.get('price_per_kg_markup')
        surface_finish_pricing = request.POST.get('surface_finish_pricing')
        # weather_price = request.POST.get('weather_price')
        if form.is_valid():
            # form_obj = form.save(commit=False)
            if labour_percentage:
                enquiry_obj.labour_percentage = labour_percentage
            else:
                if int(labour_percentage) < pricing_master.minimum_labour:
                    messages.error(
                        request, "Labour Percentage not below "+str(pricing_master.minimum_labour)+"%")
                    return redirect('enquiry_settings', pk=pk, version=versions.id)

            if overhead_percentage:
                enquiry_obj.overhead_percentage = overhead_percentage
            else:
                if int(overhead_percentage) < pricing_master.minimum_overhead:
                    messages.error(request, "Overhead Percentage not below " +
                                   str(pricing_master.minimum_overhead)+"%")
                    return redirect('enquiry_settings', pk=pk, version=versions.id)

            if price_per_kg:
                enquiry_obj.price_per_kg = price_per_kg

            if title:
                enquiry_obj.title = title

            if received_date:
                enquiry_obj.received_date = received_date

            if due_date:
                enquiry_obj.due_date = due_date

            if sealant_pricing:
                enquiry_obj.sealant_pricing_id = int(sealant_pricing)

            if price_per_kg_markup:
                enquiry_obj.price_per_kg_markup = float(price_per_kg_markup)
                
            if surface_finish_pricing:
                # surface_finish = Surface_finish_Master.objects.get(pk=surface_finish_pricing)
                enquiry_obj.surface_finish_price_id = surface_finish_pricing

            # if weather_price:
            #     enquiry_obj.weather_price = float(weather_price)

            for est in estimation:
                if status == '6':
                    esti_version = EstimationVersions.objects.get(
                        pk=est.version.id)
                    esti_version.status = 7
                    esti_version.save()
                elif status == '7':
                    esti_version = EstimationVersions.objects.get(
                        pk=est.version.id)
                    esti_version.status = 5
                    esti_version.save()
                elif status == '2':
                    esti_version = EstimationVersions.objects.get(
                        pk=est.version.id)
                    esti_version.status = 2
                    esti_version.save()
                else:
                    pass
            enquiry_obj.last_modified_date = time()
            enquiry_obj.last_modified_by = request.user
            # form.save()
            enquiry_obj.save()
            enquiry_logger(enquiry=enquiry_obj,message='Enquiry Settings Updated', action=2, user=request.user)
            messages.success(request, "Enquiry Updated Successfully")
        else:
            messages.error(request, "Please Check All Fields")
            print('errors==>', form.errors)
        data = {
            "success": True,
        }
        return JsonResponse(data, status=200)
        # return redirect('enquiry_profile', pk=pk, version=versions.id)

    context = {
        "title": PROJECT_NAME + " | Enquiry Settings",
        "form": form,
        "enquiry_obj": enquiry_obj,
        'pricing_master': pricing_master,
        'version': version,
        'surface_finish_price': surface_finish_price
    }
    return render(request, 'Enquiries/enquiry_settings_modal.html', context)


@login_required(login_url='signin')
@permission_required(['enquiries.change_enquiries'], login_url='permission_not_allowed')
def temp_enquiry_settings(request, pk, version):
    """
    The function `temp_enquiry_settings` handles the settings and updates for a temporary enquiry in a
    web application.
    """
    
    enquiry_obj = Enquiries.objects.get(pk=pk)
    form = EditEnquiryForm(instance=enquiry_obj)
    estimation = Temp_Estimations.objects.get(pk=version)
    surface_finish_price = Surface_finish_Master.objects.all().order_by('-id')
    
    try:
        pricing_master = AdditionalandLabourPriceMaster.objects.get(
            pk=enquiry_obj.additional_and_labour.id)
    except Exception as e:
        print('Exception:', e)
        pass
    if request.method == 'POST':
        form = EditEnquiryForm(request.POST, instance=enquiry_obj)
        title = request.POST.get('title')
        received_date = request.POST.get('received_date')
        due_date = request.POST.get('due_date')
        status = request.POST.get('status')
        labour_percentage = request.POST.get('labour_percentage')
        overhead_percentage = request.POST.get('overhead_percentage')
        price_per_kg = request.POST.get('price_per_kg')
        
        sealant_pricing = request.POST.get('sealant_pricing')
        price_per_kg_markup = request.POST.get('price_per_kg_markup')
        surface_finish_pricing = request.POST.get('surface_finish_pricing')

        if form.is_valid():
            if labour_percentage:
                enquiry_obj.labour_percentage = labour_percentage
            else:
                if int(labour_percentage) < pricing_master.minimum_labour:
                    messages.error(
                        request, "Labour Percentage not below "+str(pricing_master.minimum_labour)+"%")
                    return redirect('temp_enquiry_settings', pk=pk, version=version)

            if overhead_percentage:
                enquiry_obj.overhead_percentage = overhead_percentage
            else:
                if int(overhead_percentage) < pricing_master.minimum_overhead:
                    messages.error(request, "Overhead Percentage not below " +
                                   str(pricing_master.minimum_overhead)+"%")
                    return redirect('temp_enquiry_settings', pk=pk, version=version)

            if price_per_kg:
                enquiry_obj.price_per_kg = price_per_kg

            if title:
                enquiry_obj.title = title

            if received_date:
                enquiry_obj.received_date = received_date

            if due_date:
                enquiry_obj.due_date = due_date

            if sealant_pricing:
                enquiry_obj.sealant_pricing_id = int(sealant_pricing)

            if price_per_kg_markup:
                enquiry_obj.price_per_kg_markup = float(price_per_kg_markup)
                
            if surface_finish_pricing:
                # surface_finish = Surface_finish_Master.objects.get(pk=surface_finish_pricing)
                enquiry_obj.surface_finish_price_id = surface_finish_pricing
                
            if status == '6':
                esti_version = EstimationVersions.objects.get(
                    pk=estimation.version.id)
                esti_version.status = 7
                esti_version.save()
            elif status == '7':
                esti_version = EstimationVersions.objects.get(
                    pk=estimation.version.id)
                esti_version.status = 5
                esti_version.save()
            elif status == '2':
                esti_version = EstimationVersions.objects.get(
                    pk=estimation.version.id)
                esti_version.status = 2
                esti_version.save()
            else:
                pass
            enquiry_obj.last_modified_date = time()
            enquiry_obj.last_modified_by = request.user
            enquiry_obj.save()
            messages.success(request, "Enquiry Updated Successfully")
        else:
            messages.error(request, "Please Check All Fields")
            print('errors==>', form.errors)
        return redirect('tem_enquiry_profile', pk=pk, version=version)

    context = {
        "title": PROJECT_NAME + " | Enquiry Settings",
        "form": form,
        "enquiry_obj": enquiry_obj,
        'pricing_master': pricing_master,
        'version': version,
        'surface_finish_price': surface_finish_price
        
    }
    return render(request, 'Enquiries/enquiry_settings_modal.html', context)


@login_required(login_url='signin')
@permission_required(['estimations.view_estimationmainproduct'], login_url='permission_not_allowed')
def product_category_summary(request, pk):
    """
    This function retrieves various objects related to an estimation and renders them in a template for
    a product category summary page.
    
    """
    
    estimate_datas = EstimationMainProduct.objects.filter(
        building__estimation=pk, disabled=False).order_by('id')
    estimation_version = Estimations.objects.get(pk=pk)
    enquiry_obj = Enquiries.objects.get(pk=estimation_version.enquiry.id)
    specification_obj = EnquirySpecifications.objects.filter(
        estimation=estimation_version).order_by('id')
    estim_versions = Estimations.objects.filter(enquiry=enquiry_obj).order_by('id')
    buildings = EstimationBuildings.objects.filter(
        estimation=estimation_version.id).order_by('id')
    boqs = BillofQuantity.objects.filter(
        enquiry=estimation_version.enquiry).distinct('boq_number')
    product = EstimationMainProduct.objects.filter(
        building__estimation=estimation_version.id, disabled=False).order_by('id')
    quotations = Quotations.objects.filter(estimations__enquiry=enquiry_obj).order_by('id')
    temp_estimations = Temp_Estimations.objects.filter(enquiry=enquiry_obj).order_by('id')
    notes_obj = EstimationNotes.objects.filter(
        estimation=estimation_version).order_by('id')
    
    try:
        pricing_summary_obj = Pricing_Summary.objects.get(estimation=estimation_version)
    except Exception:
        pricing_summary_obj = None
        
    path = str(enquiry_obj.enquiry_id)
    parent_path = 'Quotations'
    ai_rating_label = estimation_ai_rating(enquiry_obj.id)
    
    context = {
        'title': PROJECT_NAME+' | Product Category Summary',
        'estimate_datas': estimate_datas,
        'pk': pk,
        'buildings': buildings,
        'boqs': boqs,
        "enquiry_obj": enquiry_obj,
        "version": estimation_version,
        "specification_obj": specification_obj,
        "estim_versions": estim_versions,
        "product": product,
        "quotations": quotations,
        "temp_estimations": temp_estimations,
        "notes_obj": notes_obj,
        "products": [product.id for product in estimate_datas],
        'folder_path': path,
        'parent_path': parent_path,
        'ai_rating_label': ai_rating_label,
        "pricing_summary_obj": pricing_summary_obj,
    }
    return render(request, 'Enquiries/enquiry_profile_pages/estimation_category_summary_page.html', context)


@login_required(login_url='signin')
@permission_required(['estimations.view_estimationmainproduct'], login_url='permission_not_allowed')
def temp_product_category_summary(request, pk):
    """
    This function retrieves data related to a specific estimation and renders it on a product category
    summary page.
    """
    estimate_datas = Temp_EstimationMainProduct.objects.filter(
        building__estimation=pk, disabled=False).order_by('id')
    estimation_version = Temp_Estimations.objects.get(pk=pk)
    enquiry_obj = Enquiries.objects.get(pk=estimation_version.enquiry.id)
    buildings = Temp_EstimationBuildings.objects.filter(
        estimation=estimation_version.id).order_by('id')
    estim_versions = Temp_Estimations.objects.filter(enquiry=enquiry_obj).order_by('id')
    specification_obj = Temp_EnquirySpecifications.objects.filter(
        estimation=estimation_version).order_by('id')
    estim_versions = Estimations.objects.filter(enquiry=enquiry_obj).order_by('id')
    quotations = Temp_Quotations.objects.filter(
        estimations__enquiry=enquiry_obj).order_by('id')
    product = Temp_EstimationMainProduct.objects.filter(
        building__estimation=estimation_version.id, disabled=False).order_by('id')
    temp_estimations = Temp_Estimations.objects.filter(enquiry=enquiry_obj).order_by('id')
    notes_obj = Temp_EstimationNotes.objects.filter(
        estimation=estimation_version).order_by('id')
    try:
        pricing_summary_obj = Temp_Pricing_Summary.objects.get(estimation=estimation_version)
    except Exception:
        pricing_summary_obj = None
    path = str(enquiry_obj.enquiry_id)
    parent_path = 'Quotations'
    ai_rating_label = estimation_ai_rating(enquiry_obj.id)
    
    context = {
        'title': PROJECT_NAME+' | Product Category Summary',
        'estimate_datas': estimate_datas,
        'pk': pk,
        'buildings': buildings,
        "enquiry_obj": enquiry_obj,
        "version": estimation_version,
        "specification_obj": specification_obj,
        "estim_versions": estim_versions,
        "quotations": quotations,
        "product": product,
        "temp_estimations": temp_estimations,
        "notes_obj": notes_obj,
        "products": [product.id for product in estimate_datas],
        'folder_path': path,
        'parent_path': parent_path,
        'ai_rating_label': ai_rating_label,
        "pricing_summary_obj": pricing_summary_obj,
    }
    return render(request, 'Enquiries/enquiry_profile_pages/estimation_category_summary_page.html', context)


@login_required(login_url='signin')
@permission_required(
    [
        'estimations.change_estimationmainproduct', 
        'estimations.change_mainproductaluminium', 
        'estimations.change_mainproductglass',
    ], login_url='permission_not_allowed')
def update_product_category_percentage_all(request, pk):
    """
    This function updates the percentage values for various product categories in an estimation.
    """
    
    estimate_datas = EstimationMainProduct.objects.filter(
        building__estimation=pk, disabled=False).order_by('id')
    for product in estimate_datas:
        aluminium = MainProductAluminium.objects.get(
            estimation_product=product)
        try:
            glass = MainProductGlass.objects.get(estimation_product=product)
        except Exception as e:
            glass = None
        try:
            sealant = MainProductSilicon.objects.get(
                estimation_product=product)
        except Exception as e:
            sealant = None
        labour_and_overhead = PricingOption.objects.get(
            estimation_product=product)
        pricing_master = AdditionalandLabourPriceMaster.objects.get(
            pk=estimate_datas.building.estimation.enquiry.additional_and_labour.id)

        main_form = UpdateLabourAndOverhead(instance=labour_and_overhead)
        aluminium_form = UpdateAluminiumPercentage(instance=aluminium)
        try:
            glass_form = UpdateGlassPercentage(instance=glass)
        except Exception as e:
            glass_form = None
        if request.method == 'POST':
            main_form = UpdateLabourAndOverhead(
                request.POST, instance=labour_and_overhead)
            aluminium_form = UpdateAluminiumPercentage(
                request.POST, instance=aluminium)
            alumini_final = request.POST.get('alumini_final')
            glass_final = request.POST.get('glass_final')
            sec_glass_final = request.POST.get('sec_glass_final')

            try:
                glass_form = UpdateGlassPercentage(
                    request.POST, instance=glass)
            except Exception as e:
                glass_form = None
            if aluminium_form.is_valid() and glass_form.is_valid() and main_form.is_valid():
                if main_form.cleaned_data['overhead_perce'] < pricing_master.minimum_overhead:
                    messages.error(request,
                                   "Overhead Percentage not below " + str(pricing_master.minimum_overhead) + "%")

                if main_form.cleaned_data['labour_perce'] < pricing_master.minimum_labour:
                    messages.error(request, "Labour Percentage not below " +
                                   str(pricing_master.minimum_labour) + "%")

                aluminium_obj = aluminium_form.save(commit=False)
                if alumini_final:
                    aluminium_obj.al_quoted_price = float(alumini_final)
                aluminium_obj.save()

                glass_obj = glass_form.save(commit=False)
                if glass_final:
                    glass_obj.quoted_price = float(glass_final)
                if glass_obj.is_sec_glass_cost:
                    if sec_glass_final:
                        glass_obj.sec_quoted_price = float(sec_glass_final)
                glass_obj.save()

                main_form.save()
            else:
                messages.error(request, aluminium_form.errors,
                               glass_form.errors)
                print('errors==>', main_form.errors,
                      aluminium_form.errors, glass_form.errors)

            return redirect('enquiry_profile', pk=product.building.estimation.enquiry.id, version=pk)

    context = {
        'estimate_datas': estimate_datas,
        "main_product": product,
        "aluminium": aluminium,
        "glass": glass,
        "main_form": main_form,
        "aluminium_form": aluminium_form,
        "glass_form": glass_form,
        "pk": pk,
        "sealant": sealant
    }
    return render(request, 'Enquiries/category_summary_update_all.html', context)


@login_required(login_url='signin')
@permission_required(['estimations.add_quotations'], login_url='permission_not_allowed')
def create_quotation_base(request, pk, version=None):
    """
    This function creates a quotation based on an enquiry and allows for previewing, saving, and
    submitting the quotation.
    """
    
    enquiry = Enquiries.objects.get(pk=pk)
    templates = Quotations_Master.objects.filter(company=enquiry.company).order_by('id')
    if enquiry.enquiry_type == 1:
        try:
            represent = Contacts.objects.get(
                customer=enquiry.customers.all().first(), is_primary=True)
            
        except Exception as e:
            represent = None
    else:
        represent = None

    buildings = EstimationBuildings.objects.filter(estimation=version, disabled=False).order_by('id')
    
    specifications_obj = EnquirySpecifications.objects.filter(estimation=version).distinct(
                            'categories', 
                            'panel_specification', 
                            'aluminium_system', 
                            'surface_finish', 
                            'aluminium_products',
                            'is_description'
                            )
    quotation_note_form = CreateQuotationNote()
    forms = CreateQuotationsForm()
    PROVISIONSFORMSET = modelformset_factory(Quotation_Provisions, form=CreateQuotations_Provisions, extra=1,
                                             can_delete=True)
    provisions_form = PROVISIONSFORMSET(
        queryset=Quotation_Provisions.objects.none(), prefix="quotation_provisions")
    try:
        quotation_template = Quotations_Master.objects.filter(company=enquiry.company).first()
    except:
        quotation_template = None

    try:
        estimation = Estimations.objects.get(pk=version)
    except Exception as e:
        estimation = None
    
    if request.method == 'POST':
        quotation_type = request.POST.get("quotation_type")
        template_id = request.POST.get("template_id")
        if enquiry.enquiry_type == 1:
            represented_by = request.POST.get('represented_by')
            prepared_by = request.POST.get('prepared_by')
            
        quotation_note_form = CreateQuotationNote(request.POST)
        forms = CreateQuotationsForm(request.POST)
        provisions_form = PROVISIONSFORMSET(
            request.POST, prefix="quotation_provisions")
        template= 'print_templates/quotation_print_template.html'
        footer_template = get_template('print_templates/quotation_print_footer.html')
        header_template = get_template('print_templates/quotation_print_header.html')
        
        if 'preview' in request.POST and not 'save' in request.POST and not 'submit' in request.POST:
            quotations_del = Quotations.objects.filter(estimations=estimation.id, is_draft=True)
            quotations_del.delete()
            if forms.is_valid() and quotation_note_form.is_valid() and provisions_form.is_valid():
                form_obj = forms.save(commit=False)
                form_obj.estimations_version = estimation.version
                form_obj.created_by = request.user
                form_obj.is_draft=True
                if quotation_type == '1':
                    form_obj.q_type = 1
                else:
                    form_obj.q_type = 2
                if template_id:
                    form_obj.template_id = int(template_id)
                    form_obj.estimations = estimation
                    form_obj.save()
                else:
                    messages.error(request, 'Please Select a Template')
                    return redirect('create_quotation_base', pk=enquiry.id, version=version)

                if enquiry.enquiry_type == 1:
                    form_obj.prepared_for.add(prepared_by)
                    form_obj.represented_by_id = represented_by
                    
                    quotation_customer = Contacts.objects.get(pk=represented_by).customer
                    form_obj.quotation_customer = quotation_customer
                
                form_obj.save()

                for item in provisions_form:
                    if item.is_valid():
                        item_obj = item.save(commit=False)
                        if not item_obj.provision_cost == 0:
                            item_obj.quotation = form_obj
                            item_obj.save()
                    else:
                        messages.error(request, item.errors)
                        print("items-error==>", item.errors)
                
                quotations = Quotations.objects.get(pk=form_obj.id)
                provisions_obj = Quotation_Provisions.objects.filter(quotation=quotations).order_by('id')
                
                quotation_note_obj = quotation_note_form.save(commit=False)
                quotation_note_obj.quotation = form_obj
                # try:
                #     tags = Tags.objects.get(Q(pk=1)| Q(tag_name='Quotation'))
                # except:
                #     tags = Tags(created_by=request.user, tag_name='Quotation', tag_color='#175899')
                #     tags.save()
                # quotation_note_obj.tag = tags
                quotation_note_obj.created_by = request.user
                quotation_note_obj.save()
                note = EstimationNotes(created_by=request.user, created_date=time(), estimation=estimation, \
                                    notes=quotation_note_obj.quotation_notes, note_status=10)
                note.save()
        
                context={
                    'title': f'{PROJECT_NAME} | Quotation Privew',
                    'quotations': quotations,
                    "specifications_obj": specifications_obj,
                    "buildings": buildings,
                    "filter_by_boq": False,
                    "provisions_obj": provisions_obj,
                    "estimation": estimation,
                }
                cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '38mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 12,
                    'page-size': 'A4',
                    'encoding': "UTF-8",
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,
                }
                quotation_file_name = 'Temp_Quotation.pdf'
                
                try:
                    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                    footer_template=footer_template, header_template=header_template, 
                                                    template=template, context=context)
                    pdf_data = io.BytesIO(response.rendered_content)

                    pdf_file_path = MEDIA_URL+ quotation_file_name
                    with open(pdf_file_path, 'wb') as f:
                        f.write(pdf_data.getbuffer())
        
                    return JsonResponse({
                            'pdf_url': 'http://'+str(request.get_host())+'/'+str(pdf_file_path),
                        })
                except Exception as e:
                    print("Exce==:>", e)
            else:
                messages.error(request, forms.errors)
                print('errors', forms.errors)  
                print('quotation_note_form', forms.quotation_note_form)  
                print('provisions_form', forms.provisions_form)  
        elif 'submit' in request.POST:
            quotations_del = Quotations.objects.filter(estimations=estimation.id, is_draft=True)
            quotations_del.delete()
            if forms.is_valid() and quotation_note_form.is_valid() and provisions_form.is_valid():
                form_obj = forms.save(commit=False)
                form_obj.estimations_version = estimation.version
                form_obj.created_by = request.user
                form_obj.is_draft = False
                if quotation_type == '1':
                    form_obj.q_type = 1
                else:
                    form_obj.q_type = 2
                if template_id:
                    form_obj.template_id = int(template_id)
                    form_obj.estimations = estimation
                    form_obj.save()
                else:
                    messages.error(request, 'Please Select a Template')
                    return redirect('create_quotation_base', pk=enquiry.id, version=version)

                if enquiry.enquiry_type == 1:
                    form_obj.prepared_for.add(prepared_by)
                    form_obj.represented_by_id = represented_by
                    quotation_customer = Contacts.objects.get(pk=represented_by).customer
                    form_obj.quotation_customer = quotation_customer
                    # form_obj.quotation_customer_id = int(represented_by)
                form_obj.save()
                for item in provisions_form:
                    if item.is_valid():
                        item_obj = item.save(commit=False)
                        if not item_obj.provision_cost == 0:
                            item_obj.quotation = form_obj
                            item_obj.save()
                    else:
                        messages.error(request, item.errors)
                        print("items-error==>", item.errors)

                est_version = EstimationVersions.objects.get(
                    pk=estimation.version.id)
                est_version.status = 10
                est_version.save()
                quotation_note_obj = quotation_note_form.save(commit=False)
                quotation_note_obj.quotation = form_obj
                quotation_note_obj.created_by = request.user
                # try:
                #     tags = Tags.objects.get(Q(pk=1)| Q(tag_name='Quotation'))
                # except:
                #     tags = Tags(created_by=request.user, tag_name='Quotation', tag_color='#175899')
                #     tags.save()
                # quotation_note_obj.tag = tags
                quotation_note_obj.save()
                provisions_obj = Quotation_Provisions.objects.filter(quotation=form_obj).order_by('id')
                
                note = EstimationNotes(created_by=request.user, created_date=time(), estimation=estimation, \
                                    notes=quotation_note_obj.quotation_notes, note_status=10)
                note.save()
                message = 'Created New Quotation #'+form_obj.quotation_id+' in Original.' if estimation.version.version == '0' else 'Created New Quotation #'+form_obj.quotation_id+' Revision '+str(estimation.version.version)
                enquiry_logger(enquiry=enquiry, message=message, action=1, user=request.user)
                update_pricing_summary(request, estimation.id)
                messages.success(request, "Quotation Created Successfully")
                if estimation.enquiry.enquiry_type == 1:
                    context={
                        'quotations': form_obj,
                        "specifications_obj": specifications_obj,
                        "buildings": buildings,
                        "filter_by_boq": False,
                        "provisions_obj": provisions_obj,
                        "estimation": estimation,
                    }
                    cmd_options = {
                        'quiet': True, 
                        'enable-local-file-access': True, 
                        'margin-top': '38mm', 
                        'header-spacing': 5,
                        'minimum-font-size': 12,
                        'page-size': 'A4',
                        'encoding': "UTF-8",
                        'print-media-type': True,
                        'footer-right': "[page] / [topage]",
                        'footer-font-size': 8,
                    }
                    quotation_file_name = str(estimation.enquiry.title)+'_Quotation.pdf'
                    clean_string = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                    
                    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                    footer_template=footer_template, header_template=header_template, 
                                                    template=template, context=context)
                    pdf_data = io.BytesIO(response.rendered_content)

                    version_str = 'Original' if estimation.version.version == '0' else 'Revision '+str(estimation.version.version)
                    pdf_file_path = MEDIA_URL+ 'Quotations/' + str(estimation.enquiry.enquiry_id) + '/' +\
                        str(estimation.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
                    folder = MEDIA_URL+ 'Quotations/' + str(estimation.enquiry.enquiry_id) + '/' +\
                        str(estimation.enquiry.main_customer.name) + '/'+str(version_str)
                        
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                        
                    with open(pdf_file_path, 'wb') as f:
                        f.write(pdf_data.getbuffer())
                
                return JsonResponse({'url': 'http://'+str(request.get_host())+'/Estimation/estimation_quotations_list/'+ str(estimation.id) +'/'})
            else:
                messages.error(request, forms.errors)
                print('errors', forms.errors)
        else:
            quotation = Quotations.objects.get(estimations__enquiry=pk, is_draft=True)    
            quotation.is_draft = False
            quotation.save()
            
            est_version = EstimationVersions.objects.get(
                    pk=quotation.estimations.version.id)
            est_version.status = 10
            est_version.save()
            provisions_obj = Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
                
            message = 'Created New Quotation #'+quotation.quotation_id+' in Original.' \
                if quotation.estimations.version.version == '0' else 'Created New Quotation #'+quotation.quotation_id+' Revision '+str(quotation.estimations.version.version)
            enquiry_logger(enquiry=quotation.estimations.enquiry, message=message, action=1, user=request.user)
            update_pricing_summary(request, estimation.id)
            messages.success(request, "Quotation Created Successfully")
            if estimation.enquiry.enquiry_type == 1:
                context={
                        'quotations': quotation,
                        "specifications_obj": specifications_obj,
                        "buildings": buildings,
                        "filter_by_boq": False,
                        "provisions_obj": provisions_obj,
                        "estimation": estimation,
                    }
                cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '38mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 12,
                    'page-size': 'A4',
                    'encoding': "UTF-8",
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,
                }
                quotation_file_name = str(estimation.enquiry.title)+'_Quotation.pdf'
                clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                footer_template=footer_template, header_template=header_template, 
                                                template=template, context=context)
                pdf_data = io.BytesIO(response.rendered_content)

                version_str = 'Original' if estimation.version.version == '0' else 'Revision '+str(estimation.version.version)
                pdf_file_path = MEDIA_URL+ 'Quotations/' + str(estimation.enquiry.enquiry_id) + '/' +\
                    str(estimation.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
                
                folder = MEDIA_URL+ 'Quotations/' + str(estimation.enquiry.enquiry_id) + '/' +\
                        str(estimation.enquiry.main_customer.name) + '/'+str(version_str)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                    
                with open(pdf_file_path, 'wb') as f:
                    f.write(pdf_data.getbuffer())
                    
            return redirect('estimation_quotations_list', pk=quotation.estimations.id)
    context = {
        'title': f'{PROJECT_NAME} | Create Quotation',
        'forms': forms,
        'pk': pk,
        'version': estimation,
        'enquiry': enquiry,
        'enquiry_obj': enquiry,
        'estimation': estimation,
        'represent': represent,
        'buildings': buildings,
        'estimation': estimation,
        'specifications_obj': specifications_obj,
        'provisions_form': provisions_form,
        'quotation_template': quotation_template,
        'templates': templates,
        'quotation_note_form': quotation_note_form,
        'tinymc_api': TINYMC_API,
    }
    return render(request, 'Enquiries/quotations/create_quotation_base.html', context)


@login_required(login_url='signin')
@permission_required(['estimations.add_quotations'], login_url='permission_not_allowed')
def temp_create_quotation_base(request, pk, version=None):
    """
    This function creates a quotation for an enquiry and allows the user to preview, save, or submit the
    quotation.
    """
    templates = Quotations_Master.objects.all().order_by('id')
    enquiry = Enquiries.objects.get(pk=pk)
    estimation_objs = Estimations.objects.filter(enquiry=enquiry)
    
    if enquiry.enquiry_type == 1:
        try:
            represent = Contacts.objects.get(
                customer=enquiry.customers.all().first(), is_primary=True)
        except Exception as e:
            represent = None
    else:
        represent = None

    buildings = Temp_EstimationBuildings.objects.filter(estimation=version, disabled=False).order_by('id')
    specifications_obj = Temp_EnquirySpecifications.objects.filter(estimation=version).distinct(
                            'categories', 
                            'panel_specification', 
                            'aluminium_system', 
                            'surface_finish', 
                            'aluminium_products',
                            'is_description'
                            )
    quotation_note_form = Temp_CreateQuotationNote()
    forms = TempCreateQuotationsForm()
    PROVISIONSFORMSET = modelformset_factory(Temp_Quotation_Provisions, form=TempCreateQuotations_Provisions, extra=1,
                                             can_delete=True)
    provisions_form = PROVISIONSFORMSET(
        queryset=Temp_Quotation_Provisions.objects.none(), prefix="quotation_provisions")
    try:
        quotation_template = Quotations_Master.objects.all().first()
    except:
        quotation_template = None

    try:
        estimation = Temp_Estimations.objects.get(pk=version)
    except Exception as e:
        print("EXCEPTION:", e)
        estimation = None
    q_obj = Quotations.objects.filter(estimations__enquiry=enquiry, is_draft=False).last()
    if q_obj:
        quotation_id = int((q_obj.quotation_id).split('/')[0])
    else:
        q_id = Quotations.objects.last()
        if q_id:
            quotation_id = int((q_id.quotation_id).split('/')[0])+1
        else:
            quotation_id = QUOTATION_ID
    
    if request.method == 'POST':
        quotation_type = request.POST.get("quotation_type")
        template_id = request.POST.get("template_id")
        if enquiry.enquiry_type == 1:
            represented_by = request.POST.get('represented_by')
            prepared_by = request.POST.get('prepared_by')
        quotation_note_form = Temp_CreateQuotationNote(request.POST)
        forms = TempCreateQuotationsForm(request.POST)
        provisions_form = PROVISIONSFORMSET(
            request.POST, prefix="quotation_provisions")
        template= 'print_templates/quotation_print_template.html'
        footer_template = get_template('print_templates/quotation_print_footer.html')
        header_template = get_template('print_templates/quotation_print_header.html')
        if 'preview' in request.POST and not 'save' in request.POST and not 'submit' in request.POST:
            quotations_del = Temp_Quotations.objects.filter(estimations=estimation.id, is_draft=True).delete()
            if forms.is_valid() and quotation_note_form.is_valid() and provisions_form.is_valid():
                form_obj = forms.save(commit=False)
                form_obj.estimations_version = estimation.version
                form_obj.created_by = request.user
                form_obj.quotation_id = quotation_id
                form_obj.is_draft=True
                if quotation_type == '1':
                    form_obj.q_type = 1
                else:
                    form_obj.q_type = 2
                if template_id:
                    form_obj.template_id = int(template_id)
                    form_obj.estimations = estimation
                    form_obj.save()
                else:
                    messages.error(request, 'Please Select a Template')
                    return redirect('create_quotation_base', pk=enquiry.id, version=version)

                if enquiry.enquiry_type == 1:
                    form_obj.prepared_for.add(prepared_by)
                    form_obj.represented_by_id = represented_by
                    quotation_customer = Contacts.objects.get(pk=represented_by).customer
                    form_obj.quotation_customer_id = quotation_customer
                
                form_obj.save()

                for item in provisions_form:
                    if item.is_valid():
                        item_obj = item.save(commit=False)
                        if not item_obj.provision_cost == 0:
                            item_obj.quotation = form_obj
                            item_obj.save()
                    else:
                        messages.error(request, item.errors)
                        print("items-error==>", item.errors)
                
                quotations = Temp_Quotations.objects.get(pk=form_obj.id)
                provisions_obj = Temp_Quotation_Provisions.objects.filter(quotation=quotations).order_by('id')

                quotation_note_obj = quotation_note_form.save(commit=False)
                quotation_note_obj.quotation = form_obj
                quotation_note_obj.created_by = request.user
                # try:
                #     tags = Tags.objects.get(Q(pk=1)| Q(tag_name='Quotation'))
                # except:
                #     tags = Tags(created_by=request.user, tag_name='Quotation', tag_color='#175899')
                #     tags.save()
                # quotation_note_obj.tag = tags
                quotation_note_obj.save()
                note = Temp_EstimationNotes(created_by=request.user, created_date=time(), estimation=estimation, \
                                    notes=quotation_note_obj.quotation_notes, note_status=10)
                note.save()
                
                context={
                    'title': f'{PROJECT_NAME} | Quotation Privew',
                    'quotations': quotations,
                    "specifications_obj": specifications_obj,
                    "buildings": buildings,
                    "filter_by_boq": False,
                    "provisions_obj": provisions_obj,
                }
                cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '38mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 12,
                    'page-size': 'A4',
                    'encoding': "UTF-8",
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,                    
                }
                quotation_file_name = 'Temp_Quotation.pdf'
                response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                footer_template=footer_template, header_template=header_template, 
                                                template=template, context=context)
                pdf_data = io.BytesIO(response.rendered_content)

                pdf_file_path = MEDIA_URL+ quotation_file_name
                with open(pdf_file_path, 'wb') as f:
                    f.write(pdf_data.getbuffer())
    
                return JsonResponse(
                    {
                        'pdf_url': 'http://'+str(request.get_host())+'/'+str(pdf_file_path),
                    })
            else:
                messages.error(request, forms.errors)
                print('errors', forms.errors)  
        elif 'submit' in request.POST:
            quotations_del = Temp_Quotations.objects.filter(estimations=estimation.id, is_draft=True)
            quotations_del.delete()
            if forms.is_valid() and quotation_note_form.is_valid() and provisions_form.is_valid():
                form_obj = forms.save(commit=False)
                form_obj.estimations_version = estimation.version
                form_obj.created_by = request.user
                form_obj.is_draft = False
                if quotation_type == '1':
                    form_obj.q_type = 1
                else:
                    form_obj.q_type = 2
                if template_id:
                    form_obj.template_id = int(template_id)
                    form_obj.estimations = estimation
                    form_obj.save()
                else:
                    messages.error(request, 'Please Select a Template')
                    return redirect('create_quotation_base', pk=enquiry.id, version=version)

                if enquiry.enquiry_type == 1:
                    form_obj.prepared_for.add(prepared_by)
                    form_obj.represented_by_id = represented_by
                    quotation_customer = Contacts.objects.get(pk=represented_by).customer
                    form_obj.quotation_customer_id = quotation_customer
                
                form_obj.save()

                for item in provisions_form:
                    if item.is_valid():
                        item_obj = item.save(commit=False)
                        if not item_obj.provision_cost == 0:
                            item_obj.quotation = form_obj
                            item_obj.save()
                    else:
                        messages.error(request, item.errors)
                        print("items-error==>", item.errors)

                est_version = EstimationVersions.objects.get(
                    pk=estimation.version.id)
                est_version.status = 10
                est_version.save()
                quotation_note_obj = quotation_note_form.save(commit=False)
                quotation_note_obj.quotation = form_obj
                quotation_note_obj.created_by = request.user
                # try:
                #     tags = Tags.objects.get(Q(pk=1)| Q(tag_name='Quotation'))
                # except:
                #     tags = Tags(created_by=request.user, tag_name='Quotation', tag_color='#175899')
                #     tags.save()
                # quotation_note_obj.tag = tags
                quotation_note_obj.save()
            
            
                note = Temp_EstimationNotes(created_by=request.user, created_date=time(), estimation=estimation, \
                                    notes=quotation_note_obj.quotation_notes, note_status=10)
                note.save()
                provisions_obj = Temp_Quotation_Provisions.objects.filter(quotation=form_obj).order_by('id')
                message = 'Created New Quotation #'+form_obj.quotation_id+' in Original (Cart).' \
                    if estimation.version.version == '0' else 'Created New Quotation #'+form_obj.quotation_id\
                        +' Revision '+str(estimation.version.version)+' (Cart).'
                enquiry_logger(enquiry=enquiry, message=message, action=1, user=request.user)
                update_pricing_summary(request, estimation.id)
                messages.success(request, "Quotation Created Successfully")
                if estimation.enquiry.enquiry_type == 1:
                    context={
                            'quotations': form_obj,
                            "specifications_obj": specifications_obj,
                            "buildings": buildings,
                            "filter_by_boq": False,
                            "provisions_obj": provisions_obj,
                        }
                    cmd_options = {
                        'quiet': True, 
                        'enable-local-file-access': True, 
                        'margin-top': '38mm', 
                        'header-spacing': 5,
                        'minimum-font-size': 12,
                        'page-size': 'A4',
                        'encoding': "UTF-8",
                        'print-media-type': True,
                        'footer-right': "[page] / [topage]",
                        'footer-font-size': 8,
                    }
                    quotation_file_name = str(estimation.enquiry.title)+'_Quotation.pdf'
                    clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                    footer_template=footer_template, header_template=header_template, 
                                                    template=template, context=context)
                    pdf_data = io.BytesIO(response.rendered_content)
                    version_str = 'Original' if estimation.version.version == '0' else 'Revision '+str(estimation.version.version)
                    if estimation.enquiry.enquiry_type == 1:
                        pdf_file_path = MEDIA_URL+ 'Quotations/' + str(estimation.enquiry.enquiry_id) + '/' +\
                            str(estimation.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
                        folder = MEDIA_URL+ 'Quotations/' + str(estimation.enquiry.enquiry_id) + '/' +\
                            str(estimation.enquiry.main_customer.name) + '/'+str(version_str)
                        if not os.path.exists(folder):
                            os.makedirs(folder)
                        with open(pdf_file_path, 'wb') as f:
                            f.write(pdf_data.getbuffer())
                    
                return JsonResponse({'url': 'http://'+str(request.get_host())+'/Estimation/temp_estimation_quotations_list/'+ str(form_obj.estimations.id) +'/'})
            else:
                messages.error(request, forms.errors)
                print('errors', forms.errors)
        else:
            quotation = Temp_Quotations.objects.get(estimations__enquiry=pk, is_draft=True)    
            quotation.is_draft = False
            quotation.save()
            
            est_version = EstimationVersions.objects.get(
                    pk=quotation.estimations.version.id)
            est_version.status = 10
            est_version.save()
            provisions_obj = Temp_Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
            
            message = 'Created New Quotation #'+quotation.quotation_id+' in Original (Cart).' \
                if quotation.estimations.version.version == '0' else 'Created New Quotation #'+quotation.quotation_id\
                    +' Revision '+str(quotation.estimations.version.version)+' (Cart).'
            enquiry_logger(enquiry=quotation.estimations.enquiry, message=message, action=1, user=request.user)
            update_pricing_summary(request, estimation.id)
            messages.success(request, "Quotation Created Successfully")
            if estimation.enquiry.enquiry_type == 1:
                context={
                        'quotations': quotation,
                        "specifications_obj": specifications_obj,
                        "buildings": buildings,
                        "filter_by_boq": False,
                        "provisions_obj": provisions_obj,
                    }
                cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '38mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 12,
                    'page-size': 'A4',
                    'encoding': "UTF-8",
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,
                }
                quotation_file_name = str(estimation.enquiry.title)+'_Quotation.pdf'
                clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                footer_template=footer_template, header_template=header_template, 
                                                template=template, context=context)
                pdf_data = io.BytesIO(response.rendered_content)

                version_str = 'Original' if estimation.version.version == '0' else 'Revision '+str(estimation.version.version)
                if estimation.enquiry.enquiry_type == 1:
                    pdf_file_path = MEDIA_URL+ 'Quotations/' + str(estimation.enquiry.enquiry_id) + '/' +\
                        str(estimation.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
                    folder = MEDIA_URL+ 'Quotations/' + str(estimation.enquiry.enquiry_id) + '/' +\
                        str(estimation.enquiry.main_customer.name) + '/'+str(version_str)
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    with open(pdf_file_path, 'wb') as f:
                        f.write(pdf_data.getbuffer())
                    
            return redirect('temp_estimation_quotations_list', pk=quotation.estimations.id)
    context = {
        'title': PROJECT_NAME + ' | Create Quotation',
        'forms': forms,
        'pk': pk,
        'version': estimation,
        'enquiry': enquiry,
        'enquiry_obj': enquiry,
        'represent': represent,
        'buildings': buildings,
        'specifications_obj': specifications_obj,
        'quotation_id': quotation_id,
        'provisions_form': provisions_form,
        'quotation_template': quotation_template,
        'templates': templates,
        'quotation_note_form': quotation_note_form,
        'tinymc_api': TINYMC_API,
        'estimation_objs': estimation_objs,
        
    }
    print('estimation==>', estimation)
    return render(request, 'Enquiries/quotations/create_quotation_base.html', context)


@login_required(login_url='signin')
@permission_required(['estimations.add_estimationmainproduct'], login_url='permission_not_allowed')
def product_duplicate(request, pk):
    """
    This function duplicates a product in an estimation and its associated data.
    """
    main_product = EstimationMainProduct.objects.get(pk=pk)
    buildings = EstimationBuildings.objects.filter(
        estimation=main_product.building.estimation).order_by('id')
    associated_product = EstimationMainProduct.objects.filter(
        main_product=main_product, product_type=2, disabled=False).order_by('id')
    aluminium_obj = MainProductAluminium.objects.get(
        estimation_product=main_product)
    
    try:
        series = Profile_Kit.objects.get(pk=main_product.series.id)
    except Exception as e:
        series = None
        
    covercaps = CoverCap_PressurePlates.objects.all()
    if series or not main_product.category.handrail:
        kit_items = Profile_items.objects.filter(profile_kit=series).order_by('id')
        mullion = ''
        transom = ''
        t_profile = ''
        
        for item in kit_items:
            if((item.parts.parts.parts_name).lower() == 'mullion'):
                mullion = item.formula
            
            if((item.parts.parts.parts_name).lower() == 'transom'):
                transom = item.formula
            
            if((item.parts.parts.parts_name).lower() == 't-profile'):
                t_profile = item.formula
    else:
        mullion = ''
        transom = ''
        kit_items = None
        t_profile = ''
        
    
    try:
        glass_objs = MainProductGlass.objects.get(
            estimation_product=main_product, glass_primary=True)
        second_glass_obj = MainProductGlass.objects.filter(
            estimation_product=main_product, glass_primary=False).order_by('id')
    except Exception as e:
        glass_objs = None
        second_glass_obj = None
    try:
        silicon_obj = MainProductSilicon.objects.get(
            estimation_product=main_product)
    except Exception as e:
        silicon_obj = None
    pricing_control = PricingOption.objects.get(
        estimation_product=main_product)

    addons = MainProductAddonCost.objects.filter(
        estimation_product=main_product).order_by('id')
    if request.method == 'POST':
        width = request.POST.get('width')
        height = request.POST.get('height')
        quantity = request.POST.get('quantity')
        product_type = request.POST.get('product_type')
        product_description = request.POST.get('product_description')
        new_area = request.POST.get('new_area')
        new_al_quoted_price = request.POST.get('new_al_quoted_price')
        new_glass_quoted_price = request.POST.get('new_glass_quoted_price')
        new_al_total_weight = request.POST.get('new_al_total_weight')

        enable_divisions = request.POST.get('enable_divisions')
        horizontal = request.POST.get('horizontal')
        vertical = request.POST.get('vertical')
        new_total_linear_meter = request.POST.get('new_total_linear_meter')
        new_unit_weight = request.POST.get('new_unit_weight')
        building = request.POST.get('duplicating_modal_building')
        
        external_lm = request.POST.get('external_lm')
        internal_lm = request.POST.get('internal_lm')
        polyamide_lm = request.POST.get('polyamide_lm')
        transom_lm = request.POST.get('transom_lm')
        mullion_lm = request.POST.get('mullion_lm')
        epdm_lm = request.POST.get('epdm_lm')
        
        sealant_quote_price = request.POST.get('sealant_quote_price')
    
        data = {
            'width': width,
            'height': height,
            'quantity': quantity,
            'product_type': product_type,
            'product_description': product_description,
            'new_area': new_area,
            'new_al_quoted_price': new_al_quoted_price,
            'new_al_total_weight': new_al_total_weight,
            'new_glass_quoted_price': new_glass_quoted_price,

            'enable_divisions': enable_divisions,
            'horizontal': horizontal,
            'vertical': vertical,
            'new_total_linear_meter': new_total_linear_meter,
            'new_unit_weight': new_unit_weight,
            'building': building,
            'kit_items': kit_items,
            'mullion': mullion,
            'transom': transom ,
            'covercaps': covercaps,
            
            'external_lm': external_lm,
            'internal_lm': internal_lm,
            'polyamide_lm': polyamide_lm,
            'transom_lm': transom_lm,
            'mullion_lm': mullion_lm,
            'epdm_lm': epdm_lm,
            't_profile': t_profile,
            'sealant_quote_price': sealant_quote_price,
        }
        associated_key = associated_key_gen(main_product.building.estimation.enquiry.title)
            
        prev_main_id = main_product_duplicate(
            request=request, pk=pk, data=data, associated_key=associated_key)

        try:
            if associated_product:
                for product in associated_product:
                    product_id = product.id
                    try:
                        main_product_obj_1 = product
                        main_product_obj_1.pk = None
                        main_product_obj_1.created_date = time()
                        main_product_obj_1.building_id = data['building']
                        main_product_obj_1.main_product = prev_main_id
                        main_product_obj_1.save()
                        main_product_obj_1.associated_key = str(associated_key)+str(prev_main_id.id)
                        main_product_obj_1.product_index = set_index(request, main_product_obj_1.building.id)
                        main_product_obj_1.save()
                    except Exception as e:
                        print('Exception associate Main==>', e)

                    if product.is_accessory:
                        try:
                            accessory_obj = MainProductAccessories.objects.filter(
                                estimation_product=product_id)
                            for accessory in accessory_obj:
                                accessory.pk = None
                                accessory.estimation_product = main_product_obj_1
                                accessory.created_date = time()
                                accessory.save()
                        except Exception as e:
                            print("AccessoriesKit Exception: ", e)
                        

                    try:
                        alumin_obj = MainProductAluminium.objects.get(
                            estimation_product=product_id)
                        main_aluminium = MainProductAluminium.objects.get(
                            estimation_product=product.main_product.id)
                        alumin_obj.total_quantity = float(alumin_obj.quantity)*float(main_aluminium.quantity)
                        alumin_obj.pk = None
                        alumin_obj.estimation_product = main_product_obj_1
                        alumin_obj.created_date = time()
                        alumin_obj.save()
                    except Exception as e:
                        print('Exception associate Alum==>', e)
                    try:
                        glass_obj = MainProductGlass.objects.get(
                            estimation_product=product_id, glass_primary=True)
                        glass_obj.pk = None
                        glass_obj.estimation_product = main_product_obj_1
                        glass_obj.created_date = time()
                        glass_obj.save()
                    except Exception:
                        pass

                    try:
                        second_glass_obj = MainProductGlass.objects.filter(
                            estimation_product=product_id, glass_primary=False)
                        for second_glass in second_glass_obj:
                            second_glass.pk = None
                            second_glass.estimation_product = main_product_obj_1
                            second_glass.created_date = time()
                            second_glass.save()
                    except Exception:
                        pass

                    try:
                        silicon_obj = MainProductSilicon.objects.get(
                            estimation_product=product_id)
                        silicon_obj.pk = None
                        silicon_obj.estimation_product = main_product_obj_1
                        silicon_obj.created_date = time()    
                        silicon_obj.save()
                    except Exception:
                        pass

                    try:
                        addon_obj = MainProductAddonCost.objects.filter(estimation_product=product_id)
                        for addon in addon_obj:
                            addon.pk = None
                            addon.estimation_product = main_product_obj_1
                            addon.created_date = time()
                            addon.save()
                    except Exception:
                        pass
                    associated_datas = EstimationProduct_Associated_Data.objects.filter(
                        associated_product=product_id)
                    for associated_data in associated_datas:
                        associated_data.pk = None
                        associated_data.estimation_main_product = prev_main_id
                        associated_data.associated_product = main_product_obj_1
                        associated_data.save()
                    try:
                        pricing_obj = PricingOption.objects.get(
                            estimation_product=product_id)
                        pricing_obj.pk = None
                        pricing_obj.estimation_product = main_product_obj_1
                        pricing_obj.created_date = time()
                        pricing_obj.save()
                    except Exception:
                        pass
                    
            update_pricing_summary(request, main_product.building.estimation.id)
            main_productminimum_price = min_price_setup(request, main_product.id)
            main_product.minimum_price = main_productminimum_price
            # main_product.product_index = set_index(request, main_product.building.id)
            main_product.save()
            
            messages.success(request, "Product Duplicated Successfully")
        except Exception as e:
            print("EXC_2==>", e)
            
        message = str(main_product.product.product_name) +' Product Duplicated in '+str(main_product.building.building_name)\
            +' Building in Original.' if main_product.product else str(main_product.panel_product.product_name) +\
                ' Product Duplicated in '+str(main_product.building.building_name)+' Building Original.' \
                    if main_product.building.estimation.version.version == '0' else str(main_product.product.product_name) \
                        +' Product Duplicated in '+str(main_product.building.building_name)+' Building in Revision '+\
                            str(main_product.building.estimation.version.version) if main_product.product else \
                                str(main_product.panel_product.product_name) +' Product Duplicated in '+str(main_product.building.building_name)+\
                                    ' Building Revision '+str(main_product.building.estimation.version.version)
        enquiry_logger(enquiry=main_product.building.estimation.enquiry, message=message , action=1, user=request.user)
        return redirect('estimation_list_enquiry', pk=main_product.building.estimation.id)
    
    context = {
        "aluminium_obj": aluminium_obj,
        "main_product": main_product,
        "glass_objs": glass_objs,
        "pricing_control": pricing_control,
        "addons": addons,
        "silicon_obj": silicon_obj,
        "second_glass_obj": second_glass_obj,
        "buildings": buildings,
        "kit_items": kit_items,
        'mullion': mullion,
        'transom': transom ,
        'covercaps': covercaps,
        't_profile': t_profile,
    }
    return render(request, 'Estimation/estimation_product_duplicate_modal.html', context)


@login_required(login_url='signin')
@permission_required(['estimations.add_estimationmainproduct'], login_url='permission_not_allowed')
def temp_product_duplicate(request, pk):
    """
    This function duplicates a product in a temporary estimation and saves it with associated data.
    """
    main_product = Temp_EstimationMainProduct.objects.get(pk=pk)
    buildings = Temp_EstimationBuildings.objects.filter(
        estimation=main_product.building.estimation).order_by('id')
    associated_product = Temp_EstimationMainProduct.objects.filter(
        main_product=main_product, product_type=2, disabled=False).order_by('id')
    aluminium_obj = Temp_MainProductAluminium.objects.get(
        estimation_product=main_product)
    try:
        series = Profile_Kit.objects.get(pk=main_product.series.id)
    except Exception as e:
        series = None
    covercaps = CoverCap_PressurePlates.objects.all()
    if series:
        kit_items = Profile_items.objects.filter(profile_kit=series).order_by('id')
        mullion = ''
        transom = ''
        t_profile = ''
    
        for item in kit_items:
            if((item.parts.parts.parts_name).lower() == 'mullion'):
                mullion = item.formula
            
            if((item.parts.parts.parts_name).lower() == 'transom'):
                transom = item.formula
                
            if((item.parts.parts.parts_name).lower() == 't-profile'):
                t_profile = item.formula
    else:
        mullion = ''
        transom = ''
        kit_items = None
        t_profile = ''
    try:
        glass_objs = Temp_MainProductGlass.objects.get(
            estimation_product=main_product, glass_primary=True)
        second_glass_obj = Temp_MainProductGlass.objects.filter(
            estimation_product=main_product, glass_primary=False).order_by('id')
    except Exception as e:
        glass_objs = None
        second_glass_obj = None
    try:
        silicon_obj = Temp_MainProductSilicon.objects.get(
            estimation_product=main_product)
    except Exception as e:
        silicon_obj = None
    pricing_control = Temp_PricingOption.objects.get(
        estimation_product=main_product)
    addons = Temp_MainProductAddonCost.objects.filter(
        estimation_product=main_product).order_by('id')
    if request.method == 'POST':
        width = request.POST.get('width')
        height = request.POST.get('height')
        quantity = request.POST.get('quantity')
        product_type = request.POST.get('product_type')
        product_description = request.POST.get('product_description')
        new_area = request.POST.get('new_area')
        new_al_quoted_price = request.POST.get('new_al_quoted_price')
        new_glass_quoted_price = request.POST.get('new_glass_quoted_price')
        new_al_total_weight = request.POST.get('new_al_total_weight')

        enable_divisions = request.POST.get('enable_divisions')
        horizontal = request.POST.get('horizontal')
        vertical = request.POST.get('vertical')
        new_total_linear_meter = request.POST.get('new_total_linear_meter')
        new_unit_weight = request.POST.get('new_unit_weight')
        building = request.POST.get('duplicating_modal_building')

        external_lm = request.POST.get('external_lm')
        internal_lm = request.POST.get('internal_lm')
        polyamide_lm = request.POST.get('polyamide_lm')
        transom_lm = request.POST.get('transom_lm')
        mullion_lm = request.POST.get('mullion_lm')
        epdm_lm = request.POST.get('epdm_lm')
        sealant_quote_price = request.POST.get('sealant_quote_price')

        data = {
            'width': width,
            'height': height,
            'quantity': quantity,
            'product_type': product_type,
            'product_description': product_description,
            'new_area': new_area,
            'new_al_quoted_price': new_al_quoted_price,
            'new_al_total_weight': new_al_total_weight,
            'new_glass_quoted_price': new_glass_quoted_price,

            'enable_divisions': enable_divisions,
            'horizontal': horizontal,
            'vertical': vertical,
            'new_total_linear_meter': new_total_linear_meter,
            'new_unit_weight': new_unit_weight,
            'building': building,
            'covercaps': covercaps,
            
            'external_lm': external_lm,
            'internal_lm': internal_lm,
            'polyamide_lm': polyamide_lm,
            'transom_lm': transom_lm,
            'mullion_lm': mullion_lm,
            'epdm_lm': epdm_lm,
            't_profile': t_profile,
            'sealant_quote_price': sealant_quote_price,
        }
        associated_key = associated_key_gen(main_product.building.estimation.enquiry.title)
        prev_main_id = main_product_duplicate(
            request=request, pk=pk, data=data, associated_key=associated_key)

        if associated_product:
            for product in associated_product:
                product_id = product.id
                try:
                    main_product_obj_1 = product
                    main_product_obj_1.pk = None
                    main_product_obj_1.created_date = time()
                    main_product_obj_1.building_id = data['building']
                    main_product_obj_1.main_product = prev_main_id
                    main_product_obj_1.save()
                    main_product_obj_1.associated_key = str(associated_key)+str(prev_main_id.id)
                    main_product_obj_1.save()
                except Exception as e:
                    print('Exception associate Main==>', e)
                if product.is_accessory:
                    try:
                        accessory_obj = Temp_MainProductAccessories.objects.filter(
                            estimation_product=product_id)
                        for accessory in accessory_obj:
                            accessory.pk = None
                            accessory.estimation_product = main_product_obj_1
                            accessory.created_date = time()
                            accessory.save()
                    except Exception as e:
                        print("AccessoriesKit Exception: ", e)

                try:
                    alumin_obj = Temp_MainProductAluminium.objects.get(
                        estimation_product=product_id)
                    main_aluminium = Temp_MainProductAluminium.objects.get(
                            estimation_product=product.main_product.id)
                    alumin_obj.total_quantity = float(alumin_obj.quantity)*float(main_aluminium.quantity)
                    alumin_obj.pk = None
                    alumin_obj.estimation_product = main_product_obj_1
                    alumin_obj.created_date = time()
                    alumin_obj.save()
                except Exception as e:
                    print('Exception associate Alum==>', e)
                try:
                    glass_obj = Temp_MainProductGlass.objects.get(
                        estimation_product=product_id)
                    glass_obj.pk = None
                    glass_obj.estimation_product = main_product_obj_1
                    glass_obj.created_date = time()
                    glass_obj.save()
                except Exception:
                    pass
                try:
                    silicon_obj = Temp_MainProductSilicon.objects.get(
                        estimation_product=product_id)
                    silicon_obj.pk = None
                    silicon_obj.estimation_product = main_product_obj_1
                    silicon_obj.created_date = time()
                    silicon_obj.save()
                except Exception:
                    pass
                try:
                    addon_obj = Temp_MainProductAddonCost.objects.filter(
                        estimation_product=product_id)
                    for addon in addon_obj:
                        addon.pk = None
                        addon.estimation_product = main_product_obj_1
                        addon.created_date = time()
                        addon.save()
                except Exception:
                    pass
                associated_datas = Temp_EstimationProduct_Associated_Data.objects.filter(
                    associated_product=product_id)
                for associated_data in associated_datas:
                    associated_data.pk = None
                    associated_data.estimation_main_product = prev_main_id
                    associated_data.associated_product = main_product_obj_1
                    # associated_data.is_deducted = associated_data.is_deducted
                    associated_data.save()
                try:
                    pricing_obj = Temp_PricingOption.objects.get(
                        estimation_product=product_id)
                    pricing_obj.pk = None
                    pricing_obj.estimation_product = main_product_obj_1
                    pricing_obj.created_date = time()
                    pricing_obj.save()
                except Exception:
                    pass
            main_productminimum_price = min_price_setup(request, product.id)
            product.minimum_price = main_productminimum_price
            product.product_index = set_index(request, product.building.id)
            product.save()
            
        message = str(main_product.product.product_name) +' Product Duplicated in '+str(main_product.building.building_name)\
            +' Building in Original (Cart).' if main_product.product else main_product.panel_product +\
                ' Product Duplicated in '+main_product.building.building_name+' Building Original (Cart).' \
                    if main_product.building.estimation.version.version == '0' else main_product.product.product_name \
                        +' Product Duplicated in '+str(main_product.building.building_name)+' Building in Revision '+\
                            str(main_product.building.estimation.version.version)+' (Cart).' if main_product.product else \
                                str(main_product.panel_product) +' Product Duplicated in '+str(main_product.building.building_name)+\
                                    ' Building Revision '+str(main_product.building.estimation.version.version)+' (Cart).'
        
        update_pricing_summary(request, main_product.building.estimation.id)
        
        enquiry_logger(enquiry=main_product.building.estimation.enquiry, message=message, action=1, user=request.user)
        messages.success(request, "Product Duplicated Successfully")
        return redirect('temp_estimation_list_enquiry', pk=main_product.building.estimation.id)

    context = {
        "aluminium_obj": aluminium_obj,
        "main_product": main_product,
        "glass_objs": glass_objs,
        "pricing_control": pricing_control,
        "addons": addons,
        "silicon_obj": silicon_obj,
        "second_glass_obj": second_glass_obj,
        "buildings": buildings,
        "kit_items": kit_items,
        'mullion': mullion,
        'transom': transom ,
        'covercaps': covercaps
    }
    return render(request, 'Estimation/estimation_product_duplicate_modal.html', context)


@login_required(login_url='signin')
@permission_required(['estimations.add_estimationbuildings'], login_url='permission_not_allowed')
def building_duplicate(request, pk):
    """
    This function duplicates a building and returns a JSON response indicating success.
    """
    building_duplicate_function(request, pk)
    
    data = {
        "Success": True
    }
    return JsonResponse(data, status=200)


@login_required(login_url='signin')
@permission_required(['estimations.add_estimationbuildings'], login_url='permission_not_allowed')
def temp_building_duplicate(request, pk):
    """
    This function duplicates a building and returns a JSON response indicating success.
    """
    building_duplicate_function(request, pk)
    data = {
        "Success": True
    }
    return JsonResponse(data, status=200)


@login_required(login_url='signin')
def get_alumin_products(request, pk):
    """
    This function retrieves distinct products from the Profile_Kit model based on a given category and
    renders them in an HTML dropdown menu.
    """
    data_obj = Profile_Kit.objects.filter(system__category=pk).distinct('product')
    return render(request, 'Enquiries/dropdowns/aluminium_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_alumin_custom_products(request, pk):
    """
    The function `get_alumin_custom_products` retrieves a list of products from the database based on a
    given product category and renders a template with the retrieved data.
    """
    data_obj = Product.objects.filter(product_category=pk)
    return render(request, 'Enquiries/dropdowns/aluminium_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_alumin_brand(request, pk):
    """
    This function retrieves distinct system values from the Profile_Kit model based on a given product
    and renders them in an HTML dropdown menu.
    """
    data_obj = Profile_Kit.objects.filter(product=pk).distinct('system')
    return render(request, 'Enquiries/dropdowns/aluminium_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_alumin_specification(request, pk, product):
    """
    This function retrieves aluminum specifications based on a given system and product and renders them
    in a dropdown menu.
    """
    data_obj = Profile_Kit.objects.filter(system=pk, product=product).distinct('profile_type')
    return render(request, 'Enquiries/dropdowns/aluminium_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_alumin_series(request, pk, product):
    """
    This function retrieves a distinct list of profile series from the Profile_Kit model based on the
    given profile type and product, and renders it in an HTML template.
    """
    data_obj = Profile_Kit.objects.filter(profile_type=pk, product=product).distinct('profile_series')
    return render(request, 'Enquiries/dropdowns/aluminium_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_panel_categories_glass(request, pk):
    """
    This function retrieves panel categories that are made of glass and renders them in a dropdown menu
    for use in an enquiry form.
    """
    data_obj = PanelMasterBase.objects.filter(panel_category__is_glass=True)
    return render(request, 'Enquiries/dropdowns/panel_category_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_panel_categories_panels(request, pk):
    """
    This function retrieves panel categories that are not made of glass and renders them in a dropdown
    menu.
    """
    data_obj = PanelMasterBase.objects.filter(panel_category__is_glass=False)
    return render(request, 'Enquiries/dropdowns/panel_category_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_panel_categories_all(request, pk):
    """
    This function retrieves all objects from the PanelMasterBase model and renders them in a dropdown
    menu on a webpage.
    """
    data_obj = PanelMasterBase.objects.all()
    return render(request, 'Enquiries/dropdowns/panel_category_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_panel_brand(request, pk):
    """
    This function retrieves a list of panel brands based on a given panel category ID and renders it in
    a dropdown menu format for a web page.
    """
    category = PanelMasterBase.objects.get(pk=pk).panel_category.id
    data_obj = PanelMasterBrands.objects.filter(panel_category=category)
    return render(request, 'Enquiries/dropdowns/panel_brands_dropdown.html', {'data_obj': data_obj})

@login_required(login_url='signin')
def get_panel_brand_for_sales_spec(request, pk):
    """
    This function retrieves a list of panel brands based on a given panel category ID and renders it in
    a dropdown menu format for a web page.
    """
    category = Category.objects.get(pk=pk)
    data_obj = PanelMasterBrands.objects.filter(panel_category=category)
    return render(request, 'Enquiries/dropdowns/panel_brands_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_panel_products(request, pk):
    """
    This function retrieves products related to a panel category and renders them in a dropdown menu.
    """
    category = PanelMasterBase.objects.get(pk=pk)
    products = Product.objects.filter(product_category=category.panel_category.id)
    return render(request, 'Enquiries/dropdowns/glass_products.html', {'data_obj': products})

@login_required(login_url='signin')
def get_panel_products_for_sales_spec(request, pk):
    """
    This function retrieves products related to a panel category and renders them in a dropdown menu.
    """
    category = Category.objects.get(pk=pk)
    products = Product.objects.filter(product_category=category.id)
    return render(request, 'Enquiries/dropdowns/glass_products.html', {'data_obj': products})


@login_required(login_url='signin')
def get_panel_brand_for_estimation_product(request, estimation, pk):
    """
    This function retrieves a list of distinct panel brands for a given category in an estimation and
    renders it in a dropdown menu.
    """
    try:
        category = Category.objects.get(pk=pk)
    except Exception as e:
        category = None
        
    if category:
        data_obj = EnquirySpecifications.objects.filter(
            estimation=estimation, categories=category).distinct('panel_brand')
    else:
        data_obj = None
        
    return render(request, 'Enquiries/dropdowns/aluminium_brand_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_panel_brand_for_estimation_product_temp(request, estimation, pk):
    """
    This function retrieves a list of panel brands for a specific panel category in an estimation and
    renders it in a dropdown menu.
    """
    try:
        # panel_category = PanelMasterBase.objects.get(panel_category=pk)
        panel_category = Category.objects.get(pk=pk)
    except:
        panel_category = None
    if panel_category:
        data_obj = Temp_EnquirySpecifications.objects.filter(
            estimation=estimation, categories=panel_category).distinct('panel_brand')
    else:
        data_obj = None
    return render(request, 'Enquiries/dropdowns/aluminium_brand_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_panel_series(request, pk):
    """
    This function retrieves a list of panel series based on a given panel master brand and renders it in
    an HTML dropdown menu.
    """
    master_brand = PanelMasterBrands.objects.get(pk=pk)
    data_obj = PanelMasterSeries.objects.filter(brands=master_brand)
    return render(request, 'Enquiries/dropdowns/aluminium_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_panel_series_for_estimation_product(request, estimation, pk):
    """
    This function retrieves a list of distinct panel series for a specific panel brand in an estimation
    and renders it in a dropdown menu.
    """
    data_obj = EnquirySpecifications.objects.filter(
        estimation=estimation, panel_brand=pk).distinct('panel_series')
    return render(request, 'Estimation/dropdowns/series_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_panel_series_for_estimation_product_temp(request, estimation, pk):
    """
    This function retrieves a list of distinct panel series for a given estimation and panel brand and
    renders it in a dropdown menu.
    """
    data_obj = Temp_EnquirySpecifications.objects.filter(
        estimation=estimation, panel_brand=pk).distinct('panel_series')
    return render(request, 'Estimation/dropdowns/series_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_panel_specification(request, pk):
    """
    This function retrieves panel specifications based on a given series ID and renders them in an HTML
    dropdown menu.
    """
    data_obj = PanelMasterSpecifications.objects.filter(series=pk).order_by('-id')
    return render(request, 'Enquiries/dropdowns/aluminium_dropdown.html', {'data_obj': data_obj})


@login_required(login_url='signin')
def get_panel_specification_for_estimation_product(request, estimation, pk, spec=None):
    """
    This function retrieves panel product specifications for an estimation and panel series and renders
    them in a dropdown menu.
    """
    data_obj = EnquirySpecifications.objects.filter(estimation=estimation, panel_series=pk).distinct('panel_product')
    if not spec:
        return render(request, 'Enquiries/dropdowns/panel_product_dropdown.html', {'data_obj': data_obj, 'spec': spec})
    else:
        return render(request, 'Enquiries/dropdowns/panel_product_dropdown.html', {'data_obj': data_obj, 'spec': spec})


@login_required(login_url='signin')
def get_panel_specification_for_estimation_product_temp(request, estimation, pk, spec=None):
    """
    This function retrieves panel product specifications for a given estimation and panel series and
    renders them in a dropdown menu.
    """
    data_obj = Temp_EnquirySpecifications.objects.filter(
        estimation=estimation, panel_series=pk).distinct('panel_product')
    if not spec:
        return render(request, 'Enquiries/dropdowns/panel_product_dropdown.html', {'data_obj': data_obj})
    else:
        return render(request, 'Enquiries/dropdowns/panel_product_dropdown.html', {'data_obj': data_obj})
        

@login_required(login_url='signin')
@permission_required(['Categories.view_category'], login_url='permission_not_allowed')
def get_category_dimension(request, pk):
    """
    This function retrieves data from a Category object and returns it as a JSON response.
    """
    category_data = Category.objects.get(pk=pk)

    if category_data.one_D and category_data.two_D:
        both = True
    else:
        both = False
        
    if category_data.is_ployamide_gasket:
        ployamide_gasket = category_data.ployamide_gasket.id
        ployamide_gasket_name = category_data.ployamide_gasket.sealant_type
    else:
        ployamide_gasket = '#'
        ployamide_gasket_name = None
        
    if category_data.is_transom_gasket:
        transom_gasket = category_data.transom_gasket.id
        transom_gasket_name = category_data.transom_gasket.sealant_type
    else:
        transom_gasket = '#'
        transom_gasket_name = None
        
    if category_data.is_mullion_gasket:
        mullion_gasket = category_data.mullion_gasket.id
        mullion_gasket_name = category_data.mullion_gasket.sealant_type
    else:
        mullion_gasket = '#'
        mullion_gasket_name = None
        
    
    if category_data.internal_sealant and category_data.external_sealant:
        data = {
            "one_d": category_data.one_D,
            "two_d": category_data.two_D,
            "both": both,
            "glass": category_data.is_glass,
            "is_curtain_wall": category_data.is_curtain_wall,
            "sealant": category_data.sealant,
            "points": category_data.points,
            "handrail": category_data.handrail,
            "enable_internal_sealant": category_data.enable_internal_sealant,
            "enable_external_sealant": category_data.enable_external_sealant,
            "internal_sealant": category_data.internal_sealant.id,
            "internal_sealant_name": category_data.internal_sealant.sealant_type,
            "external_sealant_name": category_data.external_sealant.sealant_type,
            "external_sealant": category_data.external_sealant.id,
            "category_id": category_data.id,
            "ployamide_gasket": ployamide_gasket,
            "transom_gasket": transom_gasket,
            "mullion_gasket": mullion_gasket,
            "ployamide_gasket_name": ployamide_gasket_name,
            "transom_gasket_name": transom_gasket_name,
            "mullion_gasket_name": mullion_gasket_name,
            "window_or_door_with_divisions": category_data.window_or_door_with_divisions,
            "door": category_data.door,
        }
    elif category_data.internal_sealant and not category_data.external_sealant:
        data = {
            "one_d": category_data.one_D,
            "two_d": category_data.two_D,
            "both": both,
            "is_curtain_wall": category_data.is_curtain_wall,
            "glass": category_data.is_glass,
            "sealant": category_data.sealant,
            "points": category_data.points,
            "handrail": category_data.handrail,
            "enable_internal_sealant": category_data.enable_internal_sealant,
            "enable_external_sealant": category_data.enable_external_sealant,
            "internal_sealant": category_data.internal_sealant.id,
            "internal_sealant_name": category_data.internal_sealant.sealant_type,
            "category_id": category_data.id,
            "ployamide_gasket": ployamide_gasket,
            "transom_gasket": transom_gasket,
            "mullion_gasket": mullion_gasket,
            "ployamide_gasket_name": ployamide_gasket_name,
            "transom_gasket_name": transom_gasket_name,
            "mullion_gasket_name": mullion_gasket_name,
            "window_or_door_with_divisions": category_data.window_or_door_with_divisions,
            "door": category_data.door,
        }
    elif not category_data.internal_sealant and category_data.external_sealant:
        data = {
            "one_d": category_data.one_D,
            "two_d": category_data.two_D,
            "both": both,
            "is_curtain_wall": category_data.is_curtain_wall,
            "glass": category_data.is_glass,
            "sealant": category_data.sealant,
            "points": category_data.points,
            "handrail": category_data.handrail,
            "enable_internal_sealant": category_data.enable_internal_sealant,
            "enable_external_sealant": category_data.enable_external_sealant,
            "external_sealant_name": category_data.external_sealant.sealant_type,
            "external_sealant": category_data.external_sealant.id,
            "category_id": category_data.id,
            "ployamide_gasket": ployamide_gasket,
            "transom_gasket": transom_gasket,
            "mullion_gasket": mullion_gasket,
            "ployamide_gasket_name": ployamide_gasket_name,
            "transom_gasket_name": transom_gasket_name,
            "mullion_gasket_name": mullion_gasket_name,
            "window_or_door_with_divisions": category_data.window_or_door_with_divisions,
            "door": category_data.door,  
        }
    else:
        data = {
            "one_d": category_data.one_D,
            "two_d": category_data.two_D,
            "both": both,
            "is_curtain_wall": category_data.is_curtain_wall,
            "glass": category_data.is_glass,
            "sealant": category_data.sealant,
            "handrail": category_data.handrail,
            "points": category_data.points,
            "enable_internal_sealant": category_data.enable_internal_sealant,
            "enable_external_sealant": category_data.enable_external_sealant,
            "category_id": category_data.id,
            "ployamide_gasket": ployamide_gasket,
            "transom_gasket": transom_gasket,
            "mullion_gasket": mullion_gasket,
            "ployamide_gasket_name": ployamide_gasket_name,
            "transom_gasket_name": transom_gasket_name,
            "mullion_gasket_name": mullion_gasket_name,
            "window_or_door_with_divisions": category_data.window_or_door_with_divisions,
            "door": category_data.door,
        }
    return JsonResponse(data, status=200)

def check_associated(product):
    try:
        associate_flag = EstimationProduct_Associated_Data.objects.filter(estimation_main_product=product).order_by('id')
    except Exception:
        associate_flag = None
        
    return associate_flag

def generate_product_data(product, temp_product):
    temp_spc = Temp_EnquirySpecifications.objects.get(
        estimation=temp_product.building.estimation, identifier=product.specification_Identifier)
    temp_product.specification_Identifier = temp_spc
    temp_product.save()
    
    accessories_kit = MainProductAccessories.objects.filter(
        estimation_product=product).order_by('id')
    
    for kit in accessories_kit:
        temp_kit = Temp_MainProductAccessories(
            estimation_product=temp_product,
            accessory_item=kit.accessory_item,
            accessory_item_quantity=kit.accessory_item_quantity,
            accessory_item_price=kit.accessory_item_price,
            accessory_item_total=kit.accessory_item_total,
        )
        temp_kit.save()
        
    try:
        alumin_obj = MainProductAluminium.objects.get(
            estimation_product=product)
    except Exception as e:
        alumin_obj = None
        print("ALUM_EXC==>", e)
        
 
    if alumin_obj:
        temp_alumin = Temp_MainProductAluminium(
            estimation_product=temp_product,
            aluminium_pricing=alumin_obj.aluminium_pricing,
            al_price_per_unit=alumin_obj.al_price_per_unit,
            al_price_per_sqm=alumin_obj.al_price_per_sqm,
            al_weight_per_unit=alumin_obj.al_weight_per_unit,
            al_markup=alumin_obj.al_markup,
            pricing_unit=alumin_obj.pricing_unit,
            custom_price=alumin_obj.custom_price,
            al_quoted_price=alumin_obj.al_quoted_price,
            width=alumin_obj.width,
            formula_base=alumin_obj.formula_base,
            height=alumin_obj.height,
            area=alumin_obj.area,
            enable_divisions=alumin_obj.enable_divisions,
            horizontal=alumin_obj.horizontal,
            vertical=alumin_obj.vertical,
            quantity=alumin_obj.quantity,
            total_quantity=alumin_obj.total_quantity,
            total_area=alumin_obj.total_area,
            total_weight=alumin_obj.total_weight,
            product_type=alumin_obj.product_type,
            product_description=alumin_obj.product_description,
            price_per_kg=alumin_obj.price_per_kg,
            weight_per_unit=alumin_obj.weight_per_unit,
            product_configuration=alumin_obj.product_configuration,
            total_linear_meter=alumin_obj.total_linear_meter,
            weight_per_lm=alumin_obj.weight_per_lm,
            surface_finish=alumin_obj.surface_finish,
            curtainwall_type=alumin_obj.curtainwall_type,
            is_conventional=alumin_obj.is_conventional,
            is_two_way=alumin_obj.is_two_way,
            in_area_input=alumin_obj.in_area_input,
        )
        temp_alumin.save()

    glass_obj = MainProductGlass.objects.filter(
        estimation_product=product, glass_primary=True).order_by('id')
    for glass in glass_obj:
        temp_glass = Temp_MainProductGlass(
            estimation_product=temp_product,
            is_glass_cost=glass.is_glass_cost,
            glass_specif=glass.glass_specif,
            total_area_glass=glass.total_area_glass,
            glass_base_rate=glass.glass_base_rate,
            glass_markup_percentage=glass.glass_markup_percentage,
            glass_quoted_price=glass.glass_quoted_price,
            glass_pricing_type=glass.glass_pricing_type,
            glass_width=glass.glass_width,
            glass_height=glass.glass_height,
            glass_area=glass.glass_area,
            glass_quantity=glass.glass_quantity,
            glass_primary=glass.glass_primary,
        )
        temp_glass.save()

    second_glass_obj = MainProductGlass.objects.filter(
        estimation_product=product, glass_primary=False).order_by('id')
    for seco_glass in second_glass_obj:
        temp_second_glass = Temp_MainProductGlass(
            estimation_product=temp_product,
            is_glass_cost=seco_glass.is_glass_cost,
            glass_specif=seco_glass.glass_specif,
            total_area_glass=seco_glass.total_area_glass,
            glass_base_rate=seco_glass.glass_base_rate,
            glass_markup_percentage=seco_glass.glass_markup_percentage,
            glass_quoted_price=seco_glass.glass_quoted_price,
            glass_pricing_type=seco_glass.glass_pricing_type,
            glass_width=seco_glass.glass_width,
            glass_height=seco_glass.glass_height,
            glass_area=seco_glass.glass_area,
            glass_quantity=seco_glass.glass_quantity,
            glass_primary=seco_glass.glass_primary,
        )
        temp_second_glass.save()
    deductions = Deduction_Items.objects.filter(
        estimation_product=product).order_by('id')
    for deduct_item in deductions:
        temp_deduct_item = Temp_Deduction_Items(
            estimation_product=temp_product,
            item_desc=temp_glass,
            main_price=deduct_item.main_price,
            item_width=deduct_item.item_width,
            item_height=deduct_item.item_height,
            item_quantity=deduct_item.item_quantity,
            item_deduction_area=deduct_item.item_deduction_area,
            item_deduction_price=deduct_item.item_deduction_price,
        )
        temp_deduct_item.save()
    merge_data = EstimationMainProductMergeData.objects.filter(estimation_product=product).order_by('id')
    for merge in merge_data:
        temp_merge = Temp_EstimationMainProductMergeData(
            estimation_product=temp_product,
            merge_product=merge.merge_product,
            merged_area=merge.merged_area,
            merged_price=merge.merged_price,
            merge_quantity=merge.merge_quantity,
            merge_aluminium_price=merge.merge_aluminium_price,
            merge_infill_price=merge.merge_infill_price,
            merge_sealant_price=merge.merge_sealant_price,
            merge_accessory_price=merge.merge_accessory_price,
        )
        temp_merge.save()
    silicon_obj = MainProductSilicon.objects.filter(
        estimation_product=product).order_by('id')
    for silicon in silicon_obj:
        temp_silicon = Temp_MainProductSilicon(
            estimation_product=temp_product,
            created_date=silicon.created_date,
            is_silicon=silicon.is_silicon,
            external_lm=silicon.external_lm,
            external_base_rate=silicon.external_base_rate,
            external_markup=silicon.external_markup,
            external_sealant_type=silicon.external_sealant_type,
            internal_lm=silicon.internal_lm,
            internal_base_rate=silicon.internal_base_rate,
            internal_markup=silicon.internal_markup,
            internal_sealant_type=silicon.internal_sealant_type,
            silicon_quoted_price=silicon.silicon_quoted_price,
            
            polyamide_gasket=silicon.polyamide_gasket,
            polyamide_markup=silicon.polyamide_markup,
            polyamide_base_rate=silicon.polyamide_base_rate,
            polyamide_lm=silicon.polyamide_lm,
            transom_gasket=silicon.transom_gasket,
            transom_markup=silicon.transom_markup,
            transom_base_rate=silicon.transom_base_rate,
            transom_lm=silicon.transom_lm,
            mullion_gasket=silicon.mullion_gasket,
            mullion_markup=silicon.mullion_markup,
            mullion_base_rate=silicon.mullion_base_rate,
            mullion_lm=silicon.mullion_lm,
        )
        temp_silicon.save()
        
    pricing = PricingOption.objects.filter(
        estimation_product=product).order_by('id')
    
    for price in pricing:
        
        try:
            temp_pricing = Temp_PricingOption.objects.get_or_create(
                estimation_product=temp_product,
                defaults={
                    'is_pricing_control': price.is_pricing_control,
                    'overhead_perce': price.overhead_perce,
                    'labour_perce': price.labour_perce,
                    'adjust_by_sqm': price.adjust_by_sqm,
                }
            )
            temp_pricing_instance = temp_pricing[0]
            temp_pricing_instance.save()
            
        except Exception as e:
            print("EXCE==>", e)

    addons = MainProductAddonCost.objects.filter(
        estimation_product=product).order_by('id')
    for addon in addons:
        temp_addon = Temp_MainProductAddonCost(
            estimation_product=temp_product,
            addons=addon.addons,
            base_rate=addon.base_rate,
            pricing_type=addon.pricing_type,
            addon_quantity=addon.addon_quantity
        )
        temp_addon.save()
    
    if product.product_type == 2:
        if not Temp_EstimationProduct_Associated_Data.objects.filter(
                estimation_main_product=temp_product.main_product, 
                associated_product=temp_product
            ).exists():
            try:
                associated_pro = EstimationProduct_Associated_Data.objects.get(estimation_main_product=product.main_product, associated_product=product)
            except:
                associated_pro = None
                
            try:
                aluminium = Temp_MainProductAluminium.objects.get(estimation_product=temp_product)
                associated_data = Temp_EstimationProduct_Associated_Data(
                    estimation_main_product=temp_product.main_product,
                    associated_product=temp_product,
                    assoicated_area=aluminium.area,
                    is_deducted= True if associated_pro.is_deducted else False,
                )
                associated_data.save()
            except MainProductAluminium.DoesNotExist:
                pass
                            

@login_required(login_url='signin')
@permission_required(['enquiries.add_estimations'], login_url='permission_not_allowed')
def create_revision(request, pk):
    """
        Create new Revision
    """
    
    if request.method == 'POST':
        due_date = request.POST.get('due_date')
        estimation_select = request.POST.get('estimation_select')
        
        estimation = Estimations.objects.get(pk=estimation_select)
        versions = Estimations.objects.filter(
            enquiry=estimation.enquiry, 
            version__main_version=estimation.version.main_version).order_by('id')
        
        if int(estimation.version.version) < versions.count():
            version_text = int(versions.count())
        else:
            version_text = int(estimation.version.version)+1
        temp_version_check = Temp_Estimations.objects.filter(
            enquiry=estimation.enquiry).order_by('id')
        if temp_version_check:
            messages.error(request, 'Already have a pending version.')
            return redirect('enquiry_profile', pk=estimation.enquiry.id, version=estimation.id)
        else:
            version = EstimationVersions(created_by=request.user, status=9,
                                        version=version_text, main_version=estimation.version.main_version)
            version.save()
            temp_estimation = Temp_Estimations(created_by=estimation.created_by, enquiry=estimation.enquiry,
                                            version=version, inherited_revision=estimation.version, parent_estimation=estimation)
            try:
                # enquiry = Enquiries.objects.get(pk=estimation.enquiry.id)
                temp_estimation.due_date = due_date
                temp_estimation.save()
            except Exception as e:
                print("E==>", e)
                
            temp_estimation.save()
            # enquiry = Enquiries.objects.get(pk=estimation.enquiry.id)
            # enquiry.status = 2
            # enquiry.save()
            
            try:
                price_summary = Pricing_Summary.objects.get(estimation=estimation.id)
            except:
                price_summary = None
            if price_summary:
                temp_pricing_sumary = Temp_Pricing_Summary(
                                            estimation=temp_estimation,
                                            scope_of_work=price_summary.scope_of_work,
                                            product_summary=price_summary.product_summary,
                                            weightage_summary=price_summary.weightage_summary,
                                            material_summary=price_summary.material_summary,
                                            pricing_review_summary=price_summary.pricing_review_summary,
                                            quotation=0.00,
                                        )
                temp_pricing_sumary.save()
                
            estimation_project_spec = EstimationProjectSpecifications.objects.filter(estimations=estimation)
            for estimation_spec in estimation_project_spec:
                temp_estimation_spec = Temp_EstimationProjectSpecifications(
                    specification_header=estimation_spec.specification_header, 
                    estimations=temp_estimation, 
                    specification=estimation_spec.specification)
                temp_estimation_spec.save()
                
            estimation.temp_last_child = temp_estimation
            estimation.save()
            specification_obj = EnquirySpecifications.objects.filter(
                estimation=estimation).order_by('id')
            
            try:
                general_note = Estimation_GeneralNotes.objects.get(estimations=estimation)
                temp_general = Temp_Estimation_GeneralNotes(
                    estimations = temp_estimation,
                    general_notes = general_note.general_notes,
                    created_by = general_note.created_by,
                )
                temp_general.save()
            except Exception as e:
                general_note = None
                
            for spec in specification_obj:
                temp_specification = Temp_EnquirySpecifications(
                    created_by=spec.created_by,
                    estimation=temp_estimation,
                    identifier=spec.identifier,
                    categories=spec.categories,
                    aluminium_products=spec.aluminium_products,
                    aluminium_system=spec.aluminium_system,
                    aluminium_specification=spec.aluminium_specification,
                    aluminium_series=spec.aluminium_series,
                    panel_category=spec.panel_category,
                    panel_brand=spec.panel_brand,
                    panel_series=spec.panel_series,
                    panel_specification=spec.panel_specification,
                    surface_finish=spec.surface_finish,
                    specification_description=spec.specification_description,
                    panel_product=spec.panel_product,
                    specification_type=spec.specification_type,
                    minimum_price=spec.minimum_price,
                )
                temp_specification.save()
                
                
                try:
                    product_complance = EstimationProductComplaints.objects.get(
                        estimation=estimation, specification=spec.id)
                except Exception as e:
                    product_complance = None
                    
                try:
                    temp_spc = Temp_EnquirySpecifications.objects.get(
                        estimation=temp_estimation, identifier=spec.identifier)
                except Exception as e:
                    temp_spc = None
                if product_complance:
                    temp_compnace = Temp_EstimationProductComplaints(
                        estimation=temp_estimation,
                        specification=temp_spc,
                        is_aluminium_complaint=product_complance.is_aluminium_complaint,
                        aluminium_complaint=product_complance.aluminium_complaint,
                        is_panel_complaint=product_complance.is_panel_complaint,
                        panel_complaint=product_complance.panel_complaint,
                        is_surface_finish_complaint=product_complance.is_surface_finish_complaint,
                        surface_finish_complaint=product_complance.surface_finish_complaint,
                    )
                    temp_compnace.save()

            buildings = EstimationBuildings.objects.filter(
                estimation=estimation).order_by('id')

            for build in buildings:
                temp_build = Temp_EstimationBuildings(
                    created_by=build.created_by, estimation=temp_estimation, 
                    building_name=build.building_name, 
                    no_typical_buildings=build.no_typical_buildings, 
                    typical_buildings_enabled=build.typical_buildings_enabled)
                temp_build.save()
                main_product = EstimationMainProduct.objects.filter(
                    building=build, product_type=1).order_by('id', 'associated_key')
                prev_main_id = None
                
                for product in main_product:
                    
                    if not product.associated_key:
                        if product.product_type == 1:
                            try:
                                temp_product = Temp_EstimationMainProduct(
                                    building=temp_build,
                                    created_by=product.created_by,
                                    category=product.category,
                                    product=product.product,
                                    product_type=product.product_type,
                                    panel_product=product.panel_product,
                                    brand=product.brand,
                                    series=product.series,
                                    panel_brand=product.panel_brand,
                                    panel_series=product.panel_series,
                                    uom=product.uom,
                                    accessories=product.accessories,
                                    is_accessory=product.is_accessory,
                                    accessory_quantity=product.accessory_quantity,
                                    tolerance_type=product.tolerance_type,
                                    tolerance=product.tolerance,
                                    is_tolerance=product.is_tolerance,
                                    total_addon_cost=product.total_addon_cost,
                                    is_sourced=product.is_sourced,
                                    supplier=product.supplier,
                                    boq_number=product.boq_number,
                                    enable_addons=product.enable_addons,
                                    accessory_total=product.accessory_total,
                                    is_display_data=product.is_display_data,
                                    display_width=product.display_width,
                                    display_height=product.display_height,
                                    display_area=product.display_area,
                                    display_quantity=product.display_quantity,
                                    display_product_name=product.display_product_name,
                                    display_total_area=product.display_total_area,
                                    deduction_price=product.deduction_price,
                                    deduction_type=product.deduction_type,
                                    deduction_method=product.deduction_method,
                                    after_deduction_price=product.after_deduction_price,
                                    total_associated_area=product.total_associated_area,
                                    deducted_area=product.deducted_area,
                                    product_unit_price=product.product_unit_price,
                                    product_sqm_price=product.product_sqm_price,
                                    product_base_rate=product.product_base_rate,
                                    have_merge=product.have_merge,
                                    merge_price=product.merge_price,
                                    # associated_key=product.associated_key,
                                    product_sqm_price_without_addon=product.product_sqm_price_without_addon,
                                    hide_dimension=product.hide_dimension,
                                    minimum_price=product.minimum_price,
                                    disabled=product.disabled,
                                    product_index=product.product_index,
                                )
                                temp_product.save()
                                temp_product.main_product = temp_product
                                associated_key = associated_key_gen(product.building.estimation.enquiry.title)
                                temp_product.associated_key = str(associated_key)+str(temp_product.id)
                                temp_product.save()
                                prev_main_id = temp_product
                            except Exception as e:
                                print('EXCEPTIONS__1==>', e)
                        else:
                            print('error_1')
                            
                        if product.product_type == 2:
                            try:
                                temp_product = Temp_EstimationMainProduct(
                                    building=temp_build,
                                    created_by=product.created_by,
                                    category=product.category,
                                    product=product.product,
                                    product_type=product.product_type,
                                    panel_product=product.panel_product,
                                    main_product=prev_main_id,
                                    brand=product.brand,
                                    series=product.series,
                                    panel_brand=product.panel_brand,
                                    panel_series=product.panel_series,
                                    uom=product.uom,
                                    accessories=product.accessories,
                                    is_accessory=product.is_accessory,
                                    is_tolerance=product.is_tolerance,
                                    tolerance_type=product.tolerance_type,
                                    tolerance=product.tolerance,
                                    total_addon_cost=product.total_addon_cost,
                                    is_sourced=product.is_sourced,
                                    supplier=product.supplier,
                                    boq_number=product.boq_number,
                                    enable_addons=product.enable_addons,
                                    accessory_total=product.accessory_total,
                                    is_display_data=product.is_display_data,
                                    display_width=product.display_width,
                                    display_product_name=product.display_product_name,
                                    display_height=product.display_height,
                                    display_area=product.display_area,
                                    display_quantity=product.display_quantity,
                                    display_total_area=product.display_total_area,
                                    deduction_price=product.deduction_price,
                                    deduction_type=product.deduction_type,
                                    deduction_method=product.deduction_method,
                                    after_deduction_price=product.after_deduction_price,
                                    total_associated_area=product.total_associated_area,
                                    
                                    deducted_area=product.deducted_area,
                                    product_unit_price=product.product_unit_price,
                                    product_sqm_price=product.product_sqm_price,
                                    product_base_rate=product.product_base_rate,
                                    # associated_key=product.associated_key,
                                    have_merge=product.have_merge,
                                    merge_price=product.merge_price,
                                    product_sqm_price_without_addon=product.product_sqm_price_without_addon,
                                    hide_dimension=product.hide_dimension,
                                    minimum_price=product.minimum_price,
                                    disabled=product.disabled,
                                    product_index=product.product_index,
                                    
                                )
                                temp_product.save()
                                associated_key = associated_key_gen(product.building.estimation.enquiry.title)
                                temp_product.associated_key = str(associated_key)+str(temp_product.id)
                                temp_product.save()

                            except Exception as e:
                                print("EXCEPTIONS__2==>", e)
                        else:
                            print('error_2')
                    else:
                        if product.product_type == 1:
                            # print("product==>", product.id)
                            associated_products = check_associated(product)
                            
                            try:
                                temp_product = Temp_EstimationMainProduct(
                                    building=temp_build,
                                    created_by=product.created_by,
                                    category=product.category,
                                    product=product.product,
                                    product_type=product.product_type,
                                    panel_product=product.panel_product,
                                    brand=product.brand,
                                    series=product.series,
                                    panel_brand=product.panel_brand,
                                    panel_series=product.panel_series,
                                    uom=product.uom,
                                    accessories=product.accessories,
                                    is_accessory=product.is_accessory,
                                    accessory_quantity=product.accessory_quantity,
                                    tolerance_type=product.tolerance_type,
                                    tolerance=product.tolerance,
                                    is_tolerance=product.is_tolerance,
                                    total_addon_cost=product.total_addon_cost,
                                    is_sourced=product.is_sourced,
                                    supplier=product.supplier,
                                    boq_number=product.boq_number,
                                    enable_addons=product.enable_addons,
                                    accessory_total=product.accessory_total,
                                    is_display_data=product.is_display_data,
                                    display_product_name=product.display_product_name,
                                    display_width=product.display_width,
                                    display_height=product.display_height,
                                    display_area=product.display_area,
                                    display_quantity=product.display_quantity,
                                    display_total_area=product.display_total_area,
                                    deduction_price=product.deduction_price,
                                    deduction_type=product.deduction_type,
                                    deduction_method=product.deduction_method,
                                    after_deduction_price=product.after_deduction_price,
                                    total_associated_area=product.total_associated_area,
                                    deducted_area=product.deducted_area,
                                    product_unit_price=product.product_unit_price,
                                    product_sqm_price=product.product_sqm_price,
                                    product_base_rate=product.product_base_rate,
                                    have_merge=product.have_merge,
                                    merge_price=product.merge_price,
                                    # associated_key=product.associated_key,
                                    product_sqm_price_without_addon=product.product_sqm_price_without_addon,
                                    hide_dimension=product.hide_dimension,
                                    minimum_price=product.minimum_price,
                                    disabled=product.disabled,
                                    product_index=product.product_index,                                    
                                    
                                )
                                temp_product.save()
                                temp_product.main_product = temp_product
                                associated_key = associated_key_gen(product.building.estimation.enquiry.title)
                                temp_product.associated_key = str(associated_key)+str(temp_product.id)
                                temp_product.save()
                                prev_main_id = temp_product
                            except Exception as e:
                                print('EXCEPTIONS__1==>', e)
                            
                            if associated_products:
                                for associated_product in associated_products:
                                    assoc = EstimationMainProduct.objects.get(pk=associated_product.associated_product.id)
                                    
                                    try:
                                        temp_product1 = Temp_EstimationMainProduct(
                                            building=temp_build,
                                            created_by=assoc.created_by,
                                            category=assoc.category,
                                            product=assoc.product,
                                            product_type=assoc.product_type,
                                            panel_product=assoc.panel_product,
                                            main_product=prev_main_id,
                                            brand=assoc.brand,
                                            series=assoc.series,
                                            panel_brand=assoc.panel_brand,
                                            panel_series=assoc.panel_series,
                                            uom=assoc.uom,
                                            accessories=assoc.accessories,
                                            is_accessory=assoc.is_accessory,
                                            is_tolerance=assoc.is_tolerance,
                                            tolerance_type=assoc.tolerance_type,
                                            tolerance=assoc.tolerance,
                                            total_addon_cost=assoc.total_addon_cost,
                                            is_sourced=assoc.is_sourced,
                                            supplier=assoc.supplier,
                                            boq_number=assoc.boq_number,
                                            enable_addons=assoc.enable_addons,
                                            accessory_total=assoc.accessory_total,
                                            is_display_data=assoc.is_display_data,
                                            display_width=assoc.display_width,
                                            display_product_name=assoc.display_product_name,
                                            display_height=assoc.display_height,
                                            display_area=assoc.display_area,
                                            display_quantity=assoc.display_quantity,
                                            display_total_area=assoc.display_total_area,
                                            deduction_price=assoc.deduction_price,
                                            deduction_type=assoc.deduction_type,
                                            deduction_method=assoc.deduction_method,
                                            after_deduction_price=assoc.after_deduction_price,
                                            total_associated_area=assoc.total_associated_area,
                                            
                                            deducted_area=assoc.deducted_area,
                                            product_unit_price=assoc.product_unit_price,
                                            product_sqm_price=assoc.product_sqm_price,
                                            product_base_rate=assoc.product_base_rate,
                                            # associated_key=assoc.associated_key,
                                            have_merge=assoc.have_merge,
                                            merge_price=assoc.merge_price,
                                            product_sqm_price_without_addon=assoc.product_sqm_price_without_addon,
                                            hide_dimension=assoc.hide_dimension,
                                            minimum_price=assoc.minimum_price,
                                            disabled=assoc.disabled,
                                            product_index=assoc.product_index,
                                            
                                        )
                                        temp_product1.save()
                                        associated_key = associated_key_gen(assoc.building.estimation.enquiry.title)
                                        temp_product1.associated_key = str(associated_key)+str(temp_product1.id)
                                        temp_product1.save()

                                    except Exception as e:
                                        print("EXCEPTIONS__2==>", e)
                                    
                                    # print('assoc==>', assoc)
                                    
                                    generate_product_data(assoc, temp_product1)
                          
                    generate_product_data(product, temp_product)
                                      
                         
                        
        message = 'Original Created Revision '+str(temp_estimation.version.version) if \
            estimation.version.version == '0' else 'Revision '+str(estimation.version.version)+\
                ' Created Revision '+str(temp_estimation.version.version)
        enquiry_logger(enquiry=estimation.enquiry, message=message, action=1, user=request.user)
        messages.success(request, "Revision Created Successfully")    
        return redirect('tem_enquiry_profile', pk=temp_estimation.enquiry.id, version=temp_estimation.id)


@login_required(login_url='signin')
@permission_required(['enquiries.add_estimations'], login_url='permission_not_allowed')
def create_new_version(request, pk):
    """
    This function creates a new version of an estimation by copying all the data from the previous
    version and incrementing the version number.
    """
    
    estimation = Estimations.objects.get(pk=pk)
    temp_version_check = Temp_Estimations.objects.filter(
        enquiry=estimation.enquiry).order_by('id')
    other_versions = Estimations.objects.filter(enquiry=estimation.enquiry).order_by('id')
    if temp_version_check:
        messages.error(request, 'Already have a pending version.')
        return redirect('enquiry_profile', pk=estimation.enquiry.id, version=estimation.id)
    else:
        main_version = EstimationManiVersion(version_text=int(
            other_versions.last().version.main_version.version_text)+1)
        main_version.save()
        version = EstimationVersions(
            created_by=request.user, status=2, version='0', main_version=main_version)
        version.save()
        temp_estimation = Temp_Estimations(created_by=estimation.created_by, enquiry=estimation.enquiry,
                                           version=version, inherited_revision=estimation.version, parent_estimation=estimation)
        temp_estimation.save()
        estimation_project_spec = EstimationProjectSpecifications.objects.filter(estimation=estimation)
        for estimation_spec in estimation_project_spec:
            temp_estimation_spec = Temp_EstimationProjectSpecifications(
                specification_header=estimation_spec.specification_header, 
                estimations=temp_estimation, 
                specification=estimation_spec.specification)
            temp_estimation_spec.save()
            
        specification_obj = EnquirySpecifications.objects.filter(
            estimation=estimation).order_by('id')
        for spec in specification_obj:
            temp_specification = Temp_EnquirySpecifications(
                created_by=spec.created_by,
                estimation=temp_estimation,
                identifier=spec.identifier,
                categories=spec.categories,
                aluminium_products=spec.aluminium_products,
                aluminium_system=spec.aluminium_system,
                aluminium_specification=spec.aluminium_specification,
                aluminium_series=spec.aluminium_series,
                panel_category=spec.panel_category,
                panel_brand=spec.panel_brand,
                panel_series=spec.panel_series,
                panel_specification=spec.panel_specification,
                surface_finish=spec.surface_finish,
                specification_description=spec.specification_description,
                panel_product=spec.panel_product,
                specification_type=spec.specification_type,
            )
            temp_specification.save()
            try:
                product_complance = EstimationProductComplaints.objects.get(
                    estimation=estimation, specification=spec.id)
            except Exception as e:
                product_complance = None
            try:
                temp_spc = Temp_EnquirySpecifications.objects.get(
                    estimation=temp_estimation, identifier=spec.identifier)
            except Exception as e:
                temp_spc = None
            if product_complance:
                temp_compnace = Temp_EstimationProductComplaints(
                    estimation=temp_estimation,
                    specification=temp_spc,
                    is_aluminium_complaint=product_complance.is_aluminium_complaint,
                    aluminium_complaint=product_complance.aluminium_complaint,
                    is_panel_complaint=product_complance.is_panel_complaint,
                    panel_complaint=product_complance.panel_complaint,
                    is_surface_finish_complaint=product_complance.is_surface_finish_complaint,
                    surface_finish_complaint=product_complance.surface_finish_complaint,
                )
                temp_compnace.save()

        buildings = EstimationBuildings.objects.filter(
            estimation=estimation).order_by('id')

        for build in buildings:
            temp_build = Temp_EstimationBuildings(
                created_by=build.created_by, estimation=temp_estimation, building_name=build.building_name)
            temp_build.save()
            main_product = EstimationMainProduct.objects.filter(
                building=build).order_by('id', 'associated_key')
            prev_main_id = None
            for product in main_product:
                if product.product_type == 1:
                    try:
                        temp_product = Temp_EstimationMainProduct(
                            building=temp_build,
                            created_by=product.created_by,
                            category=product.category,
                            specification_Identifier_id=product.specification_Identifier.id,
                            product=product.product,
                            product_type=product.product_type,
                            panel_product=product.panel_product,
                            brand=product.brand,
                            series=product.series,
                            panel_brand=product.panel_brand,
                            panel_series=product.panel_series,
                            uom=product.uom,
                            accessories=product.accessories,
                            is_accessory=product.is_accessory,
                            accessory_quantity=product.accessory_quantity,
                            tolerance_type=product.tolerance_type,
                            tolerance=product.tolerance,
                            is_tolerance=product.is_tolerance,
                            total_addon_cost=product.total_addon_cost,
                            is_sourced=product.is_sourced,
                            supplier=product.supplier,
                            boq_number=product.boq_number,
                            enable_addons=product.enable_addons,
                            accessory_total=product.accessory_total,
                            is_display_data=product.is_display_data,
                            display_width=product.display_width,
                            display_height=product.display_height,
                            display_area=product.display_area,
                            display_quantity=product.display_quantity,
                            display_total_area=product.display_total_area,
                            deduction_price=product.deduction_price,
                            deduction_type=product.deduction_type,
                            deduction_method=product.deduction_method,
                            after_deduction_price=product.after_deduction_price,
                            total_associated_area=product.total_associated_area,
                            deducted_area=product.deducted_area,
                            product_unit_price=product.product_unit_price,
                            product_sqm_price=product.product_sqm_price,
                            product_base_rate=product.product_base_rate,
                            have_merge=product.have_merge,
                            merge_price=product.merge_price,
                            # associated_key=product.associated_key,
                            product_sqm_price_without_addon=product.product_sqm_price_without_addon,
                            hide_dimension=product.hide_dimension,
                            minimum_price=product.minimum_price,
                            disabled=product.disabled,
                            product_index=product.product_index,

                        )
                        temp_product.save()
                        temp_product.main_product = temp_product
                        associated_key = associated_key_gen(product.building.estimation.enquiry.title)
                        temp_product.associated_key = str(associated_key)+str(temp_product.id)
                        temp_product.save()
                        prev_main_id = temp_product

                    except Exception as e:
                        print('EXCEPTIONS__1==>', e)
                else:
                    print('error_1')

                if product.product_type == 2:
                    try:
                        temp_product = Temp_EstimationMainProduct(
                            building=temp_build,
                            created_by=product.created_by,
                            category=product.category,
                            product=product.product,
                            product_type=product.product_type,
                            panel_product=product.panel_product,
                            brand=product.brand,
                            series=product.series,
                            panel_brand=product.panel_brand,
                            panel_series=product.panel_series,
                            uom=product.uom,
                            accessories=product.accessories,
                            is_accessory=product.is_accessory,
                            accessory_quantity=product.accessory_quantity,
                            tolerance_type=product.tolerance_type,
                            tolerance=product.tolerance,
                            is_tolerance=product.is_tolerance,
                            total_addon_cost=product.total_addon_cost,
                            is_sourced=product.is_sourced,
                            supplier=product.supplier,
                            boq_number=product.boq_number,
                            enable_addons=product.enable_addons,
                            accessory_total=product.accessory_total,
                            is_display_data=product.is_display_data,
                            display_width=product.display_width,
                            display_height=product.display_height,
                            display_area=product.display_area,
                            display_quantity=product.display_quantity,
                            display_total_area=product.display_total_area,
                            deduction_price=product.deduction_price,
                            deduction_type=product.deduction_type,
                            deduction_method=product.deduction_method,
                            after_deduction_price=product.after_deduction_price,
                            total_associated_area=product.total_associated_area,
                            deducted_area=product.deducted_area,
                            product_unit_price=product.product_unit_price,
                            product_sqm_price=product.product_sqm_price,
                            product_base_rate=product.product_base_rate,
                            have_merge=product.have_merge,
                            merge_price=product.merge_price,
                            # associated_key=product.associated_key,
                            product_sqm_price_without_addon=product.product_sqm_price_without_addon,
                            hide_dimension=product.hide_dimension,
                            minimum_price=product.minimum_price,
                            disabled=product.disabled,
                            product_index=product.product_index,
                            
                        )
                        associated_key = associated_key_gen(product.building.estimation.enquiry.title)
                        temp_product.associated_key = str(associated_key)+str(temp_product.id)
                        temp_product.save()

                    except Exception as e:
                        print("EXCEPTIONS__2==>", e)
                else:
                    print('error_2')

                temp_spc = Temp_EnquirySpecifications.objects.get(
                    estimation=temp_product.building.estimation, identifier=product.specification_Identifier)
                temp_product.specification_Identifier = temp_spc
                temp_product.save()

                accessories_kit = MainProductAccessories.objects.filter(
                    estimation_product=product).order_by('id')
                for kit in accessories_kit:
                    temp_kit = Temp_MainProductAccessories(
                        estimation_product=temp_product,
                        accessory_item=kit.accessory_item,
                        accessory_item_quantity=kit.accessory_item_quantity,
                        accessory_item_price=kit.accessory_item_price,
                    )
                    temp_kit.save()

                alumin_obj = MainProductAluminium.objects.filter(
                    estimation_product=product).order_by('id')
                for alum in alumin_obj:
                    temp_alumin = Temp_MainProductAluminium(
                        estimation_product=temp_product,
                        aluminium_pricing=alum.aluminium_pricing,
                        al_price_per_unit=alum.al_price_per_unit,
                        al_price_per_sqm=alum.al_price_per_sqm,
                        al_weight_per_unit=alum.al_weight_per_unit,
                        al_markup=alum.al_markup,
                        formula_base=alum.formula_base,
                        pricing_unit=alum.pricing_unit,
                        custom_price=alum.custom_price,
                        al_quoted_price=alum.al_quoted_price,
                        width=alum.width,
                        height=alum.height,
                        area=alum.area,
                        enable_divisions=alum.enable_divisions,
                        horizontal=alum.horizontal,
                        vertical=alum.vertical,
                        quantity=alum.quantity,
                        total_quantity=alum.total_quantity,
                        total_area=alum.total_area,
                        total_weight=alum.total_weight,
                        product_type=alum.product_type,
                        product_description=alum.product_description,
                        price_per_kg=alum.price_per_kg,
                        weight_per_unit=alum.weight_per_unit,
                        product_configuration=alum.product_configuration,
                        total_linear_meter=alum.total_linear_meter,
                        weight_per_lm=alum.weight_per_lm,
                        surface_finish=alum.surface_finish,
                        curtainwall_type=alum.curtainwall_type,
                        is_conventional=alum.is_conventional,
                        is_two_way=alum.is_two_way,
                        in_area_input=alum.in_area_input
                    )
                    temp_alumin.save()

                glass_obj = MainProductGlass.objects.filter(
                    estimation_product=product, glass_primary=True).order_by('id')
                for glass in glass_obj:
                    temp_glass = Temp_MainProductGlass(
                        estimation_product=temp_product,
                        is_glass_cost=glass.is_glass_cost,
                        glass_specif=glass.glass_specif,
                        total_area_glass=glass.total_area_glass,
                        glass_base_rate=glass.glass_base_rate,
                        glass_markup_percentage=glass.glass_markup_percentage,
                        glass_quoted_price=glass.glass_quoted_price,
                        glass_pricing_type=glass.glass_pricing_type,
                        glass_width=glass.glass_width,
                        glass_height=glass.glass_height,
                        glass_area=glass.glass_area,
                        glass_quantity=glass.glass_quantity,
                        glass_primary=glass.glass_primary,
                    )
                    temp_glass.save()

                second_glass_obj = MainProductGlass.objects.filter(
                    estimation_product=product, glass_primary=False).order_by('id')
                for seco_glass in second_glass_obj:
                    temp_second_glass = Temp_MainProductGlass(
                        estimation_product=temp_product,
                        is_glass_cost=seco_glass.is_glass_cost,
                        glass_specif=seco_glass.glass_specif,
                        total_area_glass=seco_glass.total_area_glass,
                        glass_base_rate=seco_glass.glass_base_rate,
                        glass_markup_percentage=seco_glass.glass_markup_percentage,
                        glass_quoted_price=seco_glass.glass_quoted_price,
                        glass_pricing_type=seco_glass.glass_pricing_type,
                        glass_width=seco_glass.glass_width,
                        glass_height=seco_glass.glass_height,
                        glass_area=seco_glass.glass_area,
                        glass_quantity=seco_glass.glass_quantity,
                        glass_primary=seco_glass.glass_primary,
                    )
                    temp_second_glass.save()
                    print("SAVED")
                deductions = Deduction_Items.objects.filter(
                    estimation_product=product).order_by('id')
                for deduct_item in deductions:
                    temp_deduct_item = Temp_Deduction_Items(
                        estimation_product=temp_product,
                        item_desc=temp_glass,
                        main_price=deduct_item.main_price,
                        item_width=deduct_item.item_width,
                        item_height=deduct_item.item_height,
                        item_quantity=deduct_item.item_quantity,
                        item_deduction_area=deduct_item.item_deduction_area,
                        item_deduction_price=deduct_item.item_deduction_price,
                    )
                    temp_deduct_item.save()
                merge_data = EstimationMainProductMergeData.objects.filter(estimation_product=product).order_by('id')
                for merge in merge_data:
                    temp_merge = Temp_EstimationMainProductMergeData(
                        estimation_product=temp_product,
                        merge_product=merge.merge_product,
                        merged_area=merge.merged_area,
                        merged_price=merge.merged_price,
                        merge_quantity=merge.merge_quantity,
                        merge_aluminium_price=merge.merge_aluminium_price,
                        merge_infill_price=merge.merge_infill_price,
                        merge_sealant_price=merge.merge_sealant_price,
                        merge_accessory_price=merge.merge_accessory_price,
                    )
                    temp_merge.save()
                silicon_obj = MainProductSilicon.objects.filter(
                    estimation_product=product).order_by('id')
                for silicon in silicon_obj:
                    temp_silicon = Temp_MainProductSilicon(
                        estimation_product=temp_product,
                        created_date=silicon.created_date,
                        is_silicon=silicon.is_silicon,
                        external_lm=silicon.external_lm,
                        external_base_rate=silicon.external_base_rate,
                        external_markup=silicon.external_markup,
                        external_sealant_type=silicon.external_sealant_type,
                        internal_lm=silicon.internal_lm,
                        internal_base_rate=silicon.internal_base_rate,
                        internal_markup=silicon.internal_markup,
                        internal_sealant_type=silicon.internal_sealant_type,
                        silicon_quoted_price=silicon.silicon_quoted_price,
                        
                        polyamide_gasket=silicon.polyamide_gasket,
                        polyamide_markup=silicon.polyamide_markup,
                        polyamide_base_rate=silicon.polyamide_base_rate,
                        polyamide_lm=silicon.polyamide_lm,
                        transom_gasket=silicon.transom_gasket,
                        transom_markup=silicon.transom_markup,
                        transom_base_rate=silicon.transom_base_rate,
                        transom_lm=silicon.transom_lm,
                        mullion_gasket=silicon.mullion_gasket,
                        mullion_markup=silicon.mullion_markup,
                        mullion_base_rate=silicon.mullion_base_rate,
                        mullion_lm=silicon.mullion_lm,
                    )
                    temp_silicon.save()
                pricing = PricingOption.objects.filter(
                    estimation_product=product).order_by('id')
                for price in pricing:
                    temp_pricing = Temp_PricingOption(
                        estimation_product=temp_product,
                        is_pricing_control=price.is_pricing_control,
                        overhead_perce=price.overhead_perce,
                        labour_perce=price.labour_perce
                    )
                    temp_pricing.save()

                addons = MainProductAddonCost.objects.filter(
                    estimation_product=product).order_by('id')
                for addon in addons:
                    temp_addon = Temp_MainProductAddonCost(
                        estimation_product=temp_product,
                        addons=addon.addons,
                        base_rate=addon.base_rate,
                        pricing_type=addon.pricing_type,
                        addon_quantity=addon.addon_quantity
                    )
                    temp_addon.save()
        enquiry_logger(enquiry=estimation.enquiry, message= 'Created New Version.', action=1, user=request.user)
        messages.success(request, "New Version Created Successfully")
        return redirect('tem_enquiry_profile', pk=temp_estimation.enquiry.id, version=temp_estimation.id)


@login_required(login_url='signin')
@permission_required(['enquiries.add_estimations'], login_url='permission_not_allowed')
def version_submit(request, pk):
    """
        Submitting Temporary Version to Main.
    """
    temp_estimation = Temp_Estimations.objects.get(pk=pk)
    parameters = SubmittingParameters.objects.all()
    
    if request.method == 'POST':
        version = EstimationVersions.objects.get(pk=temp_estimation.version.id)
        version.status = 3
        version.last_modified_date = time()
        version.last_modified_by = request.user
        version.save()
        enquiry_obj = Enquiries.objects.get(pk=temp_estimation.enquiry.id)
        enquiry_obj.status = 9
        enquiry_obj.due_date = temp_estimation.due_date
        enquiry_obj.save()
        
        estimation = Estimations(
                                    created_by=temp_estimation.created_by, 
                                    enquiry=temp_estimation.enquiry,
                                    version=version, 
                                    inherited_revision=temp_estimation.inherited_revision,
                                    due_date=temp_estimation.due_date,
                                    created_date=temp_estimation.created_date,
                                )
        estimation.save()
        time_data_objs = Temp_Estimation_UserTimes.objects.filter(estimation=temp_estimation)
        for time_data in time_data_objs:
            new_titme_data = Estimation_UserTimes(
                estimation=estimation, 
                user=time_data.user,
                active_time=time_data.active_time,
                updated_at=time_data.updated_at,
                last_update=time_data.last_update,
                date=time_data.date,
                status=time_data.status,
                )
            new_titme_data.save()
            
        try:
            temp_summary = Temp_Pricing_Summary.objects.get(estimation=temp_estimation.id)
        except:
            temp_summary = None
            
        if temp_summary:
            summary_price = Pricing_Summary(
                estimation=estimation,
                scope_of_work=temp_summary.scope_of_work,
                product_summary=temp_summary.product_summary,
                weightage_summary=temp_summary.weightage_summary,
                material_summary=temp_summary.material_summary,
                pricing_review_summary=temp_summary.pricing_review_summary,
                quotation=temp_summary.quotation,
            )
            summary_price.save()
        
        try:
            temp_general_note = Temp_Estimation_GeneralNotes.objects.get(estimations=temp_estimation)
            general_note = Estimation_GeneralNotes(
                estimations=estimation,
                general_notes=temp_general_note.general_notes,
                created_by=temp_general_note.created_by,
            )
            
            general_note.save()
            
        except Exception as e:
            pass
        
        estimation_project_spec = Temp_EstimationProjectSpecifications.objects.filter(estimations=temp_estimation)
        for temp_estimation_spec in estimation_project_spec:
            estimation_spec = EstimationProjectSpecifications(
                specification_header=temp_estimation_spec.specification_header, 
                estimations=estimation, 
                specification=temp_estimation_spec.specification)
            estimation_spec.save()
            
        estimation_notes = Temp_EstimationNotes.objects.filter(estimation=temp_estimation)
        for temp_note in estimation_notes:
            note = EstimationNotes(created_by=temp_note.created_by, estimation=estimation, \
                management=temp_note.management, user=temp_note.user, notes=temp_note.notes, \
                note_status=temp_note.note_status, is_replay=temp_note.is_replay, main_note=temp_note.main_note, \
                note_readed=temp_note.note_readed, read_by=temp_note.read_by, enquiry=temp_note.enquiry)
            note.save()
        
        specification_obj = Temp_EnquirySpecifications.objects.filter(
            estimation=temp_estimation).order_by('id')
        for spec in specification_obj:
            specification = EnquirySpecifications(
                created_by=spec.created_by,
                estimation=estimation,
                identifier=spec.identifier,
                categories=spec.categories,
                aluminium_products=spec.aluminium_products,
                aluminium_system=spec.aluminium_system,
                aluminium_specification=spec.aluminium_specification,
                aluminium_series=spec.aluminium_series,
                panel_category=spec.panel_category,
                panel_brand=spec.panel_brand,
                panel_series=spec.panel_series,
                panel_specification=spec.panel_specification,
                surface_finish=spec.surface_finish,
                specification_description=spec.specification_description,
                panel_product=spec.panel_product,
                specification_type=spec.specification_type,
                minimum_price=spec.minimum_price,
            )
            specification.save()
            try:
                product_complance = Temp_EstimationProductComplaints.objects.get(
                    estimation=temp_estimation, specification=spec.id)
            except Exception as e:
                product_complance = None
            try:
                temp_spc = EnquirySpecifications.objects.get(
                    estimation=estimation, identifier=spec.identifier)
            except Exception as e:
                temp_spc = None
            if product_complance:
                temp_compnace = EstimationProductComplaints(
                    estimation=estimation,
                    specification=temp_spc,
                    is_aluminium_complaint=product_complance.is_aluminium_complaint,
                    aluminium_complaint=product_complance.aluminium_complaint,
                    is_panel_complaint=product_complance.is_panel_complaint,
                    panel_complaint=product_complance.panel_complaint,
                    is_surface_finish_complaint=product_complance.is_surface_finish_complaint,
                    surface_finish_complaint=product_complance.surface_finish_complaint,
                )
                temp_compnace.save()

        temp_buildings = Temp_EstimationBuildings.objects.filter(
            estimation=temp_estimation).order_by('id')
        for build in temp_buildings:
            buildings = EstimationBuildings(
                created_by=build.created_by, 
                estimation=estimation, 
                building_name=build.building_name, 
                no_typical_buildings=build.no_typical_buildings, 
                typical_buildings_enabled=build.typical_buildings_enabled
            )
            buildings.save()
            
            main_product = Temp_EstimationMainProduct.objects.filter(
                building=build).order_by('id', 'associated_key')
            prev_main_id = None
            
            for product in main_product:
                if product.product_type == 1:
                    try:
                        temp_product = EstimationMainProduct(
                            building=buildings,
                            created_by=product.created_by,
                            category=product.category,
                            product=product.product,
                            product_type=product.product_type,
                            panel_product=product.panel_product,
                            brand=product.brand,
                            series=product.series,
                            panel_brand=product.panel_brand,
                            panel_series=product.panel_series,
                            uom=product.uom,
                            accessories=product.accessories,
                            is_accessory=product.is_accessory,
                            accessory_quantity=product.accessory_quantity,
                            is_tolerance=product.is_tolerance,
                            tolerance_type=product.tolerance_type,
                            tolerance=product.tolerance,
                            total_addon_cost=product.total_addon_cost,
                            is_sourced=product.is_sourced,
                            supplier=product.supplier,
                            boq_number=product.boq_number,
                            enable_addons=product.enable_addons,
                            accessory_total=product.accessory_total,

                            is_display_data=product.is_display_data,
                            display_width=product.display_width,
                            display_height=product.display_height,
                            display_area=product.display_area,
                            display_quantity=product.display_quantity,
                            display_total_area=product.display_total_area,
                            display_product_name=product.display_product_name,
                            deduction_price=product.deduction_price,
                            deduction_type=product.deduction_type,
                            deducted_area=product.deducted_area,
                            product_unit_price=product.product_unit_price,
                            product_sqm_price=product.product_sqm_price,
                            product_base_rate=product.product_base_rate,
                            # associated_key=product.associated_key,
                            product_sqm_price_without_addon=product.product_sqm_price_without_addon,
                            have_merge=product.have_merge,
                            merge_price=product.merge_price,
                            hide_dimension=product.hide_dimension,
                            deduction_method=product.deduction_method,
                            after_deduction_price=product.after_deduction_price,
                            minimum_price=product.minimum_price,
                            product_index=product.product_index,
                            disabled=product.disabled,
                        )
                        temp_product.save()
                        temp_product.main_product = temp_product
                        associated_key = associated_key_gen(product.building.estimation.enquiry.title)
                        temp_product.associated_key = str(associated_key)+str(temp_product.id)
                        temp_product.save()
                        prev_main_id = temp_product
                    except Exception as e:
                        print('EXCEPTIONS__1==>', e)
                else:
                    print('error_1')
                if product.product_type == 2:
                    try:
                        temp_product = EstimationMainProduct(
                            building=buildings,
                            created_by=product.created_by,
                            category=product.category,
                            product=product.product,
                            product_type=product.product_type,
                            panel_product=product.panel_product,
                            main_product=prev_main_id,
                            brand=product.brand,
                            series=product.series,
                            panel_brand=product.panel_brand,
                            panel_series=product.panel_series,
                            uom=product.uom,
                            accessories=product.accessories,
                            is_accessory=product.is_accessory,
                            is_tolerance=product.is_tolerance,
                            tolerance_type=product.tolerance_type,
                            tolerance=product.tolerance,
                            total_addon_cost=product.total_addon_cost,
                            is_sourced=product.is_sourced,
                            supplier=product.supplier,
                            boq_number=product.boq_number,
                            enable_addons=product.enable_addons,
                            accessory_total=product.accessory_total,
                            
                            is_display_data=product.is_display_data,
                            display_width=product.display_width,
                            display_height=product.display_height,
                            display_area=product.display_area,
                            display_quantity=product.display_quantity,
                            display_total_area=product.display_total_area,
                            display_product_name=product.display_product_name,
                            
                            deduction_price=product.deduction_price,
                            deduction_type=product.deduction_type,
                            deducted_area=product.deducted_area,
                            product_unit_price=product.product_unit_price,
                            product_sqm_price=product.product_sqm_price,
                            product_base_rate=product.product_base_rate,
                            # associated_key=product.associated_key,
                            product_sqm_price_without_addon=product.product_sqm_price_without_addon,
                            have_merge=product.have_merge,
                            merge_price=product.merge_price,
                            hide_dimension=product.hide_dimension,
                            deduction_method=product.deduction_method,
                            after_deduction_price=product.after_deduction_price,
                            minimum_price=product.minimum_price,
                            product_index=product.product_index,
                            disabled=product.disabled,
                        )
                        temp_product.save()
                        associated_key = associated_key_gen(product.building.estimation.enquiry.title)
                        temp_product.associated_key = str(associated_key)+str(temp_product.main_product.id)
                        temp_product.save()
                    except Exception as e:
                        print("EXCEPTIONS__2==>", e)
                else:
                    print('error_2')
                temp_spc = EnquirySpecifications.objects.get(
                    estimation=temp_product.building.estimation, 
                    identifier=product.specification_Identifier,
                )
                temp_product.specification_Identifier = temp_spc
                temp_product.save()

                accessories_kit = Temp_MainProductAccessories.objects.filter(
                    estimation_product=product).order_by('id')
                for kit in accessories_kit:
                    temp_kit = MainProductAccessories(
                        estimation_product=temp_product,
                        accessory_item=kit.accessory_item,
                        accessory_item_quantity=kit.accessory_item_quantity,
                        accessory_item_price=kit.accessory_item_price,
                        accessory_item_total=kit.accessory_item_total,
                    )
                    temp_kit.save()

                alumin_obj = Temp_MainProductAluminium.objects.filter(
                    estimation_product=product)
                for alum in alumin_obj:
                    temp_alumin = MainProductAluminium(
                        estimation_product=temp_product,
                        aluminium_pricing=alum.aluminium_pricing,
                        al_price_per_unit=alum.al_price_per_unit,
                        al_price_per_sqm=alum.al_price_per_sqm,
                        al_weight_per_unit=alum.al_weight_per_unit,
                        al_markup=alum.al_markup,
                        pricing_unit=alum.pricing_unit,
                        custom_price=alum.custom_price,
                        al_quoted_price=alum.al_quoted_price,
                        width=alum.width,
                        formula_base=alum.formula_base,
                        height=alum.height,
                        area=alum.area,
                        enable_divisions=alum.enable_divisions,
                        horizontal=alum.horizontal,
                        vertical=alum.vertical,
                        quantity=alum.quantity,
                        total_quantity=alum.total_quantity,
                        total_area=alum.total_area,
                        total_weight=alum.total_weight,
                        product_type=alum.product_type,
                        product_description=alum.product_description,
                        price_per_kg=alum.price_per_kg,
                        weight_per_unit=alum.weight_per_unit,
                        product_configuration=alum.product_configuration,
                        total_linear_meter=alum.total_linear_meter,
                        weight_per_lm=alum.weight_per_lm,
                        surface_finish=alum.surface_finish,
                        
                        curtainwall_type=alum.curtainwall_type,
                        is_conventional=alum.is_conventional,
                        is_two_way=alum.is_two_way,
                        in_area_input=alum.in_area_input,
                    )
                    temp_alumin.save()
                    temp_product.total_associated_area = alum.total_area
                    temp_product.save()
                glass_obj = Temp_MainProductGlass.objects.filter(
                    estimation_product=product, glass_primary=True)
                for glass in glass_obj:
                    temp_glass = MainProductGlass(
                        estimation_product=temp_product,
                        is_glass_cost=glass.is_glass_cost,
                        glass_specif=glass.glass_specif,
                        total_area_glass=glass.total_area_glass,
                        glass_base_rate=glass.glass_base_rate,
                        glass_markup_percentage=glass.glass_markup_percentage,
                        glass_quoted_price=glass.glass_quoted_price,
                        glass_pricing_type=glass.glass_pricing_type,
                        glass_width=glass.glass_width,
                        glass_height=glass.glass_height,
                        glass_area=glass.glass_area,
                        glass_quantity=glass.glass_quantity,
                        glass_primary=glass.glass_primary,
                    )
                    temp_glass.save()

                second_glass_obj = Temp_MainProductGlass.objects.filter(
                    estimation_product=product, glass_primary=False).order_by('id')
                for seco_glass in second_glass_obj:
                    temp_second_glass = MainProductGlass(
                        estimation_product=temp_product,
                        is_glass_cost=seco_glass.is_glass_cost,
                        glass_specif=seco_glass.glass_specif,
                        total_area_glass=seco_glass.total_area_glass,
                        glass_base_rate=seco_glass.glass_base_rate,
                        glass_markup_percentage=seco_glass.glass_markup_percentage,
                        glass_quoted_price=seco_glass.glass_quoted_price,
                        glass_pricing_type=seco_glass.glass_pricing_type,
                        glass_width=seco_glass.glass_width,
                        glass_height=seco_glass.glass_height,
                        glass_area=seco_glass.glass_area,
                        glass_quantity=seco_glass.glass_quantity,
                        glass_primary=seco_glass.glass_primary,
                    )
                    temp_second_glass.save()
                deductions = Temp_Deduction_Items.objects.filter(
                    estimation_product=product).order_by('id')
                for deduct_item in deductions:
                    temp_deduct_item = Deduction_Items(
                        estimation_product=temp_product,
                        item_desc=temp_glass,
                        main_price=deduct_item.main_price,
                        item_width=deduct_item.item_width,
                        item_height=deduct_item.item_height,
                        item_quantity=deduct_item.item_quantity,
                        item_deduction_area=deduct_item.item_deduction_area,
                        item_deduction_price=deduct_item.item_deduction_price,
                    )
                    temp_deduct_item.save()
                merge_data = Temp_EstimationMainProductMergeData.objects.filter(estimation_product=product).order_by('id')
                for merge in merge_data:
                    temp_merge = EstimationMainProductMergeData(
                        estimation_product=temp_product,
                        merge_product=merge.merge_product,
                        merged_area=merge.merged_area,
                        merged_price=merge.merged_price,
                        merge_quantity=merge.merge_quantity,
                        merge_aluminium_price=merge.merge_aluminium_price,
                        merge_infill_price=merge.merge_infill_price,
                        merge_sealant_price=merge.merge_sealant_price,
                        merge_accessory_price=merge.merge_accessory_price,
                    )
                    temp_merge.save()
                silicon_obj = Temp_MainProductSilicon.objects.filter(
                    estimation_product=product).order_by('id')
                for silicon in silicon_obj:
                    temp_silicon = MainProductSilicon(
                        estimation_product=temp_product,
                        created_date=silicon.created_date,
                        is_silicon=silicon.is_silicon,
                        external_lm=silicon.external_lm,
                        external_base_rate=silicon.external_base_rate,
                        external_markup=silicon.external_markup,
                        external_sealant_type=silicon.external_sealant_type,
                        internal_lm=silicon.internal_lm,
                        internal_base_rate=silicon.internal_base_rate,
                        internal_markup=silicon.internal_markup,
                        internal_sealant_type=silicon.internal_sealant_type,
                        silicon_quoted_price=silicon.silicon_quoted_price,
                        
                        polyamide_gasket=silicon.polyamide_gasket,
                        polyamide_markup=silicon.polyamide_markup,
                        polyamide_base_rate=silicon.polyamide_base_rate,
                        polyamide_lm=silicon.polyamide_lm,
                        transom_gasket=silicon.transom_gasket,
                        transom_markup=silicon.transom_markup,
                        transom_base_rate=silicon.transom_base_rate,
                        transom_lm=silicon.transom_lm,
                        mullion_gasket=silicon.mullion_gasket,
                        mullion_markup=silicon.mullion_markup,
                        mullion_base_rate=silicon.mullion_base_rate,
                        mullion_lm=silicon.mullion_lm,
                    )
                    temp_silicon.save()
                pricing = Temp_PricingOption.objects.filter(
                    estimation_product=product)
                for price in pricing:
                    temp_pricing = PricingOption(
                        estimation_product=temp_product,
                        is_pricing_control=price.is_pricing_control,
                        overhead_perce=price.overhead_perce,
                        labour_perce=price.labour_perce
                    )
                    temp_pricing.save()

                addons = Temp_MainProductAddonCost.objects.filter(
                    estimation_product=product)
                for addon in addons:
                    temp_addon = MainProductAddonCost(
                        estimation_product=temp_product,
                        addons=addon.addons,
                        base_rate=addon.base_rate,
                        pricing_type=addon.pricing_type,
                        addon_quantity=addon.addon_quantity
                    )
                    temp_addon.save()


                temp_comments = Temp_ProductComments.objects.filter(
                    product=product)
                for comment in temp_comments:
                    main_comment = ProductComments(
                        created_date=comment.created_date, created_by=comment.created_by, 
                        product=temp_product, comment=comment.comment)
                    main_comment.save()
                
                if product.product_type == 2:
                    associated_datas = Temp_EstimationProduct_Associated_Data.objects.filter(associated_product=product).order_by('id')
                    for associated_data in associated_datas:
                        temp_associated = EstimationProduct_Associated_Data(
                            estimation_main_product=temp_product.main_product,
                            associated_product=temp_product,
                            is_sync=associated_data.is_sync,
                            assoicated_area=associated_data.assoicated_area,
                            is_deducted=associated_data.is_deducted,
                        )
                        temp_associated.save()
                
                temp_audit_log = Temp_AuditLogModel.objects.filter(estimation=temp_estimation, product=product)
                for audit_log in temp_audit_log:
                    new_audit_log = AuditLogModel(
                        message=audit_log.message,
                        estimation=estimation,
                        product=temp_product,
                        user=audit_log.user,
                        old_area=audit_log.old_area,
                        new_area=audit_log.new_area,
                        old_quantity=audit_log.old_quantity,
                        new_quantity=audit_log.new_quantity,
                        old_price=audit_log.old_price,
                        new_price=audit_log.new_price,
                        old_sqm=audit_log.old_sqm,
                        new_sqm=audit_log.new_sqm,
                        
                    )
                    new_audit_log.save()
                    
        temp_quotations = Temp_Quotations.objects.filter(
            estimations=temp_estimation)
        for quotation in temp_quotations:
            main_quotation = Quotations.objects.create(
                estimations=estimation,
                estimations_version=quotation.estimations_version,
                quotation_id=quotation.quotation_id,
                quotation_date=quotation.quotation_date,
                valid_till=quotation.valid_till,
                created_by=quotation.created_by,
                q_type=quotation.q_type,
                remarks=quotation.remarks,
                quotation_customer=quotation.quotation_customer,
                represented_by=quotation.represented_by,
                description=quotation.description,
                products_specifications=quotation.products_specifications,
                terms_of_payment=quotation.terms_of_payment,
                exclusions=quotation.exclusions,
                terms_and_conditions=quotation.terms_and_conditions,
                signature=quotation.signature,
                discount_type=quotation.discount_type,
                apply_total=quotation.apply_total,
                apply_line_items=quotation.apply_line_items,
                discount=quotation.discount,
                template=quotation.template,
                notes=quotation.notes,
                other_notes=quotation.other_notes,
                custom_specifictaion= quotation.custom_specifictaion,
                watermark=quotation.watermark,
                building_total_enable=quotation.building_total_enable,
                is_draft=quotation.is_draft,
                is_provisions=quotation.is_provisions,
            
                is_dimensions=quotation.is_dimensions,
                is_quantity=quotation.is_quantity,
                is_rpu=quotation.is_rpu,
                is_rpsqm=quotation.is_rpsqm,
                is_area=quotation.is_area,
            )
    
        for prepared_for in quotation.prepared_for.all():
            main_quotation.prepared_for.add(
                Customers.objects.get(pk=prepared_for.id).id)
        main_quotation.save()

        temp_quotation_provisions = Temp_Quotation_Provisions.objects.filter(
            quotation=quotation)
        for quotation_provisions in temp_quotation_provisions:
            main_quotation_provisions = Quotation_Provisions(
                quotation=main_quotation,
                provision=quotation_provisions.provision,
                provision_cost=quotation_provisions.provision_cost
            )
            main_quotation_provisions.save()
        quotation_notes = Temp_Quotation_Notes.objects.filter(quotation=quotation)
        for note in quotation_notes:
            try:
                main_q_note = Quotation_Notes.objects.create(
                                                                quotation=main_quotation, 
                                                                quotation_notes=note.quotation_notes, 
                                                                quote_value=note.quote_value, 
                                                                # tag=note.tag
                                                            )
                main_q_note.save()
            except Exception as e:
                print('EXCEPTION==>', e)
                
            
            comments = Temp_Quotation_Notes_Comments.objects.filter(quotation_note=note)
            for comment in comments:
                comment_data = Quotation_Notes_Comments.objects.create(activated=comment.activated, 
                                                        created_date=comment.created_date, 
                                                        last_modified_date=comment.last_modified_date,
                                                        last_modified_by=comment.last_modified_by,
                                                        comments=comment.comments,
                                                        created_by=comment.created_by,
                                                        quotation_note=main_q_note,
                                                        is_read=comment.is_read,
                                                        read_by=comment.read_by
                                                        )
                comment_data.save()
    
    
        for parameter in parameters:
            parameter_check = request.POST.get(f'parameter_check_{parameter.id}')
            parameter_input = request.POST.get(f'parameter_{parameter.id}')
            if parameter_check == 'on' and parameter_input:
                try:
                    parameter_obj = EstimationSubmitting_Hours.objects.get(estimation=estimation, parameter=parameter)
                    parameter_obj.time_data = str(sum_times([str(parameter_obj.time_data), f'{parameter_input}:00']))
                    parameter_obj.save()
                except Exception as e:
                    submit_obj = EstimationSubmitting_Hours(estimation=estimation, parameter=parameter, time_data=f'{parameter_input}:00')
                    submit_obj.save()
        
        clear_temp(pk=pk)
        message = 'Revision '+str(estimation.version.version)+' Submitted to Managment from Cart.'
        enquiry_logger(enquiry=enquiry_obj, message=message , action=2, user=request.user)
        messages.success(request, "Revision Submited Successfully")
        return redirect('enquiry_profile', pk=estimation.enquiry.id, version=estimation.id)
    
    context = {
        "estimation": temp_estimation,
        "parameters": parameters,
        "check_list": [1, 2, 3]
    }
    return render(request, 'Enquiries/quotations/management_review_sumbit_model.html', context)
    

@login_required(login_url='signin')
def clear_temp_data(request, est_id, pk):
    """
    This function clears temporary data related to a specific estimation version and logs the action.
    
    """
    estimation_version = Estimations.objects.get(pk=est_id)
    enquiry = Enquiries.objects.get(pk=estimation_version.enquiry.id)
    other_estimations = Estimations.objects.filter(enquiry=enquiry.id).last()
    if other_estimations.version.status == 3:
        enquiry.status = 9
    elif other_estimations.version.status in [4, 9, 10, 14]:
        enquiry.status = 2
    elif other_estimations.version.status == 5:
        enquiry.status = 7
    elif other_estimations.version.status == 12:
        enquiry.status = 10
    elif other_estimations.version.status == 7:
        enquiry.status = 4
    elif other_estimations.version.status in [13, 15]:
        enquiry.status = 8
    elif other_estimations.version.status == 6:
        enquiry.status = 5
    else:
        enquiry.status = 1
    enquiry.save()
        
    try:
        clear_temp(pk=pk)
        message = 'Cleared Cart Data of Original.' if estimation_version.version.version == '0' else 'Cleared Cart Data of '+str(estimation_version.version.version)
        enquiry_logger(enquiry=estimation_version.enquiry, message=message, action=3, user=request.user)
        messages.success(request, "Successfully Cleared Cart Data.")
    except Exception as e:
        messages.error(request, 'Error in Clearing Cart Data.. Please Contact Admin.')
    return redirect('enquiry_profile', pk=estimation_version.enquiry.id, version=estimation_version.id)


@login_required(login_url='signin')
def clear_version(request, pk):
    """
    The function `clear_version` deletes various related objects and redirects to a specific page.
    """
    try:
        temp_estimations = Estimations.objects.get(pk=pk)
        temp_quotations = Quotations.objects.filter(
            estimations=temp_estimations)
        for quotation in temp_quotations:
            quotation_notes = Quotation_Notes.objects.filter(quotation=quotation)
            for note in quotation_notes:
                Quotation_Notes_Comments.objects.filter(quotation_note=note).delete()
            quotation_notes.delete()
            
        for temp_quotation in temp_quotations:
            provisions = Quotation_Provisions.objects.filter(
                quotation=temp_quotation).delete()
            Quotation_Notes.objects.filter(quotation=temp_quotation).delete()
        temp_quotations.delete()
        
        EstimationProductComplaints.objects.filter(estimation=temp_estimations).delete()
        Quotation_Notes.objects.filter(quotation__estimations=temp_estimations).delete()
        EstimationProjectSpecifications.objects.filter(estimations=temp_estimations).delete()
        Quotation_Notes_Comments.objects.filter(quotation_note__quotation__estimations=temp_estimations).delete()
        Estimation_GeneralNotes.objects.filter(estimations=temp_estimations).delete()
        Pricing_Summary.objects.get(estimation=temp_estimations).delete()
        EstimationSubmitting_Hours.objects.filter(estimation=temp_estimations).delete()
        AuditLogModel.objects.filter(estimation=temp_estimations).delete()
        
    except Exception as e:
        print("Exception clear==>", e)
        
    try:
        temp_specification = EnquirySpecifications.objects.filter(
            estimation=temp_estimations)
        temp_building = EstimationBuildings.objects.filter(
            estimation=temp_estimations)
        for building in temp_building:
            temp_main_products = EstimationMainProduct.objects.filter(
                building__estimation=building.estimation)
            for products in temp_main_products:
                MainProductAddonCost.objects.filter(
                    estimation_product=products).delete()
                PricingOption.objects.filter(
                    estimation_product=products).delete()
                MainProductGlass.objects.filter(
                    estimation_product=products).delete()
                MainProductSilicon.objects.filter(
                    estimation_product=products).delete()
                MainProductAluminium.objects.filter(
                    estimation_product=products).delete()
                ProductComments.objects.filter(
                    product=products).delete()
                MainProductAccessories.objects.filter(
                    estimation_product=products).delete()
                EstimationProduct_Associated_Data.objects.filter(
                    estimation_main_product=products).delete()
                Deduction_Items.objects.filter(estimation_product=products).delete()
                EstimationMainProductMergeData.objects.filter(estimation_product=products).delete()
                # hours = EstimationSubmitting_Hours.objects.filter(estimation=temp_estimations)
                # for hrs in hours:
                #     print("hrs==>", hrs)
                #     hrs.delete()
                # AuditLogModel.objects.filter(estimation=temp_estimations).delete()
                
            temp_main_products.delete()
        temp_building.delete()
        temp_specification.delete()
        temp_estimations.delete()
    except Exception as r:
        print("Exception Clear ==>", r)
    return redirect('list_add_enquiries')


@login_required(login_url='signin')
@permission_required(['enquiries.change_estimations'], login_url='permission_not_allowed')
def reopen_estimation(request, enqu_id, est_id):
    """
    This function reopens an estimation and updates the status of the corresponding enquiry.
    """
    estimation_obj = Estimations.objects.get(pk=est_id)
    estimate = EstimationVersions.objects.get(pk=estimation_obj.version.id)
    estimate.status = 2
    estimate.save()
    enquiry_obj = Enquiries.objects.get(pk=enqu_id)
    enquiry_obj.status = 2
    enquiry_obj.save()
    return redirect('enquiry_profile', pk=enqu_id, version=est_id)


@login_required(login_url='signin')
def get_series_kg_lm(request, pk):
    """
    This function retrieves the weight of a kit per linear meter and returns it as a JSON response.
    """
    data_obj = Profile_Kit.objects.get(pk=pk)
    data = {
        'config_kg_per_lm': data_obj.kit_weight_lm
    }
    return JsonResponse(data, status=200)


@login_required(login_url='signin')
@never_cache
@permission_required(['estimations.view_quotations'], login_url='permission_not_allowed')
def view_quotations(request, pk):
    """
    This function retrieves data related to a specific quotation and renders it in a HTML template.
    """
    
    try:
        quotations = Quotations.objects.get(pk=pk)
        product = EstimationMainProduct.objects.filter(building__estimation=quotations.estimations, disabled=False).order_by('id')
        try:
            summary_data = Pricing_Summary.objects.get(estimation=quotations.estimations.id)
        except Exception:
            summary_data = None 
            
    except Exception as e:
        product = None
        messages.error(
            request, "Error in Quotations Data. Please Check Quotations.")

    # buildings = EstimationBuildings.objects.filter(
    #     estimation=quotations.estimations, disabled=False).order_by('id')
    buildings = EstimationBuildings.objects.select_related(
        'estimation').filter(estimation=quotations.estimations, disabled=False).order_by('id')
    
    specifications_obj = EnquirySpecifications.objects.filter(estimation=quotations.estimations).distinct(
                            'categories', 
                            'panel_specification', 
                            'aluminium_system', 
                            'surface_finish', 
                            'aluminium_products',
                            'is_description'
                            )
    provisions_obj = Quotation_Provisions.objects.filter(quotation=quotations).order_by('id')
    form = CreateEstimationNotesForms()
    send_deatils = Quote_Send_Detail.objects.filter(quotation=quotations.id).order_by('id')
    # projects_obj = ProjectsModel.objects.all().exclude(status=0).order_by('id')
    # project = projects_obj.filter(quotation=quotations).order_by('id')
    old_customers = quotations.prepared_for.all().order_by('id')
    notes_obj = Quotation_Notes.objects.filter(quotation=quotations).order_by('id')
    
    # File Path
    if quotations.estimations.version.version == '0':
        version_name = 'Original'
    else:
        version_name = 'Revision '+str(quotations.estimations.version.version)
        
    # re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
    directory = os.path.join(MEDIA_URL, 'Quotations')
    # directory = os.path.join('http://'+str(request.get_host()), 'media/Quotations')
    if quotations.estimations.enquiry.enquiry_type == 1:
        customer_name = quotations.quotation_customer.name
    else:
        if quotations.prepared_for.first():
            customer_name = quotations.prepared_for.first().name
        else:
            customer_name = 'None'
        
    file_path = str(quotations.estimations.enquiry.enquiry_id)+'/'+str(customer_name)+'/'+str(version_name)
    open_path = os.path.join(directory, file_path).replace("\\", '/')
    if os.path.exists(open_path):
        for root, dirs, files in os.walk(open_path):
            for file in files:
                file_path = os.path.join(root, file).replace("\\", '/')
    else:
        file_path = None
        
    if_boq_number = 0
    if product:
        for item in product:
            if item.boq_number:
                if_boq_number += 1
            else:
                if_boq_number += 0
        
    if if_boq_number > 0:
        boq_flag = True
    else:
        boq_flag = False
    
    
    context = {
        'quotations': quotations,
        "specifications_obj": specifications_obj,
        "buildings": buildings,
        "filter_by_boq": False,
        "provisions_obj": provisions_obj,
        "form": form,
        "send_deatils": send_deatils,
        # "projects_obj": projects_obj,
        # "project": project,
        "old_customers": old_customers,
        "notes_obj": notes_obj,
        "boq_flag": boq_flag,
        "file_path": file_path,
        # "file_path": None,
        "summary_data": summary_data,
        "domain": 'http://'+str(request.get_host()),
    }
    return render(request, 'Enquiries/quotations/list_quotations.html', context)


@login_required(login_url='signin')
@permission_required(['estimations.view_quotations'], login_url='permission_not_allowed')
def view_temp_quotations(request, pk):
    """
    This function retrieves data related to a specific quotation and renders it in a HTML template.
    """
    try:
        quotations = Temp_Quotations.objects.get(pk=pk)
        product = Temp_EstimationMainProduct.objects.filter(building__estimation=quotations.estimations, disabled=False).order_by('id')
    except Exception as e:
        product = None
        messages.error(
            request, "Error in Quotations Data. Please Check Quotations.")

    buildings = Temp_EstimationBuildings.objects.filter(
        estimation=quotations.estimations, disabled=False).order_by('id')
    specifications_obj = Temp_EnquirySpecifications.objects.filter(estimation=quotations.estimations).distinct(
                            'categories', 
                            'panel_specification', 
                            'aluminium_system', 
                            'surface_finish', 
                            'aluminium_products',
                            'is_description'
                            )
    provisions_obj = Temp_Quotation_Provisions.objects.filter(
        quotation=quotations).order_by('id')
    project_create_form = CreateProject()
    notes_obj = Temp_Quotation_Notes.objects.filter(quotation=quotations).order_by('id')
    
    # File Path
    if quotations.estimations.version.version == '0':
        version_name = 'Original'
    else:
        version_name = 'Revision '+str(quotations.estimations.version.version)
        
    directory = os.path.join(MEDIA_URL, 'Quotations')
    if quotations.estimations.enquiry.enquiry_type == 1:
        customer_name = quotations.quotation_customer.name
    else:
        if quotations.prepared_for.first():
            customer_name = quotations.prepared_for.first().name
        else:
            customer_name = 'None'
        
    file_path = str(quotations.estimations.enquiry.enquiry_id)+'/'+str(customer_name)+'/'+str(version_name)
    open_path = os.path.join(directory, file_path).replace("\\", '/')
    if os.path.exists(open_path):
        for root, dirs, files in os.walk(open_path):
            for file in files:
                file_path = os.path.join(root, file).replace("\\", '/')
    else:
        file_path = None
        
    if_boq_number = 0
    if product:
        for item in product:
            if item.boq_number:
                if_boq_number += 1
            else:
                if_boq_number += 0
        
    if if_boq_number > 0:
        boq_flag = True
    else:
        boq_flag = False
    context = {
        'quotations': quotations,
        "specifications_obj": specifications_obj,
        "buildings": buildings,
        "project_create_form": project_create_form,
        "filter_by_boq": False,
        "provisions_obj": provisions_obj,
        "notes_obj": notes_obj,
        "boq_flag": boq_flag,
        "file_path": file_path,
        "domain": 'http://'+str(request.get_host()),
    }
    return render(request, 'Enquiries/quotations/list_quotations.html', context)


def generate_random_4_digit_hex():
    digits = "0123456789ABCDEF"
    random_hex = ""
    for _ in range(4):
        random_hex += random.choice(digits)
    return random_hex

def delete_files_in_folder(folder_path):
    file_list = os.listdir(folder_path)
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)


@login_required(login_url='signin')
@permission_required(['estimations.change_quotations'], login_url='permission_not_allowed')
def edit_quotation(request, pk):
    """
        Updating Quotation.
    """
    quotation = Quotations.objects.get(pk=pk)
    try:
        note = Quotation_Notes.objects.filter(quotation=quotation).last()
    except:
        note = None
    
    enquiry = quotation.estimations.enquiry
    old_customers = quotation.prepared_for.all().order_by('id')
    if enquiry.enquiry_type == 1:
        try:
            represent = Contacts.objects.get(
                customer=enquiry.customers.all().first(), is_primary=True)
        except Exception as e:
            represent = None
    else:
        represent = None

    buildings = EstimationBuildings.objects.filter(
        estimation=quotation.estimations, disabled=False).order_by('id')
    estimation = quotation.estimations
    specifications_obj = EnquirySpecifications.objects.filter(estimation=quotation.estimations).distinct(
                            'categories', 
                            'panel_specification', 
                            'aluminium_system', 
                            'surface_finish', 
                            'aluminium_products',
                            'is_description')
    forms = CreateQuotationsForm(instance=quotation)
    templates = Quotations_Master.objects.filter(company=enquiry.company).order_by('id')
    quotation_note_form = CreateQuotationNote(instance=note)
    PROVISIONSFORMSET = modelformset_factory(Quotation_Provisions, form=CreateQuotations_Provisions, extra=1,
                                             can_delete=True)
    provisions_form = PROVISIONSFORMSET(queryset=Quotation_Provisions.objects.filter(
        quotation=quotation), prefix="quotation_provisions")

    if request.method == 'POST':
        quotation_type = request.POST.get("quotation_type")
        template_id = request.POST.get('template_id')
        is_update_note = request.POST.get('is_update_note')
        
        if enquiry.enquiry_type == 1:
            represented_by = request.POST.get('represented_by')
            prepared_by = request.POST.get('prepared_by')
        else:
            prepared_by = [key.split(
                '-')[-1] for key, value in request.POST.items() if key.startswith('prepared_by')]
        provisions_form = PROVISIONSFORMSET(request.POST, queryset=Quotation_Provisions.objects.filter(
            quotation=quotation), prefix="quotation_provisions")
        quotation_note_form = CreateQuotationNote(request.POST, instance=note)
        forms = CreateQuotationsForm(request.POST, instance=quotation)
        
        template= 'print_templates/quotation_print_template.html'
        footer_template = get_template('print_templates/quotation_print_footer.html')
        header_template = get_template('print_templates/quotation_print_header.html')
        random_4_digit_hex = generate_random_4_digit_hex()
        quotation_file_name = f'{str(quotation.estimations.enquiry.title)}_Quotation_{random_4_digit_hex}.pdf'
        
        if 'preview' in request.POST and not 'save' in request.POST and not 'submit' in request.POST:
            if forms.is_valid() and quotation_note_form.is_valid():
                form_obj = forms.save(commit=False)
                form_obj.last_modified_date = time()
                form_obj.last_modified_by = request.user
                form_obj.template_id = int(template_id)
                if quotation_type == '1':
                    form_obj.q_type = 1
                else:
                    form_obj.q_type = 2
                form_obj.save()

                if enquiry.enquiry_type == 1:
                    quotation.prepared_for.clear()
                    quotation.save()
                    form_obj.prepared_for.add(prepared_by)
                    form_obj.represented_by_id = represented_by
                    quotation_customer = Contacts.objects.get(pk=represented_by).customer
                    form_obj.quotation_customer_id = quotation_customer
                
                form_obj.save()
                for item in provisions_form:
                    if item.is_valid():
                        item_obj = item.save(commit=False)
                        if not item_obj.provision_cost == 0:
                            item_obj.quotation = quotation
                            item_obj.save()
                        else:
                            print("ESL")
                    else:
                        messages.error(request, item.errors)
                        print("items-error==>", item.errors)
                if note:
                    quotation_note = quotation_note_form.save()
                    if is_update_note:
                        note = EstimationNotes(created_by=request.user, created_date=time(), estimation=quotation.estimations, \
                                        notes=quotation_note.quotation_notes, note_status=10)
                        note.save()
                else:
                    quotation_note_obj = quotation_note_form.save(commit=False)
                    quotation_note_obj.quotation = quotation
                    quotation_note_obj.created_by = request.user
                    quotation_note_obj.save()
                    if is_update_note:
                        note = EstimationNotes(created_by=request.user, created_date=time(), estimation=quotation.estimations, \
                                        notes=quotation_note_obj.quotation_notes, note_status=10)
                        note.save()
                provisions_obj = Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
                
                context={
                    'title': f'{PROJECT_NAME} | Quotation Privew',
                    'quotations': form_obj,
                    "specifications_obj": specifications_obj,
                    "buildings": buildings,
                    "filter_by_boq": False,
                    "provisions_obj": provisions_obj,
                    "estimation": estimation,
                }
                cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '38mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 12,
                    'page-size': 'A4',
                    'encoding': "UTF-8",
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,                    
                }
                quotation_file_name = 'Temp_Quotation.pdf'
                response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                footer_template=footer_template, header_template=header_template, 
                                                template=template, context=context)
                pdf_data = io.BytesIO(response.rendered_content)

                pdf_file_path = MEDIA_URL+ quotation_file_name
                with open(pdf_file_path, 'wb') as f:
                    f.write(pdf_data.getbuffer())
                    
                if quotation.estimations.enquiry.enquiry_type == 1:
                    # quotation_file_name2 = str(quotation.estimations.enquiry.title)+'_Quotation.pdf'
                    clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                    footer_template=footer_template, header_template=header_template, 
                                                    template=template, context=context)
                    pdf_data = io.BytesIO(response.rendered_content)

                    version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                    pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
                    
                    folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    else:
                        delete_files_in_folder(folder)
                        
                    with open(pdf_file_path2, 'wb') as f:
                        f.write(pdf_data.getbuffer())
                else:
                    for customer in quotation.prepared_for.all():
                        # random_4_digit_hex = generate_random_4_digit_hex()
                        # quotation_file_name2 = f'{str(quotation.estimations.enquiry.title)}_Quotation_{random_4_digit_hex}.pdf'
                        clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                        customer_name = Customers.objects.get(pk=customer.id)
                        context['customer'] = customer_name
                        response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                        footer_template=footer_template, header_template=header_template, 
                                                        template=template, context=context)
                        pdf_data = io.BytesIO(response.rendered_content)

                        version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                        
                        pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                            str(customer_name.name) + '/'+str(version_str)+'/' + clean_string
                        
                            
                        folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                            str(customer_name.name) + '/'+str(version_str)
                        if not os.path.exists(folder):
                            os.makedirs(folder)
                        else:
                            delete_files_in_folder(folder)
                            
                        with open(pdf_file_path2, 'wb') as f:
                            f.write(pdf_data.getbuffer())
                    
                    
                return JsonResponse({
                        'pdf_url': 'http://'+str(request.get_host())+'/'+str(pdf_file_path),
                    })
            else:
                messages.error(request, forms.errors)
                print('errors', forms.errors)
        elif 'submit' in request.POST:
            if forms.is_valid() and quotation_note_form.is_valid():
                form_obj = forms.save(commit=False)
                form_obj.last_modified_date = time()
                form_obj.last_modified_by = request.user
                form_obj.template_id = int(template_id)
                if quotation_type == '1':
                    form_obj.q_type = 1
                else:
                    form_obj.q_type = 2
                form_obj.save()

                if enquiry.enquiry_type == 1:
                    quotation.prepared_for.clear()
                    quotation.save()
                    form_obj.prepared_for.add(prepared_by)
                    form_obj.represented_by_id = represented_by
                    quotation_customer = Contacts.objects.get(pk=represented_by).customer
                    form_obj.quotation_customer_id = quotation_customer
                form_obj.save()

                for item in provisions_form:
                    if item.is_valid():
                        item_obj = item.save(commit=False)
                        if not item_obj.provision_cost == 0:
                            item_obj.quotation = quotation
                            item_obj.save()
                    else:
                        messages.error(request, item.errors)
                        print("items-error==>", item.errors)
                if note:
                    quotation_note = quotation_note_form.save()
                    if is_update_note:
                        note = EstimationNotes(created_by=request.user, created_date=time(), estimation=quotation.estimations, \
                                        notes=quotation_note.quotation_notes, note_status=10)
                        note.save()
                else:
                    quotation_note_obj = quotation_note_form.save(commit=False)
                    quotation_note_obj.quotation = quotation
                    quotation_note_obj.created_by = request.user
                    quotation_note_obj.save()
                    if is_update_note:
                        note = EstimationNotes(created_by=request.user, created_date=time(), estimation=quotation.estimations, \
                                        notes=quotation_note_obj.quotation_notes, note_status=10)
                        note.save()
                provisions_obj = Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
                message = 'Updated Quotation #'+form_obj.quotation_id+'in Original.' \
                    if quotation.estimations.version.version == '0' else 'Updated Quotation #'\
                        +form_obj.quotation_id+' in Revision '+str(quotation.estimations.version.version)
                enquiry_logger(enquiry=enquiry, message=message, action=2, user=request.user)
                messages.success(request, "Quotation Updated Successfully")
                context={
                    'quotations': form_obj,
                    "specifications_obj": specifications_obj,
                    "buildings": buildings,
                    "filter_by_boq": False,
                    "provisions_obj": provisions_obj,
                    "estimation": estimation,
                }
                cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '38mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 12,
                    'page-size': 'A4',
                    'encoding': "UTF-8",
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,                    
                }
                if quotation.estimations.enquiry.enquiry_type == 1:
                    # random_4_digit_hex = generate_random_4_digit_hex()
                    # quotation_file_name = f'{str(quotation.estimations.enquiry.title)}_Quotation_{random_4_digit_hex}.pdf'
                    clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                    footer_template=footer_template, header_template=header_template, 
                                                    template=template, context=context)
                    pdf_data = io.BytesIO(response.rendered_content)

                    version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                    pdf_file_path = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
                    folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)
                    try:
                        if not os.path.exists(folder):
                            os.makedirs(folder)
                        else:
                            delete_files_in_folder(folder)
                            
                        with open(pdf_file_path, 'wb') as f:
                            f.write(pdf_data.getbuffer())
                    except Exception as e:
                        pass
                else:
                    
                    for customer in quotation.prepared_for.all():
                        # random_4_digit_hex = generate_random_4_digit_hex()
                        # quotation_file_name2 = f'{str(quotation.estimations.enquiry.title)}_Quotation_{random_4_digit_hex}.pdf'
                        # quotation_file_name2 = str(quotation.estimations.enquiry.title)+'_Quotation.pdf'
                        clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                        customer_name = Customers.objects.get(pk=customer.id)
                        context['customer'] = customer_name
                        response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                        footer_template=footer_template, header_template=header_template, 
                                                        template=template, context=context)
                        pdf_data = io.BytesIO(response.rendered_content)

                        version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                        pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                            str(customer_name.name) + '/'+str(version_str)+'/' + clean_string
                        
                        folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                            str(customer_name.name) + '/'+str(version_str)
                        if not os.path.exists(folder):
                            os.makedirs(folder)
                        else:
                            delete_files_in_folder(folder)
                            
                        with open(pdf_file_path2, 'wb') as f:
                            f.write(pdf_data.getbuffer())
                return JsonResponse({'url': 'http://'+str(request.get_host())+'/Estimation/estimation_quotations_list/'+ str(quotation.estimations.id) +'/'})
            else:
                messages.error(request, forms.errors)
                print('errors', forms.errors)
        else:
            message = 'Updated Quotation #'+quotation.quotation_id+'in Original.' \
                if quotation.estimations.version.version == '0' else 'Updated Quotation #'\
                    +quotation.quotation_id+' in Revision '+str(quotation.estimations.version.version)
            enquiry_logger(enquiry=enquiry, message=message, action=2, user=request.user)
            messages.success(request, "Quotation Updated Successfully")
            
            provisions_obj = Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
            context={
                    'quotations': quotation,
                    "specifications_obj": specifications_obj,
                    "buildings": buildings,
                    "filter_by_boq": False,
                    "provisions_obj": provisions_obj,
                    "estimation": estimation,
                }
            cmd_options = {
                'quiet': True, 
                'enable-local-file-access': True, 
                'margin-top': '38mm', 
                'header-spacing': 5,
                'minimum-font-size': 12,
                'page-size': 'A4',
                'encoding': "UTF-8",
                'print-media-type': True,
                'footer-right': "[page] / [topage]",
                'footer-font-size': 8,                    
            }
            if quotation.estimations.enquiry.enquiry_type == 1:
                clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                footer_template=footer_template, header_template=header_template, 
                                                template=template, context=context)
                pdf_data = io.BytesIO(response.rendered_content)

                version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                pdf_file_path = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                    str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
                folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                    str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                else:
                    delete_files_in_folder(folder)
                    
                with open(pdf_file_path, 'wb') as f:
                    f.write(pdf_data.getbuffer())
            else:
                for customer in quotation.prepared_for.all():
                    clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                    customer_name = Customers.objects.get(pk=customer.id)
                    context['customer'] = customer_name
                    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                    footer_template=footer_template, header_template=header_template, 
                                                    template=template, context=context)
                    pdf_data = io.BytesIO(response.rendered_content)

                    version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                    pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(customer_name.name) + '/'+str(version_str)+'/' + clean_string
                    
                    folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(customer_name.name) + '/'+str(version_str)
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    else:
                        delete_files_in_folder(folder)
                        
                    with open(pdf_file_path2, 'wb') as f:
                        f.write(pdf_data.getbuffer())
            return redirect('estimation_quotations_list', pk=quotation.estimations.id)
    context = {
        'title': f'{PROJECT_NAME} | Edit Quotation',
        'forms': forms,
        'pk': pk,
        'version': estimation,
        'enquiry': enquiry,
        'enquiry_obj': enquiry,
        'estimation': estimation,
        'represent': represent,
        'buildings': buildings,
        'specifications_obj': specifications_obj,
        'quid': quotation.id,
        'edit': True,
        'quotation': quotation,
        'provisions_form': provisions_form,
        'old_customers': old_customers,
        'quotation_note_form': quotation_note_form,
        'templates': templates,
        'tinymc_api': TINYMC_API,
    }
    return render(request, 'Enquiries/quotations/create_quotation_base.html', context)


@login_required(login_url='signin')
@permission_required(['estimations.change_quotations'], login_url='permission_not_allowed')
def temp_edit_quotation(request, pk):
    quotation = Temp_Quotations.objects.get(pk=pk)
    enquiry = quotation.estimations.enquiry
    estimation_objs = Estimations.objects.filter(enquiry=enquiry)
    old_customers = quotation.prepared_for.all().order_by('id')
    try:
        note = Temp_Quotation_Notes.objects.filter(quotation=quotation).last()
    except:
        note = None
    if enquiry.enquiry_type == 1:
        try:
            represent = Contacts.objects.get(
                customer=enquiry.customers.all().first(), is_primary=True)
        except Exception as e:
            represent = None
    else:
        represent = None

    buildings = Temp_EstimationBuildings.objects.filter(
        estimation=quotation.estimations, disabled=False).order_by('id')
    specifications_obj = Temp_EnquirySpecifications.objects.filter(estimation=quotation.estimations).distinct('categories', 'panel_specification', 'aluminium_system', 'surface_finish', 'aluminium_products')
    estimation=quotation.estimations
    forms = TempCreateQuotationsForm(instance=quotation)
    
    templates = Quotations_Master.objects.all().order_by('id')
    quotation_note_form = Temp_CreateQuotationNote(instance=note)
    PROVISIONSFORMSET = modelformset_factory(Temp_Quotation_Provisions, form=TempCreateQuotations_Provisions, extra=1,
                                             can_delete=True)
    provisions_form = PROVISIONSFORMSET(queryset=Temp_Quotation_Provisions.objects.filter(
        quotation=quotation), prefix="quotation_provisions")

    if request.method == 'POST':
        quotation_type = request.POST.get("quotation_type")
        template_id = request.POST.get('template_id')
        is_update_note = request.POST.get('is_update_note')
        
        if enquiry.enquiry_type == 1:
            represented_by = request.POST.get('represented_by')
            prepared_by = request.POST.get('prepared_by')
        else:
            prepared_by = [key.split(
                '-')[-1] for key, value in request.POST.items() if key.startswith('prepared_by')]
        provisions_form = PROVISIONSFORMSET(request.POST, queryset=Temp_Quotation_Provisions.objects.filter(
            quotation=quotation), prefix="quotation_provisions")

        forms = TempCreateQuotationsForm(request.POST, instance=quotation)
        quotation_note_form = Temp_CreateQuotationNote(request.POST, instance=note)
        template= 'print_templates/quotation_print_template.html'
        footer_template = get_template('print_templates/quotation_print_footer.html')
        header_template = get_template('print_templates/quotation_print_header.html')
        
        random_4_digit_hex = generate_random_4_digit_hex()
        quotation_file_name = f'{str(quotation.estimations.enquiry.title)}_Quotation_{random_4_digit_hex}.pdf'
                    
        if 'preview' in request.POST and not 'save' in request.POST and not 'submit' in request.POST:
            if forms.is_valid() and quotation_note_form.is_valid():
                form_obj = forms.save(commit=False)
                form_obj.last_modified_date = time()
                form_obj.last_modified_by = request.user
                form_obj.template_id = int(template_id)
                if quotation_type == '1':
                    form_obj.q_type = 1
                else:
                    form_obj.q_type = 2
                form_obj.save()

                if enquiry.enquiry_type == 1:
                    quotation.prepared_for.clear()
                    quotation.save()
                    form_obj.prepared_for.add(prepared_by)
                    form_obj.represented_by_id = represented_by
                    quotation_customer = Contacts.objects.get(pk=represented_by).customer
                    form_obj.quotation_customer_id = quotation_customer
                form_obj.save()

                for item in provisions_form:
                    if item.is_valid():
                        item_obj = item.save(commit=False)
                        
                        if not item_obj.provision_cost == 0:
                            item_obj.quotation = quotation
                            item_obj.save()
                    else:
                        messages.error(request, item.errors)
                        print("items-error==>", item.errors)
                if note:
                    quotation_note = quotation_note_form.save()
                    if is_update_note:
                        note = Temp_EstimationNotes(created_by=request.user, created_date=time(), estimation=quotation.estimations, \
                                        notes=quotation_note.quotation_notes, note_status=10)
                        note.save()
                else:
                    quotation_note_obj = quotation_note_form.save(commit=False)
                    quotation_note_obj.quotation = quotation
                    quotation_note_obj.created_by = request.user
                    quotation_note_obj.save()
                    if is_update_note:
                        note = Temp_EstimationNotes(created_by=request.user, created_date=time(), estimation=quotation.estimations, \
                                        notes=quotation_note_obj.quotation_notes, note_status=10)
                        note.save()
                provisions_obj = Temp_Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
                
                context={
                    'title': f'{PROJECT_NAME} | Quotation Privew',
                    'quotations': form_obj,
                    "specifications_obj": specifications_obj,
                    "buildings": buildings,
                    "filter_by_boq": False,
                    "provisions_obj": provisions_obj,
                }
                cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '38mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 12,
                    'page-size': 'A4',
                    'encoding': "UTF-8",
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,                    
                }
                quotation_file_name = 'Temp_Quotation.pdf'
                response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                footer_template=footer_template, header_template=header_template, 
                                                template=template, context=context)
                pdf_data = io.BytesIO(response.rendered_content)

                pdf_file_path = MEDIA_URL+ quotation_file_name
                with open(pdf_file_path, 'wb') as f:
                    f.write(pdf_data.getbuffer())
                
                if quotation.estimations.enquiry.enquiry_type == 1:
                    # quotation_file_name2 = str(quotation.estimations.enquiry.title)+'_Quotation.pdf'
                    clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                    footer_template=footer_template, header_template=header_template, 
                                                    template=template, context=context)
                    pdf_data = io.BytesIO(response.rendered_content)

                    version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                    pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
                    folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    else:
                        delete_files_in_folder(folder)
                        
                    with open(pdf_file_path2, 'wb') as f:
                        f.write(pdf_data.getbuffer())
                else:
                    for customer in quotation.prepared_for.all():
                        # quotation_file_name2 = str(quotation.estimations.enquiry.title)+'_Quotation.pdf'
                        clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                        customer_name = Customers.objects.get(pk=customer.id)
                        context['customer'] = customer_name
                        response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                        footer_template=footer_template, header_template=header_template, 
                                                        template=template, context=context)
                        pdf_data = io.BytesIO(response.rendered_content)

                        version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                        pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                            str(customer_name.name) + '/'+str(version_str)+'/' + clean_string
                        
                        folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                            str(customer_name.name) + '/'+str(version_str)
                        if not os.path.exists(folder):
                            os.makedirs(folder)
                        else:
                            delete_files_in_folder(folder)
                            
                        with open(pdf_file_path2, 'wb') as f:
                            f.write(pdf_data.getbuffer())
                            
                return JsonResponse({
                        'pdf_url': 'http://'+str(request.get_host())+'/'+str(pdf_file_path),
                    })
                
            else:
                messages.error(request, forms.errors)
                print('errors', forms.errors)
        elif 'submit' in request.POST:
            
            if forms.is_valid() and quotation_note_form.is_valid():
                form_obj = forms.save(commit=False)
                form_obj.last_modified_date = time()
                form_obj.last_modified_by = request.user
                form_obj.template_id = int(template_id)
                if quotation_type == '1':
                    form_obj.q_type = 1
                else:
                    form_obj.q_type = 2
                form_obj.save()
                if enquiry.enquiry_type == 1:
                    quotation.prepared_for.clear()
                    quotation.save()
                    form_obj.prepared_for.add(prepared_by)
                    form_obj.represented_by_id = represented_by
                    quotation_customer = Contacts.objects.get(pk=represented_by).customer
                    form_obj.quotation_customer_id = quotation_customer
                form_obj.save()

                for item in provisions_form:
                    if item.is_valid():
                        item_obj = item.save(commit=False)
                        if not item_obj.provision_cost == 0:
                            item_obj.quotation = quotation
                            item_obj.save()
                    else:
                        messages.error(request, item.errors)
                        print("items-error==>", item.errors)
                if note:
                    quotation_note = quotation_note_form.save()
                    if is_update_note:
                        note = Temp_EstimationNotes(created_by=request.user, created_date=time(), estimation=quotation.estimations, \
                                        notes=quotation_note.quotation_notes, note_status=10)
                        note.save()
                else:
                    quotation_note_obj = quotation_note_form.save(commit=False)
                    quotation_note_obj.quotation = quotation
                    quotation_note_obj.created_by = request.user
                    quotation_note_obj.save()
                    if is_update_note:
                        note = Temp_EstimationNotes(created_by=request.user, created_date=time(), estimation=quotation.estimations, \
                                        notes=quotation_note_obj.quotation_notes, note_status=10)
                        note.save()
                    
                provisions_obj = Temp_Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
                message = 'Updated Quotation #'+form_obj.quotation_id+'in Original (Cart).' \
                    if quotation.estimations.version.version == '0' else 'Updated Quotation #'\
                        +form_obj.quotation_id+' in Revision '+str(quotation.estimations.version.version)+' (Cart).'
                enquiry_logger(enquiry=enquiry, message=message, action=2, user=request.user)
                messages.success(request, "Quotation Updated Successfully")
                context={
                    'quotations': form_obj,
                    "specifications_obj": specifications_obj,
                    "buildings": buildings,
                    "filter_by_boq": False,
                    "provisions_obj": provisions_obj,
                }
                cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '38mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 12,
                    'page-size': 'A4',
                    'encoding': "UTF-8",
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,                    
                }
                
                if quotation.estimations.enquiry.enquiry_type == 1:
                    # quotation_file_name2 = str(quotation.estimations.enquiry.title)+'_Quotation.pdf'
                    clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                    footer_template=footer_template, header_template=header_template, 
                                                    template=template, context=context)
                    pdf_data = io.BytesIO(response.rendered_content)

                    version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                    pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
                    folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    else:
                        delete_files_in_folder(folder)
                        
                    with open(pdf_file_path2, 'wb') as f:
                        f.write(pdf_data.getbuffer())
                else:
                    for customer in quotation.prepared_for.all():
                        # quotation_file_name2 = str(quotation.estimations.enquiry.title)+'_Quotation.pdf'
                        clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                        customer_name = Customers.objects.get(pk=customer.id)
                        context['customer'] = customer_name
                        response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                        footer_template=footer_template, header_template=header_template, 
                                                        template=template, context=context)
                        pdf_data = io.BytesIO(response.rendered_content)

                        version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                        pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                            str(customer_name.name) + '/'+str(version_str)+'/' + clean_string
                        
                        folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                            str(customer_name.name) + '/'+str(version_str)
                        
                        if not os.path.exists(folder):
                            os.makedirs(folder)
                        else:
                            delete_files_in_folder(folder)
                            
                        with open(pdf_file_path2, 'wb') as f:
                            f.write(pdf_data.getbuffer())
                        
                return JsonResponse({'url': 'http://'+str(request.get_host())+'/Estimation/temp_estimation_quotations_list/'+ str(form_obj.estimations.id) +'/'})
            else:
                messages.error(request, forms.errors)
                print('errors', forms.errors)
        else:
            message = 'Updated Quotation #'+quotation.quotation_id+'in Original (Cart).' \
                if quotation.estimations.version.version == '0' else 'Updated Quotation #'\
                    +quotation.quotation_id+' in Revision '+str(quotation.estimations.version.version)+' (Cart).'
            enquiry_logger(enquiry=enquiry, message=message, action=2, user=request.user)
            messages.success(request, "Quotation Updated Successfully")
            
            provisions_obj = Temp_Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
            context={
                    'quotations': quotation,
                    "specifications_obj": specifications_obj,
                    "buildings": buildings,
                    "filter_by_boq": False,
                    "provisions_obj": provisions_obj,
                    "estimation": quotation.estimations,
                }
            cmd_options = {
                'quiet': True, 
                'enable-local-file-access': True, 
                'margin-top': '38mm', 
                'header-spacing': 5,
                'minimum-font-size': 12,
                'page-size': 'A4',
                'encoding': "UTF-8",
                'print-media-type': True,
                'footer-right': "[page] / [topage]",
                'footer-font-size': 8,                    
            }
            if quotation.estimations.enquiry.enquiry_type == 1:
                # quotation_file_name = str(quotation.estimations.enquiry.title)+'_Quotation.pdf'
                clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                footer_template=footer_template, header_template=header_template, 
                                                template=template, context=context)
                pdf_data = io.BytesIO(response.rendered_content)

                version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                pdf_file_path = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                    str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
                folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                    str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                else:
                    delete_files_in_folder(folder)
                    
                with open(pdf_file_path, 'wb') as f:
                    f.write(pdf_data.getbuffer())
            else:
                for customer in quotation.prepared_for.all():
                    # quotation_file_name2 = str(quotation.estimations.enquiry.title)+'_Quotation.pdf'
                    clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                    customer_name = Customers.objects.get(pk=customer.id)
                    context['customer'] = customer_name
                    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                    footer_template=footer_template, header_template=header_template, 
                                                    template=template, context=context)
                    pdf_data = io.BytesIO(response.rendered_content)

                    version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                    pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(customer_name.name) + '/'+str(version_str)+'/' + clean_string
                    
                    folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                        str(customer_name.name) + '/'+str(version_str)
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    else:
                        delete_files_in_folder(folder)
                        
                    with open(pdf_file_path2, 'wb') as f:
                        f.write(pdf_data.getbuffer())
            return redirect('temp_estimation_quotations_list', pk=quotation.estimations.id)

    context = {
        'title': f'{PROJECT_NAME} | Edit Quotation',
        'forms': forms,
        'pk': pk,
        'version': estimation,
        'enquiry': enquiry,
        'enquiry_obj': enquiry,
        'represent': represent,
        'buildings': buildings,
        'edit': True,
        'quotation': quotation,
        'specifications_obj': specifications_obj,
        'quid': quotation.id,
        'provisions_form': provisions_form,
        'old_customers': old_customers,
        'quotation_note_form': quotation_note_form,
        'templates': templates,
        'tinymc_api': TINYMC_API,
        'estimation_objs': estimation_objs,
    }
    return render(request, 'Enquiries/quotations/create_quotation_base.html', context)
    
    
@login_required(login_url='signin')
@permission_required(['enquiries.view_enquiries'], login_url='permission_not_allowed')
def approval_list(request):
    """
    This function returns a list of Enquiries objects filtered by status and user permissions, along
    with other related objects and variables, to be displayed in a template.
    """
    if request.user.is_superuser:
        enquiry_objs = Enquiries.objects.filter(status=9).order_by('enquiry_id')
    else:
        enquiry_objs = Enquiries.objects.filter(Q(status=9) & Q(created_by=request.user) | Q(enquiry_members=request.user)).order_by('enquiry_id')
        
    form = CreateEnquiryForm()
    
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in enquiry_objs for member in enquiry.enquiry_members.all()])
    estimating_count = Enquiries.objects.filter(status=2).count()
    
    context = {
        "title": f'{PROJECT_NAME} | List Approval Enquiries',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': 0,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
    }
    return render(request, "Enquiries/enquiry_list.html", context)


@login_required(login_url='signin')
@permission_required(['enquiries.view_enquiries'], login_url='permission_not_allowed')
def approved_list(request):
    """
    This function returns a list of approved enquiries based on the user's role and filters.
    """
    
    if request.user.is_superuser:
        enquiry_objs = Enquiries.objects.filter(status=5).order_by('enquiry_id')
    else:
        enquiry_objs = Enquiries.objects.filter(Q(status=5) & Q(created_by=request.user) | Q(enquiry_members=request.user)).order_by('enquiry_id')
        
    form = CreateEnquiryForm()
    
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in enquiry_objs for member in enquiry.enquiry_members.all()])
    
    estimating_count = Enquiries.objects.filter(status=2).count()
    
    context = {
        "title": f'{PROJECT_NAME} | List Approval Enquiries',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': 0,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
    }
    return render(request, "Enquiries/enquiry_list.html", context)


@login_required(login_url='singnin')
def approval_filter(request, cpny=None):
    """
        This function filters and displays a list of enquiries based on their status and company.
    """
    form = CreateEnquiryForm()
    
    if cpny:
        if cpny == 0:
            enquiry_objs = Enquiries.objects.filter(
                status=9).exclude(status=0).order_by('enquiry_id')
            company = 0
        else:
            enquiry_objs = Enquiries.objects.filter(
                status=9, company=cpny).exclude(status=0).order_by('enquiry_id')
            company = Companies.objects.get(pk=cpny)
    else:
        enquiry_objs = Enquiries.objects.filter(
                status=9).exclude(status=0).order_by('enquiry_id')
        company = 0
    
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in enquiry_objs for member in enquiry.enquiry_members.all()])
    
    estimating_count = Enquiries.objects.filter(status=2).count()
    context = {
        "title": PROJECT_NAME + " | Approval Filter",
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': company,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
        
    }
    return render(request, "Enquiries/enquiry_list.html", context)


@login_required(login_url='singnin')
def approved_filter(request, cpny=None):
    """
    This function filters and displays a list of approved enquiries based on the company and enquiry
    members.
    
    """
    
    form = CreateEnquiryForm()
    
    if cpny:
        if cpny == 0:
            enquiry_objs = Enquiries.objects.filter(
                status=5).exclude(status=0).order_by('enquiry_id')
            company = 0
        else:
            enquiry_objs = Enquiries.objects.filter(
                status=5, company=cpny).exclude(status=0).order_by('enquiry_id')
            company = Companies.objects.get(pk=cpny)
    else:
        enquiry_objs = Enquiries.objects.filter(
                status=5).exclude(status=0).order_by('enquiry_id')
        company = 0
    
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in enquiry_objs for member in enquiry.enquiry_members.all()])
    
    estimating_count = Enquiries.objects.filter(status=2).count()
    context = {
        "title": f'{PROJECT_NAME} | Approval Filter',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': company,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
        
    }
    return render(request, "Enquiries/enquiry_list.html", context)
 
    
@login_required(login_url='signin')
@permission_required(['enquiries.view_enquiries'], login_url='permission_not_allowed')
def quotation_list_enquiry(request):
    """
    This function retrieves a list of enquiries based on the user's permissions and displays them on a
    webpage.
    """
    
    if request.user.is_superuser:
        enquiry_objs = Enquiries.objects.filter(status = 10).order_by('enquiry_id')
    else:
        enquiry_objs = Enquiries.objects.filter(Q(status=10) & Q(created_by=request.user) | Q(enquiry_members=request.user)).order_by('enquiry_id')
        
    form = CreateEnquiryForm()
    
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in enquiry_objs for member in enquiry.enquiry_members.all()])
    
    estimating_count = Enquiries.objects.filter(status=2).count()
    context = {
        "title": f'{PROJECT_NAME} | Quotation List Enquiries',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': 0,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
    }
    
    return render(request, "Enquiries/enquiry_list.html", context)


@login_required(login_url='singnin')
def quotation_filter(request, cpny=None):
    """
    This function filters and displays a list of enquiries based on the company and status.
    """
    
    form = CreateEnquiryForm()
    
    if cpny:
        if cpny == 0:
            enquiry_objs = Enquiries.objects.filter(
                status=10).exclude(status=0).order_by('enquiry_id')
            company = 0 
        else:
            enquiry_objs = Enquiries.objects.filter(
                status=10, company=cpny).exclude(status=0).order_by('enquiry_id')
            company = Companies.objects.get(pk=cpny)
    else:
        enquiry_objs = Enquiries.objects.filter(
                status=10).exclude(status=0).order_by('enquiry_id')
        company = 0 
        
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in enquiry_objs for member in enquiry.enquiry_members.all()])
    
    estimating_count = Enquiries.objects.filter(status=2).count()
    context = {
        "title": f'{PROJECT_NAME} | Quotations Filter',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': company,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
    }
    return render(request, "Enquiries/enquiry_list.html", context)
   
    
@login_required(login_url='signin')
@permission_required(['enquiries.view_enquiries'], login_url='permission_not_allowed')
def cancelled_enquiries(request):
    """
    This function retrieves cancelled enquiries and renders them in a template for display.
    """
    
    if request.user.is_superuser:
        enquiry_objs = Enquiries.objects.filter(Q(status=4) | Q(status=6)).order_by('enquiry_id')
    else:
        enquiry_objs = Enquiries.objects.filter(Q(status=4) | Q(status=6) & Q(created_by=request.user) | Q(enquiry_members=request.user)).order_by('enquiry_id')
        
    form = CreateEnquiryForm()
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    
    enquiry_members = set([member for enquiry in enquiry_objs for member in enquiry.enquiry_members.all()])
    estimating_count = Enquiries.objects.filter(status=2).count()
    context = {
        "title": f'{PROJECT_NAME} | Cancelled Enquiries.',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': 0,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
    }
    
    return render(request, "Enquiries/enquiry_list.html", context)
    

@login_required(login_url='singnin')
def cancelled_enquiries_filter(request, cpny=None):    
    """
    This function filters cancelled enquiries based on the company and returns a rendered template with
    the filtered enquiries.
    
    """
    form = CreateEnquiryForm()
    if cpny:
        if cpny == 0:
            enquiry_objs = Enquiries.objects.filter(
                Q(status=4) | Q(status=6)).exclude(status=0).order_by('enquiry_id')
            company = 0
        else:
            enquiry_objs = Enquiries.objects.filter(
                Q(status=4) | Q(status=6), company=cpny).exclude(status=0).order_by('enquiry_id')
            company = Companies.objects.get(pk=cpny)
    else:
        enquiry_objs = Enquiries.objects.filter(
                Q(status=4) | Q(status=6)).exclude(status=0).order_by('enquiry_id')
        company = 0
        
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in enquiry_objs for member in enquiry.enquiry_members.all()])
    estimating_count = Enquiries.objects.filter(status=2).count()
    context = {
        "title": f'{PROJECT_NAME} | Cancelled Enquiries Filter',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': company,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
    }
    return render(request, "Enquiries/enquiry_list.html", context)


@login_required(login_url='signin')
@permission_required(['estimations.change_estimations'], login_url='permission_not_allowed')
def workin_current_version(request, pk):
    """
    This function updates the status of an estimation version and enquiry to "2" and redirects to the
    enquiry profile page.
    """
    estimation = Estimations.objects.get(pk=pk)
    if request.method == "POST":
        version = EstimationVersions.objects.get(pk=estimation.version.id)
        version.status = 2
        version.save()
        enquiry = Enquiries.objects.get(pk=estimation.enquiry.id)
        enquiry.status = 2
        enquiry.save()
        
    return redirect('enquiry_profile', pk=estimation.enquiry.id, version=estimation.id)


@login_required(login_url='signin')
def get_enquiry_sealant_data(request, pk):
    """
    The function retrieves data related to a sealant kit object and returns it as a JSON response.
    """
    sealant_kit_obj = Sealant_kit.objects.get(pk=pk)
    data = {
        'normal_price': sealant_kit_obj.normal_price,
        'price': sealant_kit_obj.price,
        'sealant_markup': sealant_kit_obj.sealant_markup,
    }
    return JsonResponse(data, status=200)


@login_required(login_url='signin')
def get_specification_details(request, estimation_id, pk):
    """
    This function retrieves specification details for a given estimation and category and renders them
    in a dropdown menu.
    
    """
    data = EnquirySpecifications.objects.filter(
        estimation=estimation_id, categories=pk).order_by('id')
    context = {
        "data_obj": data,
    }
    return render(request, 'Enquiries/dropdowns/specification_identifier_dropdown.html', context)


@login_required(login_url='signin')
def temp_get_specification_details(request, estimation_id, pk):
    """
    This function retrieves specification details for a given estimation and category and renders them
    in a dropdown menu.
    
    """
    data = Temp_EnquirySpecifications.objects.filter(
        estimation=estimation_id, categories=pk).order_by('id')
    context = {
        "data_obj": data,
    }
    return render(request, 'Enquiries/dropdowns/specification_identifier_dropdown.html', context)


@login_required(login_url='signin')
@permission_required(['enquiries.view_enquiryspecifications'], login_url='permission_not_allowed')
def get_specification_data(request, pk):
    """
    This function retrieves data based on a primary key and returns a JSON response containing the
    retrieved data.
    """
    
    data = EnquirySpecifications.objects.get(pk=pk)
    if data.specification_type == 1:
        if not (data.categories.two_D):
            try:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": data.aluminium_system.id,
                    "aluminium_specification": data.aluminium_specification.profile_master_type.profile_type,
                    "aluminium_series_id": data.aluminium_series.id if data.aluminium_series else None,
                    "surface_finish_id": data.surface_finish.id,
                    "specification_type": data.specification_type,
                }
            except Exception as e:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": data.aluminium_system.id,
                    "aluminium_specification": data.aluminium_specification.profile_master_type.profile_type,
                    "aluminium_series_id": data.aluminium_series.id if data.aluminium_series else None,
                    "surface_finish_id": None,
                    "specification_type": data.specification_type,
                }
                
            return JsonResponse({"data_obj": data_obj}, status=200)
        elif not (data.categories.one_D):
            data_obj = {
                "panel_category_id": data.panel_category.id,
                "panel_brand_id": data.panel_brand.id,
                "panel_series_id": data.panel_series.id,
                "panel_specification_id": data.panel_specification.id,
                "panel_product_id": data.panel_product.id,
                "specification_type": data.specification_type,
            }
            
            return JsonResponse({"data_obj": data_obj}, status=200)

        elif (data.categories.one_D and data.categories.two_D):
            try:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": data.aluminium_system.id,
                    "aluminium_series_id": data.aluminium_series.id if data.aluminium_series else None,
                    "panel_brand_id": data.panel_brand.id,
                    "panel_series_id": data.panel_series.id,
                    "panel_specification_id": data.panel_specification.id,
                    "surface_finish_id": data.surface_finish.id,
                    "panel_product_id": data.panel_product.id,
                    "specification_type": data.specification_type,
                }
            except Exception as e:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": data.aluminium_system.id,
                    "aluminium_series_id": data.aluminium_series.id if data.aluminium_series else None,
                    "panel_brand_id": data.panel_brand.id,
                    "panel_series_id": data.panel_series.id,
                    "panel_specification_id": data.panel_specification.id,
                    "surface_finish_id": None,
                    "panel_product_id": data.panel_product.id,
                    "specification_type": data.specification_type,
                }
                
            return JsonResponse({"data_obj": data_obj}, status=200)
        
    else:
            
        if not (data.categories.two_D):
            try:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": None,
                    "aluminium_specification": None,
                    "aluminium_series_id": None,
                    "surface_finish_id": data.surface_finish.id,
                    "specification_type": data.specification_type,
                }
            except Exception as e:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": None,
                    "aluminium_specification": None,
                    "aluminium_series_id": None,
                    "surface_finish_id": None,
                    "specification_type": data.specification_type,
                }
                
            return JsonResponse({"data_obj": data_obj}, status=200)
        elif not (data.categories.one_D):
            data_obj = {
                "panel_category_id": data.panel_category.id,
                "panel_brand_id": data.panel_brand.id,
                "panel_series_id": data.panel_series.id,
                "panel_specification_id": data.panel_specification.id,
                "panel_product_id": data.panel_product.id,
                "specification_type": data.specification_type,
            }
            
            return JsonResponse({"data_obj": data_obj}, status=200)

        elif (data.categories.one_D and data.categories.two_D):
            try:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": None,
                    "aluminium_series_id": None,
                    "panel_brand_id": data.panel_brand.id,
                    "panel_series_id": data.panel_series.id,
                    "panel_specification_id": data.panel_specification.id,
                    "surface_finish_id": data.surface_finish.id,
                    "panel_product_id": data.panel_product.id,
                    "specification_type": data.specification_type,
                }
            except Exception as e:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": None,
                    "aluminium_series_id": None,
                    "panel_brand_id": data.panel_brand.id,
                    "panel_series_id": data.panel_series.id,
                    "panel_specification_id": data.panel_specification.id,
                    "surface_finish_id": None,
                    "panel_product_id": data.panel_product.id,
                    "specification_type": data.specification_type,
                }
                
            return JsonResponse({"data_obj": data_obj}, status=200)
        
        
@login_required(login_url='signin')
@permission_required(['enquiries.view_enquiryspecifications'], login_url='permission_not_allowed')
def temp_get_specification_data(request, pk):
    """
    This function retrieves data based on a given primary key and returns a JSON response containing the
    relevant data based on certain conditions.
    
    """
    data = Temp_EnquirySpecifications.objects.get(pk=pk)
    if data.specification_type == 1:
        if not (data.categories.two_D):
            try:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": data.aluminium_system.id,
                    "aluminium_specification": data.aluminium_specification,
                    "aluminium_series_id": data.aluminium_series.id if data.aluminium_series else None,
                    "surface_finish_id": data.surface_finish.id,
                    "specification_type": data.specification_type,
                }
            except Exception as e:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": data.aluminium_system.id,
                    "aluminium_specification": data.aluminium_specification,
                    "aluminium_series_id": data.aluminium_series.id if data.aluminium_series else None,
                    "surface_finish_id": None,
                    "specification_type": data.specification_type,
                }
            return JsonResponse({"data_obj": data_obj}, status=200)
        elif not (data.categories.one_D):
            data_obj = {
                "panel_category_id": data.panel_category.id,
                "panel_brand_id": data.panel_brand.id,
                "panel_series_id": data.panel_series.id,
                "panel_specification_id": data.panel_specification.id,
                "panel_product_id": data.panel_product.id,
                "specification_type": data.specification_type,
                
            }
            return JsonResponse({"data_obj": data_obj}, status=200)

        elif (data.categories.one_D and data.categories.two_D):
            try:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": data.aluminium_system.id,
                    "aluminium_series_id": data.aluminium_series.id if data.aluminium_series else None,
                    "panel_brand_id": data.panel_brand.id,
                    "panel_series_id": data.panel_series.id,
                    "panel_specification_id": data.panel_specification.id,
                    "surface_finish_id":  data.surface_finish.id,
                    "panel_product_id": data.panel_product.id,
                    "specification_type": data.specification_type,
                }
            except Exception as e:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": data.aluminium_system.id,
                    "aluminium_series_id": data.aluminium_series.id if data.aluminium_series else None,
                    "panel_brand_id": data.panel_brand.id,
                    "panel_series_id": data.panel_series.id,
                    "panel_specification_id": data.panel_specification.id,
                    "surface_finish_id":  None,
                    "panel_product_id": data.panel_product.id,
                    "specification_type": data.specification_type,
                }
            return JsonResponse({"data_obj": data_obj}, status=200)
    else:
        if not (data.categories.two_D):
            try:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": None,
                    "aluminium_specification": None,
                    "aluminium_series_id": None,
                    "surface_finish_id": data.surface_finish.id,
                    "specification_type": data.specification_type,
                }
            except Exception as e:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": None,
                    "aluminium_specification": None,
                    "aluminium_series_id": None,
                    "surface_finish_id": None,
                    "specification_type": data.specification_type,
                }
                
            return JsonResponse({"data_obj": data_obj}, status=200)
        elif not (data.categories.one_D):
            data_obj = {
                "panel_category_id": data.panel_category.id,
                "panel_brand_id": data.panel_brand.id,
                "panel_series_id": data.panel_series.id,
                "panel_specification_id": data.panel_specification.id,
                "panel_product_id": data.panel_product.id,
                "specification_type": data.specification_type,
            }
            
            return JsonResponse({"data_obj": data_obj}, status=200)

        elif (data.categories.one_D and data.categories.two_D):
            try:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": None,
                    "aluminium_series_id": None,
                    "panel_brand_id": data.panel_brand.id,
                    "panel_series_id": data.panel_series.id,
                    "panel_specification_id": data.panel_specification.id,
                    "surface_finish_id": data.surface_finish.id,
                    "panel_product_id": data.panel_product.id,
                    "specification_type": data.specification_type,
                }
            except Exception as e:
                data_obj = {
                    "aluminium_products_id": data.aluminium_products.id,
                    "aluminium_product_description": data.aluminium_products.description,
                    "aluminium_system_id": None,
                    "aluminium_series_id": None,
                    "panel_brand_id": data.panel_brand.id,
                    "panel_series_id": data.panel_series.id,
                    "panel_specification_id": data.panel_specification.id,
                    "surface_finish_id": None,
                    "panel_product_id": data.panel_product.id,
                    "specification_type": data.specification_type,
                }
                
            return JsonResponse({"data_obj": data_obj}, status=200)


@login_required(login_url='signin')
@permission_required(['enquiries.view_enquiries'], login_url='permission_not_allowed')
def enquiry_filter(request, pk, cpny=None, user=None):
    """
    This function filters and displays a list of Enquiries based on their status and company.
    """
    if request.user.is_superuser:
        if cpny:
            if cpny == 0:
                if pk == 0:
                    enquiry_objs = Enquiries.objects.all().exclude(status=0).order_by('enquiry_id')
                else:
                    enquiry_objs = Enquiries.objects.filter(
                        status=pk).exclude(status=0).order_by('enquiry_id')
                company = 0
            else:
                if pk == 0:
                    enquiry_objs = Enquiries.objects.filter(company=cpny).exclude(status=0).order_by('enquiry_id')
                else:
                    enquiry_objs = Enquiries.objects.filter(
                        status=pk, company=cpny).exclude(status=0).order_by('enquiry_id')
                company = Companies.objects.get(pk=cpny)
        else:
            if pk == 0:
                enquiry_objs = Enquiries.objects.all().exclude(status=0).order_by('enquiry_id')
            else:
                enquiry_objs = Enquiries.objects.filter(
                    status=pk).exclude(status=0).order_by('enquiry_id')
            company = 0
    else:
        if user:
            if cpny:
                if cpny == 0:
                    if pk == 0:
                        enquiry_objs = Enquiries.objects.filter(enquiry_members=user).exclude(status=0).order_by('enquiry_id')
                    else:
                        enquiry_objs = Enquiries.objects.filter(
                            status=pk, enquiry_members=user).exclude(status=0).order_by('enquiry_id')
                    company = 0
                else:
                    if pk == 0:
                        enquiry_objs = Enquiries.objects.filter(company=cpny, enquiry_members=user).exclude(status=0).order_by('enquiry_id')
                    else:
                        enquiry_objs = Enquiries.objects.filter(
                            status=pk, company=cpny, enquiry_members=user).exclude(status=0).order_by('enquiry_id')
                    company = Companies.objects.get(pk=cpny)
            else:
                if pk == 0:
                    enquiry_objs = Enquiries.objects.filter(enquiry_members=user).exclude(status=0).order_by('enquiry_id')
                else:
                    enquiry_objs = Enquiries.objects.filter(
                        status=pk, enquiry_members=user).exclude(status=0).order_by('enquiry_id')
                company = 0
                
        else:
            if cpny:
                if cpny == 0:
                    if pk == 0:
                        enquiry_objs = Enquiries.objects.all().exclude(status=0).order_by('enquiry_id')
                    else:
                        enquiry_objs = Enquiries.objects.filter(
                            status=pk).exclude(status=0).order_by('enquiry_id')
                    company = 0
                else:
                    if pk == 0:
                        enquiry_objs = Enquiries.objects.filter(company=cpny).exclude(status=0).order_by('enquiry_id')
                    else:
                        enquiry_objs = Enquiries.objects.filter(
                            status=pk, company=cpny).exclude(status=0).order_by('enquiry_id')
                    company = Companies.objects.get(pk=cpny)
            else:
                if pk == 0:
                    enquiry_objs = Enquiries.objects.all().exclude(status=0).order_by('enquiry_id')
                else:
                    enquiry_objs = Enquiries.objects.filter(
                        status=pk).exclude(status=0).order_by('enquiry_id')
                company = 0
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    form = CreateEnquiryForm()
    
    enquiry_members = set([member for enquiry in enquiry_objs for member in enquiry.enquiry_members.all()])
    estimating_count = Enquiries.objects.filter(status=2).count()
    management_count = Enquiries.objects.filter(status=9)
    
    context = {
        "title": f'{PROJECT_NAME} | List Enquiries',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': company,
        'status': pk,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
        'management_count': management_count,
    }
    return render(request, "Enquiries/enquiry_list.html", context)


@login_required(login_url='signin')
@permission_required(['customers.view_customers'], login_url='permission_not_allowed')
def get_customer_data(request, pk, quotation_id, temp=None):
    """
    This function retrieves customer data and file path for a quotation based on the primary contact and
    version number.
    """
    
    if not temp:
        quotation = Quotations.objects.get(pk=quotation_id)
    else:
        quotation = Temp_Quotations.objects.get(pk=quotation_id)
        
    data = Contacts.objects.get(customer=pk, is_primary=True)
    
    customer_name = data.customer.name
    if quotation.estimations.version.version == '0':
        version_name = 'Original'
    else:
        version_name = 'Revision '+str(quotation.estimations.version.version)
            
    directory = os.path.join(MEDIA_URL, 'Quotations')
    file_path = str(quotation.estimations.enquiry.enquiry_id)+'/'+str(customer_name)+'/'+str(version_name)
    open_path = os.path.join(directory, file_path).replace("\\", '/')
    
    if os.path.exists(open_path):
        for root, dirs, files in os.walk(open_path):
            for file in files:
                file_path = os.path.join(root, file).replace("\\", '/')
    else:
        file_path = None
    data_obj = {
        'customer_name': data.customer.name,
        'represent_name': str(data.first_name)+' '+str(data.last_name),
        'designation': data.designation.designation,
        "file_path": file_path,
        "domain": 'http://'+str(request.get_host()),
        "temp": temp,
    }
    return JsonResponse(data_obj, status=200)


@login_required(login_url='signin')
@permission_required(['estimations.view_quotations'], login_url='permission_not_allowed')
def new_quotaion_customers(request, pk):
    """
    This function adds new customers to an existing quotation and generates a PDF file for each
    customer.
    
    """
    quotation = Quotations.objects.get(pk=pk)
    old_customers = quotation.prepared_for.all()
    prepared_by = [key.split(
        '-')[-1] for key, value in request.POST.items() if key.startswith('prepared_by')]

    template= 'print_templates/quotation_print_template.html'
    footer_template = get_template('print_templates/quotation_print_footer.html')
    header_template = get_template('print_templates/quotation_print_header.html')
    provisions_obj = Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
    specifications_obj = EnquirySpecifications.objects.filter(estimation=quotation.estimations).distinct(
                            'categories', 
                            'panel_specification', 
                            'aluminium_system', 
                            'surface_finish', 
                            'aluminium_products',
                            'is_description')
    buildings = EstimationBuildings.objects.filter(
        estimation=quotation.estimations, disabled=False).order_by('id')
    
    if request.method == 'POST':
        for customer in prepared_by:
            represent = Contacts.objects.get(customer=customer, is_primary=True)
            quotation.represented_by = represent
            quotation.prepared_for.add(customer)
            quotation.save()
            customer_name = Customers.objects.get(pk=customer)
            
            context={
                    'quotations': quotation,
                    "specifications_obj": specifications_obj,
                    "buildings": buildings,
                    "filter_by_boq": False,
                    "provisions_obj": provisions_obj,
                    "customer": customer_name,
                }
            cmd_options = {
                'quiet': True, 
                'enable-local-file-access': True, 
                'margin-top': '38mm', 
                'header-spacing': 5,
                'minimum-font-size': 12,
                'page-size': 'A4',
                'encoding': "UTF-8",
                'print-media-type': True,
                'footer-right': "[page] / [topage]",
                'footer-font-size': 8,                    
            }
            
            quotation_file_name = str(quotation.estimations.enquiry.title)+'_Quotation.pdf'
            clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
            response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                            footer_template=footer_template, header_template=header_template, 
                                            template=template, context=context)
            pdf_data = io.BytesIO(response.rendered_content)

            version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
            pdf_file_path = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                str(customer_name.name) + '/'+str(version_str)+'/' + clean_string
            folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                str(customer_name.name) + '/'+str(version_str)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(pdf_file_path, 'wb') as f:
                f.write(pdf_data.getbuffer())
        return redirect('estimation_quotations_list', pk=quotation.estimations.id)
    
    context = {
        "old_customers": old_customers,
        'quotations': quotation
    }
    return render(request, 'Enquiries/quotations/add_new_customer_modal.html', context)


@login_required(login_url='signin')
@permission_required(['estimations.view_quotations'], login_url='permission_not_allowed')
def temp_new_quotaion_customers(request, pk):
    """
    This function generates a PDF quotation for a new customer and saves it to a specific folder.
    
    """
    quotation = Temp_Quotations.objects.get(pk=pk)
    old_customers = quotation.prepared_for.all()
    prepared_by = [key.split(
        '-')[-1] for key, value in request.POST.items() if key.startswith('prepared_by')]
    template= 'print_templates/quotation_print_template.html'
    footer_template = get_template('print_templates/quotation_print_footer.html')
    header_template = get_template('print_templates/quotation_print_header.html')
    provisions_obj = Temp_Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
    specifications_obj = Temp_EnquirySpecifications.objects.filter(estimation=quotation.estimations).distinct(
                            'categories', 
                            'panel_specification', 
                            'aluminium_system', 
                            'surface_finish', 
                            'aluminium_products',
                            'is_description')
    buildings = Temp_EstimationBuildings.objects.filter(
        estimation=quotation.estimations, disabled=False).order_by('id')
    
    if request.method == 'POST':
        for customer in prepared_by:
            represent = Contacts.objects.get(
                customer=customer, is_primary=True)
            quotation.represented_by = represent
            quotation.prepared_for.add(customer)
            quotation.save()
            
            customer_name = Customers.objects.get(pk=customer)
            
            context={
                    'quotations': quotation,
                    "specifications_obj": specifications_obj,
                    "buildings": buildings,
                    "filter_by_boq": False,
                    "provisions_obj": provisions_obj,
                    "customer": customer_name,
                }
            cmd_options = {
                'quiet': True, 
                'enable-local-file-access': True, 
                'margin-top': '38mm', 
                'header-spacing': 5,
                'minimum-font-size': 12,
                'page-size': 'A4',
                'encoding': "UTF-8",
                'print-media-type': True,
                'footer-right': "[page] / [topage]",
                'footer-font-size': 8,                    
            }
            
            quotation_file_name = str(quotation.estimations.enquiry.enquiry_id)+'_Quotation.pdf'
            clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
            response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                            footer_template=footer_template, header_template=header_template, 
                                            template=template, context=context)
            pdf_data = io.BytesIO(response.rendered_content)

            version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
            pdf_file_path = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                str(customer_name.name) + '/'+str(version_str)+'/' + clean_string
            folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                str(customer_name.name) + '/'+str(version_str)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(pdf_file_path, 'wb') as f:
                f.write(pdf_data.getbuffer())
                
        return redirect('temp_estimation_quotations_list', pk=quotation.estimations.id)
    
    context = {
        "old_customers": old_customers,
        'quotations': quotation
    }
    return render(request, 'Enquiries/quotations/add_new_customer_modal.html', context)


@login_required(login_url='signin')
@permission_required(['enquiries.view_enquiries'], login_url='permission_not_allowed')
def enquiry_xlsx_export(request, type):
    """
    This function exports a report of enquiries in an xlsx format.
    """
    
    header = ['Title', 'Created On', 'Compnay', 'Received On', 'Due Date', 'User']
    if type == 'xlsx':
        enquiries = Enquiries.objects.filter(status__in=[1, 2]).order_by('id')
        output = io.BytesIO()
        workbook = Workbook(output)
        worksheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'bold': True, 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'fg_color': '#485699'})
        date_format = workbook.add_format({'num_format':'yyyy-mm-dd hh:mm:ss'})
        for p, head in enumerate(header):
            worksheet.write(0, p, head, cell_format)
        for i, enquiry in enumerate(enquiries):
            worksheet.write(i+1, 0, enquiry.title +' | '+ enquiry.main_customer.name if enquiry.main_customer else str([customer for customer in enquiry.customers.all()][0]) +' | '+ str(enquiry.get_enquiry_type_display()) +' | '+ str(enquiry.industry_type))
            worksheet.write(i+1, 1, enquiry.created_date.strftime("%Y-%m-%d"), date_format)
            worksheet.write(i+1, 2, enquiry.company.company_name)
            worksheet.write(i+1, 3, enquiry.received_date.strftime("%Y-%m-%d"), date_format)
            worksheet.write(i+1, 4, enquiry.due_date.strftime("%Y-%m-%d"), date_format)
            worksheet.write(i+1, 5, enquiry.created_by.name)
        workbook.close()
        output.seek(0)
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=Enquiry_Report.xlsx'
        return response

      
@login_required(login_url='signin')
@permission_required([
                        'estimations.change_mainproductaluminium', 
                        'estimations.change_mainproductglass',
                        'estimations.change_estimationmainproduct'
                    ], login_url='permission_not_allowed')
def merge_summary_percentage(request, pk, version):
    """
    This function updates the markup, overhead, and labour percentage for a given product in an
    estimation.
    
    """
    categiory = Category.objects.get(pk=pk)
    main_product = EstimationMainProduct.objects.get(pk=pk)
    aluminium = MainProductAluminium.objects.get(
        estimation_product=main_product)
    try:
        glass = MainProductGlass.objects.get(
            estimation_product=main_product, glass_primary=True)
        second_glass_obj = MainProductGlass.objects.filter(
            estimation_product=pk, glass_primary=False).order_by('id')
    except Exception as e:
        glass = None
        second_glass_obj = None
    labour_and_overhead = PricingOption.objects.get(
        estimation_product=main_product)
    pricing_master = AdditionalandLabourPriceMaster.objects.get(
        pk=main_product.building.estimation.enquiry.additional_and_labour.id)
    addons = MainProductAddonCost.objects.filter(
        estimation_product=main_product).order_by('id')
    try:
        silicon = MainProductSilicon.objects.get(
            estimation_product=main_product)
    except Exception as e:
        silicon = None

    main_form = UpdateLabourAndOverhead(instance=labour_and_overhead)
    tolerance_form = UpdateTolerance(instance=main_product)
    aluminium_form = UpdateAluminiumPercentage(instance=aluminium)

    try:
        glass_form = UpdateGlassPercentage(instance=glass)
    except Exception as e:
        glass_form = None

    if request.method == 'POST':
        main_form = UpdateLabourAndOverhead(
            request.POST, instance=labour_and_overhead)
        tolerance_form = UpdateTolerance(request.POST, instance=main_product)
        aluminium_form = UpdateAluminiumPercentage(
            request.POST, instance=aluminium)
        alumini_final = request.POST.get('alumini_quoted')
        glass_final = request.POST.get('glass_quoted')
        try:
            glass_form = UpdateGlassPercentage(request.POST, instance=glass)
        except Exception as e:
            glass_form = None

        if aluminium_form.is_valid() and glass_form.is_valid() and main_form.is_valid() and tolerance_form.is_valid():
            if (main_form.cleaned_data['overhead_perce'] >= pricing_master.minimum_overhead) and (main_form.cleaned_data['labour_perce'] >= pricing_master.minimum_labour):
                main_form.save()
            else:
                if main_form.cleaned_data['overhead_perce'] < pricing_master.minimum_overhead:
                    messages.error(request, "Overhead Percentage not below " +
                                   str(pricing_master.minimum_overhead) + "%")
                if main_form.cleaned_data['labour_perce'] < pricing_master.minimum_labour:
                    messages.error(request, "Labour Percentage not below " +
                                   str(pricing_master.minimum_labour) + "%")

            if main_product.tolerance_type == 1:
                if int(tolerance_form.cleaned_data['tolerance']) < 0 or int(tolerance_form.cleaned_data['tolerance']) > 100:
                    messages.error(
                        request, "Tolerance Percentage not below 0 or grater than 100. ")
                else:
                    tolerance_obj = tolerance_form.save(commit=False)
                    tolerance_obj.last_modified_by = request.user
                    tolerance_obj.last_modified_date = time()
                    tolerance_obj.save()
            else:
                tolerance_obj = tolerance_form.save(commit=False)
                tolerance_obj.last_modified_by = request.user
                tolerance_obj.last_modified_date = time()
                tolerance_obj.save()

            aluminium_obj = aluminium_form.save(commit=False)
            if alumini_final:
                aluminium_obj.al_quoted_price = float(alumini_final)
                aluminium_obj.last_modified_by = request.user
                aluminium_obj.last_modified_date = time()
            aluminium_obj.save()

            glass_obj = glass_form.save(commit=False)
            if glass_final:
                glass_obj.glass_quoted_price = float(glass_final)
                glass_obj.last_modified_by = request.user
                glass_obj.last_modified_date = time()
            else:
                print("NOT IN GLASS")
            glass_obj.save()
            if second_glass_obj:
                for second_glass in second_glass_obj:
                    sec_glass_markup = request.POST.get(
                        'glass_markup_percentage_'+str(second_glass.id))
                    sec_glass_final = request.POST.get(
                        'sec_glass_final_'+str(second_glass.id))
                    if sec_glass_final:
                        second_glass.glass_markup_percentage = float(
                            sec_glass_markup)
                        second_glass.glass_quoted_price = float(
                            sec_glass_final)
                        second_glass.last_modified_by = request.user
                        second_glass.last_modified_date = time()
                        second_glass.save()
            message = main_product.product.product_name+' Update markups/Overhead/Labour Percentage in Original.' \
                if main_product.product else str(main_product.panel_product.product_name)+\
                    ' Update markups/Overhead/Labour Percentage in Original.' if main_product.building.estimation.version.version == '0' \
                        else main_product.product.product_name+' Update markups/Overhead/Labour Percentage in Revision '\
                            +str(main_product.building.estimation.version) if main_product.product else \
                                str(main_product.panel_product.product_name)+' Update markups/Overhead/Labour Percentage in Revision '\
                                    +str(main_product.building.estimation.version)
            enquiry_logger(enquiry=main_product.building.estimation.enquiry, message= message , action=2, user=request.user)
            messages.success(request, "Updated Successfully")
        else:
            messages.error(request, aluminium_form.errors, glass_form.errors)
            print('errors==>', main_form.errors, aluminium_form.errors,
                  glass_form.errors, tolerance_form.errors)

        return redirect('product_category_summary', pk=main_product.building.estimation.id)

    context = {
        "main_product": main_product,
        "aluminium": aluminium,
        "glass": glass,
        "main_form": main_form,
        "aluminium_form": aluminium_form,
        "glass_form": glass_form,
        "addons": addons,
        "second_glass_obj": second_glass_obj,
        "silicon": silicon,
        "tolerance_form": tolerance_form,
        "categiory": categiory
    }
    return render(request, "Enquiries/merge_summary_update.html", context)


@login_required(login_url='signin')
def open_enquiry(request, pk, version=None):
    """
    This function opens an enquiry and retrieves related objects based on the primary key and version
    number.
    
    """
    enquiry_obj = Enquiries.objects.get(pk=pk)
    if version:
        versions = Estimations.objects.get(pk=version)
        product = EstimationMainProduct.objects.filter(
            building__estimation=versions.id, disabled=False).order_by('id')
        quotations = Quotations.objects.filter(
            estimations__enquiry=enquiry_obj).order_by('id')
        specification_obj = EnquirySpecifications.objects.filter(
            estimation=versions).order_by('id')
    else:
        versions = Estimations.objects.filter(enquiry=enquiry_obj).first()
        product = None
        quotations = None
        specification_obj = None
    estim_versions = Estimations.objects.filter(enquiry=enquiry_obj).order_by('id')
    temp_estimations = Temp_Estimations.objects.filter(enquiry=enquiry_obj).order_by('id')
    notes_obj = EstimationNotes.objects.filter(
        estimation=versions).order_by('id')
    
    ai_rating_label = estimation_ai_rating(enquiry_obj.id)
    context = {
        "enquiry_obj": enquiry_obj,
        "version": versions,
        "quotations": quotations,
        "product": product,
        "specification_obj": specification_obj,
        "estim_versions": estim_versions,
        "temp_estimations": temp_estimations,
        "notes_obj": notes_obj,
        "ai_rating_label": ai_rating_label,
    }
    return render(request, "Enquiries/enquiry_entry_modal.html", context)


@login_required(login_url='signin')
@permission_required(['enquiries.view_estimationnotes'], login_url='permission_not_allowed')
def enquiry_notes(request, pk, last_version):
    """
    This function handles the creation and display of notes related to an estimation for a specific
    enquiry.
    """
    version = Estimations.objects.get(pk=last_version)
    enquiry_obj = Enquiries.objects.get(pk=pk)
    estimation = Estimations.objects.filter(enquiry=enquiry_obj)
    notes_obj = EstimationNotes.objects.filter(Q(estimation__in=estimation) | Q(enquiry=enquiry_obj)).order_by('id')
    for note in notes_obj:
        if not note.note_readed and not request.user == note.created_by:
            note.note_readed = True
            note.save()
        
    estim_versions = Estimations.objects.filter(enquiry=enquiry_obj).order_by('id')
    form = CreateEstimationNotesForms()
    not_users = set([notes.created_by for notes in notes_obj])
    
    context = {
        'title':  f'{PROJECT_NAME} | Estimation Notes',
        'notes_obj': notes_obj,
        'enquiry_obj': enquiry_obj,
        'form': form,
        'estim_versions': estim_versions,
        'not_users': not_users,
        'last_version': last_version,
        'version': version,
    }
    return render(request, "Enquiries/enquiry_note_page.html", context)


@login_required(login_url="signin")
def general_notes_add(request, pk):
    """
    This function adds general notes to an estimation object and redirects to the enquiry profile page.
    
    """
    estimation = Estimations.objects.get(pk=pk)
        
    if request.method == 'POST':
        general_notes = request.POST.get('general_notes_field')
        general_note_obj = Estimation_GeneralNotes(
                                    estimations=estimation, 
                                    general_notes=general_notes, 
                                    created_by=request.user
                                )
       
        general_note_obj.save()
        messages.success(request, "Successfully Added General Notes")
    else:
        messages.error(request, "Somting Wrong.")
    return redirect('enquiry_profile', pk=estimation.enquiry.id, version=estimation.id)
        
              
@login_required(login_url="signin")
def temp_general_notes_add(request, pk):
    """
    This function adds general notes to a temporary estimation object and redirects to the corresponding
    enquiry profile.
    """
    estimation = Temp_Estimations.objects.get(pk=pk)
    if request.method == 'POST':
        general_notes = request.POST.get('general_notes_field')
        
        general_note_obj = Temp_Estimation_GeneralNotes(
                                    estimations=estimation, 
                                    general_notes=general_notes, 
                                    created_by=request.user
                                )
        general_note_obj.save()
        messages.success(request, "Successfully Added General Notes")
    else:
        messages.error(request, "Somting Wrong.")
    
    return redirect('temp_enquiry_profile', pk=estimation.enquiry.id, version=estimation.id)
     
           
@login_required(login_url="signin")
def update_general_notes(request, pk):
    """
    This function updates the general notes of an Estimation_GeneralNotes object and redirects to the
    enquiry profile page.
    """
    general_note_obj = Estimation_GeneralNotes.objects.get(pk=pk)
    if request.method == 'POST':
        general_notes = request.POST.get('general_notes_field')
        general_note_obj.general_notes = general_notes
        general_note_obj.last_modified_date = time()
        general_note_obj.last_modified_by = request.user
        general_note_obj.save()
        messages.success(request, "Successfully Updated General Notes")
    else:
        messages.error(request, "Somting Wrong in Update.")
        
    return redirect('enquiry_profile', pk=general_note_obj.estimations.enquiry.id, version=general_note_obj.estimations.id)


@login_required(login_url="signin")
def temp_update_general_notes(request, pk):
    """
    This function updates the general notes of a Temp_Estimation_GeneralNotes object based on a POST
    request and redirects to a specific page.
    """
    general_note_obj = Temp_Estimation_GeneralNotes.objects.get(pk=pk)
    if request.method == 'POST':
        general_notes = request.POST.get('general_notes_field')
        general_note_obj.general_notes = general_notes
        general_note_obj.last_modified_date = time()
        general_note_obj.last_modified_by = request.user
        general_note_obj.save()
        messages.success(request, "Successfully Updated General Notes")
    else:
        messages.error(request, "Somting Wrong in Update.")
        
    return redirect('tem_enquiry_profile', pk=general_note_obj.estimations.enquiry.id, version=general_note_obj.estimations.id)


@login_required(login_url="signin")
def user_filter_enq(request, pk, status=None):
    """
    This function filters Enquiries objects based on user ID and status, and returns a rendered HTML
    template with the filtered objects and related data.
    
    """
    if status:
        enquiry_objs = Enquiries.objects.filter(enquiry_members=pk, status=status)
    else:
        enquiry_objs = Enquiries.objects.filter(enquiry_members=pk)
        status = 0
    form = CreateEnquiryForm()
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in Enquiries.objects.filter(status=status) for member in enquiry.enquiry_members.all()])
    estimating_count = Enquiries.objects.filter(status=2).count()
    
    context = {
        "title": f'{PROJECT_NAME} | List Enquiries',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': 0,
        'enq_user': pk,
        'enquiry_members': enquiry_members,
        'status': status,
        'estimating_count': estimating_count,
    }
    return render(request, "Enquiries/enquiry_list.html", context)


@login_required(login_url="signin")
def user_filter_approval_enq(request, pk):
    """
    This function filters Enquiries objects based on a user's approval and returns a rendered HTML
    template with the filtered objects and related data.
    
    """
    enquiry_objs = Enquiries.objects.filter(enquiry_members=pk, status=9)
    form = CreateEnquiryForm()
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in Enquiries.objects.all() for member in enquiry.enquiry_members.all()])
    estimating_count = Enquiries.objects.filter(status=2)
    
    context = {
        "title": f'{PROJECT_NAME} | List Enquiries',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': 0,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
        
    }
    return render(request, "Enquiries/enquiry_list.html", context)


@login_required(login_url="signin")
def user_filter_approved_enq(request, pk):
    """
    This function filters approved enquiries based on a user's ID and returns a rendered HTML template
    with relevant context data.
    
    """
    enquiry_objs = Enquiries.objects.filter(enquiry_members=pk, status=5)
    form = CreateEnquiryForm()
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in Enquiries.objects.all() for member in enquiry.enquiry_members.all()])
    estimating_count = Enquiries.objects.filter(status=2)
    
    context = {
        "title": PROJECT_NAME + " | List Enquiries",
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': 0,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,
        
    }
    return render(request, "Enquiries/enquiry_list.html", context)


@login_required(login_url="signin")
def user_filter_quotations_enq(request, pk):
    """
    This function filters Enquiries objects based on certain criteria and returns a rendered HTML
    template with the filtered objects and other related data.
    
    """
    enquiry_objs = Enquiries.objects.filter(
        enquiry_members=pk, status__in=[5, 8, 9, 10])
    form = CreateEnquiryForm()
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in Enquiries.objects.all()
                          for member in enquiry.enquiry_members.all()])
    estimating_count = Enquiries.objects.filter(status=2)

    context = {
        "title": f'{PROJECT_NAME} | List Enquiries',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': 0,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,

    }
    return render(request, "Enquiries/enquiry_list.html", context)


@login_required(login_url="signin")
def user_filter_cancelled_enquiries_enq(request, pk):
    """
    This function filters cancelled enquiries for a specific user and renders them in a template.
    
    """
    enquiry_objs = Enquiries.objects.filter(
        enquiry_members=pk, status__in=[4, 6])
    form = CreateEnquiryForm()
    companies_objs = [enquiry.company for enquiry in enquiry_objs]
    enquiry_members = set([member for enquiry in Enquiries.objects.all()
                          for member in enquiry.enquiry_members.all()])
    estimating_count = Enquiries.objects.filter(status=2)

    context = {
        "title": f'{PROJECT_NAME} | List Enquiries',
        "enquiry_objs": enquiry_objs,
        "form": form,
        'companies_objs': set(companies_objs),
        'company': 0,
        'enquiry_members': enquiry_members,
        'estimating_count': estimating_count,

    }
    return render(request, "Enquiries/enquiry_list.html", context)
    
    
@login_required(login_url="signin")
def view_timer_log(request, pk):
    time_log = EnquiryUser.objects.filter(enquiry=pk, user=request.user)
    context = {
        "time_log" : time_log,
    }
    return render(request, "Enquiries/time_loger.html", context)


@login_required(login_url="signin")
def delete_quotation(request, pk):
    quotation = Quotations.objects.get(id=pk)
    version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
    if quotation.estimations.enquiry.enquiry_type == 1:
        folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)
    
        if request.method == 'POST':
            try:
                Quotation_Provisions.objects.filter(quotation=quotation.id).delete()
                Quote_Send_Detail.objects.filter(quotation=quotation.id).delete()
                Quotation_Notes.objects.filter(quotation=quotation.id).delete()
                Quotation_Notes_Comments.objects.filter(quotation_note__quotation=quotation.id).delete()
                QuotationDownloadHistory.objects.filter(quotation_data=quotation.id).delete()
                quotation.delete()
                
                if os.path.exists(folder):
                    delete_files_in_folder(folder)
            except Exception as e:
                print("EXCEw==>", e)
                messages.error(request, "Error deleting the quotation.")
            return redirect('estimation_quotations_list', pk=quotation.estimations.id)
    else:
        if request.method == 'POST':
            try:
                Quotation_Provisions.objects.filter(quotation=quotation.id).delete()
                Quote_Send_Detail.objects.filter(quotation=quotation.id).delete()
                Quotation_Notes.objects.filter(quotation=quotation.id).delete()
                Quotation_Notes_Comments.objects.filter(quotation_note__quotation=quotation.id).delete()
                QuotationDownloadHistory.objects.filter(quotation_data=quotation.id).delete()
                
                for customer in quotation.prepared_for.all():
                    customer_name = Customers.objects.get(pk=customer.id)
                    folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                            str(customer_name.name) + '/'+str(version_str)
                    if os.path.exists(folder):
                        delete_files_in_folder(folder)
                quotation.delete()
            except Exception as e:
                print("EXC2E==>", e)
                messages.error(request, "Error deleting the quotation.")
            return redirect('estimation_quotations_list', pk=quotation.estimations.id)
            
        
    
    context = {
        "url": "/Enquiries/delete_quotation/"+str(pk)+"/",
        "content": f'{version_str} Quotation {quotation.quotation_id}' 
    }
    return render(request, "Master_settings/delete_modal.html", context)
        
        
@login_required(login_url="signin")
def temp_delete_quotation(request, pk):
    quotation = Temp_Quotations.objects.get(id=pk)
    if request.method == 'POST':
        try:
            Temp_Quotation_Provisions.objects.filter(quotation=quotation.id).delete()
            # Temp_Quote_Send_Detail.objects.filter(quotation=quotation.id).delete()
            Temp_Quotation_Notes.objects.filter(quotation=quotation.id).delete()
            Temp_Quotation_Notes_Comments.objects.filter(quotation_note__quotation=quotation.id).delete()
            # Temp_QuotationDownloadHistory.objects.filter(quotation=quotation.id).delete()
            quotation.delete()
            
        except Exception as e:
            messages.error("Error deleting the quotation.")
        return redirect('temp_estimation_quotations_list', pk=quotation.estimations.id)
    
    context = {
        "url": "/Enquiries/temp_delete_quotation/"+str(pk)+"/",
        "content": f'Quotation {quotation.quotation_id}' 
    }
    return render(request, "Master_settings/delete_modal.html", context)


def enquiry_generate_product_data(product, temp_product):
    temp_spc = EnquirySpecifications.objects.get(
        estimation=temp_product.building.estimation, identifier=product.specification_Identifier)
    temp_product.specification_Identifier = temp_spc
    temp_product.save()
    
    if product.is_accessory:
        accessories_kit = MainProductAccessories.objects.filter(
            estimation_product=product).order_by('id')
        for kit in accessories_kit:
            temp_kit = MainProductAccessories(
                estimation_product=temp_product,
                accessory_item=kit.accessory_item,
                accessory_item_quantity=kit.accessory_item_quantity,
                accessory_item_price=kit.accessory_item_price,
                accessory_item_total=kit.accessory_item_total,
            )
            temp_kit.save()
    try:
        alumin_obj = MainProductAluminium.objects.get(
            estimation_product=product)
    except Exception as e:
        alumin_obj = None
        print("ALUM_EXC==>", e)
        
 
    if alumin_obj:
        temp_alumin = MainProductAluminium(
            estimation_product=temp_product,
            aluminium_pricing=alumin_obj.aluminium_pricing,
            al_price_per_unit=alumin_obj.al_price_per_unit,
            al_price_per_sqm=alumin_obj.al_price_per_sqm,
            al_weight_per_unit=alumin_obj.al_weight_per_unit,
            al_markup=alumin_obj.al_markup,
            pricing_unit=alumin_obj.pricing_unit,
            custom_price=alumin_obj.custom_price,
            al_quoted_price=alumin_obj.al_quoted_price,
            width=alumin_obj.width,
            formula_base=alumin_obj.formula_base,
            height=alumin_obj.height,
            area=alumin_obj.area,
            enable_divisions=alumin_obj.enable_divisions,
            horizontal=alumin_obj.horizontal,
            vertical=alumin_obj.vertical,
            quantity=alumin_obj.quantity,
            total_quantity=alumin_obj.total_quantity,
            total_area=alumin_obj.total_area,
            total_weight=alumin_obj.total_weight,
            product_type=alumin_obj.product_type,
            product_description=alumin_obj.product_description,
            price_per_kg=alumin_obj.price_per_kg,
            weight_per_unit=alumin_obj.weight_per_unit,
            product_configuration=alumin_obj.product_configuration,
            total_linear_meter=alumin_obj.total_linear_meter,
            weight_per_lm=alumin_obj.weight_per_lm,
            surface_finish=alumin_obj.surface_finish,
            curtainwall_type=alumin_obj.curtainwall_type,
            is_conventional=alumin_obj.is_conventional,
            is_two_way=alumin_obj.is_two_way,
            in_area_input=alumin_obj.in_area_input,
        )
        temp_alumin.save()

    glass_obj = MainProductGlass.objects.filter(
        estimation_product=product, glass_primary=True).order_by('id')
    
    for glass in glass_obj:
        temp_glass = MainProductGlass(
            estimation_product=temp_product,
            is_glass_cost=glass.is_glass_cost,
            glass_specif=glass.glass_specif,
            total_area_glass=glass.total_area_glass,
            glass_base_rate=glass.glass_base_rate,
            glass_markup_percentage=glass.glass_markup_percentage,
            glass_quoted_price=glass.glass_quoted_price,
            glass_pricing_type=glass.glass_pricing_type,
            glass_width=glass.glass_width,
            glass_height=glass.glass_height,
            glass_area=glass.glass_area,
            glass_quantity=glass.glass_quantity,
            glass_primary=glass.glass_primary,
        )
        temp_glass.save()

    second_glass_obj = MainProductGlass.objects.filter(
        estimation_product=product, glass_primary=False).order_by('id')
    
    for seco_glass in second_glass_obj:
        temp_second_glass = MainProductGlass(
            estimation_product=temp_product,
            is_glass_cost=seco_glass.is_glass_cost,
            glass_specif=seco_glass.glass_specif,
            total_area_glass=seco_glass.total_area_glass,
            glass_base_rate=seco_glass.glass_base_rate,
            glass_markup_percentage=seco_glass.glass_markup_percentage,
            glass_quoted_price=seco_glass.glass_quoted_price,
            glass_pricing_type=seco_glass.glass_pricing_type,
            glass_width=seco_glass.glass_width,
            glass_height=seco_glass.glass_height,
            glass_area=seco_glass.glass_area,
            glass_quantity=seco_glass.glass_quantity,
            glass_primary=seco_glass.glass_primary,
        )
        temp_second_glass.save()
    deductions = Deduction_Items.objects.filter(
        estimation_product=product).order_by('id')
    
    for deduct_item in deductions:
        temp_deduct_item = Deduction_Items(
            estimation_product=temp_product,
            item_desc=temp_glass,
            main_price=deduct_item.main_price,
            item_width=deduct_item.item_width,
            item_height=deduct_item.item_height,
            item_quantity=deduct_item.item_quantity,
            item_deduction_area=deduct_item.item_deduction_area,
            item_deduction_price=deduct_item.item_deduction_price,
        )
        temp_deduct_item.save()
    merge_data = EstimationMainProductMergeData.objects.filter(estimation_product=product).order_by('id')
    
    for merge in merge_data:
        temp_merge = EstimationMainProductMergeData(
            estimation_product=temp_product,
            merge_product=merge.merge_product,
            merged_area=merge.merged_area,
            merged_price=merge.merged_price,
            merge_quantity=merge.merge_quantity,
            merge_aluminium_price=merge.merge_aluminium_price,
            merge_infill_price=merge.merge_infill_price,
            merge_sealant_price=merge.merge_sealant_price,
            merge_accessory_price=merge.merge_accessory_price,
        )
        temp_merge.save()
    silicon_obj = MainProductSilicon.objects.filter(
        estimation_product=product).order_by('id')
    
    for silicon in silicon_obj:
        temp_silicon = MainProductSilicon(
            estimation_product=temp_product,
            created_date=silicon.created_date,
            is_silicon=silicon.is_silicon,
            external_lm=silicon.external_lm,
            external_base_rate=silicon.external_base_rate,
            external_markup=silicon.external_markup,
            external_sealant_type=silicon.external_sealant_type,
            internal_lm=silicon.internal_lm,
            internal_base_rate=silicon.internal_base_rate,
            internal_markup=silicon.internal_markup,
            internal_sealant_type=silicon.internal_sealant_type,
            silicon_quoted_price=silicon.silicon_quoted_price,
            
            polyamide_gasket=silicon.polyamide_gasket,
            polyamide_markup=silicon.polyamide_markup,
            polyamide_base_rate=silicon.polyamide_base_rate,
            polyamide_lm=silicon.polyamide_lm,
            transom_gasket=silicon.transom_gasket,
            transom_markup=silicon.transom_markup,
            transom_base_rate=silicon.transom_base_rate,
            transom_lm=silicon.transom_lm,
            mullion_gasket=silicon.mullion_gasket,
            mullion_markup=silicon.mullion_markup,
            mullion_base_rate=silicon.mullion_base_rate,
            mullion_lm=silicon.mullion_lm,
        )
        temp_silicon.save()
        
    pricing = PricingOption.objects.filter(
        estimation_product=product).order_by('id')
    
    for price in pricing:
        try:
            temp_pricing = PricingOption.objects.get_or_create(
                estimation_product=temp_product,
                defaults={
                    'is_pricing_control': price.is_pricing_control,
                    'overhead_perce': price.overhead_perce,
                    'labour_perce': price.labour_perce,
                    'adjust_by_sqm': price.adjust_by_sqm,
                }
            )
            temp_pricing_instance = temp_pricing[0]
            temp_pricing_instance.save()
            
        except Exception as e:
            print("EXCE==>", e)

    addons = MainProductAddonCost.objects.filter(
        estimation_product=product).order_by('id')
    for addon in addons:
        temp_addon = MainProductAddonCost(
            estimation_product=temp_product,
            addons=addon.addons,
            base_rate=addon.base_rate,
            pricing_type=addon.pricing_type,
            addon_quantity=addon.addon_quantity
        )
        temp_addon.save()
    
    if product.product_type == 2:
        if not EstimationProduct_Associated_Data.objects.filter(
                estimation_main_product=temp_product.main_product, 
                associated_product=temp_product
            ).exists():
            try:
                associated_pro = EstimationProduct_Associated_Data.objects.get(estimation_main_product=product.main_product, associated_product=product)
            except:
                associated_pro = None
                
            try:
                aluminium = MainProductAluminium.objects.get(estimation_product=temp_product)
                associated_data = EstimationProduct_Associated_Data(
                    estimation_main_product=temp_product.main_product,
                    associated_product=temp_product,
                    assoicated_area=aluminium.area,
                    is_deducted= True if associated_pro.is_deducted else False,
                )
                associated_data.save()
            except MainProductAluminium.DoesNotExist:
                pass
                            

@login_required(login_url='signin')
def delete_enquiry_data(request, pk):
    
    if request.method == "POST":
        try:
            enquiry_obj = Enquiries.objects.get(pk=pk)
            estimations_objs = Estimations.objects.filter(enquiry=enquiry_obj).order_by('id')
            for estimations_obj in estimations_objs:
                clear_version(request, estimations_obj.id)
                
            # enquiry_obj.delete()
            messages.success(request, "Enquiry Deleted Successfully")
            
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.", e)
            
        return redirect('enquiry_profile', pk=enquiry_obj.id)

    context = {"url": f"/Enquiries/delete_enquiry_data/{str(pk)}/"}
    
    return render(request, "Master_settings/delete_modal.html", context)




