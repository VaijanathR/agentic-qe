import json
from pathlib import Path


class TestDataResolver:
    """
    Deterministically resolves approved test-data IDs from
    testdata/testdata.json.

    Responsibilities:
    - Load approved test-data baseline.
    - Resolve a testcase's test_data_ids.
    - Return matching approved data.
    - Never invent test data.
    - Never modify the approved baseline.
    """
    __test__ = False
    
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)

    def _load_testdata(self):
        testdata_file = self.project_root / "testdata" / "testdata.json"

        with testdata_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _index_data(self, data):
        index = {}

        for section_name, section_data in data.items():
            if not isinstance(section_data, list):
                continue

            for item in section_data:
                if not isinstance(item, dict):
                    continue

                data_id = item.get("data_id")

                if data_id:
                    index[data_id] = {
                        "data_id": data_id,
                        "section": section_name,
                        "data": item,
                    }

                variations = item.get("variations", [])

                if isinstance(variations, list):
                    for variation in variations:
                        if not isinstance(variation, dict):
                            continue

                        variation_id = variation.get("variation_id")

                        if variation_id:
                            index[variation_id] = {
                                "data_id": variation_id,
                                "parent_data_id": data_id,
                                "section": section_name,
                                "data": variation,
                            }

        return index

    def resolve(self, data_ids):
        """
        Resolve one or more approved test-data IDs.

        Returns:
            list of resolved approved test-data records.

        Raises:
            ValueError when an ID cannot be resolved.
        """

        if isinstance(data_ids, str):
            data_ids = [data_ids]

        if not data_ids:
            return []

        baseline = self._load_testdata()
        index = self._index_data(baseline)

        resolved = []

        for data_id in data_ids:
            key = str(data_id).strip()

            if key not in index:
                raise ValueError(
                    f"Approved test data not found: {key}"
                )

            resolved.append(index[key])

        return resolved