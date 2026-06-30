import unittest

from app import create_app, predict_consumption


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("نظام للتنبؤ", response.get_data(as_text=True))

    def test_legacy_sc1_route_loads_home_page(self):
        response = self.client.get("/sc1.html")

        self.assertEqual(response.status_code, 200)
        self.assertIn("نظام للتنبؤ", response.get_data(as_text=True))

    def test_login_accepts_user_details_and_redirects_to_prediction_form(self):
        response = self.client.post(
            "/login",
            data={
                "username": "Hind",
                "email": "hind@example.com",
                "password": "secret123",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/predict")

    def test_predict_form_requires_login(self):
        response = self.client.get("/predict", follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/login")

    def test_prediction_submission_renders_result(self):
        with self.client.session_transaction() as session:
            session["user"] = {"username": "Hind", "email": "hind@example.com"}

        response = self.client.post(
            "/preprocess",
            data={
                "date": "2026-06-30",
                "temperature": "34.5",
                "working_day": "1",
                "devices": "12",
            },
        )

        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("نتيجة التنبؤ", html)
        self.assertIn("kWh", html)
        self.assertIn("2026-06-30", html)

    def test_legacy_sc5_route_loads_latest_result(self):
        with self.client.session_transaction() as session:
            session["user"] = {"username": "Hind", "email": "hind@example.com"}

        self.client.post(
            "/preprocess",
            data={
                "date": "2026-06-30",
                "temperature": "34.5",
                "working_day": "1",
                "devices": "12",
            },
        )

        response = self.client.get("/sc5.html")

        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("نتيجة التنبؤ", html)
        self.assertIn("kWh", html)

    def test_prediction_validation_rejects_bad_numeric_values(self):
        with self.client.session_transaction() as session:
            session["user"] = {"username": "Hind", "email": "hind@example.com"}

        response = self.client.post(
            "/preprocess",
            data={
                "date": "2026-06-30",
                "temperature": "hot",
                "working_day": "1",
                "devices": "-2",
            },
        )

        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn("أدخل قيما صحيحة", html)

    def test_prediction_formula_is_deterministic(self):
        first = predict_consumption("2026-06-30", 34.5, True, 12)
        second = predict_consumption("2026-06-30", 34.5, True, 12)

        self.assertEqual(first, second)
        self.assertGreater(first["prediction"], 0)
        self.assertGreaterEqual(first["mae"], 0)


if __name__ == "__main__":
    unittest.main()
