from typing import Any
from django.db.models import Q
from django.db.models.query import QuerySet
from blog.models import Post
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
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
    allow_empty = False

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(
            catetogy__slug=self.kwargs.get('slug')
        )
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs) 
        
        page_title = f'{self.object_list[0].category.name} - Categoria - '

        ctx.update(
            {
                'page_title': page_title
            }
        )

        return ctx
    

class TagListView(PostListView):
    allow_empty = False

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(
            tag__slug=self.kwargs.get('slug')
        )
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs) 
        
        page_title = f'{self.object_list[0].tag.first().name} - Tag - '

        ctx.update(
            {
                'page_title': page_title
            }
        )

        return ctx
    

class SearchListView(PostListView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._search_value = ''

    def setup(self, request, *args, **kwargs):
        self._search_value = request.GET.get('search', '').strip()
        return super.setup(request, *args, **kwargs)
    
    def get_queryset(self) -> QuerySet[Any]:
        search_value = self._search_value   
        return super().get_queryset().filter(
            Q(title__icontains=search_value) |
            Q(except__icontains=search_value) |
            Q(content__icontains=search_value) 
        )[:PER_PAGE]
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs) 
        search_value = self._search_value
        ctx.update(
            {
                'page_title': f'{search_value[:30]} - Search - ',
                'search_value': search_value
            }
        )
        return ctx
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self._search_value == '':
            return  redirect('blog:index')
        return super().get(request, *args, **kwargs)