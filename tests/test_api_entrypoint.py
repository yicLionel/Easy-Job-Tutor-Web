import unittest


class ApiEntrypointTests(unittest.TestCase):
    def test_vercel_entrypoint_imports_as_package(self):
        from api.index import app

        route_paths = {route.path for route in app.routes}
        self.assertIn("/api/health", route_paths)
        self.assertIn("/api/analyze", route_paths)

    def test_health_endpoint(self):
        from api.index import app

        health_route = next(route for route in app.routes if route.path == "/api/health")
        self.assertEqual(health_route.endpoint(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
