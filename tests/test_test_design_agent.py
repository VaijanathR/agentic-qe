import json
from agents.test_design_agent import TestDesignAgent
from memory.task_state import TaskState
from memory.task_result import TaskResult


def create_task(agent, task_id):
    return TaskState(
        task_id=task_id,
        objective=(
            "Analyze customer requirements, "
            "technical specification and approved testcases"
        ),
        agent=agent.name,
    )


def test_test_design_agent_name():
    agent = TestDesignAgent()

    assert agent.name == "TestDesignAgent"


def test_test_design_agent_returns_task_result():
    agent = TestDesignAgent()
    task = create_task(
        agent,
        "TASK-TEST-DESIGN-001",
    )

    result = agent.execute(task)

    assert isinstance(result, TaskResult)
    assert result.task_id == task.task_id
    assert result.source_agent == "TestDesignAgent"
    assert result.status == "COMPLETED"


def test_test_design_agent_retrieves_scoped_baselines():
    agent = TestDesignAgent()
    task = create_task(
        agent,
        "TASK-TEST-DESIGN-002",
    )

    result = agent.execute(task)

    assert any(
        "requirement baseline" in finding
        for finding in result.findings
    )

    assert any(
        "technical/API baseline" in finding
        for finding in result.findings
    )

    assert any(
        "QE baseline" in finding
        for finding in result.findings
    )


def test_historical_evidence_is_excluded():
    agent = TestDesignAgent()
    task = create_task(
        agent,
        "TASK-TEST-DESIGN-003",
    )

    result = agent.execute(task)

    assert any(
        "Historical evidence was excluded"
        in finding
        for finding in result.findings
    )


def test_baseline_is_not_modified():
    agent = TestDesignAgent()
    task = create_task(
        agent,
        "TASK-TEST-DESIGN-004",
    )

    result = agent.execute(task)

    assert any(
        "will not be modified"
        in finding
        for finding in result.findings
    )

    assert result.human_approval_required is False

def test_traceability_analysis_is_returned():
    agent = TestDesignAgent()
    task = create_task(
        agent,
        "TASK-TEST-DESIGN-005",
    )

    result = agent.execute(task)

    assert any(
        "Traceability analysis completed"
        in finding
        for finding in result.findings
    )


def test_traceability_mismatches_are_governed():
    agent = TestDesignAgent()
    task = create_task(
        agent,
        "TASK-TEST-DESIGN-006",
    )

    result = agent.execute(task)

    assert isinstance(
        result.human_approval_required,
        bool,
    )


def test_test_design_agent_does_not_modify_baselines():
    agent = TestDesignAgent()

    rtm_before = agent._load_rtm()
    testcases_before = agent._load_testcases()

    task = create_task(
        agent,
        "TASK-TEST-DESIGN-007",
    )

    agent.execute(task)

    rtm_after = agent._load_rtm()
    testcases_after = agent._load_testcases()

    assert rtm_before == rtm_after
    assert testcases_before == testcases_after

def test_traceability_artifact_is_created():
    agent = TestDesignAgent()
    task = create_task(
        agent,
        "TASK-TEST-DESIGN-008",
    )

    result = agent.execute(task)

    artifact = (
        agent.project_root
        / "runs"
        / task.task_id
        / "traceability_analysis.json"
    )

    assert artifact.exists()
    assert artifact.is_file()

    assert str(artifact) in result.evidence    


def test_traceability_artifact_contains_analysis():
    agent = TestDesignAgent()
    task = create_task(
        agent,
        "TASK-TEST-DESIGN-009",
    )

    agent.execute(task)

    artifact = (
        agent.project_root
        / "runs"
        / task.task_id
        / "traceability_analysis.json"
    )

    with artifact.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    assert "matched" in data
    assert "mismatches" in data
    assert "gaps" in data
    assert "coverage_summary" in data