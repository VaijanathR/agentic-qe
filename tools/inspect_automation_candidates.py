import json

with open("testcases/testcases.json", encoding="utf-8") as f:
    data = json.load(f)

testcases = data if isinstance(data, list) else data["testcases"]

for tc in testcases:
    status = str(tc.get("automation_status", "")).strip()

    if status in {"Candidate", "Agentic"}:
        print(
            f"{tc.get('testcase_id')} | "
            f"{tc.get('requirement_id')} | "
            f"{tc.get('title')} | "
            f"{status} | "
            f"{tc.get('category')}"
        )