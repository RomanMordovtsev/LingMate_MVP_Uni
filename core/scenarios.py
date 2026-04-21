SCENARIOS = {
    "coffee_shop": {
        "title": "Coffee shop in London",
        "target_language": "en",
        "goal": "Order a drink politely, ask for options, and pay.",
        "situation": "You are in a coffee shop in London. You want to order a drink, ask about milk options, and complete the order politely.",
        "example_dialogue": [
            {"speaker": "Customer", "text": "Hello! Could I get a medium latte with oat milk, please?"},
            {"speaker": "Barista", "text": "Sure. For here or to go?"},
            {"speaker": "Customer", "text": "To go, please."}
        ],
        "key_phrases": [
            {
                "phrase": "Could I get...?",
                "meaning": "вежливая просьба заказать что-то",
                "example": "Could I get a latte, please?"
            },
            {
                "phrase": "For here or to go?",
                "meaning": "вопрос о том, будете ли вы есть или пить на месте или брать с собой",
                "example": "For here, please."
            },
            {
                "phrase": "How much is it?",
                "meaning": "вопрос о цене",
                "example": "How much is it?"
            },
            {
                "phrase": "Oat milk",
                "meaning": "овсяное молоко",
                "example": "Do you have oat milk?"
            }
        ],
        "teacher_notes": "Focus on polite requests and basic café interaction."
    },

    "small_talk": {
        "title": "Meeting a new person",
        "target_language": "en",
        "goal": "Introduce yourself, ask simple follow-up questions, and keep the conversation going.",
        "situation": "You meet a student from another country after class. Start a friendly conversation and learn basic information about each other.",
        "example_dialogue": [
            {"speaker": "You", "text": "Hi, nice to meet you. I'm Roman."},
            {"speaker": "Other person", "text": "Nice to meet you too! Where are you from?"},
            {"speaker": "You", "text": "I'm from Russia. What about you?"}
        ],
        "key_phrases": [
            {
                "phrase": "Nice to meet you",
                "meaning": "вежливая фраза при знакомстве",
                "example": "Nice to meet you!"
            },
            {
                "phrase": "Where are you from?",
                "meaning": "вопрос о том, из какой страны или города человек",
                "example": "Where are you from?"
            },
            {
                "phrase": "What do you study?",
                "meaning": "вопрос о специальности или предмете обучения",
                "example": "What do you study at university?"
            },
            {
                "phrase": "How about you?",
                "meaning": "короткий способ вернуть вопрос собеседнику",
                "example": "I study computer science. How about you?"
            }
        ],
        "teacher_notes": "Encourage reciprocal questions and a natural flow."
    },

    "hotel_checkin": {
        "title": "Hotel check-in",
        "target_language": "en",
        "goal": "Check in at a hotel, confirm your reservation, and ask basic questions about the room.",
        "situation": "You arrive at a hotel in London. You need to speak to the receptionist, confirm your booking, and ask for practical details.",
        "example_dialogue": [
            {"speaker": "Guest", "text": "Hello, I have a reservation under Roman Mordovtsev."},
            {"speaker": "Receptionist", "text": "Welcome. May I see your passport, please?"},
            {"speaker": "Guest", "text": "Sure. Is breakfast included?"}
        ],
        "key_phrases": [
            {
                "phrase": "I have a reservation",
                "meaning": "сообщение о том, что у вас есть бронирование",
                "example": "Hello, I have a reservation."
            },
            {
                "phrase": "May I see your passport, please?",
                "meaning": "вежливая просьба показать паспорт",
                "example": "May I see your passport, please?"
            },
            {
                "phrase": "Is breakfast included?",
                "meaning": "вопрос, входит ли завтрак в стоимость",
                "example": "Is breakfast included?"
            },
            {
                "phrase": "What time is check-out?",
                "meaning": "вопрос о времени выезда из отеля",
                "example": "What time is check-out?"
            }
        ],
        "teacher_notes": "Focus on travel-related hotel phrases and practical questions."
    },

    "airport_checkin": {
        "title": "Airport check-in",
        "target_language": "en",
        "goal": "Check in for a flight, answer basic airport questions, and ask about baggage.",
        "situation": "You are at the airport check-in desk before an international flight. You need to check in, show your passport, and talk about your baggage.",
        "example_dialogue": [
            {"speaker": "Passenger", "text": "Hello, I'd like to check in for my flight."},
            {"speaker": "Staff", "text": "Sure. May I see your passport?"},
            {"speaker": "Passenger", "text": "Of course. Can I check in this bag?"}
        ],
        "key_phrases": [
            {
                "phrase": "I'd like to check in for my flight",
                "meaning": "сообщение о том, что вы хотите зарегистрироваться на рейс",
                "example": "Hello, I'd like to check in for my flight."
            },
            {
                "phrase": "Can I check in this bag?",
                "meaning": "вопрос о сдаче багажа",
                "example": "Can I check in this bag?"
            },
            {
                "phrase": "Window seat",
                "meaning": "место у окна",
                "example": "Could I have a window seat, please?"
            },
            {
                "phrase": "Boarding pass",
                "meaning": "посадочный талон",
                "example": "Here is your boarding pass."
            }
        ],
        "teacher_notes": "Focus on airport vocabulary, practical requests, and short confident responses."
    }
}