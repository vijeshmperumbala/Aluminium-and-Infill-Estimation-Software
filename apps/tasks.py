
# from celery import Celery, shared_task
import math
# from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, FileResponse
from apps.enquiries.models import (
    Estimations, 
    Temp_EnquirySpecifications, 
    Temp_Estimations
    )
from apps.estimations.models import (
    EstimationMainProduct, 
    MainProductAccessories, 
    MainProductAluminium, 
    MainProductGlass, 
    MainProductAddonCost, 
    MainProductSilicon, 
    PricingOption, 
    EstimationBuildings, 
    Temp_EstimationBuildings, 
    Temp_EstimationMainProduct, 
    Temp_MainProductAccessories, 
    Temp_MainProductAddonCost, 
    Temp_MainProductAluminium, 
    Temp_MainProductGlass, 
    Temp_MainProductSecondtaryGlass, 
    Temp_MainProductSilicon,
    Temp_PricingOption, 
    Temp_ProductComments, 
    Temp_Quotation_Provisions, 
    Temp_Quotations
    )
from django.utils.timezone import now as time
from django.utils import dateformat
import math
from django.utils.encoding import smart_str


import csv
from apps.suppliers.models import BillofQuantity

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.tables import Table,TableStyle,colors
from reportlab.lib.styles import getSampleStyleSheet


# @shared_task
# def custom_export_csv_estimation_socpe(estimation_id):
#     buildings = EstimationBuildings.objects.filter(estimation=estimation_id)
#     estimation = Estimations.objects.get(pk=estimation_id)
#     # csv_file_name = str(estimation.enquiry)+'_'+dateformat.format(time(), 'd-m-Y')
#     csv_file_name = str(estimation.enquiry)
#     header = ['Product', 'Dimension', 'Area Per Unit', 'Quantity', 'Total Area per Unit', 'Rate per Unit', 'Rate per Meter', 'Total Price']
    
#     with open(csv_file_name+'.csv', 'w', encoding='UTF8') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(header)
        
#         for building in buildings:
#             writer.writerow([building.building_name])
#             main_product = EstimationMainProduct.objects.filter(building=building).order_by('id')
#             for i, products in enumerate(main_product):
#                 building_name = building.building_name
#                 aluminium_obj = MainProductAluminium.objects.get(estimation_product=products)
#                 try:
#                     glass_obj = MainProductGlass.objects.get(estimation_product=products, glass_primary=True)
#                 except Exception as e:
#                     glass_obj = None
#                 try:
#                     second_glass_obj = MainProductGlass.objects.filter(estimation_product=products, glass_primary=False)
#                 except Exception as e:
#                     second_glass_obj = None
#                 try:
#                     silicon_obj = MainProductSilicon.objects.get(estimation_product=products)
#                 except Exception as e:
#                     silicon_obj = None
#                 try:
#                     addons = MainProductAddonCost.objects.filter(estimation_product=products)
#                 except Exception as e:
#                     addons = None
#                 pricing_control = PricingOption.objects.get(estimation_product=products)
#                 unit_price = 0
#                 labour_percentage = 0
#                 labour_percent_price = 0
#                 overhead_percentage = 0
#                 overhead_percent_price = 0
#                 unit_total_price = 0
#                 tolarance = 0
#                 tolarance_price = 0
#                 estimated_value = 0
#                 total_price = 0
#                 quantity = 0
#                 unit_area = 0
#                 total_area = 0
#                 dimension = 0
#                 silicon_price = 0
#                 if aluminium_obj:
#                     dimension = str(int(aluminium_obj.width)) + '*' + str(int(aluminium_obj.height))
#                     unit_area = (int(aluminium_obj.width) * int(aluminium_obj.height))/1000000
#                     quantity = aluminium_obj.total_quantity
#                     total_area = float(unit_area) * float(quantity)
#                     if aluminium_obj.al_quoted_price:
#                         unit_price += float(aluminium_obj.al_quoted_price)

#                 if glass_obj:
#                     if glass_obj.is_glass_cost:
#                         if glass_obj.glass_quoted_price:
#                             unit_price += float(glass_obj.glass_quoted_price)
#                 if second_glass_obj:
#                     for second_glass in second_glass_obj:
#                         if second_glass.glass_quoted_price:
#                             unit_price += float(second_glass.glass_quoted_price)
#                 if silicon_obj:
#                     if silicon_obj.is_silicon:
#                         unit_price += float(silicon_obj.silicon_quoted_price)
#                 if products:
#                     if products.accessory_total and products.is_accessory:
#                         unit_price += float(products.accessory_total)
#                     if pricing_control:
#                         if pricing_control.labour_perce:
#                             labour_percentage = float(pricing_control.labour_perce)/100
#                             labour_percent_price = round((float(unit_price)*float(labour_percentage)), 2)
#                         if pricing_control.overhead_perce:
#                             overhead_percentage = float(pricing_control.overhead_perce)/100
#                             overhead_percent_price = round((float(unit_price)*float(overhead_percentage)), 2)

#                     if aluminium_obj.aluminium_pricing == 1 or aluminium_obj.aluminium_pricing == 2:
#                         if products.is_tolerance:
#                             if products.tolerance_type == 1:
#                                 tolarance = int(products.tolerance)/100
#                                 tolarance_price = float(aluminium_obj.al_quoted_price)*tolarance
#                             elif products.tolerance_type == 2:
#                                 tolarance_price = float(products.tolerance)
#                             else:
#                                 tolarance_price = 0
#                     else:
#                         tolarance_price = 0 
#                     estimated_value = float(math.ceil(unit_price))+float(overhead_percent_price)+float(labour_percent_price)+float(tolarance_price)+float(products.total_addon_cost)
#                     total_price = math.ceil(float(estimated_value))*int(quantity)

#                 try:
#                     rp_sqm = total_price/total_area
#                 except Exception as e:
#                     rp_sqm = 0
#                 if products.product:
#                     writer.writerow([aluminium_obj.product_type + ' | ' + products.product.product_name, dimension, aluminium_obj.area, aluminium_obj.total_quantity, aluminium_obj.total_area, math.ceil(round(estimated_value, 2)), round(rp_sqm, 2), math.ceil(round(total_price, 2))])
#                 else:
#                     writer.writerow([aluminium_obj.product_type + ' | ' + products.product.panel_product, dimension, aluminium_obj.area, aluminium_obj.total_quantity, aluminium_obj.total_area, math.ceil(round(estimated_value, 2)), round(rp_sqm, 2), math.ceil(round(total_price, 2))])
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename='+csv_file_name+'.csv' 
#     return response


# @shared_task
# def custom_export_pdf_estimation_socpe(estimation_id):
#     buildings = EstimationBuildings.objects.filter(estimation=estimation_id)
#     estimation = Estimations.objects.get(pk=estimation_id)
#     csv_file_name = str(estimation.enquiry)+'_'+dateformat.format(time(), 'd-m-Y')
#     header = ['Product', 'Dimension', 'Area Per Unit', 'Quantity', 'Total Area per Unit', 'Rate per Unit', 'Rate per Meter', 'Total Price']
#     # create a CSV file
#     my_path = csv_file_name+'.pdf'
#     my_doc=SimpleDocTemplate(my_path,pagesize=landscape(A4))
#     c_width=[2*inch,1*inch,1*inch,1*inch, 1*inch]
#     # c_width=[2*inch,0.5*inch,1*inch,0.5*inch, 0.5*inch]
    
#     t=Table(header,rowHeights=20,repeatRows=1,colWidths=c_width)
    
#     my_data = [header, ]
    
#     for building in buildings:
#         main_product = EstimationMainProduct.objects.filter(building=building).order_by('id')
#         my_data.append((building.building_name, ))
#         for i, products in enumerate(main_product):
#             building_name = building.building_name
#             aluminium_obj = MainProductAluminium.objects.get(estimation_product=products)
#             try:
#                 glass_obj = MainProductGlass.objects.get(estimation_product=products, glass_primary=True)
#             except Exception as e:
#                 glass_obj = None
#             try:
#                 second_glass_obj = MainProductGlass.objects.filter(estimation_product=products, glass_primary=False)
#             except Exception as e:
#                 second_glass_obj = None
#             try:
#                 silicon_obj = MainProductSilicon.objects.get(estimation_product=products)
#             except Exception as e:
#                 silicon_obj = None
#             try:
#                 addons = MainProductAddonCost.objects.filter(estimation_product=products)
#             except Exception as e:
#                 addons = None
#             pricing_control = PricingOption.objects.get(estimation_product=products)
#             unit_price = 0
#             labour_percentage = 0
#             labour_percent_price = 0
#             overhead_percentage = 0
#             overhead_percent_price = 0
#             unit_total_price = 0
#             tolarance = 0
#             tolarance_price = 0
#             estimated_value = 0
#             total_price = 0
#             quantity = 0
#             unit_area = 0
#             total_area = 0
#             dimension = 0
#             silicon_price = 0
#             if aluminium_obj:
#                 dimension = str(int(aluminium_obj.width)) + '*' + str(int(aluminium_obj.height))
#                 unit_area = (int(aluminium_obj.width) * int(aluminium_obj.height))/1000000
#                 quantity = aluminium_obj.total_quantity
#                 total_area = float(unit_area) * float(quantity)
#                 if aluminium_obj.al_quoted_price:
#                     unit_price += float(aluminium_obj.al_quoted_price)

#             if glass_obj:
#                 if glass_obj.is_glass_cost:
#                     if glass_obj.glass_quoted_price:
#                         unit_price += float(glass_obj.glass_quoted_price)
#             if second_glass_obj:
#                 for second_glass in second_glass_obj:
#                     if second_glass.glass_quoted_price:
#                         unit_price += float(second_glass.glass_quoted_price)
#             if silicon_obj:
#                 if silicon_obj.is_silicon:
#                     unit_price += float(silicon_obj.silicon_quoted_price)
#             if products:
#                 if products.accessory_total and products.is_accessory:
#                     unit_price += float(products.accessory_total)
#                 if pricing_control:
#                     if pricing_control.labour_perce:
#                         labour_percentage = float(pricing_control.labour_perce)/100
#                         labour_percent_price = round((float(unit_price)*float(labour_percentage)), 2)
#                     if pricing_control.overhead_perce:
#                         overhead_percentage = float(pricing_control.overhead_perce)/100
#                         overhead_percent_price = round((float(unit_price)*float(overhead_percentage)), 2)

#                 if aluminium_obj.aluminium_pricing == 1 or aluminium_obj.aluminium_pricing == 2:
#                     if products.is_tolerance:
#                         if products.tolerance_type == 1:
#                             tolarance = int(products.tolerance)/100
#                             tolarance_price = float(aluminium_obj.al_quoted_price)*tolarance
#                         elif products.tolerance_type == 2:
#                             tolarance_price = float(products.tolerance)
#                         else:
#                             tolarance_price = 0
#                 else:
#                     tolarance_price = 0 
#                 estimated_value = float(math.ceil(unit_price))+float(overhead_percent_price)+float(labour_percent_price)+float(tolarance_price)+float(products.total_addon_cost)
#                 total_price = math.ceil(float(estimated_value))*int(quantity)

#             try:
#                 rp_sqm = total_price/total_area
#             except Exception as e:
#                 rp_sqm = 0
#             if products.product:
#                 my_data.append((aluminium_obj.product_type + ' | ' + products.product.product_name, dimension, aluminium_obj.area, aluminium_obj.total_quantity, aluminium_obj.total_area, math.ceil(round(estimated_value, 2)), round(rp_sqm, 2), math.ceil(round(total_price, 2))))
#             else:
#                 my_data.append(aluminium_obj.product_type + ' | ' + products.product.product_name, dimension, aluminium_obj.area, aluminium_obj.total_quantity, aluminium_obj.total_area, math.ceil(round(estimated_value, 2)), round(rp_sqm, 2), math.ceil(round(total_price, 2)))
#     t=Table(my_data,rowHeights=20,repeatRows=1,colWidths=c_width)
#     t.setStyle(TableStyle(
#         [
#             ('BACKGROUND',(0,0),(-1,0),colors.red),
#             ('FONTSIZE',(0,0),(-1,-1),10),
#             ('GRID', (0,0), (-1,-1), 0.25, colors.red),
#             ('ALIGN',(1,1),(-2,-2),'RIGHT'),
#             # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
#             ('BOX', (0,0), (-1,-1), 0.25, colors.red),
#             # ('SPAN', (0, 1), (7,1))
#         ]))
#     s = getSampleStyleSheet() 
#     style_normal = s['Normal']
#     s = s["BodyText"]
#     s.wordWrap = 'LTR'
#     elements=[]
#     elements.append(t)
#     # elements.append(Paragraph(t, style_normal))
#     # elements.append(Spacer(inch, .25*inch))
#     my_doc.build(elements)
#     return None


# def custom_export_csv_estimation_scope_boq(enquiry_id):
#     boqs = BillofQuantity.objects.filter(enquiry=enquiry_id)
#     header = ['Product', 'Dimension', 'Area Per Unit', 'Quantity', 'Total Area per Unit', 'Rate per Unit', 'Rate per Meter', 'Total Price']
#     csv_file_name = 'BOQ.csv'
#     with open(csv_file_name, 'w', encoding='UTF8') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(header)
#         for boq in boqs:
#             main_product = EstimationMainProduct.objects.filter(boq_number__boq_number=boq.boq_number)
#             for i, products in enumerate(main_product):
#                 # building_name = building.building_name
#                 aluminium_obj = MainProductAluminium.objects.get(estimation_product=products)
#                 try:
#                     glass_obj = MainProductGlass.objects.get(estimation_product=products, glass_primary=True)
#                 except Exception as e:
#                     glass_obj = None
#                 try:
#                     second_glass_obj = MainProductGlass.objects.filter(estimation_product=products, glass_primary=False)
#                 except Exception as e:
#                     second_glass_obj = None
#                 try:
#                     silicon_obj = MainProductSilicon.objects.get(estimation_product=products)
#                 except Exception as e:
#                     silicon_obj = None
#                 try:
#                     addons = MainProductAddonCost.objects.filter(estimation_product=products)
#                 except Exception as e:
#                     addons = None
#                 pricing_control = PricingOption.objects.get(estimation_product=products)
#                 unit_price = 0
#                 labour_percentage = 0
#                 labour_percent_price = 0
#                 overhead_percentage = 0
#                 overhead_percent_price = 0
#                 unit_total_price = 0
#                 tolarance = 0
#                 tolarance_price = 0
#                 estimated_value = 0
#                 total_price = 0
#                 quantity = 0
#                 unit_area = 0
#                 total_area = 0
#                 dimension = 0
#                 silicon_price = 0
#                 if aluminium_obj:
#                     dimension = str(int(aluminium_obj.width)) + '*' + str(int(aluminium_obj.height))
#                     unit_area = (int(aluminium_obj.width) * int(aluminium_obj.height))/1000000
#                     quantity = aluminium_obj.total_quantity
#                     total_area = float(unit_area) * float(quantity)
#                     if aluminium_obj.al_quoted_price:
#                         unit_price += float(aluminium_obj.al_quoted_price)

#                 if glass_obj:
#                     if glass_obj.is_glass_cost:
#                         if glass_obj.glass_quoted_price:
#                             unit_price += float(glass_obj.glass_quoted_price)
#                 if second_glass_obj:
#                     for second_glass in second_glass_obj:
#                         if second_glass.glass_quoted_price:
#                             unit_price += float(second_glass.glass_quoted_price)
#                 if silicon_obj:
#                     if silicon_obj.is_silicon:
#                         unit_price += float(silicon_obj.silicon_quoted_price)
#                 if products:
#                     if products.accessory_total and products.is_accessory:
#                         unit_price += float(products.accessory_total)
#                     if pricing_control:
#                         if pricing_control.labour_perce:
#                             labour_percentage = float(pricing_control.labour_perce)/100
#                             labour_percent_price = round((float(unit_price)*float(labour_percentage)), 2)
#                         if pricing_control.overhead_perce:
#                             overhead_percentage = float(pricing_control.overhead_perce)/100
#                             overhead_percent_price = round((float(unit_price)*float(overhead_percentage)), 2)

#                     if aluminium_obj.aluminium_pricing == 1 or aluminium_obj.aluminium_pricing == 2:
#                         if products.is_tolerance:
#                             if products.tolerance_type == 1:
#                                 tolarance = int(products.tolerance)/100
#                                 tolarance_price = float(aluminium_obj.al_quoted_price)*tolarance
#                             elif products.tolerance_type == 2:
#                                 tolarance_price = float(products.tolerance)
#                             else:
#                                 tolarance_price = 0
#                     else:
#                         tolarance_price = 0 
#                     estimated_value = float(math.ceil(unit_price))+float(overhead_percent_price)+float(labour_percent_price)+float(tolarance_price)+float(products.total_addon_cost)
#                     total_price = math.ceil(float(estimated_value))*int(quantity)

#                 try:
#                     rp_sqm = total_price/total_area
#                 except Exception as e:
#                     rp_sqm = 0
#                 if products.product:
#                     writer.writerow([aluminium_obj.product_type + ' | ' + products.product.product_name, dimension, aluminium_obj.area, aluminium_obj.total_quantity, aluminium_obj.total_area, math.ceil(round(estimated_value, 2)), round(rp_sqm, 2), math.ceil(round(total_price, 2))])
#                 else:
#                     writer.writerow([aluminium_obj.product_type + ' | ' + products.product.panel_product, dimension, aluminium_obj.area, aluminium_obj.total_quantity, aluminium_obj.total_area, math.ceil(round(estimated_value, 2)), round(rp_sqm, 2), math.ceil(round(total_price, 2))])
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename='+csv_file_name+'.csv' 
#     return response



