
# Fallback Chat System
class FallbackChatSystem:
    def __init__(self):
        self.responses = {
            "hello": "Hello! Welcome to Creditor Academy! How can I help you today?",
            "hi": "Hi there! I'm here to assist with Creditor Academy questions.",
            "what is creditor academy": "Creditor Academy is a sovereignty education platform teaching private operation and financial freedom.",
            "how do i cancel": "To cancel your membership, please email support@creditoracademy.com or visit your account settings.",
            "default": "I'm here to help with Creditor Academy questions. Please ask me something specific!"
        }

    def get_response(self, message):
        message_lower = message.lower().strip()
        for key, response in self.responses.items():
            if key in message_lower:
                return response
        return self.responses["default"]

fallback_system = FallbackChatSystem()
