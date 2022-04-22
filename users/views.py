import django
from typing import FrozenSet
from django.http.response import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile 
from feed.models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings 
from django.http import HttpResponse 
from .models import Profile, FriendRequest
from .forms import UserCreationForm, UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import feed.views as feed_views
from feed.forms import NewCommentForm
import random
from direct.models import Message
from django.template import loader, RequestContext
from django.contrib.auth import logout
# Create your views here.

# @login_required
# def home(request):
#     return render(request, "./home.html")

User = get_user_model()

def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return redirect('login')

@login_required
def users_list(request):
	users = Profile.objects.exclude(user=request.user)
	sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
	sent_to = []
	friends = []
	for user in users:
		friend = user.friends.all()
		for f in friend:
			if f in friends:
				friend = friend.exclude(user=f.user)
		friends+=friend
	my_friends = request.user.profile.friends.all()
	for i in my_friends:
		if i in friends:
			friends.remove(i)
	if request.user.profile in friends:
		friends.remove(request.user.profile)
	random_list = random.sample(list(users), min(len(list(users)), 10))
	for r in random_list:
		if r in friends:
			random_list.remove(r)
	friends+=random_list
	for i in my_friends:
		if i in friends:
			friends.remove(i)
	for se in sent_friend_requests:
		sent_to.append(se.to_user)
	context = {
		'users': friends,
		'sent': sent_to
	}
	return render(request, "users/users_list.html", context)

def friend_list(request):
    p = request.user.profile
    friends = p.friends.all()
    context = {
        'friends': friends
    }
    return render(request, 'users/friends_list.html', context)

@login_required
def send_friend_request(request, id):
    user = get_object_or_404(User, id= id)
    frequest, created = FriendRequest.objects.get_or_create(
        from_user= request.user,
        to_user= user
    )
    return HttpResponseRedirect(f'/users/{user.profile.slug}')

@login_required
def cancel_friend_request(request, id):
    user = get_object_or_404(User, id= id)
    frequest = FriendRequest.objects.filter(
        from_user = request.user,
        to_user = user
    ).first() 
    
    frequest.delete()
    return HttpResponseRedirect(f'/users/{user.profile.slug}')

@login_required
def accept_friend_request(request, id):
    from_user = get_object_or_404(User, id= id)
    frequest = FriendRequest.objects.filter(
        from_user = from_user,
        to_user = request.user
    ).first()
    user1 = from_user
    user2 = request.user
    user1.profile.friends.add(user2.profile)
    user2.profile.friends.add(user1.profile)
    if(FriendRequest.objects.filter(from_user= request.user, to_user= from_user).first()):
        request_rev = FriendRequest.objects.filter(from_user= request.user, to_user= from_user).first()
        request_rev.delete()
    frequest.delete()
    return HttpResponseRedirect(f'/users/{user1.profile.slug}')

def delete_friend_request(request, id):
    from_user = get_object_or_404(User, id= id)
    frequest = FriendRequest.onjects.filter(from_user= request.user, to_user= from_user).first()
    frequest.delete()
    return HttpResponseRedirect('my_profile')

def delete_friend(request, id):
    user_profile = request.user.profile
    friend_profile = get_object_or_404(Profile, id= id)
    user_profile.friends.remove(friend_profile)
    friend_profile.friends.remove(user_profile)
    return HttpResponseRedirect(f'/users/{friend_profile.slug}')

def delete_friend_list(request, id):
    user_profile = request.user.profile
    friend_profile = get_object_or_404(Profile, id= id)
    user_profile.friends.remove(friend_profile)
    friend_profile.friends.remove(user_profile)
    return HttpResponseRedirect('friend_list')

@login_required
def profile_view(request, slug):
    p = Profile.objects.filter(slug= slug).first()
    u = p.user
    sent_friend_requests = FriendRequest.objects.filter(from_user= p.user)
    rec_friend_requests = FriendRequest.objects.filter(to_user= p.user)
    user_posts = Post.objects.filter(username= u)
    friends = request.user.profile.friends.all()
    
    
    # is this user our friend or not
    button_status= 'none'
    if p not in request.user.profile.friends.all():
        button_status = 'not_friend'

        # if we have sent them a friend request
        if (FriendRequest.objects.filter(from_user= request.user).filter(to_user= p.user)):
            button_status = 'friend_request_sent'

        # if we have received a friend request from them
        if FriendRequest.objects.filter(from_user= p.user).filter(to_user= request.user):
            button_status = 'friend_request_received'

    context = {
        'u': u,
        'p': p,
        'button_status': button_status,
        'friends_list': friends,
        'sent_friend_requests': sent_friend_requests,
        'rec_friend_requests': rec_friend_requests,
        'post_count': user_posts.count,
        'user_posts': user_posts,
        # 'form': form,
    }
    return render(request, 'users/profile.html', context)

@login_required
def notifications(request):
    p = request.user.profile
    u = p.user
    sent_friend_requests = FriendRequest.objects.filter(from_user= u)
    rec_friend_requests = FriendRequest.objects.filter(to_user= u)
    friends = p.friends.all()
    user_post = Post.objects.filter(username= u)

    button_status = 'none'
    # if this user is our friend
    if(p.user not in request.user.profile.friends.all()):
        button_status = 'not_friend'

        #  if we have sent a friend request
        if len(FriendRequest.objects.filter(from_user= request.user).filter(to_user= u)) == 1:
            button_status = 'friend_request_sent'
        
        # if received a friend request from them
        if len(FriendRequest.objects.filter(from_user= p.user).filter(to_user= request.user)) == 1:
            button_status = 'friend_request_received'

    context = {
        'u': u,
        'button_status': button_status,
        'friends_list': friends,
        'sent_friend_requests': sent_friend_requests,
        'rec_friend_requests': rec_friend_requests,
        'post_count': user_post.count
    }
    return render(request, f'users/notifications.html', context)

# def save_values(username, firstname, lastname, i_name, i_area, phone):
#     Profile.objects.filter(slug = username).first().firstname = firstname
#     Profile.objects.filter(slug = username).first().lastname = lastname
#     Profile.objects.filter(slug = username).first().i_name = i_name
#     Profile.objects.filter(slug = username).first().i_area = i_area
#     Profile.objects.filter(slug = username).first().phone = phone
#     return(username, firstname, lastname, i_name)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            # firstname = form.cleaned_data.get('firstname')
            # lastname = form.cleaned_data.get('lastname')
            # i_name = form.cleaned_data.get('Institute_Name')
            # i_area = form.cleaned_data.get('Institute_Area')
            # phone = form.cleaned_data.get('phone')
            form.save()
            messages.success(request, f'Your Account has been Created ! You can now Login !')
            return redirect('login')
    
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
def edit_profile(request):
    u_form = UserUpdateForm(request.POST, request.FILES,  instance = request.user)
    p_form = ProfileUpdateForm(request.POST, request.FILES, instance = request.user.profile)
    if request.method == 'POST':
        if p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated !')
            return redirect('my_profile')
    else:
        u_form = UserUpdateForm(instance = request.user)
        p_form = ProfileUpdateForm(instance = request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/edit_profile.html', context)

# @login_required
def my_profile(request):
    p = request.user.profile
    u = p.user
    bio = p.bio
    model = Post
    template_name = 'users/profile.html'
    paginate_by = 10
    user_post = Post.objects.filter(username = u)
    friends = p.friends.all()

    button_status = 'none'
    # if this user is our friend
    if(p.user not in request.user.profile.friends.all()):
        button_status = 'not_friend'

        #  if we have sent a friend request
        if len(FriendRequest.objects.filter(from_user= request.user).filter(to_user= u)) == 1:
            button_status = 'friend_request_sent'
        
        # if received a friend request from them
        if len(FriendRequest.objects.filter(from_user= p.user).filter(to_user= request.user)) == 1:
            button_status = 'friend_request_received'

    context = {
        'u': u,
        'bio': bio,
        # 'button_status': button_status,
        # 'friends_list': friends,
        # 'sent_friend_requests': sent_friend_requests,
        # 'rec_friend_requests': rec_friend_requests,
        'post_count': user_post.count,
        "posts": user_post,
        "friend_list": friends,
    }
    return render(request, f'users/profile.html', context)

@login_required
def search_users(request):
    query = request.GET.get('q')
    object_list = User.objects.filter(username__icontains= query)
    context = {
        'users': object_list
    }
    return render(request, f'users/search_users.html', context)



