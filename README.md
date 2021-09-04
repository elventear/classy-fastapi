# IMPORTANT

Unfortunately this does not work with `async` routes with Python versions less than 3.8 due to bugs in
`inspect.iscoroutinefunction` (see https://stackoverflow.com/a/52422903/1431244 for details). Specifically with older
versions of Python `iscoroutinefunction` incorrectly returns false so `async` routes aren't `await`'d. However, the only
reason Companion is still on Python 3.7 is to support outdated versions of TensorFlow due to now fixed issues with
TFLite and the Coral board so we will be upgrading to Python 3.9 soon.

# Overview

This directory contains classes and decorators to use FastAPI with "class based routing".

In particular, FastAPI generally has one define routes like:

```py
app = FastAPI()

@app.get('/echo/{x}')
def echo(x: int) -> int:
   return x
```

Note that `app` is a global. Furthermore, [FastAPI's suggested way of doing dependency
injection](https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/) is handy for things like pulling
values out of header in the HTTP request. However, they don't work well for more standard dependency injection scenarios
where we'd like to do something like inject a DAO or database connection. For that, FastAPI suggests [their
parameterized dependencies](https://fastapi.tiangolo.com/advanced/advanced-dependencies/) which might look something
like:

```py
app = FastAPI()

class ValueToInject:
   def __init__(self, y: int) -> None:
      self.y = y

   def __call__(self) -> int:
      return self.y

to_add = ValueToInject(2)

@app.get('/add/{x}')
def add(x: int, y: Depends(to_add)) -> int:
   return x + y
```

This works but there's a few issues:

* The `Dependency` must be a callable which requires an unfortunate amount of boilerplate.
* If we want to use the same dependency on several routes, as we would with something like a database connection, we
  have to repeat the `Dependency(to_add)` bit on each endpoint. Note that FastAPI lets you group endpoints your we can
  [include the dependency on all of them]( https://fastapi.tiangolo.com/tutorial/bigger-applications) but then there's
  no way to access the dependency so this really only works for things like authentication where the dependency can do
  some route handling (e.g. return a 402 if an auth header is missing).
* `to_add` is a global variable which is limiting.

Let's consider an expanded, more realistic example where we have a group of routes that operate on users to add them,
delete them, change the password, etc. Those routes will need to access a database so we have a DAO that helps set that
up. We're going to take the database URL, password, etc. via command line arguments and then set up our routes.
Furthermore, we'll split up our application into a few separate files. Doing this without class routing looks like the
following:

```py
# main.py

import .user
from .deps import dao

def parse_arg() -> argparse.Namespace:
   """parse command line arguments."""
   ...

def main():
    args = parse_args()
    global dao
    dao = Dao(args.url, args.user, args.password)
    
    app = FastAPI()
    app.include_router(user.router)

####
# dao.py

from dao import Dao

# DAO for injection. We don't know the command line arguments yet but we need to make this global as we need to be able
to access it in user.py below so it's None here and gets set in main()
dao: Optional[Dao] = None

#####
# user.py
from .deps import dao
from dao import Dao
from fastapi.routing import APIRouter

@router.get('/user/{name}')
def get_user_by_name(name: str, dao: Dao = Depends(dao)) -> User:
   return dao.get_user_by_name(name)

@router.delete('/user/{name}')
def delete_user(name: str, dao: Dao = Depends(dao)) -> None:
   dao.delete(name)

# ... additional user methods ...
```

That works but it's a bit verbose. Additionally, as noted above, it has some limitations. For example, suppose we've
updated our API in a breaking way so we've added a `/v2` set of routes. However, the `users.py` routes haven't changed
at all except that we've changed how we store users (e.g. a new password hashing algorithm) so `/v2` user routes need to
use a different DAO. Ideally you'd call `app.include_router` twice with different prefixes but that won't work because
the dependency on the DAO is to _a specific DAO instance_ in `user.py`. Furthermore, this makes testing error prone as
the injected instances are global. If test 1 injects a DAO instance that simulates errors that will affect test 2 unless
you remember to change what was injected.

Let's look at the alternative with class routing as set up in this package:

```py
from dao import Dao
# Here "cr" is short for "class routing"
from fastapi_utils import cr

def parse_arg() -> argparse.Namespace:
   """parse command line arguments."""
   ...


class UserRoutes(cr.Routable):
   """Inherits from Routable."""
   def __init__(self, dao: Dao) -> None:
      """Constructor. The Dao is injected here."""
      self.__dao = Dao

   @cr.get('/user/{name}')
   def get_user_by_name(name: str) -> User:
      return self.__dao.get_user_by_name(name)

   @cr.delete('/user/{name}')
   def delete_user(name: str) -> None:
      self.__dao.delete(name)


def main():
    args = parse_args()
    global dao
    dao = Dao(args.url, args.user, args.password)
    # Simple intuitive injection
    user_routes = UserRoutes(dao)
    
    app = FastAPI()
    # router memeber inherited from cr.Routable and configured per the annotations.
    app.include_router(user_routes.router)
```

That's clearly a bit shorter. It also solves the issues above (e.g. we could easily construct a 2nd instance of
`UserRoutes` passing in a different DAO and pass that to `app.include_router(user_routes2, prefix='/v2')`).

## Alternatives

[FastAPI-utils](https://fastapi-utils.davidmontague.xyz/user-guide/class-based-views/) has a class based views
implementation but the routes are on the class instance rather than on instances of the class. Thus the injection
remains global and you can't instantiate different instances with different things injected.

There's demand for this feature so a number of alternatives have been proposed [in an open
bug](https://github.com/tiangolo/fastapi/issues/270) and [on
StackOverflow](https://stackoverflow.com/questions/2366713/can-a-decorator-of-an-instance-method-access-the-class) but
all seem to require global injection.
