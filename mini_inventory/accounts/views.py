from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import User
from .forms import UserCreateForm, UserUpdateForm, ProfileUpdateForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard_home")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        messages.success(
            request,
            f"Welcome back, {user.get_full_name() or user.username}!",
        )

        return redirect("dashboard:dashboard_home")

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )


@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(
        request,
        "accounts/profile.html",
        {"form": form},
    )


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if request.user.role != User.Role.ADMIN:
            messages.error(request, "You are not authorized to access this page.")
            return redirect("dashboard:home")

        return view_func(request, *args, **kwargs)

    wrapper.__name__ = view_func.__name__
    wrapper.__doc__ = view_func.__doc__
    return wrapper


@login_required
@admin_required
def user_list(request):
    users = User.objects.all().order_by("username")

    query = request.GET.get("q", "").strip()
    role = request.GET.get("role", "").strip()

    if query:
        users = users.filter(
            username__icontains=query
        ) | users.filter(
            first_name__icontains=query
        ) | users.filter(
            last_name__icontains=query
        ) | users.filter(
            email__icontains=query
        )

    if role in User.Role.values:
        users = users.filter(role=role)

    return render(
        request,
        "accounts/user_list.html",
        {
            "users": users,
            "query": query,
            "selected_role": role,
            "roles": User.Role.choices,
        },
    )


@login_required
@admin_required
def user_create(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"User {user.username} created successfully.",
            )
            return redirect("accounts:user_list")
    else:
        form = UserCreateForm()

    return render(
        request,
        "accounts/user_form.html",
        {"form": form, "title": "Create User"},
    )


@login_required
@admin_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"User {user.username} updated successfully.",
            )
            return redirect("accounts:user_list")
    else:
        form = UserUpdateForm(instance=user)

    return render(
        request,
        "accounts/user_form.html",
        {"form": form, "title": "Edit User"},
    )
