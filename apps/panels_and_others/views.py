from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.timezone import now as time
from openpyxl import Workbook
from apps.estimations.taskes import infill_reference_export_shared
from xlsxwriter.workbook import Workbook
from django.template.loader import get_template

from apps.brands.models import CategoryBrands
from apps.panels_and_others.forms import (
            CreatePanelMasterBaseForm,
            CreatePanelMasterBrandsForm, 
            CreatePanelMasterSeriesForm,
            AddPanelConfigurationFrom, 
            AddGlassSpecificationsFrom, 
            AddPanelSpecificationsFrom,
)
from apps.product_master.models import Product
from amoeba.settings import MEDIA_URL, PROJECT_NAME, STATIC_URL
from apps.panels_and_others.models import (
                PanelMasterBase, 
                PanelMasterBrands, 
                PanelMasterSeries, 
                PanelMasterSpecifications, 
                PanelMasterConfiguration,
)

import io

from wkhtmltopdf.views import PDFTemplateResponse
from wkhtmltopdf import wkhtmltopdf


@login_required(login_url="signin")
@permission_required(['panels_and_others.view_panelmasterbase'], login_url='permission_not_allowed')
def panel_master_base(request):
    """
    This function retrieves all PanelMasterBase objects and renders them in a template with a context
    containing the title and panel_obj.
    """
    panel_obj = PanelMasterBase.objects.all().order_by('id')
    context = {
        "title": f"{PROJECT_NAME} | Panel and Others Master",
        "panel_obj": panel_obj,
    }
    return render(request, "Master_settings/Panels_and_others_Master/panelmaster_base.html", context)


@login_required(login_url='signin')
@permission_required(['panels_and_others.add_panelmasterbase'], login_url='permission_not_allowed')
def add_panel_category(request):
    """
    This function adds a new panel category to the database based on user input.
    """
    form = CreatePanelMasterBaseForm()
    if request.method == 'POST':
        form = CreatePanelMasterBaseForm(request.POST)
        if form.is_valid():
            form_obj = form.save()
            form_obj.created_by = request.user
            form_obj.save()
        else:
            messages.error(request, form.errors)
        return redirect("panel_master_base")
    context = {
        "form": form
    }
    return render(request, "Master_settings/Panels_and_others_Master/add_panel_category.html", context)
    
@login_required(login_url='signin')
def delete_panel_category(request, pk):
    """
    This function deletes a panel category and displays a success or error message depending on whether
    the deletion was successful or not.
    """
    item = PanelMasterBase.objects.get(pk=pk)
    if request.method == "POST":
        try:
            item.delete()
            messages.success(request, f"Panel Master Category {item} Deleted Successfully")

        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('panel_master_base')

    context = {"url": f"/Panels_and_others/delete_panel_category/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
@permission_required(['panels_and_others.view_panelmasterbrands'], login_url='permission_not_allowed')
def panel_brands_list(request, pk):
    """
    This function retrieves a list of panel brands based on a given panel category and renders it in a
    template.
    
    """
    panel_obj = PanelMasterBase.objects.all().order_by('id')
    category = PanelMasterBase.objects.get(pk=pk)
    brands = PanelMasterBrands.objects.filter(panel_category=category.panel_category).order_by("id")

    context = {
        "title": f"{PROJECT_NAME} | Panel and Others Master",
        "category": category,
        "brands": brands,
        "panel_obj": panel_obj,
    }
    return render(request, "Master_settings/Panels_and_others_Master/panelmaster_base.html", context)

@login_required(login_url='signin')
@permission_required(['panels_and_others.add_panelmasterbrands'], login_url='permission_not_allowed')
def add_panel_brands(request, pk):
    """
    This function adds a new panel brand to a panel category and renders a form to do so.
    
    """
    category = PanelMasterBase.objects.get(pk=pk)
    form = CreatePanelMasterBrandsForm()
    form.fields['panel_brands'] = forms.ModelChoiceField(
                                    queryset=CategoryBrands.objects.filter(
                                        category=category.panel_category
                                    ), empty_label="Select a Brand")
    form.fields['panel_brands'].widget.attrs.update({
            'class': 'form-select btn-sm mb-2',
            'data-control': 'select2',
            'data-hide-search': 'true',
            'data-placeholder': 'Select an option'
        })
    if request.method == 'POST':
        form = CreatePanelMasterBrandsForm(request.POST)
        if form.is_valid():
            form_obj = form.save()
            form_obj.panel_category = category.panel_category
            form_obj.created_by = request.user
            form_obj.save()
        else:
            messages.error(request, form.errors)
            print("errors==>", form.errors)
        return redirect('panel_brands_list', pk=category.id)
    context = {
        'form': form, 
        'category': category 
        }
    return render(request, "Master_settings/Panels_and_others_Master/add_panel_brand.html", context)


@login_required(login_url='signin')
def delete_panel_brand(request, pk):
    """
    This function deletes a PanelMasterBrands object and displays a success or error message depending
    on whether the object was successfully deleted or not.
    
    """
    item = PanelMasterBrands.objects.get(pk=pk)
    if request.method == "POST":
        try:
            item.delete()
            messages.success(
                request,
                f"Panel Master Brand {item.panel_brands.brand} Deleted Successfully",
            )

        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('panel_master_base')

    context = {"url": f"/Panels_and_others/delete_panel_brand/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
@permission_required(['panels_and_others.view_panelmasterseries'], login_url='permission_not_allowed')
def list_panel_series(request, pk):
    """
    This function retrieves and displays a list of panel series based on a given brand ID.
    
    """
    brand = PanelMasterBrands.objects.get(pk=pk)
    series = PanelMasterSeries.objects.filter(brands=pk).order_by('id')

    panel_obj = PanelMasterBase.objects.all()
    category = PanelMasterBase.objects.get(panel_category=brand.panel_category)
    brands = PanelMasterBrands.objects.filter(panel_category=brand.panel_category).order_by("id")

    context = {
        "title": f"{PROJECT_NAME} | Panel and Others Master",
        "brands": brands,
        "brand": brand,
        "series": series,
        "category": category,
        "panel_obj": panel_obj,
    }
    return render(request, "Master_settings/Panels_and_others_Master/panelmaster_base.html", context)


@login_required(login_url='signin')
@permission_required(['panels_and_others.add_panelmasterseries'], login_url='permission_not_allowed')
def add_panel_series(request, pk):
    """
    This function adds a new panel series to a panel master brand and saves the form data if it is
    valid.
    
    """
    brand = PanelMasterBrands.objects.get(pk=pk)
    form = CreatePanelMasterSeriesForm()
    if request.method == 'POST':
        form = CreatePanelMasterSeriesForm(request.POST)
        if form.is_valid():
            form_obj = form.save()
            form_obj.brands = brand
            form_obj.created_by = request.user
            form_obj.save()
        else:
            messages.error(request, form.errors)
            print("errors==>", form.errors)
        return redirect('list_panel_series', pk=brand.id)
    context = {
        "brand": brand,
        "form": form,
    }
    return render(request, "Master_settings/Panels_and_others_Master/add_panel_series.html", context)


@login_required(login_url='signin')
def delete_panel_series(request, pk):
    """
    This function deletes a panel series object and displays a success or error message.
    
    """
    item = PanelMasterSeries.objects.get(pk=pk)
    if request.method == "POST":
        try:
            item.delete()
            messages.success(request, f"Panel Series {item.series} Deleted Successfully")

        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_panel_series', pk=item.brands.id)

    context = {"url": f"/Panels_and_others/delete_panel_series/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
@permission_required(['panels_and_others.view_panelmasterspecifications'], login_url='permission_not_allowed')
def list_panel_specification(request, pk):
    """
    This function retrieves panel specifications based on a given panel series and renders them in a
    template with related data.
    
    """
    serie = PanelMasterSeries.objects.get(pk=pk)
    products = PanelMasterSpecifications.objects.filter(series=pk).order_by('id')

    brand = serie.brands
    series = PanelMasterSeries.objects.filter(brands=serie.brands).order_by('id')
    panel_obj = PanelMasterBase.objects.all().order_by('id')
    category = PanelMasterBase.objects.get(panel_category=brand.panel_category)
    brands = PanelMasterBrands.objects.filter(panel_category=brand.panel_category).order_by("id")

    context = {
        "title": f"{PROJECT_NAME} | Panel and Others Master",
        "products": products,
        "serie": serie,
        "brands": brands,
        "brand": brand,
        "series": series,
        "category": category,
        "panel_obj": panel_obj,
    }
    return render(request, "Master_settings/Panels_and_others_Master/panelmaster_base.html", context)


@login_required(login_url='signin')
@permission_required(['panels_and_others.add_panelmasterspecifications'], login_url='permission_not_allowed')
def add_specification(request, pk):
    """
    This function adds a specification for a panel master series based on whether the panel category is
    glass or not.
    
    """
    series = PanelMasterSeries.objects.get(pk=pk)
    if series.brands.panel_category.is_glass:
        form = AddGlassSpecificationsFrom()
    else:
        form = AddPanelSpecificationsFrom()
    if request.method == 'POST':
        if series.brands.panel_category.is_glass:
            form = AddGlassSpecificationsFrom(request.POST)
        else:
            form = AddPanelSpecificationsFrom(request.POST)

        if form.is_valid():
            form_obj = form.save()
            form_obj.series = series
            form_obj.created_by = request.user
            form_obj.save()
        else:
            messages.error(request, form.errors)
            print("errors==>", form.errors)
        return redirect('list_panel_specification', pk=series.id)
    context = {
        "title": f"{PROJECT_NAME} | Panel and Others Master",
        "series": series,
        "form": form,
    }
    return render(request, "Master_settings/Panels_and_others_Master/panel_master_specification_add_modal.html", context)


@login_required(login_url='signin')
def delete_panel_spec(request, pk):
    """
    This function deletes a panel specification and displays a success or error message depending on
    whether the deletion was successful or not.
    
    """
    item = PanelMasterSpecifications.objects.get(pk=pk)
    if request.method == "POST":
        try:
            item.delete()
            messages.success(
                request,
                f"Panel Specification {item.specifications} Deleted Successfully",
            )

        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_panel_specification', pk=item.series.id)

    context = {"url": f"/Panels_and_others/delete_panel_spec/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
@permission_required(['panels_and_others.view_panelmasterconfiguration'], login_url='permission_not_allowed')
def panel_item_details(request, pk):
    """
    This function retrieves and organizes data related to panel items and renders it in a template.
    
    """
    specification_obj = PanelMasterSpecifications.objects.get(pk=pk)
    panel_object = PanelMasterConfiguration.objects.filter(panel_specification=specification_obj).order_by('id')

    serie = PanelMasterSeries.objects.get(pk=specification_obj.series.id)
    products = PanelMasterSpecifications.objects.filter(series=serie).order_by('id')
    brand = serie.brands
    series = PanelMasterSeries.objects.filter(brands=serie.brands).order_by('id')
    panel_obj = PanelMasterBase.objects.all().order_by('id')
    category = PanelMasterBase.objects.get(panel_category=brand.panel_category)
    brands = PanelMasterBrands.objects.filter(panel_category=brand.panel_category).order_by("id")

    context = {
        "title": f"{PROJECT_NAME} | Panel and Others Master",
        "specification_obj": specification_obj,
        "panel_obj": panel_obj,
        "products": products,
        "serie": serie,
        "brands": brands,
        "brand": brand,
        "series": series,
        "category": category,
        "panel_object": panel_object,
    }
    return render(request, "Master_settings/Panels_and_others_Master/panelmaster_base.html", context)


@login_required(login_url='signin')
@permission_required(['panels_and_others.add_panelmasterconfiguration'], login_url='permission_not_allowed')
def panel_config_add(request, pk):
    """
    This function adds a new panel configuration to a panel master specification object and redirects to
    the panel item details page.
    
    """
    specification_obj = PanelMasterSpecifications.objects.get(pk=pk)
    form = AddPanelConfigurationFrom()
    if request.method == 'POST':
        form = AddPanelConfigurationFrom(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.created_by = request.user
            form_obj.panel_specification = specification_obj
            form_obj.save()
        else:
            messages.error(request, form.errors)
            print("ERRORS==>", form.errors)

        return redirect('panel_item_details', pk=specification_obj.id)
    context = {
        'form': form,
        'specification_obj': specification_obj
    }
    return render(request, "Master_settings/Panels_and_others_Master/panel_master_configurations_add.html", context)


@login_required(login_url='signin')
@permission_required(['panels_and_others.change_panelmasterconfiguration'], login_url='permission_not_allowed')
def panel_config_edit(request, pk):
    """
        This function edits a panel configuration and saves the changes made by the user.
    """
    config_data = PanelMasterConfiguration.objects.get(pk=pk)
    form = AddPanelConfigurationFrom(instance=config_data)
    if request.method == 'POST':
        form = AddPanelConfigurationFrom(request.POST, instance=config_data)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.last_modified_by = request.user
            form_obj.last_modified_date = time()
            form_obj.save()
        else:
            messages.error(request, form.errors)
            print("ERRORS==>", form.errors)

        return redirect('panel_item_details', pk=config_data.panel_specification.id)
    context = {
        'form': form,
        'config_data': config_data
    }
    return render(request, "Master_settings/Panels_and_others_Master/panel_master_configurations_add.html", context)


@login_required(login_url='signin')
def delete_panel_config(request, pk):
    """
    This function deletes a panel configuration object and displays a success or error message depending
    on whether the object has been used in the application or not.
    
    """
    item = PanelMasterConfiguration.objects.get(pk=pk)
    if request.method == "POST":
        try:
            item.delete()
            messages.success(request, "Panel Configuration Deleted Successfully")

        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('panel_item_details', pk=item.panel_specification.id)

    context = {"url": f"/Panels_and_others/delete_panel_config/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
@permission_required(['estimations.view_mainproductglass'], login_url='permission_not_allowed')
def glass_database_list(request):
    """
    This function retrieves a list of glass panel configurations from the database and renders them in a
    web page.
    
    """
    
    glass_datas = PanelMasterConfiguration.objects.filter(panel_specification__series__brands__panel_category__is_glass=True)
    context = {
        "title": f"{PROJECT_NAME} | Glass Database List",
        "glass_data": glass_datas,
        "glass_data_count": glass_datas.count(),
    }
    return render(request, "Master_settings/Panels_and_others_Master/glass_database.html", context)

@login_required(login_url='signin')
@permission_required(['estimations.view_mainproductglass'], login_url='permission_not_allowed')
def glass_database_filter(request, brand=None, series=None):
    """
    This function filters a database of glass panel configurations based on brand and series parameters
    and returns the filtered data in a rendered HTML table.
    
    """
    if not series and not brand:
        glass_datas = PanelMasterConfiguration.objects.filter(panel_specification__series__brands__panel_category__is_glass=True)\
                                            .distinct('panel_specification__series__brands')

    elif not brand:
        glass_datas = PanelMasterConfiguration.objects.filter(panel_specification__series__brands__panel_category__is_glass=True, 
                                                             panel_specification__series=PanelMasterSeries.objects.get(pk=series))\
                                                            .distinct('panel_specification__series__brands')

    elif not series:
        glass_datas = PanelMasterConfiguration.objects.filter(panel_specification__series__brands__panel_category__is_glass=True, 
                                                             panel_specification__series__brands=PanelMasterBrands.objects.get(pk=brand))\
                                                            .distinct('panel_specification__series__brands')

    else:
        glass_datas = PanelMasterConfiguration.objects.filter(panel_specification__series__brands__panel_category__is_glass=True, 
                                                             panel_specification__series=PanelMasterSeries.objects.get(pk=series), 
                                                             panel_specification__series__brands=PanelMasterBrands.objects.get(pk=brand))\
                                                        .distinct('panel_specification__series__brands')
    context = {
        "title": f"{PROJECT_NAME} | Glass Database List",
        "glass_data": glass_datas,
        "glass_data_count": glass_datas.count(),
    }
    return render(request, "Master_settings/Panels_and_others_Master/glass_db_table.html", context)


@login_required(login_url='signin')
@permission_required(['estimations.view_mainproductglass'], login_url='permission_not_allowed')
def glass_database_table(request):
    """
    This function retrieves data from a database table and renders it in a HTML template for displaying
    a list of glass panels.
    
    """
    glass_data = PanelMasterConfiguration.objects.filter(panel_specification__series__brands__panel_category__is_glass=True)\
            .order_by('-panel_specification__series__brands')
    context = {
        "title": PROJECT_NAME + " | Glass Database List",
        "glass_data": glass_data
    }
    return render(request, "Master_settings/Panels_and_others_Master/glass_db_table.html", context)


@login_required(login_url='signin')
def export_glass_data(request, type):
    """
    This function exports glass panel data in either xlsx or pdf format.
    
    """
    
    # output = io.BytesIO()
    # workbook = Workbook(output)
    # worksheet = workbook.add_worksheet()
    # cell_format = workbook.add_format({'bold': True, 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'fg_color': '#485699'})
    # main_total = 0
    # glass_data = PanelMasterConfiguration.objects.filter(panel_specification__series__brands__panel_category__is_glass=True)\
    #     .order_by('-panel_specification__series__brands')
    # if type == 'xlsx':
    #     header = ['Brand', 'Series', 'Specification', 'U value', 'Shading Co.', 'Base Price', 'Markup', 'Quoted Rate']
    #     for i, head in enumerate(header):
    #         worksheet.write(1, i, head, workbook.add_format({'bold': True}))
    #     for i, glass in enumerate(glass_data):
    #         worksheet.write(i+2, 0, glass.panel_specification.series.brands.panel_brands.brands)
    #         worksheet.write(i+2, 1, glass.panel_specification.series.series)
    #         worksheet.write(i+2, 2, glass.panel_specification.specifications)
    #         worksheet.write(i+2, 3, glass.u_value)
    #         worksheet.write(i+2, 4, glass.shading_coefficient)
    #         worksheet.write(i+2, 5, glass.price_per_sqm)
    #         worksheet.write(i+2, 6, glass.markup_percentage)
    #         worksheet.write(i+2, 7, glass.panel_quoted_rate)

    #     workbook.close()
    #     output.seek(0)
    #     response = HttpResponse(
    #         output,
    #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #     )
    #     response['Content-Disposition'] = 'attachment; filename=Panel_Details.xlsx'
    #     return response

    # elif type == 'pdf':
    #     glass_datas = PanelMasterConfiguration.objects.filter(
    #                     panel_specification__series__brands__panel_category__is_glass=True)\
    #                 .distinct('panel_specification__series__brands')
    #     context = {
    #         "glass_data": glass_datas,
    #         "STATIC_URL": f'http://{str(request.get_host())}/{str(STATIC_URL)}',
    #         "MEDIA_URL": f'http://{str(request.get_host())}/{str(MEDIA_URL)}',
    #     }
    #     cmd_options = {
    #                 'quiet': True, 
    #                 'enable-local-file-access': True, 
    #                 'margin-top': '10mm', 
    #                 'header-spacing': 5,
    #                 'minimum-font-size': 16,
    #                 'page-size': 'A4',
    #                 'javascript-delay':  500,
    #                 'orientation': 'Landscape',
    #                 'encoding': "UTF-8",
    #                 'print-media-type': True,
    #                 'footer-right': "[page] / [topage]",
    #                 'footer-font-size': 8,
    #             }
    #     file_name = "Galss Reference.pdf"
    #     template = get_template('print_templates/glass_reference_print.html')
    #     response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=False, \
    #                 template=template, context=context)
    #     response = HttpResponse(response.rendered_content, content_type='application/pdf')
    #     response['Content-Disposition'] = f'attachment; filename={file_name}'

    #     return response
    return infill_reference_export_shared(request, type)
        
        
        