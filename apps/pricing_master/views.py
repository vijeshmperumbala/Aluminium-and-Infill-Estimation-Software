from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import modelformset_factory

from apps.pricing_master.models import (
                    AdditionalandLabourPriceMaster, 
                    PriceMaster, 
                    Sealant_kit, 
                    SealantPriceMaster, 
                    Surface_finish_Master, 
                    Surface_finish_kit,
)
from apps.pricing_master.forms import (
                    CreateAdditionalandLabourForm, 
                    CreatePricingForm, 
                    CreateSealantForm,
                    CreateSurfaceFinishMaster, 
                    EditPricingForm, 
                    EditSealantForm,
)
from amoeba.settings import PROJECT_NAME
from apps.surface_finish.models import Surface_finish


@login_required(login_url="signin")
@permission_required(['pricing_master.view_pricemaster', 'pricing_master.add_pricemaster'], login_url='permission_not_allowed')
def list_price_master(request):
    """
    This function handles the creation and display of pricing information for various products and
    services.
    
    """
    price_obj_international = PriceMaster.objects.filter(type=1).order_by('-id')
    price_obj_local = PriceMaster.objects.filter(type=2).order_by('-id')
    additional_obj = AdditionalandLabourPriceMaster.objects.all().order_by('-id')
    sealant_obj = SealantPriceMaster.objects.all().order_by('-id')
    surface_finish_master_obj = Surface_finish_Master.objects.all().order_by('-id')
    form = CreatePricingForm()
    additional_form = CreateAdditionalandLabourForm()
    
    SEALANTFORMSET = modelformset_factory(Sealant_kit, form=CreateSealantForm, extra=1, can_delete=True)
    sealant_form = SEALANTFORMSET(queryset=SealantPriceMaster.objects.none(), prefix="sealant_price")
    surface_finish_form = CreateSurfaceFinishMaster()
    surafec_finish_obj = Surface_finish.objects.all().order_by('id')
    
    if request.method == 'POST':
        price_date = request.POST.get('price_date')
        total_price = request.POST.get('total_price')
        title = request.POST.get('title')
        form = CreatePricingForm(request.POST)
        sealant_form = SEALANTFORMSET(request.POST, prefix="sealant_price")
        additional_form = CreateAdditionalandLabourForm(request.POST)
        surface_finish_form = CreateSurfaceFinishMaster(request.POST)
        
        if 'pricing' in request.POST:
            if form.is_valid():
                form_obj = form.save()
                form_obj.created_by = request.user
                form_obj.date = price_date
                form_obj.total_price = total_price
                form_obj.save()
            else:
                messages.error(request, form.errors)
        elif 'additional' in request.POST:
            if additional_form.is_valid():
                additional_form_obj = additional_form.save()
                additional_form_obj.created_by = request.user
                additional_form_obj.save()
            else:
                messages.error(request, additional_form.errors)
        elif 'sealant_add' in request.POST:
            sealant_master = SealantPriceMaster(created_by=request.user, created_date=time(), name=title)
            sealant_master.save()
            for item in sealant_form:
                if item.is_valid():
                    sealant_form_obj = item.save(commit=False)
                    price = (float(sealant_form_obj.sealant_markup/100)*float(sealant_form_obj.normal_price))+float(sealant_form_obj.normal_price)
                    sealant_form_obj.price = float(price)
                    sealant_form_obj.pricing_master=sealant_master
                    sealant_form_obj.save()
                else:
                    messages.error(request, item.errors)
        elif 'surface_finish_add' in request.POST:
            if surface_finish_form.is_valid():
                surface_finish_form_obj = surface_finish_form.save()
                surface_finish = request.POST.getlist('surface_finish')
                surface_finish_price = request.POST.getlist('surface_finish_price')
                for i, item in enumerate(surface_finish):
                    kit_data = Surface_finish_kit(surface_finish_price=float(surface_finish_price[i]), surface_finish_id=int(item), master=surface_finish_form_obj)
                    kit_data.save()
                messages.success(request, "successfully Added Surface Finish Price")
            else:
                messages.error(request, surface_finish_form.errors)
        else:
            print("ERROR")
        return redirect('list_price_master')

    context = {
        "title": PROJECT_NAME + " | Price Master List",
        "price_obj_international": price_obj_international,
        "price_obj_local": price_obj_local,
        "form": form,
        "additional_form": additional_form,
        "additional_obj": additional_obj,
        "sealant_obj": sealant_obj,
        "sealant_form": sealant_form,
        "surface_finish_form": surface_finish_form,
        "surface_finish_master_obj": surface_finish_master_obj,
        "surafec_finish_obj": surafec_finish_obj,
    }
    return render(request, "Master_settings/Pricing_Master/pricing_master_base.html", context)


@login_required(login_url="signin")
@permission_required(['pricing_master.change_pricemaster'], login_url='permission_not_allowed')
def edit_price_master(request, pk):
    """
    It takes the price_obj, which is a PriceMaster object, and then it takes the form, which is an
    EditPricingForm object, and then it takes the price_date, which is a string, and then it takes the
    total_price, which is a string.
    
    """
    price_obj = PriceMaster.objects.get(pk=pk)
    form = EditPricingForm(instance=price_obj)
    price_date = request.POST.get('price_date')
    total_price = request.POST.get('total_price2')

    if request.method == 'POST':
        form = EditPricingForm(request.POST, instance=price_obj)
        if form.is_valid():
            form_obj = form.save()
            if not str(price_obj.date.date()) == str(price_date):
                form_obj.date = price_date
            form_obj.last_modified_by = request.user
            form_obj.last_modified_date = time()
            form_obj.total_price = total_price
            form_obj.save()
        else:
            messages.error(request, form.errors)
        return redirect('list_price_master')
    context = {
        "title": PROJECT_NAME + " | Price Master Edit",
        "pk": price_obj,
        "form": form,
    }
    return render(request, "Master_settings/Pricing_Master/edit_price_master_modal.html", context)


@login_required(login_url="signin")
@permission_required(['pricing_master.delete_pricemaster'], login_url='permission_not_allowed')
def price_delete(request, pk):
    """
    This function deletes a price object and displays a success or error message depending on whether
    the object has been used in the application or not.
    
    """
    price_obj = PriceMaster.objects.get(pk=pk)
    if request.method == 'POST':
        try:
            price_obj.delete()
            messages.success(request, "Successfully deleted")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
        return redirect('list_price_master')
    context = {
        "url": "/Pricing_Master/price_delete/"+str(pk)+"/",
    }
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url="signin")
@permission_required(['pricing_master.delete_additionalandlabourpricemaster'], login_url='permission_not_allowed')
def additional_delete(request, pk):
    """
    This function deletes an object from a database and displays a success or error message depending on
    whether the object has been used in an application.
    
    """
    additional_obj = AdditionalandLabourPriceMaster.objects.get(pk=pk)
    if request.method == 'POST':
        try:
            additional_obj.delete()
            messages.success(request, "Successfully deleted")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("deletion not possible")
        return redirect('list_price_master')
    context = {
        "url": "/Pricing_Master/additional_delete/"+str(pk)+"/",
    }
    return render(request, "Master_settings/delete_modal.html", context)
    

@login_required(login_url="signin")
def get_pricing(request, pk):
    """
    This function retrieves the latest pricing information for a given type and returns it as a JSON
    response.
    
    """
    price = PriceMaster.objects.filter(type=pk).last()
    data = {
        "price": price.price_per_kg,
        "markup_percentage": price.markup,
        "pricing_master": price.id
        
    }
    return JsonResponse(data, status=200)


@login_required(login_url="signin")
def get_additional_data(request, pk):
    """
    The function retrieves ideal labour and overhead data for a specific object and returns it as a JSON
    response.
    
    """
    data_obj = AdditionalandLabourPriceMaster.objects.get(pk=pk)
    data = {
        "labour": data_obj.ideal_labour,
        "additional": data_obj.ideal_overhead
    }
    return JsonResponse(data, status=200)


@login_required(login_url="signin")
@permission_required(['pricing_master.change_additionalandlabourpricemaster'], login_url='permission_not_allowed')
def edit_additional_price_master(request, pk):
    """
    This function edits an instance of AdditionalandLabourPriceMaster using a form and saves the
    changes.
    
    """
    additional_obj = AdditionalandLabourPriceMaster.objects.get(pk=pk)
    form = CreateAdditionalandLabourForm(instance=additional_obj)
    if request.method == 'POST':
        form = CreateAdditionalandLabourForm(request.POST, instance=additional_obj)
        if form.is_valid():
            form_obj = form.save()
            form_obj.last_modified_by = request.user
            form_obj.last_modified_date = time()
            form_obj.save()
        else:
            messages.error(request, form.errors)
            print("Errors==>", form.errors)
        return redirect('list_price_master')
    context = {
        "pk": additional_obj.id,
        "form": form,
    }
    return render(request, "Master_settings/Pricing_Master/edit_additional_pricing_modal.html", context)


@login_required(login_url="signin")
@permission_required(['pricing_master.delete_sealantpricemaster'], login_url='permission_not_allowed')
def sealant_pricing_delete(request, pk):
    """
    This function deletes a sealant pricing object and its related sealant kits, and displays a success
    or error message.
    
    """
    sealant_obj = SealantPriceMaster.objects.get(pk=pk)
    sealant_kit = Sealant_kit.objects.filter(pricing_master=sealant_obj).order_by('id')
    for sealant in sealant_kit:
        sealant.delete()
    if request.method == 'POST':
        try:
            sealant_obj.delete()
            messages.success(request, "Successfully deleted")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("deletion not possible")
        return redirect('list_price_master')
    context = {
        "url": "/Pricing_Master/sealant_pricing_delete/"+str(pk)+"/",
    }
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url="signin")
@permission_required(['pricing_master.change_sealantpricemaster'], login_url='permission_not_allowed')
def edit_sealant_price_master(request, pk):
    """
    This function edits the pricing details of a sealant kit and updates the sealant price master.
    
    """
    sealant_obj = SealantPriceMaster.objects.get(pk=pk)
    sealant_kit_items = Sealant_kit.objects.filter(pricing_master=sealant_obj).order_by('id')
    edit_name = EditSealantForm(instance=sealant_obj)
    SEALANTFORMSET = modelformset_factory(Sealant_kit, form=CreateSealantForm, extra=1, can_delete=True)
    sealant_form = SEALANTFORMSET(queryset=SealantPriceMaster.objects.none(), prefix="sealant_price3")
    if request.method == 'POST':
        edit_name = EditSealantForm(request.POST, instance=sealant_obj)
        if edit_name.is_valid():
            edit_name.save()
        else:
            messages.error(request, edit_name.errors)
        sealant_form = SEALANTFORMSET(request.POST, prefix="sealant_price3")
        if sealant_form.is_valid():
            for item in sealant_form:
                if item.is_valid():
                    sealant_form_obj = item.save(commit=False)
                    if sealant_form_obj.normal_price == 0 or sealant_form_obj.normal_price:
                        price = (float(sealant_form_obj.sealant_markup/100)*float(sealant_form_obj.normal_price))+float(sealant_form_obj.normal_price)
                        sealant_form_obj.price = float(price)
                        sealant_form_obj.pricing_master=sealant_obj
                        sealant_form_obj.save()
                    messages.success(request, "Successfully Updated Sealant/Gasket")
                else:
                    messages.error(request, item.errors)
        else:
            messages.error(request, sealant_form.errors)
        return redirect('list_price_master')
    
    context = {
        "pk": sealant_obj.id,
        "sealant_form": sealant_form,
        "sealant_obj": sealant_obj,
        "edit_name": edit_name,
        "sealant_kit_items": sealant_kit_items
    }
    return render(request, "Master_settings/Pricing_Master/edit_sealant_pricing_modal.html", context)


@login_required(login_url="signin")
@permission_required(['pricing_master.delete_sealant_kit'], login_url='permission_not_allowed')
def delete_sealant_kit(request, pk):
    """
    This function deletes a sealant kit object and returns a JSON response indicating success or
    failure.
    
    """
    sealant_kit = Sealant_kit.objects.get(pk=pk)
    try:
        sealant_kit.delete()
        messages.success(request, "Successfully deleted")
    except Exception as e:
        messages.error(request, "Unable to delete the data. Already used in application.")
        print("deletion not possible")
    return JsonResponse({"success": True})


@login_required(login_url='signin')
def edit_surface_finish(request, pk):
    """
    This function edits the price of a surface finish kit and saves the changes to the database.
    
    """
    surface_finish = Surface_finish_Master.objects.get(pk=pk)
    surface_finish_data = Surface_finish_kit.objects.filter(master=surface_finish)
    form = CreateSurfaceFinishMaster(instance=surface_finish)
    if request.POST:
        form = CreateSurfaceFinishMaster(request.POST, instance=surface_finish)
        if form.is_valid():
            surface_finish_form_obj = form.save()
            surface_finish = request.POST.getlist('surface_finish')
            surface_finish_price = request.POST.getlist('surface_finish_price')
            for i, item in enumerate(surface_finish):
                kit_data = Surface_finish_kit.objects.get(pk=item)
                kit_data.surface_finish_price = float(surface_finish_price[i])
                kit_data.save()
                messages.success(request, "successfully Updated Surface Finish Price")
        else:
            messages.error(request, form.errors)
        return redirect('list_price_master')
    context = {
        "surface_finish_data": surface_finish_data,
        "form": form,
        "surface_finish": surface_finish,
    }
    return render(request, 'Master_settings/Pricing_Master/edit_surface_finish_price_modal.html', context)

@login_required(login_url="signin")
def delete_surface_finish(request, pk):
    """
    This function deletes a surface finish and its related data from the database and displays success
    or error messages accordingly.
    
    """
    if request.method == "POST":
        surface_finish = Surface_finish_Master.objects.get(pk=pk)
        try:
            surface_finish_data = Surface_finish_kit.objects.filter(master=surface_finish).delete()
            surface_finish.delete()
            messages.success(request, "Shop Floor Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_price_master')

    context = {
        "url": "/Pricing_Master/delete_surface_finish/"+str(pk)+"/",
    }
    return render(request, "Master_settings/delete_modal.html", context)

@login_required(login_url='signin')
def sealant_price_duplicate(request, pk):
    """
    This function creates a duplicate of a sealant pricing master and its associated sealant kits.
    
    """
    sealnt = SealantPriceMaster.objects.get(pk=pk)
    
    form = EditSealantForm(instance=sealnt)
    SEALANTFORMSET = modelformset_factory(Sealant_kit, form=CreateSealantForm, extra=1, can_delete=True)
    sealant_form = SEALANTFORMSET(queryset=Sealant_kit.objects.filter(pricing_master=sealnt), prefix="sealant_price3") 
    
    if request.method == "POST":
        form = EditSealantForm(request.POST)
        sealant_form = SEALANTFORMSET(request.POST, prefix="sealant_price3")
        if form.is_valid() and sealant_form.is_valid():
            new_sealant_obj = form.save()
            new_sealant_obj.created_by = request.user
            new_sealant_obj.created_date = time()
            new_sealant_obj.save()
            
            for item in sealant_form:
                sealant_form_obj = item.save(commit=False)
                new_sealant_form_obj = sealant_form_obj
                if new_sealant_form_obj.normal_price == 0 or new_sealant_form_obj.normal_price:
                    price = (float(new_sealant_form_obj.sealant_markup/100)*float(new_sealant_form_obj.normal_price))+float(new_sealant_form_obj.normal_price)
                    new_sealant_form_obj.pk = None
                    new_sealant_form_obj.price = float(price)
                    new_sealant_form_obj.pricing_master=new_sealant_obj
                    new_sealant_form_obj.save()
            
            messages.success(request, "Successfully Created Duplicate")
        return redirect('list_price_master')

        
    context = {
        "title": PROJECT_NAME+" | Sealant Duplicate.",
        "form": form,
        "sealant_form": sealant_form,
        "sealnt": sealnt,
    }
    return render(request, "Master_settings/Pricing_Master/sealant_duplicate.html", context)
    