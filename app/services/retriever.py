# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer

# from app.utils.catalog_loader import load_catalog


# class SHLRetriever:

#     def __init__(self):

#         print("Loading catalog...")

#         self.catalog = load_catalog()

#         print("Loading embedding model...")

#         self.model = SentenceTransformer(
#             "BAAI/bge-base-en-v1.5"
#         )

#         self.documents = []
#         self.metadata = []

#         self.build_documents()

#         print("Generating embeddings...")

#         self.embeddings = self.model.encode(
#             self.documents,
#             normalize_embeddings=True,
#             show_progress_bar=True
#         )

#         self.dimension = self.embeddings.shape[1]

#         print("Creating FAISS index...")

#         self.index = faiss.IndexFlatIP(self.dimension)

#         self.index.add(
#             np.array(self.embeddings).astype("float32")
#         )

#         print(f"\nIndexed {len(self.documents)} assessments")

#     # ---------------------------------------------------------
#     # BUILD SEARCHABLE DOCUMENTS
#     # ---------------------------------------------------------

#     def build_documents(self):

#         for item in self.catalog:

#             name = item.get("name", "")
#             description = item.get("description", "")
#             categories = item.get("keys", [])
#             job_levels = item.get("job_levels", [])
#             languages = item.get("languages", [])

#             searchable_text = f"""
#             Assessment Name:
#             {name}

#             Assessment Description:
#             {description}

#             Assessment Categories:
#             {' '.join(categories)}

#             Recommended Job Levels:
#             {' '.join(job_levels)}

#             Supported Languages:
#             {' '.join(languages)}
#             """

#             self.documents.append(searchable_text)

#             self.metadata.append(item)

#     # ---------------------------------------------------------
#     # SEARCH FUNCTION
#     # ---------------------------------------------------------

#     def search(
#         self,
#         query,
#         top_k=10,
#         required_categories=None
#     ):

#         query_embedding = self.model.encode(
#             [query],
#             normalize_embeddings=True
#         )

#         # Retrieve more results for reranking
#         scores, indices = self.index.search(
#             np.array(query_embedding).astype("float32"),
#             top_k * 5
#         )

#         results = []

#         query_lower = query.lower()

#         # ---------------------------------------------------------
#         # IMPORTANT TECHNICAL KEYWORDS
#         # ---------------------------------------------------------

#         technical_query_words = [
#             "java",
#             "spring",
#             "spring boot",
#             "python",
#             "django",
#             "flask",
#             "fastapi",
#             "react",
#             "angular",
#             "javascript",
#             "typescript",
#             "frontend",
#             "backend",
#             "fullstack",
#             "api",
#             "microservices",
#             "docker",
#             "kubernetes",
#             "aws",
#             "azure",
#             "gcp",
#             "cloud",
#             "sql",
#             "mysql",
#             "postgresql",
#             "mongodb",
#             "jenkins",
#             "devops",
#             "machine learning",
#             "ai",
#             "data science"
#         ]

#         important_skills = [
#             skill
#             for skill in technical_query_words
#             if skill in query_lower
#         ]

#         is_technical_query = len(important_skills) > 0

#         # ---------------------------------------------------------
#         # LOOP THROUGH RETRIEVED RESULTS
#         # ---------------------------------------------------------

#         for score, idx in zip(scores[0], indices[0]):

#             item = self.metadata[idx]

#             item_categories = [
#                 category.strip().lower()
#                 for category in item.get("keys", [])
#             ]

#             categories_lower = " ".join(item_categories)

#             # ---------------------------------------------------------
#             # CATEGORY FILTERING
#             # ---------------------------------------------------------

#             if required_categories:

#                 normalized_required = [
#                     category.strip().lower()
#                     for category in required_categories
#                 ]

#                 matched = any(
#                     req in category
#                     for req in normalized_required
#                     for category in item_categories
#                 )

#                 if not matched:
#                     continue

#             # ---------------------------------------------------------
#             # SEARCHABLE TEXT
#             # ---------------------------------------------------------

#             name = item.get("name", "")
#             description = item.get("description", "")

#             name_desc = f"{name} {description}".lower()

#             # ---------------------------------------------------------
#             # SCORING
#             # ---------------------------------------------------------

#             bonus = 0
#             penalty = 0

#             matched_skills = []

#             # ---------------------------------------------------------
#             # EXACT SKILL MATCH BOOST
#             # ---------------------------------------------------------

#             for skill in important_skills:

#                 if skill in name_desc:

#                     matched_skills.append(skill)

#                     # Strong exact tech boost
#                     bonus += 0.35

#             # ---------------------------------------------------------
#             # STACK CONSISTENCY PENALTIES
#             # ---------------------------------------------------------

#             # Python query should not rank Java tests highly
#             if "python" in query_lower:

#                 if any(
#                     word in name_desc
#                     for word in [
#                         "java",
#                         "j2ee",
#                         "java ee"
#                     ]
#                 ):
#                     penalty += 0.35

#             # Frontend query should avoid enterprise backend tests
#             if (
#                 "frontend" in query_lower
#                 or "react" in query_lower
#                 or "angular" in query_lower
#             ):

#                 if any(
#                     word in name_desc
#                     for word in [
#                         "java ee",
#                         "enterprise edition",
#                         "soap",
#                         "web services"
#                     ]
#                 ):
#                     penalty += 0.25

#             # Backend query should not prioritize frontend-only tests
#             if "backend" in query_lower:

#                 if any(
#                     word in name_desc
#                     for word in [
#                         "html",
#                         "css",
#                         "ui/ux"
#                     ]
#                 ):
#                     penalty += 0.20

#             # ---------------------------------------------------------
#             # CATEGORY BOOSTING
#             # ---------------------------------------------------------

#             if is_technical_query:

#                 # Boost technical assessments
#                 if (
#                     "knowledge & skills" in categories_lower
#                     or "simulations" in categories_lower
#                     or "technical" in categories_lower
#                 ):
#                     bonus += 0.35

#                 # Penalize personality assessments
#                 if (
#                     "personality & behavior" in categories_lower
#                     or "personality" in categories_lower
#                     or "behavior" in categories_lower
#                     or "competencies" in categories_lower
#                 ):
#                     penalty += 0.25

#             # ---------------------------------------------------------
#             # FINAL SCORE
#             # ---------------------------------------------------------

#             final_score = float(score) + bonus - penalty

#             results.append({
#                 "score": round(final_score, 4),
#                 "matched_skills": matched_skills,
#                 "assessment": item
#             })

#         # ---------------------------------------------------------
#         # SORT RESULTS
#         # ---------------------------------------------------------

#         results = sorted(
#             results,
#             key=lambda x: x["score"],
#             reverse=True
#         )

#         # ---------------------------------------------------------
#         # RETURN TOP RESULTS
#         # ---------------------------------------------------------

#         return results[:top_k]


from app.utils.catalog_loader import load_catalog


class SHLRetriever:

    def __init__(self):

        print("Loading catalog...")

        self.catalog = load_catalog()

    # ---------------------------------------------------------
    # SEARCH FUNCTION
    # ---------------------------------------------------------

    def search(
        self,
        query,
        top_k=10,
        required_categories=None
    ):

        query_lower = query.lower()

        results = []

        # ---------------------------------------------------------
        # IMPORTANT TECHNICAL KEYWORDS
        # ---------------------------------------------------------

        technical_query_words = [
            "java",
            "spring",
            "spring boot",
            "python",
            "django",
            "flask",
            "fastapi",
            "react",
            "angular",
            "javascript",
            "typescript",
            "frontend",
            "backend",
            "fullstack",
            "api",
            "microservices",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "cloud",
            "sql",
            "mysql",
            "postgresql",
            "mongodb",
            "jenkins",
            "devops",
            "machine learning",
            "ai",
            "data science"
        ]

        important_skills = [
            skill
            for skill in technical_query_words
            if skill in query_lower
        ]

        is_technical_query = len(important_skills) > 0

        # ---------------------------------------------------------
        # LOOP THROUGH CATALOG
        # ---------------------------------------------------------

        for item in self.catalog:

            item_categories = [
                category.strip().lower()
                for category in item.get("keys", [])
            ]

            categories_lower = " ".join(item_categories)

            # ---------------------------------------------------------
            # CATEGORY FILTERING
            # ---------------------------------------------------------

            if required_categories:

                normalized_required = [
                    category.strip().lower()
                    for category in required_categories
                ]

                matched = any(
                    req in category
                    for req in normalized_required
                    for category in item_categories
                )

                if not matched:
                    continue

            # ---------------------------------------------------------
            # SEARCHABLE TEXT
            # ---------------------------------------------------------

            name = item.get("name", "")
            description = item.get("description", "")

            searchable_text = f"""
            {name}
            {description}
            {' '.join(item.get('keys', []))}
            {' '.join(item.get('job_levels', []))}
            {' '.join(item.get('languages', []))}
            """.lower()

            # ---------------------------------------------------------
            # BASE KEYWORD SCORE
            # ---------------------------------------------------------

            base_score = 0

            for token in query_lower.split():

                if token in searchable_text:
                    base_score += 0.2

            # ---------------------------------------------------------
            # SCORING
            # ---------------------------------------------------------

            bonus = 0
            penalty = 0

            matched_skills = []

            # ---------------------------------------------------------
            # EXACT SKILL MATCH BOOST
            # ---------------------------------------------------------

            # ---------------------------------------------------------
            # EXACT SKILL MATCH BOOST
            # ---------------------------------------------------------

            for skill in important_skills:

                if skill in searchable_text:

                    matched_skills.append(skill)

                    # Strong framework/library boost
                    if skill in [
                        "spring",
                        "spring boot",
                        "react",
                        "angular",
                        "django",
                        "flask",
                        "fastapi"
                    ]:
                        bonus += 0.60

                    # Normal tech boost
                    else:
                        bonus += 0.35
            # ---------------------------------------------------------
            # STACK CONSISTENCY PENALTIES
            # ---------------------------------------------------------

            if "python" in query_lower:

                if any(
                    word in searchable_text
                    for word in [
                        "java",
                        "j2ee",
                        "java ee"
                    ]
                ):
                    penalty += 0.35

            if (
                "frontend" in query_lower
                or "react" in query_lower
                or "angular" in query_lower
            ):

                if any(
                    word in searchable_text
                    for word in [
                        "java ee",
                        "enterprise edition",
                        "soap",
                        "web services"
                    ]
                ):
                    penalty += 0.25

            if "backend" in query_lower:

                if any(
                    word in searchable_text
                    for word in [
                        "html",
                        "css",
                        "ui/ux"
                    ]
                ):
                    penalty += 0.20


            # Java query should avoid .NET assessments

            if "java" in query_lower:

                if any(
                    word in searchable_text
                    for word in [
                        ".net",
                        "asp.net",
                        "c#"
                    ]
                ):
                    penalty += 0.40

            # ---------------------------------------------------------
            # CATEGORY BOOSTING
            # ---------------------------------------------------------

            if is_technical_query:

                if (
                    "knowledge & skills" in categories_lower
                    or "simulations" in categories_lower
                    or "technical" in categories_lower
                ):
                    bonus += 0.35

                if (
                    "personality & behavior" in categories_lower
                    or "personality" in categories_lower
                    or "behavior" in categories_lower
                    or "competencies" in categories_lower
                ):
                    penalty += 0.25

            # ---------------------------------------------------------
            # FINAL SCORE
            # ---------------------------------------------------------

            final_score = base_score + bonus - penalty

            if final_score > 0:

                results.append({
                    "score": round(final_score, 4),
                    "matched_skills": matched_skills,
                    "assessment": item
                })

        # ---------------------------------------------------------
        # SORT RESULTS
        # ---------------------------------------------------------

        results = sorted(
            results,
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:top_k]