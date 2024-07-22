from typing import Any
from django.db.models import Q
from django.db.models.query import QuerySet
from blog.models import Page, Post
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView
from blog.models import Post

PER_PAGE = 9

class PostListView(ListView):   
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'
    ordering = '-pk', 
    paginate_by = PER_PAGE
    queryset = Post.objects.get_published()

    # def get_queryset(self) -> QuerySet[Any]:
    #     queryset = super().get_queryset()
    #     queryset.filter(is_published=True)
    #     return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': 'Home -'
            }
        )
        return context
    

class CreatedByListView(PostListView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._temp_args_context: dict[str, Any] = {}

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs) 
        user = self._temp_args_context['user']
        user_full_name = user.username

        if user.first_name:
            user_full_name = f'{user.first_name} {user.last_name}'
        page_title = 'Posts de ' + user_full_name + ' - '

        ctx.update(
            {
                'page_title': page_title
            }
        )

        return ctx
    
    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(created_by__pk=self._temp_args_context['user'].pk)
        return qs
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        author_pk = self.kwargs.get('author_pk')
        user = User.objects.filter(pk=author_pk).first()

        if user is None:
            return redirect('blog:index')
        
        return super().get(request, *args, **kwargs)
    

class CategoryListView(PostListView):
    ...