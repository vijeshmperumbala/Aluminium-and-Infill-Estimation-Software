from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import modelformset_factory
from django.utils.timezone import now as time
from apps.accessories_kit.models import AccessoriesKit, AccessoriesKitItem
from apps.accessories_kit.forms import (
        CreateAccessoryKitForm, 
        CreateAccessoryKitItemForm,
    )
from apps.functions import calculate_kit_total
from apps.product_master.models import (
        Product, 
        Product_Accessories, 
        Product_Accessories_Kit,
    )
from apps.accessories_master.models import Accessories
from apps.Categories.models import Category

from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
@permission_required(['accessories_kit.view_accessorieskit'], login_url='permission_not_allowed')
def accessories_kit_list(request):
    """
        Accessories kit list view
        display all category
    """
    category_obj = Category.objects.all().order_by('id')
    resource_count = Product.objects.count()
    context = {
        "title": PROJECT_NAME + " | Accessories Kit",
        "category_obj": category_obj,
        "resource_count": resource_count
    }
    return render(request, "Master_settings/Accessories_kit/accessories_kit.html", context)


@login_required(login_url='signin')
@permission_required(['accessories_kit.view_accessorieskit'], login_url='permission_not_allowed')
def kit_products_list(request, pk):
    """
        Accessories kit Product listing page view function.
        pk: category id
        the category id is used for taking related product under the category.
    """
    category_obj = Category.objects.all().order_by('id')
    products_obj = Product.objects.filter(product_category=pk).order_by('id')
    resource_count = Product.objects.count()
    category = Category.objects.get(pk=pk)
    context = {
        "title": PROJECT_NAME + " | Accessories Kit",
        "products_obj": products_obj,
        "category": category,
        "category_obj": category_obj,
        "resource_count": resource_count
    }
    return render(request, "Master_settings/Accessories_kit/accessories_kit.html", context)


@login_required(login_url='signin')
@permission_required(['accessories_kit.view_accessorieskit'], login_url='permission_not_allowed')
def kit_list(request, pk):
    """
        Accessory kit items listing page.
        pk: product id
        product id is used to display all accessories under the product
    """
    category_obj = Category.objects.all().order_by('id')
    product = Product.objects.get(pk=pk)
    category = product.product_category
    resource_count = Product.objects.count()
    products_obj = Product.objects.filter(
        product_category=category).order_by('id')

    form = CreateAccessoryKitForm()

    kit_obj = AccessoriesKit.objects.filter(product=pk).order_by('-id')
    product_accessory = Product_Accessories.objects.filter(product=product)
    
    context = {
        "title": PROJECT_NAME + " | Accessories Kit",
        "kit_obj": kit_obj,
        "product": product,
        "form": form,
        "products_obj": products_obj,
        "category": category,
        "category_obj": category_obj,
        "resource_count": resource_count,
        "product_accessory": product_accessory
    }
    return render(request, "Master_settings/Accessories_kit/accessories_kit.html", context)


@login_required(login_url='signin')
@permission_required(['accessories_kit.add_accessorieskit'], login_url='permission_not_allowed')
def kit_create(request, pk):
    """
        Create Accessory Kit under current selected product
        pk: Product id
    """
    product = Product.objects.get(pk=pk)
    form = CreateAccessoryKitForm()
    product_accessory = Product_Accessories.objects.filter(product=product).order_by('id')
    
    if request.method == 'POST':
        form = CreateAccessoryKitForm(request.POST)
        accessory_product = request.POST.get('accessory_product')
        accessories = request.POST.getlist('accessory')
        accessory_model = request.POST.getlist('accessory_model')
        accessory_quantity = request.POST.getlist('accessory_quantity')
        kit_item_price = request.POST.getlist('kit_item_price')
        kit_item_total = request.POST.getlist('kit_item_total')
        kit_formula = request.POST.getlist("kit_formula")
        kit_divisions = request.POST.getlist("kit_divisions")
        
        try:
            accessory_product = Product_Accessories.objects.get(pk=accessory_product)
        except:
            accessory_product = None
            
        if form.is_valid():
            form_kit_obj = form.save()
            form_kit_obj.product_id = pk
            form_kit_obj.created_by = request.user
            form_kit_obj.accessory_product = accessory_product
            form_kit_obj.save()
            for i in range(len(accessories)):
                accessory = Accessories.objects.get(pk=accessories[i])
                if not accessory_quantity[i] == '0':
                    AccessoriesKitItem.objects.create(
                            created_by=request.user, 
                            accessory=accessory, 
                            brand=accessory.accessory_brand,
                            model=accessory_model[i],
                            kit_item_price=kit_item_price[i],
                            quantity=accessory_quantity[i],
                            kit_item_total=kit_item_total[i],
                            accessory_kit=form_kit_obj,
                            accessory_formula=kit_formula[i],
                            acce_divisions=kit_divisions[i],
                            )
            total = calculate_kit_total(form_kit_obj.id)
            form_kit_obj.kit_price = total
            form_kit_obj.save()
            messages.success(request, "Accessory Kit Created Successfully")
        else:
            messages.error(request, form.errors)
        return redirect('configuration_product_accessories', pk=product.id)

    kit_obj = AccessoriesKit.objects.filter(product=pk).order_by('-id')
    product = Product.objects.get(pk=pk)
    context = {
        "title": PROJECT_NAME + " | Accessories Kit",
        "kit_obj": kit_obj,
        "product": product,
        "form": form,
        "product_accessory": product_accessory
    }
    return render(request, "Master_settings/Accessories_kit/accessories_kit.html", context)


@login_required(login_url='signin')
@permission_required(['accessories_kit.change_accessorieskit'], login_url='permission_not_allowed')
def kit_edit(request, pk):
    """
        Edit Accessory kit view function
        pk: Accessory kit id
    """
    
    acc_kit_obj = AccessoriesKit.objects.get(pk=pk)
    product = acc_kit_obj.product.id
    form = CreateAccessoryKitForm(instance=acc_kit_obj)
    data = AccessoriesKitItem.objects.filter(accessory_kit=acc_kit_obj).order_by('id')
    FORMSET = modelformset_factory(AccessoriesKitItem, CreateAccessoryKitItemForm, extra=0, can_delete=True)
    formset = FORMSET(queryset=AccessoriesKitItem.objects.filter(accessory_kit=acc_kit_obj), prefix="accessory_formset")
    product_accessory = Product_Accessories.objects.filter(product=product)

    if request.method == 'POST':
        form = CreateAccessoryKitForm(request.POST, instance=acc_kit_obj)
        formset = FORMSET(request.POST, prefix="accessory_formset")
        accessory_product = request.POST.get('accessory_product')
        
        try:
            accessory_product = Product_Accessories.objects.get(pk=accessory_product)
        except Exception:
            accessory_product = None

        if form.is_valid() and formset.is_valid():
            form_kit_obj = form.save()
            form_kit_obj.product_id = acc_kit_obj.product
            form_kit_obj.last_modified_by = request.user
            form_kit_obj.last_modified_date = time()
            form_kit_obj.accessory_product = accessory_product
            form_kit_obj.save()

            for item in formset:
                if item.is_valid():
                    item_obj = item.save(commit=False)
                    if item_obj.kit_item_price and item_obj.quantity:
                        try:
                            formula = Product_Accessories_Kit.objects.get(product_accessory=accessory_product, accessory=item_obj.accessory).accessory_formula
                        except Exception:
                            formula = None
                        item_obj.accessory_kit = form_kit_obj
                        item_obj.accessory_formula = formula
                        item_obj.save()
                        form_kit_obj.kit_price = calculate_kit_total(
                            form_kit_obj.id)
                        form_kit_obj.save()
                        messages.success(request, "Accessory Kit Updated Successfully")
                    else:
                        messages.error(
                            request, "Item price and quantity must be needed.")
                else:
                    print("ITEM ERROR==>", item.errors)
                    messages.error(request, item.errors)
        else:
            print("form ERROR==>", form.errors)
            messages.error(request, form.errors)


        return redirect('configuration_product_accessories', pk=product)
    context = {
        "title": f"{PROJECT_NAME} | Accessories Kit",
        "pk": pk,
        "form": form,
        "data_obj": data,
        "formset": formset,
        "product_accessory": product_accessory,
        "acc_kit_obj": acc_kit_obj,
    }
    return render(request, "Master_settings/Accessories_kit/kit_item_edit.html", context)


@login_required(login_url='signin')
@permission_required(['accessories_kit.delete_accessorieskit'], login_url='permission_not_allowed')
def kit_delete(request, pk):
    """
        Accessory kit Delete function
        pk: Accessory kit id
    """
    acc_kit_obj = AccessoriesKit.objects.get(pk=pk)
    kit_items_obj = AccessoriesKitItem.objects.filter(
        accessory_kit=acc_kit_obj).order_by('id')
    if request.method == "POST":
        try:
            kit_items_obj.delete()
            acc_kit_obj.delete()
            messages.success(request, "Accessory Kit Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Deletion is not possible.")
        return redirect('configuration_product_accessories', pk=acc_kit_obj.product.id)
    context = {
                "url": f"/Accessories_kit/kit_delete/{str(pk)}/"
            }
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='siginin')
@permission_required(['accessories_kit.view_accessories'], login_url='permission_not_allowed')
def kit_item_brand(request, pk):
    """
        Get Accessory brand by selecting accessory on create/edit page dropdown.
        pk: accessory id
    """
    acc_obj = Accessories.objects.get(pk=pk).accessory_brand
    data = {
        "acc_brand": acc_obj.brand,
        "acc_country": acc_obj.country.name,

    }
    return JsonResponse(data, status=200)


@login_required(login_url='signin')
@permission_required(['accessories_master.view_accessories'], login_url='permission_not_allowed')
def get_access_data(request, pk):
    """
    This function retrieves accessory data for a specific product and renders it in a dropdown menu.
    """
    product = Product.objects.get(pk=pk)
    data = Accessories.objects.filter(
        accessory_category=product.product_category.id).order_by('id')
    context = {
        "data_obj": data,
    }
    return render(request, 'Master_settings/Accessories_kit/dropdown_accessory.html', context)


@login_required(login_url='signin')
@permission_required(['estimations.view_mainproductaccessories'], login_url='permission_not_allowed')
def get_product_accessory(request, pk):
    """
    This function retrieves a list of product accessories kits based on a given primary key and renders
    them in a template.
    
    """
    data = Product_Accessories_Kit.objects.filter(product_accessory=pk).order_by('id')
    context = {
        "data_obj": data,
        
    }
    return render(request, 'Master_settings/Accessories_kit/product_accessory_list.html', context)