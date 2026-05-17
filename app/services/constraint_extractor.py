import re


class ConstraintExtractor:

    def __init__(self):

        self.seniority_levels = [
            "entry",
            "junior",
            "mid",
            "mid-level",
            "senior",
            "lead",
            "manager"
        ]

        self.personality_keyword_map = {

            "communication": [
                "communication",
                "interpersonal",
                "presentation",
                "verbal"
            ],

            "stakeholder": [
                "stakeholder",
                "client-facing",
                "collaboration",
                "consulting"
            ],

            "leadership": [
                "leadership",
                "management",
                "decision-making",
                "influence"
            ],

            "teamwork": [
                "teamwork",
                "collaboration",
                "team player"
            ]
        }

        # -----------------------------------
        # TECHNICAL SKILLS
        # -----------------------------------

        self.technical_keywords = [
            "java",
            "spring",
            "spring boot",
            "hibernate",
            "backend",
            "frontend",
            "developer",
            "engineer",
            "api",
            "web services",
            "microservices",
            "sql",
            "python",
            "react",
            "aws",
            "docker",
            "kubernetes",
            "cloud",
            "jenkins"
        ]

    # -----------------------------------
    # SKILL EXTRACTION
    # -----------------------------------

    def extract_skills(self, text):

        text = text.lower()

        found = []

        for skill in self.technical_keywords:

            if skill in text:
                found.append(skill)

        return list(set(found))

    # -----------------------------------
    # MAIN EXTRACTION
    # -----------------------------------

    def extract(self, text):

        text_lower = text.lower()

        constraints = {
            "seniority": None,
            "technical_skills": [],
            "behavioral_traits": [],
            "skills": [],
            "needs_personality": False,
            "needs_technical": False
        }

        # -----------------------------------
        # SENIORITY
        # -----------------------------------

        for level in self.seniority_levels:

            if level in text_lower:
                constraints["seniority"] = level
                break

        # -----------------------------------
        # TECHNICAL SKILLS
        # -----------------------------------

        extracted_skills = self.extract_skills(
            text_lower
        )

        constraints["skills"] = extracted_skills

        constraints["technical_skills"] = extracted_skills

        if extracted_skills:
            constraints["needs_technical"] = True

        # -----------------------------------
        # BEHAVIORAL TRAITS
        # -----------------------------------

        for trigger, expanded_terms in self.personality_keyword_map.items():

            if trigger in text_lower:

                constraints["behavioral_traits"].extend(
                    expanded_terms
                )

                constraints["needs_personality"] = True

        return constraints


if __name__ == "__main__":

    extractor = ConstraintExtractor()

    query = """
    Hiring a mid-level Java backend developer
    with stakeholder communication.
    Need technical + communication assessment.
    """

    constraints = extractor.extract(query)

    print("\nExtracted Constraints:\n")

    for key, value in constraints.items():

        print(f"{key}: {value}")