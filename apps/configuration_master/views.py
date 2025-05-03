
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.db.models import Q
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse

from apps.Categories.models import Category
from apps.accessories_kit.forms import CreateAccessoryKitForm
from apps.accessories_kit.models import AccessoriesKit, AccessoriesKitItem
from apps.accessories_master.models import Accessories
from apps.brands.models import CategoryBrands
from apps.configuration_master.forms import (
        CreateConfiProductKitItem, 
        CreateConfigurationProductKit,
        CreateConfigurationMasterForm,
    )
from apps.configuration_master.models import (
        ConfigurationMasterBase, 
        ConfigurationsMaster,
    )
from apps.functions import calculate_kit_total
from apps.product_master.models import (
        Product, 
        Product_Accessories, 
        Product_Accessories_Kit,
    )
from amoeba.settings import PROJECT_NAME
from apps.product_parts.forms import CreateProfilesKit
from apps.product_parts.models import (
        Product_Parts_Kit, 
        Product_Parts_Kit_Items, 
        Profile_Kit, 
        Profile_items,
    )
from apps.profiles.models import (
        ProfileMasterSeries, 
        ProfileMasterType, 
        Profiles,
    )


@login_required(login_url="signin")
@permission_required(['configuration_master.view_configurationmasterbase'], login_url='permission_not_allowed')
def configuration_base(request):
    """
        listing all configuration categories that are user previously added
    """
    config_obj = ConfigurationMasterBase.objects.all().order_by('id')
    config_count = ConfigurationsMaster.objects.all().count()
    categories = Category.objects.filter(Q(one_D=True)).order_by('id')

    context = {
        "title": PROJECT_NAME + " | Configuration Master",
        "config_obj": config_obj,
        "config_count": config_count,
        "categories": categories
    }
    return render(request, "Master_settings/Configuration_Master/configuration_base_profile.html", context)

@login_required(login_url="signin")
def category_wise_product(request, pk):
    """
    This function retrieves all products belonging to a specific category and renders them in a dropdown
    menu on a web page.
    """
    category = Category.objects.get(pk=pk)
    products = Product.objects.filter(product_category=pk, status=1).order_by('id')
    categories = Category.objects.all().order_by('id')
    context = {
        "products": products,
        "category": category,
        "categories": categories
    }
    return render(request, 'Master_settings/Configuration_Master/configuration_product_dropdown.html', context)


@login_required(login_url='signin')
@permission_required(['configuration_master.view_configurationmasterbrands'], login_url='permission_not_allowed')
def configuration_brands(request, pk):
    """
    This function retrieves and organizes data related to product configurations and categories for
    display on a web page.
    """
    config_obj = ConfigurationMasterBase.objects.all().order_by('id')
    config_count = ConfigurationsMaster.objects.all().count()
    product = Product.objects.get(pk=pk)
    categories = Category.objects.all().order_by('id')

    products_obj = Product.objects.filter(
        product_category=product.product_category, status=1).order_by('id')
    products = Product.objects.filter(product_category=pk, status=1).order_by('id')

    profile_kit_data = Profile_Kit.objects.filter(product=product).order_by('id')

    context = {
        "title": f"{PROJECT_NAME} | Configuration Master",
        "config_obj": config_obj,
        "config_count": config_count,
        "category": product.product_category,
        "products_obj": products_obj,
        "product": product,
        "products": products,
        "categories": categories,
        "profile_kit_data": profile_kit_data,
    }
    return render(request, "Master_settings/Configuration_Master/configuration_base_profile.html", context)


@login_required(login_url='signin')
def configuration_product_parts(request, pk):
    """
    This function retrieves and returns various objects related to a product's configuration and parts
    kit for display on a web page.
    
    """
    config_obj = ConfigurationMasterBase.objects.all().order_by('id')
    config_count = ConfigurationsMaster.objects.all().count()
    product = Product.objects.get(pk=pk)
    categories = Category.objects.all().order_by('id')

    products_obj = Product.objects.filter(
        product_category=product.product_category, status=1).order_by('id')
    products = Product.objects.filter(product_category=pk, status=1).order_by('id')

    product_parts_kit = Product_Parts_Kit.objects.filter(product=product).order_by('id')

    context = {
        "title": f"{PROJECT_NAME} | Configuration Master",
        "config_obj": config_obj,
        "config_count": config_count,
        "category": product.product_category,
        "products_obj": products_obj,
        "product": product,
        "products": products,
        "categories": categories,
        "product_parts_kit": product_parts_kit,
    }
    return render(request, "Master_settings/Configuration_Master/configuration_base_parts.html", context)


@login_required(login_url='signin')
def configuration_product_parts_kit(request, pk):
    """
    This function creates a product parts kit with associated kit items and saves them to the database.
    
    """
    product = Product.objects.get(pk=pk)
    form = CreateConfigurationProductKit()
    kit_item_form = CreateConfiProductKitItem(
        category=product.product_category)
    parts_kit_forms = modelformset_factory(
        Product_Parts_Kit_Items, form=kit_item_form, extra=1, can_delete=True)
    parts_kit_formset = parts_kit_forms(
        queryset=Product_Parts_Kit_Items.objects.none(), prefix="parts_kit")
    if request.method == "POST":
        form = CreateConfigurationProductKit(request.POST)
        parts_kit_formset = parts_kit_forms(
            request.POST, queryset=Product_Parts_Kit_Items.objects.none(), prefix="parts_kit")
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.product = product
            form_obj.save()
            for items in parts_kit_formset:
                if items.is_valid():
                    items_obj = items.save(commit=False)
                    items_obj.product_parts_kit = form_obj
                    if items_obj.formula:
                        items_obj.save()
                        messages.success(request, "Product Parts Kit Created Successfully")
                else:
                    messages.error(request, "Error in one of the item.")
        else:
            messages.error(request, form.errors)
        return redirect('configuration_product_parts', pk=product.id)

    context = {
        "product": product,
        "form": form,
        "parts_kit_formset": parts_kit_formset,
    }
    return render(request, 'Master_settings/Configuration_Master/add_product_parts_modal.html', context)


@login_required(login_url='signin')
def configuration_product_parts_kit_edit(request, pk):
    """
    This function edits a product parts kit and its associated items.
    
    """
    kit = Product_Parts_Kit.objects.get(pk=pk)
    form = CreateConfigurationProductKit(instance=kit)
    kit_item_form = CreateConfiProductKitItem(
        category=kit.product.product_category)
    parts_kit_forms = modelformset_factory(
        Product_Parts_Kit_Items, form=kit_item_form, extra=1, can_delete=True)
    parts_kit_formset = parts_kit_forms(queryset=Product_Parts_Kit_Items.objects.filter(
        product_parts_kit=kit), prefix="parts_kit")
    if request.method == "POST":
        form = CreateConfigurationProductKit(request.POST, instance=kit)
        parts_kit_formset = parts_kit_forms(request.POST, queryset=Product_Parts_Kit_Items.objects.filter(
            product_parts_kit=kit), prefix="parts_kit")
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.product = kit.product
            form_obj.save()
            for items in parts_kit_formset:
                if items.is_valid():
                    items_obj = items.save(commit=False)
                    items_obj.product_parts_kit = form_obj
                    if items_obj.formula:
                        items_obj.save()
                        messages.success(request, "Product Parts Kit Updated Successfully")
                else:
                    messages.error(request, "Error in one of the item.")
        else:
            messages.error(request, form.errors)
        return redirect('configuration_product_parts', pk=kit.product.id)

    context = {
        "kit_id": kit.id,
        "form": form,
        "parts_kit_formset": parts_kit_formset,
    }
    return render(request, 'Master_settings/Configuration_Master/add_product_parts_modal.html', context)

@login_required(login_url='signin')
def delete_part_item(request, pk):
    """
    This function deletes a part item and all associated profile items from the database.
    
    """
    Profile_items.objects.filter(parts=pk).delete()
    part_item = Product_Parts_Kit_Items.objects.get(pk=pk)
    try:
        part_item.delete()
    except Exception as e:
        print('EXCe==>', e)
        messages.error(request, "Error")
    return JsonResponse({"success": True}, status=200)

@login_required(login_url='signin')
@permission_required(['product_parts.delete_parts'], login_url='permission_not_allowed')
def delete_product_parts_kit(request, pk):
    """
    This function deletes a product parts kit and its associated items, and returns the user to the
    product parts configuration page.
    
    """
    kit = Product_Parts_Kit.objects.get(pk=pk)
    try:
        Product_Parts_Kit_Items.objects.filter(product_parts_kit=kit).delete()
        messages.success(request, "Product Parts Kit Deleted Successfully")
    except Exception as e:
        messages.error(
            request, "Error in Deleting Parts. Parts Maybe used in any other configurations. Please Check it before deleting. ",)
    kit.delete()
    return redirect("configuration_product_parts", pk=kit.product.id)


@login_required(login_url='signin')
@permission_required(['product_parts.add_profile_kit'], login_url='permission_not_allowed')
def create_product_profile(request, pk):
    """
    This function creates a product profile with associated profile items and saves it to the database.
    
    """
    product = Product.objects.get(pk=pk)
    form = CreateProfilesKit(product=product)
    if request.method == "POST":
        form = CreateProfilesKit(request.POST, product=product)
        parts = request.POST.getlist("parts", None)
        profile = request.POST.getlist("profile", None)
        thickness = request.POST.getlist("thickness", None)
        weight_per_lm = request.POST.getlist("weight_per_lm", None)
        formula = request.POST.getlist("formula", None)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.product = product
            form_obj.save()
            for i in range(len(parts)):
                parts_kit = Product_Parts_Kit_Items.objects.get(pk=parts[i])
                Profile_items.objects.create(
                    profile_id=profile[i],
                    parts=parts_kit,
                    thickness=thickness[i],
                    weight_per_lm=weight_per_lm[i],
                    formula=formula[i],
                    profile_kit=form_obj
                )
            messages.success(request, "Product Profile Created Successfully")
        else:
            messages.error(request, form.errors)
        return redirect('configuration_brands', pk=product.id)

    context = {
        "form": form,
        "product": product,
    }
    return render(request, 'Master_settings/Configuration_Master/config_profile_add_modal.html', context)


@login_required(login_url='signin')
def edit_product_profile(request, pk):
    """
    This function edits a product profile and saves the changes to the database.
    """
    kit = Profile_Kit.objects.get(pk=pk)
    product = Product.objects.get(pk=kit.product.id)
    form = CreateProfilesKit(instance=kit, product=product)
    form.fields['parts_kit'].disabled = True
    kit_objs = Product_Parts_Kit_Items.objects.filter(
        product_parts_kit=kit.parts_kit).order_by('id')
    if request.method == "POST":
        form = CreateProfilesKit(request.POST, product=product, instance=kit)
        parts = request.POST.getlist("parts", None)
        profiles = request.POST.getlist("profiles", None)
        thickness = request.POST.getlist("thicknesss", None)
        weight_per_lm = request.POST.getlist("weight_per_lms", None)
        formula = request.POST.getlist("formulas", None)
        if form.is_valid():
            form.save()
            data = Profile_items.objects.filter(profile_kit=kit)
            counter = 0
            try:
                for obj in data:
                    obj.profile = Profiles.objects.get(pk=profiles[counter])
                    obj.profile_kit = kit
                    obj.parts = Product_Parts_Kit_Items.objects.get(pk=parts[counter])
                    obj.thickness = thickness[counter]
                    obj.weight_per_lm = weight_per_lm[counter]
                    obj.formula = formula[counter]
                    obj.save()
                    counter += 1
                    
                if not counter == len(parts):
                    for w in range(len(parts)):
                        Profile_items.objects.create(
                            profile_id=profiles[counter],
                            parts_id=parts[counter],
                            thickness=thickness[counter],
                            weight_per_lm=weight_per_lm[counter],
                            formula=formula[counter],
                            profile_kit=kit
                        )
                        counter += 1
            except Exception as e:
                pass
            messages.success(request, "Product Profile Updated Successfully")
        else:
            messages.error(request, form.errors)
        return redirect('configuration_brands', pk=product.id)

    context = {
        "form": form,
        "product": product,
        "kit": kit,
        "kit_objs": kit_objs,
        "profile_series": kit.profile_series
    }
    return render(request, 'Master_settings/Configuration_Master/config_profile_add_modal.html', context)


@login_required(login_url='signin')
def get_profile_type(request, pk):
    """
    This function retrieves profile types based on a given brand ID and renders them in a dropdown menu.
    """
    types = ProfileMasterType.objects.filter(profile_master_brand=pk).order_by('id')
    return render(request, "Master_settings/Configuration_Master/config_profile_type_dropdown.html", {"types": types})


@login_required(login_url='signin')
def get_profile_series(request, pk):
    """
    This function retrieves a list of ProfileMasterSeries objects filtered by a given
    profile_master_type and returns a rendered HTML template with the list of objects.
    
    """
    seriess = ProfileMasterSeries.objects.filter(profile_master_type=pk).order_by('id')
    return render(request, "Master_settings/Configuration_Master/config_profile_series_dropdown.html", {"seriess": seriess})


@login_required(login_url='signin')
def get_product_profile_settings(request, pk, profile_series):
    """
    This function retrieves product profile settings for a given product parts kit and profile series
    and renders them in a template.
    
    """
    kit = Product_Parts_Kit.objects.get(pk=pk)
    kit_objs = Product_Parts_Kit_Items.objects.filter(product_parts_kit=kit).order_by('id')
    context = {
        "kit": kit,
        "kit_objs": kit_objs,
        "profile_series": profile_series,
        # "profile": profile
    }
    return render(request, "Master_settings/Configuration_Master/product_parts_list_in_profile_add.html", context)


@login_required(login_url='signin')
def get_profile_data_config(request, pk):
    """
    This function retrieves profile data from the database and returns it as a JSON response.
    
    """
    profile_data = Profiles.objects.get(pk=pk)
    context = {
        "thickness": profile_data.thickness,
        "weight_per_lm": profile_data.weight_per_lm
    }
    return JsonResponse(context, status=200)


@login_required(login_url='signin')
def get_edit_profile_parts(request, pk, profile_id):
    """
    This function retrieves data from a database and returns it as a JSON response.
    
    """
    
    try:
        datas = Profile_items.objects.get(parts=pk, profile_kit=profile_id)
    except Exception as e:
        print("exception==>", e)
    context = {
        'thickness': datas.thickness,
        'weight_per_lm': datas.weight_per_lm,
        'profile': datas.profile.id
    }
    return JsonResponse(context, status=200)


@login_required(login_url='signin')
@permission_required(['configuration_master.view_configurationmasterbrands'], login_url='permission_not_allowed')
def configuration_product_accessories(request, pk):
    """
    This function creates and saves a product accessory kit with its items and calculates the total
    price.
    
    """
    config_obj = ConfigurationMasterBase.objects.all().order_by('id')
    config_count = ConfigurationsMaster.objects.all().count()
    product = Product.objects.get(pk=pk)
    categories = Category.objects.all().order_by('id')

    products_obj = Product.objects.filter(
        product_category=product.product_category, status=1).order_by('id')
    products = Product.objects.filter(product_category=pk, status=1).order_by('id')

    form = CreateAccessoryKitForm()
    product_accessory = Product_Accessories.objects.filter(product=product).order_by('id')
    accessories_obj = AccessoriesKit.objects.filter(product=product).order_by('id')
    
    if request.method == 'POST':
        form = CreateAccessoryKitForm(request.POST)
        accessory_product = request.POST.getlist('accessory_product')
        accessories = request.POST.getlist('accessory')
        accessory_model = request.POST.getlist('accessory_model')
        accessory_quantity = request.POST.getlist('accessory_quantity')
        kit_item_price = request.POST.getlist('kit_item_price')
        kit_item_total = request.POST.getlist('kit_item_total')
        if form.is_valid():
            form_kit_obj = form.save()
            form_kit_obj.product_id = pk
            form_kit_obj.created_by = request.user
            form_kit_obj.save()
            for i in range(len(accessories)):
                accessory = Accessories.objects.get(pk=accessories[i])
                if accessory_quantity[i] != '0':
                    try:
                        formula = Product_Accessories_Kit.objects.get(
                                        product_accessory=accessory_product, 
                                        accessory=accessory
                                    ).accessory_formula
                        
                    except Exception:
                        formula = None
                    AccessoriesKitItem.objects.create(
                        created_by=request.user,
                        accessory=accessory,
                        brand=accessory.accessory_brand,
                        model=accessory_model[i],
                        kit_item_price=kit_item_price[i],
                        quantity=accessory_quantity[i],
                        kit_item_total=kit_item_total[i],
                        accessory_kit=form_kit_obj,
                        accessory_formula=formula
                    )
            total = calculate_kit_total(form_kit_obj.id)
            form_kit_obj.kit_price = total
            form_kit_obj.save()
            
            messages.success(request, "Product Accessory Kit Created Successfully")
        else:
            messages.error(request, form.errors)
        return redirect('configuration_product_accessories', pk=product.id)

    kit_obj = AccessoriesKit.objects.filter(product=pk).order_by('-id')

    context = {
        "title": f'{PROJECT_NAME} | Configuration Master',
        "config_obj": config_obj,
        "config_count": config_count,
        "category": product.product_category,
        "products_obj": products_obj,
        "product": product,
        "products": products,
        "categories": categories,
        "kit_obj": kit_obj,
        "product_accessory": product_accessory,
        "form": form,
        "accessories_obj": accessories_obj
    }
    return render(request, "Master_settings/Configuration_Master/configuration_product_accessories.html", context)


@login_required(login_url='signin')
@permission_required(['configuration_master.view_configurationmasterbrands'], login_url='permission_not_allowed')
def configuration_product_accessories_settings(request, pk):
    """
    This function retrieves and renders various objects related to a product's accessory kit settings
    for a configuration master page.
    
    """
    config_obj = ConfigurationMasterBase.objects.all().order_by('id')
    config_count = ConfigurationsMaster.objects.all().count()
    product = Product.objects.get(pk=pk)
    categories = Category.objects.all().order_by('id')

    products_obj = Product.objects.filter(
        product_category=product.product_category, status=1).order_by('id')
    products = Product.objects.filter(product_category=pk, status=1).order_by('id')

    product_accessory_kit = Product_Accessories.objects.filter(product=product).order_by('id')
    context = {
        "title": f"{PROJECT_NAME} | Configuration Master",
        "config_obj": config_obj,
        "config_count": config_count,
        "category": product.product_category,
        "products_obj": products_obj,
        "product": product,
        "products": products,
        "categories": categories,
        "product_accessory_kit": product_accessory_kit,
    }
    return render(request, "Master_settings/Configuration_Master/configuration_product_accessory_settings.html", context)


@login_required(login_url='signin')
@permission_required(['configuration_master.view_configurationmasterbrands'], login_url='permission_not_allowed')
def configuration_pre_defined_prices(request, pk):
    """
    This function retrieves and returns various objects and data to be used in a configuration master
    page template.
    
    """
    config_obj = ConfigurationMasterBase.objects.all().order_by('id')
    config_count = ConfigurationsMaster.objects.all().count()
    product = Product.objects.get(pk=pk)
    categories = Category.objects.all().order_by('id')

    products_obj = Product.objects.filter(
        product_category=product.product_category, status=1).order_by('id')
    brands = Profile_Kit.objects.filter(product=product).distinct('system')
    products = Product.objects.filter(product_category=pk, status=1).order_by('id')

    context = {
        "title": f"{PROJECT_NAME} | Configuration Master",
        "config_obj": config_obj,
        "config_count": config_count,
        "category": product.product_category,
        "products_obj": products_obj,
        "brands": brands,
        "product": product,
        "products": products,
        "categories": categories,
    }
    return render(request, "Master_settings/Configuration_Master/configuration_pre_price.html", context)


@login_required(login_url='signin')
@permission_required(['configuration_master.view_configurationmasterseries'], login_url='permission_not_allowed')
def configuration_profile_type_list(request, pk, product):
    """
    This function returns a list of profile types for a given product and brand, along with other
    related data, to be displayed in a configuration master page.
    
    """
    brand = CategoryBrands.objects.get(pk=pk)
    config_obj = ConfigurationMasterBase.objects.all().order_by('id')
    config_count = ConfigurationsMaster.objects.all().count()
    categories = Category.objects.all().order_by('id')
    product = Product.objects.get(pk=product)
    brands = Profile_Kit.objects.filter(product=product).distinct('system')
    profile_types = Profile_Kit.objects.filter(
        system=brand, product=product.id).distinct('profile_type')

    context = {
        "title": f"{PROJECT_NAME} | Configuration Master",
        "config_obj": config_obj,
        "config_count": config_count,
        "category": product.product_category,
        "brands": brands,
        "brand": brand,
        "product": product,
        "categories": categories,
        "profile_types": profile_types,
    }
    return render(request, "Master_settings/Configuration_Master/configuration_pre_price.html", context)


@login_required(login_url='signin')
@permission_required(['configuration_master.view_configurationmasterseries'], login_url='permission_not_allowed')
def configuration_series(request, pk, product):
    """
    This function retrieves and organizes data related to product configurations and displays it on a
    web page.
    
    """
    config_obj = ConfigurationMasterBase.objects.all().order_by('id')
    config_count = ConfigurationsMaster.objects.all().count()
    categories = Category.objects.all().order_by('id')
    product = Product.objects.get(pk=product)

    brands = Profile_Kit.objects.filter(product=product).distinct('system')
    profile_type = ProfileMasterType.objects.get(pk=pk)
    brand = CategoryBrands.objects.get(pk=profile_type.profile_master_brand.id)
    profile_types = Profile_Kit.objects.filter(
        system=brand, product=product.id).distinct('profile_type')
    profile_seriess = Profile_Kit.objects.filter(
        system=brand, profile_type=profile_type.id, product=product.id).distinct('profile_type')

    context = {
        "title": f"{PROJECT_NAME} | Configuration Master",
        "config_obj": config_obj,
        "config_count": config_count,
        "category": product.product_category,
        "brands": brands,
        "brand": brand,
        "product": product,
        "categories": categories,
        "profile_types": profile_types,
        "profile_type": profile_type,
        "profile_seriess": profile_seriess,
    }
    return render(request, "Master_settings/Configuration_Master/configuration_pre_price.html", context)


@login_required(login_url='signin')
@permission_required(['configuration_master.view_configurationsmaster'], login_url='permission_not_allowed')
def configuration_master(request, pk, product):
    """
    This function renders a configuration master page with various context variables.
    """
    
    config_obj = ConfigurationMasterBase.objects.all().order_by('id')
    config_count = ConfigurationsMaster.objects.all().count()
    categories = Category.objects.all().order_by('id')
    product = Product.objects.get(pk=product)

    profile_type1 = Profile_Kit.objects.get(pk=pk)
    profile_type = ProfileMasterType.objects.get(pk=profile_type1.profile_type.id)
    brands = Profile_Kit.objects.filter(product=product).distinct('system')
    brand = CategoryBrands.objects.get(pk=profile_type.profile_master_brand.id)
    profile_types = Profile_Kit.objects.filter(
        system=brand, product=product.id).distinct('profile_type')
    profile_seriess = Profile_Kit.objects.filter(
        system=brand, profile_type=profile_type.id, product=product.id).distinct('profile_type')

    configurations = ConfigurationsMaster.objects.filter(
        config_series=profile_type1).order_by('id')

    context = {
        "title": f"{PROJECT_NAME} | Configuration Master",
        "config_obj": config_obj,
        "config_count": config_count,
        "category": product.product_category,
        "brands": brands,
        "brand": brand,
        "product": product,
        "categories": categories,
        "profile_types": profile_types,
        "profile_type": profile_type1,
        "name": profile_type,
        "profile_seriess": profile_seriess,
        "configurations": configurations,
    }
    return render(request, "Master_settings/Configuration_Master/configuration_pre_price.html", context)


@login_required(login_url='signin')
@permission_required(['configuration_master.add_configurationsmaster'], login_url='permission_not_allowed')
def add_configuration(request, pk):
    """
    This function adds a new configuration to a product series and saves it to the database.
    """
    series = Profile_Kit.objects.get(pk=pk)
    form = CreateConfigurationMasterForm()
    unit_area = request.POST.get('unit_area')
    if request.method == 'POST':
        form = CreateConfigurationMasterForm(request.POST)
        if form.is_valid():
            form_obj = form.save()
            form_obj.config_series = series
            form_obj.unit_area = unit_area
            form_obj.created_by = request.user
            form_obj.save()
            messages.success(request, "Product Configuration Created Successfully")
        else:
            messages.error(request, form.errors)
            print("form errors==>", form.errors)

        return redirect("configuration_master", pk=series.id, product=series.product.id)
    context = {
        "form": form,
        "series_id": series
    }
    return render(request, "Master_settings/Configuration_Master/configuration_master_edit_form.html", context)


@login_required(login_url='signin')
@permission_required(['configuration_master.change_configurationsmaster'], login_url='permission_not_allowed')
def configuration_master_edit(request, pk):
    """
    This function edits a configuration master object and saves the changes made by the user.
    
    """
    configurations = ConfigurationsMaster.objects.get(pk=pk)
    form = CreateConfigurationMasterForm(instance=configurations)
    unit_area = request.POST.get('unit_area')

    if request.method == 'POST':
        form = CreateConfigurationMasterForm(
            request.POST, instance=configurations)
        if form.is_valid():
            form_obj = form.save()
            form_obj.unit_area = unit_area
            form_obj.created_by = request.user
            form_obj.save()
            messages.success(request, "Product Configuration Updated Successfully")
        else:
            messages.error(request, form.errors)
            print("form errors==>", form.errors)
        return redirect("configuration_master", pk=configurations.config_series.id, product=configurations.config_series.product.id)
    context = {
        "configurations": configurations,
        "form": form,
        "series_id": configurations.config_series
    }
    return render(request, "Master_settings/Configuration_Master/configuration_master_edit_form.html", context)
