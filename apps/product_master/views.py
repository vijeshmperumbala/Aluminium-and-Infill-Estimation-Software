from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.product_master.models import (
    Product, 
    Product_Accessories, 
    Product_Accessories_Kit, 
    Product_WorkStations,
    SecondaryProducts,
)
from apps.Categories.models import Category
from apps.product_master.forms import (
    CreateProductForm, 
    CreateProductWorkstations,
    CreateSecondaryProduct, 
    EditProductForm, 
    Product_Accessory_Form
)
from amoeba.settings import PROJECT_NAME
from apps.product_parts.models import  Profile_Kit


@login_required(login_url='signin')
@permission_required(['product_master.view_product'], login_url='permission_not_allowed')
def products_list(request):
    """
    This function retrieves a list of products and their categories to be displayed on a web page.
    
    """
    cat_name = Category.objects.all().order_by('id').first()
    count = Product.objects.filter(product_category=cat_name, product_type=1).order_by('id')
    category_obj = Category.objects.all().order_by('id')
        
    context = {
        "title": f"{PROJECT_NAME} | Products master",
        "products": count,
        "category_obj": category_obj,
        "cat_name": cat_name,
        "count": count.count(),
    }
    return render(request, 'Master_settings/Products_Master/products.html', context)


@login_required(login_url='signin')
@permission_required(['product_master.add_product'], login_url='permission_not_allowed')
def products_create(request, pk):
    """
    This function creates a new product and associates it with a specific category.
    """
    category_obj = Category.objects.get(pk=pk)
    form = CreateProductForm()
    if request.method == 'POST':
        form = CreateProductForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            obj.created_by = request.user
            obj.product_type = 1
            obj.product_category = category_obj
            obj.save()
        else:
            messages.error(request, form.errors)
        return redirect('category_wise_products', pk)

    context = {
        "title": f"{PROJECT_NAME} | Products Create",
        "form": form,
        "pk": pk,
    }
    return render(request, 'Master_settings/Products_Master/product_add_drawer.html', context)

@login_required(login_url='signin')
@permission_required(['product_master.add_product'], login_url='permission_not_allowed')
def products_add(request, pk):
    """
    This function adds a new product to a category with associated workstations.
    """
    category_obj = Category.objects.get(pk=pk)
    form = CreateProductForm()
    PRODUCT_WORKSTATIONFORMSET = modelformset_factory(Product_WorkStations, form=CreateProductWorkstations, can_delete=True)
    product_workstation_formset = PRODUCT_WORKSTATIONFORMSET(
                                        queryset=Product_WorkStations.objects.none(), 
                                        prefix="product_workstation_formset"
                                    )

    if request.method == 'POST':
        form = CreateProductForm(request.POST, request.FILES)
        product_workstation_formset = PRODUCT_WORKSTATIONFORMSET(request.POST, prefix="product_workstation_formset")
        
        if form.is_valid():
            obj = form.save()
            obj.created_by = request.user
            obj.product_type = 1
            obj.product_category = category_obj
            obj.save()
            
            for item in product_workstation_formset:
                if item.is_valid():
                    item_obj = item.save(commit=False)
                    item_obj.product = obj
                    item_obj.save()
                else:
                    print('Error==>', item.errors)
        else:
            messages.error(request, form.errors)
        return redirect('category_wise_products', pk)

    context = {
        "title": f"{PROJECT_NAME} | Products Create",
        "form": form,
        "pk": pk,
        "category_obj": category_obj,
        "product_workstation_formset": product_workstation_formset,
    }
    return render(request, 'Master_settings/Products_Master/product_add.html', context)


@login_required(login_url='signin')
@permission_required(['product_master.change_product'], login_url='permission_not_allowed')
def products_edit(request, pk):
    """
    This function edits a product and its associated workstations in a formset.
    
    """
    product = Product.objects.get(pk=pk)
    form = EditProductForm(instance=product)
    PRODUCT_WORKSTATIONFORMSET = modelformset_factory(Product_WorkStations, form=CreateProductWorkstations, can_delete=True, extra=1)
    product_workstation_formset = PRODUCT_WORKSTATIONFORMSET(
                                                queryset=Product_WorkStations.objects.filter(product=product), 
                                                prefix="product_workstation_formset"
                                                )

    if request.method == 'POST':
        form = EditProductForm(request.POST, request.FILES, instance=product)
        product_workstation_formset = PRODUCT_WORKSTATIONFORMSET(
                                                request.POST, 
                                                queryset=Product_WorkStations.objects.filter(product=product), 
                                                prefix="product_workstation_formset"
                                            )
        if form.is_valid():
            obj = form.save()
            obj.last_modified_by = request.user
            obj.last_modified_date = time()
            obj.save()
            for item in product_workstation_formset:
                if item.is_valid():
                    item_obj = item.save(commit=False)
                    if item_obj.workstation:
                        item_obj.product = obj
                        item_obj.save()
                else:
                    print('Error')
                    print('Error==>', item.errors)
                    messages.error(request, item.errors)

            return redirect('category_wise_products', pk=product.product_category.id)
        else:
            messages.error(request, form.errors)
            return redirect('products_list')

    context = {
        "title": f"{PROJECT_NAME} | Products Edit",
        "form": form,
        "product": product,
        "category_obj": product.product_category,
        "product_workstation_formset": product_workstation_formset,
    }
    return render(request, 'Master_settings/Products_Master/product_add.html', context)


@login_required(login_url='signin')
@permission_required(['product_master.delete_product'], login_url='permission_not_allowed')
def product_delete(request, pk):
    """
    This function deletes a product object and redirects to the category-wise products page, while
    displaying an error message if the object is already in use.
    
    """
    if request.method == "POST":
        product_obj = Product.objects.get(pk=pk)
        try:
            product_obj.delete()
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('category_wise_products', pk=product_obj.product_category.id)
    context = {"url": f"/Products_master/product_delete/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
@permission_required(['product_master.view_product'], login_url='permission_not_allowed')
def category_wise_products(request, pk):
    """
    This function retrieves a list of products belonging to a specific category and renders them on a
    web page along with other related information.
    
    """
    products = Product.objects.filter(product_category=pk, product_type=1).order_by('id')
    count = products.count()
    category_obj = Category.objects.all().order_by('id')
    cat_name = Category.objects.get(pk=pk)
    context = {
        "title": f"{PROJECT_NAME} | Products List",
        "products": products,
        "count": count,
        "category_obj": category_obj,
        "cat_name": cat_name,
    }
    return render(request, 'Master_settings/Products_Master/products.html', context)


@login_required(login_url='signin')
def product_profile(request, pk):
    """
    This function retrieves information about a product and its associated profile kits and accessories,
    and renders it on a product profile page.
    """
    product_obj = Product.objects.get(pk=pk)
    kit_obj = Profile_Kit.objects.filter(product=product_obj).order_by('id')
    accessories_obj = Product_Accessories.objects.filter(product=product_obj).order_by('id')
    context = {
        "title": f"{PROJECT_NAME} | Product Profile",
        "product_obj": product_obj,
        "kit_obj": kit_obj,
        "accessories_obj": accessories_obj,
    }
    return render(request, 'Master_settings/Products_Master/product_profile.html', context)


@login_required(login_url='signin')
@permission_required(['product_master.change_product'], login_url='permission_not_allowed')
def products_edit_profile(request, pk):
    """
    This function edits a product's profile and saves the changes made by the user.
    
    """
    product = Product.objects.get(pk=pk)
    form = EditProductForm(instance=product)
    if request.method == 'POST':
        form = EditProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            obj = form.save()
            obj.last_modified_by = request.user
            obj.last_modified_date = time()
            obj.save()
        else:
            messages.error(request, form.errors)
        return redirect('product_profile', pk=product.id)

    context = {
        "title": f"{PROJECT_NAME} | Products Edit",
        "form": form,
        "product": product,
    }
    return render(request, 'Master_settings/Products_Master/edit_modal.html', context)


@login_required(login_url='signin')
def get_kit_data(request, pk):
    """
    This function retrieves the weight of a kit object and returns it as a JSON response.
    """
    kit_obj = Profile_Kit.objects.get(pk=pk)
    data = {
        "kit_weight_lm": kit_obj.kit_weight_lm
    }
    return JsonResponse(data, status=200)


@login_required(login_url='signin')
def create_product_accessory(request, pk):
    """
    This function creates a product accessory formset and saves the data to the database.
    
    """
    product = Product.objects.get(pk=pk)
    product_access = Product_Accessory_Form(product)
    FORMSET = modelformset_factory(
        Product_Accessories_Kit, product_access,  extra=1, can_delete=True)

    accessory_formset = FORMSET(
        queryset=Product_Accessories_Kit.objects.none(), prefix="product_accessory")
    if request.method == "POST":
        title = request.POST.get("product_accessory_title")
        accessory_formset = FORMSET(request.POST, prefix="product_accessory")
        main_access = Product_Accessories.objects.create(
            product=product, product_accessories_title=title)
        if accessory_formset.is_valid():
            for item in accessory_formset:
                item_obj = item.save(commit=False)
                if item_obj.accessory:
                    item_obj.product_accessory = main_access
                    item_obj.save()
        else:
            messages.error(request, accessory_formset.errors)
        return redirect('configuration_product_accessories_settings', pk=product.id)
    return render(request, "Master_settings/Products_Master/product_accessory_modal.html", {"product": product, "formset": accessory_formset})


@login_required(login_url="signin")
def delete_product_accessories(request, pk):
    """
    This function deletes a product accessory and its associated accessories from the database.
    """
    accessory_kit = Product_Accessories.objects.get(pk=pk)
    try:
        accessories = Product_Accessories_Kit.objects.filter(
            product_accessory=accessory_kit).delete()
        accessory_kit.delete()
    except Exception as e:
        messages.error(request, "Product Accessory can't delete..")
    return redirect("configuration_product_accessories_settings", pk=accessory_kit.product.id)


@login_required(login_url="signin")
@permission_required(['product_master.change_product_accessories'], login_url='permission_not_allowed')
def edit_product_accessory(request, pk):
    """
    This function edits a product accessory and its associated kit items.
    
    """
    accessory_bundle = Product_Accessories.objects.get(pk=pk)
    product_access = Product_Accessory_Form(accessory_bundle.product)
    FORMSET = modelformset_factory(Product_Accessories_Kit, product_access,  extra=1, can_delete=True)
    accessory_formset = FORMSET(queryset=Product_Accessories_Kit.objects.filter(
        product_accessory=accessory_bundle.id), prefix="product_accessory")
    if request.method == "POST":
        accessory_formset = FORMSET(request.POST, queryset=Product_Accessories_Kit.objects.filter(
            product_accessory=accessory_bundle.id), prefix="product_accessory")

        if accessory_formset.is_valid():
            for item in accessory_formset:
                item_obj = item.save(commit=False)
                if item_obj.accessory:
                    item_obj.product_accessory = accessory_bundle
                    item_obj.save()
        else:
            messages.error(request, accessory_formset.errors)
        return redirect('configuration_product_accessories_settings', pk=accessory_bundle.product.id)
    return render(request, "Master_settings/Products_Master/product_accessory_modal.html", {"product": accessory_bundle, "formset": accessory_formset})


@login_required(login_url='signin')
@permission_required(['product_master.delete_product_accessories'], login_url='permission_not_allowed')
def delete_accessory_from_bundle(request, pk):
    """
    This function deletes a product accessory kit from a bundle and returns a JSON response indicating
    success or failure.
    
    """
    Product_Accessories_Kit.objects.get(pk=pk).delete()
    return JsonResponse({"success": False})


@login_required(login_url='signin')
def list_secondary_products(request):
    
    # sec_product_objs = SecondaryProducts.objects.filter(active=True)
    
    sec_product_objs = Product.objects.filter(product_type=2)
    
    context = {
        "title": f"{PROJECT_NAME} | Secondary Products",
        "sec_product_objs": sec_product_objs,

    }
    return render(request, "Master_settings/Secondary_products/secondary_products.html", context)


@login_required(login_url='signin')
def secondary_products_add(request):
    
    form = CreateSecondaryProduct()
    url = '/Products_master/secondary_products_add/'
    PRODUCT_WORKSTATIONFORMSET = modelformset_factory(Product_WorkStations, form=CreateProductWorkstations, can_delete=True)
    product_workstation_formset = PRODUCT_WORKSTATIONFORMSET(
                                        queryset=Product_WorkStations.objects.none(), 
                                        prefix="product_workstation_formset"
                                    )
    
    if request.method == 'POST':
        form = CreateSecondaryProduct(request.POST, request.FILES)
        product_workstation_formset = PRODUCT_WORKSTATIONFORMSET(request.POST, prefix="product_workstation_formset")
        
        if form.is_valid():
            obj = form.save()
            obj.created_by = request.user
            obj.product_type = 2
            obj.save()
            
            for item in product_workstation_formset:
                if item.is_valid():
                    item_obj = item.save(commit=False)
                    item_obj.product = obj
                    item_obj.save()
                else:
                    print('Error==>', item.errors)
                    
        else:
            messages.error(request, form.errors)
        return redirect('list_secondary_products')

    context = {
        "form": form,
        "url": url,
        "product_workstation_formset": product_workstation_formset,
    }
    return render(request, "Master_settings/Secondary_products/secondary_product_add.html", context)    



@login_required(login_url='signin')
def secondary_products_update(request, pk):
    # secondary_product_obj = SecondaryProducts.objects.get(pk=pk)
    secondary_product_obj = Product.objects.get(pk=pk)
    form = CreateSecondaryProduct(instance=secondary_product_obj)
    url = f'/Products_master/secondary_products_update/{secondary_product_obj.id}/'
    
    PRODUCT_WORKSTATIONFORMSET = modelformset_factory(Product_WorkStations, form=CreateProductWorkstations, can_delete=True)
    product_workstation_formset = PRODUCT_WORKSTATIONFORMSET(
                                        queryset=Product_WorkStations.objects.filter(product=secondary_product_obj), 
                                        prefix="product_workstation_formset"
                                    )
    
    if request.method == 'POST':
        form = CreateSecondaryProduct(request.POST, request.FILES, instance=secondary_product_obj)
        product_workstation_formset = PRODUCT_WORKSTATIONFORMSET(request.POST, prefix="product_workstation_formset")
        
        if form.is_valid():
            item_obj = form.save(commit=True)
            # item_obj.product_type = 2
            item_obj.save()
            
            for item in product_workstation_formset:
                if item.is_valid():
                    item_obj = item.save(commit=False)
                    item_obj.product = secondary_product_obj
                    item_obj.save()
                    print("HAKS")
                else:
                    print('Error==>', item.errors)
                    
        else:
            messages.error(request, form.errors)
        return redirect('list_secondary_products')

    context = {
        "form": form,
        "url": url,
        "secondary_product_obj": secondary_product_obj,
        "product_workstation_formset": product_workstation_formset,
    }
    return render(request, "Master_settings/Secondary_products/secondary_product_add.html", context)    



@login_required(login_url='signin')
@permission_required(['product_master.delete_product'], login_url='permission_not_allowed')
def secondary_product_delete(request, pk):
    """
    This function deletes a product object and redirects to the category-wise products page, while
    displaying an error message if the object is already in use.
    
    """
    if request.method == "POST":
        # secondary_product_obj = SecondaryProducts.objects.get(pk=pk)
        secondary_product_obj = Product.objects.get(pk=pk)
        try:
            secondary_product_obj.delete()
            messages.success(request, f"Successfuly Deleted Secondary Product {secondary_product_obj.product_name}")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_secondary_products')
    context = {"url": f"/Products_master/secondary_product_delete/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)




