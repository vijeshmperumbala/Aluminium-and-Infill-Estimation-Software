from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from apps.shopfloors.models import Shopfloors
from apps.shopfloors.forms import ShopFloorForm
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
def shopfloor_list(request):
    """
    This function displays a list of shop floors and allows the user to create a new shop floor.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the user's session and any submitted form data
    :return: an HTTP response generated by the `render` method, which renders a template called
    "shopfloors.html" with the given context dictionary. The template will display a list of shop floors
    and a form to create a new shop floor. If the request method is POST and the form is valid, a new
    shop floor will be created and the user will be redirected to the same page
    """
    shopfloor_list = Shopfloors.objects.all().order_by('-id')
    create_form = ShopFloorForm()
    if request.method == "POST":
        create_form = ShopFloorForm(request.POST)
        if create_form.is_valid():
            create_form_obj = create_form.save(commit=False)
            create_form_obj.created_by = request.user
            create_form_obj.save()
            messages.success(request, "Successfully Created Shop Floor.")
        else:
            messages.error(request, create_form.errors)
        return redirect('shopfloor_list')

    context = {
        "title": PROJECT_NAME+" | ShopFloors",
        "shopfloor_list": shopfloor_list,
        "create_form": create_form,
    }
    return render(request, "Master_settings/ShopFloors/shopfloors.html", context)
    
    
@login_required(login_url='signin')
def shopfloor_update(request, pk):
    """
    This function updates a shop floor object in the database and displays a success or error message.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: pk is a parameter that represents the primary key of a Shopfloors object. It is used to
    retrieve the specific Shopfloors object from the database that needs to be updated
    :return: an HTTP response rendered using a template called "update_shopfloor.html". The context
    dictionary contains the title of the page, the shop floor object being updated, and an instance of
    the ShopFloorForm for editing the shop floor object. If the request method is POST and the form is
    valid, the shop floor object is updated with the new data and a success message is displayed. If
    """
    shop_floor = Shopfloors.objects.get(pk=pk)
    edit_form = ShopFloorForm(instance=shop_floor)
    if request.method == "POST":
        edit_form = ShopFloorForm(request.POST, instance=shop_floor)
        if edit_form.is_valid():
            edit_form_obj = edit_form.save(commit=False)
            edit_form_obj.last_modified_date = time()
            edit_form_obj.last_modified_by = request.user
            edit_form_obj.save()
            messages.success(request, "Successfully Updated Shop Floor.")
        else:
            messages.error(request, edit_form.errors)
        return redirect('shopfloor_list')
    context = {
        "title": PROJECT_NAME+" | ShopFloors",
        "shop_floor": shop_floor,
        "edit_form": edit_form,
    }
    return render(request, "Master_settings/ShopFloors/update_shopfloor.html", context)


@login_required(login_url='signin')
# @permission_required(['accessories_master.delete_accessories'], login_url='permission_not_allowed')
def shopfloor_delete(request, pk):
    """
    This function deletes a shop floor object and displays a success or error message depending on
    whether the deletion was successful or not.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the user making the request and any data submitted with the request
    :param pk: pk is a parameter that represents the primary key of a Shopfloors object that needs to be
    deleted. It is used to identify the specific object that needs to be deleted from the database
    :return: a rendered HTML template for a delete confirmation modal dialog box. If the request method
    is POST, it will attempt to delete a Shopfloors object with the given primary key (pk) and redirect
    to the shopfloor_list page. If the deletion is not possible due to the object being used in an
    application, it will display an error message.
    """
    if request.method == "POST":
        try:
            shop_floor = Shopfloors.objects.get(pk=pk)
            shop_floor.delete()
            messages.success(request, "Shop Floor Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('shopfloor_list')

    context = {
        "url": "/ShopFlowrs/shopfloor_delete/"+str(pk)+"/",
    }
    return render(request, "Master_settings/delete_modal.html", context)