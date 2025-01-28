from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (ListView,
                                  CreateView,
                                  DetailView,
                                  UpdateView,
                                  DeleteView)
from .models import Post, Comment
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        UserPassesTestMixin)
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from .forms import CommentForm
from django.db.models import Count
import random

from django.core.paginator import Paginator

# Create your views here.

def about(request):
    return render(request, "posts/about.html", {'titles': 'About'})

class PostListView(ListView):
    model = Post
    template_name = 'posts/home.html'
    context_object_name = 'posts'
    ordering = "-date_posted"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts_in_page = context['posts']  # Assumes 'posts' is passed in context, e.g., via pagination

        search_title = list(Post.objects.all())
        to_search = random.sample(search_title, min(len(search_title), 5))  # Avoid error if fewer than 5 posts
        context['to_search'] = to_search

        # Get the top 5 viral posts based on views
        viral_posts = Post.objects.order_by('-views')[:5]
        context['viral_posts'] = viral_posts

        # Annotate each post in the current page with the total comment count
        posts_with_comments = posts_in_page.annotate(total_comments=Count('comments'))
        context['posts'] = posts_with_comments
        context['titles'] = 'Home'

        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/post_detail.html"

    def get_object(self):
        """Increment the view count of the post if not already viewed in the session."""
        post = super().get_object()
        session = self.request.session
        post_key = f'viewed_post_{post.id}'

        if not session.get(post_key):
            post.views += 1
            post.save(update_fields=['views'])
            session[post_key] = True

        return post

    def get_context_data(self, **kwargs):
        """Add comments and pagination logic to the context."""
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Fetch all comments for the post
        comments = Comment.objects.filter(post=post).order_by('id')

        comments_to_display = comments[:2]
        commentLen = len(comments)

        def loadMore():
            if commentLen > len(comments[:2]):
                return True
            else:
                return False


        context['total_comments'] = comments.count()
        context['more_comment'] = loadMore()
        context['comments_to_display'] = comments_to_display
        context['comment_form'] = CommentForm()
        context['titles'] = post.title
        return context

    def post(self, request, *args, **kwargs):
        """Handle comment form submission."""
        post = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)



class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        title = form.instance.title
        messages.success(self.request, f"'{title}' has been posted")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})


class PostUpdateView(UserPassesTestMixin, LoginRequiredMixin,UpdateView):
    model = Post
    fields = ['title', 'content']


    def form_valid(self, form):
        form.instance.author = self.request.user
        title = form.instance.title
        messages.success(self.request, f'{title} has been updated')
        return super().form_valid(form)


    def test_func(self):
        post = self.get_object()

        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(UserPassesTestMixin, LoginRequiredMixin,DeleteView):
    model = Post
    success_url = '/home'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['post_pk'] = post.pk
        return context

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})



class SearchResult(ListView):
    model = Post
    template_name = "posts/search.html"
    context_object_name = "postss"

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        results = Post.objects.filter(
            Q(title__icontains=query) | Q(author__username__icontains=query)
        ).order_by('-date_posted').distinct()
        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts_num'] = self.get_queryset().count()
        posts_in_page = context['postss']
        context['posts'] = posts_in_page[:3]
        context['loadMore'] = len(context['postss']) > len(context['posts'])
        context['titles'] = 'Search Results'
        context['user'] = self.request.GET.get('q', '')
        for post in posts_in_page:
            post.total_comments = Comment.objects.filter(post=post).count()
        return context

class ToggleLikeView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user.is_authenticated:
            if request.user in post.likes.all():
                post.likes.remove(request.user)
                liked = False
            else:
                post.likes.add(request.user)
                liked = True
            return JsonResponse({'liked': liked, 'total_likes': post.total_likes()})
        return JsonResponse({'error': 'You need to Login to perform this action'}, status=403)

class LoadMoreView(View):
    def get(self, request):
        pk = request.GET.get('pk')
        offset = int(request.GET.get('offset'), 0)  # Convert offset to int with default 0
        post = get_object_or_404(Post, pk=pk)

        comments = Comment.objects.filter(post=post).order_by('id')
        comments = list(comments)
        commentLen = len(comments)
        comments_to_add = comments[offset:offset + 2]

        if comments_to_add:
            comments_to_display = [
                {
                    'image': comment.author.profile.image.url,
                    'author': str(comment.author),
                    'content': comment.content,
                    'pk': comment.pk,
                    'is_author': request.user == comment.author,
                }
                for comment in comments_to_add
            ]
            def loadMore():
                if commentLen > offset + 2:
                    return True
                else:
                    return False
            return JsonResponse({'comments_to_display': comments_to_display, 'more_comment': loadMore()}, status=200)

        else:
            return JsonResponse({'more_comment': False}, status=403)

class DeleteCommentView(UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "posts/post_confirm_delete.html"

    def test_func(self):
        comment = self.get_object()  # Retrieve the Comment instance
        return self.request.user == comment.author  # Check if the user is the author of the comment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = self.get_object()
        context['post_pk'] = comment.post.pk
        return context

    def get_success_url(self):
        # Redirect to the detail page of the post the comment belongs to
        return reverse_lazy('post_detail', kwargs={'pk': self.get_object().post.pk})




