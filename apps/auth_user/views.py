from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from apps.user.models import User
from amoeba.settings import PROJECT_NAME


def two_step_verification(request):
    """
    This function redirects the user to a two-step verification page with a context containing the
    project name.
    """
    context = {"title": f"Two Step Verification | {PROJECT_NAME}"}
    return redirect(request, 'two-step.html', context)
