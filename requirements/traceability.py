class TraceabilityAnalyzer:
    """
    Deterministic analyzer for requirement-to-test traceability.

    The analyzer does not modify requirements, RTM entries,
    or testcases. It identifies relationships, mismatches,
    and coverage gaps for further governance or analysis.
    """

    def _normalize(self, value):
        if value is None:
            return ""

        return " ".join(
            str(value)
            .lower()
            .replace("_", " ")
            .replace("-", " ")
            .split()
        )

    def _semantic_match(self, requirement, rtm_row):
        """
        Performs a conservative semantic comparison.

        Identifier equality is preferred.

        If identifiers differ, title/category similarity may
        indicate a possible relationship, but this is reported
        as a mismatch rather than silently accepted.
        """

        requirement_id = requirement.get("requirement_id")
        rtm_requirement_id = rtm_row.get("Requirement_ID")

        if requirement_id == rtm_requirement_id:
            return {
                "match": True,
                "match_type": "IDENTIFIER",
            }

        requirement_text = self._normalize(
            requirement.get("title", "")
        )

        rtm_text = self._normalize(
            rtm_row.get("Requirement_Title", "")
        )

        if (
            requirement_text
            and rtm_text
            and (
                requirement_text in rtm_text
                or rtm_text in requirement_text
            )
        ):
            return {
                "match": True,
                "match_type": "SEMANTIC_IDENTIFIER_MISMATCH",
            }

        return {
            "match": False,
            "match_type": None,
        }

    def analyze(self, requirements, rtm_rows, testcases):
        matched = []
        mismatches = []
        gaps = []
        mapped_rtm_ids = set()
        mapped_testcase_ids = set()

        for requirement in requirements:
            requirement_id = requirement.get(
                "requirement_id"
            )

            candidate_rtm = None
            match_type = None

            for rtm_row in rtm_rows:
                result = self._semantic_match(
                    requirement,
                    rtm_row,
                )

                if result["match"]:
                    candidate_rtm = rtm_row
                    match_type = result["match_type"]
                    break

            if candidate_rtm is None:
                gaps.append(
                    {
                        "requirement_id": requirement_id,
                        "gap_type": "NO_RTM_MAPPING",
                        "description": (
                            "Requirement has no corresponding "
                            "RTM entry"
                        ),
                    }
                )
                continue

            rtm_requirement_id = candidate_rtm.get(
                "Requirement_ID"
            )

            testcase_id = candidate_rtm.get(
                "Testcase_ID"
            )

            mapped_rtm_ids.add(rtm_requirement_id)

            testcase = next(
                (
                    item
                    for item in testcases
                    if item.get("testcase_id") == testcase_id
                ),
                None,
            )

            if testcase is None:
                gaps.append(
                    {
                        "requirement_id": requirement_id,
                        "rtm_requirement_id": rtm_requirement_id,
                        "testcase_id": testcase_id,
                        "gap_type": "NO_TESTCASE",
                        "description": (
                            "RTM mapping exists but the "
                            "referenced testcase was not found"
                        ),
                    }
                )
                continue

            mapped_testcase_ids.add(testcase_id)

            trace_record = {
                "requirement_id": requirement_id,
                "rtm_requirement_id": rtm_requirement_id,
                "testcase_id": testcase_id,
                "match_type": match_type,
            }

            if match_type == "SEMANTIC_IDENTIFIER_MISMATCH":
                mismatches.append(
                    {
                        **trace_record,
                        "mismatch_type": (
                            "REQUIREMENT_IDENTIFIER_MISMATCH"
                        ),
                        "description": (
                            "Requirement and RTM appear "
                            "semantically related, but their "
                            "identifiers differ"
                        ),
                        "human_governance_required": True,
                    }
                )

            matched.append(trace_record)

        unmapped_rtm = [
            row.get("Requirement_ID")
            for row in rtm_rows
            if row.get("Requirement_ID")
            not in mapped_rtm_ids
        ]

        unmapped_testcases = [
            testcase.get("testcase_id")
            for testcase in testcases
            if testcase.get("testcase_id")
            not in mapped_testcase_ids
        ]

        total_requirements = len(requirements)

        covered_requirements = len(
            [
                item
                for item in matched
                if item["testcase_id"]
            ]
        )

        coverage_percentage = (
            (
                covered_requirements
                / total_requirements
            )
            * 100
            if total_requirements
            else 0
        )

        return {
            "matched": matched,
            "mismatches": mismatches,
            "gaps": gaps,
            "unmapped_rtm": unmapped_rtm,
            "unmapped_testcases": unmapped_testcases,
            "coverage_summary": {
                "total_requirements": total_requirements,
                "covered_requirements": covered_requirements,
                "coverage_percentage": coverage_percentage,
            },
        }