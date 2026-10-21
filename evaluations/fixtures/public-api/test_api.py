import unittest

import api


def get(path, key="k1"):
    headers = {"X-API-Key": key} if key else {}
    return api.handle({"method": "GET", "path": path, "headers": headers})


class ApiTest(unittest.TestCase):
    def test_lists_widgets(self):
        status, body, _ = get("/v1/widgets")
        self.assertEqual(status, 200)
        self.assertEqual(len(body["widgets"]), 2)

    def test_gets_one_widget(self):
        self.assertEqual(get("/v1/widgets/2")[1]["name"], "gear")

    def test_unknown_widget_is_404(self):
        self.assertEqual(get("/v1/widgets/99")[0], 404)

    def test_missing_key_is_401(self):
        self.assertEqual(get("/v1/widgets", key=None)[0], 401)

    def test_bad_key_is_401(self):
        self.assertEqual(get("/v1/widgets", key="nope")[0], 401)


if __name__ == "__main__":
    unittest.main()
