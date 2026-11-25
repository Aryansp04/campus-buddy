import hashlib
import os
import unittest

from server import (
    ROOT_DIR,
    api_attendance,
    api_calculate,
    api_chat,
    api_gpa,
    api_overview,
    api_search,
    api_timetable,
    build_campus_buddy_document,
    AttendanceRequest,
    ChatRequest,
    GpaCourse,
    GpaRequest,
    MathRequest,
)


EXPECTED_SHA256 = {
    "src/shaders/landing-pages/LandingPages.tsx": "4d379461ad00eb4de7900df312878035383de7e1ed4e13283b8143a2eea9d30a",
    "src/shaders/landing-pages/pageTypography.ts": "809cc65797d531cd3b3ca5a56815d55d24b3ee8d293e4e4bad6fdfe6c83244cc",
    "src/shaders/landing-pages/pageRecipes.ts": "c9d9849cc255bac2d1d938d088c50917f84916f1c516d2bbb27fcfd803523233",
    "src/shaders/landing-pages/LandingPageFrame.tsx": "61de2cc50888aac4ac5557420b07fa47ed3543bb57c1e0055fafdefa53dbaa78",
    "public/landing-pages/inner-green-3d.html": "69c3694bd63f44ef9f007ebe4dac57a83e4402e0cdf6b54dd10b96dd4f05e197",
    "public/landing-pages/inner-green-assets/three.min.js": "8a5f7249903b54d30f79f708699d2fed2d6a1d0741a4cd41377d1f01bb5a2271",
    "src/shaders/threeui.css": "efe4447139f1358dd8e9be68edf6fa46cbefbd1de423a4d6c439ca61d2c8eccf",
    "public/landing-pages/inner-green-assets/card-ecostove.jpg": "70ce084084902bc502f00c366405b661ecdff90dee95d363b36a6e146829e433",
    "public/landing-pages/inner-green-assets/card-ethos.jpg": "337627390f499b3ae272cec9e2f83c817694a82f42e1aa10a7b26a2c7d679dff",
    "public/landing-pages/inner-green-assets/lexend-latin.woff2": "1ec8f6ee2750554b4bc59ff0b507d316a82a7ba37e0e5bebc41d3bd9b9faad46",
}


class TestSylvaDashboardIntegration(unittest.TestCase):
    def test_all_registered_sha256_hashes(self):
        for rel_path, expected in EXPECTED_SHA256.items():
            full = os.path.join(ROOT_DIR, rel_path.replace("/", os.sep))
            self.assertTrue(os.path.exists(full), f"Missing required file: {rel_path}")
            with open(full, "rb") as f:
                actual = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(actual, expected, f"SHA-256 mismatch on {rel_path}")

    def test_dashboard_document_structure_and_campus_data(self):
        html = build_campus_buddy_document()
        # Authored Three.js + WebGL2 + typography preserved
        self.assertIn('/landing-pages/inner-green-assets/three.min.js', html)
        self.assertIn('/landing-pages/inner-green-assets/lexend-latin.woff2', html)
        self.assertIn('/landing-pages/inner-green-assets/card-ethos.jpg', html)
        self.assertIn('/landing-pages/inner-green-assets/card-ecostove.jpg', html)
        self.assertIn('id="threeui-page-typography"', html)
        self.assertIn('data-liquid-metal="explore"', html)
        self.assertIn('data-liquid-metal="play"', html)
        self.assertIn('buildButterfly', html)

        # Original Sylva copy replaced with Campus Buddy copy
        for old_text in [
            "Canopy restored",
            "282 ha",
            "Native species",
            "43 mapped",
            "After the Rain",
            "Let the wild lead.",
            "Explore the work",
            ">SYLVA<",
        ]:
            self.assertNotIn(old_text, html)

        for new_text in [
            "Campus Buddy — Student AI Copilot",
            "Meet your",
            "campus companion",
            "Ask Campus Buddy",
            ">CAMPUS<",
            'id="dashboard"',
            'id="cb-chat-form"',
            'id="cb-timetable-grid"',
            'id="cb-directory-grid"',
        ]:
            self.assertIn(new_text, html)

    def test_backend_api_endpoints(self):
        ov = api_overview()
        self.assertEqual(ov["total_classes"], 13)
        self.assertEqual(ov["total_services"], 8)

        tt = api_timetable(query=None, day="Monday", course=None, instructor=None, room=None)
        self.assertTrue(tt["success"])
        self.assertEqual(tt["count"], 3)

        att = api_attendance(AttendanceRequest(attended=23, total=30, target_percent=75.0))
        self.assertTrue(att["success"])
        self.assertEqual(att["status"], "safe")

        calc = api_calculate(MathRequest(expression="15% of 850 + sqrt(144)"))
        self.assertTrue(calc["success"])
        self.assertEqual(calc["result"], 139.5)

        gpa = api_gpa(GpaRequest(courses=[
            GpaCourse(name="CS101", credits=4, grade="A+"),
            GpaCourse(name="MATH201", credits=4, grade="A"),
        ]))
        self.assertTrue(gpa["success"])
        self.assertEqual(gpa["gpa"], 9.5)

        srch = api_search(query="wifi", category=None)
        self.assertTrue(srch["success"])
        self.assertGreater(srch["count"], 0)

        chat_resp = api_chat(ChatRequest(message="How do I connect to campus Wi-Fi?"))
        self.assertEqual(chat_resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
