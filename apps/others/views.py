from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required

from amoeba.settings import PROJECT_NAME
from apps.others.forms import (
        CreateElevation, 
        CreateLabour_and_OverheadPercentage,
        CreateProjectBuilding,
        CreateProjectFloor, 
        CreateSubmitParameterForm,
    )
from apps.others.models import (
        AI_RatingModel, 
        Labour_and_OverheadMaster, 
        SubmittingParameters,
    )
from apps.projects.models import EPSBuildingsModel, FloorModel, ProjectsModel
from apps.projects.models import ElevationModel


@login_required(login_url='signin')
def other_settings(request):
    rating_objs = AI_RatingModel.objects.all()
    parameter_obj = SubmittingParameters.objects.all()
    loh_objs = Labour_and_OverheadMaster.objects.all()
    # elevations = ElevationModel.objects.all()
    try:
        excellent_obj = AI_RatingModel.objects.get(label=1)
        good_obj =  AI_RatingModel.objects.get(label=2)
        average_obj =  AI_RatingModel.objects.get(label=3)
        bl_average_obj =  AI_RatingModel.objects.get(label=4)
        poor_obj =  AI_RatingModel.objects.get(label=5)
    except Exception:
        excellent_obj = None
        good_obj = None
        average_obj = None
        bl_average_obj = None
        poor_obj = None
    
    context = {
        "title": f'{PROJECT_NAME} | Amoeba.',
        'excellent_obj': excellent_obj,
        'good_obj': good_obj,
        'average_obj': average_obj,
        'bl_average_obj': bl_average_obj,
        'poor_obj': poor_obj,
        'rating_objs': rating_objs,
        'parameter_obj': parameter_obj,
        'loh_objs': loh_objs,
        # 'elevations': elevations,
    }
    return render(request, 'Master_settings/Others/other_settings.html', context)


@login_required(login_url='signin')
def update_ai_rating(request):
    """
    The function `update_ai_rating` updates the AI rating model based on user input and redirects to the
    "other_settings" page.
    
    """
    rating_objs = AI_RatingModel.objects.all()
    
    try:
        excellent_obj = AI_RatingModel.objects.get(label=1)
        good_obj =  AI_RatingModel.objects.get(label=2)
        average_obj =  AI_RatingModel.objects.get(label=3)
        bl_average_obj =  AI_RatingModel.objects.get(label=4)
        poor_obj =  AI_RatingModel.objects.get(label=5)
    except Exception:
        excellent_obj = None
        good_obj = None
        average_obj = None
        bl_average_obj = None
        poor_obj = None
        
    if request.method == 'POST':
        excellent = request.POST.get('excellent')
        good = request.POST.getlist('good')
        average = request.POST.getlist('average')
        bl_average = request.POST.getlist('bl_average')
        poor = request.POST.get('poor')
        
        if 'create' in request.POST:
            if excellent:
                excellent_obj =  AI_RatingModel(created_by=request.user, label=1, from_value=0, to_value=float(excellent))
                excellent_obj.save()
            if good:
                good_obj =  AI_RatingModel(created_by=request.user, label=2, from_value=float(good[0]), to_value=float(good[1]))
                good_obj.save()
            if average:
                average_obj =  AI_RatingModel(created_by=request.user, label=3, from_value=float(average[0]), to_value=float(average[1]))
                average_obj.save()
            if bl_average:
                bl_average_obj =  AI_RatingModel(created_by=request.user, label=4, from_value=float(bl_average[0]), to_value=float(bl_average[1]))
                bl_average_obj.save()
            if poor:
                poor_obj =  AI_RatingModel(created_by=request.user, label=5, from_value=float(poor), to_value=10000)
                poor_obj.save()
                    
        elif 'update' in request.POST:
            if excellent:
                excellent_obj = AI_RatingModel.objects.get(label=1)
                excellent_obj.to_value=float(excellent)
                excellent_obj.save()
            if good:
                good_obj =  AI_RatingModel.objects.get(label=2)
                good_obj.from_value=float(good[0])
                good_obj.to_value=float(good[1])
                good_obj.save()
            if average:
                average_obj =  AI_RatingModel.objects.get(label=3)
                average_obj.from_value=float(average[0])
                average_obj.to_value=float(average[1])
                average_obj.save()
            if bl_average:
                bl_average_obj =  AI_RatingModel.objects.get(label=4)
                bl_average_obj.from_value=float(bl_average[0])
                bl_average_obj.to_value=float(bl_average[1])
                bl_average_obj.save()
            if poor:
                poor_obj =  AI_RatingModel.objects.get(label=5)
                poor_obj.from_value=float(poor)
                poor_obj.save()
            
        return redirect('other_settings')
        
    context = {
        "title": f'{PROJECT_NAME} | Amoeba.',
        "rating_objs": rating_objs,
        'excellent_obj': excellent_obj,
        'good_obj': good_obj,
        'average_obj': average_obj,
        'bl_average_obj': bl_average_obj,
        'poor_obj': poor_obj,
        
    }
    return render(request, 'Master_settings/Others/rating_model.html', context)


@login_required(login_url='signin')
def add_estimation_submit_parameters(request):
    create_form = CreateSubmitParameterForm()
    if request.method == "POST":
        create_form = CreateSubmitParameterForm(request.POST)
        if create_form.is_valid():
            create_form.save()
            messages.success(request, "Successfully Added.")
        else:
            messages.error(request, "Error in Adding.")
        return redirect('other_settings')
            
    context = {
        "form" : create_form,
    }
    return render(request, "Master_settings/Others/parameter_model.html", context)


@login_required(login_url='signin')
def update_estimation_submit_parameters(request, pk):
    parameter_obj = SubmittingParameters.objects.get(pk=pk)
    update_form = CreateSubmitParameterForm(instance=parameter_obj)
    if request.method == "POST":
        update_form = CreateSubmitParameterForm(request.POST, instance=parameter_obj)
        if update_form.is_valid():
            obj = update_form.save(commit=False)
            obj.last_modified_date = time()
            obj.last_modified_by = request.user
            obj.save()
            messages.success(request, "Successfully Updated.")
        else:
            messages.error(request, "Error in Updating.")
        return redirect('other_settings')
            
    context = {
        "form" : update_form,
        "parameter_obj": parameter_obj,
    }
    return render(request, "Master_settings/Others/parameter_model.html", context)


@login_required(login_url='signin')
def delete_parameter(request, pk):
    """
    The function `delete_parameter` deletes a parameter object based on its primary key and displays a
    success message if the deletion is successful, otherwise it displays an error message.
    """
    if request.method == "POST":
        try:
            parameters = SubmittingParameters.objects.get(pk=pk)
            parameters.delete()
            messages.success(request, "Parameter Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('other_settings')

    context = {"url": f"/others/delete_parameter/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
def loh_percentage_add(request):
    forms = CreateLabour_and_OverheadPercentage()
    if request.method == "POST":
        forms = CreateLabour_and_OverheadPercentage(request.POST)
        if forms.is_valid():
            forms.save()
            messages.success(request, "Successfully Added.")
        else:
            print('ERROR=>', forms.errors())
            messages.error(request, "Error in Adding.")
        return redirect('other_settings')
    
    context = {
        "form" : forms,
    }
    return render(request, "Master_settings/Others/loh_percenatage_model.html", context)


@login_required(login_url='signin')
def loh_percentage_update(request, pk):
    loh_objs = Labour_and_OverheadMaster.objects.get(pk=pk)
    forms = CreateLabour_and_OverheadPercentage(instance=loh_objs)
    if request.method == "POST":
        forms = CreateLabour_and_OverheadPercentage(request.POST, instance=loh_objs)
        if forms.is_valid():
            forms.save()
            messages.success(request, "Successfully Updated.")
        else:
            print('ERROR=>', forms.errors())
            messages.error(request, "Error in Updating.")
        return redirect('other_settings')
    
    context = {
        "form" : forms,
        "loh_objs": loh_objs,
    }
    return render(request, "Master_settings/Others/loh_percenatage_model.html", context)


@login_required(login_url='signin')
def delete_loh_percentage(request, pk):
    if request.method == "POST":
        try:
            loh_objs = Labour_and_OverheadMaster.objects.get(pk=pk)
            loh_objs.delete()
            messages.success(request, "Labour & Overhead Percenatage Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('other_settings')

    context = {"url": f"/others/delete_loh_percentage/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
def elevation_add(request, pk):
    
    building_obj = EPSBuildingsModel.objects.get(pk=pk)
    forms = CreateElevation()
    if request.method == "POST":
        forms = CreateElevation(request.POST)
        if forms.is_valid():
            form_obj = forms.save()
            form_obj.building = building_obj
            form_obj.save()
            messages.success(request, "Successfully Added.")
        else:
            print('ERROR=>', forms.errors())
            messages.error(request, "Error in Adding.")
        return redirect('project_settings', pk=building_obj.project.id, building_id=building_obj.id)
    
    context = {
        "form" : forms,
        "projec_obj": building_obj.project,
        "building_obj": building_obj,
    }
    return render(request, "Master_settings/Others/elevation_model.html", context)


@login_required(login_url='signin')
def elevation_update(request, pk):
    elevation_obj = ElevationModel.objects.get(pk=pk)
    project = elevation_obj.project
    forms = CreateElevation(instance=elevation_obj)
    if request.method == "POST":
        forms = CreateElevation(request.POST, instance=elevation_obj)
        if forms.is_valid():
            forms.save()
            messages.success(request, "Successfully Updated.")
        else:
            print('ERROR=>', forms.errors())
            messages.error(request, "Error in Updating.")
        return redirect('project_settings', pk=project.id, building_id=elevation_obj.building.id)
    
    context = {
        "form" : forms,
        "elevation_obj": elevation_obj,
    }
    return render(request, "Master_settings/Others/elevation_model.html", context)


@login_required(login_url='signin')
def delete_elevation(request, pk):
    elevation_obj = ElevationModel.objects.get(pk=pk)
    # try:
    #     project = elevation_obj.project
    # except Exception as e:
    #     print("EXCE==>", e)
    #     project = None
    
    # projec_obj = ProjectsModel.objects.get(pk=project.id) 
    if request.method == "POST":
        try:
            elevation_obj.delete()
            messages.success(request, "Elevation Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            
        return redirect('project_settings', pk=elevation_obj.building.project.id, building_id=elevation_obj.building.id)

    context = {"url": f"/others/delete_elevation/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
def project_building_add(request, pk):
    projec_obj = ProjectsModel.objects.get(pk=pk)
    forms = CreateProjectBuilding()
    if request.method == "POST":
        forms = CreateProjectBuilding(request.POST)
        if forms.is_valid():
            form_obj = forms.save()
            form_obj.project = projec_obj
            form_obj.save()
            messages.success(request, "Successfully Added.")
        else:
            print('ERROR=>', forms.errors())
            messages.error(request, "Error in Adding.")
        return redirect('project_settings', pk=projec_obj.id)
    
    context = {
        "form" : forms,
        "projec_obj": projec_obj,
    }
    return render(request, "Master_settings/Others/project_building_model.html", context)


@login_required(login_url='signin')
def project_building_update(request, pk):
    # projec_obj = ProjectsModel.objects.get(pk=pk)
    building_obj = EPSBuildingsModel.objects.get(pk=pk)
    forms = CreateProjectBuilding(instance=building_obj)
    if request.method == "POST":
        forms = CreateProjectBuilding(request.POST, instance=building_obj)
        if forms.is_valid():
            forms.save()
            
            messages.success(request, "Successfully Updated.")
        else:
            print('ERROR=>', forms.errors())
            messages.error(request, "Error in Updating.")
        return redirect('project_settings', pk=building_obj.project.id)
    
    context = {
        "form" : forms,
        "building_obj": building_obj,
        "projec_obj": building_obj.project,
    }
    return render(request, "Master_settings/Others/project_building_model.html", context)


@login_required(login_url='signin')
def delete_project_building(request, pk):
    building_obj = EPSBuildingsModel.objects.get(pk=pk)
    try:
        project = building_obj.project
    except Exception as e:
        print("EXCE==>", e)
        project = None
    # projec_obj = ProjectsModel.objects.get(pk=project.id) 
    if request.method == "POST":
        try:
            building_obj.delete()
            messages.success(request, "Project Building Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            
        return redirect('project_settings', pk=project.id)

    context = {"url": f"/others/delete_project_building/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)


@login_required(login_url='signin')
def project_floor_add(request, pk):
    # projec_obj = ProjectsModel.objects.get(pk=pk)
    elevations_obj = ElevationModel.objects.get(pk=pk)
    forms = CreateProjectFloor()
    if request.method == "POST":
        forms = CreateProjectFloor(request.POST)
        if forms.is_valid():
            form_obj = forms.save()
            form_obj.elevation = elevations_obj
            form_obj.save()
            messages.success(request, "Successfully Added.")
        else:
            print('ERROR=>', forms.errors())
            messages.error(request, "Error in Adding.")
        # return redirect('project_settings', pk=projec_obj.id)
        return redirect('project_settings', pk=elevations_obj.building.project.id, building_id=elevations_obj.building.id, elevation=elevations_obj.id)
    
    context = {
        "form" : forms,
        "projec_obj": elevations_obj.building.project,
        "elevations_obj": elevations_obj,
    }
    return render(request, "Master_settings/Others/project_floor_model.html", context)

@login_required(login_url='signin')
def project_floor_update(request, pk):
    # projec_obj = ProjectsModel.objects.get(pk=pk)
    # elevations_obj = ElevationModel.objects.get(pk=pk)
    floor_obj = FloorModel.objects.get(pk=pk)
    forms = CreateProjectFloor(instance=floor_obj)
    if request.method == "POST":
        forms = CreateProjectFloor(request.POST, instance=floor_obj)
        if forms.is_valid():
            forms.save()
            messages.success(request, "Successfully Added.")
        else:
            print('ERROR=>', forms.errors())
            messages.error(request, "Error in Adding.")
        # return redirect('project_settings', pk=projec_obj.id)
        return redirect('project_settings', pk=floor_obj.elevation.building.project.id, building_id=floor_obj.elevation.building.id, elevation=floor_obj.elevation.id)
    
    context = {
        "form" : forms,
        "projec_obj": floor_obj.elevation.building.project,
        "elevations_obj": floor_obj.elevation,
        "floor_obj": floor_obj,
        
    }
    return render(request, "Master_settings/Others/project_floor_model.html", context)

@login_required(login_url='signin')
def delete_project_floor(request, pk):
    floor_obj = FloorModel.objects.get(pk=pk)
    
    # projec_obj = ProjectsModel.objects.get(pk=project.id) 
    if request.method == "POST":
        try:
            floor_obj.delete()
            messages.success(request, "Project Building Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            
        return redirect('project_settings', pk=floor_obj.elevation.building.project.id, building_id=floor_obj.elevation.building.id, elevation=floor_obj.elevation.id)

    context = {"url": f"/others/delete_project_floor/{str(pk)}/"}
    return render(request, "Master_settings/delete_modal.html", context)












