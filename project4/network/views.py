from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Post


from .models import User


def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    return render(request, "network/index.html", {
        "posts": posts
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required(login_url="/login", redirect_field_name=None)
def newpost_view(request):
    if request.method == "POST":
        body = request.POST["body"]
        if body != "":
            Post.objects.create(user=request.user, body=body)
    return redirect("index")

#profile view
@login_required(login_url="/login", redirect_field_name=None)
def profile_view(request, username):
    user_profile = User.objects.get(username = username)
    posts = user_profile.posts.all().order_by('-timestamp')
    is_following = request.user.following.filter(username=username).exists()
    
    return render(request, "network/profile.html", {
         "profile": user_profile,
        "posts": posts,
        "followers_count": user_profile.followers.count(),
        "following_count": user_profile.following.count(),
        "is_following": is_following,
        "is_self": request.user == user_profile
    })

#follow view
@login_required
def follow(request, username):
    user_to_follow = User.objects.get(username=username)
    if request.user != user_to_follow:
        if request.method == "POST":
            if request.POST.get("follow") == "1":
                request.user.following.add(user_to_follow)
            elif request.POST.get("follow") == "0":
                request.user.following.remove(user_to_follow)
    return HttpResponseRedirect(reverse("profile", args=[username]))


@login_required
def following(request):
    following_users = request.user.following.all()
    posts = Post.objects.filter(user__in=following_users).order_by('-timestamp')
    return render(request, "network/index.html", {
        "posts": posts,
        "following_page": True
    })


@login_required
def like_post(request, post_id):
    if request.method == "POST":
        try:
            post = Post.objects.get(pk=post_id)
            if request.user in post.likes.all():
                post.likes.remove(request.user)
                liked = False
            else:
                post.likes.add(request.user)
                liked = True
                return JsonResponse({
                "likes": post.likes.count(),
                "liked": liked
            })
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)
    return JsonResponse({"error": "POST request required"}, status=400)

@login_required
def edit_post(request, post_id):
    if request.method == "POST":
        try:
            post = Post.objects.get(pk=post_id)
            # Security check
            if request.user != post.user:
                return JsonResponse({"error": "Unauthorized"}, status=403)
            
            # Change this line to handle form data instead of JSON
            body = request.POST.get("body")
            post.body = body
            post.save()
            return JsonResponse({"message": "Post updated successfully", "body": body})
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)
    return JsonResponse({"error": "POST request required"}, status=400)