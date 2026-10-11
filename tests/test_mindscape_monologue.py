import unittest
from unittest.mock import MagicMock
from pathlib import Path
import json

from core.pulse_loop import PulseLoop
from brain.stability_sentinel import StabilitySentinel
from core.context_focus import ContextFocus, resolve_profiles


class TestMindscapeMonologueAndFocus(unittest.TestCase):

    def test_thought_is_quarantined_by_membrane(self):
        """Internal monologue prefixed with [thought] must NEVER be delivered externally."""
        delivered_calls = []

        def mock_delivery(recipient, text):
            delivered_calls.append((recipient, text))

        loop = PulseLoop.__new__(PulseLoop)
        loop._delivery_callback = mock_delivery
        loop.channel_router = None

        events = ["User is talking to me via direct. They said: hello"]
        feeling = {
            "is_external": True,
            "inbound_speaker": "User",
            "inbound_channel": "direct",
            "modality": "EXTERNAL_COMMUNICATION",
        }

        # 1. An explicit response SHOULD be delivered
        thought_resp = "[response] Hello there, how can I help?"
        delivered = loop._deliver_mindscape_output(thought_resp, events, feeling)
        self.assertTrue(delivered)
        self.assertEqual(len(delivered_calls), 1)
        self.assertEqual(delivered_calls[0], ("User", "Hello there, how can I help?"))

        # 2. An internal thought MUST NOT be delivered
        delivered_calls.clear()
        thought_internal = "[thought] I need to think carefully about this question first."
        delivered = loop._deliver_mindscape_output(thought_internal, events, feeling)
        self.assertFalse(delivered, "Internal [thought] must be quarantined and return False")
        self.assertEqual(len(delivered_calls), 0, "No external delivery callback may be called for [thought]")

    def test_multi_pulse_thinking_preserves_pending_interaction(self):
        """When an agent takes a thinking pulse, the pending request must NOT be cleared."""
        from core.mindscape import Mindscape

        mindscape = object.__new__(Mindscape)
        mindscape.session_id = "test-session"
        mindscape.needs_native_observation = False
        mindscape.continuation = {
            "pending": {
                "recipient": "User",
                "channel": "direct",
                "messages": ["Please search the workspace for scripts"],
                "observations": [],
            }
        }
        mindscape._observed_return_id = None
        mindscape._admitted_foreground = None
        mindscape.native = MagicMock()
        mindscape.native.backend.dump_state.return_value = b"state"
        mindscape.native.backend.encode.return_value = [1, 2, 3]
        mindscape.native.runtime.embedder.embed.return_value = [0.1] * 8
        mindscape._receipt = MagicMock()
        mindscape._save_continuation = MagicMock()

        # Finishing a pulse with delivered_external=False (thinking pulse)
        thought = "[thought] I am examining the workspace structure..."
        mindscape._finish(thought, pulse=1, delivered_external=False)

        # Pending MUST still exist
        self.assertIn("pending", mindscape.continuation, "Pending request must be preserved across thinking pulses")
        self.assertEqual(
            mindscape.continuation["pending"]["messages"],
            ["Please search the workspace for scripts"],
        )

        # Finishing a pulse with delivered_external=True clears the completed task
        response = "[response] I found the scripts in tools/."
        mindscape._finish(response, pulse=2, delivered_external=True)
        self.assertNotIn("pending", mindscape.continuation, "Delivered response must clear completed pending request")

    def test_sentinel_modulates_cognitive_focus(self):
        """StabilitySentinel must provide cognitive focus state combining 384D/8D entropy and feeling."""
        sentinel = StabilitySentinel.__new__(StabilitySentinel)
        sentinel.omega = 0.6
        sentinel.current_entropy = 0.15
        sentinel._spatial_H = 0.10
        sentinel._h_raw_baseline = 0.20  # h_ratio = 0.5 (low entropy / deep focus)
        sentinel.s_total = 0.3
        sentinel.get_severity = MagicMock(return_value=StabilitySentinel.ALL_CLEAR)

        # 1. Deep internal monologue (low entropy, no outward push)
        feeling_internal = {"modality": "INTERNAL_MONOLOGUE", "is_external": False, "speak_probability": 0.1}
        focus_state = sentinel.get_cognitive_focus_state(feeling=feeling_internal)

        self.assertEqual(focus_state["modality"], "INTERNAL_MONOLOGUE")
        self.assertGreater(focus_state["weights"].get("reflection", 0), focus_state["weights"].get("conversation", 0))

        # 2. Action required (pending obligations)
        feeling_action = {"modality": "INTERNAL_ACTION_REQUIRED", "is_external": False, "needs_action": True}
        focus_action = sentinel.get_cognitive_focus_state(feeling=feeling_action, has_pending_obligations=True)

        self.assertEqual(focus_action["modality"], "INTERNAL_ACTION_REQUIRED")
        self.assertGreater(focus_action["weights"].get("action", 0), focus_action["weights"].get("conversation", 0))

    def test_failed_write_does_not_satisfy_obligation(self):
        """A failed write error MUST NOT satisfy the obligation to write a file."""
        from core.mindscape_intention import check_obligations_satisfied

        obligations = {
            "required_abilities": {"write"},
            "target_paths": {"tools/workspace_search.py"},
        }
        obs_failed_write = [{
            "action": "write",
            "path": "tools/workspace_search.py",
            "status": "error",
            "receipt": {"verified": True},
        }]

        # Must NOT be satisfied
        self.assertFalse(
            check_obligations_satisfied(obligations, obs_failed_write, current_position="."),
            "A failed write attempt must not satisfy the obligation to write the file",
        )

        obs_success_write = [{
            "action": "write",
            "path": "tools/workspace_search.py",
            "status": "completed",
            "receipt": {"verified": True},
        }]
        self.assertTrue(
            check_obligations_satisfied(obligations, obs_success_write, current_position="."),
            "A completed write must satisfy the obligation",
        )

    def test_step_guidance_sequences_perception_before_execution(self):
        """When sense is requested, step guidance must prioritize sensing before writing/running."""
        from core.mindscape_intention import step_guidance_for_pending

        obligations = {
            "required_abilities": {"sense", "open", "write", "run"},
            "target_paths": {"tools/workspace_search.py"},
        }

        # Initial step: must guide sense
        guidance_initial = step_guidance_for_pending(obligations, [], current_position=".")
        self.assertIn("sense", guidance_initial.lower(), "Initial guidance must prioritize sensing the workspace")
        self.assertNotIn("action 'run'", guidance_initial.lower(), "Must not tell agent to run before writing")

    def test_step_guidance_provides_sha256_for_replacement(self):
        """When an earlier write created a file, guidance must supply its observed sha256 to allow replacement or run."""
        from core.mindscape_intention import step_guidance_for_pending

        obligations = {
            "required_abilities": {"write", "run"},
            "target_paths": {"tools/workspace_search.py"},
        }
        obs = [
            {
                "action": "write",
                "path": "tools/workspace_search.py",
                "status": "success",
                "receipt": {
                    "sha256": "8a4eac8d6babed01d7855f87db83080c98dad8e6d97d6e2cfa24848844cc1f3f",
                    "verified": True,
                },
            },
            {
                "action": "run",
                "path": "tools/workspace_search.py",
                "status": "error",
                "receipt": {"verified": True},
            },
        ]

        guidance = step_guidance_for_pending(obligations, obs, current_position=".")
        self.assertIn(
            "8a4eac8d6babed01d7855f87db83080c98dad8e6d97d6e2cfa24848844cc1f3f",
            guidance,
            "Guidance must provide observed sha256 to allow update or run",
        )


if __name__ == "__main__":
    unittest.main()
