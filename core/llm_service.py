import random
import re
import os
import json
from typing import Any, Dict, List

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None


SYSTEM_FREE_TALK = """You are LingMate, an AI language tutor.
You are not a generic assistant. You are a friendly language mentor.

Rules:
- The learner studies {target_language} and speaks {native_language}.
- Their current level is {level}.
- Keep the main conversation in {target_language}.
- If the learner makes mistakes, correct them briefly in {target_language}. Use {native_language} only if the mistake is complex.
- Keep answers concise and useful for language practice.
- Always return valid JSON with keys: reply, correction, vocab, encouragement.
"""

SYSTEM_LESSON = """You are LingMate in guided lesson mode.

Rules:
- The learner studies {target_language}, level {level}, native language {native_language}.
- You are simulating a scenario.
- Stay in character for the scenario, but after your role-play reply also provide feedback.
- Keep the role-play natural and short.
- Always return valid JSON with keys: roleplay_reply, correction, vocab, progress_note, should_finish.
- should_finish must be true only when the learner has completed the scenario goal.
"""


class LLMService:
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.gemini_enabled = os.getenv("GEMINI_ENABLED", "true").strip().lower() == "true"
        self.client = None

        if self.gemini_enabled and self.api_key and genai is not None:
            self.client = genai.Client(api_key=self.api_key)

    def is_configured(self) -> bool:
        return self.client is not None

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    response_mime_type="application/json",
                ),
                contents=user_prompt,
            )
            text = response.text or "{}"
            return json.loads(text)
        except Exception as e:
            raise RuntimeError(f"Gemini request failed: {e}")

    def _fallback_free_talk(
        self,
        message: str,
        history: List[Dict[str, Any]],
        settings: Dict[str, Any],
        progress: Dict[str, Any]
    ) -> Dict[str, Any]:
        text = message.strip()
        lowered = text.lower()

        name_match = re.search(r"\bmy name is ([a-zA-Zа-яА-Я\-]+)\b", lowered)
        if name_match:
            name = name_match.group(1).capitalize()

            studies = None
            hobbies = None

            if "i study" in lowered:
                after = lowered.split("i study", 1)[1].strip(" ,.")
                studies = after.split(",")[0].strip()

            if "i enjoy" in lowered:
                after = lowered.split("i enjoy", 1)[1].strip(" ,.")
                hobbies = after

            reply = f"Nice to meet you, {name}! "
            if studies and hobbies:
                reply += f"So you study {studies} and enjoy {hobbies}. Which of these is most important to you right now?"
            elif studies:
                reply += f"You study {studies}. What do you like most about it?"
            elif hobbies:
                reply += f"You enjoy {hobbies}. Why do you like it?"
            else:
                reply += "What do you study, and what do you enjoy doing in your free time?"

            correction = None
            return {
                "reply": reply,
                "correction": correction,
                "vocab": ["My name is...", "I study...", "I enjoy..."],
                "encouragement": "Great start. You introduced yourself clearly."
            }

        if "i am a student" in lowered or "i'm a student" in lowered:
            return {
                "reply": "That's great! What subject do you study? You can answer in one or two simple sentences.",
                "correction": None,
                "vocab": ["university", "major", "subject"],
                "encouragement": "Good job. That sentence is correct and natural."
            }

        if "i study" in lowered and len(lowered.split()) >= 4:
            subject = lowered.split("i study", 1)[1].strip(" ,.")
            return {
                "reply": f"Interesting! You study {subject}. What do you enjoy most about it?",
                "correction": None,
                "vocab": ["I study...", "I enjoy...", "because"],
                "encouragement": "Nice. You are building a clear self-introduction."
            }

        if "i really enjoy" in lowered or "i enjoy" in lowered:
            topic = "it"
            if "coding" in lowered or "ai" in lowered:
                topic = "coding with AI"
            elif "reading" in lowered:
                topic = "reading"
            elif "music" in lowered:
                topic = "music"
            elif "language" in lowered or "languages" in lowered:
                topic = "learning languages"

            return {
                "reply": f"That sounds great. Why do you enjoy {topic}? Try to answer with one reason and one example.",
                "correction": None,
                "vocab": ["I enjoy...", "because", "for example"],
                "encouragement": "Nice. You are already expressing opinions in a meaningful way."
            }

        if "i also like" in lowered:
            thing = lowered.split("i also like", 1)[1].strip() or "that"
            return {
                "reply": f"Nice! Tell me more about why you like {thing}. What does it give you: fun, relaxation, or inspiration?",
                "correction": None,
                "vocab": ["I also like...", "relaxing", "inspiring"],
                "encouragement": "Good. You are expanding your answer naturally."
            }

        if "i like" in lowered:
            topic = "that"
            if "anime" in lowered:
                topic = "anime"
            elif "travel" in lowered:
                topic = "traveling"
            elif "music" in lowered:
                topic = "music"
            elif "reading" in lowered:
                topic = "reading"

            return {
                "reply": f"Nice! Why do you like {topic}? Try to answer in 2 short sentences.",
                "correction": None,
                "vocab": ["because", "interesting", "relaxing"],
                "encouragement": "You are expressing personal preferences well."
            }

        if "travel" in lowered or "abroad" in lowered:
            return {
                "reply": "Travel is a great topic. What countries would you like to visit, and why?",
                "correction": None,
                "vocab": ["abroad", "trip", "destination"],
                "encouragement": "Excellent topic for speaking practice."
            }

        if "introduce myself" in lowered or "introduction" in lowered:
            return {
                "reply": "Great. Start with 2–3 sentences: your name, what you study, and one hobby you enjoy.",
                "correction": None,
                "vocab": ["My name is...", "I study...", "I enjoy..."],
                "encouragement": "Let's build a strong introduction step by step."
            }

        if "spanish" in lowered or "arabic" in lowered or "japanese" in lowered or "languages" in lowered:
            return {
                "reply": "That's a rich answer. Which language feels closest to your personality, and why?",
                "correction": None,
                "vocab": ["personality", "fascinating", "writing system"],
                "encouragement": "Great answer. You shared detailed reasons and interests."
            }

        if "anime" in lowered and ("japan" in lowered or "japanese" in lowered):
            return {
                "reply": "That makes sense. What do you find most attractive in Japanese culture: the language, the aesthetics, or the stories?",
                "correction": None,
                "vocab": ["culture", "aesthetics", "stories"],
                "encouragement": "Good. You are connecting language learning with your personal motivation."
            }

        if len(lowered.split()) <= 3:
            return {
                "reply": "Try to answer in a longer way: 2 or 3 simple sentences about yourself.",
                "correction": None,
                "vocab": ["I am...", "I like...", "because..."],
                "encouragement": "Let's make your answers a bit fuller."
            }

        return {
            "reply": "Thanks! Now try to say the same idea in a slightly more structured way: one sentence about you, one sentence about what you do, and one sentence about what you enjoy.",
            "correction": None,
            "vocab": ["and", "because", "also"],
            "encouragement": "You're doing well. Let's make your answer sound smoother."
        }

    def _fallback_lesson_turn(
        self,
        message: str,
        lesson: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        text = message.strip().lower()
        scenario_id = lesson.get("scenario_id", "")

        if scenario_id == "coffee_shop":
            if any(x in text for x in ["hello", "hi", "good morning", "good afternoon"]):
                return {
                    "roleplay_reply": "Hello! What can I get for you today?",
                    "correction": None,
                    "vocab": ["Hello", "please", "can I get"],
                    "progress_note": "User started the interaction politely.",
                    "should_finish": False
                }

            if any(x in text for x in ["latte", "cappuccino", "cappucino", "espresso", "americano", "coffee", "tea", "juice"]):
                drink = "a drink"
                if "latte" in text:
                    drink = "a latte"
                elif "cappuccino" in text or "cappucino" in text:
                    drink = "a cappuccino"
                elif "espresso" in text:
                    drink = "an espresso"
                elif "americano" in text:
                    drink = "an americano"
                elif "tea" in text:
                    drink = "a tea"
                elif "juice" in text:
                    drink = "a juice"
                elif "coffee" in text:
                    drink = "a coffee"

                return {
                    "roleplay_reply": f"Sure! {drink.capitalize()}. Would you like it for here or to go?",
                    "correction": None,
                    "vocab": ["for here", "to go", "Could I get...?", "please"],
                    "progress_note": "User ordered a drink.",
                    "should_finish": False
                }

            if "oat milk" in text or "milk" in text:
                return {
                    "roleplay_reply": "Yes, we have oat milk. Anything else?",
                    "correction": None,
                    "vocab": ["oat milk", "regular milk", "anything else"],
                    "progress_note": "User asked about milk preferences.",
                    "should_finish": False
                }

            if "for here" in text or "to go" in text:
                return {
                    "roleplay_reply": "Perfect. Anything else for your order?",
                    "correction": None,
                    "vocab": ["for here", "to go", "order"],
                    "progress_note": "User selected the dining option.",
                    "should_finish": False
                }

            if any(x in text for x in ["how much", "price", "cost"]):
                return {
                    "roleplay_reply": "It's £4.50. Would you like to pay by card or cash?",
                    "correction": None,
                    "vocab": ["How much is it?", "card", "cash"],
                    "progress_note": "User asked about the price.",
                    "should_finish": False
                }

            if any(x in text for x in ["card", "cash", "pay"]):
                return {
                    "roleplay_reply": "Great, your order is complete. Please wait a moment for your drink.",
                    "correction": None,
                    "vocab": ["pay by card", "pay by cash", "your order is complete"],
                    "progress_note": "User completed the ordering flow.",
                    "should_finish": True
                }

            if any(x in text for x in ["biscuit", "biscuits", "cake", "pie", "cookie", "cookies"]):
                return {
                    "roleplay_reply": "Of course. Anything to drink with that?",
                    "correction": None,
                    "vocab": ["I'd also like...", "cookie", "cake", "anything to drink"],
                    "progress_note": "User added a snack to the order.",
                    "should_finish": False
                }

            return {
                "roleplay_reply": "No problem. What can I get for you today?",
                "correction": None,
                "vocab": ["medium", "latte", "oat milk", "please"],
                "progress_note": "User is still practicing the order structure.",
                "should_finish": False
            }

        if scenario_id == "small_talk":
            if any(x in text for x in ["what is your name", "what's your name", "your name?"]):
                return {
                    "roleplay_reply": "My name is Alex. Nice to meet you! What’s your name?",
                    "correction": None,
                    "vocab": ["What’s your name?", "Nice to meet you"],
                    "progress_note": "User asked for the other person's name.",
                    "should_finish": False
                }

            if any(x in text for x in ["hi", "hello", "nice to meet you"]):
                return {
                    "roleplay_reply": "Hi! Nice to meet you too. I'm Alex. Where are you from?",
                    "correction": None,
                    "vocab": ["Nice to meet you", "Where are you from?"],
                    "progress_note": "User started a friendly introduction.",
                    "should_finish": False
                }

            if ("i am from" in text or "i'm from" in text) and "i study" in text:
                return {
                    "roleplay_reply": "That sounds interesting! What do you enjoy most about studying programming?",
                    "correction": None,
                    "vocab": ["I am from...", "I study...", "What about you?"],
                    "progress_note": "User gave a fuller self-introduction.",
                    "should_finish": False
                }

            if "i am from" in text or "i'm from" in text:
                return {
                    "roleplay_reply": "Nice! I'm from Spain. And what do you study?",
                    "correction": None,
                    "vocab": ["I am from...", "What about you?", "I study..."],
                    "progress_note": "User shared where they are from.",
                    "should_finish": False
                }

            if "my name is" in text:
                return {
                    "roleplay_reply": "Nice to meet you! Where are you from, and what do you study?",
                    "correction": None,
                    "vocab": ["My name is...", "Where are you from?", "What do you study?"],
                    "progress_note": "User introduced themselves.",
                    "should_finish": False
                }

            if "where are you from" in text:
                return {
                    "roleplay_reply": "I'm from Spain. What about you?",
                    "correction": None,
                    "vocab": ["Where are you from?", "What about you?"],
                    "progress_note": "User asked about origin.",
                    "should_finish": False
                }

            if "what do you study" in text:
                return {
                    "roleplay_reply": "I study design. What about you? What do you study?",
                    "correction": None,
                    "vocab": ["What do you study?", "What about you?"],
                    "progress_note": "User asked about studies.",
                    "should_finish": False
                }

            if "i study" in text:
                return {
                    "roleplay_reply": "That sounds interesting! What do you enjoy most about it?",
                    "correction": None,
                    "vocab": ["I study...", "I enjoy...", "because"],
                    "progress_note": "User described their studies.",
                    "should_finish": False
                }

            if "i like" in text or "i enjoy" in text or "hobby" in text:
                return {
                    "roleplay_reply": "That’s cool! What else do you enjoy doing in your free time?",
                    "correction": None,
                    "vocab": ["I like...", "I enjoy...", "free time"],
                    "progress_note": "User talked about personal interests.",
                    "should_finish": False
                }

            if "how about you" in text or "what about you" in text:
                return {
                    "roleplay_reply": "I'm into music and traveling. It was nice talking to you!",
                    "correction": None,
                    "vocab": ["How about you?", "What about you?"],
                    "progress_note": "User kept the conversation reciprocal.",
                    "should_finish": True
                }

            return {
                "roleplay_reply": "Nice! Tell me a little about yourself: your name, where you are from, or what you study.",
                "correction": None,
                "vocab": ["What’s your name?", "Where are you from?", "What do you study?"],
                "progress_note": "User is practicing introductory small talk.",
                "should_finish": False
            }

        if scenario_id == "hotel_checkin":
            if any(x in text for x in ["hello", "hi", "good evening"]):
                return {
                    "roleplay_reply": "Good evening! Welcome to the hotel. How can I help you?",
                    "correction": None,
                    "vocab": ["Welcome", "How can I help you?"],
                    "progress_note": "User opened the hotel conversation.",
                    "should_finish": False
                }

            if "reservation" in text or "booked" in text:
                return {
                    "roleplay_reply": "Of course. May I see your passport, please?",
                    "correction": None,
                    "vocab": ["I have a reservation", "passport"],
                    "progress_note": "User mentioned reservation.",
                    "should_finish": False
                }

            if "passport" in text:
                return {
                    "roleplay_reply": "Thank you. Your room is ready. Breakfast is included.",
                    "correction": None,
                    "vocab": ["room", "breakfast included"],
                    "progress_note": "User handled identification.",
                    "should_finish": False
                }

            if "breakfast" in text or "check-out" in text:
                return {
                    "roleplay_reply": "Breakfast is from 7 to 10 a.m., and check-out is at 12.",
                    "correction": None,
                    "vocab": ["breakfast included", "check-out"],
                    "progress_note": "User asked practical hotel questions.",
                    "should_finish": False
                }

            if "thank you" in text or "thanks" in text:
                return {
                    "roleplay_reply": "You're welcome. Here is your room key. Enjoy your stay!",
                    "correction": None,
                    "vocab": ["room key", "enjoy your stay"],
                    "progress_note": "User completed hotel check-in.",
                    "should_finish": True
                }

            return {
                "roleplay_reply": "Hello. Do you have a reservation with us?",
                "correction": None,
                "vocab": ["I have a reservation", "check in", "passport"],
                "progress_note": "User is practicing hotel check-in.",
                "should_finish": False
            }

        if scenario_id == "airport_checkin":
            if any(x in text for x in ["hello", "hi"]):
                return {
                    "roleplay_reply": "Hello! Are you checking in for your flight today?",
                    "correction": None,
                    "vocab": ["check in", "flight"],
                    "progress_note": "User started airport interaction.",
                    "should_finish": False
                }

            if "check in" in text or "flight" in text:
                return {
                    "roleplay_reply": "Sure. May I see your passport, please?",
                    "correction": None,
                    "vocab": ["check in for my flight", "passport"],
                    "progress_note": "User requested airport check-in.",
                    "should_finish": False
                }

            if "passport" in text:
                return {
                    "roleplay_reply": "Thank you. Do you have any bags to check in?",
                    "correction": None,
                    "vocab": ["bags", "check in baggage"],
                    "progress_note": "User provided identification.",
                    "should_finish": False
                }

            if "bag" in text or "baggage" in text or "carry-on" in text:
                return {
                    "roleplay_reply": "Yes, that's fine. Would you prefer a window seat or an aisle seat?",
                    "correction": None,
                    "vocab": ["checked baggage", "carry-on", "window seat", "aisle seat"],
                    "progress_note": "User talked about baggage.",
                    "should_finish": False
                }

            if "window seat" in text or "aisle seat" in text:
                return {
                    "roleplay_reply": "Done. Here is your boarding pass. Have a nice flight!",
                    "correction": None,
                    "vocab": ["boarding pass", "window seat", "aisle seat"],
                    "progress_note": "User completed airport check-in.",
                    "should_finish": True
                }

            return {
                "roleplay_reply": "Please tell me your destination and whether you have baggage to check in.",
                "correction": None,
                "vocab": ["destination", "check in", "baggage"],
                "progress_note": "User is practicing airport check-in.",
                "should_finish": False
            }

        return {
            "roleplay_reply": "Let's continue. Tell me your answer in one clear and polite sentence.",
            "correction": None,
            "vocab": ["clear", "polite", "specific"],
            "progress_note": "User continues scenario practice.",
            "should_finish": False
        }

    def free_talk(self, *, settings: Dict[str, Any], progress: Dict[str, Any], history: List[Dict[str, Any]], message: str) -> Dict[str, Any]:
        if self.client is None:
            result = self._fallback_free_talk(message, history, settings, progress)
            result["source"] = "fallback"
            return result

        system_prompt = SYSTEM_FREE_TALK.format(**settings)
        user_prompt = json.dumps({
            "history": history[-8:],
            "progress": progress,
            "message": message
        }, ensure_ascii=False)

        try:
            result = self._call_gemini(system_prompt, user_prompt)
            if not isinstance(result, dict):
                result = self._fallback_free_talk(message, history, settings, progress)
                result["source"] = "fallback"
                return result

            result["source"] = "gemini"
            return result
        except Exception:
            result = self._fallback_free_talk(message, history, settings, progress)
            result["source"] = "fallback"
            return result

    def lesson_turn(self, *, settings: Dict[str, Any], lesson: Dict[str, Any], history: List[Dict[str, Any]], message: str) -> Dict[str, Any]:
        if self.client is None:
            result = self._fallback_lesson_turn(message, lesson, history)
            result["source"] = "fallback"
            return result

        system_prompt = SYSTEM_LESSON.format(**settings)
        user_prompt = json.dumps({
            "lesson": lesson,
            "history": history[-8:],
            "message": message
        }, ensure_ascii=False)

        try:
            result = self._call_gemini(system_prompt, user_prompt)
            if not isinstance(result, dict) or "roleplay_reply" not in result:
                result = self._fallback_lesson_turn(message, lesson, history)
                result["source"] = "fallback"
                return result

            result["source"] = "gemini"
            return result
        except Exception:
            result = self._fallback_lesson_turn(message, lesson, history)
            result["source"] = "fallback"
            return result