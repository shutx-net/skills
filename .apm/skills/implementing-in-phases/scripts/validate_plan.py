#!/usr/bin/env python3
"""Validate a plan directory written by the implementing-in-phases skill.

Usage:
    python3 validate_plan.py PLAN_DIR

Checks plan-index.json, every phase file it lists, and any result-*.json
files against references/plan-schema.md. Prints one line per finding:
ERROR lines must be fixed before implementing; WARNING lines deserve a look
but don't block. File size and the number of steps are never limited.

Exit status: 0 with no errors, 1 with errors, 2 when PLAN_DIR can't be read.
Needs only the Python 3 standard library.
"""

import json
import os
import re
import sys

INDEX_FILE = "plan-index.json"
ACTIONS = ("create", "modify", "delete")
CHECK_STATUSES = ("passed", "failed", "not_run")
RESULT_STATUSES = (
    "completed",
    "unverified",
    "needs_replan",
    "needs_user_decision",
    "blocked",
    "failed",
)
ESCALATION_STATUSES = ("needs_replan", "needs_user_decision", "blocked", "failed")
EFFORT_ROLES = ("planning", "implementation")

INDEX_KEYS = ("task", "repoRoot", "effort", "createdAt", "openQuestions", "phases")
INDEX_PHASE_KEYS = ("id", "file", "title", "dependsOn")
PHASE_KEYS = (
    "id",
    "title",
    "goal",
    "dependsOn",
    "acceptanceCriteria",
    "constraints",
    "contextFiles",
    "steps",
    "verification",
    "notes",
)
STEP_KEYS = ("file", "action", "detail")
RESULT_KEYS = (
    "phase",
    "status",
    "summary",
    "model",
    "changedFiles",
    "verification",
    "deviations",
    "handoff",
    "escalation",
)
CHECK_KEYS = ("item", "status", "detail")
DEVIATION_KEYS = ("plan", "actual", "reason")
ESCALATION_KEYS = ("reason", "reproduction", "logs", "attempts")

ISO_8601 = re.compile(
    r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?$"
)
JSON_TYPES = {
    dict: "an object",
    list: "an array",
    str: "a string",
    bool: "a boolean",
    int: "an integer",
    float: "a number",
}


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, message):
        self.errors.append("ERROR {}: {}".format(where, message))

    def warning(self, where, message):
        self.warnings.append("WARNING {}: {}".format(where, message))


class PhaseEntry:
    """A phase as plan-index.json lists it."""

    def __init__(self, position, phase_id, file, title, depends_on):
        self.position = position
        self.phase_id = phase_id
        self.file = file
        self.title = title
        self.depends_on = depends_on


class Phase:
    """What the other checks need from a phase file."""

    def __init__(self, entry):
        self.id = entry.phase_id
        self.label = entry.file
        self.steps = []  # (position, path, action)
        self.context_files = []  # (position, path)
        self.verification = []


# --- Small helpers ---------------------------------------------------------


def json_type(value):
    if value is None:
        return "null"
    return JSON_TYPES.get(type(value), type(value).__name__)


def describe(value):
    if isinstance(value, str):
        return "an empty string" if not value.strip() else "{!r} (a string)".format(value)
    if value is None or isinstance(value, (dict, list)):
        return json_type(value)
    return "{} ({})".format(json.dumps(value), json_type(value))


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def is_text(value):
    return isinstance(value, str) and value.strip() != ""


def load_json(report, path, label):
    duplicates = []

    def keep_last(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                duplicates.append(key)
            obj[key] = value
        return obj

    try:
        with open(path, encoding="utf-8-sig") as handle:
            data = json.load(handle, object_pairs_hook=keep_last)
    except json.JSONDecodeError as error:
        report.error(
            label,
            "not valid JSON: {} at line {}, column {}".format(error.msg, error.lineno, error.colno),
        )
        return None
    except (OSError, UnicodeDecodeError) as error:
        report.error(label, "can't be read: {}".format(error))
        return None
    for key in sorted(set(duplicates)):
        report.warning(label, "field {!r} appears more than once; only the last value is used".format(key))
    return data


def check_object(report, where, value):
    if isinstance(value, dict):
        return True
    report.error(where, "must be an object, not {}".format(json_type(value)))
    return False


def warn_unknown_keys(report, where, data, known):
    for key in data:
        if key not in known:
            report.warning(where, "unknown field {!r}; known fields: {}".format(key, ", ".join(known)))


def get_text(report, where, data, key, required=True):
    if key not in data:
        if required:
            report.error(where, "missing required field {!r}".format(key))
        return None
    value = data[key]
    if not is_text(value):
        report.error("{} {}".format(where, key), "must be a non-empty string, not {}".format(describe(value)))
        return None
    return value


def get_text_list(report, where, data, key, allow_empty, hint=""):
    if key not in data:
        report.error(where, "missing required field {!r}{}".format(key, hint))
        return None
    value = data[key]
    label = "{} {}".format(where, key)
    if not isinstance(value, list):
        report.error(label, "must be an array of strings, not {}".format(json_type(value)))
        return None
    if not value and not allow_empty:
        report.error(label, "must contain at least one entry")
    items = []
    for position, item in enumerate(value):
        if is_text(item):
            items.append(item)
        else:
            report.error("{}[{}]".format(label, position), "must be a non-empty string, not {}".format(describe(item)))
    return items


def relative_path(report, where, path, base="repoRoot"):
    """Return the path normalized with forward slashes, or None if it's unusable."""
    if not is_text(path):
        report.error(where, "must be a non-empty string, not {}".format(describe(path)))
        return None
    if "\\" in path:
        report.warning(where, "{!r} uses backslashes; use forward slashes".format(path))
    posix = path.replace("\\", "/")
    if posix.startswith("/") or re.match(r"^[A-Za-z]:", posix):
        report.error(where, "{!r} is an absolute path; write paths relative to {}".format(path, base))
        return None
    parts = []
    for part in posix.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                report.error(where, "{!r} points outside {}".format(path, base))
                return None
            parts.pop()
        else:
            parts.append(part)
    if not parts:
        report.error(where, "{!r} doesn't name a file".format(path))
        return None
    return "/".join(parts)


def path_list(report, where, data, key, hint):
    """Check an array of relative paths. Returns [(position, path)] or None."""
    if key not in data:
        report.error(where, "missing required field {!r}{}".format(key, hint))
        return None
    value = data[key]
    if not isinstance(value, list):
        report.error("{} {}".format(where, key), "must be an array of paths, not {}".format(json_type(value)))
        return None
    paths = []
    for position, item in enumerate(value):
        path = relative_path(report, "{} {}[{}]".format(where, key, position), item)
        if path is not None:
            paths.append((position, path))
    return paths


def is_within(path, parent):
    return path == parent or path.startswith(parent.rstrip(os.sep) + os.sep)


def git_work_tree(path):
    current = path
    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


# --- plan-index.json -------------------------------------------------------


def check_index(report, plan_dir, index):
    """Return (repo_root, entries). repo_root is None when it's unusable."""
    if not check_object(report, INDEX_FILE, index):
        return None, []
    warn_unknown_keys(report, INDEX_FILE, index, INDEX_KEYS)
    get_text(report, INDEX_FILE, index, "task")
    repo_root = check_repo_root(report, plan_dir, index)
    check_effort(report, index)
    created = get_text(report, INDEX_FILE, index, "createdAt")
    if created is not None and not ISO_8601.match(created.strip()):
        report.warning("{} createdAt".format(INDEX_FILE), "{!r} isn't an ISO 8601 date-time".format(created))
    check_open_questions(report, index)
    return repo_root, check_phase_list(report, index)


def check_repo_root(report, plan_dir, index):
    where = "{} repoRoot".format(INDEX_FILE)
    if "repoRoot" not in index:
        report.error(INDEX_FILE, "missing required field 'repoRoot'; set it to the absolute path of the repository root")
        return None
    value = index["repoRoot"]
    if not is_text(value):
        report.error(where, "must be a non-empty string, not {}".format(describe(value)))
        return None
    if not os.path.isabs(value):
        report.error(where, "{!r} must be an absolute path".format(value))
        return None
    if not os.path.isdir(value):
        report.error(where, "{!r} doesn't exist or isn't a directory".format(value))
        return None
    root = os.path.realpath(value)
    plan = os.path.realpath(plan_dir)
    if is_within(plan, root):
        report.error(where, "the plan directory {} is inside repoRoot; keep plans outside the repository".format(plan))
        return root
    plan_tree = git_work_tree(plan)
    if plan_tree is not None:
        if plan_tree == git_work_tree(root):
            report.error(
                where,
                "the plan directory {} is inside the git repository at {}; keep plans outside it".format(plan, plan_tree),
            )
        else:
            report.warning(
                where,
                "the plan directory {} is inside the git repository at {}; plans belong outside git repositories".format(
                    plan, plan_tree
                ),
            )
    return root


def check_effort(report, index):
    where = "{} effort".format(INDEX_FILE)
    example = '{"planning": "high", "implementation": "medium"}'
    if "effort" not in index:
        report.error(INDEX_FILE, "missing required field 'effort'; record the level for each role, e.g. {}".format(example))
        return
    effort = index["effort"]
    if isinstance(effort, str):
        report.error(
            where,
            "must be an object with 'planning' and 'implementation'; for one level for both roles use "
            '{{"planning": "{0}", "implementation": "{0}"}}'.format(effort),
        )
        return
    if not check_object(report, where, effort):
        return
    warn_unknown_keys(report, where, effort, EFFORT_ROLES)
    for role in EFFORT_ROLES:
        get_text(report, where, effort, role)


def check_open_questions(report, index):
    if "openQuestions" not in index:
        return
    where = "{} openQuestions".format(INDEX_FILE)
    questions = get_text_list(report, INDEX_FILE, index, "openQuestions", allow_empty=True)
    if questions:
        report.error(
            where,
            "{} open question(s) remain. Ask the user, record the answers in the affected phases, "
            "and empty openQuestions before implementing.".format(len(index["openQuestions"])),
        )


def check_depends_on(report, where, data):
    if "dependsOn" not in data:
        report.error(where, "missing required field 'dependsOn'; use [] for none")
        return None
    value = data["dependsOn"]
    label = "{} dependsOn".format(where)
    if not isinstance(value, list):
        report.error(label, "must be an array of phase ids, not {}".format(json_type(value)))
        return None
    depends_on = []
    for position, item in enumerate(value):
        if not is_int(item):
            report.error("{}[{}]".format(label, position), "must be a phase id (an integer), not {}".format(describe(item)))
            return None
        if item in depends_on:
            report.error(label, "lists phase {} more than once".format(item))
            continue
        depends_on.append(item)
    return depends_on


def check_phase_list(report, index):
    where = "{} phases".format(INDEX_FILE)
    if "phases" not in index:
        report.error(INDEX_FILE, "missing required field 'phases'")
        return []
    phases = index["phases"]
    if not isinstance(phases, list):
        report.error(where, "must be an array, not {}".format(json_type(phases)))
        return []
    if not phases:
        report.error(where, "must list at least one phase")
        return []
    entries = []
    used_ids = {}
    used_files = {}
    for position, raw in enumerate(phases):
        label = "{}[{}]".format(where, position)
        if not check_object(report, label, raw):
            continue
        warn_unknown_keys(report, label, raw, INDEX_PHASE_KEYS)
        phase_id = raw.get("id")
        if "id" not in raw:
            report.error(label, "missing required field 'id'")
            phase_id = None
        elif not is_int(phase_id) or phase_id < 1:
            report.error("{} id".format(label), "must be an integer of 1 or more, not {}".format(describe(phase_id)))
            phase_id = None
        file = None
        if "file" not in raw:
            report.error(label, "missing required field 'file'")
        else:
            file = relative_path(report, "{} file".format(label), raw["file"], base="the plan directory")
        title = get_text(report, label, raw, "title")
        depends_on = check_depends_on(report, label, raw)
        if phase_id is None or depends_on is None:
            continue
        if phase_id in used_ids:
            report.error("{} id".format(label), "phase id {} is already used by phases[{}]".format(phase_id, used_ids[phase_id]))
            continue
        used_ids[phase_id] = position
        if file is not None:
            if file in used_files:
                report.error("{} file".format(label), "{} is already used by phases[{}]".format(file, used_files[file]))
                file = None
            else:
                used_files[file] = position
        entries.append(PhaseEntry(position, phase_id, file, title, depends_on))
    return entries


# --- phase-NN.json ---------------------------------------------------------


def check_phase_file(report, plan_dir, entry):
    label = entry.file
    path = os.path.join(plan_dir, entry.file)
    if not os.path.isfile(path):
        report.error(label, "listed in {} as phase {}, but the file doesn't exist".format(INDEX_FILE, entry.phase_id))
        return None
    data = load_json(report, path, label)
    if data is None or not check_object(report, label, data):
        return None
    warn_unknown_keys(report, label, data, PHASE_KEYS)
    phase = Phase(entry)

    if "id" not in data:
        report.error(label, "missing required field 'id'")
    elif not is_int(data["id"]) or data["id"] != entry.phase_id:
        report.error(
            "{} id".format(label),
            "is {}, but {} lists this file as phase {}".format(describe(data["id"]), INDEX_FILE, entry.phase_id),
        )
    title = get_text(report, label, data, "title")
    if title is not None and entry.title is not None and title != entry.title:
        report.error("{} title".format(label), "{!r} differs from {!r} in {}".format(title, entry.title, INDEX_FILE))
    depends_on = check_depends_on(report, label, data)
    if depends_on is not None and sorted(depends_on) != sorted(entry.depends_on):
        report.error(
            "{} dependsOn".format(label),
            "{} differs from {} in {}".format(json.dumps(sorted(depends_on)), json.dumps(sorted(entry.depends_on)), INDEX_FILE),
        )
    get_text(report, label, data, "goal")
    get_text_list(report, label, data, "acceptanceCriteria", allow_empty=False)
    get_text_list(report, label, data, "constraints", allow_empty=True, hint="; use [] when there are none")
    context_files = path_list(report, label, data, "contextFiles", hint="; use [] when the steps are enough")
    if context_files:
        phase.context_files = context_files
    check_steps(report, label, data, phase)
    verification = get_text_list(report, label, data, "verification", allow_empty=False)
    if verification:
        phase.verification = verification
    if "notes" in data and not isinstance(data["notes"], str):
        report.error("{} notes".format(label), "must be a string, not {}".format(json_type(data["notes"])))
    return phase


def check_steps(report, label, data, phase):
    if "steps" not in data:
        report.error(label, "missing required field 'steps'")
        return
    steps = data["steps"]
    if not isinstance(steps, list):
        report.error("{} steps".format(label), "must be an array of steps, not {}".format(json_type(steps)))
        return
    if not steps:
        report.error("{} steps".format(label), "must contain at least one step")
        return
    for position, step in enumerate(steps):
        where = "{} steps[{}]".format(label, position)
        if not check_object(report, where, step):
            continue
        warn_unknown_keys(report, where, step, STEP_KEYS)
        path = None
        if "file" not in step:
            report.error(where, "missing required field 'file'")
        else:
            path = relative_path(report, "{} file".format(where), step["file"])
        action = step.get("action")
        if "action" not in step:
            report.error(where, "missing required field 'action'")
        elif action not in ACTIONS:
            report.error("{} action".format(where), "{} is not one of {}".format(describe(action), ", ".join(ACTIONS)))
        get_text(report, where, step, "detail")
        if path is not None and action in ACTIONS:
            phase.steps.append((position, path, action))


# --- Dependencies ----------------------------------------------------------


def check_dependencies(report, entries):
    """Return {phase id: set of ancestor ids}, or None when the graph is broken."""
    ids = set(entry.phase_id for entry in entries)
    listed = ", ".join(str(phase_id) for phase_id in sorted(ids))
    broken = False
    graph = {}
    for entry in entries:
        where = "{} phases[{}] dependsOn".format(INDEX_FILE, entry.position)
        edges = []
        for dep in entry.depends_on:
            if dep == entry.phase_id:
                report.error(where, "phase {} depends on itself".format(dep))
                broken = True
            elif dep not in ids:
                report.error(
                    where,
                    "phase {} depends on phase {}, which doesn't exist (phase ids: {})".format(entry.phase_id, dep, listed),
                )
                broken = True
            else:
                edges.append(dep)
        graph[entry.phase_id] = edges
    cycles = find_cycles(graph)
    for cycle in cycles:
        report.error(
            "{} phases".format(INDEX_FILE),
            "dependency cycle: {} (each phase depends on the next)".format(" -> ".join(str(node) for node in cycle)),
        )
    if broken or cycles:
        return None
    return ancestors_of(graph)


def find_cycles(graph):
    unvisited, active, done = 0, 1, 2
    state = dict((node, unvisited) for node in graph)
    stack = []
    cycles = []
    seen = set()

    def visit(node):
        state[node] = active
        stack.append(node)
        for dep in graph[node]:
            if state[dep] == active:
                cycle = stack[stack.index(dep):] + [dep]
                key = frozenset(cycle)
                if key not in seen:
                    seen.add(key)
                    cycles.append(cycle)
            elif state[dep] == unvisited:
                visit(dep)
        stack.pop()
        state[node] = done

    for node in sorted(graph):
        if state[node] == unvisited:
            visit(node)
    return cycles


def ancestors_of(graph):
    memo = {}

    def walk(node):
        if node not in memo:
            found = set()
            for dep in graph[node]:
                found.add(dep)
                found |= walk(dep)
            memo[node] = found
        return memo[node]

    for node in graph:
        walk(node)
    return memo


# --- Files under repoRoot and parallel phases ------------------------------


def check_files(report, repo_root, phases, ancestors, implemented):
    created = dict((phase.id, set(p for _, p, a in phase.steps if a == "create")) for phase in phases)
    deleted = dict((phase.id, set(p for _, p, a in phase.steps if a == "delete")) for phase in phases)
    # Ancestors before descendants: a phase has more ancestors than any phase it depends on.
    for phase in sorted(phases, key=lambda p: (len(ancestors[p.id]), p.id)):
        if phase.id in implemented:
            continue  # Its changes may already be on disk.
        before_created = set()
        before_deleted = set()
        for ancestor in ancestors[phase.id]:
            before_created |= created.get(ancestor, set())
            before_deleted |= deleted.get(ancestor, set())

        def on_disk(path):
            return os.path.exists(os.path.join(repo_root, path)) and path not in before_deleted

        own_created = set()
        for position, path, action in phase.steps:
            where = "{} steps[{}]".format(phase.label, position)
            available = on_disk(path) or path in before_created or path in own_created
            if action in ("modify", "delete") and not available:
                others = sorted(
                    other.id
                    for other in phases
                    if other.id != phase.id and path in created[other.id] and other.id not in ancestors[phase.id]
                )
                hint = ""
                if others:
                    hint = " Phase {} creates it; add a dependency on it.".format(", ".join(str(i) for i in others))
                report.warning(
                    where,
                    "{} {}: it doesn't exist under repoRoot and no earlier phase creates it.{}".format(action, path, hint),
                )
            if action == "create" and on_disk(path):
                report.warning(
                    where,
                    "create {}: it already exists under repoRoot; use modify, or say in detail that the file is replaced".format(path),
                )
            if action == "create":
                own_created.add(path)
            elif action == "delete":
                own_created.discard(path)
        for position, path in phase.context_files:
            if not on_disk(path) and path not in before_created:
                report.warning(
                    "{} contextFiles[{}]".format(phase.label, position),
                    "{} doesn't exist under repoRoot and no earlier phase creates it".format(path),
                )


def check_parallel_overlap(report, phases, ancestors):
    changed = dict((phase.id, set(path for _, path, _ in phase.steps)) for phase in phases)
    ordered = sorted(phases, key=lambda p: p.id)
    for position, first in enumerate(ordered):
        for second in ordered[position + 1:]:
            if first.id in ancestors[second.id] or second.id in ancestors[first.id]:
                continue
            shared = changed[first.id] & changed[second.id]
            if shared:
                report.warning(
                    "{} phases".format(INDEX_FILE),
                    "phases {} and {} don't depend on each other but both change {}; "
                    "run them one after the other, not in parallel".format(first.id, second.id, ", ".join(sorted(shared))),
                )


# --- result-NN.json --------------------------------------------------------


def check_results(report, plan_dir, phases_by_id, known_ids):
    """Return (ids of phases with a result, "phase N: status" summaries)."""
    implemented = set()
    summaries = []
    names = sorted(name for name in os.listdir(plan_dir) if name.startswith("result-") and name.endswith(".json"))
    for name in names:
        data = load_json(report, os.path.join(plan_dir, name), name)
        if data is None or not check_object(report, name, data):
            continue
        warn_unknown_keys(report, name, data, RESULT_KEYS)
        phase_id = data.get("phase")
        if "phase" not in data:
            report.error(name, "missing required field 'phase'")
            phase_id = None
        elif not is_int(phase_id) or phase_id not in known_ids:
            report.error("{} phase".format(name), "{} isn't a phase id in {}".format(describe(phase_id), INDEX_FILE))
            phase_id = None
        else:
            implemented.add(phase_id)
            expected = "result-{:02d}.json".format(phase_id)
            if name != expected:
                report.warning(name, "records phase {}; name the file {}".format(phase_id, expected))
        status = data.get("status")
        if "status" not in data:
            report.error(name, "missing required field 'status'")
            status = None
        elif status not in RESULT_STATUSES:
            report.error("{} status".format(name), "{} is not one of {}".format(describe(status), ", ".join(RESULT_STATUSES)))
            status = None
        get_text(report, name, data, "summary")
        if "model" in data and not isinstance(data["model"], str):
            report.error("{} model".format(name), "must be a string, not {}".format(json_type(data["model"])))
        path_list(report, name, data, "changedFiles", hint="; use [] when nothing changed")
        checks = check_verification_results(report, name, data)
        check_deviations(report, name, data)
        get_text_list(report, name, data, "handoff", allow_empty=True, hint="; use [] when there is nothing to hand off")
        check_escalation(report, name, data, status)
        if status is not None and checks is not None:
            check_status_matches(report, name, status, checks)
        phase = phases_by_id.get(phase_id)
        if phase is not None and checks is not None:
            recorded = set(item.strip() for item, _ in checks)
            for item in phase.verification:
                if item.strip() not in recorded:
                    report.warning(
                        "{} verification".format(name),
                        "no entry for {!r} from {}; record it as passed, failed, or not_run".format(item, phase.label),
                    )
        if phase_id is not None and status is not None:
            summaries.append("phase {} {}".format(phase_id, status))
    return implemented, summaries


def check_verification_results(report, name, data):
    """Return [(item, status)] for well-formed entries, or None."""
    if "verification" not in data:
        report.error(name, "missing required field 'verification'")
        return None
    value = data["verification"]
    where = "{} verification".format(name)
    if not isinstance(value, list):
        report.error(where, "must be an array of objects, not {}".format(json_type(value)))
        return None
    checks = []
    for position, check in enumerate(value):
        label = "{}[{}]".format(where, position)
        if not check_object(report, label, check):
            continue
        warn_unknown_keys(report, label, check, CHECK_KEYS)
        item = get_text(report, label, check, "item")
        state = check.get("status")
        if "status" not in check:
            report.error(label, "missing required field 'status'")
            continue
        if state not in CHECK_STATUSES:
            report.error("{} status".format(label), "{} is not one of {}".format(describe(state), ", ".join(CHECK_STATUSES)))
            continue
        detail = check.get("detail", "")
        if not isinstance(detail, str):
            report.error("{} detail".format(label), "must be a string, not {}".format(json_type(detail)))
        elif state != "passed" and not detail.strip():
            report.error("{} detail".format(label), "say why the item is {}".format(state))
        if item is not None:
            checks.append((item, state))
    return checks


def check_status_matches(report, name, status, checks):
    states = set(state for _, state in checks)
    where = "{} status".format(name)
    if status == "completed":
        if not checks:
            report.error(where, "completed requires at least one verification entry")
        elif states - {"passed"}:
            report.error(
                where,
                "completed, but verification has {} entries; use failed when an item failed, "
                "unverified when items couldn't be run".format(" and ".join(sorted(states - {"passed"}))),
            )
    elif status == "unverified":
        if "failed" in states:
            report.error(where, "unverified, but an item failed; use failed")
        elif "not_run" not in states:
            report.error(where, "unverified requires at least one not_run entry; use completed when every item passed")


def check_deviations(report, name, data):
    if "deviations" not in data:
        report.error(name, "missing required field 'deviations'; use [] when there are none")
        return
    value = data["deviations"]
    if not isinstance(value, list):
        report.error("{} deviations".format(name), "must be an array of objects, not {}".format(json_type(value)))
        return
    for position, deviation in enumerate(value):
        label = "{} deviations[{}]".format(name, position)
        if not check_object(report, label, deviation):
            continue
        warn_unknown_keys(report, label, deviation, DEVIATION_KEYS)
        for key in DEVIATION_KEYS:
            get_text(report, label, deviation, key)


def check_escalation(report, name, data, status):
    required = status in ESCALATION_STATUSES
    if "escalation" not in data:
        if required:
            report.error(name, "status {} requires an 'escalation' object that explains why work stopped".format(status))
        return
    where = "{} escalation".format(name)
    escalation = data["escalation"]
    if not check_object(report, where, escalation):
        return
    warn_unknown_keys(report, where, escalation, ESCALATION_KEYS)
    get_text(report, where, escalation, "reason", required=required)
    if "reproduction" in escalation and not isinstance(escalation["reproduction"], str):
        report.error("{} reproduction".format(where), "must be a string, not {}".format(json_type(escalation["reproduction"])))
    for key in ("logs", "attempts"):
        if key in escalation:
            get_text_list(report, where, escalation, key, allow_empty=True)
    if status == "failed":
        if not is_text(escalation.get("reproduction")):
            report.error(where, "failed requires 'reproduction': how to reproduce the failure")
        attempts = escalation.get("attempts")
        if not isinstance(attempts, list) or not any(is_text(attempt) for attempt in attempts):
            report.error(where, "failed requires 'attempts': what was tried and what happened")


# --- Entry point -----------------------------------------------------------


def validate(plan_dir):
    """Return (report, number of phases, result summaries)."""
    report = Report()
    index_path = os.path.join(plan_dir, INDEX_FILE)
    if not os.path.isfile(index_path):
        report.error(INDEX_FILE, "not found in the plan directory")
        return report, 0, []
    index = load_json(report, index_path, INDEX_FILE)
    if index is None:
        return report, 0, []
    repo_root, entries = check_index(report, plan_dir, index)
    phases = []
    for entry in entries:
        if entry.file is not None:
            phase = check_phase_file(report, plan_dir, entry)
            if phase is not None:
                phases.append(phase)
    ancestors = check_dependencies(report, entries)
    phases_by_id = dict((phase.id, phase) for phase in phases)
    known_ids = set(entry.phase_id for entry in entries)
    implemented, results = check_results(report, plan_dir, phases_by_id, known_ids)
    if ancestors is not None:
        if repo_root is not None:
            check_files(report, repo_root, phases, ancestors, implemented)
        check_parallel_overlap(report, phases, ancestors)
    return report, len(entries), results


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    if len(args) == 1 and args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    if len(args) != 1:
        print(__doc__.strip())
        return 2
    plan_dir = args[0]
    if not os.path.isdir(plan_dir):
        print("ERROR: the plan directory {} doesn't exist or isn't a directory".format(plan_dir))
        return 2
    report, phase_count, results = validate(plan_dir)
    for line in report.errors + report.warnings:
        print(line)
    if report.errors:
        print(
            "NG: {} error(s), {} warning(s). Fix the errors and run this script again before implementing.".format(
                len(report.errors), len(report.warnings)
            )
        )
        return 1
    suffix = "; results: {}".format(", ".join(results)) if results else ""
    print("OK: {} phase(s), {} warning(s){}.".format(phase_count, len(report.warnings), suffix))
    return 0


if __name__ == "__main__":
    sys.exit(main())
