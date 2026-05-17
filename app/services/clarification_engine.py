class ClarificationEngine:

    def generate_questions(self, constraints):

        questions = []

        # -----------------------------------
        # ROLE / TECHNICAL SKILLS
        # -----------------------------------

        if not constraints["technical_skills"]:

            questions.append(
                "What role are you hiring for?"
            )

        # -----------------------------------
        # SENIORITY
        # -----------------------------------

        if not constraints["seniority"]:

            questions.append(
                "What seniority level is required?"
            )

        # -----------------------------------
        # PERSONALITY
        # -----------------------------------

        if not constraints["behavioral_traits"]:

            questions.append(
                "Does the role require stakeholder communication or teamwork?"
            )

        return questions


if __name__ == "__main__":

    engine = ClarificationEngine()

    constraints = {
        "seniority": None,
        "technical_skills": [],
        "behavioral_traits": [],
        "needs_personality": False,
        "needs_technical": False
    }

    questions = engine.generate_questions(
        constraints
    )

    print("\nClarification Questions:\n")

    for question in questions:

        print("-", question)