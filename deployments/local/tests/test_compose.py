"""Check the rendered deployment contract without starting Docker containers."""

import json
import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[3]


class LocalDeploymentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            ["docker", "compose", "--env-file", "/dev/null", "-f",
             "docker-compose-local.yml", "config", "--format", "json"],
            cwd=ROOT,
            env={**os.environ, "WEB_URL": "http://192.0.2.10:17239",
                 "SECRET_KEY": "test-only-django-secret", "LIVE_SERVER_SECRET_KEY": "test-only-live-secret"},
            capture_output=True, text=True, check=True,
        )
        cls.services = json.loads(result.stdout)["services"]

    def test_all_plane_interfaces_build_from_source(self):
        for name in ("web", "admin", "space", "live", "api", "worker", "beat-worker", "migrator"):
            with self.subTest(service=name):
                self.assertIn("build", self.services[name])
                self.assertNotIn(".dev", self.services[name]["build"]["dockerfile"])

    def test_only_one_http_port_is_published(self):
        ports = [(name, port["target"], str(port["published"]))
                 for name, service in self.services.items() for port in service.get("ports", [])]
        self.assertEqual(ports, [("proxy", 80, "17239")])

    def test_rustfs_replaces_minio(self):
        self.assertIn("rustfs/rustfs:", self.services["plane-rustfs"]["image"])
        self.assertNotIn("plane-minio", self.services)
        self.assertEqual(self.services["api"]["environment"]["AWS_S3_ENDPOINT_URL"], "http://plane-rustfs:9000")

    def test_persistent_services_use_data_subdirectories(self):
        for name in ("plane-db", "plane-redis", "plane-mq", "plane-rustfs", "proxy", "beat-worker"):
            with self.subTest(service=name):
                writable = [mount for mount in self.services[name].get("volumes", []) if not mount.get("read_only")]
                self.assertTrue(writable)
                for mount in writable:
                    self.assertEqual(mount["type"], "bind")
                    self.assertTrue(Path(mount["source"]).resolve().is_relative_to(ROOT / "data"))

    def test_migrations_and_dependencies_gate_startup(self):
        self.assertEqual(self.services["api"]["depends_on"]["migrator"]["condition"], "service_completed_successfully")
        self.assertEqual(self.services["migrator"]["depends_on"]["plane-db"]["condition"], "service_healthy")

    def test_same_origin_and_optional_smtp(self):
        env = self.services["api"]["environment"]
        self.assertEqual(env["WEB_URL"], "http://192.0.2.10:17239")
        self.assertEqual(env["CORS_ALLOWED_ORIGINS"], env["WEB_URL"])
        self.assertEqual(env["EMAIL_HOST"], "")
        self.assertEqual(env["ENABLE_SIGNUP"], "1")
        self.assertEqual(env["ENABLE_MAGIC_LINK_LOGIN"], "0")
        self.assertEqual(self.services["live"]["environment"]["LIVE_SERVER_SECRET_KEY"], env["LIVE_SERVER_SECRET_KEY"])

    def test_background_document_conversion_reaches_live_internally(self):
        self.assertEqual(self.services["worker"]["environment"].get("LIVE_BASE_URL"), "http://live:3000")


if __name__ == "__main__":
    unittest.main()
