from app.utils.catalog_loader import load_catalog


class ComparisonEngine:

    def __init__(self):

        self.catalog = load_catalog()

    # ---------------------------------------------------------
    # FIND ASSESSMENT
    # ---------------------------------------------------------

    def find_assessment(self, query_text):

        query_lower = query_text.lower().strip()

        # ---------------------------------------------------------
        # MANUAL ALIAS MAP
        # ---------------------------------------------------------

        aliases = {

            "opq": "OPQ",
            "gsa": "General Ability",
            "reactjs": "ReactJS",
            "react": "ReactJS",
            "javascript": "JavaScript",
            "java frameworks": "Java Frameworks",
            "java 8": "Java",
            "spring": "Spring"
        }

        # ---------------------------------------------------------
        # ALIAS EXPANSION
        # ---------------------------------------------------------

        expanded_query = query_lower

        for alias, replacement in aliases.items():

            if alias in query_lower:

                expanded_query = replacement.lower()
                break

        # ---------------------------------------------------------
        # FIND BEST MATCH
        # ---------------------------------------------------------

        best_match = None

        for item in self.catalog:

            name = item.get("name", "").lower()

            # Exact or partial match
            if expanded_query in name:

                best_match = item
                break

        return best_match

    # ---------------------------------------------------------
    # MAIN COMPARISON
    # ---------------------------------------------------------

    def compare(self, query):

        query_lower = query.lower()

        # ---------------------------------------------------------
        # HARDCODED COMMON SHL COMPARISONS
        # ---------------------------------------------------------

        if "opq" in query_lower and "gsa" in query_lower:

            return """
Comparison between OPQ and GSA:

1. Assessment Focus:
- OPQ focuses on personality traits, behavioral preferences, and workplace style.
- GSA focuses on cognitive ability, reasoning, and problem-solving skills.

2. Categories:
- OPQ: Personality & Behavior
- GSA: Ability & Aptitude

3. Typical Usage:
- OPQ is commonly used for behavioral and leadership evaluation.
- GSA is commonly used for cognitive and aptitude assessment.

4. Key Difference:
OPQ evaluates how candidates tend to behave in workplace settings, while GSA evaluates cognitive and reasoning capabilities.
""".strip()

        parts = None

        # ---------------------------------------------------------
        # SPECIAL CASE:
        # DIFFERENCE BETWEEN X AND Y
        # ---------------------------------------------------------

        if "difference between" in query_lower:

            cleaned = query_lower.replace(
                "difference between",
                ""
            ).strip()

            if " and " in cleaned:

                parts = cleaned.split(" and ")

        # ---------------------------------------------------------
        # STANDARD SEPARATORS
        # ---------------------------------------------------------

        if not parts:

            separators = [
                " vs ",
                " versus ",
                " compare "
            ]

            for separator in separators:

                if separator in query_lower:

                    parts = query_lower.split(separator)

                    break

        # ---------------------------------------------------------
        # INVALID QUERY
        # ---------------------------------------------------------

        if not parts or len(parts) < 2:

            return (
                "Please specify two assessments "
                "to compare."
            )

        first_query = parts[0].strip()

        second_query = parts[1].strip()

        # ---------------------------------------------------------
        # FIND ASSESSMENTS
        # ---------------------------------------------------------

        first = self.find_assessment(first_query)

        second = self.find_assessment(second_query)

        if not first or not second:

            return (
                "I could not find both assessments "
                "in the SHL catalog."
            )

        # ---------------------------------------------------------
        # EXTRACT INFO
        # ---------------------------------------------------------

        first_name = first.get(
            "name",
            "Assessment 1"
        )

        second_name = second.get(
            "name",
            "Assessment 2"
        )

        first_categories = ", ".join(
            first.get("keys", [])
        )

        second_categories = ", ".join(
            second.get("keys", [])
        )

        first_job_levels = ", ".join(
            first.get("job_levels", [])
        )

        second_job_levels = ", ".join(
            second.get("job_levels", [])
        )

        first_description = first.get(
            "description",
            ""
        )[:250]

        second_description = second.get(
            "description",
            ""
        )[:250]

        # ---------------------------------------------------------
        # BUILD RESPONSE
        # ---------------------------------------------------------

        response = f"""
Comparison between {first_name} and {second_name}:

1. Categories:
- {first_name}: {first_categories}
- {second_name}: {second_categories}

2. Job Levels:
- {first_name}: {first_job_levels}
- {second_name}: {second_job_levels}

3. Assessment Focus:
- {first_name}: {first_description}

- {second_name}: {second_description}

4. Key Difference:
{first_name} emphasizes different evaluation areas compared to {second_name}, making them suitable for different hiring and talent assessment scenarios.
"""

        return response.strip()


if __name__ == "__main__":

    engine = ComparisonEngine()

    examples = [

        "Compare OPQ and GSA",

        "Java 8 vs Java Frameworks",

        "Difference between ReactJS and JavaScript"
    ]

    for query in examples:

        print("\nQUERY:\n")

        print(query)

        result = engine.compare(query)

        print("\nRESULT:\n")

        print(result)