# Copyright © 2023, Indiana University
# BSD 3-Clause License

"""
Test that flask routes return valid (200) HTTP responses.
"""

from unittest import TestCase

from flaskapp.app import app
app.testing = True


class TestValidRoutes(TestCase):
    def test_get_root_responds_200_status(self):
        with app.test_client() as client:
            self.assertEqual(client.get("/").status_code, 200)
