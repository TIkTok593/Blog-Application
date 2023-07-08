from typing import Any, Dict, Optional
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.views.generic import ListView, CreateView, DetailView, FormView
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.utils.text import slugify
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from taggit.models import Tag
from .models import Post, Comment, Profile, User
from .forms import EmailPostForm, CommentForm,\
                   PostForm, UserRegistrationForm,\
                   ProfileForm

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        print('lksadjflksajdflk')
        print('lksadjflksajdflk')

        tag_slug = kwargs.get('tag_slug')
        tag = None
        post_list = self.get_queryset()
        if tag_slug:
            tag = get_object_or_404(Tag, tag=tag_slug)
            post_list = post_list.filter(tag__in=[tag])  # tag is an array.
        
        paginator = Paginator(post_list, self.paginate_by)  # This post_list is for the variable That get the value from the model
        page_number = self.request.GET.get('page', 1)  # Get the value of the page if it has a one, if not return 1
        print(page_number)
        try:
            posts = paginator.page(page_number)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(1)
        except InvalidPage:
            posts = paginator.page(paginator.num_pages)

        context = super().get_context_data(**kwargs)
        context['posts'] = posts
        context['tag'] = tag
        return context
            

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, tag=tag_slug)
        post_list = post_list.filter(tag__in=[tag]) # here we put the tag in brackets because it's an array

    paginator = Paginator(post_list, 3)  # This post_list is for the variable That get the value from the model
    page_number = request.GET.get('page', 1)  # Get the value of the page if it has a one, if not return 1
    try:
        posts = paginator.page(page_number)

    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 
    'blog/post/list.html', 
    {
        'posts': posts,
        'tag': tag                
    })




@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post/post_create.html'

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        title = form.cleaned_data['title']
        slug = slugify(title)
        form.instance.slug = slug
        form.instance.author = self.request.user
        # form.instance.user = self.request.user

        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('blog:post_list')


@method_decorator(login_required, name='dispatch')
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post/detail.html'
    # queryset = Post.objects.all()
    context_object_name = 'post'
    slug_url_kwarg = 'post'
    year_url_kwarg = 'year'
    month_url_kwarg = 'month'
    day_url_kwarg = 'day'
    def get_queryset(self):
        queryset = Post.objects.all()
        return queryset.filter(
            publish__year=self.kwargs.get('year'),
            publish__month=self.kwargs.get('month'),
            publish__day=self.kwargs.get('day'),
            status=Post.Status.PUBLISHED
        )
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comments.filter(active=True)
        form = CommentForm()
        context['comments'] = comments
        context['form'] = form
        return context



@login_required
def post_detail(request, year, month, day, post):
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404('No Post found.')
    # return render(request, 'blog/post/detail.html', {'post': post})
    post = get_object_or_404(Post, 
                            slug=post,
                            publish__year=year,
                            publish__month=month,
                            publish__day = day,
                            status=Post.Status.PUBLISHED)
    
    comments = post.comments.filter(active=True) # we can use comments, because we defined the related_name in Comments's Model
    form = CommentForm()
    return render(request,
     'blog/post/detail.html',
      {'post': post,
       'comments': comments,
       'form': form
       }
    )



@method_decorator(login_required, name='dispatch')
class PostShareView(View):
    template_name = 'blog/post/share.html'
    form_class = EmailPostForm

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
        form = self.form_class()
        context = {'post': post, 'form': form, 'sent': False}
        return render(request, self.template_name, context)

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, 'abuyahyadiab@gmail.com', [cd['to']])
            sent = True
        else:
            sent = False
        context = {'post': post, 'form': form, 'sent': sent}
        return render(request, self.template_name, context)


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'abuyahyadiab@gmail.com',
                      [cd['to']])
            sent = True


    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form, 'sent': sent})


@method_decorator(login_required, name='dispatch')
class PostCommentView(View):
    template_name = 'blog/post/comment.html'
    form_class = CommentForm

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED) # you have to assure that this is a published post not a draft one.
        form = self.form_class(request.POST)
        comment = None
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})




@require_POST
def post_comment(request, post_id):
    # here the user has been posted a comment to a specific post
    # I'll try to fetch this post, if not exist, an error will be generated
    # If it exist, we will assign this post to a field on that comment's object
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED) # you have to assure that this is a published post not a draft one.
    comment = None
    form = CommentForm(request.POST) # by using request.POST, we get the form object that has been submitted, and we pass it to comment form to check it's validation
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})



class UserRegisterView(View):
    def get(self, request):
        user_form = UserRegistrationForm()
        return render(request,
                  'blog/register.html',
                  {'user_form': user_form})
    
    def post(self, request):
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password1'])
            new_user.save()
            return render(request, 'blog/register_done.html', {'user_form': user_form})
        else:
            return render(request, 'blog/register.html', {'user_form': user_form})



def user_register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)  # don't save the user now, because we want to add on it.
            new_user.set_password(  # this method is for hashing passwords rather than put it in a plain text.
                user_form.cleaned_data['password1']
            )
            new_user.save()
            return render(request, 'blog/register_done.html', {'user_form': user_form})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'blog/register.html',
                  {'user_form': user_form}
                  )




class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = ProfileForm
    template_name='blog/post/profile_create.html'
    
    def get_success_url(self) -> str:
        return reverse("blog:post_list")
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs


class ProfileDetailView(DetailView):
    template_name = 'blog/post/profile_detail.html'
    context_object_name = 'profile'
    pk_url_kwarg = 'pk'

    # def get_(self) -> QuerySet[Any]:
    #     profile = Profile.objects.get(id=self.kwargs['pk'])
    #     return profile
    
    def get_object(self, queryset: QuerySet[Any] | None = ...):
        profile = Profile.objects.get(id=self.kwargs['pk'])
        return profile
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['pk']
        posts = Post.objects.filter(author=user_id)
        context['posts'] = posts
        return context

    
class UserListView(ListView):
    template_name = 'blog/post/users_list.html'
    queryset = User.objects.all()
    context_object_name = 'users'


class UserDetailView(DetailView):
    template_name = 'blog/post/user_detail.html'
    context_object_name = 'user'
    pk_url_kwarg = 'id'

    def get_object(self) -> QuerySet[Any]:
        user = User.objects.get(id=self.kwargs['id'])
        return user
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['id']
        posts = Post.objects.filter(author=user_id)
        profile = Profile.objects.get(user=user_id)
        context['posts'] = posts
        context['profile'] = profile
        return context
    