from lib import crud

"""Library for interacting with REST services. Wraps some key requests things & allows for easy pickling of established session
  (if it turns out that's a relevant and/or useful thing to do to speed up subsequent calls to the library)
"""


def example():
    @crud.resource(base_url="https://jsonplaceholder.typicode.com")
    class SomeRestResource:
        @crud.get(path="/users/${id}")
        def get(self, response):
            return response.json()

        @crud.request(path="/users", method="GET")
        def get_all(self, response, *argsss, **kwkww):
            return response.json()

        @crud.post(path="/posts")
        def create_post(self, response):
            print("created!", response.status_code)
            return response.json()

    patterns = SomeRestResource()

    print(patterns.get(id=1))
    print(patterns.create_post(json={}))


if __name__ == "__main__":
    example()
