class Reranker:

    def __init__(self):

        self.behavioral_boost_terms = [
            "communication",
            "stakeholder",
            "collaboration",
            "teamwork",
            "leadership",
            "client"
        ]

    def rerank(
        self,
        results,
        behavioral_traits=None
    ):

        if behavioral_traits is None:
            behavioral_traits = []

        reranked = []

        for item in results:

            assessment = item["assessment"]

            score = item["score"]

            text = f"""
            {assessment.get('name', '')}
            {assessment.get('description', '')}
            {' '.join(assessment.get('keys', []))}
            """.lower()

            # -----------------------------------
            # BEHAVIORAL TERM BOOSTING
            # -----------------------------------

            for trait in behavioral_traits:

                if trait.lower() in text:
                    score += 0.08

            # -----------------------------------
            # EXTRA BOOST TERMS
            # -----------------------------------

            for keyword in self.behavioral_boost_terms:

                if keyword in text:
                    score += 0.03

            reranked.append({
                "score": score,
                "assessment": assessment
            })

        reranked = sorted(
            reranked,
            key=lambda x: x["score"],
            reverse=True
        )

        return reranked