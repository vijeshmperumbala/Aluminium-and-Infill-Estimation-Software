from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
import json

import random

from apps.tags.models import Tags
from apps.tags.forms import CreateTagForm
from amoeba.settings import PROJECT_NAME

@login_required(login_url='signin')
def list_tags(request, pk=None):
    """
    This function lists and manages tags in a web application.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the method (GET, POST, etc.), headers, and any data submitted in the request
    :param pk: pk is a parameter that represents the primary key of a specific Tags object. It is used
    to retrieve and update a specific tag in the database. If it is None, it means that the function is
    being called to display a list of all tags
    :return: an HTTP response with the rendered "Master_settings/Tags/tags_list.html" template, along
    with a context dictionary containing the title and a queryset of all Tags objects ordered by their
    id.
    """
    tags_lists = Tags.objects.all().order_by('id')
    
    # Tag color list
    tag_color_list = [  '#175899', '#d8348e', '#6dbb54', 
                        '#074167', '#007130', '#643a88',
                        '#a55e44', '#20599c', '#ac1c45', 
                        '#029bbd', '#556179', '#ff2c69',
                        '#0390b4', '#7b00a7', '#e5463b', 
                        '#618c80', '#106789', '#444444',
                        '#9fe43f', '#b23488', '#472a6d',
                    ]
    
    if request.method == "POST":
        if 'create_tag' in request.POST:
            tags_list = request.POST.getlist('tags')
            for tag_items in tags_list:
                for tag in json.loads(tag_items):
                    tag_name = tag['value']
                    if len(tag_color_list) < tags_lists.count():
                        tag_color = random.choice(tag_color_list)
                        tag_obj = Tags(created_by=request.user, created_date=time(), tag_name=tag_name, tag_color=tag_color)
                    else:
                        tag_color = tag_color_list[tags_lists.count()]
                        tag_obj = Tags(created_by=request.user, created_date=time(), tag_name=tag_name, tag_color=tag_color)
                    tag_obj.save()
            messages.success(request, "Successfully Added Tag")
        elif 'update_tag' in request.POST:
            tag_name = request.POST.get('update_tags')
            tag = Tags.objects.get(pk=pk)
            tag.tag_name = tag_name
            tag.save()
            messages.success(request, "Successfully Updated Tag")
        return redirect("list_tags")
    
    context = {
        "title": PROJECT_NAME+" | Tags list",
        "tags_list": tags_lists,
    }
    return render(request, "Master_settings/Tags/tags_list.html", context)

@login_required(login_url='signin')
def delete_tag(request, pk):
    """
    This function deletes a tag object and displays a success message if successful, or an error message
    if the tag is already in use.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the user making the request and any data submitted with the request
    :param pk: pk stands for "primary key". In this context, it refers to the unique identifier of a
    specific instance of the Tags model. The function is designed to delete the tag with the given
    primary key from the database
    :return: a redirect to the 'list_tags' URL.
    """
    tag = Tags.objects.get(pk=pk)
    try:
        tag.delete()
        messages.success(request, "Successfully Deleted Tag")
    except:
        messages.error(request, "Unable to delete the data. Already used in application")
    return redirect('list_tags')


