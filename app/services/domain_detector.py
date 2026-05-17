class DomainDetector:

    def is_shl_related(self, text):

        text = text.lower()

        hiring_keywords = [

            # General Hiring
            "hiring",
            "assessment",
            "test",
            "candidate",
            "developer",
            "engineer",
            "manager",
            "role",
            "job",
            "evaluation",

            # Behavioral
            "personality",
            "skills",
            "communication",
            "leadership",
            "stakeholder",
            "teamwork",

            # Technical
            "backend",
            "frontend",
            "technical",
            "java",
            "python",
            "react",
            "reactjs",
            "angular",
            "javascript",
            "spring",
            "spring boot",
            "api",
            "cloud",
            "aws",

            # SHL Assessments
            "opq",
            "gsa",
            "hipo",
            "pjm"
        ]

        return any(
            keyword in text
            for keyword in hiring_keywords
        )