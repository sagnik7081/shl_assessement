class ConversationMemory:

    def __init__(self):
        self.sessions = {}

    def get_context(self, session_id):
        return self.sessions.get(session_id, {})

    def update_context(self, session_id, new_data):

        if session_id not in self.sessions:
            self.sessions[session_id] = {}

        self.sessions[session_id].update(new_data)

    def clear_context(self, session_id):

        if session_id in self.sessions:
            del self.sessions[session_id]