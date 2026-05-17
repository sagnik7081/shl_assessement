from app.services.constraint_extractor import ConstraintExtractor


class ConversationAnalyzer:

    def __init__(self):

        self.extractor = ConstraintExtractor()

    def analyze(self, messages):

        combined_user_text = []

        # -----------------------------------
        # COMBINE USER MESSAGES
        # -----------------------------------

        for message in messages:

            if message["role"] == "user":

                combined_user_text.append(
                    message["content"]
                )

        full_context = " ".join(combined_user_text)

        # -----------------------------------
        # EXTRACT CONSTRAINTS
        # -----------------------------------

        constraints = self.extractor.extract(
            full_context
        )

        return {
            "full_context": full_context,
            "constraints": constraints
        }


if __name__ == "__main__":

    analyzer = ConversationAnalyzer()

    messages = [

        {
            "role": "user",
            "content": "Hiring a Java backend developer"
        },

        {
            "role": "assistant",
            "content": "What seniority level?"
        },

        {
            "role": "user",
            "content": "Mid-level and needs stakeholder communication"
        }
    ]

    result = analyzer.analyze(messages)

    print("\nConversation Analysis:\n")

    print(result)