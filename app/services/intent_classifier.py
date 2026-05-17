class IntentClassifier:

    def classify(self, messages):

        latest_message = messages[-1]["content"].lower()

        # -----------------------------------
        # COMPARISON
        # -----------------------------------

        comparison_keywords = [
            "difference",
            "compare",
            "vs",
            "versus"
        ]

        if any(
            keyword in latest_message
            for keyword in comparison_keywords
        ):

            return "comparison"

        # -----------------------------------
        # REFINEMENT
        # -----------------------------------

        refinement_keywords = [
            "add",
            "remove",
            "include",
            "instead",
            "also",
            "change"
        ]

        if any(
            keyword in latest_message
            for keyword in refinement_keywords
        ):

            return "refinement"

        # -----------------------------------
        # CLARIFICATION
        # -----------------------------------

        clarification_keywords = [
            "developer",
            "engineer",
            "manager",
            "analyst",
            "designer",
            "hiring"
        ]

        has_seniority = any(
            level in latest_message
            for level in [
                "junior",
                "mid",
                "mid-level",
                "senior",
                "lead"
            ]
        )

        has_skills = any(
            skill in latest_message
            for skill in [
                "java",
                "python",
                "react",
                "spring",
                "spring boot",
                "aws",
                "sql",
                "backend",
                "frontend",
                "node",
                "microservices",
                "docker",
                "kubernetes",
                "api",
                "rest",
                "devops",
                "cloud",
                "angular",
                "flask",
                "fastapi"
            ]
        )

        if (
            any(
                keyword in latest_message
                for keyword in clarification_keywords
            )
            and (
                not has_seniority
                or not has_skills
            )
        ):

            return "clarification"

        # -----------------------------------
        # DEFAULT
        # -----------------------------------

        return "recommendation"


if __name__ == "__main__":

    classifier = IntentClassifier()

    examples = [

        [{"content": "I need an assessment"}],

        [{"content": "Compare OPQ and GSA"}],

        [{"content": "Add personality tests"}],

        [{"content": "Hiring a Java developer with backend experience"}]
    ]

    for example in examples:

        intent = classifier.classify(example)

        print(f"\nMessage: {example[-1]['content']}")

        print(f"Intent: {intent}")