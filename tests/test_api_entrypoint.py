import json
from pathlib import Path
import unittest


class ApiEntrypointTests(unittest.TestCase):
    def test_vercel_entrypoint_imports_as_package(self):
        from api.analyze import app as analyze_app
        from api.health import app as health_app
        from api.index import app as index_app

        for app in (index_app, health_app, analyze_app):
            route_paths = {route.path for route in app.routes}
            self.assertIn("/api/health", route_paths)
            self.assertIn("/api/analyze", route_paths)

    def test_health_endpoint(self):
        from api.index import app

        health_route = next(route for route in app.routes if route.path == "/api/health")
        self.assertEqual(health_route.endpoint(), {"status": "ok"})

    def test_vercel_config_does_not_limit_fastapi_to_an_exact_api_file(self):
        config = json.loads(Path("vercel.json").read_text(encoding="utf-8"))
        self.assertNotIn("functions", config)


if __name__ == "__main__":
    unittest.main()
