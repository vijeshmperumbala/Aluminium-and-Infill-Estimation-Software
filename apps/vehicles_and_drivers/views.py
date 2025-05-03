from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
import json

import random

from apps.vehicles_and_drivers.models import Vehicles, Drivers
from apps.vehicles_and_drivers.forms import CreateDriverForm, CreateVehicleForm
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
def list_vehicles_and_drivers(request):
    """
    This function retrieves all vehicles and drivers objects from the database and renders them in a
    template.
    
    :param request: The request object represents the current HTTP request that the user has made to the
    server. It contains information about the user's request, such as the URL, headers, and any data
    that was submitted with the request
    :return: a rendered HTML template with a context that includes a title, a queryset of all Vehicles
    objects ordered by their id in descending order, and a queryset of all Drivers objects ordered by
    their id in descending order.
    """

    vehicles_obj = Vehicles.objects.all().order_by('-id')
    drivers_obj = Drivers.objects.all().order_by('-id')

    context = {
        "title": PROJECT_NAME + " | Vehicles and Drivers.",
        "vehicles_obj": vehicles_obj,
        "drivers_obj": drivers_obj,
    }
    return render(request, "Master_settings/Vehicles_and_Drivers/list.html", context)


@login_required(login_url="signin")
def add_vehicles_and_drivers(request, type):
    """
    This function adds new drivers or vehicles to a database and displays a form for the user to input
    the necessary information.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param type: The type of form to be displayed, either 'driver' or 'vehicle'
    :return: a rendered HTML template with a form for creating a new driver or vehicle, depending on the
    value of the 'type' parameter. If the request method is POST and the form is valid, the new driver
    or vehicle is saved and a success message is displayed. If the form is not valid, an error message
    is displayed. Finally, the function redirects to a view that lists all
    """
    if type == 'driver':
        form = CreateDriverForm()
    elif type == 'vehicle':
        form = CreateVehicleForm()
    else:
        pass

    if request.method == "POST":
        if type == 'driver':
            form = CreateDriverForm(request.POST)
        elif type == 'vehicle':
            form = CreateVehicleForm(request.POST)
        else:
            pass

        if form.is_valid():
            form.save()
            messages.success(request, "Successfully Created.")
        else:
            messages.error(request, form.errors)

        return redirect('list_vehicles_and_drivers')
    context = {
        "form": form,
        "type": type,
    }
    return render(request, "Master_settings/Vehicles_and_Drivers/add_new_vehicles_and_drivers.html", context)


@login_required(login_url='signin')
def update_vehicles_and_drivers(request, pk, type):
    """
    This function updates information for either a driver or a vehicle and saves the changes to the
    database.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: pk stands for primary key, which is a unique identifier for a specific object in a
    database table. In this case, it is used to retrieve a specific driver or vehicle object from the
    database
    :param type: The type parameter is a string that specifies whether the item being updated is a
    driver or a vehicle. It is used to determine which form to display and which model to query from the
    database
    :return: a rendered HTML template with a form to update either a driver or a vehicle, depending on
    the 'type' parameter passed to the function. If the form is submitted and valid, the item is updated
    and a success message is displayed. If the form is not valid, an error message is displayed.
    Finally, the function redirects to a list view of all vehicles and drivers.
    """
    if type == 'driver':
        item = Drivers.objects.get(pk=pk)
        form = CreateDriverForm(instance=item)
    elif type == 'vehicle':
        item = Vehicles.objects.get(pk=pk)
        form = CreateVehicleForm(instance=item)
    else:
        pass

    if request.method == "POST":
        if type == 'driver':
            form = CreateDriverForm(request.POST, instance=item)
        elif type == 'vehicle':
            form = CreateVehicleForm(request.POST, instance=item)
        else:
            pass

        if form.is_valid():
            form.save()
            messages.success(request, "Successfully Updated.")
        else:
            messages.error(request, form.errors)

        return redirect('list_vehicles_and_drivers')

    context = {
        "form": form,
        "type": type,
        "item": item,
    }
    return render(request, "Master_settings/Vehicles_and_Drivers/add_new_vehicles_and_drivers.html", context)


@login_required(login_url='signin')
# @permission_required(['accessories_master.delete_accessories'], login_url='permission_not_allowed')
def vehicles_and_drivers_delete(request, pk, type):
    """
    This function deletes a driver or vehicle object based on the type parameter and displays a success
    or error message.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: The primary key of the object to be deleted (either a driver or a vehicle)
    :param type: The type parameter is a string that specifies whether the item to be deleted is a
    driver or a vehicle. It is used to determine which model to query and which success message to
    display after the item is deleted
    :return: a rendered HTML template for a delete confirmation modal dialog box. The context variable
    contains the URL for the delete view, which is used in the modal form action.
    """
    
    if type == 'driver':
        item = Drivers.objects.get(pk=pk)
    elif type == 'vehicle':
        item = Vehicles.objects.get(pk=pk)
    else:
        pass
    
    if request.method == "POST":
        try:
            item.delete()
            if type == 'driver':
                messages.success(request, "Driver Deleted Successfully")
            else:
                messages.success(request, "Vehicle Deleted Successfully")
                
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_vehicles_and_drivers')

    context = {
        "url": "/vehicles_and_drivers/vehicles_and_drivers_delete/"+str(pk)+"/"+str(type)+"/",
    }
    return render(request, "Master_settings/delete_modal.html", context)