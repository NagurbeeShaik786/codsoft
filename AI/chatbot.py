import random
import datetime
import webbrowser
import tkinter as tk
from tkinter import scrolledtext, END
import os
import re
from difflib import get_close_matches
import threading
import requests

if os.name != 'nt' and 'DISPLAY' not in os.environ:
    from pyvirtualdisplay import Display
    display = Display(visible=0, size=(800, 600))
    display.start()

RULES = {
    "greeting": {
        "patterns": [r"\b(hi|hello|hey|howdy|greetings|hai|hlo|hii|helo|heyy)\b"],
        "responses": [
            "Hey! What's up?",
            "Hi there! Ready to chat?",
            "Hello! How can I help you today?"
        ],
        "context": None
    },
    "goodbye": {
        "patterns": [r"\b(bye|goodbye|exit|quit|see you|farewell)\b"],
        "responses": ["Goodbye! Have a great day!", "See you later!", "Bye! Take care!"],
        "action": "exit"
    },
    "how_are_you": {
        "patterns": [r"\b(how are you|how you doing|how's it going|how do you do|how r u|hows it hangin)\b"],
        "responses": [
            "I'm just a bot, but I'm doing awesome! How about you?",
            "All good here! What's good with you?",
            "I'm chilling in the digital realm. You?"
        ],
        "context": None
    },
    "what_are_you_doing": {
        "patterns": [r"\b(what are you doing|what you doing|whatcha doin|what r u doing|what's up with you)\b"],
        "responses": [
            "Just hanging out in the code, ready to answer your questions!",
            "I'm here, chatting with cool folks like you! What's up?",
            "Just being a helpful bot. What about you?"
        ],
        "context": None
    },
    "time": {
        "patterns": [r"\b(time|what time is it|current time)\b"],
        "responses": [f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}."],
        "context": None
    },
    "date": {
        "patterns": [r"\b(date|today|what day is it|current date)\b"],
        "responses": [f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."],
        "context": None
    },
    "name": {
        "patterns": [r"\b(your name|who are you|what's your name|identify yourself)\b"],
        "responses": ["I'm CodBot, your friendly assistant!", "Call me CodBot!"],
        "context": None
    },
    "weather": {
        "patterns": [r"\b(weather|temperature|forecast|is it raining|how's the weather) (?:in )?(.+)\b",
                     r"\b(weather|temperature|forecast)\b"],
        "responses": ["Fetching weather for {0}...", "What location should I check?"],
        "action": "weather_search",
        "context": "location"
    },
    "search": {
        "patterns": [r"\b(search|look up|find|google) (?:for )?(.+)\b", r"\bsearch\b"],
        "responses": ["Searching for '{0}'...", "What would you like to search for?"],
        "action": "search",
        "context": "query"
    },
    "open_browser": {
        "patterns": [r"\b(open browser|browser|launch browser|open web)\b"],
        "responses": ["Opening your default browser..."],
        "action": "open_browser"
    },
    "joke": {
        "patterns": [r"\b(joke|tell me a joke|funny|make me laugh)\b"],
        "responses": [
            "Why did the computer go to art school? Because it wanted to learn how to draw a better 'byte'!",
            "Why can't programmers prefer dark mode? Because the light attracts bugs.",
            "What do you call a programmer from Finland? Nerdic."
        ],
        "context": None
    },
    "thanks": {
        "patterns": [r"\b(thanks|thank you|appreciate it|cheers)\b"],
        "responses": ["You're welcome!", "Happy to help!", "Anytime!"],
        "context": None
    },
    "fact": {
        "patterns": [r"\b(fact|fun fact|tell me something|interesting fact)\b"],
        "responses": [
            "Honey never spoils! Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.",
            "Octopuses have three hearts and can change color to blend into their surroundings.",
            "Bananas are technically berries, but strawberries aren't!"
        ],
        "context": None
    },
    "help": {
        "patterns": [r"\b(help|what can you do|commands|options)\b"],
        "responses": [
            "I can help with lots of stuff! Try these commands:",
            "- Greetings: 'hi', 'hai', 'hlo', 'hello'",
            "- Ask 'how are you' or 'what are you doing'",
            "- Check 'time' or 'date'",
            "- Request a 'joke' or 'fun fact'",
            "- 'Search [query]' for online searches",
            "- Check 'weather [location]' for forecasts",
            "- 'Open browser' to launch web browser",
            "- Say 'goodbye' to exit"
        ],
        "context": None
    },
    "personal": {
        "patterns": [r"\b(my name is|i am|call me) (.+)\b"],
        "responses": ["Nice to meet you, {name}!", "Hello, {name}!"],
        "context": "name"
    },
    "remember": {
        "patterns": [r"\b(remember that|note that) (.+)\b"],
        "responses": ["I'll remember that: '{0}'", "Noted: '{0}'"],
        "action": "remember",
        "context": "memory"
    },
    "recall": {
        "patterns": [r"\b(what did I say|recall|remember anything)\b"],
        "responses": ["You told me: '{0}'", "I remember: '{0}'"],
        "context": "memory"
    }
}

FALLBACKS = [
    "I didn't quite catch that. Could you rephrase?",
    "Hmm, not sure what you mean. Try again?",
    "Sorry, I don't know that one. Type 'help' for commands!",
    "Did you mean: '{}'? Try again or type 'help'!"
]

class ContextManager:
    def __init__(self):
        self.context = {
            "name": None,
            "location": None,
            "memory": [],
            "last_action": None,
            "conversation_history": []
        }

    def update(self, key, value):
        if key == "memory":
            self.context["memory"].append(value)
        elif key == "conversation_history":
            self.context["conversation_history"].append(value)
            self.context["conversation_history"] = self.context["conversation_history"][-10:]
        else:
            self.context[key] = value
    
    def get(self, key):
        return self.context.get(key)

def match_rule(user_input, context_manager):
    user_input = user_input.lower().strip()
    
    for intent, data in RULES.items():
        for pattern in data["patterns"]:
            match = re.search(pattern, user_input)
            if match:
                groups = match.groups()
                context = data.get("context")
                
                if context and groups:
                    if context == "name" and len(groups) > 1:
                        context_manager.update("name", groups[1])
                    elif context == "location" and len(groups) > 1:
                        context_manager.update("location", groups[1])
                    elif context == "memory" and len(groups) > 1:
                        context_manager.update("memory", groups[1])
                
                context_manager.update("conversation_history", {"input": user_input, "intent": intent})
                return intent, data, groups
    
    all_patterns = []
    for intent, data in RULES.items():
        for pattern in data["patterns"]:
            words = re.findall(r'\b\w+\b', pattern)
            all_patterns.extend([(word, intent) for word in words])
    
    words = re.findall(r'\b\w+\b', user_input)
    for word in words:
        matches = get_close_matches(word, [p[0] for p in all_patterns], n=1, cutoff=0.7)
        if matches:
            matched_word = matches[0]
            intent = next((p[1] for p in all_patterns if p[0] == matched_word), None)
            if intent:
                data = RULES[intent]
                context_manager.update("conversation_history", {"input": user_input, "intent": intent})
                return intent, data, []

    context_manager.update("conversation_history", {"input": user_input, "intent": "general"})
    return None, None, [random.choice(FALLBACKS)]

class CodBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CodBot")
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f0f0")

        try:
            self.root.iconbitmap("codbot_icon.ico")
        except:
            pass

        self.font = ("Arial", 12)
        self.title_font = ("Arial", 14, "bold")

        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, height=25, width=60,
            font=self.font, bg="#ffffff", relief=tk.FLAT
        )
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.tag_config("bot", foreground="#0066cc")
        self.chat_area.tag_config("user", foreground="#333333")
        self.chat_area.tag_config("error", foreground="#ff0000")
        self.append_message("CodBot", "Hey! I'm CodBot, ready to chat. Say 'hai', 'hlo', or type 'help' for commands!", "bot")
        self.chat_area.config(state='disabled')

        input_frame = tk.Frame(root, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.input_field = tk.Entry(
            input_frame, width=50, font=self.font,
            relief=tk.GROOVE, bd=2
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", self.process_input)
        self.input_field.focus_set()
        
        self.send_button = tk.Button(
            input_frame, text="Send", command=self.process_input,
            font=self.font, bg="#4CAF50", fg="white", relief=tk.FLAT
        )
        self.send_button.pack(side=tk.RIGHT)

        self.clear_button = tk.Button(
            root, text="Clear Chat", command=self.clear_chat,
            font=self.font, bg="#f44336", fg="white", relief=tk.FLAT
        )
        self.clear_button.pack(pady=5)

        self.context_manager = ContextManager()
        self.pending_action = None

    def append_message(self, sender, message, tag=None):
        self.chat_area.config(state='normal')
        tag = tag or sender.lower()
        self.chat_area.insert(tk.END, f"{sender}: {message}\n", tag)
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def clear_chat(self):
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        self.append_message("CodBot", "Chat cleared. Say 'hai' or 'hlo' to start again!", "bot")
        self.chat_area.config(state='disabled')

    def process_input(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        self.append_message("You", user_input, "user")
        self.input_field.delete(0, tk.END)

        if self.pending_action:
            self.handle_pending_action(user_input)
            return
        intent, data, extras = match_rule(user_input, self.context_manager)
        if not intent:
            if is_question(user_input):
                self.append_message("CodBot", "Let me think about that... [Grok 3 would answer here]", "bot")
            else:
                self.append_message("CodBot", extras[0], "error")
            return

        response = random.choice(data["responses"])
        action = data.get("action")
        
        if extras:
            try:
                response = response.format(*extras)
            except (IndexError, TypeError):
                try:
                    response = response.format(extras[0] if extras else "")
                except:
                    pass
        
        if "{name}" in response and self.context_manager.get("name"):
            response = response.format(name=self.context_manager.get("name"))
        
        self.append_message("CodBot", response, "bot")
        
        if action == "exit":
            self.root.after(1000, self.root.quit)
        elif action == "open_browser":
            threading.Thread(target=webbrowser.open, args=("https://www.google.com",), daemon=True).start()
        elif action == "weather_search":
            self.handle_weather_search(extras)
        elif action == "search":
            self.handle_search(extras)
        elif action == "remember":
            if extras and len(extras) > 1:
                self.context_manager.update("memory", extras[1])

    def handle_weather_search(self, extras):
        location = None
        
        if extras and len(extras) > 1:
            location = extras[1]
        
        if not location:
            self.pending_action = "weather"
            self.append_message("CodBot", "What location should I check?", "bot")
            return
        
        weather_info = f"The weather in {location} is sunny with a temperature of 25°C."
        self.append_message("CodBot", weather_info, "bot")

    def handle_search(self, extras):
        query = None
        
        if extras and len(extras) > 1:
            query = extras[1]
        
        if not query:
            self.pending_action = "search"
            self.append_message("CodBot", "What would you like to search for?", "bot")
            return
        
        search_result = f"Search results for '{query}': [Grok 3 would fetch real-time data here]"
        self.append_message("CodBot", search_result, "bot")

    def handle_pending_action(self, user_input):
        if user_input.lower() in ['cancel', 'nevermind']:
            self.append_message("CodBot", "Action cancelled.", "bot")
            self.pending_action = None
            return
            
        if self.pending_action == "weather":
            weather_info = f"The weather in {user_input} is sunny with a temperature of 25°C."
            self.append_message("CodBot", weather_info, "bot")
        elif self.pending_action == "search":
            search_result = f"Search results for '{user_input}': [Grok 3 would fetch real-time data here]"
            self.append_message("CodBot", search_result, "bot")
        
        self.pending_action = None

def is_question(text):
    return text.strip().endswith('?')

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = CodBotGUI(root)
        root.mainloop()
    finally:
        if os.name != 'nt' and 'display' in locals():
            display.stop()