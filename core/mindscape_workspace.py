"""Workspace embodiment for the existing native mind, not another agent loop.

These handlers are host actuators. Their presence alone proves neither a learned
RWKV motor decoder nor an agent's ability to choose and use them.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

from habitus_ai.agent_workspace import AgentWorkspace
from habitus_ai.tools import ToolDefinition
from habitus_ai.types import OutputTrunk
from core.mindscape_intention import ABILITY_DESCRIPTIONS


class MindscapeWorkspace(AgentWorkspace):
    """Persistent position, metadata-only touch, real content and checked writes."""

    def _normalize_supplied_path(self, supplied):
        raw = str(supplied).strip()
        path_obj = Path(raw)
        if path_obj.is_absolute():
            if path_obj.is_relative_to(self.root):
                return "/" + path_obj.relative_to(self.root).as_posix()
            parts = path_obj.parts
            for idx in range(1, len(parts)):
                subpath = Path(*parts[idx:])
                candidate = self.root / subpath
                if candidate.exists() or candidate.parent.exists():
                    return "/" + subpath.as_posix()
        return raw

    def resolve_path(self, supplied):
        raw = self._normalize_supplied_path(supplied)
        return super().resolve_path(raw)

    def _destination(self, supplied):
        raw = self._normalize_supplied_path(supplied)
        return super()._destination(raw)

    @staticmethod
    def _attributes(path):
        info = path.lstat()
        kind = ("symlink" if stat.S_ISLNK(info.st_mode) else
                "directory" if stat.S_ISDIR(info.st_mode) else
                "file" if stat.S_ISREG(info.st_mode) else "other")
        return {"name": path.name, "kind": kind, "size_bytes": info.st_size,
                "modified_ns": info.st_mtime_ns, "mode": stat.S_IMODE(info.st_mode),
                "extension_hint": path.suffix.lower() if kind == "file" else ""}

    def sense(self, arguments):
        path = self.resolve_path(arguments.get("path", "."))
        result = {"path": path.relative_to(self.root).as_posix(),
                  "position": self.position, **self._attributes(path),
                  "content_opened": False,
                  "interpretation": "filesystem attributes; extension is a hint, not verified content"}
        if path.is_dir():
            result["entries"] = [self._attributes(child) for child in sorted(path.iterdir())]
        return result

    def move(self, arguments):
        destination = self.resolve_path(arguments["path"])
        if not destination.is_dir():
            raise NotADirectoryError("movement requires a directory")
        before = self.position
        self.position = destination.relative_to(self.root).as_posix()
        self.store.set_metadata("agent_workspace_position", self.position)
        if self.store.get_metadata("agent_workspace_position") != self.position:
            raise OSError("workspace position did not persist")
        return {"previous_position": before, "position": self.position,
                "position_verified": True, "observed": self.sense({"path": "."})}

    def open(self, arguments):
        path = self.resolve_file(arguments["path"])
        before = path.stat()
        payload = path.read_bytes()
        after = path.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
            raise OSError("file changed while opening it; no stable content observation")
        if payload.startswith(b"%PDF-"):
            reader = shutil.which("pdftotext")
            if reader is None:
                raise RuntimeError("PDF opening requires the installed pdftotext reader")
            extracted = subprocess.run([reader, "-layout", "-", "-"], input=payload, capture_output=True)
            if extracted.returncode:
                raise ValueError("PDF text extraction failed: " + extracted.stderr.decode(errors="replace"))
            content, format_name = extracted.stdout.decode("utf-8"), "pdf_text"
            if not content.strip():
                raise ValueError("PDF has no extractable text; image/OCR reading is not connected")
        else:
            content, format_name = payload.decode("utf-8"), "utf8_text"
        return {"path": path.relative_to(self.root).as_posix(), "position": self.position,
                "size_bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                "content": content, "content_opened": True, "format": format_name,
                "complete": True, "text_extraction_only": format_name == "pdf_text"}

    def run(self, arguments):
        """Run the observed script inside a workspace-only filesystem/network scope.

        No runtime or output ceiling is imposed. A nonzero exit is an observed
        execution failure, never a completed task. The regular host is not
        mounted; only the interpreter, system libraries and workspace are.
        """
        path = self.resolve_file(arguments["path"])
        if path.suffix != ".py":
            raise ValueError("this actuator executes Python scripts only")
        if arguments.get("expected_sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError("the current script hash is required before execution")
        bwrap = shutil.which("bwrap")
        if bwrap is None:
            raise RuntimeError("isolated Python execution requires bubblewrap")
        command = [bwrap, "--die-with-parent", "--unshare-all", "--new-session", "--clearenv",
                   "--ro-bind", "/usr", "/usr", "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"]
        for location in ("/bin", "/sbin", "/lib", "/lib64"):
            if Path(location).is_symlink():
                command += ["--symlink", os.readlink(location), location]
            elif Path(location).exists():
                command += ["--ro-bind", location, location]
        if Path("/etc/ld.so.cache").exists():
            command += ["--ro-bind", "/etc/ld.so.cache", "/etc/ld.so.cache"]
        environment = Path(sys.prefix).resolve()
        if not environment.is_relative_to("/usr"):
            command += ["--ro-bind", str(environment), str(environment)]
        command += ["--bind", str(self.root), "/workspace", "--chdir", f"/workspace/{self.position}",
                    "--setenv", "PATH", "/usr/bin:/bin", "--setenv", "HOME", "/tmp",
                    "--setenv", "PYTHONDONTWRITEBYTECODE", "1", "--", sys.executable, "-I",
                    "/workspace/" + path.relative_to(self.root).as_posix()]
        result = subprocess.run(command, capture_output=True, text=True)
        observed = {"path": path.relative_to(self.root).as_posix(),
                    "sha256": arguments["expected_sha256"], "return_code": result.returncode,
                    "stdout": result.stdout, "stderr": result.stderr,
                    "execution_scope": "selected workspace; isolated network and process namespace",
                    "interpreter": sys.executable, "runtime_limit": None, "output_limit": None}
        if result.returncode:
            raise RuntimeError("Python execution failed: " + json.dumps(observed, ensure_ascii=False))
        return observed


class NativeWorkspaceBody:
    """Attach actuators to ContinualMind's existing SELF authorization/return loop."""

    def __init__(self, native, root):
        self.native = native
        self.workspace = MindscapeWorkspace(root, native.mind.store)
        self.abilities = {}
        for action, trunk in (("move", OutputTrunk.DO), ("sense", OutputTrunk.LOOK),
                              ("open", OutputTrunk.LOOK), ("write", OutputTrunk.DO),
                              ("mkdir", OutputTrunk.DO), ("run", OutputTrunk.DO)):
            ability_id = f"ability:helix-workspace-{action}"
            self.abilities[action] = ability_id
            native.tools.register_tool(ToolDefinition(
                tool_id=ability_id, trunk=trunk, label=f"Workspace {action}",
                description=ABILITY_DESCRIPTIONS[action], terms=(), parameters={},
                handler=getattr(self.workspace, action), opaque=True, bind_to_trunk=False,
                sensory_encoder=native._sensory_encoder(ability_id)))
            motives = (native.foundation["drives"]["inquiry"], native.foundation["drives"]["integrity"]) if trunk == OutputTrunk.LOOK else (
                native.foundation["drives"]["agency"], native.foundation["composites"]["responsible_action"])
            for motive in motives:
                native.mind.add_relation(motive, ability_id, side="output")

    def execute(self, action, arguments):
        """A proposal is not authority; only a current selected affordance can act."""
        if action not in self.abilities:
            raise ValueError(f"unknown workspace action: {action}")
        ability_id = self.abilities[action]
        opportunity = self.native._ability_opportunity(ability_id, arguments)
        pulse = self.native.runtime.advance((opportunity,))
        self.native.latest_pulse = pulse
        affordance = self.native._affordance(pulse, ability_id)
        self.native._latest_tool_return_pulse = None
        receipt = self.native.tools.execute(ability_id, dict(arguments), affordance=affordance)
        returned = self.native._latest_tool_return_pulse
        if returned is None or not receipt.return_record_id or not receipt.outcome_id:
            raise RuntimeError("native action has no settled sensory return; no completion established")
        self.native.latest_pulse = returned
        return {"proposal_pulse": pulse.cycle.cycle_id, "selected_affordance": ability_id,
                "return_pulse": returned.cycle.cycle_id, "receipt": receipt.to_dict()}
