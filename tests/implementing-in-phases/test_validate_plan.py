"""Tests for skills/implementing-in-phases/scripts/validate_plan.py.

Each test writes a plan directory to a temporary location, runs the script
as a separate process, and checks the exit status and the reported findings.
"""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "implementing-in-phases" / "scripts" / "validate_plan.py"


def run_validator(plan_dir):
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_dir)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    return completed.returncode, completed.stdout


def make_phase(phase_id, depends_on=(), steps=None, **fields):
    phase = {
        "id": phase_id,
        "title": "Phase {}".format(phase_id),
        "goal": "Goal of phase {}".format(phase_id),
        "dependsOn": list(depends_on),
        "acceptanceCriteria": ["The new behavior is observable"],
        "constraints": ["Keep the public API compatible"],
        "contextFiles": ["src/app.py"],
        "steps": steps
        if steps is not None
        else [{"file": "src/app.py", "action": "modify", "detail": "Change the behavior"}],
        "verification": ["python -m unittest"],
    }
    phase.update(fields)
    return phase


def make_result(phase_id, status="completed", verification=None, **fields):
    result = {
        "phase": phase_id,
        "status": status,
        "summary": "Implemented the phase",
        "changedFiles": ["src/app.py"],
        "verification": verification
        if verification is not None
        else [{"item": "python -m unittest", "status": "passed", "detail": "Ran 3 tests, OK"}],
        "deviations": [],
        "handoff": [],
    }
    result.update(fields)
    return result


class Plan:
    """A repository and a plan directory in a temporary location."""

    def __init__(self, test, plan_inside_repo=False):
        tmp = tempfile.TemporaryDirectory()
        test.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.repo = base / "repo"
        (self.repo / "src").mkdir(parents=True)
        (self.repo / "src" / "app.py").write_text("print('app')\n", encoding="utf-8")
        self.dir = self.repo / "plans" if plan_inside_repo else base / "plan"
        self.dir.mkdir()
        self.index = {
            "task": "Add a feature",
            "repoRoot": str(self.repo),
            "effort": {"planning": "high", "implementation": "medium"},
            "createdAt": "2026-11-05T10:00:00+09:00",
            "openQuestions": [],
            "phases": [],
        }
        self.phases = {}
        self.results = {}

    def add(self, phase):
        name = "phase-{:02d}.json".format(phase["id"])
        self.index["phases"].append(
            {"id": phase["id"], "file": name, "title": phase["title"], "dependsOn": list(phase["dependsOn"])}
        )
        self.phases[name] = phase
        return phase

    def add_result(self, result, name=None):
        self.results[name or "result-{:02d}.json".format(result["phase"])] = result

    def write(self):
        files = dict(self.phases)
        files.update(self.results)
        files["plan-index.json"] = self.index
        for name, data in files.items():
            (self.dir / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def run(self):
        self.write()
        return run_validator(self.dir)


class ValidatePlanTestCase(unittest.TestCase):
    def two_phase_plan(self, **options):
        plan = Plan(self, **options)
        plan.add(make_phase(1))
        plan.add(
            make_phase(
                2,
                depends_on=[1],
                steps=[{"file": "src/report.py", "action": "create", "detail": "Add the report module"}],
            )
        )
        return plan

    def assert_ok(self, outcome, warnings=False):
        code, output = outcome
        self.assertEqual(code, 0, output)
        self.assertIn("OK:", output)
        if not warnings:
            self.assertNotIn("WARNING", output)
        return output

    def assert_errors(self, outcome, *fragments):
        code, output = outcome
        self.assertEqual(code, 1, output)
        self.assertIn("NG:", output)
        for fragment in fragments:
            self.assertIn(fragment, output)
        return output


class PlanStructureTest(ValidatePlanTestCase):
    def test_valid_plan_passes(self):
        output = self.assert_ok(self.two_phase_plan().run())
        self.assertIn("OK: 2 phase(s), 0 warning(s).", output)

    def test_missing_required_field(self):
        plan = self.two_phase_plan()
        del plan.phases["phase-01.json"]["acceptanceCriteria"]
        self.assert_errors(plan.run(), "ERROR phase-01.json: missing required field 'acceptanceCriteria'")

    def test_wrong_type(self):
        plan = self.two_phase_plan()
        plan.phases["phase-01.json"]["steps"] = "Edit src/app.py"
        self.assert_errors(plan.run(), "ERROR phase-01.json steps: must be an array of steps, not a string")

    def test_empty_acceptance_criteria(self):
        plan = self.two_phase_plan()
        plan.phases["phase-02.json"]["acceptanceCriteria"] = []
        self.assert_errors(plan.run(), "phase-02.json acceptanceCriteria: must contain at least one entry")

    def test_invalid_action(self):
        plan = self.two_phase_plan()
        plan.phases["phase-01.json"]["steps"][0]["action"] = "rename"
        self.assert_errors(plan.run(), "'rename' (a string) is not one of create, modify, delete")

    def test_duplicate_phase_id(self):
        plan = self.two_phase_plan()
        plan.index["phases"][1]["id"] = 1
        plan.index["phases"][1]["dependsOn"] = []
        self.assert_errors(plan.run(), "phase id 1 is already used by phases[0]")

    def test_phase_file_disagrees_with_index(self):
        plan = self.two_phase_plan()
        plan.phases["phase-02.json"]["title"] = "Another title"
        plan.phases["phase-02.json"]["dependsOn"] = []
        self.assert_errors(
            plan.run(),
            "phase-02.json title: 'Another title' differs from 'Phase 2'",
            "phase-02.json dependsOn: [] differs from [1]",
        )

    def test_missing_phase_file(self):
        plan = self.two_phase_plan()
        plan.write()
        (plan.dir / "phase-02.json").unlink()
        self.assert_errors(run_validator(plan.dir), "phase-02.json: listed in plan-index.json as phase 2")

    def test_invalid_json_reports_position(self):
        plan = self.two_phase_plan()
        plan.write()
        (plan.dir / "phase-01.json").write_text('{"id": 1,\n  "title": }\n', encoding="utf-8")
        self.assert_errors(run_validator(plan.dir), "phase-01.json: not valid JSON", "line 2")

    def test_missing_plan_directory(self):
        code, output = run_validator(Path(tempfile.gettempdir()) / "no-such-plan-directory-for-tests")
        self.assertEqual(code, 2, output)

    def test_repo_root_must_be_an_existing_absolute_path(self):
        plan = self.two_phase_plan()
        plan.index["repoRoot"] = "relative/repo"
        self.assert_errors(plan.run(), "'relative/repo' must be an absolute path")
        plan.index["repoRoot"] = str(plan.repo / "missing")
        self.assert_errors(plan.run(), "doesn't exist or isn't a directory")

    def test_plan_inside_repository_is_rejected(self):
        plan = self.two_phase_plan(plan_inside_repo=True)
        self.assert_errors(plan.run(), "is inside repoRoot; keep plans outside the repository")

    def test_paths_must_stay_inside_repo_root(self):
        plan = self.two_phase_plan()
        plan.phases["phase-01.json"]["steps"][0]["file"] = "../outside.py"
        plan.phases["phase-01.json"]["contextFiles"] = ["/etc/hosts"]
        self.assert_errors(plan.run(), "'../outside.py' points outside repoRoot", "'/etc/hosts' is an absolute path")

    def test_effort_names_each_role(self):
        plan = self.two_phase_plan()
        plan.index["effort"] = "high"
        self.assert_errors(plan.run(), "must be an object with 'planning' and 'implementation'")

    def test_open_questions_block_implementation(self):
        plan = self.two_phase_plan()
        plan.index["openQuestions"] = ["Should the report include archived items?"]
        self.assert_errors(plan.run(), "1 open question(s) remain")

    def test_unknown_field_warns(self):
        plan = self.two_phase_plan()
        plan.phases["phase-01.json"]["acceptanceCriterias"] = ["typo"]
        output = self.assert_ok(plan.run(), warnings=True)
        self.assertIn("unknown field 'acceptanceCriterias'", output)


class SizeTest(ValidatePlanTestCase):
    def test_large_phase_is_accepted(self):
        plan = Plan(self)
        steps = [
            {"file": "src/app.py", "action": "modify", "detail": "Detailed change {}: {}".format(n, "x" * 600)}
            for n in range(40)
        ]
        plan.add(make_phase(1, steps=steps))
        outcome = plan.run()
        self.assertGreater((plan.dir / "phase-01.json").stat().st_size, 15 * 1024)
        self.assert_ok(outcome)


class DependencyTest(ValidatePlanTestCase):
    def test_unknown_dependency(self):
        plan = self.two_phase_plan()
        plan.index["phases"][1]["dependsOn"] = [7]
        plan.phases["phase-02.json"]["dependsOn"] = [7]
        self.assert_errors(plan.run(), "phase 2 depends on phase 7, which doesn't exist (phase ids: 1, 2)")

    def test_self_dependency(self):
        plan = self.two_phase_plan()
        plan.index["phases"][1]["dependsOn"] = [2]
        plan.phases["phase-02.json"]["dependsOn"] = [2]
        self.assert_errors(plan.run(), "phase 2 depends on itself")

    def test_dependency_cycle(self):
        plan = Plan(self)
        plan.add(make_phase(1, depends_on=[3]))
        plan.add(make_phase(2, depends_on=[1]))
        plan.add(make_phase(3, depends_on=[2]))
        self.assert_errors(plan.run(), "dependency cycle: 1 -> 3 -> 2 -> 1")


class FileTest(ValidatePlanTestCase):
    def test_modifying_a_missing_file_warns(self):
        plan = self.two_phase_plan()
        plan.phases["phase-01.json"]["steps"][0]["file"] = "src/missing.py"
        output = self.assert_ok(plan.run(), warnings=True)
        self.assertIn("modify src/missing.py: it doesn't exist under repoRoot", output)

    def test_file_created_by_an_earlier_phase(self):
        plan = self.two_phase_plan()
        plan.add(
            make_phase(
                3,
                depends_on=[2],
                steps=[{"file": "src/report.py", "action": "modify", "detail": "Extend the report"}],
                contextFiles=["src/report.py"],
            )
        )
        self.assert_ok(plan.run())

    def test_missing_dependency_on_the_creating_phase(self):
        plan = self.two_phase_plan()
        plan.add(
            make_phase(3, depends_on=[1], steps=[{"file": "src/report.py", "action": "modify", "detail": "Extend it"}])
        )
        output = self.assert_ok(plan.run(), warnings=True)
        self.assertIn("Phase 2 creates it; add a dependency on it.", output)

    def test_creating_an_existing_file_warns(self):
        plan = self.two_phase_plan()
        plan.phases["phase-02.json"]["steps"][0]["file"] = "src/app.py"
        output = self.assert_ok(plan.run(), warnings=True)
        self.assertIn("create src/app.py: it already exists under repoRoot", output)

    def test_independent_phases_changing_the_same_file_warn(self):
        plan = self.two_phase_plan()
        plan.add(make_phase(3, depends_on=[1]))
        plan.add(make_phase(4, depends_on=[1]))
        output = self.assert_ok(plan.run(), warnings=True)
        self.assertIn("phases 3 and 4 don't depend on each other but both change src/app.py", output)

    def test_implemented_phase_skips_file_checks(self):
        plan = self.two_phase_plan()
        (plan.repo / "src" / "report.py").write_text("REPORT = True\n", encoding="utf-8")
        plan.add_result(make_result(1))
        plan.add_result(make_result(2, changedFiles=["src/report.py"]))
        output = self.assert_ok(plan.run())
        self.assertIn("results: phase 1 completed, phase 2 completed", output)


class ResultTest(ValidatePlanTestCase):
    def test_valid_result_passes(self):
        plan = self.two_phase_plan()
        plan.add_result(make_result(1, handoff=["report() returns a dict keyed by SKU"]))
        self.assert_ok(plan.run())

    def test_completed_with_a_failed_check_is_rejected(self):
        plan = self.two_phase_plan()
        plan.add_result(
            make_result(1, verification=[{"item": "python -m unittest", "status": "failed", "detail": "1 failure"}])
        )
        self.assert_errors(plan.run(), "completed, but verification has failed entries")

    def test_unverified_requires_a_check_that_was_not_run(self):
        plan = self.two_phase_plan()
        plan.add_result(make_result(1, status="unverified"))
        self.assert_errors(plan.run(), "unverified requires at least one not_run entry")

    def test_unverified_with_a_check_that_was_not_run(self):
        plan = self.two_phase_plan()
        not_run = [{"item": "python -m unittest", "status": "not_run", "detail": "The test database isn't available"}]
        plan.add_result(make_result(1, status="unverified", verification=not_run))
        self.assert_ok(plan.run())

    def test_check_that_was_not_run_needs_a_reason(self):
        plan = self.two_phase_plan()
        not_run = [{"item": "python -m unittest", "status": "not_run", "detail": ""}]
        plan.add_result(make_result(1, status="unverified", verification=not_run))
        self.assert_errors(plan.run(), "say why the item is not_run")

    def test_unknown_status_is_rejected(self):
        plan = self.two_phase_plan()
        plan.add_result(make_result(1, status="done"))
        self.assert_errors(plan.run(), "'done' (a string) is not one of completed, unverified")

    def test_escalation_is_required_when_work_stops(self):
        plan = self.two_phase_plan()
        plan.add_result(make_result(1, status="needs_replan"))
        self.assert_errors(plan.run(), "status needs_replan requires an 'escalation' object")

    def test_failed_needs_reproduction_and_attempts(self):
        plan = self.two_phase_plan()
        failing = [{"item": "python -m unittest", "status": "failed", "detail": "test_report fails"}]
        plan.add_result(
            make_result(1, status="failed", verification=failing, escalation={"reason": "The cause is unknown"})
        )
        self.assert_errors(plan.run(), "failed requires 'reproduction'", "failed requires 'attempts'")

    def test_failed_with_full_escalation_passes(self):
        plan = self.two_phase_plan()
        failing = [{"item": "python -m unittest", "status": "failed", "detail": "test_report fails"}]
        escalation = {
            "reason": "The cause is unknown",
            "reproduction": "python -m unittest tests.test_report",
            "logs": ["logs/phase-01-unittest.txt"],
            "attempts": ["Reverted the formatter change; the test still fails"],
        }
        plan.add_result(make_result(1, status="failed", verification=failing, escalation=escalation))
        self.assert_ok(plan.run())

    def test_result_for_an_unknown_phase(self):
        plan = self.two_phase_plan()
        plan.add_result(make_result(9))
        self.assert_errors(plan.run(), "9 (an integer) isn't a phase id in plan-index.json")

    def test_missing_verification_entry_warns(self):
        plan = self.two_phase_plan()
        result = make_result(1)
        result["verification"][0]["item"] = "python -m unittest tests.test_app"
        plan.add_result(result)
        output = self.assert_ok(plan.run(), warnings=True)
        self.assertIn("no entry for 'python -m unittest' from phase-01.json", output)

    def test_result_name_matches_the_phase(self):
        plan = self.two_phase_plan()
        plan.add_result(copy.deepcopy(make_result(1)), name="result-1.json")
        output = self.assert_ok(plan.run(), warnings=True)
        self.assertIn("name the file result-01.json", output)


if __name__ == "__main__":
    unittest.main()
