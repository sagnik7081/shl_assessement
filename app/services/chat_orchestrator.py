from app.services.intent_classifier import IntentClassifier
from app.services.conversation_analyzer import ConversationAnalyzer
from app.services.clarification_engine import ClarificationEngine
from app.services.recommendation import RecommendationEngine
from app.services.comparison_engine import ComparisonEngine
from app.core.services import recommendation_engine
from app.services.domain_detector import DomainDetector
from app.services.llm_response_generator import LLMResponseGenerator
from app.services.conversation_memory import ConversationMemory


class ChatOrchestrator:

    def __init__(self, recommendation_engine):

        self.intent_classifier = IntentClassifier()

        self.conversation_analyzer = ConversationAnalyzer()

        self.clarification_engine = ClarificationEngine()

        self.recommendation_engine = recommendation_engine

        self.comparison_engine = ComparisonEngine()

        self.domain_detector = DomainDetector()

        self.llm_generator = LLMResponseGenerator()

        self.memory = ConversationMemory()

    def handle_chat(self, messages, session_id="default"):

        # -----------------------------------
        # LOAD MEMORY
        # -----------------------------------

        stored_context = self.memory.get_context(session_id)

        # -----------------------------------
        # DETECT INTENT
        # -----------------------------------

        intent = self.intent_classifier.classify(
            messages
        )

        # -----------------------------------
        # ANALYZE CURRENT MESSAGE
        # -----------------------------------

        analysis = self.conversation_analyzer.analyze(
            messages
        )

        constraints = analysis["constraints"]

        # -----------------------------------
        # BUILD COMBINED CONTEXT
        # -----------------------------------

        combined_context = analysis["full_context"]

        if stored_context.get("full_context"):

            combined_context = (
                stored_context["full_context"]
                + " "
                + analysis["full_context"]
            )

            stored_context.update(constraints)

            constraints = stored_context

        # -----------------------------------
        # DOMAIN DETECTION
        # IMPORTANT FIX:
        # Use combined_context instead of
        # only current message
        # -----------------------------------

        if not self.domain_detector.is_shl_related(
            combined_context
        ):

            return {
                "reply": (
                    "I can only assist with SHL assessment "
                    "recommendations and hiring-related queries."
                ),
                "recommendations": [],
                "end_of_conversation": False
            }

        # -----------------------------------
        # SAVE MEMORY
        # -----------------------------------

        memory_payload = {
            **constraints,
            "full_context": combined_context
        }

        self.memory.update_context(
            session_id,
            memory_payload
        )

        # -----------------------------------
        # CLARIFICATION FLOW
        # -----------------------------------

        if intent == "clarification":

            questions = []

            if "seniority" not in constraints:
                questions.append(
                    "What seniority level are you hiring for?"
                )

            if "skills" not in constraints:
                questions.append(
                    "What technical skills are required?"
                )

            if "behavioral" not in constraints:
                questions.append(
                    "Any behavioral or communication skills needed?"
                )

            return {
                "intent": intent,
                "reply": " ".join(questions),
                "recommendations": [],
                "end_of_conversation": False
            }

        # -----------------------------------
        # COMPARISON FLOW
        # -----------------------------------

        if intent == "comparison":

            comparison = self.comparison_engine.compare(
                combined_context
            )

            return {
                "intent": intent,
                "reply": comparison,
                "recommendations": [],
                "end_of_conversation": False
            }

        # -----------------------------------
        # RECOMMENDATION FLOW
        # IMPORTANT FIX:
        # Use combined_context
        # -----------------------------------

        recommendations = self.recommendation_engine.recommend(
            query=combined_context,
            constraints=constraints,
            top_k=5
        )

        reply = self.llm_generator.generate_recommendation_response(
            query=combined_context,
            recommendations=recommendations
        )

        return {
            "intent": intent,
            "reply": reply,
            "recommendations": recommendations,
            "end_of_conversation": False
        }


if __name__ == "__main__":

    orchestrator = ChatOrchestrator(
        recommendation_engine
    )

    messages = [

        {
            "role": "user",
            "content": (
                "Hiring a mid-level Java backend "
                "developer with stakeholder communication."
            )
        }
    ]

    response = orchestrator.handle_chat(
        messages
    )

    print("\nORCHESTRATOR RESPONSE:\n")

    print(response)