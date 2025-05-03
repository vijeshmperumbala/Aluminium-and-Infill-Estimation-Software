
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.associated_product.forms import CreateAssociatedProductForm
from apps.associated_product.models import AssociatedProducts
from amoeba.settings import PROJECT_NAME


# def list_associated_products(request, pk=None):
#     """
#     This function lists and allows editing or creating associated products in a web application.
    
#     :param request: The HTTP request object that contains metadata about the request being made, such as
#     the user agent, headers, and data
#     :param pk: pk is a parameter that represents the primary key of an AssociatedProduct object. It is
#     used to retrieve a specific AssociatedProduct object from the database and to edit it. If pk is
#     None, it means that the view is being used to list all the AssociatedProduct objects or to create a
#     new one
#     :return: The function `list_associated_products` returns either a rendered HTML template for editing
#     an associated product or a rendered HTML template for listing all associated products, depending on
#     whether a primary key (`pk`) is provided in the request or not.
#     """
#     associated_products = AssociatedProducts.objects.all().order_by('id')
#     if pk:
#         associated_product = AssociatedProducts.objects.get(pk=pk)
#         form = CreateAssociatedProductForm(instance=associated_product)
#         if request.method == 'POST':
#             form = CreateAssociatedProductForm(request.POST, instance=associated_product)
#             if form.is_valid():
#                 form_obj = form.save(commit=False)
#                 form_obj.last_modified_date = time()
#                 form_obj.last_modified_by = request.user
#                 form_obj.save()
#                 messages.success(request, f'Successfully Updated {form_obj.product_name}')
#             else:
#                 messages.error(request, form.errors)
#             return redirect("list_associated_products")
#         context = {
#             'title': f'{PROJECT_NAME} | Associated Product',
#             'associated_products': associated_products,
#             'associated_product': associated_product,
#             'form': form,
#         }
#         return render(request, "Master_settings/Associated_Products/edit_associated_product.html", context)
#     else:
#         form = CreateAssociatedProductForm()
#         if request.method == 'POST':
#             form = CreateAssociatedProductForm(request.POST)
#             if form.is_valid():
#                 form_obj = form.save(commit=False)
#                 form_obj.created_by = request.user
#                 form_obj.created_date = time()
#                 form_obj.save()
#                 messages.success(request, f'Successfully Added {form_obj.product_name}')
#             else:
#                 messages.error(request, form.errors)
#             return redirect("list_associated_products")
#         context = {
#             'title': f'{PROJECT_NAME} | Associated Product',
#             'associated_products': associated_products,
#             'form': form,
#         }
#         return render(request, "Master_settings/Associated_Products/list_associated_products.html", context)

@login_required(login_url='signin')
def list_associated_products(request, pk=None):
    """
    The function `list_associated_products` retrieves a list of associated products and either creates a
    new associated product or edits an existing one based on the provided primary key.
    """
    associated_products = AssociatedProducts.objects.all().order_by('id')
    
    if pk:
        return edit_associated_product(request, associated_products, pk)
    else:
        return create_associated_product(request, associated_products)


def edit_associated_product(request, associated_products, pk):
    """
    The function `edit_associated_product` is used to edit an associated product in a web application.
    
    """
    associated_product = AssociatedProducts.objects.get(pk=pk)
    form = CreateAssociatedProductForm(instance=associated_product)
    
    if request.method == 'POST':
        form = CreateAssociatedProductForm(request.POST, instance=associated_product)
        if form.is_valid():
            update_associated_product(form, request)
            messages.success(request, f'Successfully Updated {associated_product.product_name}')
        else:
            messages.error(request, form.errors)
        return redirect("list_associated_products")
    
    context = {
        'title': f'{PROJECT_NAME} | Associated Product',
        'associated_products': associated_products,
        'associated_product': associated_product,
        'form': form,
    }
    return render(request, "Master_settings/Associated_Products/edit_associated_product.html", context)


def update_associated_product(form, request):
    """
    The function updates the associated product with the information from the form and saves the
    changes.
    """
    form_obj = form.save(commit=False)
    form_obj.last_modified_date = time()
    form_obj.last_modified_by = request.user
    form_obj.save()


def create_associated_product(request, associated_products):
    """
    The function creates an associated product using a form and redirects to a list of associated
    products.
    """
    form = CreateAssociatedProductForm()
    
    if request.method == 'POST':
        form = CreateAssociatedProductForm(request.POST)
        if form.is_valid():
            create_associated_product_instance(form, request)
        else:
            messages.error(request, form.errors)
        return redirect("list_associated_products")
    
    context = {
        'title': f'{PROJECT_NAME} | Associated Product',
        'associated_products': associated_products,
        'form': form,
    }
    return render(request, "Master_settings/Associated_Products/list_associated_products.html", context)

def create_associated_product_instance(form, request):
    """
    The function creates an instance of an associated product with the provided form data and saves it
    to the database.
    """
    form_obj = form.save(commit=False)
    form_obj.created_by = request.user
    form_obj.created_date = time()
    form_obj.save()
    messages.success(request, f'Successfully Added {form_obj.product_name}')
    
    
    
@login_required(login_url='signin')
def delete_associated_product(request, pk):
    """
    This function deletes an associated product and displays a success message if the deletion is
    successful, otherwise it displays an error message.
    
    """
    associated_product = AssociatedProducts.objects.get(pk=pk)
    try:
        associated_product.delete()
        messages.success(request, "Associated Product Deleted Successfully")
    except Exception as e:
        messages.error(request, "Unable to Delete the Data. Already used in Application.")
    return redirect('list_associated_products')