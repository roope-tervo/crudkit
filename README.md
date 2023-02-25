# crud decorator library

This library defines a set of function and class decorators that aim to make dealing with API resources simpler. 

## Usage

### read

The read decorator by default wraps the decorated function with a requests.get() call. 

So if for example we want to create a function to read a single post resource from typicode's dummy json API:

```

from crud-decorators import read

@crud.read("https://jsonplaceholder.typicode.com/posts/${id}")
def fun(response, id):
  print(id, response.status_code)
  return response.json()

fun(id=1)
# => {"id":1,"title":"...} 

```

The decorator accepts one or none positional arguments. If one is specified, it should be a url template string like you would use with `string.Template`. It also accepts any number of keyword arguments. 

When the resulting wrapper function is called, it automatically injects the decorated function with the result of the http request (`requests.Response` object) as a positional argument. 

All decorator and wrapper arguments that are strings will be passed through `string.Template`'s `safe_substitute` method, substituting words starting with $ (and enclosed in optional {} brackets) with matching keyword arguments if they are found. 

