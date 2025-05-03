import io, re, math, os
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.db.models import Sum, F, Func
from django.shortcuts import render, redirect
from apps.addon_master.models import Addons
from apps.companies.models import Companies
from apps.enquiries.templatetags import quotation_product_data
from apps.estimations.templatetags import assocciated_data
from apps.estimations.templatetags.aluminium_data import display_product_name
from apps.functions import category_summary_data_excel, merge_summary_count, merge_summary_count2

from celery import shared_task
from apps.Categories.models import Category
from apps.enquiries.models import (
    Enquiries, 
    EnquirySpecifications, 
    Estimations, 
    Temp_Estimations, 
    Temp_EnquirySpecifications,
)

from apps.estimations.models import (
    EstimationBuildings, 
    EstimationMainProduct,
    MainProductAddonCost,
    MainProductAluminium,
    MainProductGlass,
    MainProductSilicon,
    PricingOption,
    Quotations, 
    Temp_EstimationBuildings, 
    Temp_EstimationMainProduct,
    Temp_MainProductAddonCost,
    Temp_MainProductAluminium,
    Temp_MainProductGlass,
    Temp_MainProductSilicon,
    Temp_PricingOption,
    Temp_Quotations,
)
from apps.helper import enquiry_logger
from apps.suppliers.models import BillofQuantity

from xlsxwriter.workbook import Workbook
from wkhtmltopdf.views import PDFTemplateResponse
import urllib.parse
from apps.profiles.models import (
            Profiles,
)

from apps.profile_types.models import Profile_Types
from apps.panels_and_others.models import (
                PanelMasterConfiguration,
)

from amoeba.local_settings import STATIC_URL, STATICFILES_DIRS
from amoeba.settings import MEDIA_URL, PROJECT_NAME


@shared_task(name="aluminium_data_export_shared", time_limit=600)
def aluminium_data_export_shared(request, type):
    
    output = io.BytesIO()
    workbook = Workbook(output)
    worksheet = workbook.add_worksheet()
    profile_data = Profiles.objects.all().order_by(
        'profile_master_series__profile_master_type__profile_master_category',
        'profile_master_series__profile_master_type__profile_master_brand',
        'profile_master_series__profile_master_series',
    )
    if type == 'xlsx':
        header = ['Category', 'System', 'Type', 'Series', 'Profile']
        for i, head in enumerate(header):
            worksheet.write(1, i, head, workbook.add_format({'bold': True}))

        for i, profile_item in enumerate(profile_data):
            worksheet.write(i+2, 0, profile_item.profile_master_series.profile_master_type.profile_master_category.category)
            worksheet.write(i+2, 1, profile_item.profile_master_series.profile_master_type.profile_master_brand.brands.brand_name)
            worksheet.write(i+2, 2, profile_item.profile_master_series.profile_master_type.profile_master_type.profile_type)
            worksheet.write(i+2, 3, profile_item.profile_master_series.profile_master_series)
            worksheet.write(i+2, 4, f'{str(profile_item.profile_code)} | {str(profile_item.profile_master_part)} | Weight/Lm: {str(profile_item.weight_per_lm)} | Thickness: {str(profile_item.thickness)}')

        workbook.close()
        output.seek(0)
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=Panel_Details.xlsx'
        return response

    elif type == 'pdf':
        profile_data = Profile_Types.objects.all()
        company_obj = Companies.objects.all().first()
        context = {
            "profiles": profile_data,
            "STATIC_URL": f'http://{str(request.get_host())}/{str(STATIC_URL)}',
            "MEDIA_URL": f'http://{str(request.get_host())}{str(MEDIA_URL)}',
            "full_static_url" : f'{request.scheme}://{request.get_host()}/{STATIC_URL}',
            "company_obj": company_obj,
        }
        cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '10mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 16,
                    'page-size': 'A4',
                    'orientation': 'Landscape',
                    'encoding': "UTF-8",
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,
                }
        file_name = "Aluminium Reference.pdf"
        template = get_template('print_templates/aluminium_reference.html')
        response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=False, \
                    template=template, context=context)
        response = HttpResponse(response.rendered_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={file_name}'

        return response
    
    
@shared_task(time_limit=600)
def infill_reference_export_shared(request, type):
    output = io.BytesIO()
    workbook = Workbook(output)
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format({'bold': True, 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'fg_color': '#485699'})
    main_total = 0
    glass_data = PanelMasterConfiguration.objects.filter(panel_specification__series__brands__panel_category__is_glass=True)\
        .order_by('-panel_specification__series__brands')
    if type == 'xlsx':
        header = ['Brand', 'Series', 'Specification', 'U value', 'Shading Co.', 'Base Price', 'Markup', 'Quoted Rate']
        for i, head in enumerate(header):
            worksheet.write(1, i, head, workbook.add_format({'bold': True}))
        for i, glass in enumerate(glass_data):
            worksheet.write(i+2, 0, glass.panel_specification.series.brands.panel_brands.brands.brand_name)
            worksheet.write(i+2, 1, glass.panel_specification.series.series)
            worksheet.write(i+2, 2, glass.panel_specification.specifications)
            worksheet.write(i+2, 3, glass.u_value)
            worksheet.write(i+2, 4, glass.shading_coefficient)
            worksheet.write(i+2, 5, glass.price_per_sqm)
            worksheet.write(i+2, 6, glass.markup_percentage)
            worksheet.write(i+2, 7, glass.panel_quoted_rate)

        workbook.close()
        output.seek(0)
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=Panel_Details.xlsx'
        return response

    elif type == 'pdf':
        glass_datas = PanelMasterConfiguration.objects.filter(
                        panel_specification__series__brands__panel_category__is_glass=True)\
                    .distinct('panel_specification__series__brands')
        company_obj = Companies.objects.all().first()
        context = {
            "glass_data": glass_datas,
            "STATIC_URL": f'http://{str(request.get_host())}/{str(STATIC_URL)}',
            "MEDIA_URL": f'http://{str(request.get_host())}{str(MEDIA_URL)}',
            "company_obj": company_obj,
        }
        cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '10mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 16,
                    'page-size': 'A4',
                    'javascript-delay':  500,
                    'orientation': 'Landscape',
                    'encoding': "UTF-8",
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,
                }
        file_name = "Galss Reference.pdf"
        template = get_template('print_templates/glass_reference_print.html')
        response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=False, \
                    template=template, context=context)
        response = HttpResponse(response.rendered_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={file_name}'

        return response 
    
    
@shared_task(time_limit=600)
def consolidate_scope_summary_print_shared(request, pk, detailed, temp):
    if temp:
        EstimationsModel = Temp_Estimations
        EstimationMainProductModel = Temp_EstimationMainProduct
        EnquirySpecificationsModel = Temp_EnquirySpecifications
        EstimationBuildingsModel = Temp_EstimationBuildings
        MainProductAddonCostModel = Temp_MainProductAddonCost
    else:
        EstimationsModel = Estimations
        EstimationMainProductModel = EstimationMainProduct
        EnquirySpecificationsModel = EnquirySpecifications
        EstimationBuildingsModel = EstimationBuildings
        MainProductAddonCostModel = MainProductAddonCost
        
        
    estimation = EstimationsModel.objects.get(pk=pk)
    enquiry_obj = Enquiries.objects.get(pk=estimation.enquiry.id)
    categories_obj = Category.objects.filter(
        pk__in=[category.category.id for category in EstimationMainProductModel.objects.filter(building__estimation=estimation)])

    buildings = EstimationBuildingsModel.objects.filter(estimation=estimation.id)
    specifications = EnquirySpecificationsModel.objects.filter(estimation=estimation.id)
    
    addons_datas = MainProductAddonCostModel.objects.filter(estimation_product__building__estimation=estimation)\
        .values('estimation_product__category__category', 'addons__addon').annotate(
                    total_addon_quantity=Sum('addon_quantity')
                )
    
    
    
    if detailed == 1:
        context = {
            "estimation": estimation,
            "enquiry_obj": enquiry_obj,
            "categories_obj": categories_obj,
            "buildings": buildings,
            "version": estimation,
            "specifications": specifications,
            "addons_datas": addons_datas,
        }
        
    elif detailed == 0:
        context = {
            "estimation": estimation,
            "enquiry_obj": enquiry_obj,
            "categories_obj": categories_obj,
        }
    

    cmd_options = {
            'quiet': True,
            'enable-local-file-access': True,
            'margin-top': '10mm',
            'header-spacing': 5,

            'orientation': 'Landscape',
            'minimum-font-size': 14,
            'page-size': 'A3',
            'encoding': "UTF-8",
            'print-media-type': True,
            'footer-right': "[page] / [topage]",
            'footer-font-size': 8,
    }
    template = get_template('print_templates/scope_summary/consloidate_scope_summary_print.html')

    file_names = (
        (
            (
                "Consolidated Scope Summary "
                + str(
                    [
                        'Original'
                        if estimation.version.version == '0'
                        else f'Revision {str(estimation.version.version)}'
                    ][0]
                )
            )
            + " in "
        )
        + str(estimation.enquiry.title)
        + '.pdf'
    )
    clean_string  = re.sub(r'[^\w\s\-\.]', '', file_names)
    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True,
                                    template=template, context=context)
    response = HttpResponse(response.rendered_content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename='+clean_string
    return response
    
    
@shared_task(time_limit=600)
def building_scope_summary_print_shared(request, pk, temp=None):
    if temp:
        EstimationsModel = Temp_Estimations
        EstimationMainProductModel = Temp_EstimationMainProduct
        EnquirySpecificationsModel = Temp_EnquirySpecifications
        EstimationBuildingsModel = Temp_EstimationBuildings
    else:
        EstimationsModel = Estimations
        EstimationMainProductModel = EstimationMainProduct
        EnquirySpecificationsModel = EnquirySpecifications
        EstimationBuildingsModel = EstimationBuildings

    estimation = EstimationsModel.objects.get(pk=pk)
    enquiry_obj = Enquiries.objects.get(pk=estimation.enquiry.id)
    categories_obj = Category.objects.filter(
        pk__in=[category.category.id for category in EstimationMainProductModel.objects.filter(building__estimation=estimation)])
    buildings = EstimationBuildingsModel.objects.filter(estimation=estimation.id)

    context = {
        "estimation": estimation,
        "enquiry_obj": enquiry_obj,
        "categories_obj": categories_obj,
        "buildings": buildings,
        "version": estimation,
    }
    cmd_options = {
            'quiet': True,
            'enable-local-file-access': True,
            'margin-top': '10mm',
            'header-spacing': 5,

            'orientation': 'Landscape',
            'minimum-font-size': 14,
            'page-size': 'A3',
            'encoding': "UTF-8",
            'print-media-type': True,
            'footer-right': "[page] / [topage]",
            'footer-font-size': 8,
    }
    template = get_template('print_templates/scope_summary/building_wise_summary_print.html')

    file_names = (
        (
            (
                "Building Scope Summary "
                + str(
                    [
                        'Original'
                        if estimation.version.version == '0'
                        else f'Revision {str(estimation.version.version)}'
                    ][0]
                )
            )
            + " in "
        )
        + str(estimation.enquiry.title)
        + '.pdf'
    )
    clean_string  = re.sub(r'[^\w\s\-\.]', '', file_names)
    response = PDFTemplateResponse(
                                        request=request, 
                                        cmd_options=cmd_options, 
                                        show_content_in_browser=True,
                                        template=template, 
                                        context=context
                                )
    response = HttpResponse(response.rendered_content, content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename='+clean_string
    return response
    
    
@shared_task(time_limit=600)
def specification_scope_summary_print_shared(request, pk, temp=None):
    if temp:
        EstimationsModel = Temp_Estimations
        EstimationMainProductModel = Temp_EstimationMainProduct
        EnquirySpecificationsModel = Temp_EnquirySpecifications
        EstimationBuildingsModel = Temp_EstimationBuildings
    else:
        EstimationsModel = Estimations
        EstimationMainProductModel = EstimationMainProduct
        EnquirySpecificationsModel = EnquirySpecifications
        EstimationBuildingsModel = EstimationBuildings


    estimation = EstimationsModel.objects.get(pk=pk)
    enquiry_obj = Enquiries.objects.get(pk=estimation.enquiry.id)
    categories_obj = Category.objects.filter(
        pk__in=[category.category.id for category in EstimationMainProductModel.objects.filter(building__estimation=estimation)])
    specifications = EnquirySpecificationsModel.objects.filter(estimation=estimation.id)

    context = {
        "estimation": estimation,
        "enquiry_obj": enquiry_obj,
        "categories_obj": categories_obj,
        "specifications": specifications,
    }

    cmd_options = {
            'quiet': True,
            'enable-local-file-access': True,
            'margin-top': '10mm',
            'header-spacing': 5,

            'orientation': 'Landscape',
            'minimum-font-size': 14,
            'page-size': 'A3',
            'encoding': "UTF-8",
            'print-media-type': True,
            'footer-right': "[page] / [topage]",
            'footer-font-size': 8,
    }
    template = get_template('print_templates/scope_summary/specification_wise_scope_summary_print.html')

    file_names = (
        (
            (
                "Specification wise Scope Summary "
                + str(
                    [
                        'Original'
                        if estimation.version.version == '0'
                        else f'Revision {str(estimation.version.version)}'
                    ][0]
                )
            )
            + " in "
        )
        + str(estimation.enquiry.title)
        + '.pdf'
    )
    clean_string  = re.sub(r'[^\w\s\-\.]', '', file_names)
    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True,
                                    template=template, context=context)
    response = HttpResponse(response.rendered_content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename='+clean_string
    return response
 
    
@shared_task(time_limit=600)
def building_price_print_shared(request, version, type, temp=None):

    if temp:
        EstimationsModel = Temp_Estimations
        EstimationBuildingsModel = Temp_EstimationBuildings
    else:
        EstimationsModel = Estimations
        EstimationBuildingsModel = EstimationBuildings
    estimation = EstimationsModel.objects.get(pk=version)
    
    if type == 'building':
        buildings = EstimationBuildingsModel.objects.filter(estimation=version)
        filter_by_boq = None
        boqs = None
    elif type == 'boq':
        filter_by_boq = True
        boqs = BillofQuantity.objects.filter(enquiry=estimation.enquiry)
        buildings = None
    else:
        print('Pass')

    context = {
        "estimation": estimation,
        "boq_obj": boqs,
        "version": estimation,
        "filter_by_boq": filter_by_boq,
        "buildings": buildings,
        "STATIC_URL": f'http://{str(request.get_host())}/{str(STATIC_URL)}',
        "MEDIA_URL": f'http://{str(request.get_host())}{str(MEDIA_URL)}',
    }
    
    cmd_options = {
                'quiet': True, 
                'enable-local-file-access': True, 
                'margin-top': '10mm', 
                'header-spacing': 5,
                # 'javascript-delay': 5000,
                # 'debug-javascript': True,
                'orientation': 'Landscape',
                'minimum-font-size': 16,
                'page-size': 'A4',
                'encoding': "UTF-8",
                'print-media-type': True,
                'footer-right': "[page] / [topage]",
                'footer-font-size': 8,
            }
    template = get_template('print_templates/scope_building_price_print.html')
    
    file_name = (
        "Scope of  "
        + str(
            [
                'Original'
                if estimation.version.version == '0'
                else f'Revision {str(estimation.version.version)}'
            ][0]
        )
        + " in "
        + str(estimation.enquiry.title)
        + ' By Building.pdf'
    )

    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, \
        template=template, context=context)
    clean_string  = re.sub(r'[^\w\s\-\.]', '', file_name)
    response = HttpResponse(response.rendered_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={clean_string}'
    return response
    
    
@shared_task()
def export_csv_estimation_socpe_shared(request, version, type, temp=None):
    if temp:
        EstimationsModel = Temp_Estimations
        EstimationMainProductModel = Temp_EstimationMainProduct
        EnquirySpecificationsModel = Temp_EnquirySpecifications
        EstimationBuildingsModel = Temp_EstimationBuildings
        MainProductAluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        MainProductSiliconModel = Temp_MainProductSilicon
        MainProductAddonCostModel = Temp_MainProductAddonCost
        PricingOptionModel = Temp_PricingOption
        QuotationsModel = Temp_Quotations
    else:
        EstimationsModel = Estimations
        EstimationMainProductModel = EstimationMainProduct
        EnquirySpecificationsModel = EnquirySpecifications
        EstimationBuildingsModel = EstimationBuildings
        MainProductAluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
        MainProductSiliconModel = MainProductSilicon
        MainProductAddonCostModel = MainProductAddonCost
        PricingOptionModel = PricingOption
        QuotationsModel = Quotations
    
    if type == 'xlsx':
        buildings = EstimationBuildingsModel.objects.filter(estimation=version).order_by('id')
        estimation = EstimationsModel.objects.get(pk=version)
        csv_file_name = str(estimation.enquiry)
        output = io.BytesIO()
        header = ['Product', 'Dimension', 'Area Per Unit', 'Quantity',
                'Total Area per Unit', 'Rate per Unit', 'Rate per Meter', 'Total Price']
        workbook = Workbook(output)
        worksheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'bold': True, 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'fg_color': '#485699'})
        # sheet = workbook.active
        for p, head in enumerate(header):
            worksheet.write(0, p, head, workbook.add_format({'bold': True}))
        header_title = 2
        footer_row = 0
        for j, building in enumerate(buildings):
            index = 0
            building_total_price = 0
            main_product = EstimationMainProductModel.objects.filter(
                building=building).order_by('product_index')
            mergerange = 'A'+str(j+header_title-footer_row) + \
                ':'+'H'+str(j+header_title-footer_row)
            worksheet.merge_range(
                mergerange, building.building_name, cell_format)
            for i, products in enumerate(main_product):
                
                building_name = building.building_name
                aluminium_obj = MainProductAluminiumModel.objects.get(
                    estimation_product=products.id)
                try:
                    glass_obj = MainProductGlassModel.objects.get(
                        estimation_product=products, glass_primary=True)
                except Exception as e:
                    glass_obj = None
                try:
                    second_glass_obj = MainProductGlassModel.objects.filter(
                        estimation_product=products, glass_primary=False)
                except Exception as e:
                    second_glass_obj = None
                try:
                    silicon_obj = MainProductSiliconModel.objects.get(
                        estimation_product=products)
                except Exception as e:
                    silicon_obj = None
                try:
                    addons = MainProductAddonCostModel.objects.filter(
                        estimation_product=products)
                except Exception as e:
                    addons = None
                pricing_control = PricingOptionModel.objects.get(
                    estimation_product=products)

                # try:
                # merge_product = EstimationMainProductMergeData.objects.get(estimation_product=products.main_product.id, merge_product=products.id)
                # except:
                #     merge_product = None

                unit_price = 0
                labour_percentage = 0
                labour_percent_price = 0
                overhead_percentage = 0
                overhead_percent_price = 0
                unit_total_price = 0
                tolarance = 0
                tolarance_price = 0
                estimated_value = 0
                total_price = 0
                quantity = 0
                unit_area = 0
                total_area = 0
                dimension = 0
                silicon_price = 0

                if aluminium_obj:
                    dimension = str(int(aluminium_obj.width)) + \
                        '*' + str(int(aluminium_obj.height))
                    # unit_area = (int(aluminium_obj.width) *
                    #              int(aluminium_obj.height))/1000000
                    quantity = aluminium_obj.total_quantity
                    
                    if products.deduction_method == 2:
                        deducted_area = float(aluminium_obj.area) - float(products.deducted_area)
                        unit_area = deducted_area
                    else:
                        unit_area = float(aluminium_obj.area)
                        
                    total_area = float(unit_area) * float(quantity)
                if not products.have_merge:
                    if aluminium_obj.al_quoted_price:
                        unit_price += float(aluminium_obj.al_quoted_price)

                    if glass_obj and glass_obj.is_glass_cost and glass_obj.glass_quoted_price:
                        unit_price += float(glass_obj.glass_quoted_price)
                    if second_glass_obj:
                        for second_glass in second_glass_obj:
                            if second_glass.glass_quoted_price:
                                unit_price += float(second_glass.glass_quoted_price)

                    if silicon_obj and silicon_obj.is_silicon:
                            unit_price += float(silicon_obj.silicon_quoted_price)
                    if products:
                        if products.accessory_total and products.is_accessory:
                            unit_price += float(products.accessory_total)
                        if pricing_control:
                            if pricing_control.labour_perce:
                                labour_percentage = float(
                                    pricing_control.labour_perce)/100
                                labour_percent_price = (
                                    float(unit_price)*float(labour_percentage))
                            if pricing_control.overhead_perce:
                                overhead_percentage = float(
                                    pricing_control.overhead_perce)/100
                                overhead_percent_price = (
                                    float(unit_price)*float(overhead_percentage))

                        if aluminium_obj.aluminium_pricing == 1 or aluminium_obj.aluminium_pricing == 2:
                            if products.is_tolerance:
                                if products.tolerance_type == 1:
                                    tolarance = int(products.tolerance)/100
                                    tolarance_price = float(
                                        aluminium_obj.al_quoted_price)*tolarance
                                elif products.tolerance_type == 2:
                                    tolarance_price = float(products.tolerance)
                                else:
                                    tolarance_price = 0
                            else:
                                tolarance_price = 0
                        else:
                            tolarance_price = 0
                        if products.deduction_method == 1:
                            if not products.after_deduction_price:
                                estimated_value = float((unit_price))+float(overhead_percent_price)+float(
                                    labour_percent_price)+float(tolarance_price)+float(products.total_addon_cost)
                            else:
                                estimated_value = float(products.after_deduction_price)
                        else:
                            if not products.deduction_price:
                                estimated_value = float((unit_price))+float(overhead_percent_price)+float(
                                    labour_percent_price)+float(tolarance_price)+float(products.total_addon_cost)
                            else:
                                estimated_value = products.after_deduction_price
                        # if not merge_product:
                        total_price = float(
                            math.ceil(estimated_value))*int(quantity)
                        # else:
                        #     total_price = 0
                else:
                    estimated_value = products.merge_price
                    total_price = float(
                        math.ceil(estimated_value))*int(quantity)

                try:
                    rp_sqm = total_price/total_area
                except Exception as e:
                    rp_sqm = 0
                # if not merge_product:
                if not products.main_product.have_merge or not products.product_type == 2:
                    building_total_price += total_price
                    if products.deduction_method == 1 or products.deduction_method == 2:
                        new_area = float(aluminium_obj.area) - float(products.deducted_area)
                        total_new_area = float(new_area)*float(aluminium_obj.total_quantity)
                        
                        if products.product:
                            worksheet.write(header_title+index, 0, str(aluminium_obj.product_type) + ' | ' + str(
                                products.product.product_name) + ' | ' + str(aluminium_obj.product_description or ''))
                            worksheet.write(header_title+index, 1, dimension)
                            worksheet.write(header_title+index, 2,
                                            round(new_area, 2))
                            worksheet.write(header_title+index, 3,
                                            round(aluminium_obj.total_quantity, 2))
                            worksheet.write(header_title+index, 4,
                                            round(total_new_area, 2))
                            worksheet.write(header_title+index, 5,
                                            math.ceil(round(estimated_value, 2)))
                            worksheet.write(header_title+index, 6, round(rp_sqm, 2))
                            worksheet.write(header_title+index, 7,
                                            math.ceil(round(total_price, 2)))
                            worksheet.write_formula(
                                'H'+str(header_title+index+1), '=D'+str(header_title+index+1)+'*F'+str(header_title+index+1))
                            index += 1
                        else:
                            worksheet.write(header_title+index, 0, str(aluminium_obj.product_type) + ' | ' + str(
                                products.panel_product.product_name) + ' | ' + str(aluminium_obj.product_description or ''))
                            worksheet.write(header_title+index, 1, dimension)
                            worksheet.write(header_title+index, 2,
                                            round(new_area, 2))
                            worksheet.write(header_title+index, 3,
                                            round(aluminium_obj.total_quantity, 2))
                            worksheet.write(header_title+index, 4,
                                            round(total_new_area, 2))
                            worksheet.write(header_title+index, 5,
                                            math.ceil(round(estimated_value, 2)))
                            worksheet.write(header_title+index, 6, round(rp_sqm, 2))
                            worksheet.write(header_title+index, 7,
                                            math.ceil(round(total_price, 2)))
                            worksheet.write_formula(
                                'H'+str(header_title+index+1), '=D'+str(header_title+index+1)+'*F'+str(header_title+index+1))
                            index += 1
                    else:
                        if products.product:
                            worksheet.write(header_title+index, 0, str(aluminium_obj.product_type) + ' | ' + str(
                                products.product.product_name) + ' | ' + str(aluminium_obj.product_description or ''))
                            worksheet.write(header_title+index, 1, dimension)
                            worksheet.write(header_title+index, 2,
                                            round(aluminium_obj.area, 2))
                            worksheet.write(header_title+index, 3,
                                            round(aluminium_obj.total_quantity, 2))
                            worksheet.write(header_title+index, 4,
                                            round(aluminium_obj.total_area, 2))
                            worksheet.write(header_title+index, 5,
                                            math.ceil(round(estimated_value, 2)))
                            worksheet.write(header_title+index, 6, round(rp_sqm, 2))
                            worksheet.write(header_title+index, 7,
                                            math.ceil(round(total_price, 2)))
                            worksheet.write_formula(
                                'H'+str(header_title+index+1), '=D'+str(header_title+index+1)+'*F'+str(header_title+index+1))
                            index += 1
                        else:
                            worksheet.write(header_title+index, 0, str(aluminium_obj.product_type) + ' | ' + str(
                                products.panel_product.product_name) + ' | ' + str(aluminium_obj.product_description or ''))
                            worksheet.write(header_title+index, 1, dimension)
                            worksheet.write(header_title+index, 2,
                                            round(aluminium_obj.area, 2))
                            worksheet.write(header_title+index, 3,
                                            round(aluminium_obj.total_quantity, 2))
                            worksheet.write(header_title+index, 4,
                                            round(aluminium_obj.total_area, 2))
                            worksheet.write(header_title+index, 5,
                                            math.ceil(round(estimated_value, 2)))
                            worksheet.write(header_title+index, 6, round(rp_sqm, 2))
                            worksheet.write(header_title+index, 7,
                                            math.ceil(round(total_price, 2)))
                            worksheet.write_formula(
                                'H'+str(header_title+index+1), '=D'+str(header_title+index+1)+'*F'+str(header_title+index+1))
                            index += 1
                
                    
            header_title += index
                    
            if not building_total_price == 0:
                worksheet.write(header_title, 7, 'QAR. '+str(round(building_total_price, 2)),
                                workbook.add_format({'bold': True, 'font_color': 'white', 'fg_color': '#485699'}))

            footer_row += 1
            if building.typical_buildings_enabled:
                header_title += 4
            
                mergerange2 = 'A'+str((header_title-2)) + \
                    ':'+'G'+str(header_title-2)
                worksheet.merge_range(
                    mergerange2, "Number of Typical Buildings: "+str(building.no_typical_buildings), cell_format)
                worksheet.write(header_title-3, 7, 'QAR. '+str(round((float(building_total_price)*float(building.no_typical_buildings)), 2)),
                                workbook.add_format({'bold': True, 'font_color': 'white', 'fg_color': '#485699'}))
            else:
                header_title += 2

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=' + \
            csv_file_name+'.xlsx'
        message = 'Exported Estimation Scope Excel Data From Original ' if estimation.version.version == '0' \
            else 'Exported Estimation Scope Excel Data From Revision '+str(estimation.version.version)
        enquiry_logger(enquiry=estimation.enquiry,
                    message=message, action=4, user=request.user)
        return HttpResponse(response, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    elif type == 'pdf':
        buildings = EstimationBuildingsModel.objects.filter(estimation=version).order_by('id')
        estimation = EstimationsModel.objects.get(pk=version)
        product = EstimationMainProductModel.objects.select_related(
            'building').filter(building__estimation=estimation.id).order_by('product_index')
        specification_obj = EnquirySpecificationsModel.objects.select_related(
            'estimation').filter(estimation=estimation).order_by('id')
        try:
            quotations = QuotationsModel.objects.get(estimations=version)
        except Exception:
            quotations = None

        context = {
            "estimation": estimation,
            "product": product,
            "version": estimation,
            "enquiry_obj": estimation.enquiry,
            "specification_obj": specification_obj,
            "filter_by_boq": False,
            "quotations": quotations,
            "building_obj": buildings,
            "STATIC_URL": f'http://{str(request.get_host())}/{str(STATIC_URL)}',
            "MEDIA_URL": f'http://{str(request.get_host())}{str(MEDIA_URL)}',
        }
        cmd_options = {
            'quiet': True,
            'enable-local-file-access': True,
            'margin-top': '10mm',
            'header-spacing': 5,
            # 'javascript-delay': 5000,
            # 'debug-javascript': True,
            'orientation': 'Landscape',
            'minimum-font-size': 16,
            'page-size': 'A4',
            'encoding': "UTF-8",
            'print-media-type': True,
            'footer-right': "[page] / [topage]",
            'footer-font-size': 8,
        }
        template = get_template('print_templates/scope_data_print.html')
        
        file_name = "Scope of  "+str(['Original' if estimation.version.version == '0' else 'Revision '+str(
            estimation.version.version)][0])+" in "+str(estimation.enquiry.title)+' By Building.pdf'
        clean_string  = re.sub(r'[^\w\s\-\.]', '', file_name)
        response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True,
                                    template=template, context=context)
        response = HttpResponse(response.rendered_content, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename='+clean_string
        
        return response
        
    
@shared_task(time_limit=600)
def export_csv_estimation_socpe_boq_shared(request, version, enq, type, temp=None):
    
    if temp:
        EstimationsModel = Temp_Estimations
        EstimationMainProductModel = Temp_EstimationMainProduct
        EnquirySpecificationsModel = Temp_EnquirySpecifications
        EstimationBuildingsModel = Temp_EstimationBuildings
        MainProductAluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        MainProductSiliconModel = Temp_MainProductSilicon
        MainProductAddonCostModel = Temp_MainProductAddonCost
        PricingOptionModel = Temp_PricingOption
        QuotationsModel = Temp_Quotations
    else:
        EstimationsModel = Estimations
        EstimationMainProductModel = EstimationMainProduct
        EnquirySpecificationsModel = EnquirySpecifications
        EstimationBuildingsModel = EstimationBuildings
        MainProductAluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
        MainProductSiliconModel = MainProductSilicon
        MainProductAddonCostModel = MainProductAddonCost
        PricingOptionModel = PricingOption
        QuotationsModel = Quotations
        
    if type == 'xlsx':
        boqs = BillofQuantity.objects.filter(enquiry=enq).order_by('id')
        header = ['Product', 'Dimension', 'Area Per Unit', 'Quantity',
                  'Total Area per Unit', 'Rate per Unit', 'Rate per Meter', 'Total Price']
        csv_file_name = 'BOQ'
        output = io.BytesIO()
        workbook = Workbook(output)
        worksheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'bold': True, 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'fg_color': '#485699'})
        # sheet = workbook.active
        for p, head in enumerate(header):
            worksheet.write(0, p, head, workbook.add_format({'bold': True}))
        header_title = 2
        footer_row = 0

        for j, boq in enumerate(boqs):
            boq_total_price = 0
            main_product = EstimationMainProductModel.objects.filter(
                boq_number__boq_number=boq.boq_number).order_by('product_index')
            mergerange = 'A'+str(j+header_title-footer_row) + \
                ':'+'H'+str(j+header_title-footer_row)
            worksheet.merge_range(mergerange, boq.boq_number, cell_format)
            for i, products in enumerate(main_product):
                # building_name = building.building_name
                aluminium_obj = MainProductAluminiumModel.objects.get(
                    estimation_product=products)
                try:
                    glass_obj = MainProductGlassModel.objects.get(
                        estimation_product=products, glass_primary=True)
                except Exception as e:
                    glass_obj = None
                try:
                    second_glass_obj = MainProductGlassModel.objects.filter(
                        estimation_product=products, glass_primary=False).order_by('id')
                except Exception as e:
                    second_glass_obj = None
                try:
                    silicon_obj = MainProductSiliconModel.objects.get(
                        estimation_product=products)
                except Exception as e:
                    silicon_obj = None
                try:
                    addons = MainProductAddonCostModel.objects.filter(
                        estimation_product=products).order_by('id')
                except Exception as e:
                    addons = None
                pricing_control = PricingOptionModel.objects.get(
                    estimation_product=products)
                unit_price = 0
                labour_percentage = 0
                labour_percent_price = 0
                overhead_percentage = 0
                overhead_percent_price = 0
                unit_total_price = 0
                tolarance = 0
                tolarance_price = 0
                estimated_value = 0
                total_price = 0
                quantity = 0
                unit_area = 0
                total_area = 0
                dimension = 0
                silicon_price = 0
                if aluminium_obj:
                    dimension = str(int(aluminium_obj.width)) + \
                        '*' + str(int(aluminium_obj.height))
                    unit_area = round((int(aluminium_obj.width) *
                                 int(aluminium_obj.height))/1000000, 2)
                    quantity = aluminium_obj.total_quantity
                    total_area = float(unit_area) * float(quantity)
                    if aluminium_obj.al_quoted_price:
                        unit_price += float(aluminium_obj.al_quoted_price)

                if glass_obj:
                    if glass_obj.is_glass_cost:
                        if glass_obj.glass_quoted_price:
                            unit_price += float(glass_obj.glass_quoted_price)
                if second_glass_obj:
                    for second_glass in second_glass_obj:
                        if second_glass.glass_quoted_price:
                            unit_price += float(second_glass.glass_quoted_price)
                if silicon_obj:
                    if silicon_obj.is_silicon:
                        unit_price += float(silicon_obj.silicon_quoted_price)
                if products:
                    if products.accessory_total and products.is_accessory:
                        unit_price += float(products.accessory_total)
                    if pricing_control:
                        if pricing_control.labour_perce:
                            labour_percentage = float(
                                pricing_control.labour_perce)/100
                            labour_percent_price = (
                                float(unit_price)*float(labour_percentage))
                        if pricing_control.overhead_perce:
                            overhead_percentage = float(
                                pricing_control.overhead_perce)/100
                            overhead_percent_price = (
                                float(unit_price)*float(overhead_percentage))

                    if aluminium_obj.aluminium_pricing == 1 or aluminium_obj.aluminium_pricing == 2:
                        if products.is_tolerance:
                            if products.tolerance_type == 1:
                                tolarance = int(products.tolerance)/100
                                tolarance_price = float(
                                    aluminium_obj.al_quoted_price)*tolarance
                            elif products.tolerance_type == 2:
                                tolarance_price = float(products.tolerance)
                            else:
                                tolarance_price = 0
                        else:
                            tolarance_price = 0
                    else:
                        tolarance_price = 0
                    if products.deduction_method == 2:
                        if not products.deduction_price:
                            estimated_value = float(unit_price)+float(overhead_percent_price)+float(
                                labour_percent_price)+float(tolarance_price)+float(products.total_addon_cost)
                        else:
                            estimated_value = products.after_deduction_price
                    else:
                        if not products.after_deduction_price:
                            estimated_value = float(unit_price)+float(overhead_percent_price)+float(
                                labour_percent_price)+float(tolarance_price)+float(products.total_addon_cost)
                        else:
                            estimated_value = float(
                                products.after_deduction_price)

                    total_price = float(
                        math.ceil(estimated_value))*int(quantity)
                    boq_total_price += total_price
                try:
                    rp_sqm = total_price/total_area
                except Exception as e:
                    rp_sqm = 0
                if products.product:
                    worksheet.write(header_title+i, 0, aluminium_obj.product_type + ' | ' +
                                    products.product.product_name + ' | ' + aluminium_obj.product_description)
                    worksheet.write(header_title+i, 1, dimension)
                    worksheet.write(header_title+i, 2,
                                    round(aluminium_obj.area, 2))
                    worksheet.write(header_title+i, 3,
                                    round(aluminium_obj.total_quantity, 2))
                    worksheet.write(header_title+i, 4,
                                    round(aluminium_obj.total_area, 2))
                    worksheet.write(header_title+i, 5,
                                    round(estimated_value, 2))
                    worksheet.write(header_title+i, 6, round(rp_sqm, 2))
                    worksheet.write(header_title+i, 7, round(total_price, 2))
                else:
                    worksheet.write(header_title+i, 0, aluminium_obj.product_type + ' | ' +
                                    products.panel_product.product_name + ' | ' + aluminium_obj.product_description)
                    worksheet.write(header_title+i, 1, dimension)
                    worksheet.write(header_title+i, 2,
                                    round(aluminium_obj.area, 2))
                    worksheet.write(header_title+i, 3,
                                    round(aluminium_obj.total_quantity, 2))
                    worksheet.write(header_title+i, 4,
                                    round(aluminium_obj.total_area, 2))
                    worksheet.write(header_title+i, 5,
                                    round(estimated_value, 2))
                    worksheet.write(header_title+i, 6, round(rp_sqm, 2))
                    worksheet.write(header_title+i, 7, round(total_price, 2))
            header_title += i+1
            if not boq_total_price == 0:
                worksheet.write(header_title, 7, 'QAR. '+str(boq_total_price), workbook.add_format(
                    {'bold': True, 'font_color': 'white', 'fg_color': '#485699'}))
            header_title += 2
            footer_row += 1

        workbook.close()
        output.seek(0)
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=' + \
            csv_file_name+'.xlsx'
        try:
            message = 'Exported Estimation Scope BoQ Wise Excel Data From Original.' if products.building.estimation.version.version == '0' \
                else 'Exported Estimation Scope  BoQ Wise Excel Data From Revision '+str(products.building.estimation.version.version)
            enquiry_logger(enquiry=boqs.first().enquiry,
                           message=message, action=4, user=request.user)
        except:
            pass
        return response
    elif type == 'pdf':
        boqs = BillofQuantity.objects.filter(enquiry=enq).order_by('id')
        estimation = EstimationsModel.objects.get(pk=version)
        enquiry_obj = Enquiries.objects.get(pk=estimation.enquiry.id)
        estim_versions = EstimationsModel.objects.select_related(
            'enquiry').filter(enquiry=enquiry_obj).order_by('id')
        temp_estimations = Temp_Estimations.objects.select_related(
            'enquiry').filter(enquiry=enquiry_obj).order_by('id')
        product = EstimationMainProductModel.objects.select_related(
            'building').filter(building__estimation=estimation.id).order_by('product_index')
        specification_obj = EnquirySpecificationsModel.objects.select_related(
            'estimation').filter(estimation=estimation).order_by('id')
        quotations = QuotationsModel.objects.select_related('estimations').filter(
            estimations__enquiry=enquiry_obj).order_by('id')

        context = {
            "estimation": estimation,
            "product": product,
            "version": estimation,
            "estim_versions": estim_versions,
            "temp_estimations": temp_estimations,
            "enquiry_obj": enquiry_obj,
            "specification_obj": specification_obj,
            "filter_by_boq": True,
            "quotations": quotations,
            "boqs": boqs,
            "STATIC_URL": 'http://'+str(request.get_host())+'/'+str(STATIC_URL),
            "MEDIA_URL": 'http://'+str(request.get_host())+'/'+str(MEDIA_URL)

        }
        cmd_options = {
            'quiet': True,
            'enable-local-file-access': True,
            'margin-top': '10mm',
            'header-spacing': 5,
            # 'javascript-delay': 5000,
            # 'debug-javascript': True,
            'orientation': 'Landscape',
            'minimum-font-size': 16,
            'page-size': 'A4',
            'encoding': "UTF-8",
            'print-media-type': True,
            'footer-right': "[page] / [topage]",
            'footer-font-size': 8,
        }
        template = get_template('print_templates/scope_data_print.html')

        file_name = "Scope of  "+str(['Original' if estimation.version.version == '0' else 'Revision '+str(
            estimation.version.version)][0])+" in "+str(estimation.enquiry.title)+' By BoQ.pdf'
        clean_string  = re.sub(r'[^\w\s\-\.]', '', file_name)
        response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True,
                                       template=template, context=context)
        response = HttpResponse(response.rendered_content,
                                content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename='+clean_string
        return response
    

def product_merge_excel(request, version):
    
    PATHS = [
        '/Estimation/product_merge_summary/',
        '/Estimation/merge_summary_print/',
        '/Enquiries/product_category_summary/',
        '/Estimation/merge_summary_print_2/',
    ]
    
    if any(path in request.path for path in PATHS):
        specification_obj = EnquirySpecifications.objects.filter(estimation=version).distinct(
                                        'identifier', 
                                        'categories', 
                                        'aluminium_products', 
                                        'panel_specification'
                                    )
    else:
        specification_obj = Temp_EnquirySpecifications.objects.filter(estimation=version).distinct(
                                        'identifier', 
                                        'categories', 
                                        'aluminium_products', 
                                        'panel_specification'
                                    )
    data = {
        "categorys": specification_obj
    }
    return data

def product_by_identifier_excel(request, version, pk):
    
    PATHS = [
        '/Estimation/product_merge_summary/',
        '/Estimation/merge_summary_print/',
        '/Enquiries/product_category_summary/',
        '/Estimation/merge_summary_print_2/',
        '/Estimation/costing_summary/',
        '/Estimation/comparing_data/',
    ]
    
    if any(path in request.path for path in PATHS):
        EstimationMainProductModel = EstimationMainProduct
    else:
        EstimationMainProductModel = Temp_EstimationMainProduct
        
    curtain_wall_products = EstimationMainProductModel.objects.filter(
        category__is_curtain_wall=True,
        building__estimation=version,
        specification_Identifier=pk,
        disabled=False
    ).annotate(
        product_sqm_price_without_addon_int=Func(F('product_sqm_price_without_addon'), function='FLOOR')
    ).distinct('product_sqm_price_without_addon_int', 'product__product_name')
    other_products = EstimationMainProductModel.objects.filter(category__is_curtain_wall=False, \
        building__estimation=version, specification_Identifier=pk).distinct('product_base_rate', 'product__product_name')
    data = {
        'curtain_wall_products': curtain_wall_products,
        'other_products': other_products,
    }
    return data


def get_product_pricing_type_excel(request, pk):
    """
    The function retrieves the pricing type of a product based on its attributes and returns the pricing
    types for aluminum and glass components.
    """
    PATHS = [
        '/Estimation/product_merge_summary/',
        '/Estimation/merge_summary_print/',
        '/Enquiries/product_category_summary/', 
        '/Estimation/merge_summary_print_2/',
        '/Estimation/costing_summary/',
        '/Estimation/cost_summary_details/',
        '/Estimation/estimation_comparing_summary/',
        '/Estimation/comparing_data/',
        '/Estimation/comparing_data_with_q_id/',
    ]
    if any(path in request.path for path in PATHS):
        EstimationMainProductModel = EstimationMainProduct
        MainProductAluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
    else:
        EstimationMainProductModel = Temp_EstimationMainProduct
        MainProductAluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        
    product = EstimationMainProductModel.objects.get(pk=pk)
    al_pricing_type = None
    gl_pricing_type = None
    
    try:
        aluminium_obj = MainProductAluminiumModel.objects.get(estimation_product=product.id)
    except Exception:
        aluminium_obj = None
    try:
        glass_obj = MainProductGlassModel.objects.get(estimation_product=product.id, glass_primary=True)
    except Exception:
        glass_obj = None
            
    if aluminium_obj.aluminium_pricing == 1:
        if aluminium_obj.al_price_per_unit:
            al_pricing_type = 'PRE_UNIT'
        elif aluminium_obj.al_price_per_sqm:
            al_pricing_type = 'PRE_SQM'
        elif aluminium_obj.al_weight_per_unit:
            al_pricing_type = 'PRE_KG'
        else:
            al_pricing_type = None
    elif aluminium_obj.aluminium_pricing == 2:
        if aluminium_obj.pricing_unit == 1:
            al_pricing_type = 'CUSTOM_SQM'
        elif aluminium_obj.pricing_unit == 2:
            al_pricing_type = 'CUSTOM_UNIT'
        elif aluminium_obj.pricing_unit == 3:
            al_pricing_type = 'CUSTOM_KG'
        else:
            al_pricing_type = None
    elif aluminium_obj.aluminium_pricing == 4:
        al_pricing_type = 'FORMULA_KG'
    else:
        al_pricing_type = None
    
    if glass_obj:
        if glass_obj.glass_pricing_type == 1:
            gl_pricing_type = 'PRE_SQM'
        elif glass_obj.glass_pricing_type == 2:
            gl_pricing_type = 'CUSTOM_SQM'
        else:
            gl_pricing_type = None
    
    if al_pricing_type and gl_pricing_type:
        context = {
            'al_pricing_type': al_pricing_type,
            'gl_pricing_type': gl_pricing_type
        }
    elif al_pricing_type and not gl_pricing_type:
        context = {
            'al_pricing_type': al_pricing_type,
        }
    elif not al_pricing_type and gl_pricing_type:
        context = {
            'gl_pricing_type': gl_pricing_type
        }
    else:
        context = {
            'al_pricing_type': None,
            'gl_pricing_type': None
        }
        
    
    return context


def get_product_name(request, product):
    if product.main_product and product.main_product.have_merge:
        if product.product_type == 1:
            # Fetch associated data for the main product
            associ_datas = assocciated_data(request=request, pk=product.main_product.id)
            associated_product = associ_datas.first()  # Use first() to get the first object from the QuerySet
            if associated_product:
                if associated_product.product:
                    return str(associated_product.product)  # Assuming `product` has a string representation (e.g., product_name)
                else:
                    return str(associated_product.panel_product)  # Assuming `panel_product` has a string representation
        else:
            if product.product:
                return str(product.product)
            else:
                return str(product.panel_product)
    else:
        if product.product:
            return str(product.product)
        else:
            return str(product.panel_product)
        

def get_merge_products_excel(request, category, products):
    """
    This function retrieves product data and category information based on a given category and list of
    product IDs.
    
    """
    category = Category.objects.get(pk=category)
    product_data = []
    product_ids = []
    alumin = []
    PATHS = [
        '/Enquiries/product_category_summary/',
        '/Estimation/merge_summary_print_2/'
    ]
    if any(path in request for path in PATHS):
        EstimationMainProductModel = EstimationMainProduct
        MainProductAluminiumModel = MainProductAluminium
    else:
        EstimationMainProductModel = Temp_EstimationMainProduct
        MainProductAluminiumModel = Temp_MainProductAluminium
    
    summary_product = MainProductAluminiumModel.objects.filter(estimation_product__in=products).order_by('area')
    alumin.append(summary_product)
    for pro in summary_product:
        main_pro = EstimationMainProductModel.objects.filter(pk=pro.estimation_product.id)
        product_data.append(main_pro)
        
    data = {
        "category": category,
        "product_data": product_data,
        "products": products
    }
    return data

@shared_task(time_limit=600)
def merge_summary_print_2_shared(request, pk, type, f_type=None, temp=None):
    
    if temp:
        EstimationsModel = Temp_Estimations
        EstimationMainProductModel = Temp_EstimationMainProduct
        EnquirySpecificationsModel = Temp_EnquirySpecifications
        EstimationBuildingsModel = Temp_EstimationBuildings
        MainProductAluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        MainProductSiliconModel = Temp_MainProductSilicon
        MainProductAddonCostModel = Temp_MainProductAddonCost
        PricingOptionModel = Temp_PricingOption
        QuotationsModel = Temp_Quotations
    else:
        EstimationsModel = Estimations
        EstimationMainProductModel = EstimationMainProduct
        EnquirySpecificationsModel = EnquirySpecifications
        EstimationBuildingsModel = EstimationBuildings
        MainProductAluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
        MainProductSiliconModel = MainProductSilicon
        MainProductAddonCostModel = MainProductAddonCost
        PricingOptionModel = PricingOption
        QuotationsModel = Quotations
        
        
    estimation_version = EstimationsModel.objects.get(pk=pk)
    enquiry_obj = Enquiries.objects.get(pk=estimation_version.enquiry.id)
    specification_obj = EnquirySpecificationsModel.objects.filter(estimation=estimation_version).order_by('id')
    main_product = EstimationMainProductModel.objects.filter(building__estimation=estimation_version).order_by('product_index')
    
    if type == 'pdf':
    
        context = {
            'pk': pk,
            "enquiry_obj": enquiry_obj,
            "version": estimation_version,
            "specification_obj": specification_obj,
            "main_product": main_product,
            "f_type": f_type,
            # 'STATIC_URL': 'http://'+str(request.get_host())+'/'+str(STATIC_URL),
            # "MEDIA_URL": 'http://'+str(request.get_host())+'/'+str(MEDIA_URL)
            'STATIC_URL': STATIC_URL,
            "MEDIA_URL": MEDIA_URL,
        }
        
        cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '10mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 14,
                    'page-size': 'A3',
                    'encoding': "UTF-8",
                    'orientation': 'Landscape',
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,
                    
                }
        template = get_template('print_templates/mass_update_2_print.html')
        file_name = 'Merge Summary_2 of Version '+ str(['Original' if estimation_version.version.version == 0 else 'Revision '+str(estimation_version.version.version)][0])+' in '+str(enquiry_obj.title)+'.pdf'
        # html_content = template.render(context)
        # pdf_bytes = subprocess.run(cmd_options, input=html_content.encode('utf-8'), capture_output=True).stdout
        response = PDFTemplateResponse(
                        request=request, 
                        cmd_options=cmd_options, 
                        # header_template=header,
                        show_content_in_browser=False, 
                        template=template, context=context,
                    )
        response = HttpResponse(response.rendered_content, content_type='application/pdf')
        # response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename='+file_name
        return response
    elif type == 'xlsx':
        
        # Define the header for the Excel file
        header = [
            'No.', 'Product', 'Type', 'Aluminium', 'Infill/Panel',
            'Accessories', 'Sealant', 'Material Cost',
            'L + OH', 'Sub Total', 'RpM2', 'Add-Ons', 'Rate/Unit',
            'Line Total', 'Add-Ons RpM2'
        ]
        csv_file_name = 'Product Summary'
        output = io.BytesIO()
        workbook = Workbook(output)
        worksheet = workbook.add_worksheet()

        # Define formats
        header_format = workbook.add_format({
            'bold': True, 'font_color': 'white', 'align': 'center',
            'valign': 'vcenter', 'fg_color': '#485699'
        })
        bold_red_format = workbook.add_format({
            'bold': True, 'font_color': 'red', 'align': 'right'
        })
        bold_red_center_format = workbook.add_format({
            'bold': True, 'font_color': 'red', 'align': 'center'
        })
        text_format = workbook.add_format({'align': 'left'})
        number_format = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
        muted_format = workbook.add_format({'font_color': '#757575', 'align': 'right'})
        total_format = workbook.add_format({
            'bold': True, 'font_color': 'black', 'align': 'right',
            'num_format': '#,##0.00', 'bg_color': '#D3D3D3'
        })
        
        type_formats = {
            'CUSTOM_KG': workbook.add_format({'bg_color': '#00FF00', 'align': 'center', 'font_color': 'white'}),
            'CUSTOM_UNIT': workbook.add_format({'bg_color': '#FFFF00', 'align': 'center', 'font_color': 'white'}),
            'CUSTOM_SQM': workbook.add_format({'bg_color': '#0000FF', 'align': 'center', 'font_color': 'white'}),
            'PRE_UNIT': workbook.add_format({'bg_color': '#FFFF00', 'align': 'center', 'font_color': 'white'}),
            'PRE_SQM': workbook.add_format({'bg_color': '#0000FF', 'align': 'center', 'font_color': 'white'}),
            'PRE_KG': workbook.add_format({'bg_color': '#00FF00', 'align': 'center', 'font_color': 'white'}),
            'FORMULA_KG': workbook.add_format({'bg_color': '#00FF00', 'align': 'center', 'font_color': 'white'}),
            'DEFAULT': workbook.add_format({'bg_color': '#0000FF', 'align': 'center', 'font_color': 'white'}),
        }

        # Write the header
        for col, head in enumerate(header):
            worksheet.write(0, col, head, header_format)

        # Initialize row counters
        header_title = 2
        footer_row = 0
        row_counter = 0

        # Fetch data for categories
        datas = product_merge_excel(request=request, version=estimation_version.id)
        sub_line_total = 0
        for i, specification in enumerate(datas['categorys']):
            products = product_by_identifier_excel(request=request, version=estimation_version.id, pk=specification.id)
            if products['curtain_wall_products'] or products['other_products']:
                # Write category title
                title = f'{specification} - {specification.categories}'
                mergerange = f'A{header_title + row_counter}:O{header_title + row_counter}'
                worksheet.merge_range(mergerange, title, header_format)
                row_counter += 1

                # Process curtain wall products
                for j, product in enumerate(products['curtain_wall_products']):
                    product_data = category_summary_data_excel(request=request, pk=product.id)
                    pricing_type = get_product_pricing_type_excel(request=request, pk=product_data['main_product'].id)
                    data = merge_summary_count2(
                        request=request, pk=specification.id, version=estimation_version.id,
                        sqm=product_data['main_product'].product_sqm_price_without_addon,
                        product=product_data['main_product'].id
                    )

                    # Write product row
                    current_row = header_title + row_counter - 1
                    worksheet.write(current_row, 0, j + 1, bold_red_center_format)

                    # Product name and details
                    product_name = get_product_name(request, product)
                    area_label0 = f"{product_data['aluminium_obj'].area} m²"
                    if not product_data['main_product'].category.is_curtain_wall:
                        area_label = f"{data['quantity']} Nº" if product_data['aluminium_obj'].total_quantity else '- Nº'
                    else:
                        area_label = f"{data['quantity']} Nº" if product_data['aluminium_obj'].total_quantity else '- Nº'

                    if product_data['main_product'].deduction_method == 2 and product_data['main_product'].deduction_price:
                        main_area = product_data['main_product'].total_associated_area
                        deduct_area = product_data['main_product'].deducted_area
                        quantity = data['quantity']
                        area_label2 = f"{float(main_area - deduct_area) * quantity:.2f} m²"
                    else:
                        area_label2 = f"{data['total_area']:.2f} m²"

                    product_details = f"{product_name}\n{area_label0} | {area_label} | {area_label2}"
                    worksheet.write(current_row, 1, product_details, text_format)

                    # Pricing type
                    pricing_type_value = pricing_type.get('al_pricing_type', '-')
                    type_label = {
                        'CUSTOM_KG': 'Kg', 'CUSTOM_UNIT': 'Unit', 'CUSTOM_SQM': 'SqM',
                        'PRE_UNIT': 'Unit', 'PRE_SQM': 'SqM', 'PRE_KG': 'Kg',
                        'FORMULA_KG': 'Kg'
                    }.get(pricing_type_value, 'SqM')
                    type_format = type_formats.get(pricing_type_value, type_formats['DEFAULT'])
                    worksheet.write(current_row, 2, type_label, type_format)

                    # Aluminium cost
                    aluminium_cost = f"{data['aluminium_rate']:.2f}" if product_data['aluminium_obj'].al_quoted_price else '-'
                    worksheet.write(current_row, 3, aluminium_cost, bold_red_format)

                    # Infill/Panel cost
                    glass_cost = f"{data['glass_rate']:.2f}" if product_data['glass_obj'] else '-'
                    worksheet.write(current_row, 4, glass_cost, bold_red_format)

                    # Accessories cost
                    accessory_cost = f"{data['accessory_price']:.2f}" if data['accessory_price'] else '-'
                    worksheet.write(current_row, 5, accessory_cost, bold_red_format)

                    # Sealant cost
                    silicon_cost = f"{data['silicon_price']:.2f}" if data['silicon_price'] else '-'
                    worksheet.write(current_row, 6, silicon_cost, bold_red_format)

                    # Material cost
                    material_cost = f"{data['material_cost']:.2f}" if product_data['material_total'] else '-'
                    worksheet.write(current_row, 7, material_cost, bold_red_format)

                    # Labor + Overhead
                    labour_overhead = f"{data['labour_overhead']:.2f}" if product_data['l_o'] else '-'
                    worksheet.write(current_row, 8, labour_overhead, bold_red_format)

                    # Sub Total
                    sub_total = f"{data['sub_total']:.2f}" if data['sub_total'] else '-'
                    worksheet.write(current_row, 9, sub_total, bold_red_format)

                    # Rate per m² (without add-ons)
                    rpm2 = f"{product_data['rate_per_sqm_without_addons']:.2f}" if product_data['rate_per_sqm_without_addons'] else '-'
                    worksheet.write(current_row, 10, rpm2, bold_red_format)

                    # Add-Ons cost
                    addon_cost = f"{data['addon_cost']:.2f}" if data['addon_cost'] else '-'
                    worksheet.write(current_row, 11, addon_cost, bold_red_format)

                    # Rate per Unit
                    rate_unit = '-'  # As per template, this column is hardcoded to '-'
                    worksheet.write(current_row, 12, rate_unit, bold_red_format)

                    # Line Total
                    line_total = f"{data['round_total_price']:.2f}" if data['round_total_price'] else '-'
                    sub_line_total += float(line_total) if line_total else 0
                    worksheet.write(current_row, 13, line_total, bold_red_format)

                    # Add-Ons Rate per m²
                    addon_rpm2 = f"{product_data['rate_per_sqm']:.2f}" if product_data['rate_per_sqm'] else '-'
                    worksheet.write(current_row, 14, addon_rpm2, bold_red_format)

                    row_counter += 1

                    # Add sub-rows for merged products if f_type is True
                    if f_type:
                        products_data = get_merge_products_excel(request=request.path, category=product_data['main_product'].category.id, products=data['ids'])
                        for k, sub_product in enumerate(products_data['product_data']):
                            sub_product_data = category_summary_data_excel(request=request, pk=sub_product[0].id)
                            sub_row = header_title + row_counter - 1

                            # Sub-row numbering
                            worksheet.write(sub_row, 0, f"{j + 1}.{k + 1}", muted_format)

                            # Sub-product details
                            sub_area_label = (
                                f"{sub_product_data['aluminium_obj'].product_type} | "
                                f"{sub_product_data['aluminium_obj'].width:.0f}*{sub_product_data['aluminium_obj'].height:.0f} | "
                                f"{sub_product_data['aluminium_obj'].area} m² | "
                                f"{sub_product_data['aluminium_obj'].total_quantity} Nº | "
                            )
                            if sub_product_data['main_product'].deduction_method == 2 and sub_product_data['main_product'].deduction_price:
                                main_area = sub_product_data['main_product'].total_associated_area
                                deduct_area = sub_product_data['main_product'].deducted_area
                                quantity = sub_product_data['aluminium_obj'].total_quantity
                                total_area = float(main_area - deduct_area) * float(quantity)
                                sub_area_label += f"TA: {total_area:.2f} m²"
                            else:
                                total_area = sub_product_data['aluminium_obj'].total_area
                                sub_area_label += f"TA: {total_area:.2f} m²"
                            worksheet.write(sub_row, 1, sub_area_label, text_format)
                            worksheet.write(sub_row, 2, '', text_format)  # Type column (empty for sub-row)

                            # Sub-row costs (muted if deduction method is applied)
                            format_to_use = muted_format if sub_product_data['main_product'].deduction_method else number_format
                            worksheet.write(sub_row, 3, sub_product_data['aluminium_obj'].al_quoted_price or '-', format_to_use)
                            glass_cost = sub_product_data['glass_obj'].glass_quoted_price if sub_product_data['glass_obj'] and sub_product_data['glass_obj'].is_glass_cost else '0.00'
                            worksheet.write(sub_row, 4, glass_cost, format_to_use)
                            worksheet.write(sub_row, 5, sub_product_data['total_access_price'] or '-', format_to_use)
                            worksheet.write(sub_row, 6, sub_product_data['silicon_total'] or '-', format_to_use)
                            worksheet.write(sub_row, 7, sub_product_data['material_total'] or '-', format_to_use)
                            worksheet.write(sub_row, 8, sub_product_data['l_o'] or '-', format_to_use)
                            worksheet.write(sub_row, 9, sub_product_data['sub_total'] or '-', format_to_use)
                            worksheet.write(sub_row, 10, sub_product_data['rate_per_sqm_without_addons'] or '-', format_to_use)
                            worksheet.write(sub_row, 11, sub_product_data['total_addon_cost'] or '-', format_to_use)
                            worksheet.write(sub_row, 12, sub_product_data['round_rate_per_unit'] or '-', format_to_use)
                            worksheet.write(sub_row, 13, sub_product_data['round_line_total'] or '-', format_to_use)
                            worksheet.write(sub_row, 14, sub_product_data['rate_per_sqm'] or '-', format_to_use)

                            row_counter += 1
                    # worksheet.write(row_counter+sub_row, 13, sub_line_total, bold_red_format)
                    
                    # total_row = header_title + row_counter
                    # worksheet.merge_range(f'A{total_row}:M{total_row}', 'Total for Section', total_format)
                    # worksheet.write(total_row, 13, sub_line_total, total_format)
                    # worksheet.write(total_row, 14, '', total_format)
                    
                # Process other products
                for j, product in enumerate(products['other_products']):
                    product_data = category_summary_data_excel(request=request, pk=product.id)
                    pricing_type = get_product_pricing_type_excel(request=request, pk=product_data['main_product'].id)
                    data = merge_summary_count2(
                        request=request, pk=specification.id, version=estimation_version.id,
                        sqm=product_data['main_product'].product_sqm_price,
                        base_rate=product_data['main_product'].product_base_rate,
                        product=product_data['main_product'].id
                    )

                    # Write product row
                    current_row = header_title + row_counter - 1
                    worksheet.write(current_row, 0, j + 1, bold_red_center_format)

                    # Product name and details
                    product_name = get_product_name(request, product)
                    area_label0 = f"{product_data['aluminium_obj'].area} m²"
                    if not product_data['main_product'].category.is_curtain_wall:
                        area_label = f"{data['quantity']} Nº" if product_data['aluminium_obj'].total_quantity else '- Nº'
                    else:
                        area_label = f"{product_data['aluminium_obj'].total_quantity} Nº"
                    if product_data['main_product'].deduction_method == 2 and product_data['main_product'].deduction_price:
                        main_area = product_data['main_product'].total_associated_area
                        deduct_area = product_data['main_product'].deducted_area
                        quantity = data['quantity']
                        area_label2 = f"{float(main_area - deduct_area) * quantity:.2f} m²"
                    else:
                        area_label2 = f"{data['total_area']:.2f} m²"

                    product_details = f"{product_name}\n{area_label0} | {area_label} | {area_label2}"
                    worksheet.write(current_row, 1, product_details, text_format)

                    # Pricing type
                    pricing_type_value = pricing_type.get('al_pricing_type', '-')
                    type_label = {
                        'CUSTOM_KG': 'Kg', 'CUSTOM_UNIT': 'Unit', 'CUSTOM_SQM': 'SqM',
                        'PRE_UNIT': 'Unit', 'PRE_SQM': 'SqM', 'PRE_KG': 'Kg',
                        'FORMULA_KG': 'Kg'
                    }.get(pricing_type_value, 'SqM')
                    type_format = type_formats.get(pricing_type_value, type_formats['DEFAULT'])
                    worksheet.write(current_row, 2, type_label, type_format)

                    # Aluminium cost
                    aluminium_cost = f"{data['aluminium_rate']:.2f}" if product_data['aluminium_obj'].al_quoted_price else '-'
                    worksheet.write(current_row, 3, aluminium_cost, bold_red_format)

                    # Infill/Panel cost
                    glass_cost = f"{data['glass_rate']:.2f}" if product_data['glass_obj'] else '-'
                    worksheet.write(current_row, 4, glass_cost, bold_red_format)

                    # Accessories cost
                    accessory_cost = f"{data['accessory_price']:.2f}" if data['accessory_price'] else '-'
                    worksheet.write(current_row, 5, accessory_cost, bold_red_format)

                    # Sealant cost
                    silicon_cost = f"{data['silicon_price']:.2f}" if data['silicon_price'] else '-'
                    worksheet.write(current_row, 6, silicon_cost, bold_red_format)

                    # Material cost
                    material_cost = f"{data['material_cost']:.2f}" if product_data['material_total'] else '-'
                    worksheet.write(current_row, 7, material_cost, bold_red_format)

                    # Labor + Overhead
                    labour_overhead = f"{data['labour_overhead']:.2f}" if product_data['l_o'] else '-'
                    worksheet.write(current_row, 8, labour_overhead, bold_red_format)

                    # Sub Total
                    sub_total = f"{data['sub_total']:.2f}" if data['sub_total'] else '-'
                    worksheet.write(current_row, 9, sub_total, bold_red_format)

                    # Rate per m² (without add-ons)
                    rpm2 = f"{product_data['rate_per_sqm_without_addons']:.2f}" if product_data['rate_per_sqm_without_addons'] else '-'
                    worksheet.write(current_row, 10, rpm2, bold_red_format)

                    # Add-Ons cost
                    addon_cost = f"{data['addon_cost']:.2f}" if data['addon_cost'] else '-'
                    worksheet.write(current_row, 11, addon_cost, bold_red_format)

                    # Rate per Unit
                    rate_unit = '-'  # As per template
                    worksheet.write(current_row, 12, rate_unit, bold_red_format)

                    # Line Total
                    line_total = f"{data['round_total_price']:.2f}" if data['round_total_price'] else '-'
                    # sub_line_total += float(line_total) if line_total else 0
                    worksheet.write(current_row, 13, line_total, bold_red_format)

                    # Add-Ons Rate per m²
                    addon_rpm2 = f"{product_data['rate_per_sqm']:.2f}" if product_data['rate_per_sqm'] else '-'
                    worksheet.write(current_row, 14, addon_rpm2, bold_red_format)

                    row_counter += 1

                    # Add sub-rows for merged products if f_type is True
                    if f_type:
                        products_data = get_merge_products_excel(
                            request=request.path, category=product_data['main_product'].category.id, products=data['ids']
                        )
                        for k, sub_product in enumerate(products_data['product_data']):
                            sub_product_data = category_summary_data_excel(request=request, pk=sub_product[0].id)
                            sub_row = header_title + row_counter - 1

                            # Sub-row numbering
                            worksheet.write(sub_row, 0, f"{j + 1}.{k + 1}", muted_format)

                            # Sub-product details
                            sub_area_label = (
                                f"{sub_product_data['aluminium_obj'].product_type} | "
                                f"{sub_product_data['aluminium_obj'].width:.0f}*{sub_product_data['aluminium_obj'].height:.0f} | "
                                f"{sub_product_data['aluminium_obj'].area} m² | "
                                f"{sub_product_data['aluminium_obj'].total_quantity} Nº | "
                            )
                            if sub_product_data['main_product'].deduction_method == 2 and sub_product_data['main_product'].deduction_price:
                                main_area = sub_product_data['main_product'].total_associated_area
                                deduct_area = sub_product_data['main_product'].deducted_area
                                quantity = sub_product_data['aluminium_obj'].total_quantity
                                total_area = float(main_area - deduct_area) * float(quantity)
                                sub_area_label += f"TA: {total_area:.2f} m²"
                            else:
                                total_area = sub_product_data['aluminium_obj'].total_area
                                sub_area_label += f"TA: {total_area:.2f} m²"
                            worksheet.write(sub_row, 1, sub_area_label, text_format)
                            worksheet.write(sub_row, 2, '', text_format)  # Type column (empty for sub-row)

                            # Sub-row costs (muted if deduction method is applied)
                            format_to_use = muted_format if sub_product_data['main_product'].deduction_method else number_format
                            worksheet.write(sub_row, 3, sub_product_data['aluminium_obj'].al_quoted_price or '-', format_to_use)
                            glass_cost = sub_product_data['glass_obj'].glass_quoted_price if sub_product_data['glass_obj'] and sub_product_data['glass_obj'].is_glass_cost else '0.00'
                            worksheet.write(sub_row, 4, glass_cost, format_to_use)
                            worksheet.write(sub_row, 5, sub_product_data['total_access_price'] or '-', format_to_use)
                            worksheet.write(sub_row, 6, sub_product_data['silicon_total'] or '-', format_to_use)
                            worksheet.write(sub_row, 7, sub_product_data['material_total'] or '-', format_to_use)
                            worksheet.write(sub_row, 8, sub_product_data['l_o'] or '-', format_to_use)
                            worksheet.write(sub_row, 9, sub_product_data['sub_total'] or '-', format_to_use)
                            worksheet.write(sub_row, 10, sub_product_data['rate_per_sqm_without_addons'] or '-', format_to_use)
                            worksheet.write(sub_row, 11, sub_product_data['total_addon_cost'] or '-', format_to_use)
                            worksheet.write(sub_row, 12, sub_product_data['round_rate_per_unit'] or '-', format_to_use)
                            worksheet.write(sub_row, 13, sub_product_data['round_line_total'] or '-', format_to_use)
                            worksheet.write(sub_row, 14, sub_product_data['rate_per_sqm'] or '-', format_to_use)

                            row_counter += 1
                    
                    # total_row = header_title + row_counter
                    # worksheet.merge_range(f'A{total_row}:M{total_row}', 'Total for Section', total_format)
                    # worksheet.write(total_row, 13, sub_line_total, total_format)
                    # worksheet.write(total_row, 14, '', total_format)
                    # worksheet.write(row_counter+sub_row, 13, sub_line_total, bold_red_format)
                footer_row += 1

        # Finalize the workbook
        workbook.close()
        output.seek(0)
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={csv_file_name}.xlsx'
        return response
 
 

@shared_task(time_limit=600)
def scope_addons_summary_print(request, pk, temp=None):
    if not temp:
        estimation = Estimations.objects.get(pk=pk)
        addons_datas = MainProductAddonCost.objects.filter(estimation_product__building__estimation=estimation)\
            .values('estimation_product__category__category', 'addons__addon').annotate(
                        total_addon_quantity=Sum('addon_quantity')
                    )
    else:
        estimation = Temp_Estimations.objects.get(pk=pk)
        addons_datas = Temp_MainProductAddonCost.objects.filter(estimation_product__building__estimation=estimation)\
            .values('estimation_product__category__category', 'addons__addon').annotate(
                        total_addon_quantity=Sum('addon_quantity')
                    )
        
    context = {
        "estimation": estimation,
        "addons_datas": addons_datas,
    }
    template = get_template('print_templates/scope_summary/addon_summary_print.html')
    cmd_options = {
        'quiet': True, 
        'enable-local-file-access': True, 
        'margin-top': '30mm', 
        'header-spacing': 5,
        'minimum-font-size': 12,
        'page-size': 'A4',
        'encoding': "UTF-8",
        'print-media-type': True,
        'footer-right': "[page] / [topage]",
        'footer-font-size': 8,                    
    }
    # template = get_template('print_templates/scope_summary/specification_wise_scope_summary_print.html')

    file_names = "Scope Add-ons Summary "+str(['Original' if estimation.version.version == '0' else 'Revision '+str(
        estimation.version.version)][0])+" in "+str(estimation.enquiry.title)+'.pdf'
    clean_string  = re.sub(r'[^\w\s\-\.]', '', file_names)
    response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True,
                                    template=template, context=context)
    response = HttpResponse(response.rendered_content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename='+clean_string
    return response
    # return render(request, "Enquiries/scope_addons_summary.html", context)
    
    
@shared_task(time_limit=600)
def addons_data_export_shared(request, type):
    
    output = io.BytesIO()
    workbook = Workbook(output)
    worksheet = workbook.add_worksheet()
    addons_objs = Addons.objects.filter(activated=True)
    if type == 'xlsx':
        header = ['Add-ons', 'LM Price', 'SqM Price', 'Unit Price']
        for i, head in enumerate(header):
            worksheet.write(1, i, head, workbook.add_format({'bold': True}))

        for i, addons_obj in enumerate(addons_objs):
            worksheet.write(i+2, 0, addons_obj.addon)
            worksheet.write(i+2, 1, round(addons_obj.linear_meter, 2) if addons_obj.linear_meter else '-')
            worksheet.write(i+2, 2, round(addons_obj.sqm, 2) if addons_obj.sqm else '-')
            worksheet.write(i+2, 3, round(addons_obj.unit, 2) if addons_obj.unit else '-')

        workbook.close()
        output.seek(0)
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=Addons_Reference.xlsx'
        return response

    elif type == 'pdf':
        addons_objs = Addons.objects.filter(activated=True)
        company_obj = Companies.objects.all().first()
        context = {
            "addons_objs": addons_objs,
            "STATIC_URL": f'http://{str(request.get_host())}/{str(STATIC_URL)}',
            "MEDIA_URL": f'http://{str(request.get_host())}{str(MEDIA_URL)}',
            "company_obj": company_obj,
        }
        
        cmd_options = {
                    'quiet': True, 
                    'enable-local-file-access': True, 
                    'margin-top': '10mm', 
                    'header-spacing': 5,
                    'minimum-font-size': 16,
                    'page-size': 'A4',
                    'orientation': 'Landscape',
                    'encoding': "UTF-8",
                    'print-media-type': True,
                    'footer-right': "[page] / [topage]",
                    'footer-font-size': 8,
                }
        
        
        file_name = "Addons Reference.pdf"
        template = get_template('print_templates/addons_reference.html')
        response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=False, \
                    template=template, context=context)
        response = HttpResponse(response.rendered_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={file_name}'

        return response
        
    

def quotation_product_data_excel(request, pk):
    """
    This function calculates the cost and pricing information for a quotation product based on various
    inputs and returns the data in a dictionary format.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the user making the request and any data submitted with the request
    :param pk: The primary key of the EstimationMainProduct or Temp_EstimationMainProduct object being
    queried
    :return: a dictionary containing data related to a quotation product, including the main product,
    aluminium object, unit price, total price, and rate per square meter.
    """
    material_cost = 0
    labour_percent_price = 0
    overhead_percent_price = 0
    total_addon_cost = 0
    PATHS = [
                    '/Enquiries/view_quotations/', 
                    '/Enquiries/edit_quotation/', 
                    '/Estimation/quotation_by_boq_enquiry/',              
                    '/Estimation/quotation_print_by_customer/', 
                    '/Estimation/quotation_print/', 
                    '/Estimation/quotation_print_boq/',              
                    '/Estimation/quotation_print_by_customer_boq/', 
                    '/Enquiries/create_quotation_base/',
                    '/Estimation/building_price_print/',
                    '/Enquiries/new_quotaion_customers/',
                    '/Estimation/sync_quotation/',
                    '/Enquiries/get_customer_data/',
                    '/Estimation/submit_estimation/',
                    '/Estimation/estimation_quotations_list/',
                    '/Estimation/quotation_by_boq_enquiry/',
                    '/Estimation/quotation_unit_price/',
                    '/Estimation/quotation_excel_import_view/',

                ]

    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
        MainProductSiliconModel = MainProductSilicon
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
        MainProductSiliconModel = Temp_MainProductSilicon


    try:
        main_product = MainProduct.objects.get(pk=pk)
    except Exception:
        main_product = None
    try:
        aluminium_obj = AluminiumModel.objects.get(estimation_product=pk)
    except Exception:
        aluminium_obj = None
    try:
        glass_obj = MainProductGlassModel.objects.get(estimation_product=pk, glass_primary=True)
        second_glass_obj = MainProductGlassModel.objects.select_related('estimation_product').filter(estimation_product=pk, glass_primary=False)
    except Exception:
        glass_obj = None
        second_glass_obj = None
    try:
        silicon_obj = MainProductSiliconModel.objects.get(estimation_product=pk)
    except Exception:
        silicon_obj = None
    try:
        pricing_control = PricingOptionModel.objects.get(estimation_product=pk)
    except Exception as e:
        pricing_control = None

    if aluminium_obj and aluminium_obj.al_quoted_price:
        material_cost += float(aluminium_obj.al_quoted_price)
        
    if main_product.deduction_method == 2:
        deducted_area = float(aluminium_obj.area) - float(main_product.deducted_area)
        unit_area = round(deducted_area, 2)
    else:
        unit_area = round(float(aluminium_obj.area), 2)

    if glass_obj and (glass_obj.is_glass_cost and glass_obj.glass_quoted_price):
        material_cost += float(glass_obj.glass_quoted_price)

    if second_glass_obj:
        for second_glass in second_glass_obj:
            material_cost += float(second_glass.glass_quoted_price)

    if silicon_obj and silicon_obj.is_silicon:
        material_cost += float(silicon_obj.silicon_quoted_price)
    if main_product and (main_product.accessory_total and main_product.is_accessory):
        material_cost += float(main_product.accessory_total)
    if pricing_control:
        if pricing_control.labour_perce:
            labour_percentage = float(pricing_control.labour_perce)/100
            labour_percent_price = round(float(material_cost)*float(labour_percentage), 4)

        if pricing_control.overhead_perce:
            overhead_percentage = float(pricing_control.overhead_perce)/100
            overhead_percent_price = round(float(material_cost)*float(overhead_percentage), 4)

    sub_total = (material_cost+labour_percent_price+overhead_percent_price+float(main_product.total_addon_cost))
    
    if aluminium_obj.aluminium_pricing in [1, 2, 4]:
        if main_product:
            if main_product.is_tolerance and main_product.tolerance_type == 1:
                tolarance = int(main_product.tolerance) / 100
                tolarance_price = float(aluminium_obj.al_quoted_price) * tolarance
            elif main_product.is_tolerance and main_product.tolerance_type == 2:
                tolarance_price = main_product.tolerance
            else:
                tolarance_price = 0
        else:
            tolarance_price = 0
    else:
        tolarance_price = 0
        
    if not main_product.have_merge: 
        if not main_product.after_deduction_price:
            rpu = round((float(sub_total)+float(tolarance_price)), 2)
        else: 
            temp = float(main_product.after_deduction_price)
            rpu = round(temp, 2)

        total = (float(rpu)*float(aluminium_obj.total_quantity))
        round_total = round((math.ceil(float(rpu))*float(aluminium_obj.total_quantity)), 2)
        if main_product.after_deduction_price:
            rate_per_sqm = float(rpu)/(float(aluminium_obj.area)-float(main_product.deducted_area))
        else:
            rate_per_sqm = float(rpu)/float(aluminium_obj.area)
    else:
        rpu = float(round(main_product.merge_price, 2))
        total = float(main_product.merge_price)*float(aluminium_obj.total_quantity)
        round_total = math.ceil(float(main_product.merge_price)*float(aluminium_obj.total_quantity))
        if main_product.after_deduction_price:
            rate_per_sqm = float(rpu)/(float(aluminium_obj.area)-float(main_product.deducted_area))
        else:
            rate_per_sqm = float(rpu)/float(aluminium_obj.area)
    
    return {
        'main_product': main_product,
        'aluminium_obj': aluminium_obj,
        'rpu': round(rpu, 2),
        'round_rpu': math.ceil(round(rpu, 2)),
        'total': total,
        'round_total': round_total,
        'rate_per_sqm': math.ceil(round(rate_per_sqm, 2)),
        'unit_area': unit_area,
    }
    

def shift_letter(start_letter: str, shift: int) -> str:
    """Shift a capital letter by a given amount in the alphabet."""
    return chr(((ord(start_letter.upper()) - ord('A') + shift-1) % 26) + ord('A'))

# @shared_task(time_limit=600)
# def quotation_excel_import(request, pk):

#     PATHS = [
#         '/Enquiries/view_quotations/',
#         '/Estimation/quotation_excel_import_view/'
#     ]
    
#     if any(path in request.path for path in PATHS):
#         QuotationsModel = Quotations
#         EstimationBuildingsModel = EstimationBuildings
#         MainProductModel = EstimationMainProduct
#         AluminiumModel = MainProductAluminium
#     else:
#         QuotationsModel = Temp_Quotations
#         EstimationBuildingsModel = Temp_EstimationBuildings
#         MainProductModel = Temp_EstimationMainProduct
#         AluminiumModel = Temp_MainProductAluminium
        
#     quotations = QuotationsModel.objects.get(pk=pk)
#     buildings = EstimationBuildingsModel.objects.filter(
#             estimation=quotations.estimations, disabled=False).order_by('id')
#     csv_file_name = f'{quotations.quotation_id} | {quotations.estimations.enquiry.title}'
#     output = io.BytesIO()
#     workbook = Workbook(output)
#     worksheet = workbook.add_worksheet()
    
#     header = ['#', 'Product Description']
    
#     if quotations.is_dimensions:
#         header.append('Dimensions')
#     if quotations.is_area:
#         header.append('Area')
#     if quotations.is_quantity:
#         header.append('Qty')
#     if quotations.is_rpu:
#         header.append('RpU')
#     if quotations.is_rpsqm:
#         header.append('RpM²')
        
#     header.append('Total')
#     # header = ['#', 'Product Description', 'Dimensions', 'Area', 'Qty', 'RpU', 'RpM2', 'Total']
        
#     header_format = workbook.add_format({
#             'bold': True, 'font_color': 'white', 'align': 'start',
#             'valign': 'vcenter', 'fg_color': '#485699'
#         })
#     bold_red_center_format = workbook.add_format({
#             'bold': True, 'font_color': 'red', 'align': 'center'
#         })
#     text_format = workbook.add_format({'align': 'left'})
#     number_format = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
#     muted_format = workbook.add_format({'font_color': '#757575', 'align': 'right'})
#     total_format = workbook.add_format({
#         'bold': True, 'font_color': 'black', 'align': 'right',
#         'num_format': '#,##0.00', 'bg_color': '#D3D3D3'
#     })
    
#     for col, head in enumerate(header):
#         worksheet.write(0, col, head, header_format)
            
#     header_title = 2
#     footer_row = 0
#     row_counter = 0
#     end_point = shift_letter('A', len(header))
    
#     sub_total = 0
#     discount_value = 0
#     sub_row = 0
    
#     building_totals = []

#     for i, building_obj in enumerate(buildings):
#         title = f'{building_obj.building_name}'
#         building_row = header_title + row_counter
#         mergerange = f'A{building_row}:{end_point}{building_row}'
#         worksheet.merge_range(mergerange, title, header_format)
#         row_counter += 1
        
#         products_objs = MainProductModel.objects.filter(building=building_obj, product_type=1, disabled=False).order_by('product_index')
#         # Reset building total for this section
#         current_building_total = 0
        
#         for j, product in enumerate(products_objs):
            
#             try:
#                 aluminium_obj = AluminiumModel.objects.get(estimation_product=product)
#             except Exception as e:
#                 aluminium_obj = None
                
#             current_row = building_row + j  # Adjusted row calculation
#             worksheet.write(current_row, 0, j + 1, bold_red_center_format)

#             product_data = quotation_product_data_excel(request=request, pk=product.id)
            
#             name = display_product_name(request=request, pk=product.id)
#             product_label = (
#                 aluminium_obj.product_type + ' | ' + name if name else '' +
#                 ' | ' + aluminium_obj.product_description if aluminium_obj.product_description else '' +
#                 ' | ⚠️' if product.main_product.minimum_price > product_data['round_rpu'] else ''
#             )
#             worksheet.write(current_row, 1, product_label, text_format)
            
#             if quotations.is_dimensions:
#                 dim_col = header.index('Dimensions')
#                 dimensions_data = f'{product.display_width}' if product.main_product.category.handrail else (f'{round(product.main_product.display_width, 0)}' + '*' + f'{round(product.main_product.display_height, 0)}' if product.main_product.display_width and product.main_product.display_height else '-' if product.main_product.is_display_data else (f'{round(aluminium_obj.width, 0)}' + ' * ' + f'{round(aluminium_obj.height, 0)}' if not product.main_product.hide_dimension else '-'))
#                 worksheet.write(current_row, dim_col, dimensions_data, text_format)
                
#             if quotations.is_area:
#                 dim_col = header.index('Area')
#                 area_label = f'{product.unit_area} m²' if product.main_product.deduction_method == 1 or product.main_product.deduction_method == 2 else f'{product.main_product.display_area} m²' if product.main_product.is_display_data else f'{aluminium_obj.area} m²'
#                 worksheet.write(current_row, dim_col, area_label, number_format)
            
#             if quotations.is_quantity:
#                 dim_col = header.index('Qty')
#                 if product.main_product.is_display_data:
#                     qty_label = f'{product.main_product.display_quantity}' 
#                 elif aluminium_obj.total_quantity:
#                     qty_label = f'{aluminium_obj.total_quantity}' 
                    
#                 qty_uom = ' m²' if product.main_product.uom.uom == 'SqM' else f' {product.main_product.uom}'
#                 worksheet.write(current_row, dim_col, qty_label + qty_uom, number_format)
            
#             if quotations.is_rpu:
#                 dim_col = header.index('RpU')
#                 round_rpu_label = product_data['round_rpu']
#                 worksheet.write(current_row, dim_col, round_rpu_label, number_format)
                
#             if quotations.is_rpsqm:
#                 dim_col = header.index('RpM²')
#                 rate_per_sqm_label = product_data['rate_per_sqm']
#                 worksheet.write(current_row, dim_col, rate_per_sqm_label, number_format)
            
#             round_total_label = product_data['round_total']
#             current_building_total += float(round_total_label) 
        
#             flag_products = MainProductModel.objects.filter(main_product=product.id, product_type=2, main_product__have_merge=False)
            
#             for k, sub_product in enumerate(flag_products):
#                 print("sub_product==>", sub_product.id)
                
#                 try:
#                     aluminium_obj = AluminiumModel.objects.get(estimation_product=sub_product)
#                 except Exception as e:
#                     aluminium_obj = None
                
#                 sub_row = current_row + k + 1
#                 worksheet.write(sub_row, 0, f'{j + 1}.{k + 1}', muted_format)
                
#                 product_data = quotation_product_data_excel(request=request, pk=sub_product.id)
#                 print("SSSS==>", f'{j + 1}.{k + 1}')
#                 name = display_product_name(request=request, pk=sub_product.id)
#                 product_label = (
#                     aluminium_obj.product_type + ' | ' + name if name else '' +
#                     ' | ' + aluminium_obj.product_description if aluminium_obj.product_description else '' +
#                     ' | ⚠️' if sub_product.main_product.minimum_price > product_data['round_rpu'] else ''
#                 )
#                 worksheet.write(sub_row, 1, product_label, text_format)
                
#                 if quotations.is_dimensions:
#                     dim_col = header.index('Dimensions')
#                     dimensions_data = f'{sub_product.display_width}' if sub_product.main_product.category.handrail else (f'{round(sub_product.main_product.display_width, 0)}' + '*' + f'{round(sub_product.main_product.display_height, 0)}' if sub_product.main_product.display_width and sub_product.main_product.display_height else '-' if sub_product.main_product.is_display_data else (f'{round(aluminium_obj.width, 0)}' + ' * ' + f'{round(aluminium_obj.height, 0)}' if not sub_product.main_product.hide_dimension else '-'))
#                     worksheet.write(sub_row, dim_col, dimensions_data, text_format)
                    
#                 if quotations.is_area:
#                     dim_col = header.index('Area')
#                     area_label = f'{sub_product.unit_area} m²' if sub_product.main_product.deduction_method == 1 or sub_product.main_product.deduction_method == 2 else f'{sub_product.main_product.display_area} m²' if sub_product.main_product.is_display_data else f'{aluminium_obj.area} m²'
#                     worksheet.write(sub_row, dim_col, area_label, number_format)
                
#                 if quotations.is_quantity:
#                     dim_col = header.index('Qty')
#                     if sub_product.main_product.is_display_data:
#                         qty_label = f'{sub_product.main_product.display_quantity}' 
#                     elif aluminium_obj.total_quantity:
#                         qty_label = f'{aluminium_obj.total_quantity}' 
                        
#                     qty_uom = ' m²' if sub_product.main_product.uom.uom == 'SqM' else f' {sub_product.main_product.uom}'
#                     worksheet.write(sub_row, dim_col, qty_label + qty_uom, number_format)
                
#                 if quotations.is_rpu:
#                     dim_col = header.index('RpU')
#                     round_rpu_label = product_data['round_rpu']
#                     worksheet.write(sub_row, dim_col, round_rpu_label, number_format)
                    
#                 if quotations.is_rpsqm:
#                     dim_col = header.index('RpM²')
#                     rate_per_sqm_label = product_data['rate_per_sqm']
#                     worksheet.write(sub_row, dim_col, rate_per_sqm_label, number_format)
                
#                 round_total_label = product_data['round_total']
#                 current_building_total += float(round_total_label) 
#                 # dim_col = header.index('Total')
#                 # worksheet.write(sub_row, dim_col, round_total_label, number_format)
                
#                 sub_row += 1
            
#             dim_col = header.index('Total')
#             worksheet.write(current_row+sub_row, dim_col, round_total_label, number_format)
#             row_counter += 1
            
#         # After processing all products for this building, add subtotal row
#         subtotal_row = building_row + len(products_objs)
#         worksheet.write(subtotal_row, len(header)-2, 'Total', bold_red_center_format)
#         worksheet.write(subtotal_row, len(header)-1, current_building_total, total_format)
#         sub_total += current_building_total
#         # Store the building total for the final total
#         building_totals.append(current_building_total)
        
#         # Add an extra row after the subtotal for spacing
#         row_counter += 2
#         building_row = header_title + row_counter

#     sub_total_row = header_title + row_counter
#     worksheet.write(sub_total_row, len(header)-2, 'Subtotal', bold_red_center_format)
#     sub_total = sum(building_totals)
#     worksheet.write(sub_total_row, len(header)-1, sub_total, total_format)

#     discount_row = header_title + row_counter + 1
#     discount_label = quotations.discount
#     if quotations.discount_type == 0:
#         discount_row -= 1
#     elif quotations.discount_type == 1:
#         discount_label_type = '%'
#         discount_value = (sub_total/discount_label)

#     elif quotations.discount_type == 2:
#         discount_label_type = 'QAR'
#         discount_value = discount_label

#     if not quotations.discount_type == 0:
#         dis_lab = str(round(int(quotations.discount), 0)) + discount_label_type if quotations.discount_type == 1 else ''
#         worksheet.write(discount_row, len(header)-2, f'Discount {dis_lab}', bold_red_center_format)
#         worksheet.write(discount_row, len(header)-1, discount_value, total_format)


#     grand_total = sub_total - discount_value

#     worksheet.write(discount_row+1, len(header)-2, f'Grand Total', bold_red_center_format)
#     worksheet.write(discount_row+1, len(header)-1, grand_total, total_format)

#     workbook.close()
#     output.seek(0)
#     safe_filename = urllib.parse.quote(f'{csv_file_name}.xlsx')
    
#     response = HttpResponse(
#         output,
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )
#     response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{safe_filename}'
#     return response




@shared_task(time_limit=600)
def quotation_excel_import(request, pk):
    PATHS = [
        '/Enquiries/view_quotations/',
        '/Estimation/quotation_excel_import_view/'
    ]
    
    if any(path in request.path for path in PATHS):
        QuotationsModel = Quotations
        EstimationBuildingsModel = EstimationBuildings
        MainProductModel = EstimationMainProduct
        AluminiumModel = MainProductAluminium
    else:
        QuotationsModel = Temp_Quotations
        EstimationBuildingsModel = Temp_EstimationBuildings
        MainProductModel = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
    
    try:
        quotation = QuotationsModel.objects.get(pk=pk)
    except QuotationsModel.DoesNotExist:
        return HttpResponse("Quotation not found", status=404)

    buildings = EstimationBuildingsModel.objects.filter(
        estimation=quotation.estimations, 
        disabled=False
    ).order_by('id')
    
    csv_file_name = f'{quotation.quotation_id} | {quotation.estimations.enquiry.title}'
    output = io.BytesIO()
    workbook = Workbook(output)
    worksheet = workbook.add_worksheet()
    
    header = ['#', 'Product Type', 'Product Name', 'Description']
    
    if quotation.is_dimensions:
        header.append('Dimensions')
    if quotation.is_area:
        header.append('Area')
    if quotation.is_quantity:
        header.append('Qty')
    if quotation.is_rpu:
        header.append('RpU')
    if quotation.is_rpsqm:
        header.append('RpM²')
    header.append('Total')
    
    header_format = workbook.add_format({
        'bold': True, 'font_color': 'white', 'align': 'start',
        'valign': 'vcenter', 'fg_color': '#485699'
    })
    bold_red_center_format = workbook.add_format({
        'bold': True, 'font_color': 'red', 'align': 'center'
    })
    text_format = workbook.add_format({'align': 'left'})
    number_format = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
    muted_format = workbook.add_format({'font_color': '#757575', 'align': 'right'})
    total_format = workbook.add_format({
        'bold': True, 'font_color': 'black', 'align': 'right',
        'num_format': '#,##0.00', 'bg_color': '#D3D3D3'
    })
    
    for col, head in enumerate(header):
        worksheet.write(0, col, head, header_format)
    
    row_counter = 2
    building_totals = []
    total_col = header.index('Total')
    
    for i, building in enumerate(buildings):
        worksheet.merge_range(f'A{row_counter}:{chr(65 + len(header) - 1)}{row_counter}', 
                            f'{building.building_name}', header_format)
        row_counter += 1
        
        products = MainProductModel.objects.filter(
            building=building, 
            product_type=1, 
            disabled=False
        ).order_by('product_index')
        
        building_total = 0
        item_counter = 0  # Continuous counter for this building
        
        for j, product in enumerate(products):
            item_counter += 1
            current_row = row_counter
            worksheet.write(current_row, 0, item_counter, bold_red_center_format)
            
            aluminium_obj = AluminiumModel.objects.filter(estimation_product=product).first()
            product_data = quotation_product_data_excel(request=request, pk=product.id)
            name = display_product_name(request=request, pk=product.id)
            # product_label = (
            #     aluminium_obj.product_type + ' | ' + name if name else '' +
            #     ' | ' + aluminium_obj.product_description if aluminium_obj.product_description else '' +
            #     ' | ⚠️' if product.main_product.minimum_price > product_data['round_rpu'] else ''
            # )
            product_label = (
                name if name else '' + ' | ⚠️' if product.main_product.minimum_price > product_data['round_rpu'] else ''
            )
            
            worksheet.write(current_row, 1, aluminium_obj.product_type, text_format)
            worksheet.write(current_row, 2, product_label, text_format)
            
            product_descr = aluminium_obj.product_description if aluminium_obj and aluminium_obj.product_description else ''
            worksheet.write(current_row, 3, product_descr, text_format)
            
            col_offset = 4
            if quotation.is_dimensions:
                dimensions = (
                    f"{product.display_width}" if product.category.handrail else
                    f"{round(product.display_width, 0)}*{round(product.display_height, 0)}" 
                    if product.display_width and product.display_height else
                    "-" if product.is_display_data else
                    f"{round(aluminium_obj.width, 0)}*{round(aluminium_obj.height, 0)}" 
                    if aluminium_obj and not product.hide_dimension else "-"
                )
                worksheet.write(current_row, col_offset, dimensions, text_format)
                col_offset += 1
                
            if quotation.is_area:
                area = (
                    f"{product.unit_area} m²" if product.deduction_method in [1, 2] else
                    f"{product.display_area} m²" if product.is_display_data else
                    f"{aluminium_obj.area} m²" if aluminium_obj else "0 m²"
                )
                worksheet.write(current_row, col_offset, area, number_format)
                col_offset += 1
                
            if quotation.is_quantity:
                qty = (
                    f"{product.display_quantity}" if product.is_display_data else
                    f"{aluminium_obj.total_quantity}" if aluminium_obj and aluminium_obj.total_quantity else "0"
                )
                qty_uom = " m²" if product.uom.uom == 'SqM' else f" {product.uom}"
                worksheet.write(current_row, col_offset, qty + qty_uom, number_format)
                col_offset += 1
                
            if quotation.is_rpu:
                worksheet.write(current_row, col_offset, product_data['round_rpu'], number_format)
                col_offset += 1
                
            if quotation.is_rpsqm:
                worksheet.write(current_row, col_offset, product_data['rate_per_sqm'], number_format)
                col_offset += 1
                
            total = float(product_data['round_total'])
            building_total += total
            worksheet.write(current_row, total_col, total, number_format)
            
            row_counter += 1
            
            sub_products = MainProductModel.objects.filter(
                main_product=product,
                product_type=2,
                main_product__have_merge=False
            )
            
            for k, sub_product in enumerate(sub_products):
                item_counter += 1
                sub_row = row_counter
                worksheet.write(sub_row, 0, item_counter, bold_red_center_format)
                
                aluminium_sub = AluminiumModel.objects.filter(estimation_product=sub_product).first()
                sub_data = quotation_product_data_excel(request=request, pk=sub_product.id)
                sub_name = display_product_name(request=request, pk=sub_product.id)
                
                # sub_label = (
                #     aluminium_sub.product_type + ' | ' + sub_name if sub_name else '' +
                #     ' | ' + aluminium_sub.product_description if aluminium_sub.product_description else '' +
                #     ' | ⚠️' if sub_product.main_product.minimum_price > sub_data['round_rpu'] else ''
                # )
                sub_label = (
                    sub_name if sub_name else '' +
                    ' | ⚠️' if sub_product.main_product.minimum_price > sub_data['round_rpu'] else ''
                )
                worksheet.write(sub_row, 1, aluminium_sub.product_type, text_format)
                worksheet.write(sub_row, 2, sub_label, text_format)
                
                sub_product_descr = f'{aluminium_sub.product_description}' if aluminium_sub.product_description else ''
                worksheet.write(sub_row, 3, sub_product_descr, text_format)
                
                col_offset = 4
                if quotation.is_dimensions:
                    sub_dims = (
                        f"{sub_product.display_width}" if sub_product.category.handrail else
                        f"{round(sub_product.display_width, 0)}*{round(sub_product.display_height, 0)}" 
                        if sub_product.display_width and sub_product.display_height else
                        "-" if sub_product.is_display_data else
                        f"{round(aluminium_sub.width, 0)}*{round(aluminium_sub.height, 0)}" 
                        if aluminium_sub and not sub_product.hide_dimension else "-"
                    )
                    worksheet.write(sub_row, col_offset, sub_dims, text_format)
                    col_offset += 1
                    
                if quotation.is_area:
                    sub_area = (
                        f"{sub_product.unit_area} m²" if sub_product.deduction_method in [1, 2] else
                        f"{sub_product.display_area} m²" if sub_product.is_display_data else
                        f"{aluminium_sub.area} m²" if aluminium_sub else "0 m²"
                    )
                    worksheet.write(sub_row, col_offset, sub_area, number_format)
                    col_offset += 1
                    
                if quotation.is_quantity:
                    sub_qty = (
                        f"{sub_product.display_quantity}" if sub_product.is_display_data else
                        f"{aluminium_sub.total_quantity}" if aluminium_sub and aluminium_sub.total_quantity else "0"
                    )
                    sub_uom = " m²" if sub_product.uom.uom == 'SqM' else f" {sub_product.uom}"
                    worksheet.write(sub_row, col_offset, sub_qty + sub_uom, number_format)
                    col_offset += 1
                    
                if quotation.is_rpu:
                    worksheet.write(sub_row, col_offset, sub_data['round_rpu'], number_format)
                    col_offset += 1
                    
                if quotation.is_rpsqm:
                    worksheet.write(sub_row, col_offset, sub_data['rate_per_sqm'], number_format)
                    col_offset += 1
                    
                sub_total = float(sub_data['round_total'])
                building_total += sub_total
                worksheet.write(sub_row, total_col, sub_total, number_format)
                
                row_counter += 1
        
        subtotal_row = row_counter
        worksheet.write(subtotal_row, len(header)-2, 'Total', bold_red_center_format)
        worksheet.write(subtotal_row, len(header)-1, building_total, total_format)
        building_totals.append(building_total)
        row_counter += 2
    
    sub_total = sum(building_totals)
    discount_value = 0
    
    worksheet.write(row_counter, len(header)-2, 'Subtotal', bold_red_center_format)
    worksheet.write(row_counter, len(header)-1, sub_total, total_format)
    row_counter += 1
    
    if quotation.discount_type == 1:
        discount_value = sub_total * (quotation.discount / 100)
        worksheet.write(row_counter, len(header)-2, f'Discount {round(quotation.discount, 0)}%', 
                       bold_red_center_format)
        worksheet.write(row_counter, len(header)-1, discount_value, total_format)
        row_counter += 1
    elif quotation.discount_type == 2:
        discount_value = float(quotation.discount or 0)
        worksheet.write(row_counter, len(header)-2, 'Discount QAR', 
                       bold_red_center_format)
        worksheet.write(row_counter, len(header)-1, discount_value, total_format)
        row_counter += 1
    
    grand_total = sub_total - discount_value
    worksheet.write(row_counter, len(header)-2, 'Grand Total', bold_red_center_format)
    worksheet.write(row_counter, len(header)-1, grand_total, total_format)
    
    workbook.close()
    output.seek(0)
    safe_filename = urllib.parse.quote(f'{csv_file_name}.xlsx')
    
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{safe_filename}'
    return response







