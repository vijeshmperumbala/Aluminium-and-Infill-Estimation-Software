from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from apps.Categories.models import Category
from django.http import JsonResponse

from apps.brands.forms import (
        CreateBaseBrands, 
        CreateCategoryBrandForm, 
        CreateAccessoryBrandForm,
    )
from apps.brands.models import (
        AccessoriesBrands, 
        Brands, 
        CategoryBrands,
    )
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
# @permission_required([
#                 'brands.add_accessoriesbrands', 'brands.add_categorybrands', 
#                 'brands.view_categorybrands', 'brands.view_accessoriesbrands',
#                 'brands.add_brands', 'brands.view_brands',
#                 ], login_url='permission_not_allowed')
def list_brands(request):
    """
    This function retrieves all categories and renders a template with the categories as context.
    """
    categories = Category.objects.all().order_by('id')
    brands = Brands.objects.all()
    
    context = {"title": f"{PROJECT_NAME} | Brands List", "categories": categories, "brands": brands}
    
    return render(request, 'Master_settings/Brands/brands.html', context)


@login_required(login_url='signin')
def create_category_brand(request, pk):
    """
    This function creates a new category brand and associates it with a specific category.
    
    """
    form = CreateCategoryBrandForm()
    if request.method == 'POST':
        form = CreateCategoryBrandForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.category_id = pk 
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Category Brand Created Successfully")
        else:
            messages.error(request, form.errors)
        return redirect('list_brands')
    context = {
        "form": form,
        "category": pk,
    }
    return render(request, 'Master_settings/Brands/add_category_brands_modal.html', context)


@login_required(login_url='signin')
def update_category_brand(request, pk):
    """
    This function updates a category brand instance and redirects to the list of brands page.
    """
    data = CategoryBrands.objects.get(pk=pk)
    form = CreateCategoryBrandForm(instance=data)
    if request.method == 'POST':
        form = CreateCategoryBrandForm(request.POST, instance=data)
        if form.is_valid():
            form.save()
            messages.success(request, "Category Brand Updated Successfully")
        else:
            messages.error(request, form.errors)
        return redirect('list_brands')
    context = {
        "form": form,
        "category": data.id,
    }
    return render(request, 'Master_settings/Brands/update_category_brands_modal.html', context)

@login_required(login_url='signin')
def delete_category_brand(request, pk):
    """
    This function deletes a CategoryBrands object with the given primary key and returns a success
    message or an error message if the object is already in use.
    
    """
    try: 
        CategoryBrands.objects.get(pk=pk).delete()
        messages.success(request, "Brand Successfully Deleted.")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
    return JsonResponse({'success': True}, status=200)


@login_required(login_url='signin')
def create_accessory_brand(request, pk):
    """
    This function creates a new accessory brand and associates it with a specific category.
    """
    form = CreateAccessoryBrandForm(request.POST)
    if request.method == 'POST':
        form = CreateAccessoryBrandForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.category_id = pk
            obj.save()
            messages.success(request, "Accessory Brand Created Successfully")
        else:
            messages.error(request, form.errors)
        return redirect('list_brands')
    context = {
        "form": form,
        "category": pk,
    }
    return render(request, 'Master_settings/Brands/add_category_brands_modal.html', context)



@login_required(login_url='signin')
def update_accessory_brand(request, pk):
    """
    This function updates an accessory brand in the database based on the provided primary key.
    """
    data = AccessoriesBrands.objects.get(pk=pk)
    form = CreateAccessoryBrandForm(instance=data)
    if request.method == 'POST':
        form = CreateAccessoryBrandForm(request.POST, instance=data)
        if form.is_valid():
            form.save()
            messages.success(request, "Accessory Brand Updated Successfully")
        else:
            messages.error(request, form.errors)
        return redirect('list_brands')
    context = {
        "form": form,
        "category": data.id,
    }
    return render(request, 'Master_settings/Brands/update_category_brands_modal.html', context)


@login_required(login_url='signin')
def delete_accessory_brand(request, pk):
    """
    This function deletes an accessory brand and returns a success message or an error message if the
    brand is already in use.
    """
    try: 
        AccessoriesBrands.objects.get(pk=pk).delete()
        messages.success(request, "Brand Successfully Deleted.")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
    return JsonResponse({'success': True}, status=200)


@login_required(login_url='signin')
def create_base_brand(request):
    """
    The function `create_base_brand` is used to handle the creation of a base brand object in a Django
    web application.
    """
    forms = CreateBaseBrands()
    if request.method == 'POST':
        forms = CreateBaseBrands(request.POST)
        if forms.is_valid():
            forms_obj = forms.save(commit=False)
            forms_obj.created_by = request.user
            forms_obj.save()
            messages.success(request, "Successfully Added Brand.")
        else:
            messages.error(request, forms.errors)
        return redirect('list_brands')
    
    context = {
        "forms": forms,
    }
    return render(request, "Master_settings/Brands/add_base_brand.html", context)
            
            
@login_required(login_url='signin')
def edit_base_brand(request, pk):
    """
    The function `edit_base_brand` is used to edit and update a brand object in a Django web
    application.
    
    """
    brand = Brands.objects.get(pk=pk)
    forms = CreateBaseBrands(instance=brand)
    if request.method == 'POST':
        forms = CreateBaseBrands(request.POST, instance=brand)
        if forms.is_valid():
            forms_obj = forms.save(commit=False)
            forms_obj.save()
            messages.success(request, "Successfully Updated Brand.")
        else:
            messages.error(request, forms.errors)
        return redirect('list_brands')
    
    context = {
        "forms": forms,
        "brand": brand,
    }
    return render(request, "Master_settings/Brands/add_base_brand.html", context)


@login_required(login_url='signin')
def delete_base(request, pk):
    """
        The function `delete_base` deletes a Brands object with the specified primary key (pk) and displays
        a success message if the deletion is successful, otherwise it displays an error message.
       
    """
    if request.method == "POST":
        try:
            brands = Brands.objects.get(pk=pk)
            brands.delete()
            messages.success(request, "Brand Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_brands')

    context = {"url": f"/Brands/delete_base/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)