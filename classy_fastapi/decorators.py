from typing import Any, Callable, List, TypeVar

from .route_args import EndpointDefinition, RouteArgs

AnyCallable = TypeVar('AnyCallable', bound=Callable[..., Any])


def route(path: str, methods: List[str], **kwargs: Any) -> Callable[[AnyCallable], AnyCallable]:
    """General purpose route definition. Requires you to pass an array of HTTP methods like GET, POST, PUT, etc.

    The remaining kwargs are exactly the same as for FastAPI's decorators like @get, @post, etc.

    Most users will probably want to use the shorter decorators like @get, @post, @put, etc. so they don't have to pass
    the list of methods.
    """
    def marker(method: AnyCallable) -> AnyCallable:
        setattr(method, '_endpoint',
                EndpointDefinition(endpoint=method, args=RouteArgs(path=path, methods=methods, **kwargs)))
        return method
    return marker


def get(path: str, **kwargs: Any) -> Callable[[AnyCallable], AnyCallable]:
    return route(path, methods=['GET'], **kwargs)


def post(path: str, **kwargs: Any) -> Callable[[AnyCallable], AnyCallable]:
    return route(path, methods=['POST'], **kwargs)


def put(path: str, **kwargs: Any) -> Callable[[AnyCallable], AnyCallable]:
    return route(path, methods=['PUT'], **kwargs)


def delete(path: str, **kwargs: Any) -> Callable[[AnyCallable], AnyCallable]:
    return route(path, methods=['DELETE'], **kwargs)
