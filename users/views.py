from django.shortcuts import render, redirect, get_object_or_404
from .forms import (UserRegisterationForm,
                    UserUpdateForm,
                    ProfileUpdateForm,
                    CustomPasswordResetForm,
                    CustomPasswordResetConfirmForm)
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.db.models import Q
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (PasswordResetView,
                                       PasswordResetConfirmView)
from django.http import JsonResponse
from posts.models import Post, Comment
from django.contrib import messages
from django.urls import reverse_lazy
import random

# Create your views here.

class RegisterView(CreateView):
    model = User
    form_class = UserRegisterationForm
    template_name = "users/register.html"
    success_url = "/login"

    def form_valid(self, form):
        username = form.instance.username
        messages.success(self.request, f'Account for {username} has been created!!')
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, View):
    template_name = 'users/profile.html'

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        posts = Post.objects.filter(author=user).order_by('-date_posted')
        post_to_display = posts[:2]

        loadMore = len(posts) > len(posts[:2])


        title = list(Post.objects.all())
        to_search = random.sample(title, min(len(title), 5))  # Avoid error if fewer than 5 posts

        # Calculate total comments for each post in the paginated posts
        for post in post_to_display:  # Use the paginated posts here
            post.total_comments = Comment.objects.filter(post=post).count()

        return render(request, self.template_name, {
            'user_form': UserUpdateForm(instance=user),
            'profile_form': ProfileUpdateForm(instance=user.profile),
            'user_p': user,
            'posts_num': posts.count(),
            'to_search': to_search,
            'titles': f'{username} Profile',
            'posts': post_to_display,
            'more_post': loadMore,
            'viral_posts': Post.objects.order_by('-views')[:5],
        })

    
    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(self.request, 'Your Profile has been Updated')
            return redirect('profile', username=username)  # Redirect to the updated profile

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
        })

class LoadMorePost(View):
    def get(self, request):
        offset = int(request.GET.get('offset'), 0)
        username = request.GET.get('username')
        posts = Post.objects.filter(Q(author__username__icontains=username) | Q(title__icontains=username)
                                    ).order_by('-date_posted').distinct()
        posts = list(posts)
        user = get_object_or_404(User, username=username)
        post_to_add = posts[offset:offset + 2]

        loadMore = len(posts) > offset + 2

        if post_to_add:
            more_posts = [
                {
                    'author': post.author.username,
                    'content': post.content,
                    'date_posted': post.date_posted.strftime('%b %d, %Y'),
                    'title': post.title,
                    'image': post.author.profile.image.url if post.author.profile.image else '/static/icon.png',
                    'id': post.id,
                    'views': post.views,
                    'total_likes': post.total_likes(),
                    'is_liked': True if user in post.likes.all() else False,
                    'total_comments': post.comments.count(),
                }
                for post in post_to_add
            ]
            return JsonResponse({'more_posts': more_posts, 'loadMore': loadMore}, status=200)
        else:
            return JsonResponse({'loadMore': loadMore}, status=403)



class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "users/password_reset_form.html"
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy('password_reset_complete')

    # def get_context_data(self, **kwargs):
    #     # Explicitly pass the form to the context
    #     context = super().get_context_data(**kwargs)
    #     context['form'] = context.get('form')  # Ensure 'form' is passed to the template
    #     return context


