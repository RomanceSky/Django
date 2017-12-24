# -*- coding: utf-8 -*-
from functools import wraps

from django.middleware.cache import CacheMiddleware
from django.utils.cache import add_never_cache_headers, patch_cache_control
from django.utils.decorators import (
    available_attrs, decorator_from_middleware_with_args,
)

"""
详解Django框架中的视图级缓存_脚本之家
更加颗粒级的缓存框架使用方法是对单个视图的输出进行缓存。 django.views.decorators.cache定义了一个自动缓存视图响应的cache_page装饰器。 他是很容易使用的:

from django.views.decorators.cache import cache_page
 
def my_view(request):
  # ...
 
my_view = cache_page(my_view, 60 * 15)
也可以使用Python2.4的装饰器语法：

@cache_page(60 * 15)
def my_view(request):
  # ...
cache_page 只接受一个参数： 以秒计的缓存超时时间。 在前例中， “my_view()” 视图的结果将被缓存 15 分钟。 （注意： 为了提高可读性，该参数被书写为 60 * 15 。 60 * 15 将被计算为 900 ，也就是说15 分钟乘以每分钟 60 秒。）
和站点缓存一样，视图缓存与 URL 无关。 如果多个 URL 指向同一视图，每个视图将会分别缓存。 继续 my_view 范例，如果 URLconf 如下所示：

urlpatterns = ('',
  (r'^foo/(\d{1,2})/$', my_view),
)
那么正如你所期待的那样，发送到 /foo/1/ 和 /foo/23/ 的请求将会分别缓存。 但一旦发出了特定的请求（如： /foo/23/ ），之后再度发出的指向该 URL 的请求将使用缓存。
"""
def cache_page(*args, **kwargs):
    """
    Decorator for views that tries getting the page from the cache and
    populates the cache if the page isn't in the cache yet.

    The cache is keyed by the URL and some data from the headers.
    Additionally there is the key prefix that is used to distinguish different
    cache areas in a multi-site setup. You could use the
    get_current_site().domain, for example, as that is unique across a Django
    project.

    Additionally, all headers from the response's Vary header will be taken
    into account on caching -- just like the middleware does.
    """
    # We also add some asserts to give better error messages in case people are
    # using other ways to call cache_page that no longer work.
    if len(args) != 1 or callable(args[0]):
        raise TypeError("cache_page has a single mandatory positional argument: timeout")
    cache_timeout = args[0]
    cache_alias = kwargs.pop('cache', None)
    key_prefix = kwargs.pop('key_prefix', None)
    if kwargs:
        raise TypeError("cache_page has two optional keyword arguments: cache and key_prefix")

    return decorator_from_middleware_with_args(CacheMiddleware)(
        cache_timeout=cache_timeout, cache_alias=cache_alias, key_prefix=key_prefix
    )


def cache_control(**kwargs):
    def _cache_controller(viewfunc):
        @wraps(viewfunc, assigned=available_attrs(viewfunc))
        def _cache_controlled(request, *args, **kw):
            response = viewfunc(request, *args, **kw)
            patch_cache_control(response, **kwargs)
            return response
        return _cache_controlled
    return _cache_controller


def never_cache(view_func):
    """
    Decorator that adds headers to a response so that it will
    never be cached.
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view_func(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response
    return _wrapped_view_func
