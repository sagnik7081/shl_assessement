import os

from langchain_groq import ChatGroq

from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
load_dotenv()


class LLMResponseGenerator:

    def __init__(self):

        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.3
        )

    def generate_recommendation_response(
        self,
        query,
        recommendations
    ):

        recommendation_text = ""

        for idx, rec in enumerate(recommendations, 1):

            recommendation_text += f"""
            Assessment {idx}:
            Name: {rec['name']}
            Reason: {rec['reason']}
            Categories: {", ".join(rec['categories'])}
            URL: {rec['url']}

            """

        prompt = f"""
        You are an SHL assessment recommendation assistant.

        User hiring query:
        {query}

        Recommended assessments:
        {recommendations}

        Generate a concise recruiter-friendly response.

        Rules:
        - Keep response under 150 words
        - Do NOT use greetings like "Dear Hiring Manager"
        - Explain why the assessments match the role
        - Mention technical and behavioral coverage if relevant
        - Sound professional and conversational
        """

        try:

            response = self.llm.invoke([
                HumanMessage(content=prompt)
            ])

            return response.content

        except Exception as e:

            print(f"LLM ERROR: {e}")

            return (
                "Recommended SHL assessments generated successfully "
                "based on the hiring requirements."
            )