import unittest
from agent.campus_agent import CampusBuddyAgent
from tools.timetable_tool import lookup_timetable
from tools.calculator_tool import safe_calculate, calculate_attendance
from tools.search_tool import campus_search

class TestCampusBuddyAgent(unittest.TestCase):
    def setUp(self):
        self.agent = CampusBuddyAgent()

    def test_timetable_tool_direct(self):
        # Look up Monday classes
        res = lookup_timetable(day="Monday")
        self.assertTrue(res["success"])
        self.assertGreater(res["count"], 0)
        self.assertTrue(any(c["course_code"] == "CS101" for c in res["classes"]))

        # Look up specific course CS202
        res2 = lookup_timetable(course="CS202")
        self.assertTrue(res2["success"])
        self.assertTrue(any("Knuth" in c["instructor"] for c in res2["classes"]))

    def test_calculator_tool_direct(self):
        # Safe math
        calc = safe_calculate("25 * 4 + 10")
        self.assertTrue(calc["success"])
        self.assertEqual(calc["result"], 110)

        # Zero division safety
        zero_calc = safe_calculate("10 / 0")
        self.assertFalse(zero_calc["success"])
        self.assertIn("Division by zero", zero_calc["error"])

        # Attendance calculation
        att = calculate_attendance(attended=20, total=30, target_percent=75.0)
        self.assertTrue(att["success"])
        self.assertEqual(att["status"], "shortage")
        self.assertGreater(att["classes_needed_to_reach_target"], 0)

    def test_search_tool_direct(self):
        # Library search
        res = campus_search("library hours")
        self.assertTrue(res["success"])
        self.assertGreater(res["count"], 0)
        self.assertIn("Central University Library", res["summary"])

        # Cafeteria search
        food_res = campus_search("cafeteria lunch food")
        self.assertTrue(food_res["success"])
        self.assertGreater(food_res["count"], 0)

    def test_react_loop_timetable_query(self):
        output = self.agent.run("What classes do I have on Monday?")
        trace = output["trace"]
        self.assertTrue(trace.tool_needed)
        self.assertEqual(trace.tool_name, "college_timetable_lookup")
        self.assertIsNotNone(trace.observation)
        self.assertIn("CS101", output["answer"])

    def test_react_loop_math_and_attendance(self):
        # Math calculation query
        output = self.agent.run("Calculate 125 * 8")
        trace = output["trace"]
        self.assertTrue(trace.tool_needed)
        self.assertEqual(trace.tool_name, "calculator")
        self.assertIn("1000", output["answer"])

        # Attendance calculation query
        att_output = self.agent.run("I attended 24 out of 30 classes. What is my attendance percentage?")
        self.assertTrue(att_output["trace"].tool_needed)
        self.assertEqual(att_output["trace"].tool_name, "calculator")
        self.assertIn("80", att_output["answer"])

    def test_react_loop_search(self):
        output = self.agent.run("When does the library close?")
        trace = output["trace"]
        self.assertTrue(trace.tool_needed)
        self.assertEqual(trace.tool_name, "campus_search")
        self.assertIn("Library", output["answer"])

    def test_no_raw_errors_exposed(self):
        # Invalid math expression should fail gracefully without unhandled crash
        output = self.agent.run("what is 10 / 0 ?")
        self.assertNotIn("Traceback", output["answer"])
        self.assertNotIn("ZeroDivisionError", output["answer"])
        self.assertIn("Division by zero is undefined", output["answer"])

if __name__ == "__main__":
    unittest.main()
