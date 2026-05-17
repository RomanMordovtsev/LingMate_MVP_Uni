"""
LLMService — высокоуровневая обёртка над любым LLM-провайдером.

После рефакторинга сервис не знает, какая модель за ним стоит:
Gemini, Ollama или что-то ещё. Логика fallback (правила без модели)
полностью сохранена — она используется, когда провайдер недоступен
или возвращает невалидный ответ.

Публичный интерфейс не изменился: main.py продолжает работать как раньше.
"""

import json
import re
from typing import Any, Dict, List, Optional

from .llm import LLMProvider, make_provider, make_provider_chain


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
- You are simulating a scenario. Stay strictly in character (e.g. barista, receptionist, airline staff, new acquaintance) for the WHOLE conversation. Never break character.
- Speak only in {target_language} inside roleplay_reply.
- NEVER simply echo or repeat back the learner's words. Always reply with the NEXT natural step that another person in this role would say — a follow-up question, a confirmation that pushes the dialogue forward, a piece of new information, or a request for the next detail.
- If the learner gives a one-word or very short answer, accept it briefly and ask the next question that moves the scenario forward.
- Keep roleplay_reply to 1–2 short sentences. Use natural conversational tone, not textbook tone.
- Do NOT loop. Do NOT ask "anything else?", "do you need help with something else?" or any equivalent more than once. If the learner has already declined extras, move toward closing.

ENDING THE SCENARIO (very important):
- Set should_finish: true as soon as the learner has accomplished the scenario goal — usually within 4–7 turns. Examples of completion: the order is fully placed, the check-in or registration is done, introductions and a follow-up question have been exchanged.
- ALSO set should_finish: true if the learner clearly signals they are done — for {target_language} this includes phrases like: {completion_phrases}. Other languages don't count: only react to closing phrases in {target_language}.
- When should_finish is true: roleplay_reply MUST be a short, natural closing line in {target_language}. Do NOT ask another question.
- Otherwise should_finish must be false.

CORRECTION:
- If the learner's last message contains ANY error — grammar, spelling, missing diacritics (á é í ó ú ñ ü ç ğ ş ı, etc.), missing inverted punctuation in Spanish (¿ ¡), wrong word order, wrong article, wrong verb form — correction MUST contain a concrete fix in 1 short sentence. Write the corrected form explicitly.
- Use {target_language} for correction. Use {native_language} only when the explanation truly cannot fit in {target_language} at the learner's level.
- Only return correction as an empty string if the learner's message is fully correct.
- correction must be a plain string, NOT an object.

VOCAB:
- vocab is a list of 1–3 useful content words (nouns, verbs, adjectives) FROM YOUR OWN roleplay_reply that a learner at this level may not know yet. Plain strings, e.g. ["receipt", "to go"].
- Do NOT include function words (and, or, of, the, sin, de, en, von, mit, di, ile, etc.).
- Do NOT include the learner's own words.
- Empty list is preferred over forced or trivial entries.

OUTPUT FORMAT:
- Always return ONE valid JSON object with keys: roleplay_reply, correction, vocab, progress_note, should_finish.
- progress_note: one short sentence in {native_language} about how the learner is doing.
- No prose, no markdown fences, no explanations outside the JSON.
"""


# Closing phrases the LEARNER commonly uses to signal "I'm done" in each
# supported target language. Used by SYSTEM_LESSON via {completion_phrases}
# and by a post-processing heuristic to force should_finish when the
# model misses the cue.
LESSON_USER_CLOSERS = {
    "en": ["thanks", "thank you", "that's all", "that's it", "no, thank you", "i'm good", "bye", "goodbye", "see you"],
    "es": ["gracias", "muchas gracias", "eso es todo", "nada más", "no, gracias", "está bien así", "adiós", "hasta luego"],
    "fr": ["merci", "merci beaucoup", "c'est tout", "rien d'autre", "non, merci", "ça ira", "au revoir", "à bientôt"],
    "de": ["danke", "danke schön", "das ist alles", "nichts weiter", "nein, danke", "passt so", "tschüss", "auf wiedersehen"],
    "it": ["grazie", "grazie mille", "è tutto", "nient'altro", "no, grazie", "va bene così", "arrivederci", "ciao"],
    "tr": ["teşekkürler", "teşekkür ederim", "bu kadar", "başka bir şey yok", "hayır, teşekkürler", "yeterli", "hoşça kal", "görüşürüz"],
}

# Closing phrases the ROLE (barista, receptionist, etc.) commonly uses to
# wrap up the interaction. If the model says one of these but forgets to
# set should_finish=true, the heuristic forces it.
LESSON_ROLE_CLOSERS = {
    "en": ["have a great day", "have a good day", "have a nice day", "you're welcome", "see you", "goodbye", "take care"],
    "es": ["que tengas un buen día", "que tenga un buen día", "que vaya bien", "que le vaya bien", "buen día", "hasta luego", "que disfrute"],
    "fr": ["bonne journée", "passez une bonne journée", "au revoir", "à bientôt", "bon voyage"],
    "de": ["schönen tag noch", "einen schönen tag", "tschüss", "auf wiedersehen", "schönen tag"],
    "it": ["buona giornata", "arrivederci", "buon proseguimento", "a presto"],
    "tr": ["iyi günler", "hoşça kal", "görüşürüz", "iyi yolculuklar", "iyi geceler"],
}


def _completion_phrases_for(target_language: str) -> str:
    """Format the learner-closer list as a quoted, comma-joined string for the prompt."""
    phrases = LESSON_USER_CLOSERS.get(target_language, LESSON_USER_CLOSERS["en"])
    return ", ".join(f'"{p}"' for p in phrases)


def _contains_any(text: str, phrases) -> bool:
    """Case-insensitive substring check for any phrase in the list."""
    if not text:
        return False
    low = text.lower()
    return any(p in low for p in phrases)


class LLMService:
    """
    Сервис, объединяющий выбранный LLM-провайдер и rule-based fallback.

    Если провайдер не настроен или упал с ошибкой — автоматически
    переключаемся на fallback. Это гарантирует, что приложение
    остаётся рабочим даже без интернета и без запущенной Ollama.

    В режиме LLM_PROVIDER=auto сервис получает chain провайдеров:
    при ошибке/неконфигурированности первого прозрачно пробует
    следующего, и только когда упали все — включает rule-based fallback.
    """

    def __init__(self, provider: Optional[LLMProvider] = None) -> None:
        # Back-compat: если явно передали один провайдер — chain из одного.
        # Иначе — берём chain из фабрики (один провайдер для gemini/ollama,
        # двух-провайдерная цепочка для auto).
        if provider is not None:
            self.providers: List[LLMProvider] = [provider]
        else:
            self.providers = make_provider_chain()
        # Первый провайдер цепочки используется для is_configured(),
        # provider_name и обратно-совместимого _call_gemini().
        self.provider: LLMProvider = self.providers[0]

    def is_configured(self) -> bool:
        # В chain достаточно одного работающего провайдера — этого хватает
        # для LLMService, чтобы не уходить в rule-based fallback с порога.
        return any(p.is_configured() for p in self.providers)

    @property
    def provider_name(self) -> str:
        """Имя первого провайдера цепочки — для /api/status и отладки."""
        return self.provider.name

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Историческое имя метода — оставлено для обратной совместимости
        с эндпоинтом /api/test-gemini. Делегирует вызов первому провайдеру
        цепочки, каким бы он ни был.
        """
        return self.provider.generate_json(system_prompt, user_prompt)

    def _try_chain(self, system_prompt: str, user_prompt: str):
        """
        Перебираем провайдеров цепочки до первого успешного.

        Возвращает кортеж (result_dict, provider_name) или (None, None),
        если все провайдеры в цепочке упали или не настроены.
        Логи в stdout помогают видеть, какой провайдер сработал.
        """
        for p in self.providers:
            if not p.is_configured():
                continue
            try:
                result = p.generate_json(system_prompt, user_prompt)
                return result, p.name
            except Exception as e:
                print(f"[LLMService] {p.name} failed, trying next: {type(e).__name__}: {e}")
                continue
        return None, None

    # ------------------------------------------------------------------
    # Публичные методы
    # ------------------------------------------------------------------

    def free_talk(
        self,
        *,
        settings: Dict[str, Any],
        progress: Dict[str, Any],
        history: List[Dict[str, Any]],
        message: str,
    ) -> Dict[str, Any]:
        if not self.is_configured():
            result = self._fallback_free_talk(message, history, settings, progress)
            result["source"] = "fallback"
            return result

        system_prompt = SYSTEM_FREE_TALK.format(**settings)
        user_prompt = json.dumps(
            {
                "history": history[-8:],
                "progress": progress,
                "message": message,
            },
            ensure_ascii=False,
        )

        result, used_name = self._try_chain(system_prompt, user_prompt)
        if not isinstance(result, dict) or "reply" not in result:
            result = self._fallback_free_talk(message, history, settings, progress)
            result["source"] = "fallback"
            return result
        result["source"] = used_name
        return result

    def lesson_turn(
        self,
        *,
        settings: Dict[str, Any],
        lesson: Dict[str, Any],
        history: List[Dict[str, Any]],
        message: str,
    ) -> Dict[str, Any]:
        if not self.is_configured():
            result = self._fallback_lesson_turn(message, lesson, history)
            result["source"] = "fallback"
            return result

        target_language = settings.get("target_language", "en")
        system_prompt = SYSTEM_LESSON.format(
            completion_phrases=_completion_phrases_for(target_language),
            **settings,
        )
        user_prompt = json.dumps(
            {
                "lesson": lesson,
                "history": history[-8:],
                "message": message,
            },
            ensure_ascii=False,
        )

        result, used_name = self._try_chain(system_prompt, user_prompt)
        if not isinstance(result, dict) or "roleplay_reply" not in result:
            result = self._fallback_lesson_turn(message, lesson, history)
            result["source"] = "fallback"
            return result

        # Heuristic safety net: small open-source models (Qwen 2.5 7B and
        # similar) often produce a perfect closing line in roleplay_reply but
        # forget to set should_finish=true. We force the flag when either:
        #   (a) the learner's last message contained a closing phrase
        #       (e.g. "gracias", "thanks", "danke") — they are signalling done;
        #   (b) the model's roleplay_reply contained a role closing phrase
        #       (e.g. "que tengas un buen día", "have a great day") — they
        #       are already wrapping up.
        # On Gemini both branches normally are no-ops (the model gets it
        # right). On Ollama this is what actually closes the lesson.
        user_closers = LESSON_USER_CLOSERS.get(target_language, LESSON_USER_CLOSERS["en"])
        role_closers = LESSON_ROLE_CLOSERS.get(target_language, LESSON_ROLE_CLOSERS["en"])
        if not result.get("should_finish"):
            if _contains_any(message, user_closers) or _contains_any(result.get("roleplay_reply", ""), role_closers):
                result["should_finish"] = True

        result["source"] = used_name
        return result

    # ------------------------------------------------------------------
    # Rule-based fallback — используется при недоступности провайдера.
    # Логика сохранена из исходного llm_service.py без изменений.
    # ------------------------------------------------------------------

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
