from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import NewCommentForm, NewPostForm
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post,Comments,Like
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from direct.models import Message
from django.template import loader, RequestContext

# Create your views here.

from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
#@login_required
class PostListView(ListView):
	model = Post
	template_name = 'feed/home.html'
	context_object_name = 'posts'
	ordering = ['-date_posted']
	# paginate_by = 10

	def get_context_data(self, **kwargs):
		context = super(PostListView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated:
			user = self.request.user
			messages =Message.get_messages(user=user)
			directs = Message.objects.filter(user=user, recipient__username=user.username)
			liked = [i for i in Post.objects.all() if Like.objects.filter(user = self.request.user, post=i)]
			context['liked_post'] = liked
		friends = []
		for friend in self.request.user.profile.friends.all():
			friends.append(friend.user.username)
		friends.append(user.username)
		context['friends'] = friends
		context['messages'] = messages
		context['directs'] = directs
		context['count'] = directs.count()
		context['m_count'] = len(messages)
		return context

class Explore(ListView):
	model = Post
	template_name = 'feed/explore.html'
	context_object_name = 'posts'
	ordering = ['-date_posted']
	paginate_by = 10

	def get_context_data(self, **kwargs):
		context = super(Explore, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated:
			user = self.request.user
			messages =Message.get_messages(user=user)
			directs = Message.objects.filter(user=user, recipient__username=user.username)
			liked = [i for i in Post.objects.all() if Like.objects.filter(user = self.request.user, post=i)]
			context['liked_post'] = liked
		friends = []
		for friend in self.request.user.profile.friends.all():
			friends.append(friend.user.username)
		context['friends'] = friends
		context['messages'] = messages
		context['directs'] = directs
		context['count'] = directs.count()
		context['m_count'] = len(messages)
		return context
    
class UserPostListView(LoginRequiredMixin, ListView):
	model = Post
	template_name = 'feed/user_posts.html'
	context_object_name = 'posts'
	paginate_by = 10

	def get_context_data(self, **kwargs):
		context = super(UserPostListView, self).get_context_data(**kwargs)
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		liked = [i for i in Post.objects.filter(username=user) if Like.objects.filter(user = self.request.user, post=i)]
		context['liked_post'] = liked
		return context

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Post.objects.filter(username=user).order_by('-date_posted')

@login_required
def post_detail(request, pk):
	post = get_object_or_404(Post, pk=pk)
	user = request.user
	is_liked =  Like.objects.filter(user=user, post=post)
	if request.method == 'POST':
		form = NewCommentForm(request.POST)
		if form.is_valid():
			data = form.save(commit=False)
			data.post = post
			data.username = user
			data.save()
			return redirect('post-detail', pk=pk)
	else:
		form = NewCommentForm()
	return render(request, 'feed/post_detail.html', {'post':post, 'is_liked':is_liked, 'form':form, 'user': user})

@login_required
def create_post(request):
	user = request.user
	if request.method == "POST":
		form = NewPostForm(request.POST, request.FILES)
		if form.is_valid():
			data = form.save(commit=False)
			data.username = user
			data.save()
			messages.success(request, f'Posted Successfully')
			return redirect('homepage')
	else:
		form = NewPostForm()
	return render(request, 'feed/create_post.html', {'form':form})

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	fields = ['description', 'pic', 'tags']
	template_name = 'feed/create_post.html'

	def form_valid(self, form):
		form.instance.user_name = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.username:
			return True
		return False

@login_required
def post_delete(request, pk):
	post = Post.objects.get(pk=pk)
	if request.user == post.username:
		Post.objects.get(pk=pk).delete()
	return redirect('homepage')


@login_required
def search_posts(request):
	query = request.GET.get('p')
	object_list = Post.objects.filter(tags__icontains=query)
	liked = [i for i in object_list if Like.objects.filter(user = request.user, post=i)]
	context ={
		'posts': object_list,
		'liked_post': liked
	}
	return render(request, "feed/search_posts.html", context)

@login_required
def like(request):
	post_id = request.GET.get("likeId", "")
	user = request.user
	post = Post.objects.get(pk=post_id)
	liked= False
	like = Like.objects.filter(user=user, post=post)
	if like:
		like.delete()
	else:
		liked = True
		Like.objects.create(user=user, post=post)
	resp = {
        'liked': liked
    }
	response = json.dumps(resp)
	return HttpResponse(response, content_type = "application/json")
