import unittest
from lib import crud


class TestCrudMethods(unittest.TestCase):
    def setUp(self):
        # using typicode for conveinience, TODO create a mock strategy class that can be used here
        @crud.resource(base_url="https://jsonplaceholder.typicode.com")
        class Resource:
            @crud.get(path="/users/${id}")
            def get_single_by_id(self, response):
                "should be injected with http response from base_url + path"
                return response.json()

        self.test_resource = Resource()

    def test_happy_path_get(self):
        "should be able to just call method w. keyword argument where the key was defined in decorator's string parameters"
        response = self.test_resource.get_single_by_id(id=1)
        self.assertTrue(response["id"] == 1)
        response = self.test_resource.get_single_by_id(id=5)
        self.assertTrue(response["id"] == 5)

    def test_happy_path_override(self):
        """should be able to override all parameters given in decorator calls during operation (max flexibility)"""
        response = self.test_resource.get_single_by_id(path="/${type}/2", type="posts")
        self.assertTrue(response["id"] == 2)
        # check that we changed resource types, only "post" has a body
        self.assertTrue("body" in response)


if __name__ == "__main__":
    unittest.main()
