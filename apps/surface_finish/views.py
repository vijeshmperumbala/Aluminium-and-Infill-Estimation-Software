from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from apps.pricing_master.models import Surface_finish_kit

from apps.surface_finish.models import Surface_finish, SurfaceFinishColors
from apps.surface_finish.forms import CreateSurfaceFinishForm, EditSurfaceFinishForm, SurfaceFinishColorsForm
from amoeba.settings import PROJECT_NAME


@login_required(login_url='signin')
@permission_required(['surface_finish.view_surface_finish', 'surface_finish.add_surface_finish', 'surface_finish.add_surface_finish'], login_url='permission_not_allowed')
def surface_finish_list(request, pk=None):
    """
    This function displays a list of surface finishes and allows the user to create and edit surface
    finishes.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the method (GET, POST, etc.), headers, and user information
    :param pk: pk is a parameter that represents the primary key of a specific Surface_finish object. It
    is used to retrieve and edit a specific object from the database. If a pk value is provided in the
    URL, the view will retrieve the corresponding Surface_finish object and populate the edit form with
    its data
    :return: an HTTP response with a rendered HTML template
    'Master_settings/Surface_Finish/surface_finish.html' and a context dictionary containing the title,
    create_form, surface_finish_obj, and edit_form.
    """
    surface_finish_obj = Surface_finish.objects.all().order_by('id')
    create_form = CreateSurfaceFinishForm()
    edit_form = EditSurfaceFinishForm()
    if pk:
        surfacefinish_obj = Surface_finish.objects.get(pk=pk)
        surfacefinish_color_objs = SurfaceFinishColors.objects.filter(surface_finish=surfacefinish_obj.id)
    else:
        surfacefinish_obj = None
        surfacefinish_color_objs = None
        
    if request.method == 'POST':
        if 'create_surface_finish' in request.POST:
            create_form = CreateSurfaceFinishForm(request.POST)
            if create_form.is_valid():
                create_obj = create_form.save(commit=False)
                create_obj.created_by = request.user
                create_obj.save()
                messages.success(request, "Surface Finish Created Successfully")
                return redirect('surface_finish_list')
            else:
                messages.error(request, create_form.errors)
        else:
            edit_form = EditSurfaceFinishForm(
                request.POST, instance=surfacefinish_obj)
            if edit_form.is_valid():
                edit_obj = edit_form.save()
                edit_obj.last_modified_date = time()
                edit_obj.last_modified_by = request.user
                edit_obj.save()
                messages.success(request, "Surface Finish Updated Successfully")
                return redirect('surface_finish_list')
            else:
                messages.error(request, edit_form.errors)
                
        
    context = {
        "title": PROJECT_NAME + " | Surface Finish List",
        "create_form": create_form,
        "surface_finish_obj": surface_finish_obj,
        "edit_form": edit_form,
        "surfacefinish_obj": surfacefinish_obj,
        "pk": pk,
        "surfacefinish_color_objs": surfacefinish_color_objs,
    }
    return render(request, 'Master_settings/Surface_Finish/surface_finish.html', context)


@login_required(login_url='signin')
@permission_required(['surface_finish.delete_surface_finish'], login_url='permission_not_allowed')
def surface_finish_delete(request, pk):
    """
    This function deletes a surface finish object and displays a success message, or an error message if
    the object is already in use.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and any data submitted in the request
    :param pk: pk stands for primary key. In Django, every model has a primary key field that uniquely
    identifies each instance of the model. In this case, the pk parameter is used to retrieve a specific
    instance of the Surface_finish model based on its primary key value
    :return: a redirect to the 'surface_finish_list' URL.
    """
    surface_finish_obj = Surface_finish.objects.get(pk=pk)
    try:
        surface_finish_obj.delete()
        messages.success(request, "Surface Finish Deleted Successfully")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("Delete is not possible.")
    return redirect('surface_finish_list')


@login_required(login_url='signin')
def get_surface_price(request, pk):
    """
    The function retrieves the price of a surface finish kit object and returns it as a JSON response.
    
    :param request: The request object represents the HTTP request that the view function received from
    the client
    :param pk: pk stands for "primary key" and is a unique identifier for a specific record in a
    database table. In this case, it is used to retrieve a specific Surface_finish_kit object from the
    database based on its primary key value
    :return: a JSON response containing the price of a surface finish kit object with the primary key
    (pk) specified in the function argument.
    """
    
    surface_finish_obj = Surface_finish_kit.objects.get(pk=pk)
    data = {
        'price': surface_finish_obj.surface_finish_price
    }
    return JsonResponse(data, status=200)


@login_required(login_url='signin')
def create_sf_color(request, pk):
    surface_finish_obj = Surface_finish.objects.get(pk=pk)
    form = SurfaceFinishColorsForm()
    if request.method == 'POST':
        form = SurfaceFinishColorsForm(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.surface_finish = surface_finish_obj
            form_obj.save()
            messages.success(request, "Surface Finish Color Added Successfully")
        else:
            messages.error(request, form.errors)
        
        return redirect("surface_finish_list", pk=surface_finish_obj.id)
    
    context = {
        "surface_finish_obj": surface_finish_obj,
        "form": form,
    }
    return render(request, "Master_settings/Surface_Finish/add_color.html", context)


@login_required(login_url='signin')
def update_sf_color(request, pk):
    surface_finish_color_obj = SurfaceFinishColors.objects.get(pk=pk)
    form = SurfaceFinishColorsForm(instance=surface_finish_color_obj)
    if request.method == 'POST':
        form = SurfaceFinishColorsForm(request.POST, instance=surface_finish_color_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Surface Finish Color Updated Successfully")
        else:
            messages.error(request, form.errors)
        
        return redirect("surface_finish_list", pk=surface_finish_color_obj.surface_finish.id)
    
    context = {
        "surface_finish_obj": surface_finish_color_obj.surface_finish,
        "surface_finish_color_obj": surface_finish_color_obj,
        "form": form,
    }
    return render(request, "Master_settings/Surface_Finish/add_color.html", context)


@login_required(login_url='signin')
def delete_secondary_product(request, pk):
    # secondary_product_obj = SalesOrderItems_Secondary_Product.objects.get(pk=pk)
    surface_finish_color_obj = SurfaceFinishColors.objects.get(pk=pk)
    if request.method == "POST":
        try:
            surface_finish_color_obj.delete()
            messages.success(request, "Surface Finish Color Deleted Successfully")
        except Exception as e:
            print("EEE==>", e)
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")

        return redirect('surface_finish_list', pk=surface_finish_color_obj.surface_finish.id)

    context = {"url": f"/Surface_Finish/surface_finish_list/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


