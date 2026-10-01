import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from config import Settings, make_llm
from tools import GroqSearchTool, extract_evidence
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def response():
    from groq.types.chat import ChatCompletion
    return ChatCompletion.model_validate({
        "id": "test", "created": 0, "model": "openai/gpt-oss-120b", "object": "chat.completion",
        "choices": [{"index": 0, "finish_reason": "stop", "message": {
            "role": "assistant", "content": "Evidence with caveats.",
            "executed_tools": [{"type": "browser_search", "index": 0, "arguments": '{}',
                "search_results": {"results": [{"title": "Study", "url": "https://example.org/study"}]}}]}}]})


class BoundaryTests(unittest.TestCase):
    def test_groq_payload_strips_internal_cache_marker(self):
        llm = make_llm(Settings("fake"))
        messages = [
            {"role": "system", "content": "Research carefully", "cache_breakpoint": True},
            {"role": "assistant", "content": None, "tool_calls": [
                {"id": "call_1", "type": "function", "function":
                 {"name": "groq_web_research", "arguments": '{"query":"test"}'}}]},
            {"role": "tool", "content": "Evidence", "tool_call_id": "call_1"},
        ]
        payload = llm._prepare_completion_params(messages)
        self.assertTrue(all("cache_breakpoint" not in m for m in payload["messages"]))
        self.assertTrue(messages[0]["cache_breakpoint"])
        self.assertEqual(payload["messages"][1]["tool_calls"], messages[1]["tool_calls"])
        self.assertEqual(payload["messages"][2]["tool_call_id"], "call_1")

    def test_ungrounded_response_rejected(self):
        with self.assertRaises(ValueError):
            extract_evidence(SimpleNamespace(choices=[]))
        unsupported = response()
        unsupported.choices[0].message.executed_tools = []
        unsupported.choices[0].message.content = "See https://example.org/invented"
        with self.assertRaises(ValueError):
            extract_evidence(unsupported)

    def test_success_failure_and_call_budget(self):
        events = []
        tool = GroqSearchTool(Settings("fake"), "Researcher", events.append)
        try:
            self.assertFalse(tool.require_evidence("report")[0])
            with patch.object(tool._client.chat.completions, "create", return_value=response()) as call:
                for _ in range(4):
                    tool.run(query="retrieval practice evidence")
                self.assertEqual(call.call_count, 3)
                self.assertEqual(call.call_args.kwargs["tools"], [{"type": "browser_search"}])
                self.assertEqual(call.call_args.kwargs["tool_choice"], "required")
            self.assertTrue(tool.require_evidence("report")[0])
            self.assertEqual(len(tool.records), 3)
            self.assertTrue(any(e["kind"] == "evidence" for e in events))
        finally:
            tool.close()
        tool = GroqSearchTool(Settings("fake"), "Fact Checker", events.append)
        try:
            with patch.object(tool._client.chat.completions, "create", side_effect=RuntimeError("invalid key fake")):
                result = tool.run(query="check this claim")
            self.assertNotIn("fake", result)
            self.assertIn("invalid key", result)
            self.assertFalse(tool.require_evidence("report")[0])
        finally:
            tool.close()

    def test_agents_and_task_construction(self):
        import crew
        def kickoff(fake_crew):
            self.assertEqual(len(fake_crew.agents), 3)
            self.assertEqual(len(fake_crew.tasks), 3)
            self.assertFalse(fake_crew.memory)
            for task in fake_crew.tasks:
                self.assertIsNotNone(task.guardrail)
                self.assertEqual(len(task.agent.tools), 1)
            return SimpleNamespace(raw="# Test report")
        with patch.object(crew.Crew, "kickoff", kickoff):
            result = crew.run_research("What is retrieval practice?", "Students", "Concise", Settings("fake"), lambda e: None)
        self.assertEqual(result["report"], "# Test report")

    def test_ui_empty_validation_navigation_and_success(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run()
        self.assertFalse(app.exception)
        app.button[0].click().run()
        self.assertTrue(app.error)
        app.radio[0].set_value("Meet the team").run()
        self.assertFalse(app.exception)
        app.radio[0].set_value("Launch guide").run()
        self.assertFalse(app.exception)
        app.radio[0].set_value("Research studio").run()
        app.text_area[0].set_value("What is retrieval practice?")
        app.text_input[0].set_value("fake")
        def fake_run(topic, audience, length, settings, emit):
            for name in ["Researcher", "Fact Checker", "Report Writer"]:
                emit({"kind": "active", "agent": name})
                emit({"kind": "done", "agent": name, "output": "Done"})
            return {"topic": topic, "report": "# Example report\nTest content.", "evidence": []}
        with patch("crew.run_research", side_effect=fake_run):
            app.button[0].click().run(timeout=20)
        self.assertFalse(app.exception)
        self.assertTrue(app.success)
        with patch("crew.run_research", side_effect=RuntimeError("secret error details")):
            app.button[0].click().run(timeout=20)
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertNotIn("result", app.session_state)


if __name__ == "__main__":
    unittest.main()
