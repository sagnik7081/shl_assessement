class ScoringEngine:

    # -----------------------------------
    # SKILL OVERLAP
    # -----------------------------------

    def calculate_skill_overlap(
        self,
        assessment,
        constraints
    ):

        skills = constraints.get(
            "skills",
            []
        )

        if not skills:
            return 0

        text = (
            assessment.get("name", "") + " " +
            assessment.get("description", "")
        ).lower()

        matches = 0

        for skill in skills:

            if skill.lower() in text:
                matches += 1

        return matches / max(len(skills), 1)

    # -----------------------------------
    # MAIN SCORING
    # -----------------------------------

    def calculate_score(
        self,
        assessment,
        constraints,
        semantic_score
    ):

        categories = assessment["assessment"].get(
            "keys",
            []
        )

        job_levels = assessment["assessment"].get(
            "job_levels",
            []
        )

        # -----------------------------------
        # CATEGORY SCORE
        # -----------------------------------

        category_score = 0

        if constraints["needs_technical"]:

            if "Knowledge & Skills" in categories:
                category_score += 1

            if "Ability & Aptitude" in categories:
                category_score += 0.5

        if constraints["needs_personality"]:

            if "Personality & Behavior" in categories:
                category_score += 0.5

        category_score = min(
            category_score,
            1
        )

        # -----------------------------------
        # SENIORITY SCORE
        # -----------------------------------

        seniority_score = 0

        seniority = constraints.get(
            "seniority"
        )

        if seniority == "mid":

            if any(
                level in job_levels
                for level in [
                    "Mid-Professional",
                    "Professional Individual Contributor"
                ]
            ):

                seniority_score = 1

        elif seniority == "entry":

            if any(
                level in job_levels
                for level in [
                    "Entry-Level",
                    "Graduate"
                ]
            ):

                seniority_score = 1

        elif seniority == "senior":

            if any(
                level in job_levels
                for level in [
                    "Manager",
                    "Director",
                    "Executive"
                ]
            ):

                seniority_score = 1

        # -----------------------------------
        # SKILL OVERLAP
        # -----------------------------------

        skill_score = self.calculate_skill_overlap(
            assessment["assessment"],
            constraints
        )

        # -----------------------------------
        # FINAL HYBRID SCORE
        # -----------------------------------

        final_score = (
            semantic_score * 0.45
            + skill_score * 0.40
            + seniority_score * 0.10
            + category_score * 0.05
        )

        return round(final_score, 4)