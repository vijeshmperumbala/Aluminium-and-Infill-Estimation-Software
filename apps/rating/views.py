from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django import forms
from django.contrib.auth.decorators import login_required, permission_required

from apps.rating.models import RatingHead
from apps.rating.forms import CreateRatingHeadForm

from amoeba.settings import PROJECT_NAME


@login_required(login_url="signin")
def list_rating_head(request):
    """
    This function retrieves all rating heads and renders them in a template for display.
    
    :param request: The request object represents the current HTTP request that the user has made to the
    server. It contains information about the user's request, such as the URL, headers, and any data
    that was submitted with the request
    :return: an HTTP response with a rendered HTML template "Master_settings/Rating/list.html" and a
    context dictionary containing the title of the page and a queryset of all RatingHead objects ordered
    by their id in descending order.
    """
    rating_heads = RatingHead.objects.all().order_by('-id')
    
    context = {
        'title' : PROJECT_NAME+" | Rating Parameters",
        'rating_heads': rating_heads,
    }
    return render(request, "Master_settings/Rating/list.html", context)


@login_required(login_url='signin')
def add_rating_head(request):
    """
    This function adds a new rating parameter to the database and displays a success message if the form
    is valid, otherwise it displays an error message.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the HTTP method (GET, POST, etc.), headers, and any data submitted in the request
    :return: an HTTP response rendered using the "add_rating_head.html" template with the context
    variable "forms".
    """
    forms = CreateRatingHeadForm()
    if request.method == 'POST':
        forms = CreateRatingHeadForm(request.POST)
        if forms.is_valid():
            rating_head_form = forms.save(commit=False)
            rating_head_form.created_by = request.user
            rating_head_form.created_date = time()
            rating_head_form.save()
            messages.success(request, "Successfully Added Rating Parameter.")
        else:
            messages.error(request, forms.errors)
        
        return redirect('list_rating_head')
        
    context = {
        "forms": forms
    }
    return render(request, "Master_settings/Rating/add_rating_head.html", context)
    
    
@login_required(login_url='signin')
def update_rating_head(request, pk):
    """
    This function updates a rating head object in the database based on user input.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param pk: pk stands for primary key, which is a unique identifier for a specific instance of a
    model in a database. In this case, it is used to retrieve a specific instance of the RatingHead
    model from the database
    :return: a rendered HTML template with a context dictionary containing a form instance and a rating
    head instance. The template is located at "Master_settings/Rating/add_rating_head.html".
    """
    rating_head = RatingHead.objects.get(pk=pk)
    forms = CreateRatingHeadForm(instance=rating_head)
    if request.method == 'POST':
        forms = CreateRatingHeadForm(request.POST, instance=rating_head)
        if forms.is_valid():
            rating_head_form = forms.save(commit=False)
            rating_head_form.last_modified_by = request.user
            rating_head_form.last_modified_date = time()
            rating_head_form.save()
            messages.success(request, "Successfully Updated Rating Parameter.")
        else:
            messages.error(request, forms.errors)
        
        return redirect('list_rating_head')
        
    context = {
        "forms": forms,
        "rating_head": rating_head,
    }
    return render(request, "Master_settings/Rating/add_rating_head.html", context)


@login_required(login_url='signin')
def ratehead_delete(request, pk):
    """
    This function deletes a rating head object and displays a success or error message depending on
    whether the object has been used in the application or not.
    
    :param request: The request object represents the HTTP request that the user has made to the server.
    It contains information such as the HTTP method used (GET, POST, etc.), the URL requested, any data
    submitted in the request, and more
    :param pk: pk stands for primary key. It is a unique identifier for a specific instance of a model
    in a database table. In this case, it is used to identify the specific RatingHead object that needs
    to be deleted
    :return: a rendered HTML template for a delete confirmation modal dialog box. If the request method
    is POST, it deletes a RatingHead object with the given primary key (pk) and redirects to the
    list_rating_head view. If the deletion is unsuccessful, it displays an error message.
    """
    if request.method == "POST":
        try:
            rating_head = RatingHead.objects.get(pk=pk)
            rating_head.delete()
            messages.success(request, "Rating Parameter Deleted Successfully")
        except Exception as e:
            messages.error(request, "Unable to delete the data. Already used in application.")
            print("Delete is not possible.")
        return redirect('list_rating_head')

    context = {
        "url": "/rating/ratehead_delete/"+str(pk)+"/",
    }
    return render(request, "Master_settings/delete_modal.html", context)