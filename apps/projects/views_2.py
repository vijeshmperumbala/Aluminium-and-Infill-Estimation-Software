
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import default_storage
from django.utils.timezone import now as times
from datetime import time
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, F, Sum
from amoeba.local_settings import STATIC_URL
from apps.Categories.models import Category
from apps.Workstations.models import Workstations
from django.template.loader import get_template
from apps.functions import workstation_data
from apps.helper import sum_times
from apps.product_master.models import Product_WorkStations
from apps.user.models import User
from wkhtmltopdf.views import PDFTemplateResponse
from celery import shared_task

from apps.estimations.models import (
    EstimationMainProduct, 
    MainProductAccessories,
    MainProductAluminium, 
    MainProductGlass
)

from apps.projects.forms import (
    ApprovalSpecFile,
    DeliveryNoteCartCheckoutForm,
    EPSProductDetails,
    EPSProductForm, 
    Eps_ShopFloorsSet, 
    FabricationMultiAttachment, 
    ShopFloorAttachment, 
    eps_infill_details,
    eps_openable_details,
    eps_spandrel_details,
    infillEPSform
)
from apps.projects.models import (
    ApprovalSpecFiles,
    Delivery_Note, 
    Delivery_Product_Cart_Associated, 
    Delivery_Product_Cart_Main, 
    Delivery_Product_Cart_infill,
    DeliveryNoteCart,
    EPSBuildingsModel,
    ElevationModel, 
    Eps_Associated_sub_Products, 
    Eps_Outsource_items, 
    Eps_Product_Details, 
    Eps_Products, 
    Eps_Products_For_Delivery,
    Eps_QAQC, 
    Eps_ShopFloor_associated_products, 
    Eps_ShopFloor_main_products, 
    Eps_ShopFloors, 
    Eps_infill_Details,
    Eps_infill_Temp, 
    Eps_main, 
    Fabrication_Attachments,
    FloorModel,
    InfillSchedule, 
    Inspection_History,
    ProjectEstimations, 
    ProjectsModel, 
    QAQC_infill_Products,
    SalesOrderAccessories,
    SalesOrderGroups,
    SalesOrderInfill,
    SalesOrderItems,
    SalesOrderSpecification,
    SalesSecondarySepcPanels, 
    Schedule_Product, 
    ShopFloor_Doc,
    Workstation_Associated_Product_History,
    Workstation_Associated_Products_Data, 
    Workstation_Data,
    Workstation_History
)

from amoeba.settings import DN_ID, EPS_ID, MEDIA_URL, PROJECT_NAME
from apps.shopfloors.models import Shopfloors


@login_required(login_url="signin")
def eps_consolidated_list(request, status=None):
    """
    This function generates a consolidated list of EPS objects based on their status and renders it to a
    template.
    
    """
    if status:
        eps_list = Eps_main.objects.filter(status=status)
        eps_list2 = Eps_main.objects.all()
        rcvd_eps = eps_list2.filter(status=1).count()
        in_process_eps = eps_list2.filter(status=2).count()
        cmpltd_eps = eps_list2.filter(status=3).count()
    else:
        eps_list = Eps_main.objects.all()
        rcvd_eps = eps_list.filter(status=1).count()
        in_process_eps = eps_list.filter(status=2).count()
        cmpltd_eps = eps_list.filter(status=3).count()

    context = {
        "title": f"{PROJECT_NAME} | EPS Consolidated List.",
        "eps_objs": eps_list,
        "rcvd_eps": rcvd_eps,
        "in_process_eps": in_process_eps,
        "cmpltd_eps": cmpltd_eps,
        "status": status,
    }
    return render(request, "Projects/General/Eps/eps_consolidate_view.html", context)


@login_required(login_url="signin")
def general_fabrications_view(request, status=None):
    """
    This function returns a view of EPS products with fabrication drawings requested, filtered by their
    status of received or completed.
    
    """
    if status == 'received':
        eps_products = Eps_Products.objects.filter(
                                # fabrication_drawings_req=True, 
                                eps_product_fabrication__isnull=True, 
                                eps_data__isnull=False
                            ).distinct().order_by('eps_data__created_date')
        rcvd_status = eps_products
        cmplted_status = Eps_Products.objects.filter(
                                # fabrication_drawings_req=True, 
                                eps_product_fabrication__isnull=False, 
                                eps_data__isnull=False
                            ).distinct()
    elif status == 'completed':
        eps_products = Eps_Products.objects.filter(
                                # fabrication_drawings_req=True, 
                                eps_product_fabrication__isnull=False, 
                                eps_data__isnull=False
                            ).distinct().order_by('eps_data__created_date')
        rcvd_status = Eps_Products.objects.filter(
                                # fabrication_drawings_req=True, 
                                eps_product_fabrication__isnull=True, 
                                eps_data__isnull=False
                            ).distinct()
        cmplted_status = eps_products
    else:
        eps_products = Eps_Products.objects.filter(
                                # fabrication_drawings_req=True, 
                                eps_data__isnull=False
                            ).distinct().order_by('eps_data__created_date')
        rcvd_status = eps_products.filter(eps_product_fabrication__isnull=True)
        cmplted_status = eps_products.filter(eps_product_fabrication__isnull=False)

    context = {
        "title": f"{PROJECT_NAME} | Fabrications Consolidated List.",
        "eps_products": eps_products,
        "rcvd_status": rcvd_status,
        "cmplted_status": cmplted_status,
        "status": status,
    }
    return render(request, "Projects/General/Fabrications/fabrication_view.html", context)


@login_required(login_url='signin')
def fabrication_multi_attachment(request, pk):
    """
    This function handles the uploading of multiple fabrication files and saves them as attachments to
    an EPS product.
    """
    eps_product = Eps_Products.objects.get(pk=pk)
    form = FabricationMultiAttachment()
    if request.method == "POST":
        form = FabricationMultiAttachment(request.POST, request.FILES)
        fabrication_note = request.POST.get('fabrication_note')
        if form.is_valid():
            eps_product.fabrication_note = fabrication_note
            eps_product.save()
            
            for f in request.FILES.getlist('fabrication_docs'):
                filename = default_storage.save('fabrications/'+str(f.name), f)
                attachment = Fabrication_Attachments.objects.create(
                    fabrication_docs = filename,
                    eps_product=eps_product
                )
                attachment.save()
            
            messages.success(request, "Successfully Uploaded Fabrication Files")
        else:
            print('form_error===>', form.errors)
            messages.error(request, "Please Check Uploaded File.")
        return redirect('eps_view_fabrications', pk=eps_product.id)
        
    context = {
        "eps_product": eps_product,
        "form": form
    }
    return render(request, "Projects/General/Fabrications/fabrication_file_uploader.html", context)


@login_required(login_url="signin")
def general_production_view(request, status=None):
    """
    This function retrieves and displays a list of EPS products with their respective statuses.
    """
    if status:
        eps_products = Eps_Products.objects.filter(product_status=status, eps_data__isnull=False).order_by('-eps_data__created_date')
        eps_products2 = Eps_Products.objects.filter(eps_data__isnull=False)
        rcvd_products = eps_products2.filter(product_status=1).count()
        awtg_products = eps_products2.filter(product_status=2).count()
        hold_products = eps_products2.filter(product_status=3).count()
        scheduled_products = eps_products2.filter(product_status=4).count()
    else:
        eps_products = Eps_Products.objects.filter(eps_data__isnull=False).order_by('-eps_data__created_date')
        rcvd_products = eps_products.filter(product_status=1).count()
        awtg_products = eps_products.filter(product_status=2).count()
        hold_products = eps_products.filter(product_status=3).count()
        scheduled_products = eps_products.filter(product_status=4).count()
        
    context = {
        "title": f'{PROJECT_NAME} | Production Consolidated List.',
        "eps_products": eps_products,
        "rcvd_products": rcvd_products,
        "awtg_products": awtg_products,
        "hold_products": hold_products,
        "scheduled_products": scheduled_products,
        "status": status,
    }
    return render(request, "Projects/General/Productions/production_view.html", context)


@login_required(login_url='signin')
def aluminium_status_update(request, pk):
    """
    This function updates the aluminium status of an EPS product based on user input and redirects to
    the EPS production view page.
    
    """
    eps_product = Eps_Products.objects.get(pk=pk)
    status = {
        "2": "Awaiting Materials",
        "3": "In Stock",
        "4": "Partial Stock",
        
    }
    if request.method == 'POST':
        aluminium_status = request.POST.get('status')
        eps_product.aluminium_status = int(aluminium_status)
        eps_product.save()
        messages.success(request, "Successfully Updated Aluminium Status.")
        
        return redirect('eps_production_view', pk=eps_product.id)
    
    context = {
        "eps_product": eps_product,
        "status": status
    }
    return render(request, "Projects/Eps/eps_view/product_status_update.html", context)


@login_required(login_url='signin')
def alumin_status_short_update(request, pk, status, re_dir=None):
    """
    This function updates the aluminium status of an EPS product and redirects the user to a specific
    page based on the re_dir parameter.
    
    """
    eps_product = Eps_Products.objects.get(pk=pk)
    eps_product.aluminium_status = int(status)
    eps_product.save()
    messages.success(request, "Successfully Updated Aluminium Status.")
    if re_dir == 'production':
        return redirect('eps_production_view', pk=eps_product.id)
    elif re_dir == 'shopfloor':
        return redirect('general_shopfloor_view', status=1)
    else:
        return redirect('general_production_view', status=1)
    

@login_required(login_url='signin')
def accessory_status_update(request, pk):
    """
    This function updates the accessory status of an EPS product based on user input and redirects to
    the EPS production view page.
    
    """
    eps_product = Eps_Products.objects.get(pk=pk)
    status = {
        "3": "In Stock",
        "2": "Out of Stock",
        "4": "Partial Stock",
    }
    if request.method == 'POST':
        accessory_status = request.POST.get('status')
        eps_product.accessory_status = int(accessory_status)
        eps_product.save()
        messages.success(request, "Successfully Updated Accessory Status.")
        
        return redirect('eps_production_view', pk=eps_product.id)
    
    context = {
        "eps_product": eps_product,
        "status": status
    }
    return render(request, "Projects/Eps/eps_view/product_status_update.html", context)


@login_required(login_url='signin')
def accessory_status_short_update(request, pk, status, re_dir=None):
    """
    This function updates the accessory status of an EPS product and redirects the user to a production
    view page.
    
    """
    eps_product = Eps_Products.objects.get(pk=pk)
    eps_product.accessory_status = int(status)
    eps_product.save()
    messages.success(request, "Successfully Updated Accessory Status.")
    if re_dir == 'production':
        return redirect('eps_production_view', pk=eps_product.id)
    elif re_dir == 'shopfloor':
        return redirect('general_shopfloor_view', status=1)
    else:
        return redirect('general_production_view', status=1)


@login_required(login_url='signin')
def general_new_infill(request, pk, dirc=None):
    """
    This function handles the creation of new infill details for a specific EPS product.
    
    """
    eps_product = Eps_Products.objects.get(pk=pk)

    product_data = SalesOrderItems.objects.get(pk=eps_product.eps_product.product.id)
    # product_data = EstimationMainProduct.objects.get(pk=eps_product.eps_product.product.id)
    eps_products_details = Eps_Product_Details.objects.filter(main_product=eps_product)
    
    try:
        pro_infill_details = SalesOrderSpecification.objects.get(pk=product_data.specification_Identifier.id)
        pro_sec_infill_details = SalesSecondarySepcPanels.objects.filter(specifications=product_data.specification_Identifier.id)
        
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
    except Exception:
        pro_infill_details = None
        pro_sec_infill_details = None
        
        flag_vision_panel = None
        flag_spandrel_panel = None
        flag_openable_panel = None
        
        
    # try:
    #     pro_infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
    #     pro_sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
        
    #     flag_vision_panel = True if pro_infill_details.panel_type == 1 else None
    #     flag_spandrel_panel = True if pro_infill_details.panel_type == 2 else None
    #     flag_openable_panel = True if pro_infill_details.panel_type == 3 else None
        
    #     for pro_sec_infill in pro_sec_infill_details:
    #         if not flag_vision_panel:
    #             flag_vision_panel = True if pro_sec_infill.panel_type == 1 else None
    #         if not flag_spandrel_panel:
    #             flag_spandrel_panel = True if pro_sec_infill.panel_type == 2 else None
    #         if not flag_openable_panel:
    #             flag_openable_panel = True if pro_sec_infill.panel_type == 3 else None
    # except Exception:
    #     pro_infill_details = None
    #     pro_sec_infill_details = None
        
    #     flag_vision_panel = None
    #     flag_spandrel_panel = None
    #     flag_openable_panel = None
        
    eps_product_form = infillEPSform(instance=eps_product)
    
    eps_infill_form = eps_infill_details(eps_product.eps_product.product.specification_Identifier)
    EPSINFILLDETAILS = modelformset_factory(
        Eps_infill_Details, form=eps_infill_form, extra=1)
    infill_detail_formset = EPSINFILLDETAILS(
        queryset=Eps_infill_Details.objects.none(), prefix='eps_infill')
    
    # eps_infill_form = eps_infill_details(eps_product.eps_product.product)
    # EPSINFILLDETAILS = modelformset_factory(Eps_infill_Details, form=eps_infill_form, extra=1, can_delete=True)
    
    eps_spandrel_form = eps_spandrel_details(eps_product.eps_product.product.specification_Identifier)
    EPSSPANDRELDETAILS = modelformset_factory(Eps_infill_Details, form=eps_spandrel_form, extra=1, can_delete=True)
    spandrel_detail_formset = EPSSPANDRELDETAILS(queryset=Eps_infill_Details.objects.none(), prefix='eps_spandrel_panel')
    
    eps_openable_form = eps_openable_details(eps_product.eps_product.product.specification_Identifier)
    EPSOPENALEDETAILS = modelformset_factory(Eps_infill_Details, form=eps_openable_form, extra=1, can_delete=True)
    openable_panel = EPSOPENALEDETAILS(queryset=Eps_infill_Details.objects.none(), prefix='eps_openable_panel')

    if request.method == "POST":
        eps_product_form = infillEPSform(request.POST, instance=eps_product)
        infill_detail_formset = EPSINFILLDETAILS(request.POST, prefix='eps_infill')
        spandrel_detail_formset = EPSSPANDRELDETAILS(request.POST, prefix='eps_spandrel_panel')
        openable_panel = EPSOPENALEDETAILS(request.POST, prefix='eps_openable_panel')
        is_vp = request.POST.get('is_vp')
        is_sp = request.POST.get('is_sp')
        is_op = request.POST.get('is_op')
        
        eps_product.is_vp = True if is_vp else False
        eps_product.is_sp = True if is_sp else False
        eps_product.is_op = True if is_op else False
        eps_product.save()
        if eps_product_form.is_valid():
            eps_product_form.save()
            
        
        for item2 in infill_detail_formset:
            if item2.is_valid():
                item_obj2 = item2.save(commit=False)
              
                if item_obj2.infill_quantity and item_obj2.infill_area:
                    item_obj2.main_product = eps_product
                    item_obj2.panel_type = 1
                    item_obj2.save()
                    # eps_product.no_infill_data=True
                    # eps_product.save()
                else:
                    print("Please Enter Infill Quantity.")
            else:
                print("Error in sub formset infill ==>", item2.errors)
                messages.error(request, item2.errors)
        
        for item3 in spandrel_detail_formset:
            if item3.is_valid():
                item_obj3 = item3.save(commit=False)
                if item_obj3.infill_quantity:
                    item_obj3.main_product = eps_product
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
                    item_obj4.main_product = eps_product
                    item_obj4.panel_type = 3
                    item_obj4.save()
                else:
                    # messages.error(request, "Please Enter Quantity.")
                    print("Please Enter Openable Panel Quantity.")
            else:
                print("Error in sub formset Openable ==>", item4.errors)
                messages.error(request, item4.errors)
                
        if dirc:
            return redirect('view_eps', eps=eps_product.eps_data.id)
        else:
            return redirect('eps_production_view', pk=eps_product.id)

    context = {
        "eps_product": eps_product,
        "infill_detail_formset": infill_detail_formset,
        "dirc": dirc,
        "product_data": product_data,
        "eps_products_details": eps_products_details,
        "spandrel_detail_formset": spandrel_detail_formset,
        "openable_panel": openable_panel,
        
        "eps_product_form": eps_product_form,
        "flag_vision_panel": flag_vision_panel,
        "flag_spandrel_panel": flag_spandrel_panel,
        "flag_openable_panel": flag_openable_panel,
    }
    return render(request, "Projects/General/Productions/new_infill.html", context)


@login_required(login_url='signin')
def product_details_update(request, pk):
    """
    This function updates the details of a product and its associated product details.
    
    """
    product = Eps_Product_Details.objects.get(pk=pk)
    EPS_ProductDetalForm = EPSProductDetails(product.main_product.eps_product.product.category)
    PRODUCTDETAILFORMSET = modelformset_factory(Eps_Product_Details, form=EPS_ProductDetalForm, extra=0, can_delete=True)
    product_detail_formset = PRODUCTDETAILFORMSET(queryset=Eps_Product_Details.objects.filter(pk=pk), prefix="eps_product_detail")
    
    if request.method == "POST":
        product_detail_formset = PRODUCTDETAILFORMSET(request.POST, prefix="eps_product_detail")
        if product_detail_formset.is_valid():
            for item in product_detail_formset:
                if item.is_valid():
                    item_obj = item.save(commit=False)
                    if item_obj.product_quantity:
                        item_obj.save()
                    else:
                        messages.error(request, "Please Enter Quantity.")
                        print('Please Enter PRODUCt Quantity')
                else:
                    print("Error in sub formset ==>", item.errors)
                    messages.error(request, item.errors)
        else:
            messages.error(request, "Error in Form Submition..") 
            
        return redirect('eps_production_view', pk=product.main_product.id)
    
    context = {
        "product": product,
        "product_detail_formset": product_detail_formset,
    }
    return render(request, "Projects/General/Productions/product_update.html", context)

def infill_outsource_fun(product):
    products_obj = Eps_Products.objects.get(pk=product)
    infill_details = Eps_infill_Details.objects.filter(
        main_product=products_obj)
    
    for infill in infill_details:
        infill.is_outsourced = True
        infill.save()
    #     outsource_product = Eps_Outsource_items(
    #                             infill_product=infill, 
    #                             received_quantity=0, 
    #                             remaining_quantity=infill.infill_quantity, 
    #                             actual_quantity=infill.infill_quantity
    #                         )
    #     outsource_product.save()
    products_obj.infill_status = 2
    products_obj.save()
    return products_obj

            
@login_required(login_url='signin')
def set_shopfloor(request, pk):
    """
    The function `set_shopfloor` updates the shopfloor data for a given product and saves it to the
    database.
    
    """
    eps_product = Eps_Products.objects.get(pk=pk)
    products = Eps_Product_Details.objects.filter(main_product=eps_product)
    shopfloor_eps_data, shopfloor_attachments = get_shopfloor_data(eps_product)
    main_form, form = get_forms(shopfloor_eps_data, request)
    shopfloor_items = Eps_ShopFloor_main_products.objects.filter(main_products__main_product=eps_product)
    associated_products = Eps_Associated_sub_Products.objects.filter(main_product__main_product=eps_product)
    # form = ScheduleProductForm(instance=main_product)
    main_product_quantity = 0
    
    if request.method == "POST":
        product_status = request.POST.get('product_status')
        product_stage = request.POST.get('product_stage')
        start_date = request.POST.get('start_date')
        
        eps_product.product_status = int(product_status)
        eps_product.save()
        if (
            product_status != '2'
            and product_status != '3'
            and not shopfloor_items
        ):
            if product_stage == '2':
                save_shopfloor_data(eps_product, main_form, form, request.FILES)
                save_shopfloor_items(products, associated_products, eps_product, shopfloor_items)
                update_eps_status(eps_product)
                shopfloor_items2 = Eps_ShopFloor_main_products.objects.filter(main_products__main_product=eps_product)
                schedule_product_obj = Schedule_Product(
                                            product=shopfloor_items2.first(),
                                            start_date=start_date,
                                            expected_completion=main_form.cleaned_data['required_delivery_date'],
                                            eps=eps_product.eps_data,
                                            shopfloor_status=1,
                                            processing_type=product_stage,
                                            notes=main_form.cleaned_data['shop_floor_notes']
                                        )
                schedule_product_obj.save()
            else:
                # infill_datas = Eps_Outsource_items.objects.filter(infill_product__is_outsourced=True)
                infill_schedule_obj = InfillSchedule(
                    product=eps_product,
                    eps=eps_product.eps_data,
                )
                infill_outsource_fun(eps_product.id)
                infill_schedule_obj.save()
                
            eps_product.shopfloor_status = 1
            eps_product.save()
            messages.success(request, "Successfully Added ShopFloor")
        else:
            print('NO shopfloor_items')

        return redirect('eps_production_view', pk=eps_product.id)

    context = {
        "eps_product": eps_product,
        "form": form,
        "main_form": main_form,
        "eps_data": eps_product.eps_data,
        "shopfloor_eps_data": shopfloor_eps_data
    }
    return render(request, "Projects/General/Productions/set_shopfloor.html", context)

def get_shopfloor_data(eps_product):
    """
    The function "get_shopfloor_data" retrieves shopfloor data and attachments related to a given EPS
    product.
    """
    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(eps=eps_product.eps_data, product=eps_product)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None
    return shopfloor_eps_data, shopfloor_attachments


def get_forms(shopfloor_eps_data, request):
    """
    The function "get_forms" returns two forms, one for shopfloor_eps_data and one for
    ShopFloorAttachment, based on the request method.
    
    """
    if not shopfloor_eps_data:
        main_form = Eps_ShopFloorsSet()
    else:
        main_form = Eps_ShopFloorsSet(instance=shopfloor_eps_data)
    form = ShopFloorAttachment()
    if request.method == "POST":
        main_form = Eps_ShopFloorsSet(request.POST, instance=shopfloor_eps_data)
        form = ShopFloorAttachment(request.POST, request.FILES)
    return main_form, form


def save_shopfloor_data(eps_product, main_form, form, files):
    """
    The function saves shopfloor data by creating a main form object, assigning values to its fields,
    saving it, and then creating and saving attachments for each file in the files parameter.
    
    """
    main_form_obj = main_form.save(commit=False)
    main_form_obj.eps = eps_product.eps_data
    main_form_obj.product = eps_product
    main_form_obj.save()

    for f in files.getlist('shopfloor_doc'):
        filename = default_storage.save(f'shopfloor/{str(f.name)}', f)
        attachment = ShopFloor_Doc.objects.create(
            shopfloor_doc=filename,
            eps_product=main_form_obj
        )
        attachment.save()


def save_shopfloor_items(products, associated_products, eps_product, shopfloor_items):   
    if not shopfloor_items:
        for product in products:
            shopfloor_item = Eps_ShopFloor_main_products(
                main_products=product,
                product_quantity=product.product_quantity,
                remaining_quantity=product.product_quantity
            )
            shopfloor_item.save()
            
        if associated_products:
            for associated in associated_products:
                try:
                    shopfloor_associated = Eps_ShopFloor_associated_products(
                        main_products=associated,
                        product_quantity=associated.received_quantity,
                        remaining_quantity=associated.remaining_quantity
                    )
                    shopfloor_associated.save()
                except Exception as e:
                    print('EXCe==>', e)


def update_eps_status(eps_product):
    eps_obj = Eps_main.objects.get(pk=eps_product.eps_data.id)
    eps_obj.status = 2
    eps_obj.save()


def move_to_workstation(request, pk):
    eps_product = Eps_Products.objects.get(pk=pk)
    # products = Eps_Product_Details.objects.filter(main_product=eps_product)
    
    shopfloor_items = Eps_ShopFloor_main_products.objects.filter(main_products__main_product=eps_product)
    
    # associated_products = Eps_Associated_sub_Products.objects.filter(main_product__main_product=eps_product)
    # save_shopfloor_items(products, associated_products, eps_product, shopfloor_items)
    
    try:
        schedule_product = Schedule_Product.objects.get(product__main_products__main_product=eps_product.id)
    except Exception:
        schedule_product = None
        
    if shopfloor_items:
        if shopfloor_items.first().main_products.main_product.eps_product.product.product:
            
            init_workstation1 = Product_WorkStations.objects.filter(
                                    product=shopfloor_items.first().main_products.main_product.eps_product.product.product.id
                                ).first()
        else:
            init_workstation1 = Product_WorkStations.objects.filter(
                                    product=shopfloor_items.first().main_products.main_product.eps_product.product.panel_product.id
                                ).first()
            
        if init_workstation1:
            schedule_product.in_workstation = True
            schedule_product.save()
            for product in shopfloor_items:
                
                if not product.main_products.main_product.eps_product.product.category.is_curtain_wall:
                    # if product.main_products.main_product.eps_product.product.category.handrail:
                    #     received_quantity = product.product_quantity*product.main_products.product_length
                    #     remaining_quantity = product.product_quantity*product.main_products.product_length
                    # else:
                    
                    received_quantity = product.product_quantity
                    remaining_quantity = product.product_quantity
                        
                    
                    add_to_workstation = Workstation_Data(
                                                created_by=request.user, 
                                                product=product, 
                                                received_quantity=received_quantity, 
                                                remaining_quantity=remaining_quantity, 
                                                workstation=init_workstation1.workstation,
                                                eps_product_id=eps_product
                                            )
                    
                else:
                    
                    received_quantity = product.product_quantity
                    remaining_quantity = product.product_quantity
                    
                    add_to_workstation = Workstation_Data(
                                                created_by=request.user, 
                                                product=product, 
                                                received_quantity=received_quantity, 
                                                remaining_quantity=remaining_quantity, 
                                                workstation=init_workstation1.workstation,
                                                eps_product_id=eps_product,
                                            )
                add_to_workstation.save()
                
                if product.main_products.main_product.eps_product.product.product:
                    init_workstation = Product_WorkStations.objects.filter(
                                            product=product.main_products.main_product.eps_product.product.product.id
                                        ).first()
                else:
                    init_workstation = Product_WorkStations.objects.filter(
                                            product=product.main_products.main_product.eps_product.product.panel_product.id
                                        ).first()
                    
                if init_workstation:
                    for associated_product in Eps_Associated_sub_Products.objects.filter(main_product=product.main_products):
                        # if associated_product.main_product.main_product.eps_product.product.product:
                        #     if associated_product.main_product.main_product.eps_product.product.product.have_associated_product:
                        #         qty = associated_product.main_product.main_product.eps_product.product.product.assocated_quantity
                        #     else:
                        #         qty = 1
                        # else:
                        #     if associated_product.main_product.main_product.eps_product.product.panel_product.have_associated_product:
                        #         qty = associated_product.main_product.main_product.eps_product.product.panel_product.assocated_quantity
                        #     else:
                        #         qty = 1
                            
                        workstation_associated_product = Workstation_Associated_Products_Data(
                                                                        created_by=request.user, 
                                                                        product=associated_product,
                                                                        # received_quantity=float(associated_product.received_quantity) * float(qty), 
                                                                        received_quantity=float(associated_product.received_quantity),
                                                                        remaining_quantity=float(associated_product.remaining_quantity),
                                                                        workstation=init_workstation.workstation,
                                                                        eps_product_id=eps_product
                                                                    )
                        workstation_associated_product.save()
                
                    if schedule_product:
                        schedule_product.shopfloor_status = 2
                        schedule_product.save()
                        
                    eps_product.shopfloor_status = 4
                    eps_product.save()
                    messages.success(request, "Successfully Moved to Workstation")
                else:
                    messages.error(request, "Please add workstations for the specific product.")
        else:
            messages.error(request, "Please add workstations for the specific product.")   
            
        return redirect('general_shopfloor_view', status=1)

def product_details_delete(request, pk):
    product_details = Eps_Product_Details.objects.get(pk=pk)
    product_details.delete()
    return JsonResponse({'success': True})


def product_infill_delete(request, pk):
    product_details = Eps_infill_Details.objects.get(pk=pk)
    product_details.delete()
    return JsonResponse({'success': True})

def product_temp_infill_delete(request, pk):
    product_details = Eps_infill_Temp.objects.get(pk=pk)
    product_details.delete()
    return JsonResponse({'success': True})

def sales_product_infill_delete(request, pk):
    product_details = SalesOrderInfill.objects.get(pk=pk)
    product_details.delete()
    return JsonResponse({'success': True})

@login_required(login_url='signin')
def infill_outsource(request, pk):
    """
    The function sets the is_outsourced flag to True for all infill details of a given product, creates
    corresponding outsource items with received quantity as 0 and remaining quantity as infill quantity,
    and updates the infill status of the product to 2.
    """
    
    products_obj = Eps_Products.objects.get(pk=pk)
    infill_details = Eps_infill_Details.objects.filter(
        main_product=products_obj)
    
    for infill in infill_details:
        infill.is_outsourced = True
        outsource_product = Eps_Outsource_items(infill_product=infill, received_quantity=0, remaining_quantity=infill.infill_quantity)
        outsource_product.save()
        infill.save()
        products_obj.infill_status = 2
        products_obj.save()
    return redirect('eps_production_view', pk=products_obj.id)


"""
Outsource View
"""

@login_required(login_url='signin')
def general_outsource_view(request, status=None):
    """
    This function generates a view for a consolidated list of outsourced EPS products with their
    respective statuses.
    
    """
    if status:
        # eps = [product.infill_product.main_product.eps_data.id for product in Eps_Outsource_items.objects.filter(infill_product__is_outsourced=True, status=status)]
        eps = [product.main_product.eps_data.id for product in Eps_infill_Details.objects.filter(is_outsourced=True, main_product__infill_status=status)]
        eps_list = Eps_main.objects.filter(pk__in=eps).order_by('-id')
        # infill_datas = Eps_Outsource_items.objects.filter(infill_product__is_outsourced=True)
        infill_datas = Eps_infill_Details.objects.filter(is_outsourced=True)
        pending_infill = infill_datas.filter(main_product__infill_status=1).count()
        outsourced_infill = infill_datas.filter(main_product__infill_status=2).count()
        receiving_infill = infill_datas.filter(main_product__infill_status=3).count()
        received_infill = infill_datas.filter(main_product__infill_status=4).count()
        # pending_infill = infill_datas.filter(status=1).count()
        # outsourced_infill = infill_datas.filter(status=2).count()
        # receiving_infill = infill_datas.filter(status=3).count()
        # received_infill = infill_datas.filter(status=4).count()
    else:
        # eps = [product.infill_product.main_product.eps_data.id for product in Eps_Outsource_items.objects.filter(infill_product__is_outsourced=True)]
        eps = [product.main_product.eps_data.id for product in Eps_infill_Details.objects.filter(is_outsourced=True)]
        eps_list = Eps_main.objects.filter(pk__in=eps).order_by('-id')
        # infill_datas = Eps_Outsource_items.objects.filter(infill_product__is_outsourced=True)
        # infill_datas = Eps_infill_Details.objects.filter(is_outsourced=True)
        # pending_infill = infill_datas.filter(status=1).count()
        # outsourced_infill = infill_datas.filter(status=2).count()
        # receiving_infill = infill_datas.filter(status=3).count()
        # received_infill = infill_datas.filter(status=4).count()
        infill_datas = Eps_infill_Details.objects.filter(is_outsourced=True)
        pending_infill = infill_datas.filter(main_product__infill_status=1).count()
        outsourced_infill = infill_datas.filter(main_product__infill_status=2).count()
        receiving_infill = infill_datas.filter(main_product__infill_status=3).count()
        received_infill = infill_datas.filter(main_product__infill_status=4).count()

    context = {
        "title": f"{PROJECT_NAME} | Outsource Consolidated List.",
        "eps_objs": eps_list,
        "pending_infill": pending_infill,
        "outsourced_infill": outsourced_infill,
        "receiving_infill": receiving_infill,
        "received_infill": received_infill,
        "status": status,
    }
    return render(request, "Projects/General/Outsource/outsource_view.html", context)


"""
Shopfloor View
"""


@login_required(login_url='signin')
def general_shopfloor_view(request, status=None):
    """
    This function retrieves and displays a list of EPS products filtered by shopfloor status and
    organized by shopfloor.
    
    """
    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = shopfloor_objs.first()
    shopfloor = Eps_ShopFloors.objects.filter(shopfloor=shopfloor_obj)

    if status:
        temp = Eps_ShopFloor_main_products.objects.filter(main_products__main_product__in=[item.product for item in shopfloor])
        eps_products = Eps_Products.objects.filter(pk__in=[product.main_products.main_product.id for product in temp], shopfloor_status=status).order_by('-eps_data__created_date')
        eps_products2 = Eps_Products.objects.filter(pk__in=[product.main_products.main_product.id for product in temp])
        rcvd_products = eps_products2.filter(shopfloor_status=1).count()
        scheduled_products = eps_products2.filter(shopfloor_status=2).count()
        hold_products = eps_products2.filter(shopfloor_status=3).count()
        comld_products = eps_products2.filter(shopfloor_status=4).count()
    else:
        temp = Eps_ShopFloor_main_products.objects.filter(main_products__main_product__in=[item.product for item in shopfloor])
        eps_products = Eps_Products.objects.filter(pk__in=[product.main_products.main_product.id for product in temp]).order_by('-eps_data__created_date')
        rcvd_products = eps_products.filter(shopfloor_status=1).count()
        scheduled_products = eps_products.filter(shopfloor_status=2).count()
        hold_products = eps_products.filter(shopfloor_status=3).count()
        comld_products = eps_products.filter(shopfloor_status=4).count()

    context = {
        "title": f"{PROJECT_NAME} | Shopfloor Consolidated List.",
        "eps_products": eps_products,
        "rcvd_products": rcvd_products,
        "hold_products": hold_products,
        "scheduled_products": scheduled_products,
        "comld_products": comld_products,
        "status": status,
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
    }
        

    return render(request, "Projects/General/ShopFloor/shopfloor_view.html", context)


@login_required(login_url='signin')
def shopfloor_filter(request, shopfloor, status=None):
    """
    This function filters and displays a list of products based on their shopfloor status and the
    selected shopfloor.
    
    """
    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = Shopfloors.objects.get(pk=shopfloor)
    shopfloor = Eps_ShopFloors.objects.filter(shopfloor=shopfloor_obj)

    if status:
        temp = Eps_ShopFloor_main_products.objects.filter(main_products__main_product__in=[item.product for item in shopfloor])
        eps_products = Eps_Products.objects.filter(pk__in=[product.main_products.main_product.id for product in temp], shopfloor_status=status).order_by('eps_data__created_date')
        eps_products2 = Eps_Products.objects.filter(pk__in=[product.main_products.main_product.id for product in temp])
        rcvd_products = eps_products2.filter(shopfloor_status=1).count()
        scheduled_products = eps_products2.filter(shopfloor_status=2).count()
        hold_products = eps_products2.filter(shopfloor_status=3).count()
        comld_products = eps_products2.filter(shopfloor_status=4).count()
    else:
        temp = Eps_ShopFloor_main_products.objects.filter(main_products__main_product__in=[item.product for item in shopfloor])
        eps_products = Eps_Products.objects.filter(pk__in=[product.main_products.main_product.id for product in temp]).order_by('eps_data__created_date')
        rcvd_products = eps_products.filter(shopfloor_status=1).count()
        scheduled_products = eps_products.filter(shopfloor_status=2).count()
        hold_products = eps_products.filter(shopfloor_status=3).count()
        comld_products = eps_products.filter(shopfloor_status=4).count()

    context = {
        "title": f"{PROJECT_NAME} | Shopfloor Consolidated List.",
        "eps_products": eps_products,
        "rcvd_products": rcvd_products,
        "comld_products": comld_products,
        "hold_products": hold_products,
        "scheduled_products": scheduled_products,
        "status": status,
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
    }

    return render(request, "Projects/General/ShopFloor/shopfloor_view.html", context)
    
    
@login_required(login_url='signin')
def shopfloor_projects(request, pk):
    """
    This function retrieves data on shopfloor projects and EPS data for each project and renders it in a
    template.
    
    """
    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = Shopfloors.objects.get(pk=pk)
    projects = set([product.main_products.main_product.eps_data.project for product in Eps_ShopFloor_main_products.objects.all()])

    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)

    context = {
        "title": f"{PROJECT_NAME} | Shopfloor",
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
        "projects": projects,
        "eps_data": eps_data,
    }
    return render(request, "Projects/General/ShopFloor/shopfloor_view.html", context)


@login_required(login_url='signin')
def shopfloor_detail_eps_list(request, pk):
    """
    This function retrieves data related to shopfloor and EPS objects and renders it in a view.
    
    """
    eps_obj = Eps_main.objects.filter(eps_shopfloor_data__isnull=False,  project=pk)

    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = Shopfloors.objects.get(pk=Eps_ShopFloors.objects.get(eps=eps_obj.last().id).shopfloor.id)
    projects = set([product.main_products.main_product.eps_data.project for product in Eps_ShopFloor_main_products.objects.all()])
    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)

    context = {
        "title": f"{PROJECT_NAME} | Shopfloor",
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
        "projects": projects,
        "eps_data": eps_data,
        "eps_obj": eps_obj,
    }
    return render(request, "Projects/General/ShopFloor/shopfloor_view.html", context)


@login_required(login_url="signin")
def shopfloor_details(request, pk):
    """
    This function retrieves and organizes data related to shopfloor details for a specific EPS item.
    
    """
    eps_item = Eps_main.objects.get(pk=pk)
    eps_obj = Eps_main.objects.filter(eps_shopfloor_data__isnull=False,  project=eps_item.project.id)
    products_obj = Eps_ShopFloor_main_products.objects.filter(main_products__main_product__eps_data=eps_item)\
        .distinct('main_products__main_product__eps_product__product')

    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(eps=eps_item)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None

    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = Shopfloors.objects.get(pk=Eps_ShopFloors.objects.get(eps=eps_item.id).shopfloor.id)
    projects = set([product.main_products.main_product.eps_data.project for product in Eps_ShopFloor_main_products.objects.all()])

    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)

    context = {
        "title": f"{PROJECT_NAME} | Shopfloor",
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
        "projects": projects,
        "eps_data": eps_data,
        "eps_obj": eps_obj,
        "eps_item": eps_item,
        'products_obj': products_obj,
        "shopfloor_eps_data": shopfloor_eps_data,
        "shopfloor_attachments": shopfloor_attachments,
    }
    return render(request, "Projects/General/ShopFloor/shopfloor_view.html", context)
    

@login_required(login_url='signin')
def shopfloor_product_detail_view(request, pk):
    """
    This function renders a view for a shopfloor product detail page, displaying various details and
    attachments related to the product.
    
    """
    eps_product_shopfloor = Eps_ShopFloor_main_products.objects.get(pk=pk)

    eps_product = Eps_Products.objects.get(pk=eps_product_shopfloor.main_products.main_product.id)
    product_obj = EstimationMainProduct.objects.get(
        pk=eps_product.eps_product.product.id)
    products_details = Eps_ShopFloor_main_products.objects.filter(
        main_products__main_product=eps_product)
    infill_details = Eps_infill_Details.objects.filter(
        main_product=eps_product)
    product_details = MainProductAluminium.objects.get(
        estimation_product=product_obj)

    attachments = Fabrication_Attachments.objects.filter(
        eps_product=eps_product)

    try:
        pro_infill_details = MainProductGlass.objects.get(
            estimation_product=product_obj, glass_primary=True)
        pro_sec_infill_details = MainProductGlass.objects.filter(
            estimation_product=product_obj, glass_primary=False)
    except Exception as e:
        pro_infill_details = None
        pro_sec_infill_details = None


    eps_item = Eps_main.objects.get(pk=eps_product.eps_data.id)
    eps_obj = Eps_main.objects.filter(eps_shopfloor_data__isnull=False,  project=eps_item.project.id)
    products_obj = Eps_ShopFloor_main_products.objects.filter(main_products__main_product__eps_data=eps_item).distinct('main_products__main_product__eps_product__product')

    try:
        scedule_details = Schedule_Product.objects.get(product__main_products__main_product=eps_product)
    except Schedule_Product.DoesNotExist:
        scedule_details = None

    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(eps=eps_item)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except:
        shopfloor_eps_data = None
        shopfloor_attachments = None

    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = Shopfloors.objects.get(pk=Eps_ShopFloors.objects.get(eps=eps_item.id).shopfloor.id)
    projects = set([product.main_products.main_product.eps_data.project for product in Eps_ShopFloor_main_products.objects.all()])

    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)

    context = {
        "title": f"{PROJECT_NAME} | Shopfloor",
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
        "projects": projects,
        "eps_data": eps_data,
        "eps_obj": eps_obj,
        "eps_item": eps_item,
        'products_obj': products_obj,
        "eps_product": eps_product,
        "product_obj": product_obj,
        "products_details": products_details,
        "infill_details": infill_details,
        "product_details": product_details,
        "attachments": attachments,
        "pro_infill_details": pro_infill_details,
        "pro_sec_infill_details": pro_sec_infill_details,
        "shopfloor_eps_data": shopfloor_eps_data,
        "shopfloor_attachments": shopfloor_attachments,
        "scedule_details": scedule_details,
        "eps_product_shopfloor": eps_product_shopfloor,
    }
    return render(request, "Projects/General/ShopFloor/shopfloor_view.html", context)


"""
Workstation View
"""


@login_required(login_url='signin')
def general_workstation_view(request):
    """
    This function retrieves data from various models and renders a consolidated list of workstations for
    a specific shopfloor and products that are not yet completed.
    
    """
    shopfloor_objs = Shopfloors.objects.all().order_by('id')

    shopfloor_obj = Shopfloors.objects.get(pk=shopfloor_objs.first().id)
    eps_shopfloors = Eps_ShopFloors.objects.filter(shopfloor=shopfloor_obj)
    workstations = Workstations.objects.all().order_by('-id')
    
    products_obj = Schedule_Product.objects.filter(
        Q(product__main_products__main_product__eps_data__in=[eps_shopfloor.eps for eps_shopfloor in eps_shopfloors], shopfloor_status__in=[1, 2, 3]) 
        # & ~Q(product__product_productworkstation__completed_quantity=F('product__product_productworkstation__received_quantity')
        # & ~Q(product__product_productworkstation__completed_quantity=0
        # )
        & Q(in_workstation=True) 
    ).order_by('-id').distinct('id')
    
    
    # associated_products = Workstation_Associated_Products_Data.objects.filter(eps_product_id__eps_data__in=[eps_shopfloor.eps.id for eps_shopfloor in eps_shopfloors], is_completed=False).distinct('product')
    # associated_products = Workstation_Associated_Products_Data.objects.filter(eps_product_id__eps_data__in=[eps_shopfloor.eps.id for eps_shopfloor in eps_shopfloors], is_completed=False).distinct('eps_product_id')
    
    associated_products = Schedule_Product.objects.filter(
                                # Q(product__main_products__main_product__eps_data__in=[eps_shopfloor.eps for eps_shopfloor in eps_shopfloors])
                                Q(shopfloor_status__in=[1, 2, 3]) 
                                # & Q(in_workstation=True) &
                                # (Q(product__main_products__main_product__eps_product__product__product__have_associated_product=True) | 
                                #  Q(product__main_products__main_product__eps_product__product__panel_product__have_associated_product=True))
                            ).order_by('-id')
    # .distinct('id')
    
    
    
    context = {
        "title": f"{PROJECT_NAME} | Workstations Consolidated List",
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
        "products_obj": products_obj,
        "workstations": workstations,
        
        # "main_products_obj": main_products_obj,
        "associated_products": associated_products,
        # "main_products_completed": main_products_completed,
    }
    return render(request, "Projects/General/Workstations/workstation_view.html", context)


@login_required(login_url='signin')
def workstation_completed(request, project=None):
    """
    This function retrieves a list of completed workstations for a given project or all projects.
    
    :param request: The HTTP request received by the view function. It contains information about the
    current request, such as the user making the request, the HTTP method used, and any data submitted
    with the request
    :param project: The project parameter is an optional argument that can be passed to the function. It
    is used to filter the Schedule_Product objects based on the project ID. If the project parameter is
    not provided or is set to 'ALL', then all Schedule_Product objects are returned
    :return: a rendered HTML template with a context dictionary containing various objects such as
    shopfloor objects, products objects, workstations, projects objects, and a project parameter.
    """
    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = Shopfloors.objects.get(pk=shopfloor_objs.first().id)
    eps_shopfloors = Eps_ShopFloors.objects.filter(shopfloor=shopfloor_obj)
    workstations = Workstations.objects.all().order_by('id')

    if project and not project == 'ALL':
        products_obj = Schedule_Product.objects.filter(
            Q(product__main_products__main_product__eps_data__in=[eps_shopfloor.eps for eps_shopfloor in eps_shopfloors], shopfloor_status=4)
            & Q(product__product_productworkstation__remaining_quantity=0) 
            & Q(product__main_products__main_product__eps_data__project=int(project))
        ).order_by('-id').distinct('id')
    else:
        products_obj = Schedule_Product.objects.filter(
            Q(product__main_products__main_product__eps_data__in=[eps_shopfloor.eps for eps_shopfloor in eps_shopfloors], shopfloor_status=4) 
            & Q(product__product_productworkstation__remaining_quantity=0) 
        ).order_by('-id').distinct('id')
        
    projects_obj = ProjectsModel.objects.filter(status=1)
    
    # associated_products = Workstation_Associated_Products_Data.objects.filter(
    #                             eps_product_id__eps_data__in=[eps_shopfloor.eps.id for eps_shopfloor in eps_shopfloors], 
    #                             is_completed=True
    #                         ).distinct('product')
    # ass_products = Workstation_Associated_Products_Data.objects.filter(
    #                             eps_product_id__eps_data__in=[eps_shopfloor.eps.id for eps_shopfloor in eps_shopfloors], 
    #                             is_completed=True
    #                         ).distinct('product')
    
    associated_products = Schedule_Product.objects.filter(
                                Q(product__main_products__main_product__eps_data__in=[eps_shopfloor.eps for eps_shopfloor in eps_shopfloors]) &
                                Q(shopfloor_status__in=[4]) & Q(in_workstation=True) &
                                # ~Q(product__product_productworkstation__completed_quantity=F('product__product_productworkstation__received_quantity')) &
                                Q(product__product_productworkstation__remaining_quantity=0) &
                                (Q(product__main_products__main_product__eps_product__product__product__have_associated_product=True) | 
                                 Q(product__main_products__main_product__eps_product__product__panel_product__have_associated_product=True))
                            ).distinct('id')

    context = {
        "title": f"{PROJECT_NAME} | Workstations Consolidated Completed List",
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
        "products_obj": products_obj,
        "workstations": workstations,
        "projects_obj": projects_obj,
        "project": project,
        "associated_products": associated_products,
        
    }
    return render(request, "Projects/General/Workstations/workstation_view.html", context)


@login_required(login_url='signin')
def workstation_projects(request, pk):
    """
    This function retrieves and filters data related to workstations and products for a specific
    shopfloor.
    
    """
    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = Shopfloors.objects.get(pk=pk)

    eps_shopfloors = Eps_ShopFloors.objects.filter(shopfloor=shopfloor_obj)
    workstations = Workstations.objects.all().order_by('id')
    products_obj = Schedule_Product.objects.filter(
        Q(product__main_products__main_product__eps_data__in=[eps_shopfloor.eps for eps_shopfloor in eps_shopfloors], shopfloor_status__in=[2,3,4])
        & ~Q(product__product_productworkstation__completed_quantity=F('product__product_productworkstation__received_quantity'))
    ).order_by('id').distinct('id')

    context = {
        "title": f"{PROJECT_NAME} | Workstations",
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
        "products_obj": products_obj,
        "workstations": workstations,
    }
    return render(request, "Projects/General/Workstations/workstation_view.html", context)


@login_required(login_url='signin')
def workstation_projects_cmpld(request, pk, project=None):
    """
    This function retrieves a list of completed projects for a specific shopfloor and project, if
    specified, and renders them in a view with other related objects.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: The primary key of a specific Shopfloor object
    :param project: The "project" parameter is a variable that can be passed to the function as an
    argument. It is used to filter the Schedule_Product objects based on the project number. If the
    value of "project" is not "ALL", then the function will filter the Schedule_Product objects based on
    the project number
    :return: a rendered HTML template with context variables including shopfloor objects, a specific
    shopfloor object, a list of products, a list of workstations, a list of projects, and a project
    variable.
    """
    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = Shopfloors.objects.get(pk=pk)

    eps_shopfloors = Eps_ShopFloors.objects.filter(shopfloor=shopfloor_obj)
    workstations = Workstations.objects.all().order_by('id')
    if project and not project == "ALL":
        products_obj = Schedule_Product.objects.filter(
            Q(product__main_products__main_product__eps_data__in=[eps_shopfloor.eps for eps_shopfloor in eps_shopfloors], shopfloor_status=4)
            & ~Q(product__product_productworkstation__completed_quantity=0) & Q(product__main_products__main_product__eps_data__project=int(project))
        ).order_by('id').distinct('id')
    else:
        products_obj = Schedule_Product.objects.filter(
            Q(product__main_products__main_product__eps_data__in=[eps_shopfloor.eps for eps_shopfloor in eps_shopfloors], shopfloor_status=4)
            & ~Q(product__product_productworkstation__completed_quantity=0)
        ).order_by('id').distinct('id')

    projects_obj = ProjectsModel.objects.filter(status=1)

    context = {
        "title": f"{PROJECT_NAME} | Workstations",
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
        "products_obj": products_obj,
        "workstations": workstations,
        "projects_obj": projects_obj,
        "project": project,
    }
    return render(request, "Projects/General/Workstations/workstation_view.html", context)


@login_required(login_url='signin')
def workstation_detail_eps_list(request, pk):
    """
    This function retrieves data related to workstations and EPS for a specific project and renders it
    in a template.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: The parameter "pk" is a primary key used to identify a specific project in the database.
    It is used to filter the EPS (Engineering Procurement and Construction) objects related to that
    project
    :return: a rendered HTML template with context variables including title, shopfloor objects,
    shopfloor object, projects, eps data, and eps object.
    """
    eps_obj = Eps_main.objects.filter(eps_scheduld_products__isnull=False, project=pk).distinct()

    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = Shopfloors.objects.get(pk=Eps_ShopFloors.objects.get(eps=eps_obj.last().id).shopfloor.id)
    projects = set([product.product.main_products.main_product.eps_data.project for product in Schedule_Product.objects.all()])

    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)

    context = {
        "title": f"{PROJECT_NAME} | Workstations",
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
        "projects": projects,
        "eps_data": eps_data,
        "eps_obj": eps_obj,
    }
    return render(request, "Projects/General/Workstations/workstation_view.html", context)


@login_required(login_url="signin")
def workstation_details(request, pk):
    """
    This function retrieves and organizes data related to workstations and EPS projects for display in a
    web page.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: pk is a parameter that represents the primary key of an Eps_main object, which is used to
    retrieve details of a specific workstation
    :return: a rendered HTML template with context variables for displaying details of a workstation in
    a project management system.
    """
    eps_item = Eps_main.objects.get(pk=pk)
    eps_obj = Eps_main.objects.filter(eps_scheduld_products__isnull=False, project=eps_item.project.id).distinct()

    products_obj = Schedule_Product.objects.filter(Q(product__main_products__main_product__eps_data=eps_item.id) )

    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(eps=eps_item)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None


    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = Shopfloors.objects.get(pk=Eps_ShopFloors.objects.get(eps=eps_obj.last().id).shopfloor.id)
    projects = set([product.product.main_products.main_product.eps_data.project for product in Schedule_Product.objects.all()])

    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)

    context = {
        "title": f"{PROJECT_NAME} | Workstations",
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
        "projects": projects,
        "eps_data": eps_data,
        "eps_obj": eps_obj,
        "eps_item": eps_item,
        "products_obj": products_obj,
        "shopfloor_eps_data": shopfloor_eps_data,
        "shopfloor_attachments": shopfloor_attachments,
    }
    return render(request, "Projects/General/Workstations/workstation_view.html", context)


@login_required(login_url="signin")
def workstation_product_detail_view(request, pk):
    """
    This function retrieves and organizes various details related to a scheduled product for display on
    a workstation view page.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and any data submitted in the request
    :param pk: The parameter `pk` is a primary key used to retrieve a specific `Schedule_Product` object
    from the database
    :return: a rendered HTML template with context variables.
    """
    scheduled_product = Schedule_Product.objects.get(pk=pk)

    eps_product = Eps_Products.objects.get(pk=scheduled_product.product.main_products.main_product.id)
    product_obj = EstimationMainProduct.objects.get(
        pk=eps_product.eps_product.product.id)
    products_details = Eps_ShopFloor_main_products.objects.filter(
        main_products__main_product=eps_product)
    infill_details = Eps_infill_Details.objects.filter(
        main_product=eps_product)
    product_details = MainProductAluminium.objects.get(
        estimation_product=product_obj)

    attachments = Fabrication_Attachments.objects.filter(
        eps_product=eps_product)

    try:
        pro_infill_details = MainProductGlass.objects.get(
            estimation_product=product_obj, glass_primary=True)
        pro_sec_infill_details = MainProductGlass.objects.filter(
            estimation_product=product_obj, glass_primary=False)
    except Exception as e:
        pro_infill_details = None
        pro_sec_infill_details = None

    eps_item = Eps_main.objects.get(pk=eps_product.eps_data.id)
    eps_obj = Eps_main.objects.filter(eps_scheduld_products__isnull=False, project=eps_item.project.id).distinct()

    products_obj = Schedule_Product.objects.filter(Q(product__main_products__main_product__eps_data=eps_item.id) )

    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(eps=eps_item)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None

    try:
        scedule_details = Schedule_Product.objects.get(product__main_products__main_product=eps_product)
    except Schedule_Product.DoesNotExist:
        scedule_details = None

    shopfloor_objs = Shopfloors.objects.all().order_by('id')
    shopfloor_obj = Shopfloors.objects.get(pk=Eps_ShopFloors.objects.get(eps=eps_obj.last().id).shopfloor.id)
    projects = set([product.product.main_products.main_product.eps_data.project for product in Schedule_Product.objects.all()])

    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)

    context = {
        "title": f"{PROJECT_NAME} | Workstations",
        "shopfloor_objs": shopfloor_objs,
        "shopfloor_obj": shopfloor_obj,
        "projects": projects,
        "eps_data": eps_data,
        "eps_obj": eps_obj,
        "eps_item": eps_item,
        "products_obj": products_obj,
        "eps_product": eps_product,
        "product_obj": product_obj,
        "shopfloor_eps_data": shopfloor_eps_data,
        "shopfloor_attachments": shopfloor_attachments,
        "products_details": products_details,
        "infill_details": infill_details,
        "product_details": product_details,
        "attachments": attachments,
        "pro_infill_details": pro_infill_details,
        "pro_sec_infill_details": pro_sec_infill_details,
        "shopfloor_eps_data": shopfloor_eps_data,
        "shopfloor_attachments": shopfloor_attachments,
        "scedule_details": scedule_details,
        "scheduled_product": scheduled_product,
    }
    return render(request, "Projects/General/Workstations/workstation_view.html", context)


"""
QAQC View
"""


@login_required(login_url='signin')
def general_qaqc_view(request, status=None):
    """
    This function retrieves and displays a list of EPS products with their QAQC status, filtered by
    status if provided.
    
    :param request: The HTTP request received by the server. It contains information about the client's
    request, such as the URL, headers, and any data sent in the request body
    :param status: The "status" parameter is an optional argument that can be passed to the
    "general_qaqc_view" function. If it is provided, the function filters the "eps_products" queryset
    based on the "qaqc_status" field matching the provided status value. If it is not provided, the
    :return: The function `general_qaqc_view` returns a rendered HTML template with a context dictionary
    containing the title of the page, a queryset of `eps_products`, a queryset of `rcvd_products`, a
    queryset of `cmpltd_products`, and the `status` parameter.
    """
    
    if status: 
        # eps_products2 = Eps_Products.objects.filter(pk__in=[product.product.product.main_products.main_product.id for product in Eps_QAQC.objects.all()])
        eps_products2 = Eps_Products.objects.filter(
                                        pk__in=[product.product.product.main_products.main_product.id if product.product else product.panel_product.id for product in Eps_QAQC.objects.all()]
                                    )
        eps_products = eps_products2.filter(qaqc_status=status).order_by('-eps_data__created_date')
        rcvd_products = eps_products2.filter(qaqc_status=1)
        cmpltd_products = eps_products2.filter(qaqc_status=2)
    else:
        eps_products = Eps_Products.objects.filter(
                                        pk__in=[product.product.product.main_products.main_product.id if product.product else product.panel_product.id for product in Eps_QAQC.objects.all()]
                                    ).order_by('-eps_data__created_date')
        # eps_products = Eps_Products.objects.filter(pk__in=[product.product.product.main_products.main_product.id for product in Eps_QAQC.objects.all()]).order_by('eps_data__created_date')
        rcvd_products = eps_products.filter(qaqc_status=1)
        cmpltd_products = eps_products.filter(qaqc_status=2)


    context = {
        "title": f"{PROJECT_NAME} | QAQC Consolidated List.",
        "eps_products": eps_products,
        "rcvd_products": rcvd_products,
        "cmpltd_products": cmpltd_products,
        "status": status,
    }
    return render(request, "Projects/General/QAQC/QAQC_view.html", context)


@login_required(login_url='signin')
def qaqc_detail_eps_list(request, pk):
    """
    This function retrieves EPS data for a project and displays it in a QAQC view.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the HTTP method, headers, and data
    :param pk: pk is a parameter that represents the primary key of a project. It is used to filter the
    Eps_main objects based on the project
    :return: a rendered HTML template with context variables including the title, a set of projects, a
    list of EPS data for each project, and an EPS object filtered by a specific project ID.
    """
    
    eps_obj = Eps_main.objects.filter(project=pk)
    projects = set([product.product.product.main_products.main_product.eps_data.project for product in Eps_QAQC.objects.all()])

    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)
    context = {
        "title": f"{PROJECT_NAME} | QAQC",
        "projects": projects,
        "eps_data": eps_data,
        "eps_obj": eps_obj,
    }
    return render(request, "Projects/General/QAQC/QAQC_view.html", context)


@login_required(login_url="signin")
def qaqc_details(request, pk):
    """
    This function retrieves and organizes data related to quality assurance and quality control for a
    specific project and EPS item.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: pk is a parameter that represents the primary key of an Eps_main object, which is used to
    retrieve a specific instance of the object from the database
    :return: a rendered HTML template with context variables.
    """
    eps_item = Eps_main.objects.get(pk=pk)
    eps_obj = Eps_main.objects.filter(project=eps_item.project.id)
    products_obj = Eps_QAQC.objects.filter(product__product__main_products__main_product__eps_data=eps_item)
    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(eps=eps_item)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None

    projects = set([product.product.product.main_products.main_product.eps_data.project for product in Eps_QAQC.objects.all()])
    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)
    context = {
        "title": f"{PROJECT_NAME} | QAQC",
        "projects": projects,
        "eps_data": eps_data,
        "eps_obj": eps_obj,
        "eps_item": eps_item,
        "products_obj": products_obj,
        "shopfloor_eps_data": shopfloor_eps_data,
        "shopfloor_attachments": shopfloor_attachments,
    }
    return render(request, "Projects/General/QAQC/QAQC_view.html", context)


@login_required(login_url='signin')
def qaqc_product_detail_view(request, pk):
    """
    This function retrieves and displays various details related to a product for quality assurance and
    quality control purposes.
    
    :param request: The HTTP request object. It contains information about the current request, such as
    the user agent, headers, and data submitted in the request
    :param pk: pk is a parameter that represents the primary key of an object in the database. In this
    case, it is used to retrieve a specific Eps_Products object from the database
    :return: a rendered HTML template with context variables.
    """
    
    eps_product = Eps_Products.objects.get(pk=pk)
    product_obj = EstimationMainProduct.objects.get(
        pk=eps_product.eps_product.product.id)

    qaqc_products_details = Workstation_Data.objects.filter(
        eps_product_id=eps_product, product__main_products__main_product=eps_product, is_completed=True)
    qaqc_associated_products = Workstation_Associated_Products_Data.objects.filter(
        eps_product_id=eps_product, product__main_product__main_product=eps_product, is_completed=True)

    products_details = Eps_ShopFloor_main_products.objects.filter(
        main_products__main_product=eps_product)
    infill_details = Eps_Outsource_items.objects.filter(
        infill_product__main_product=eps_product).distinct('infill_product')
    product_details = MainProductAluminium.objects.get(
        estimation_product=product_obj)

    qaqc_infills = QAQC_infill_Products.objects.filter(
        product__infill_product__main_product=eps_product)

    attachments = Fabrication_Attachments.objects.filter(
        eps_product=eps_product)

    try:
        pro_infill_details = MainProductGlass.objects.get(
            estimation_product=product_obj, glass_primary=True)
        pro_sec_infill_details = MainProductGlass.objects.filter(
            estimation_product=product_obj, glass_primary=False)
    except Exception as e:
        pro_infill_details = None
        pro_sec_infill_details = None


    eps_item = Eps_main.objects.get(pk=eps_product.eps_data.id)
    eps_obj = Eps_main.objects.filter(project=eps_item.project.id)
    products_obj = Eps_QAQC.objects.filter(product__product__main_products__main_product__eps_data=eps_item)

    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(eps=eps_item)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None

    projects = set([product.product.product.main_products.main_product.eps_data.project for product in Eps_QAQC.objects.all()])

    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)
    context = {
        "title": f"{PROJECT_NAME} | QAQC",
        "projects": projects,
        "eps_data": eps_data,
        "eps_obj": eps_obj,
        "eps_item": eps_item,
        "eps_product": eps_product,
        "products_obj": products_obj,
        "shopfloor_eps_data": shopfloor_eps_data,
        "shopfloor_attachments": shopfloor_attachments,
        "product_details": product_details,
        "qaqc_products_details": qaqc_products_details,
        "infill_details": infill_details,
        "attachments": attachments,
        "pro_infill_details": pro_infill_details,
        "pro_sec_infill_details": pro_sec_infill_details,
        "qaqc_associated_products": qaqc_associated_products,
        "qaqc_infills": qaqc_infills,
        "product_obj": product_obj,
    }
    return render(request, "Projects/General/QAQC/QAQC_view.html", context)
    


"""
Products For Delivery View
"""


@login_required(login_url='signin')
def general_product_for_delivery_view(request):
    """
    This function retrieves a list of EPS products that are ready for delivery and displays them in a
    consolidated view.
    
    :param request: The HTTP request received by the server from the client
    :return: The function `general_product_for_delivery_view` returns an HTTP response with a rendered
    HTML template `product_for_delivery_view.html` that displays a consolidated list of EPS products for
    delivery. The context of the template includes the title of the page and a queryset of EPS products
    ordered by their creation date.
    """
    subquery = Workstation_Data.objects.filter(
        Q(is_delivered=False) 
        & Q(is_completed=True)
        & ~Q(qaqc_completed_quantity=0.00)
        & Q(is_delivered=False)
    ).distinct('eps_product_id')
    
    subquery2 = Workstation_Associated_Products_Data.objects.filter(
        Q(is_delivered=False) 
        & Q(is_completed=True)
        & ~Q(qaqc_completed_quantity=0.00)
        & Q(is_delivered=False)
    ).distinct('eps_product_id')
    
    eps_product = [product.eps_product_id.id for product in subquery] + [product.eps_product_id.id for product in subquery2]
    
    infill_objs = QAQC_infill_Products.objects.filter(
        ~Q(completed_quantity=0.00) & Q(is_delivered=False) 
    )
    
    eps_data_list = Eps_Products_For_Delivery.objects.filter(
            Q(product__product__main_products__main_product__in=eps_product) | 
            (
                Q(outsourced_product__product__infill_product__main_product__in=[product.product.infill_product.main_product.id for product in infill_objs]) 
                & ~Q(outsourced_product__delivery_remaining_quantity=0.00)
            )
        )
    
    eps_datas = Eps_main.objects.filter(
            Q(pk__in=[product.product.eps.id if product.product else product.outsourced_product.product.infill_product.eps_ref.id  for product in eps_data_list])
        ).order_by('-created_date')
    
        
    context = {
        "title": f'{PROJECT_NAME} | Product Delivery Consolidated List.',
        "eps_datas": eps_datas,
    }
    return render(request, "Projects/General/Product_For_Delivery/product_for_delivery_view.html", context)


@login_required(login_url='signin')
def product_for_delivery_detail_eps_list(request, pk):
    """
    This function retrieves EPS data for a given project and displays it in a view for product delivery.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: pk is a parameter that represents the primary key of a project. It is used to filter the
    Eps_main objects based on the project
    :return: a rendered HTML template with context variables including the title, projects, eps_data,
    and eps_obj.
    """
    eps_obj = Eps_main.objects.filter(project=pk)
    projects = set(
        [product.product.product.main_products.main_product.eps_data.project for product in Eps_Products_For_Delivery.objects.all()])
    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)
    context = {
        "title": f"{PROJECT_NAME} | Product For Delivery",
        "projects": projects,
        "eps_data": eps_data,
        "eps_obj": eps_obj,
    }
    return render(request, "Projects/General/Product_For_Delivery/product_for_delivery_view.html", context)


@login_required(login_url='signin')
def general_product_for_delivery_details(request, pk):
    """
    This function retrieves and organizes data related to products for delivery and renders it in a
    view.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: pk is a parameter that represents the primary key of an Eps_main object, which is used to
    retrieve a specific instance of the object from the database
    :return: a rendered HTML template with context variables.
    """
    eps_item = Eps_main.objects.get(pk=pk)
    eps_obj = Eps_main.objects.filter(project=eps_item.project.id).order_by('created_date')
    products_obj = Eps_Products_For_Delivery.objects.filter(product__product__main_products__main_product__eps_data=eps_item)
    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(eps=eps_item)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_attachments = None

    projects = set([product.product.product.main_products.main_product.eps_data.project for product in Eps_Products_For_Delivery.objects.all()])

    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)
    context = {
        "title": f"{PROJECT_NAME} | Product For Delivery",
        "projects": projects,
        "eps_data": eps_data,
        "eps_obj": eps_obj,
        'eps_item': eps_item,
        'products_obj': products_obj,
        "shopfloor_eps_data": shopfloor_eps_data,
        "shopfloor_attachments": shopfloor_attachments,
    }
    return render(request, "Projects/General/Product_For_Delivery/product_for_delivery_view.html", context)


@login_required(login_url='signin')
def product_for_delivery_product_detail_view(request, pk):
    """
    This function retrieves and organizes various details related to a product for delivery in a
    project.
    
    :param request: The HTTP request object. It contains information about the current request,
    including the user making the request, the HTTP method used, and any data submitted in the request
    :param pk: pk is a parameter that represents the primary key of a specific object in the database.
    In this case, it is used to retrieve a specific Eps_Products object from the database
    :return: a rendered HTML template with context data.
    """
    
    eps_product = Eps_Products.objects.get(pk=pk)
    product_obj = EstimationMainProduct.objects.get(
        pk=eps_product.eps_product.product.id)
    products_details = Eps_Product_Details.objects.filter(
        main_product=eps_product)


    attachments = Fabrication_Attachments.objects.filter(
        eps_product=eps_product)

    qaqc_products_details = Workstation_Data.objects.filter(
        eps_product_id=eps_product, product__main_products__main_product=eps_product, is_qaqc_completed=True)
    qaqc_associated_products = Workstation_Associated_Products_Data.objects.filter(
        eps_product_id=eps_product, product__main_product__main_product=eps_product, is_qaqc_completed=True)

    infill_details = Eps_Outsource_items.objects.filter(
        infill_product__main_product=eps_product).distinct('infill_product')
    product_details = MainProductAluminium.objects.get(
        estimation_product=product_obj)
    products_obj = Eps_ShopFloor_main_products.objects.filter(
        main_products__main_product=eps_product)

    qaqc_infills = QAQC_infill_Products.objects.filter(
        product__infill_product__main_product=eps_product, is_qaqc_completed=True)

    cart_main_product = Delivery_Product_Cart_Main.objects.filter(
        product__eps_product_id__eps_data=eps_product.eps_data)
    cart_associated_product = Delivery_Product_Cart_Associated.objects.filter(
        product__eps_product_id__eps_data=eps_product.eps_data)
    cart_infill_product = Delivery_Product_Cart_infill.objects.filter(
        product__product__infill_product__main_product__eps_data=eps_product.eps_data)


    try:
        pro_infill_details = MainProductGlass.objects.get(
            estimation_product=product_obj, glass_primary=True)
        pro_sec_infill_details = MainProductGlass.objects.filter(
            estimation_product=product_obj, glass_primary=False)
    except Exception as e:
        pro_infill_details = None
        pro_sec_infill_details = None


    eps_item = Eps_main.objects.get(pk=eps_product.eps_data.id)
    eps_obj = Eps_main.objects.filter(project=eps_item.project.id)
    products_obj = Eps_Products_For_Delivery.objects.filter(product__product__main_products__main_product__eps_data=eps_item)
    try:
        shopfloor_eps_data = Eps_ShopFloors.objects.get(eps=eps_item)
        shopfloor_items = Eps_ShopFloor_main_products.objects.filter(main_products__main_product__eps_data=eps_item)
        shopfloor_attachments = ShopFloor_Doc.objects.filter(eps_product=shopfloor_eps_data)
    except Exception:
        shopfloor_eps_data = None
        shopfloor_items = None
        shopfloor_attachments = None

    projects = set(
        [product.product.product.main_products.main_product.eps_data.project for product in Eps_Products_For_Delivery.objects.all()])
    eps_data = []
    seen_projects = []

    for project in projects:
        if project in seen_projects:
            continue
        eps_objs = Eps_main.objects.filter(project=project)

        project_dic = {
            "project": project,
            "eps_count": int(eps_objs.count())
        }

        eps_data.append(project_dic)
        seen_projects.append(project)
    context = {
        "title": f"{PROJECT_NAME} | Product For Delivery",
        "projects": projects,
        "eps_data": eps_data,
        'eps_item': eps_item,
        "eps_obj": eps_obj,
        "product_obj": product_obj,
        "products_details": products_details,
        "infill_details": infill_details,
        "product_details": product_details,
        "attachments": attachments,
        'products_obj': products_obj,
        "shopfloor_eps_data": shopfloor_eps_data,
        "shopfloor_attachments": shopfloor_attachments,
        "pro_infill_details": pro_infill_details,
        "pro_sec_infill_details": pro_sec_infill_details,
        "shopfloor_items": shopfloor_items,
        "eps_product": eps_product,
        "qaqc_products_details": qaqc_products_details,
        "qaqc_associated_products": qaqc_associated_products,
        "qaqc_infills": qaqc_infills,
        "cart_main_product": cart_main_product,
        "cart_associated_product": cart_associated_product,
        "cart_infill_product": cart_infill_product,
    }
    return render(request, "Projects/General/Product_For_Delivery/product_for_delivery_view.html", context)


@login_required(login_url='signin')
def scheduled_deliveries(request):
    delivery_notes = Delivery_Note.objects.filter(driver__isnull=False, vehicle__isnull=False,).order_by('-id')
    
    context = {
        "title": f"{PROJECT_NAME} | Scheduled Delivery Notes",
        "delivery_notes": delivery_notes,
        
    }
    return render(request, "Projects/General/Product_For_Delivery/scheduled_dns.html", context)


@login_required(login_url='signin')
def completed_deliveries(request):
    delivery_notes = Delivery_Note.objects.filter(status=3).order_by('-id')
    
    context = {
        "title": f"{PROJECT_NAME} | Completed Delivery Notes",
        "delivery_notes": delivery_notes,
        
    }
    return render(request, "Projects/General/Product_For_Delivery/completed_deliveries.html", context)
    
    
"""
Delivery View
"""


@login_required(login_url='signin')
def general_delivery_note_view(request):
    """
    This function retrieves all delivery notes and renders them in a template for viewing.
    """
    delivery_notes = Delivery_Note.objects.filter(
        driver__isnull=True,
        vehicle__isnull=True,
        ).order_by('-id')
    context = {
        "title": f"{PROJECT_NAME} | Delivery Notes",
        "delivery_notes": delivery_notes,
        "MEDIA_URL": MEDIA_URL,
    }
    return render(request, "Projects/General/Delivery/delivery_view.html", context)


@login_required(login_url="signin")
def delivery_note_view(request, pk):
    """
    This function renders a delivery note view page with context data.
    """
    delivery_notes = Delivery_Note.objects.filter(driver__isnull=True, vehicle__isnull=True)
    dn_note_obj = Delivery_Note.objects.get(pk=pk)
    estimation = ProjectEstimations.objects.filter(project=dn_note_obj.eps.project.id).first()
    cart_dn_objs = DeliveryNoteCart.objects.filter(
                                        # temp_dn__eps__project=dn_note_obj.eps.project.id, 
                                        # temp_dn__eps=dn_note_obj.eps.id, 
                                        
                                        temp_dn__driver__isnull=True, 
                                        temp_dn__vehicle__isnull=True,
                                        created_by=request.user
                                    )
    
    context = {
        "title": f"{PROJECT_NAME} | Delivery Notes",
        "dn_note_obj": dn_note_obj,
        "delivery_notes": delivery_notes,
        "estimation": estimation,
        "STATIC_URL": f'http://{str(request.get_host())}/{str(STATIC_URL)}',
        "cart_dn_objs": cart_dn_objs,
    }
    return render(request, "Projects/General/Delivery/delivery_view.html", context)
    

def delivery_note_add_cart(request, pk):
    dn_note_obj = Delivery_Note.objects.get(pk=pk)
    
    try:
        cart_dn = DeliveryNoteCart.objects.get(created_by=request.user, temp_dn=dn_note_obj)
    except Exception as e:
        cart_dn = None
    if not cart_dn:
        cart_dn_obj = DeliveryNoteCart(created_by=request.user, temp_dn=dn_note_obj)
        cart_dn_obj.save()
    else:
        messages.error(request, "Already Exist.",)
    
    return redirect('delivery_note_view', pk=dn_note_obj.id)
    

def remove_from_dn_cart(request, pk):
    
    cart_dn_obj = DeliveryNoteCart.objects.get(pk=pk)
    dn_id = cart_dn_obj.temp_dn.id
    cart_dn_obj.delete()
    messages.success(request, "Successfully Removed From Cart")
    
    return redirect('delivery_note_view', pk=dn_id)
    
    
def checkout_dn_cart(request, pk):
    user_obj = User.objects.get(pk=pk)
    cart_dn_objs = DeliveryNoteCart.objects.filter(
                                        # temp_dn__eps__project=dn_note_obj.eps.project.id, 
                                        # temp_dn__eps=dn_note_obj.eps.id, 
                                        temp_dn__driver__isnull=True, 
                                        temp_dn__vehicle__isnull=True,
                                        created_by=user_obj
                                    )
    dn_obj = cart_dn_objs.first()
    form = DeliveryNoteCartCheckoutForm()
    
    if request.method == 'POST':
        for cart_dn_obj in cart_dn_objs:
            form = DeliveryNoteCartCheckoutForm(request.POST)

            if form.is_valid():
                driver = form.cleaned_data['driver']
                vehicle = form.cleaned_data['vehicle']
                dn_item = Delivery_Note.objects.get(pk=cart_dn_obj.temp_dn.id)
                dn_item.driver = driver
                dn_item.vehicle = vehicle
                dn_item.status = 2
                dn_item.save()
                cart_dn_obj.delete()
            else:
                messages.error(request, "Invalid form.",)
                
        return redirect('delivery_note_view', pk=dn_obj.temp_dn.id)
         
    context = {
        "cart_dn_objs": cart_dn_objs,
        "form": form,
        "user_obj": user_obj,
    }   
    return render(request, "Projects/General/Delivery/checkout_dn_cart.html", context)   
            
@login_required(login_url='signin')
def markas_dn_delivered(request, pk, re_path=None):
    dn_obj = Delivery_Note.objects.get(pk=pk)
    dn_obj.status = 3
    dn_obj.save()
    
    return redirect("scheduled_deliveries")
        
@login_required(login_url='signin')
def update_dn_status(request, pk):
    """
    This function updates the status of a delivery note object and redirects to the delivery note view
    page.
    
    :param request: The request object represents the current HTTP request that the user has made to the
    server. It contains information about the user's request, such as the HTTP method used (GET, POST,
    etc.), the URL requested, any data submitted in the request, and more
    :param pk: pk is a parameter that represents the primary key of a Delivery_Note object. It is used
    to retrieve the specific Delivery_Note object from the database and update its status to 2. The
    function then redirects the user to the delivery_note_view page for the updated Delivery_Note object
    :return: a redirect to the 'delivery_note_view' page with the primary key (pk) of the updated
    delivery note object as a parameter.
    """
    dn_note_obj = Delivery_Note.objects.get(pk=pk)
    dn_note_obj.status = 2
    dn_note_obj.save()
    messages.success(request, "Successfully Updated Status.")

    return redirect('delivery_note_view', pk=dn_note_obj.id)


@login_required(login_url='signin')
def print_delivery_note(request, pk):
    """
    This function generates a PDF delivery note and returns it as a downloadable file.
    
    :param request: The HTTP request object that triggered the view function
    :param pk: pk is a parameter that represents the primary key of a Delivery_Note object. It is used
    to retrieve the specific Delivery_Note object from the database
    :return: an HTTP response object containing a PDF file of a delivery note.
    """
    dn_note_obj = Delivery_Note.objects.get(pk=pk)
    estimation = ProjectEstimations.objects.filter(project=dn_note_obj.eps.project.id).first()
    context = {
        "dn_note_obj": dn_note_obj,
        "estimation": estimation,
        'STATIC_URL': f'http://{str(request.get_host())}/{str(STATIC_URL)}',
    }

    cmd_options = {
                'quiet': True, 
                'enable-local-file-access': True, 
                'margin-top': '10mm', 
                'header-spacing': 5,
                'minimum-font-size': 12,
                'page-size': 'A4',
                'encoding': "UTF-8",
                # 'orientation': 'Landscape',
                'print-media-type': True,
                'footer-right': "[page] / [topage]",
                'footer-font-size': 8,
            }
    template = get_template('print_templates/delivery_note_print.html')
    file_name = f'Delivery Note(DN-{str(dn_note_obj.delivery_note_id)}).pdf'
    response = PDFTemplateResponse(
                    request=request, 
                    cmd_options=cmd_options, 
                    show_content_in_browser=False, 
                    template=template, context=context,
                )
    response = HttpResponse(response.rendered_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    return response


@login_required(login_url='signin')
def inspection_list(request, project=None):
    """
    This function generates a list of products for inspection based on the selected project or all
    projects.
    """
    projects = ProjectsModel.objects.filter(status=1)
    products = []
    if project:
        if project != 'All':
            project_obj = ProjectsModel.objects.get(pk=project)
            for delivery_note in Delivery_Note.objects.filter(status=3, eps__project=project_obj, inspection_status__in=[1,2]):
                products.extend(iter(delivery_note.main_product.all()))
        else:
            for delivery_note in Delivery_Note.objects.filter(status=3):
                products.extend(iter(delivery_note.main_product.all()))
    else:
        for delivery_note in Delivery_Note.objects.filter(status=3, inspection_status__in=[1,2]):
            for product in delivery_note.main_product.all():
                qaqc_cmp_products = Workstation_Data.objects.get(
                    pk=product.id, 
                    is_qaqc_completed=True, 
                    )
                products.append(qaqc_cmp_products)

    context = {
        "title": f'{PROJECT_NAME} | Inspecion.',
        "projects": projects,
        "products": products,
        "project": project,
    }
    return render(request, "Projects/General/Inspection/Inspection_view.html", context)


@login_required(login_url='signin')
def completed_inspection_list(request, project=None):
    """
    This function generates a list of products for inspection based on the selected project or all
    projects.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and query parameters
    :param project: This is an optional parameter that can be passed to the function. It represents the
    project for which the inspection list is being generated. If it is not provided or is set to None,
    the function will generate the inspection list for all projects. If it is set to a specific project,
    the function will
    :return: The function `inspection_list` returns an HTTP response with the rendered template
    "Projects/General/Inspection/Inspection_view.html" and a context dictionary containing the title,
    projects, products, and project.
    """
    projects = ProjectsModel.objects.filter(status=1)
    products = []
    if project:
        if project != 'All':
            project_obj = ProjectsModel.objects.get(pk=project)
            for delivery_note in Delivery_Note.objects.filter(status=2, eps__project=project_obj, inspection_status=3):
                for product in delivery_note.main_product.all():
                    products.append(product)
        else:
            for delivery_note in Delivery_Note.objects.filter(status=2):
                for product in delivery_note.main_product.all():
                    products.append(product)
    else:
        for delivery_note in Delivery_Note.objects.filter(status=2, inspection_status=3):
            for product in delivery_note.main_product.all():
                qaqc_cmp_products = Workstation_Data.objects.get(
                    pk=product.id, 
                    is_qaqc_completed=True, 
                    )
                products.append(qaqc_cmp_products)
            
    context = {
        "title": f'{PROJECT_NAME} | Inspecion Completed.',
        "projects": projects,
        "products": products,
        "project": project,
    }
    return render(request, "Projects/General/Inspection/Inspection_view.html", context)


@login_required(login_url='signin')
def update_inspect_qty(request, pk, product):
    """
    This function updates the inspection quantity of a delivery note and changes its inspection status
    based on the new quantity.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: The primary key of a Delivery_Note object
    :param product: The "product" parameter is the primary key (pk) of a "Workstation_Data" object,
    which represents a specific product item being inspected in a delivery note
    :return: an HTTP response, either a redirect to the inspection_view page or a rendered HTML
    template.
    """
    delivery_note = Delivery_Note.objects.get(pk=pk)
    product_item = Workstation_Data.objects.get(pk=product)
    if request.method == 'POST':
        new_quantity = request.POST.get('new_quantity')
        if not new_quantity == '0':
            eps_product = Eps_Products.objects.get(pk=product_item.eps_product_id.id)
            delivery_note.inspect_quantity = float(delivery_note.inspect_quantity)+float(new_quantity)
            
            if float(delivery_note.inspect_quantity) == float(delivery_note.total_quantity):
                delivery_note.inspection_status = 3
                eps_product.inspection_status = 3
            else:
                delivery_note.inspection_status = 2
                eps_product.inspection_status = 2
                
            delivery_note.save()
            eps_product.save()
            
            history = Inspection_History(
                created_by=request.user,
                quantity=float(new_quantity),
                dn_details=delivery_note,
            )
            history.save()
            messages.success(request, "Successfully Updated Inspection Quantity.")
        
        return redirect('inspection_view', pk=product)
    context = {
        "delivery_note": delivery_note,
        "product_item": product
    }
    
    return render(request, "Projects/General/Inspection/inspection_quantity_update.html", context)


@login_required(login_url='signin')
def inspection_history(request, pk):
    """
    This function retrieves inspection history and delivery note details for a given primary key.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the user's session, the requested URL, and any submitted form data
    :param pk: pk is a parameter that represents the primary key of a Delivery_Note object. It is used
    to filter Inspection_History objects that are related to the Delivery_Note object with the given
    primary key. The function returns a rendered HTML template that displays the inspection history of
    the delivery note with the given primary
    :return: The function `inspection_history` returns an HTTP response that renders the
    `inspection_history.html` template with the context containing the `delivery_history` and
    `delivery_note` objects.
    """
    delivery_history = Inspection_History.objects.filter(dn_details=pk)
    delivery_note = Delivery_Note.objects.get(pk=pk)
    context = {
        'delivery_history': delivery_history,
        'delivery_note': delivery_note
    }
    return render(request, "Projects/General/Inspection/inspection_history.html", context)


@login_required(login_url='signin')
# @shared_task(name="generate_pdf_task", timeout=60)
def product_eps_print(request, pk, types=None):
    """
    This function generates a PDF file for printing EPS production details.
    """
    product = Eps_Products.objects.get(pk=pk)
    eps_obj = Eps_main.objects.get(pk=product.eps_data.id)
    products_obj = Eps_Products.objects.filter(eps_data=eps_obj)
    enquiry_data = ProjectEstimations.objects.filter(project=eps_obj.project.id).first()
    product_data = SalesOrderItems.objects.get(pk=product.eps_product.product.id)
    eps_products_details = Eps_Product_Details.objects.filter(main_product=product)
    outsourced_infill = Eps_Outsource_items.objects.filter(infill_product__main_product=product, )
    # accessories_obj = SalesOrderAccessories.objects.filter(product=product_data)
    
    # print("products_obj==>", products_obj)
    
    eps_vision_panel_details = Eps_infill_Details.objects.filter(
        main_product=product, infill__panel_type=1,
        )
    eps_spandrel_panel_details = Eps_infill_Details.objects.filter(
        main_product=product, infill__panel_type=2,
        )
    eps_openable_panel_details = Eps_infill_Details.objects.filter(
        main_product=product, infill__panel_type=3,
        )

    # try:
    #     infill_details = SalesOrderInfill.objects.get(product=product_data, infill_primary=True)
    #     sec_infill_details = SalesOrderInfill.objects.filter(product=product_data, infill_primary=False)
    # except Exception as e:
    #     infill_details = None
    #     sec_infill_details = None

    context = {
        'title': f'{PROJECT_NAME} | Download EPS',
        'products_obj': products_obj,
        'eps_obj': eps_obj,
        'product': product,
        'product_data': product_data,
        # 'product_aluminium': product_aluminium,
        # 'infill_details': infill_details,
        # 'sec_infill_details': sec_infill_details,
        'eps_products_details': eps_products_details,
        
        'eps_vision_panel_details': eps_vision_panel_details,
        'eps_spandrel_panel_details': eps_spandrel_panel_details,
        'eps_openable_panel_details': eps_openable_panel_details,
        
        'outsourced_infill': outsourced_infill,
        # 'accessories_obj': accessories_obj,
        # 'STATIC_URL': f'http://{str(request.get_host())}/{str(STATIC_URL)}altech/hleft.png',
        'STATIC_URL': f'http://{str(request.get_host())}/{str(STATIC_URL)}',
        'MEDIA_URL': f'http://{str(request.get_host())}/{str(MEDIA_URL)}',
        'enquiry_data': enquiry_data,
    }

    cmd_options = {
                'quiet': True, 
                'enable-local-file-access': True, 
                'margin-top': '10mm', 
                'header-spacing': 5,
                'minimum-font-size': 12,
                'page-size': 'A4',
                'encoding': "UTF-8",
                'print-media-type': True,
                'footer-right': "[page] / [topage]",
                'footer-font-size': 8,
            }
    template = get_template('print_templates/EPS_Print_Production.html')
    file_name = f'EPS {str(eps_obj.eps_id)} | {str(product_data.product if product_data.product else product_data.panel_product)}.pdf'
    response = PDFTemplateResponse(
                    request=request, 
                    cmd_options=cmd_options, 
                    show_content_in_browser=False, 
                    template=template, context=context,
                )
    if not types:
        response = HttpResponse(response.rendered_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response
    else:
        return response
        

@login_required(login_url='signin')
def outsource_print(request, pk):
    """
    This function generates a PDF file for an outsource print view using a template and context data.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and query parameters
    :param pk: pk is a parameter that represents the primary key of an object in the database. In this
    case, it is used to retrieve a specific Eps_Outsource_items object from the database
    :return: an HTTP response object containing a PDF file that is generated from a template and context
    data. The PDF file is named "Outsource.pdf" and is set to be downloaded as an attachment.
    """
    outsource_items = Eps_Outsource_items.objects.get(pk=pk)
    eps_obj = Eps_main.objects.get(pk=outsource_items.infill_product.main_product.eps_data.id)
    estimation = ProjectEstimations.objects.filter(project=eps_obj.project.id).first()
    
    context = {
        'title': f'{PROJECT_NAME} | Outsource Print View',
        'eps_obj': eps_obj,
        'outsource_items': outsource_items,
        'estimation': estimation,
        # 'STATIC_URL': f'http://{str(request.get_host())}/{str(STATIC_URL)}',
        # 'MEDIA_URL': f'http://{str(request.get_host())}/{str(MEDIA_URL)}',
        
    }   
    
    cmd_options = {
        'quiet': True, 
        'enable-local-file-access': True, 
        'margin-top': '10mm', 
        'header-spacing': 5,
        'minimum-font-size': 12,
        'page-size': 'A4',
        'encoding': "UTF-8",
        'print-media-type': True,
        'footer-right': "[page] / [topage]",
        'footer-font-size': 8,
    }

    template = get_template('print_templates/Outsource_print.html')
    file_name = 'Outsource.pdf'
    response = PDFTemplateResponse(
                    request=request, 
                    cmd_options=cmd_options, 
                    show_content_in_browser=False, 
                    template=template, context=context,
                )
    response = HttpResponse(response.rendered_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    return response


@login_required
def eps_print(request, pk):
    """
    This function generates a PDF file for printing EPS data and its associated products.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and any data submitted in the request
    :param pk: pk is a parameter that stands for "primary key". It is used to retrieve a specific object
    from the database based on its unique identifier. In this case, it is used to retrieve an EPS object
    with a specific primary key value
    :return: an HTTP response object containing a PDF file as an attachment.
    """
    eps_obj = Eps_main.objects.get(pk=pk)
    products_obj = Eps_Products.objects.filter(eps_data=eps_obj)
    estimation = ProjectEstimations.objects.filter(project=eps_obj.project.id).first()

    context = {
        'title': f'{PROJECT_NAME} | EPS Print ',
        'eps_obj': eps_obj,
        'products_obj': products_obj,
        'estimation': estimation,
        'STATIC_URL': f'http://{str(request.get_host())}/{str(STATIC_URL)}',
        'MEDIA_URL': f'http://{str(request.get_host())}/{str(MEDIA_URL)}',
    }

    cmd_options = {
                'quiet': True, 
                'enable-local-file-access': True, 
                'margin-top': '10mm', 
                'header-spacing': 5,
                'minimum-font-size': 12,
                'page-size': 'A4',
                'encoding': "UTF-8",
                'print-media-type': True,
                'footer-right': "[page] / [topage]",
                'footer-font-size': 8,
            }
    template = get_template('print_templates/EPS_print.html')
    file_name = f'EPS {str(eps_obj.eps_id)}.pdf'
    response = PDFTemplateResponse(
                    request=request, 
                    cmd_options=cmd_options, 
                    show_content_in_browser=False, 
                    template=template, context=context,
                )
    response = HttpResponse(response.rendered_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    return response


@login_required
def workstation_quantity_update(request, pk, types, workstation_id):
    associated_products = None
    
    if types == 1:
        print('A')
        data = Workstation_Data.objects.get(pk=pk)
        if data.eps_product_id.eps_product.product.category.is_curtain_wall:
            associated_products = Workstation_Data.objects.filter(
                    eps_product_id=data.eps_product_id, 
                    workstation=workstation_id, 
                    is_completed=False
                ).order_by('id')
        else:
            associated_products = Workstation_Data.objects.filter(
                    eps_product_id=data.eps_product_id, 
                    workstation=workstation_id, 
                    is_completed=False
                ).order_by('id')
            
        # total_qty = sum(work_product.received_quantity for work_product in Workstation_Data.objects.filter(eps_product_id=data.eps_product_id))
        associated = None
    else:
        print('B')
        data = Workstation_Associated_Products_Data.objects.get(pk=pk)
        # associated_products = Workstation_Data.objects.filter(
        #     eps_product_id=data.eps_product_id, 
        #     workstation=workstation_id, 
        #     is_completed=False
        # ).order_by('id')
        associated_products = Workstation_Associated_Products_Data.objects.filter(
            eps_product_id=data.eps_product_id, 
            workstation=workstation_id, 
            is_completed=False
        ).order_by('id')
        
        associated = True
    
    
    if request.method == 'POST':
        associa_products = request.POST.getlist('associated_product')
        
        
        if types == 1:
            print("Main Product")
            if associated_products.first().product.main_products.main_product.eps_product.product.product:
                first_workstation = associated_products.first().product.main_products.main_product.eps_product.product.product.workshop_product.first()
                final_workstation = associated_products.first().product.main_products.main_product.eps_product.product.product.workshop_product.last()
            else:
                first_workstation = associated_products.first().product.main_products.main_product.eps_product.product.panel_product.workshop_product.first()
                final_workstation = associated_products.first().product.main_products.main_product.eps_product.product.panel_product.workshop_product.last()
                
            
            
            for product_id in associa_products:
                print("product_id==>", product_id)
                print('C')
                product_obj = Eps_Product_Details.objects.get(pk=product_id)
                new_quantity = request.POST.getlist('new_quantity_'+str(product_id))
                hours_input = request.POST.getlist('time_'+str(product_id))
                hours, minutes = map(int, hours_input[0].split(':'))
                time_data = time(hour=int(hours), minute=int(minutes)).strftime('%H:%M')
                quantity = float(new_quantity[0])
                
                work_product = Workstation_Data.objects.get(
                                            product=Eps_ShopFloor_main_products.objects.get(main_products=product_obj), 
                                            workstation=workstation_id, 
                                            is_completed=False
                                        )
                print("QTY==>", quantity)
                if not quantity == 0 or not quantity == float(0):
                    print('E')
                    if work_product.product.main_products.main_product.eps_product.product.product:
                        product_id = work_product.product.main_products.main_product.eps_product.product.product.id
                        final_workstation = work_product.product.main_products.main_product.eps_product.product.product.workshop_product.last()
                    else:
                        product_id = work_product.product.main_products.main_product.eps_product.product.panel_product.id
                        final_workstation = work_product.product.main_products.main_product.eps_product.product.panel_product.workshop_product.last()
                    workstation_datas = workstation_data(
                        pk=product_id,
                        current_workstation=work_product.workstation.id
                    )
                   
                    product = Schedule_Product.objects.get(
                        product__main_products__main_product=work_product.product.main_products.main_product)
                    
                    if float(quantity) <= work_product.remaining_quantity:
                        print('G')
                        history_data = Workstation_History(
                            created_by=request.user, workstation_data=work_product, received_quantity=float(quantity), completion_time=time_data)
                        history_data.save()
                        

                        work_product.completed_quantity = float(
                            work_product.completed_quantity) + float(quantity)
                        work_product.total_completion_time = sum_times([work_product.total_completion_time, str(time_data)], types='workstation')
                        work_product.remaining_quantity = float(work_product.remaining_quantity) - float(quantity)
                        # data.remaining_quantity = float(total_qty) - float(quantity)
                        work_product.save()
                        if workstation_datas['next_workstation']:
                            print('H')
                            try:
                                flag = Workstation_Data.objects.get(eps_product_id=work_product.eps_product_id, prev_product=work_product.id, workstation=workstation_datas['next_workstation'])
                            except Exception as e:
                                flag = None

                            if not flag:
                                print('J')
                                new_data = Workstation_Data(
                                                created_by=work_product.created_by, 
                                                product=work_product.product, 
                                                received_quantity=work_product.completed_quantity, 
                                                remaining_quantity=work_product.completed_quantity, 
                                                completed_quantity=0, 
                                                workstation_id=workstation_datas['next_workstation'], 
                                                prev_product=work_product,
                                                eps_product_id=work_product.eps_product_id,
                                                total_completion_time='00:00',
                                            )
                                new_data.save()
                                
                                
                            else:
                                print('L')
                                flag.received_quantity = float(flag.received_quantity) + float(quantity)
                                # flag.total_completion_time = sum_times([flag.total_completion_time, time_data], types='workstation')
                                flag.remaining_quantity = float(flag.remaining_quantity) + float(quantity)
                                flag.save()
                                
                        else:
                            print('M')
                            if workstation_datas['final_workstation'] == work_product.workstation.id:
                                print('N')
                                try:
                                    flag2 = Workstation_Data.objects.get(eps_product_id=work_product.eps_product_id, is_completed=True, prev_product=work_product.id, workstation=workstation_datas['final_workstation'])
                                except Exception as e:
                                    flag2 = None
                                
                                shopfloor_obj = Eps_ShopFloor_main_products.objects.get(main_products=product_obj)
                                shopfloor_obj.completed_quantity = float(shopfloor_obj.completed_quantity) + float(quantity)
                                shopfloor_obj.remaining_quantity = float(shopfloor_obj.remaining_quantity) - float(quantity)
                                
                                if not flag2:
                                    print('P')
                                    new_data2  = Workstation_Data(
                                                    created_by=work_product.created_by, 
                                                    product=work_product.product, 
                                                    received_quantity=float(work_product.completed_quantity) , 
                                                    remaining_quantity=float(work_product.remaining_quantity), 
                                                    completed_quantity=float(work_product.completed_quantity), 
                                                    qaqc_received_quantity=work_product.completed_quantity,
                                                    qaqc_remaining_quantity=work_product.completed_quantity,
                                                    is_completed=True, 
                                                    prev_product=work_product,
                                                    eps_product_id=work_product.eps_product_id,
                                                    workstation=work_product.workstation,
                                                    total_completion_time=work_product.total_completion_time,
                                            )
                                    new_data2.save()
                                        
                                    
                                        
                                    if new_data2.remaining_quantity <= 0 and not Eps_QAQC.objects.filter(product=product):
                                        print('R')
                                        # new_data2.qaqc_received_quantity += float(quantity)
                                        # new_data2.qaqc_remaining_quantity += float(quantity)
                                        new_data2.save()
                                        
                                        qaqc_data = Eps_QAQC(created_by=request.user, product=product)
                                        qaqc_data.save()
                                        
                                else:
                                    print('S')
                                    
                                    flag2.received_quantity = float(flag2.received_quantity) + float(quantity)
                                    flag2.completed_quantity = float(flag2.completed_quantity) + float(quantity)
                                    flag2.remaining_quantity = float(flag2.received_quantity) - float(flag2.completed_quantity)
                                    # flag2.total_completion_time = sum_times([flag2.total_completion_time, time_data], types='workstation')
                                    flag2.save()
                                    
                                    
                                    if flag2.remaining_quantity == 0 and not Eps_QAQC.objects.filter(product=product):
                                        print('T')
                                        qaqc_data = Eps_QAQC(
                                            created_by=request.user, product=product)
                                        qaqc_data.save()
                                        
                                        shopfloor_obj.status = 3
                                        
                                    else:
                                        print('U')
                                        flag2.qaqc_received_quantity = float(flag2.qaqc_received_quantity) + float(quantity)
                                        flag2.qaqc_remaining_quantity = float(flag2.qaqc_remaining_quantity) + float(quantity)
                                        flag2.save()

                                main_product = Eps_Products.objects.get(pk=work_product.eps_product_id.id)
                                main_product.qaqc_status = 1
                                main_product.save()
                                shopfloor_obj.save()
                                print('LL')
                                print('work_product.eps_product_id==>', work_product.eps_product_id)
                                print('first_workstation.id==>', first_workstation.workstation.id)
                                print('final_workstation.id==>', final_workstation.workstation.id)
                                total_received_quantity = Workstation_Data.objects.filter(
                                                    eps_product_id=work_product.eps_product_id,
                                                    workstation=first_workstation.workstation.id,
                                                ).aggregate(total_received=Sum('received_quantity'))['total_received']
                                # total_received_quantity = Workstation_Data.objects.filter(
                                #                     eps_product_id=work_product.eps_product_id,
                                #                     workstation=first_workstation.id
                                #                 ).aggregate(total_received=Sum('received_quantity'))['total_received']
                                total_completed_quantity = Workstation_Data.objects.filter(
                                                    eps_product_id=work_product.eps_product_id,
                                                    workstation=final_workstation.workstation.id,
                                                    is_completed=True,
                                                ).aggregate(total_completed=Sum('completed_quantity'))['total_completed']
                                
                                print("total_received_quantity==>", total_received_quantity)
                                print("total_completed_quantity==>", total_completed_quantity)
                                
                                if total_received_quantity == total_completed_quantity:
                                    product.shopfloor_status = 4
                                    product.save()
                            else:
                                print('Error in Completing ')
                        messages.success(request, "Successfully Updated Quantity")
                    else:
                        messages.error(request, "Please check the entered quantity.")
                
            
            
            
        else:
            print("Associated")
            if associated_products.first().product.main_product.main_product.eps_product.product.product:
                first_workstation = associated_products.first().product.main_product.main_product.eps_product.product.product.workshop_product.first()
                final_workstation = associated_products.first().product.main_product.main_product.eps_product.product.product.workshop_product.last()
            else:
                first_workstation = associated_products.first().product.main_product.main_product.eps_product.product.panel_product.workshop_product.first()
                final_workstation = associated_products.first().product.main_product.main_product.eps_product.product.panel_product.workshop_product.last()
            
            
            for product_id in associa_products:
                print("product_id==>", product_id)
                print('1C')
                product = Eps_Product_Details.objects.get(pk=product_id)
                new_quantity = request.POST.getlist('new_quantity_'+str(product_id))
                hours_input = request.POST.getlist('time_'+str(product_id))
                hours, minutes = map(int, hours_input[0].split(':'))
                time_data = time(hour=int(hours), minute=int(minutes)).strftime('%H:%M')
                quantity = float(new_quantity[0])
                
                
                work_product = Workstation_Associated_Products_Data.objects.get(
                                            product=Eps_Associated_sub_Products.objects.get(main_product=product_id),
                                            # product=Eps_ShopFloor_main_products.objects.get(main_products=product), 
                                            workstation=workstation_id, 
                                            is_completed=False
                                        )
                    
                
                if not quantity == 0:
                    
                    print('F')
                    if work_product.product.main_product.main_product.eps_product.product.product:
                        product_id = work_product.product.main_product.main_product.eps_product.product.product.id
                    else:
                        product_id = work_product.product.main_product.main_product.eps_product.product.panel_product.id
                    workstation_datas = workstation_data(
                        pk=product_id,
                        current_workstation=work_product.workstation.id
                    )
                    
                    
                    product = Schedule_Product.objects.get(
                        product__main_products__main_product=work_product.product.main_product.main_product)
                    
                    if float(quantity) <= work_product.remaining_quantity:
                        print('G')
                        
                        history_data = Workstation_Associated_Product_History(
                                                created_by=request.user, 
                                                workstation_data=work_product, 
                                                received_quantity=float(quantity), 
                                                completion_time=time_data
                                            )
                        history_data.save()

                        work_product.completed_quantity = float(
                            work_product.completed_quantity) + float(quantity)
                        work_product.total_completion_time = sum_times([work_product.total_completion_time, str(time_data)], types='workstation')
                        work_product.remaining_quantity = float(work_product.remaining_quantity) - float(quantity)
                        # data.remaining_quantity = float(total_qty) - float(quantity)
                        work_product.save()
                        if workstation_datas['next_workstation']:
                            print('H')
                            
                            try:
                                flag = Workstation_Associated_Products_Data.objects.get(eps_product_id=work_product.eps_product_id, prev_product=work_product.id, workstation=workstation_datas['next_workstation'])
                            except Exception as e:
                                flag = None
                            
                            if not flag:
                                
                                print('K')
                                new_data = Workstation_Associated_Products_Data(
                                                created_by=work_product.created_by, 
                                                product=work_product.product, 
                                                received_quantity=work_product.completed_quantity, 
                                                remaining_quantity=work_product.completed_quantity, 
                                                completed_quantity=0, 
                                                workstation_id=workstation_datas['next_workstation'], 
                                                prev_product=work_product,
                                                eps_product_id=work_product.eps_product_id,
                                                total_completion_time='00:00',
                                            )
                                new_data.save()
                                
                            else:
                                print('L')
                                flag.received_quantity = float(flag.received_quantity) + float(quantity)
                                # flag.total_completion_time = sum_times([flag.total_completion_time, time_data], types='workstation')
                                flag.remaining_quantity = float(flag.remaining_quantity) + float(quantity)
                                flag.save()
                                
                        else:
                            print('M')
                            if workstation_datas['final_workstation'] == work_product.workstation.id:
                                print('N')
                                try:
                                    flag2 = Workstation_Associated_Products_Data.objects.get(eps_product_id=work_product.eps_product_id, is_completed=True, prev_product=work_product.id, workstation=workstation_datas['final_workstation'])
                                except Exception:
                                    flag2 = None
                                    
                                
                                
                                if not flag2:
                                    
                                    print('Q')
                                    new_data2  = Workstation_Associated_Products_Data(
                                                created_by=work_product.created_by, 
                                                product=work_product.product, 
                                                received_quantity=float(work_product.received_quantity), 
                                                remaining_quantity=float(work_product.remaining_quantity) , 
                                                completed_quantity=float(work_product.completed_quantity), 
                                                qaqc_received_quantity=work_product.completed_quantity,
                                                qaqc_remaining_quantity=work_product.completed_quantity,
                                                is_completed=True, 
                                                prev_product=work_product,
                                                eps_product_id=work_product.eps_product_id,
                                                workstation=work_product.workstation,
                                                total_completion_time=work_product.total_completion_time,
                                            )
                                    new_data2.save()
                                        
                                    if new_data2.remaining_quantity <= 0 and not Eps_QAQC.objects.filter(product=product):
                                        print('R')
                                        # new_data2.qaqc_received_quantity += float(quantity)
                                        # new_data2.qaqc_remaining_quantity += float(quantity)
                                        new_data2.save()
                                        
                                        qaqc_data = Eps_QAQC(created_by=request.user, product=product)
                                        qaqc_data.save()
                                else:
                                    shopfloor_obj = Eps_ShopFloor_associated_products.objects.get(main_products=flag2)
                                    shopfloor_obj.completed_quantity = float(shopfloor_obj.completed_quantity) + float(quantity)
                                    shopfloor_obj.remaining_quantity = float(shopfloor_obj.remaining_quantity) - float(quantity)
                                    
                                    print('S')
                                    flag2.received_quantity = float(flag2.received_quantity) + float(quantity)
                                    flag2.completed_quantity = float(flag2.completed_quantity) + float(quantity)
                                    flag2.remaining_quantity = float(flag2.received_quantity) - float(flag2.completed_quantity)
                                    # flag2.total_completion_time = sum_times([flag2.total_completion_time, time_data], types='workstation')
                                    flag2.save()
                                    
                                    if flag2.remaining_quantity == 0 and not Eps_QAQC.objects.filter(product=product):
                                        print('T')
                                        qaqc_data = Eps_QAQC(
                                            created_by=request.user, product=product)
                                        qaqc_data.save()
                                        shopfloor_obj.status = 3
                                    else:
                                        print('U')
                                        flag2.qaqc_received_quantity = float(flag2.qaqc_received_quantity) + float(quantity)
                                        flag2.qaqc_remaining_quantity = float(flag2.qaqc_remaining_quantity) + float(quantity)
                                        flag2.save()

                                    shopfloor_obj.save()
                                    
                                main_product = Eps_Products.objects.get(pk=work_product.eps_product_id.id)
                                main_product.qaqc_status = 1
                                main_product.save()
                                
                                
                                print('LL')
                                print('work_product.eps_product_id==>', work_product.eps_product_id)
                                print('first_workstation.id==>', first_workstation.workstation.id)
                                print('final_workstation.id==>', final_workstation.workstation.id)
                                
                                total_received_quantity = Workstation_Data.objects.filter(
                                                    eps_product_id=work_product.eps_product_id,
                                                    workstation=first_workstation.workstation.id,
                                                ).aggregate(total_received=Sum('received_quantity'))['total_received']
                                # total_received_quantity = Workstation_Data.objects.filter(
                                #                     eps_product_id=work_product.eps_product_id,
                                #                     workstation=first_workstation.id
                                #                 ).aggregate(total_received=Sum('received_quantity'))['total_received']
                                total_completed_quantity = Workstation_Data.objects.filter(
                                                    eps_product_id=work_product.eps_product_id,
                                                    workstation=final_workstation.workstation.id,
                                                    is_completed=True,
                                                ).aggregate(total_completed=Sum('completed_quantity'))['total_completed']
                                
                                print("total_received_quantity==>", total_received_quantity)
                                print("total_completed_quantity==>", total_completed_quantity)
                                
                                if total_received_quantity == total_completed_quantity:
                                    product.shopfloor_status = 4
                                    product.save()
                            else:
                                print('Error in Completing ')
                        messages.success(request, "Successfully Updated Quantity")
                    else:
                        messages.error(request, "Please check the entered quantity.")
                
            
        
        return redirect('general_workstation_view')
    
    context = {
        'product': data,
        'types': types,
        'associated_products': associated_products,
        'workstation': workstation_id,
    }
    return render(request, "Projects/General/Workstations/quantity_update_form.html", context)


@login_required
def workstation_time_data(request, pk, eps_id, p_type):
    if p_type == 'main':
        products = Workstation_Data.objects.filter(
            Q(eps_product_id=pk, eps_product_id__eps_data=eps_id)
            # Q(eps_product_id__eps_product__product=pk, eps_product_id__eps_data=eps_id)
        ).order_by('id')
        product = products.exclude(is_completed=True)
    elif p_type == 'associated':
        products = Workstation_Associated_Products_Data.objects.filter(
            # eps_product_id__eps_product__product=pk, 
            eps_product_id=pk, 
            eps_product_id__eps_data=eps_id,
        ).order_by('id')
        product = products.exclude(is_completed=True)
    else:
        product = None
        completed_flag = None
        
    for product_data in product:
        if product_data.remaining_quantity == 0:
            completed_flag = True
        else:
            completed_flag = None
    try:
        completed_product = products.get(is_completed=True)
    except Exception:
        completed_product = None 
        
    # if request.method == 'POST':
    #     time_data = request.POST.get('time')
    #     hours, minutes = map(int, time_data.split(':'))
    #     time_data = time(hour=int(hours), minute=int(minutes)).strftime('%H:%M')
    #     if completed_product:
    #         completed_product.total_completion_time = time_data
    #         completed_product.save()
        
    #     return redirect('general_workstation_view')
        
    context = {
        "product_objs": product,
        "pk": pk,
        "eps_id": eps_id,
        "p_type": p_type,
        "completed_flag": completed_flag,
        "completed_product": completed_product,
    }
    return render(request, "Projects/General/Workstations/workstation_timesheet.html", context)


@login_required(login_url='signin')
def get_sales_specification_by_category(request, pk, project):
    sales_specifications = SalesOrderSpecification.objects.filter(categories=pk, project=project)
    context = {
        "data_obj": sales_specifications,
    }
    return render(request, 'Enquiries/dropdowns/specification_identifier_dropdown.html', context)


@login_required(login_url='signin')
def get_data_from_sales_spec(request, pk):
    specifications = SalesOrderSpecification.objects.get(pk=pk)
    data = {
        "product": specifications.aluminium_products.id if specifications.aluminium_products else None,
        "brand": specifications.aluminium_system.id if specifications.aluminium_system else None,
        "series": specifications.aluminium_series.id if specifications.aluminium_series else None,
        "surface_finish": specifications.surface_finish.id if specifications.surface_finish else None,
        
        "panel_brand": specifications.panel_brand.id if specifications.panel_brand else None,
        "panel_series": specifications.panel_series.id if specifications.panel_series else None,
        "panel_specification": specifications.panel_specification.id if specifications.panel_specification else None,
        "panel_product": specifications.panel_product.id if specifications.panel_product else None,
    }
    return JsonResponse({'data': data})
    

@login_required(login_url='signin')
def elevation_assign(request, pk):
    projec_obj = ProjectsModel.objects.get(pk=pk)
    project_estimation_obj = ProjectEstimations.objects.filter(project=projec_obj)
    sales_groups = SalesOrderGroups.objects.filter(project=projec_obj, 
                                                #    salesorder_group__building__isnull=True, 
                                                #    salesorder_group__elevation__isnull=True, 
                                                #    salesorder_group__floor__isnull=True
                                                )
    
    building_objs = EPSBuildingsModel.objects.filter(project=projec_obj)
    elevations_objs = ElevationModel.objects.filter(building__project=projec_obj)
    floor_objs = FloorModel.objects.filter(elevation__building__project=projec_obj)
    
    if request.method == 'POST':
        assign_building = request.POST.get('assign_building')
        assign_elevation = request.POST.get('assign_elevation')
        assign_floor = request.POST.get('assign_floor')
        try:
            building_obj = building_objs.get(pk=assign_building)
        except:
            building_obj = None
        
        try:
            elevations_obj = ElevationModel.objects.get(pk=assign_elevation)
        except:
            elevations_obj = None
        
        try:
            floor_obj = FloorModel.objects.get(pk=assign_floor)
        except:
            floor_obj = None
        
        products_lists = request.POST.getlist('products_list')
        
        
        for product in products_lists:
            product_obj = SalesOrderItems.objects.get(pk=product)
            if building_obj:
                product_obj.building = building_obj
            if elevations_obj:
                product_obj.elevation = elevations_obj
            if floor_obj:
                product_obj.floor = floor_obj
            product_obj.save()
            messages.success(request, "Successfully Added Building/Elevations/Floor Details")
        
                
        return redirect('project_scop', pk=projec_obj.id)
        
    context = {
        "project": projec_obj,
        "project_estimation_obj": project_estimation_obj,
        "building_objs": building_objs,
        "sales_groups": sales_groups,
        "floor_objs": floor_objs,
        "elevations_objs": elevations_objs,
        
    }
    return render(request, "Projects/utils/elevation_assign.html", context)


@login_required(login_url='signin')
def get_elevations_list(request, pk):
    elevations_objs = ElevationModel.objects.filter(building=pk)

    context = {
        "elevations_objs": elevations_objs,
    }
    return render(request, "Projects/utils/elevations_dropdown.html", context)

@login_required(login_url='signin')
def get_floor_list(request, pk):
    floor_objs = FloorModel.objects.filter(elevation=pk)
    context = {
        "floor_objs": floor_objs,
    }
    return render(request, "Projects/utils/floor_dropdown.html", context)


@login_required(login_url='signin')
def assign_eps_uoms(request, pk):
    
    projec_obj = ProjectsModel.objects.get(pk=pk)
    project_estimation_obj = ProjectEstimations.objects.filter(project=projec_obj)
    sales_groups = SalesOrderGroups.objects.filter(project=projec_obj)
    categorys = [item.category.id for item in SalesOrderItems.objects.filter(specification_Identifier__project=projec_obj)]
    category_objs = Category.objects.filter(pk__in=categorys)
    
    
    if request.method == 'POST':
        # category_filter = request.POST.get('category_filter')
        eps_uom = request.POST.get('eps_uom')
        products_list = request.POST.getlist('products_list')
        
        for product in products_list:
            product_obj = SalesOrderItems.objects.get(pk=int(product))
            product_obj.eps_uom = eps_uom
            product_obj.save()
            messages.success(request, "Successfully Assigned EPS UoM")
            
        return redirect('project_scop', pk=projec_obj.id)
    
    context = {
        "projec_obj": projec_obj,
        "project_estimation_obj": project_estimation_obj,
        "sales_groups": sales_groups,
        "category_objs": category_objs,
    }
    return render(request, "Projects/utils/eps_uom_assign.html", context)



@login_required(login_url='signin')
def category_wise_filter(request, project, pk=None):
    
    
    projec_obj = ProjectsModel.objects.get(pk=project)
    if pk:
        category_obj = Category.objects.get(pk=pk)
        project_estimation_obj = ProjectEstimations.objects.filter(project=projec_obj)
        sales_groups = SalesOrderGroups.objects.filter(salesorder_group__category=pk, project=projec_obj).distinct('id')
        
    else:
        category_obj = None
        project_estimation_obj = ProjectEstimations.objects.filter(project=projec_obj)
        sales_groups = SalesOrderGroups.objects.filter(project=projec_obj)
    
        
    context = {
        "projec_obj": projec_obj,
        "project_estimation_obj": project_estimation_obj,
        "sales_groups": sales_groups,
        "category_obj": category_obj,
    }
    
    return render(request, "Projects/utils/category_filter_lists.html", context)


@login_required(login_url='signin')
def specificationApprovalFileUpload(request, pk):
    
    spec_obj = SalesOrderSpecification.objects.get(pk=pk)
    form = ApprovalSpecFile(instance=spec_obj)
    if request.method == 'POST':
        form = ApprovalSpecFile(request.POST, request.FILES, instance=spec_obj)
        if form.is_valid():
            uploaded_files = request.FILES.getlist('approval_file')
            # handle_uploaded_file(file)
            # print("uploaded_files==>", uploaded_files)
            for file in uploaded_files:
                approve_file_obj = ApprovalSpecFiles(
                    specification=spec_obj,
                    approval_file=file,
                    approval_name=file.name,
                )
                approve_file_obj.save()
            # form.save()
           
            messages.success(request, "Successfully Uploaded File")
        else:
            messages.error(request, form.errors)
        return redirect('salesItem_specifications', pk=spec_obj.project.id)

    context = {
        "spec_obj": spec_obj,
        "form": form,
    }
    return render(request, "Projects/utils/approval_spec_file_upload.html", context)
            

# def completed_deliveries(request):
#     completed_dn_objs = Delivery_Note.objects.filter(
#         driver__isnull=False,
#         vehicle__isnull=False,
#     )
    
    



