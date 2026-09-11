class TaskResult:
    def __init__(
        self,
        task_id,
        source_agent,
        objective,
        status,
        activities=None,
        findings=None,
        evidence=None,
        decisions=None,
        dependencies=None,
        confidence=None,
        human_approval_required=False,
        next_action=None,
        requirements=None,
    ):
        self.requirements = requirements or []
        self.task_id = task_id
        self.source_agent = source_agent
        self.objective = objective
        self.status = status
        self.activities = activities or []
        self.findings = findings or []
        self.evidence = evidence or []
        self.decisions = decisions or []
        self.dependencies = dependencies or []
        self.confidence = confidence
        self.human_approval_required = (
            human_approval_required
            
        )
        self.next_action = next_action

    def add_activity(self, activity):
        self.activities.append(activity)

    def add_finding(self, finding):
        self.findings.append(finding)

    def add_evidence(self, evidence):
        self.evidence.append(evidence)

    def add_decision(self, decision):
        self.decisions.append(decision)

    def add_requirement(self, requirement):
        self.requirements.append(requirement)

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "source_agent": self.source_agent,
            "objective": self.objective,
            "status": self.status,
            "activities": self.activities,
            "findings": self.findings,
            "evidence": self.evidence,
            "decisions": self.decisions,
            "dependencies": self.dependencies,
            "confidence": self.confidence,
            "human_approval_required": (
                self.human_approval_required
            ),
            "requirements": self.requirements,
            "next_action": self.next_action,
        }