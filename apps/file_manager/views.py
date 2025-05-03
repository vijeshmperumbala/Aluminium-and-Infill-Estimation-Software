import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now as time
from django.contrib.auth.decorators import login_required, permission_required
from apps.enquiries.models import Enquiries, Estimations

from amoeba.settings import MEDIA_URL, PROJECT_NAME, MEDIA_ROOT
import re
import os
from django.http import Http404, HttpResponse, JsonResponse
import zipfile

from django.http import JsonResponse

from django.conf import settings
import datetime
from django.urls import reverse


def convert_bytes(num):
    """
    The function converts a given number of bytes into a more readable format with units such as KB, MB,
    GB, and TB.
    
    :param num: The number of bytes to be converted to a larger unit (KB, MB, GB, or TB)
    :return: The function is not returning anything, it is defining a function to convert a given number
    of bytes to a more readable format (in terms of KB, MB, GB, or TB). The function will only return a
    value when it is called with a number as an argument.
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
        
        
@login_required(login_url='signin')
def file_manager(request):
    """
    This function retrieves file and folder data from a specified directory and renders it in a template
    for a file manager.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the user agent, headers, and any data submitted in the request
    :return: a rendered HTML template with a context containing file and folder data, as well as
    navigation and path information for a file manager page.
    """

    directory = MEDIA_ROOT+'/Quotations'
    directory_url = 'Quotations'
    file_data = []
    folder_data = []
    div_nav = []
    div_nav.append(str(directory_url))
    for filename in os.listdir(directory):
        MEDIA_PATH = 'http://'+str(request.get_host())+'/'+str(MEDIA_URL)
        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            size = convert_bytes(os.stat(path).st_size)
            created = datetime.datetime.fromtimestamp(
                os.stat(path).st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            extension = os.path.splitext(path)[1]

            file_data.append({'name': filename, 'path': os.path.join(MEDIA_PATH, 'Quotations', str(filename)).replace(
                '\\', '/'), 'size': size, 'created': created, 'extension': extension, 'parent': directory_url})
        elif os.path.isdir(path):
            folder_data.append(
                {'name': filename, 'path': filename, 'parent': directory_url})

    count = sum(1 for _ in os.listdir(directory))
    new_list = div_nav[div_nav.index('Quotations')::]
    parent_url = new_list
    new_list2 = []
    current_path = ''
    for item in parent_url:
        current_path = os.path.join(current_path, item).replace('\\', '/')
        new_list2.append(current_path)

    context = {
        'title': PROJECT_NAME + " | File Manager",
        'files': file_data,
        'folders': folder_data,
        'data_count': count,
        'base_path': directory_url,
        'nav_bar': new_list,
        'parent_url': new_list2

    }

    return render(request, "File_Manager/filemanager_list.html", context)


@login_required(login_url='signin')
def list_files(request, path, parent_path=None):
    """
    This function lists files and folders in a directory and returns them in a rendered HTML template.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and data
    :param path: The path parameter is a string that represents the path of the directory to be listed.
    It is used to construct the full path of the directory by joining it with the MEDIA_ROOT directory
    :param parent_path: The parent directory path of the current directory being listed. It is an
    optional parameter and defaults to None
    :return: The function `list_files` returns a rendered HTML template with context variables
    containing file and folder data, count, base path, navigation bar, and parent URL.
    """
    path1 = path.replace('-', '/')
    if parent_path:
        directory = os.path.join(MEDIA_ROOT, parent_path, path1)
    else:
        directory = os.path.join(MEDIA_ROOT, path1)

    file_data = []
    folder_data = []
    directory_url = path1
    div_nav = re.split(r'[\\\/]', directory)

    for filename in os.listdir(directory):
        MEDIA_PATH = 'http://'+str(request.get_host())+'/'+str(MEDIA_URL)
        path = os.path.join(directory, filename)

        if os.path.isfile(path):
            size = convert_bytes(os.stat(path).st_size)
            created = datetime.datetime.fromtimestamp(
                os.stat(path).st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            extension = os.path.splitext(path)[1]
            if parent_path:
                file_data.append({'name': filename, 'path': os.path.join(MEDIA_PATH, parent_path, directory_url, str(filename)).replace(
                    '\\', '/'), 'size': size, 'created': created, 'extension': extension, 'parent': parent_path+'/'+directory_url})
            else:
                file_data.append({'name': filename, 'path': os.path.join(MEDIA_PATH, directory_url, str(filename)).replace(
                    '\\', '/'), 'size': size, 'created': created, 'extension': extension, 'parent': parent_path+'/'+directory_url})
        elif os.path.isdir(path):
            if parent_path:
                folder_data.append(
                    {'name': filename, 'path': filename, 'parent': parent_path+'/'+directory_url})
            else:
                folder_data.append(
                    {'name': filename, 'path': filename, 'parent': directory_url})

    count = sum(1 for _ in os.listdir(directory))
    new_list = div_nav[div_nav.index('Quotations')::]

    parent_url = new_list

    new_list2 = []
    current_path = ''
    for item in parent_url:
        current_path = os.path.join(current_path, item).replace('\\', '/')
        new_list2.append(current_path)

    context = {
        'title': PROJECT_NAME + " | File Manager",
        'files': file_data,
        'folders': folder_data,
        'data_count': count,
        'base_path': directory_url,
        'nav_bar': new_list,
        'parent_url': new_list2

    }
    return render(request, "File_Manager/filemanager_list.html", context)

@login_required(login_url='signin')
def folder_downloader(request, path, parent_path, filename):
    """
    This function downloads a folder and its contents as a compressed zip file.
    
    :param request: The HTTP request object that triggered this function
    :param path: It seems that the parameter "path" is not used in the given code snippet. It is
    possible that it was intended to be used but was not implemented
    :param parent_path: The parent directory path where the folder to be downloaded is located
    :param filename: The name of the folder that needs to be downloaded
    :return: an HTTP response object that contains a zip file of the contents of a folder specified by
    the input parameters.
    """
    folder_path = os.path.join(
        MEDIA_ROOT, parent_path, filename).replace('\\', '/')
    zip_file_name = filename+'.zip'
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                zipf.write(dir_path, os.path.relpath(dir_path, folder_path))

    response = HttpResponse(zip_buffer.getvalue(),
                            content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_file_name}"'

    return response

@login_required(login_url='signin')
def file_download(request, path, filename):
    """
    This function downloads a file from a specified path and returns it as an HTTP response with an
    attachment header.
    
    :param request: The HTTP request object that contains information about the client's request
    :param path: The path parameter is a string that represents the directory path where the file to be
    downloaded is located. It is used to construct the full file path by joining it with the MEDIA_ROOT
    directory path
    :param filename: The name of the file that is being downloaded
    :return: an HTTP response object that contains the contents of the file specified by the path and
    filename parameters. The response is set to force a download of the file by setting the Content-Type
    header to 'application/octet-stream' and the Content-Disposition header to 'attachment'.
    """
    file_path = os.path.join(MEDIA_ROOT, path, filename)
    if not os.path.exists(file_path):
        raise Http404("File does not exist")
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read())
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename=' + \
            os.path.basename(file_path)
        return response
    

def delete_file(request, path, filename):
    """
    This function deletes a file or folder at a specified path and filename and returns a JSON response
    indicating success or failure.
    
    :param request: The HTTP request object that contains information about the current request
    :param path: The path of the file or folder to be deleted, relative to the MEDIA_ROOT directory
    :param filename: The name of the file or folder that needs to be deleted
    :return: A JSON response with a key-value pair of 'success': True.
    """
    file_path = os.path.join(MEDIA_ROOT, path, filename)
    if not os.path.exists(file_path):
        print('File or folder does not exist')
    try:
        if os.path.isdir(file_path):
            os.rmdir(file_path)
        else:
            os.remove(file_path)
        print('File or folder successfully deleted')
    except Exception as e:
        print(f'Error deleting file or folder: {e}')
    return JsonResponse({'success': True})


def file_tree(request):
    """
    This function generates a file tree structure for a given directory and returns it as a JSON
    response.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the HTTP method, headers, and query parameters
    :return: a JSON response containing a list of files and directories in a specified directory. The
    list is generated based on the input parameter "parent" which specifies the parent directory. If
    "parent" is "#" then the function returns a list of directories and files in the root directory. The
    function also sets icons for files and directories based on their type and status.
    """
    parent_in = request.GET.get("parent")
    data = []

    directory = os.path.join(settings.MEDIA_ROOT, 'Quotations')
    directory_url = 'Quotations'
    div_nav = []
    file_icon_color = 'text-danger'
    # folder_icon_color = 'text-warning'

    version = 0
    div_nav.append(str(directory_url))

    if parent_in == "#":
        for i, filename in enumerate(os.listdir(directory)):
            path = os.path.join(directory, filename).replace('\\', '/')
            enquiry_id = path.split('/')[-1]
            try:
                enquiry_obj = Enquiries.objects.get(enquiry_id=enquiry_id)
                versions = [str(estimation.version.version)+':'+str(estimation.id)+':'+str(estimation.enquiry.id) for estimation in Estimations.objects.filter(enquiry=enquiry_obj)]
                enquiry_title = enquiry_obj.title
            except:
                enquiry_obj = None
                versions = None
                enquiry_title = ''
            
            if os.path.isdir(path):
                data.append({
                    "id": filename,
                    "text": filename,
                    "icon": f"fa fa-folder text-warning fs-2 1",
                    "children": True,
                    "enquiry_name": enquiry_title,
                    "versions": versions,
                })
            elif os.path.isfile(path):
                data.append({
                    "id": filename,
                    "text": filename,
                    "icon": f"fa fa-file-pdf {file_icon_color} fs-2 2",
                    "type": "file",
                    "children": False,
                    "enquiry_name": enquiry_title,
                    "versions": versions,
                    
                })
    else:
        path = os.path.join(directory, parent_in).replace('\\', '/')
        enquiry = parent_in.split('\\')
        enquiry_id = enquiry[0]
        try:
            enquiry_obj = Enquiries.objects.get(enquiry_id=enquiry_id)
            versions = [str(estimation.version.version)+':'+str(estimation.id)+':'+str(estimation.enquiry.id) for estimation in Estimations.objects.filter(enquiry=enquiry_obj)]
            enquiry_title = enquiry_obj.title
        except:
            enquiry_obj = None
            versions = None
            enquiry_title = ''
            
        if len(enquiry[2::]) != 0:
            if 'Original' in enquiry[2::]:
                version = 0
            else:
                version = (enquiry[2::][0]).split(' ')[1]
        try:
            estimation = Estimations.objects.get(
                enquiry__enquiry_id=enquiry_id, version__version=version)
        except Exception as e:
            print("EXC==>", e)
            estimation = None
        if estimation:
            if estimation.version.status in [6, 12, 13, 15]:
                file_icon_color = 'text-success'
                # folder_icon_color = 'text-success'
            else:
                file_icon_color = 'text-danger'
                # folder_icon_color = 'text-warning'

        for filename in os.listdir(path):
            filepath = os.path.join(path, filename).replace('\\', '/')
            if os.path.isfile(filepath):
                data.append({
                    "id": os.path.join(parent_in, filename),
                    "text": filename,
                    "icon": f"fa fa-file-pdf {file_icon_color} fs-2 3",
                    "type": "file",
                    "children": False,
                    "enquiry_name": enquiry_title,
                    "versions": versions,
                })
            elif os.path.isdir(filepath):
                data.append({
                    "id": os.path.join(parent_in, filename),
                    "text": filename,
                    "icon": f"fa fa-folder text-warning fs-2 4",
                    "children": True,
                    "enquiry_name": enquiry_title,
                    "versions": versions,
                })

    response = JsonResponse(data, safe=False)
    response['Access-Control-Allow-Origin'] = '*'
    return response
    

def open_file(request):
    """
    This function takes a POST request with a file path, constructs a download URL, and returns it as a
    JSON response.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the HTTP method (e.g. GET, POST), headers, and any data submitted with the request
    :return: If the request method is "POST", a JSON response containing the download URL of a file
    specified by the "file_id" parameter in the request is returned. If the request method is not
    "POST", a JSON response with an error message is returned.
    """
    if request.method == "POST":
        file_path = request.POST.get("file_id")
        directory = os.path.join('http://'+str(request.get_host()), 'media/Quotations')
        open_path = os.path.join(directory, file_path).replace("\\", '/')
        download_url = open_path
        
        return JsonResponse({"download_url": download_url})
    else:
        return JsonResponse({"error": "Invalid request"})
