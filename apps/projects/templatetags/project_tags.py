from django import template
from datetime import datetime, timedelta

from apps.Categories.models import Category
from apps.helper import sum_times
from apps.projects.models import ApprovalNotes, Eps_Products, ProjectApprovalStatus, ProjectApprovalTypes, ProjectSepcificationsApproval, SalesOrderAddons, SalesOrderGroups, SalesOrderItems, SalesOrderSpecification, SalesSecondarySepcPanels, Workstation_Data

register = template.Library()


@register.simple_tag
def category_wise_products(pk, project_id, types):
    if types == 'category':
        product_objs = SalesOrderItems.objects.filter(category=pk, specification_Identifier__project=project_id, product_type__in=[1, 2])
        
    elif types == 'elevation':
        product_objs = SalesOrderItems.objects.filter(elevation=pk, specification_Identifier__project=project_id, product_type__in=[1, 2])
    elif types == 'building':
        product_objs = SalesOrderItems.objects.filter(building=pk, specification_Identifier__project=project_id, product_type__in=[1, 2])
    elif types == 'floor_obj':
        product_objs = SalesOrderItems.objects.filter(floor=pk, specification_Identifier__project=project_id, product_type__in=[1, 2])
        
        
    return product_objs

@register.simple_tag
def salesorder_addons(pk):
    product_obj = SalesOrderItems.objects.get(pk=pk)
    addons_objs = SalesOrderAddons.objects.filter(product=product_obj)
    return addons_objs

@register.simple_tag
def get_secondary_products(pk):
    secondary_product_objs = SalesOrderItems.objects.filter(main_product=pk, product_type=3)
    # secondary_product_objs = SalesOrderItems_Secondary_Product.objects.filter(main_product=product_obj)
    
    return secondary_product_objs

@register.simple_tag
def check_product_in_cart(pk):
    try:
        old_eps_product = Eps_Products.objects.filter(eps_product=pk, eps_data__isnull=True)
    except Exception as e:
        old_eps_product = None

    return old_eps_product

@register.simple_tag
def spec_approve_status(spec, approve_type):
    try:
        spec_obj = ProjectSepcificationsApproval.objects.get(specification=spec, approve_type=approve_type)
    except:
        specification_obj = SalesOrderSpecification.objects.get(pk=spec)
        app_type = ProjectApprovalTypes.objects.get(pk=approve_type)
        spec_obj = ProjectSepcificationsApproval(
            specification=specification_obj,
            approve_type=app_type,
            status=ProjectApprovalStatus.objects.first(),
        )
        spec_obj.save()
        
    return spec_obj
    
@register.simple_tag
def approval_notes(pk):
    
    notes_objs = ApprovalNotes.objects.filter(specification=pk)
    
    return notes_objs


@register.simple_tag
def check_panels(pk):
    spec_obj = SalesOrderSpecification.objects.get(pk=pk)
    sec_panels_objs = SalesSecondarySepcPanels.objects.filter(specifications=spec_obj)
    
    # if spec_obj.have_vision_panels:
    #     vision_panel = [sec_panels_obj for sec_panels_obj in sec_panels_objs if sec_panels_obj.panel_type == 1]
    
    # if spec_obj.have_spandrel_panels:
    #     spandrel_panel = [sec_panels_obj for sec_panels_obj in sec_panels_objs if sec_panels_obj.panel_type == 2]
    
    # if spec_obj.have_openable_panels:
    #     openable_panel = [sec_panels_obj for sec_panels_obj in sec_panels_objs if sec_panels_obj.panel_type == 3]
    vision_panel = []
    spandrel_panel = []
    openable_panel = []

    if spec_obj.have_vision_panels:
        vision_panel = [sec_panels_obj for sec_panels_obj in sec_panels_objs if sec_panels_obj.panel_type == 1]

    if spec_obj.have_spandrel_panels:
        spandrel_panel = [sec_panels_obj for sec_panels_obj in sec_panels_objs if sec_panels_obj.panel_type == 2]

    if spec_obj.have_openable_panels:
        openable_panel = [sec_panels_obj for sec_panels_obj in sec_panels_objs if sec_panels_obj.panel_type == 3]
    
    # if spec_obj.have_vision_panels and spec_obj.panel_specification:
    #     vision_panel.append(spec_obj)
        
    # if spec_obj.have_spandrel_panels and spec_obj.panel_specification:
    #     spandrel_panel.append(spec_obj)
        
    # if spec_obj.have_openable_panels and spec_obj.panel_specification:
    #     openable_panel.append(spec_obj)

    out_vision_panel = vision_panel if not len(vision_panel) == 0 else None
    out_spandrel_panel = spandrel_panel if not len(spandrel_panel) == 0 else None
    out_openable_panel = openable_panel if not len(openable_panel) == 0 else None
    
    
    data = {
        'vision_panel': out_vision_panel,
        'spandrel_panel': out_spandrel_panel,
        'openable_panel': out_openable_panel,
    }
    return data



def sum_times2(times):
    total_seconds = sum([int(t.split(":")[0]) * 3600 + int(t.split(":")[1]) * 60 for t in times])
    total_hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    total_minutes = remaining_seconds // 60
    total_time = f"{total_hours:02}:{total_minutes:02}"
    
    return total_time

@register.simple_tag
def workstation_time_details(pk):
    workstation_objs = Workstation_Data.objects.filter(eps_product_id=pk).order_by('workstation')
    data = {}
    for workstation in workstation_objs:
        workstation_name = workstation.workstation
        completion_time = workstation.total_completion_time or '00:00'
        
        if workstation_name in data:
            existing_time = data[workstation_name]
            times = [existing_time, completion_time]
            data[workstation_name] = sum_times2(times)
        else:
            data[workstation_name] = completion_time
    return data