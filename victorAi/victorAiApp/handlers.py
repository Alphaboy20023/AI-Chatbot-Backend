import random
import math
import re

PROMPTS = {
    "what are you": "I am Victor's first Artificial Intelligence, V1",
    "built you": "Akinola Victor is the visionary behind VictorAi, launching its first version, V1, to assist and interact intelligently.",
    "founder": "Do you want to know the founder of something?",
    "okay": "Glad to meet you too! See you soon 👋",
    "akinola victor": "Akinola Victor is the visionary behind VictorAi, launching its first version, V1, to assist and interact intelligently.",
    "story": "Sure, what story would you like?",
    "stories": "Sure, what story would you like?",
    "joke": "I love jokes too! Do you want me to crack one for you? 😎😁",
    "jokes": "I love jokes too! Do you want me to crack one for you? 😎😁",
    "machine learning": "Machine learning is a branch of AI that allows systems to learn from data and improve over time without being explicitly programmed.",
    "wassup": "Hi, wassup? How can I help you today?",
    "what is an ai chatbot": "An AI chatbot is a software program that uses artificial intelligence to simulate human conversation, understanding natural language to respond to user queries in a human-like way",
    "is url":"A URL (Uniform Resource Locator) is a web address that serves as a unique identifier and a global address for a specific resource, document, or page on the internet",
    "a url":"A URL (Uniform Resource Locator) is a web address that serves as a unique identifier and a global address for a specific resource, document, or page on the internet",
    "default": "I'm still learning, but I got your message.",
    
}

GREETINGS = {
    "hi": [
        "Hi there! How is it going?",
        "Hey! Hope you’re doing well."
    ],
    "hello": [
        "Hello there! How can I help you today?",
        "Hello there! How are you doing today?"
    ],
    "hey": [
        "Hi, how are you doing today?",
        "Hey! What’s up?"
    ],
    "good morning": [
        "Good Morning, How are you doing?",
        "Good Morning! Hope your day goes great!"
    ],
    "how are you": [
        "I'm just code, but I'm doing great 😄"
    ],
    "hi chatbot": [
        "I'm just code, but I'm doing great 😄"
    ]
}

GOODBYES = {
    "bye": [
        "Goodbye! Have a great day!",
        "Bye-bye! Take care!"
    ],
    "goodbye": [
        "Take care, see you soon!",
        "Goodbye! Until next time!"
    ],
    "see you": [
        "See you later 👋",
        "Catch you later!"
    ]
}


# ---------------- MATH HANDLER ----------------
class MathHandler:
    @staticmethod
    def _normalize(expr: str) -> str:
        expr = expr.lower()
        replacements = {
            "plus": "+", "minus": "-", "times": "*", "x": "*",
            "multiplied by": "*", "multiply": "*",
            "divide": "/", "divided by": "/"
        }
        for word, sym in replacements.items():
            expr = expr.replace(word, sym)
        return expr

    @staticmethod
    def _extract_expression(text: str) -> str | None:
        """Extract the first math-like expression from text."""
        normalized = MathHandler._normalize(text)
        match = re.search(r"\d+(\s*[\+\-\*/%]\s*\d+)+", normalized)
        return match.group(0) if match else None

    @staticmethod
    def _calculate(expr: str):
        if not expr:
            return None
        expr = expr.strip()
        if re.match(r"^[0-9\+\-\*/\.\%\(\) ]+$", expr):
            try:
                return eval(expr, {"__builtins__": None, "math": math}, {})
            except Exception:
                return None
        return None

    @classmethod
    def process(cls, text: str):
        """Return math result combined with greetings/prompts if found."""
        expr = cls._extract_expression(text)
        result = cls._calculate(expr)
        if result is None:
            return None

        responses = []

        # greetings
        for key, variants in GREETINGS.items():
            if re.search(rf"\b{re.escape(key)}\b", text.lower()):
                responses.append(random.choice(variants))

        # goodbyes
        for key, variants in GOODBYES.items():
            if re.search(rf"\b{re.escape(key)}\b", text.lower()):
                responses.append(random.choice(variants))

        # prompts
        for key, reply in PROMPTS.items():
            if key != "default" and re.search(rf"\b{re.escape(key)}\b", text.lower()):
                responses.append(reply)

        responses.append(f"The result of {expr} is {result}.")
        return " ".join(responses)


# ---------------- RESPONSE HANDLER ----------------
class ResponseHandler:
    @staticmethod
    def process(text: str):
        text_lower = text.lower()

        # if math-like content
        if any(ch.isdigit() for ch in text_lower) or any(op in text_lower for op in ["+", "-", "*", "x", "/", "plus", "minus", "times", "divide", 'divided by']):
            math_resp = MathHandler.process(text)
            if math_resp:
                return math_resp

        responses = []

        # greetings
        for key, variants in GREETINGS.items():
            if re.search(rf"\b{re.escape(key)}\b", text_lower):
                responses.append(random.choice(variants))

        # goodbyes
        for key, variants in GOODBYES.items():
            if re.search(rf"\b{re.escape(key)}\b", text_lower):
                responses.append(random.choice(variants))

        # prompts
        for key, reply in PROMPTS.items():
            if key != "default" and re.search(rf"\b{re.escape(key)}\b", text_lower):
                responses.append(reply)

        if responses:
            return " ".join(responses)
        return PROMPTS["default"]
