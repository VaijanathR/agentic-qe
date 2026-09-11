class Requirement:

    def __init__(
        self,
        requirement_id,
        title,
        description,
        source_knowledge_id,
        source_document,
        requirement_type=None,
        priority=None,
    ):
        self.requirement_id = requirement_id
        self.title = title
        self.description = description
        self.source_knowledge_id = source_knowledge_id
        self.source_document = source_document
        self.requirement_type = requirement_type
        self.priority = priority

    def to_dict(self):
        return {
            "requirement_id": self.requirement_id,
            "title": self.title,
            "description": self.description,
            "source_knowledge_id": self.source_knowledge_id,
            "source_document": self.source_document,
            "requirement_type": self.requirement_type,
            "priority": self.priority,
        }