from app.services.retriever import SHLRetriever
from app.services.reranker import Reranker
from app.services.scoring_engine import ScoringEngine


class RecommendationEngine:

    def __init__(self):

        self.retriever = SHLRetriever()
        self.reranker = Reranker()
        self.scoring_engine = ScoringEngine()

    # -----------------------------------
    # FILTER IRRELEVANT RESULTS
    # -----------------------------------

    def filter_irrelevant_results(
        self,
        results,
        is_technical_role
    ):

        if not is_technical_role:
            return results

        filtered = []

        blacklist = [
            "retail",
            "customer service",
            "contact center",
            "sales",
            "bpo"
        ]

        for item in results:

            name = item["assessment"]["name"].lower()

            if any(word in name for word in blacklist):
                continue

            filtered.append(item)

        return filtered

    # -----------------------------------
    # MAIN RECOMMENDATION LOGIC
    # -----------------------------------

    def recommend(
        self,
        query,
        constraints,
        top_k=5
    ):

        recommendations = []

        seen = set()

        # -----------------------------------
        # DETECT TECHNICAL ROLE
        # -----------------------------------

        TECH_ROLE_KEYWORDS = [
            "java",
            "spring",
            "spring boot",
            "backend",
            "developer",
            "software",
            "engineer",
            "programming",
            "coding",
            "api",
            "microservices",
            "python",
            "react",
            "frontend",
            "aws",
            "sql",
            "cloud"
        ]

        query_lower = query.lower()

        is_technical_role = any(
            keyword in query_lower
            for keyword in TECH_ROLE_KEYWORDS
        )

        # -----------------------------------
        # BUILD TARGETED QUERIES
        # -----------------------------------

        technical_query = f"""
        Software engineering assessment for
        {' '.join(constraints.get('technical_skills', []))}
        developer hiring.

        Evaluate:
        backend programming,
        software engineering,
        coding skills,
        technical proficiency,
        problem solving,
        APIs,
        system development,
        application development,
        Spring Boot backend development,
        Java engineering
        """

        behavioral_query = " ".join(
            constraints.get("behavioral_traits", [])
        )

        # -----------------------------------
        # TECHNICAL RETRIEVAL
        # -----------------------------------

        technical_results = []

        if constraints.get("needs_technical"):

            technical_results = self.retriever.search(
                query=technical_query,
                top_k=8,
                required_categories=[
                    "Knowledge & Skills"
                ]
            )

        technical_results = self.filter_irrelevant_results(
            technical_results,
            is_technical_role
        )

        # -----------------------------------
        # SKILL OVERLAP FILTERING
        # -----------------------------------

        technical_results = self.filter_by_skill_overlap(
            technical_results,
            constraints.get("skills", [])
        )

        # -----------------------------------
        # HARD FILTER NON-DEVELOPER RESULTS
        # -----------------------------------

        bad_keywords = [
            "retail",
            "customer",
            "contact center",
            "sales",
            "support",
            "bpo",
            "call center",
            "readiness"
        ]

        filtered_results = []

        for item in technical_results:

            name = item["assessment"]["name"].lower()

            if any(
                bad in name
                for bad in bad_keywords
            ):
                continue

            filtered_results.append(item)

        technical_results = filtered_results

        # -----------------------------------
        # TECHNICAL BOOSTING
        # -----------------------------------

        for item in technical_results:

            name = item["assessment"]["name"].lower()

            tech_bonus_keywords = [
                "java",
                "developer",
                "programming",
                "software",
                "backend",
                "coding",
                "technical",
                "engineer"
            ]

            keyword_bonus = any(
                keyword in name
                for keyword in tech_bonus_keywords
            )

            if is_technical_role:

                if keyword_bonus:
                    item["score"] *= 2.2
                else:
                    item["score"] *= 1.5

            else:
                item["score"] *= 1.35

        # -----------------------------------
        # COMPETENCY RETRIEVAL
        # -----------------------------------

        competency_results = self.retriever.search(
            query=query,
            top_k=5,
            required_categories=[
                "Competencies"
            ]
        )

        competency_results = self.filter_irrelevant_results(
            competency_results,
            is_technical_role
        )

        # Reduce competency dominance
        for item in competency_results:
            item["score"] *= 0.9

        # -----------------------------------
        # PERSONALITY RETRIEVAL
        # -----------------------------------

        personality_results = []

        if constraints.get("needs_personality"):

            personality_results = self.retriever.search(
                query=behavioral_query,
                top_k=3,
                required_categories=[
                    "Personality & Behavior"
                ]
            )

            personality_results = self.reranker.rerank(
                personality_results,
                behavioral_traits=constraints.get(
                    "behavioral_traits",
                    []
                )
            )

            personality_results = self.filter_irrelevant_results(
                personality_results,
                is_technical_role
            )

            # Slightly lower weight
            for item in personality_results:
                item["score"] *= 0.95

        # -----------------------------------
        # CONTROLLED RECOMMENDATION COMPOSITION
        # -----------------------------------

        final_results = []

        if is_technical_role:

            # PRIORITIZE TECHNICAL RESULTS
            final_results.extend(
                technical_results[:5]
            )

            # ONLY ADD COMPETENCY IF
            # TECHNICAL RESULTS ARE EMPTY
            if not technical_results:

                final_results.extend(
                    competency_results[:1]
                )

            # ADD LIMITED PERSONALITY
            final_results.extend(
                personality_results[:1]
            )

        else:

            final_results.extend(
                technical_results[:2]
            )

            final_results.extend(
                competency_results[:2]
            )

            final_results.extend(
                personality_results[:1]
            )
        # -----------------------------------
        # BUSINESS-AWARE RERANKING
        # -----------------------------------

        final_results = self.rerank_results(
            final_results,
            constraints
        )

        # -----------------------------------
        # DEDUPLICATION
        # -----------------------------------

        for item in final_results:

            assessment = item["assessment"]

            name = assessment["name"]

            if name in seen:
                continue

            recommendations.append({
                "name": name,
                "url": assessment["link"],
                "score": round(
                    item["final_score"],
                    4
                ),
                "reason": self.generate_reason(
                    assessment,
                    constraints
                ),
                "categories": assessment.get(
                    "keys",
                    []
                )
            })

            seen.add(name)

            if len(recommendations) >= top_k:
                break

        return recommendations


    # -----------------------------------
    # FILTER BY SKILL OVERLAP
    # -----------------------------------

    def filter_by_skill_overlap(
        self,
        assessments,
        skills
    ):

        if not skills:
            return assessments

        scored = []

        for item in assessments:

            assessment = item["assessment"]

            searchable_text = (
                assessment.get("name", "") + " " +
                assessment.get("description", "")
            ).lower()

            overlap = 0

            matched_skills = []

            for skill in skills:

                if skill.lower() in searchable_text:

                    overlap += 1

                    matched_skills.append(skill)

            item["skill_overlap"] = overlap

            item["matched_skills"] = matched_skills

            scored.append(item)

        scored.sort(
            key=lambda x: x["skill_overlap"],
            reverse=True
        )

        return scored

     # -----------------------------------
    # GENERATE EXPLANATION
    # -----------------------------------

    def generate_reason(
        self,
        assessment,
        constraints
    ):

        categories = assessment.get(
            "keys",
            []
        )

        reasons = []

        searchable_text = (
            assessment.get("name", "") + " " +
            assessment.get("description", "")
        ).lower()

        matched_skills = []

        for skill in constraints.get("skills", []):

            if skill.lower() in searchable_text:

                matched_skills.append(skill)

        if matched_skills:

            reasons.append(
                "matches skills: " +
                ", ".join(matched_skills)
            )

        if "Knowledge & Skills" in categories:

            reasons.append(
                "evaluates technical proficiency"
            )

        if "Personality & Behavior" in categories:

            reasons.append(
                "evaluates communication and collaboration"
            )

        if "Competencies" in categories:

            reasons.append(
                "assesses workplace competencies"
            )

        if constraints.get("seniority"):

            reasons.append(
                f"fits {constraints['seniority']} level hiring"
            )

        return ", ".join(reasons)
    # -----------------------------------
    # FINAL RERANKING
    # -----------------------------------

    def rerank_results(
        self,
        results,
        constraints
    ):

        reranked = []

        for result in results:

            final_score = self.scoring_engine.calculate_score(
                assessment=result,
                constraints=constraints,
                semantic_score=result["score"]
            )

            result["final_score"] = final_score

            reranked.append(result)

        reranked.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return reranked


if __name__ == "__main__":

    from app.services.constraint_extractor import (
        ConstraintExtractor
    )

    extractor = ConstraintExtractor()

    engine = RecommendationEngine()

    query = """
    Hiring a mid-level Java backend developer
    with stakeholder communication.
    Need technical + communication assessment.
    """

    constraints = extractor.extract(query)

    print("\nExtracted Constraints:\n")

    for k, v in constraints.items():
        print(f"{k}: {v}")

    results = engine.recommend(
        query=query,
        constraints=constraints,
        top_k=5
    )

    print("\nRecommendations:\n")

    for i, item in enumerate(results, 1):

        print(f"{i}. {item['name']}")

        print(f"Score: {item['score']}")

        print(f"URL: {item['url']}")

        print(f"Categories: {item['categories']}")

        print()