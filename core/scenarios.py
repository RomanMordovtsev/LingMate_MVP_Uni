SCENARIOS = {
    # ========================================================================
    # ENGLISH
    # ========================================================================
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
            {"phrase": "Could I get...?", "meaning": "вежливая просьба заказать что-то", "example": "Could I get a latte, please?"},
            {"phrase": "For here or to go?", "meaning": "вопрос о том, будете ли вы есть или пить на месте или брать с собой", "example": "For here, please."},
            {"phrase": "How much is it?", "meaning": "вопрос о цене", "example": "How much is it?"},
            {"phrase": "Oat milk", "meaning": "овсяное молоко", "example": "Do you have oat milk?"}
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
            {"phrase": "Nice to meet you", "meaning": "вежливая фраза при знакомстве", "example": "Nice to meet you!"},
            {"phrase": "Where are you from?", "meaning": "вопрос о том, из какой страны или города человек", "example": "Where are you from?"},
            {"phrase": "What do you study?", "meaning": "вопрос о специальности или предмете обучения", "example": "What do you study at university?"},
            {"phrase": "How about you?", "meaning": "короткий способ вернуть вопрос собеседнику", "example": "I study computer science. How about you?"}
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
            {"phrase": "I have a reservation", "meaning": "сообщение о том, что у вас есть бронирование", "example": "Hello, I have a reservation."},
            {"phrase": "May I see your passport, please?", "meaning": "вежливая просьба показать паспорт", "example": "May I see your passport, please?"},
            {"phrase": "Is breakfast included?", "meaning": "вопрос, входит ли завтрак в стоимость", "example": "Is breakfast included?"},
            {"phrase": "What time is check-out?", "meaning": "вопрос о времени выезда из отеля", "example": "What time is check-out?"}
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
            {"phrase": "I'd like to check in for my flight", "meaning": "сообщение о том, что вы хотите зарегистрироваться на рейс", "example": "Hello, I'd like to check in for my flight."},
            {"phrase": "Can I check in this bag?", "meaning": "вопрос о сдаче багажа", "example": "Can I check in this bag?"},
            {"phrase": "Window seat", "meaning": "место у окна", "example": "Could I have a window seat, please?"},
            {"phrase": "Boarding pass", "meaning": "посадочный талон", "example": "Here is your boarding pass."}
        ],
        "teacher_notes": "Focus on airport vocabulary, practical requests, and short confident responses."
    },

    # ========================================================================
    # ESPAÑOL — castellano (Spain Spanish)
    # ========================================================================
    "coffee_shop_es": {
        "title": "Cafetería en Madrid",
        "target_language": "es",
        "goal": "Pedir un café de forma educada, preguntar sobre opciones y pagar.",
        "situation": "Estás en una cafetería en Madrid. Quieres pedir un café, preguntar por el tipo de leche y completar el pedido con cortesía.",
        "example_dialogue": [
            {"speaker": "Cliente", "text": "Hola, ¿me pone un café con leche, por favor?"},
            {"speaker": "Camarero", "text": "Claro. ¿Para tomar aquí o para llevar?"},
            {"speaker": "Cliente", "text": "Para llevar, gracias."}
        ],
        "key_phrases": [
            {"phrase": "¿Me pone...?", "meaning": "вежливая просьба заказать (испанский Испании)", "example": "¿Me pone un café, por favor?"},
            {"phrase": "Para tomar aquí o para llevar", "meaning": "на месте или с собой", "example": "Para llevar, gracias."},
            {"phrase": "¿Cuánto es?", "meaning": "сколько стоит", "example": "¿Cuánto es en total?"},
            {"phrase": "Leche de avena", "meaning": "овсяное молоко", "example": "¿Tienen leche de avena?"}
        ],
        "teacher_notes": "Focus on polite ordering in Spain Spanish (castellano), not Latin American variants."
    },

    "small_talk_es": {
        "title": "Conocer a una persona nueva",
        "target_language": "es",
        "goal": "Presentarte, hacer preguntas básicas y mantener la conversación.",
        "situation": "Conoces a un estudiante de otro país después de clase. Empieza una conversación amistosa y aprende información básica el uno del otro.",
        "example_dialogue": [
            {"speaker": "Tú", "text": "Hola, encantado de conocerte. Me llamo Roman."},
            {"speaker": "Otra persona", "text": "¡Encantada! ¿De dónde eres?"},
            {"speaker": "Tú", "text": "Soy de Rusia. ¿Y tú?"}
        ],
        "key_phrases": [
            {"phrase": "Encantado / Encantada de conocerte", "meaning": "приятно познакомиться (форма меняется по полу)", "example": "Encantado de conocerte."},
            {"phrase": "¿De dónde eres?", "meaning": "откуда ты родом", "example": "¿De dónde eres?"},
            {"phrase": "¿Qué estudias?", "meaning": "что ты изучаешь", "example": "¿Qué estudias en la universidad?"},
            {"phrase": "¿Y tú?", "meaning": "короткий способ вернуть вопрос", "example": "Estudio informática. ¿Y tú?"}
        ],
        "teacher_notes": "Encourage reciprocal questions. Note gender agreement: encantado (m.) / encantada (f.)."
    },

    "hotel_checkin_es": {
        "title": "Recepción del hotel",
        "target_language": "es",
        "goal": "Registrarte en el hotel, confirmar tu reserva y preguntar detalles básicos.",
        "situation": "Llegas a un hotel en Madrid. Necesitas hablar con el recepcionista, confirmar tu reserva y preguntar detalles prácticos sobre la habitación.",
        "example_dialogue": [
            {"speaker": "Huésped", "text": "Hola, tengo una reserva a nombre de Roman Mordovtsev."},
            {"speaker": "Recepcionista", "text": "Bienvenido. ¿Me puede mostrar su pasaporte, por favor?"},
            {"speaker": "Huésped", "text": "Claro. ¿El desayuno está incluido?"}
        ],
        "key_phrases": [
            {"phrase": "Tengo una reserva", "meaning": "у меня есть бронирование", "example": "Tengo una reserva a nombre de..."},
            {"phrase": "¿Me puede mostrar su pasaporte?", "meaning": "вежливая просьба показать паспорт (форма usted)", "example": "¿Me puede mostrar su pasaporte, por favor?"},
            {"phrase": "¿El desayuno está incluido?", "meaning": "входит ли завтрак", "example": "¿El desayuno está incluido?"},
            {"phrase": "¿A qué hora es la salida?", "meaning": "во сколько выезд (check-out)", "example": "¿A qué hora es la salida?"}
        ],
        "teacher_notes": "Use formal address (usted) — standard in Spanish hotels."
    },

    "airport_checkin_es": {
        "title": "Facturación en el aeropuerto",
        "target_language": "es",
        "goal": "Hacer el check-in del vuelo, responder preguntas básicas y hablar sobre el equipaje.",
        "situation": "Estás en el mostrador de facturación antes de un vuelo internacional. Necesitas facturar, mostrar el pasaporte y hablar de tu equipaje.",
        "example_dialogue": [
            {"speaker": "Pasajero", "text": "Hola, quería facturar para mi vuelo."},
            {"speaker": "Empleado", "text": "Por supuesto. ¿Me enseña su pasaporte?"},
            {"speaker": "Pasajero", "text": "Claro. ¿Puedo facturar esta maleta?"}
        ],
        "key_phrases": [
            {"phrase": "Quería facturar para mi vuelo", "meaning": "я хотел бы зарегистрироваться на рейс", "example": "Quería facturar para mi vuelo a Barcelona."},
            {"phrase": "¿Puedo facturar esta maleta?", "meaning": "могу ли я сдать этот чемодан в багаж", "example": "¿Puedo facturar esta maleta?"},
            {"phrase": "Asiento de ventanilla", "meaning": "место у окна", "example": "¿Podría darme un asiento de ventanilla?"},
            {"phrase": "Tarjeta de embarque", "meaning": "посадочный талон", "example": "Aquí tiene su tarjeta de embarque."}
        ],
        "teacher_notes": "Spain Spanish airport vocabulary: facturar = check-in, maleta = suitcase, tarjeta de embarque = boarding pass."
    },

    # ========================================================================
    # FRANÇAIS (France)
    # ========================================================================
    "coffee_shop_fr": {
        "title": "Café à Paris",
        "target_language": "fr",
        "goal": "Commander une boisson poliment, demander des options et payer.",
        "situation": "Tu es dans un café à Paris. Tu veux commander une boisson, demander quel lait est disponible et finir la commande poliment.",
        "example_dialogue": [
            {"speaker": "Client", "text": "Bonjour, je voudrais un café au lait, s'il vous plaît."},
            {"speaker": "Serveur", "text": "Bien sûr. Sur place ou à emporter ?"},
            {"speaker": "Client", "text": "À emporter, merci."}
        ],
        "key_phrases": [
            {"phrase": "Je voudrais...", "meaning": "вежливая форма «я хотел бы» (стандарт для заказа)", "example": "Je voudrais un café, s'il vous plaît."},
            {"phrase": "Sur place ou à emporter ?", "meaning": "на месте или с собой", "example": "Sur place, merci."},
            {"phrase": "Ça fait combien ?", "meaning": "сколько с меня", "example": "Ça fait combien en tout ?"},
            {"phrase": "Lait d'avoine", "meaning": "овсяное молоко", "example": "Vous avez du lait d'avoine ?"}
        ],
        "teacher_notes": "Always start with 'Bonjour' — skipping it is considered rude in France."
    },

    "small_talk_fr": {
        "title": "Rencontrer quelqu'un",
        "target_language": "fr",
        "goal": "Se présenter, poser des questions simples et entretenir la conversation.",
        "situation": "Tu rencontres un étudiant d'un autre pays après le cours. Commence une conversation amicale et apprenez les bases l'un sur l'autre.",
        "example_dialogue": [
            {"speaker": "Toi", "text": "Salut, enchanté. Je m'appelle Roman."},
            {"speaker": "Autre personne", "text": "Enchantée ! D'où viens-tu ?"},
            {"speaker": "Toi", "text": "Je viens de Russie. Et toi ?"}
        ],
        "key_phrases": [
            {"phrase": "Enchanté / Enchantée", "meaning": "приятно познакомиться (форма меняется по полу)", "example": "Enchanté !"},
            {"phrase": "D'où viens-tu ?", "meaning": "откуда ты", "example": "D'où viens-tu ?"},
            {"phrase": "Qu'est-ce que tu étudies ?", "meaning": "что ты изучаешь", "example": "Qu'est-ce que tu étudies à la fac ?"},
            {"phrase": "Et toi ?", "meaning": "а ты", "example": "J'étudie l'informatique. Et toi ?"}
        ],
        "teacher_notes": "Use informal 'tu' between students. Gender agreement: enchanté (m.) / enchantée (f.)."
    },

    "hotel_checkin_fr": {
        "title": "Arrivée à l'hôtel",
        "target_language": "fr",
        "goal": "S'enregistrer à l'hôtel, confirmer la réservation et poser des questions pratiques.",
        "situation": "Tu arrives dans un hôtel à Paris. Tu dois parler au réceptionniste, confirmer ta réservation et demander des détails pratiques sur la chambre.",
        "example_dialogue": [
            {"speaker": "Client", "text": "Bonjour, j'ai une réservation au nom de Roman Mordovtsev."},
            {"speaker": "Réceptionniste", "text": "Bienvenue. Votre passeport, s'il vous plaît."},
            {"speaker": "Client", "text": "Voilà. Le petit-déjeuner est compris ?"}
        ],
        "key_phrases": [
            {"phrase": "J'ai une réservation", "meaning": "у меня бронирование", "example": "Bonjour, j'ai une réservation."},
            {"phrase": "Votre passeport, s'il vous plaît", "meaning": "паспорт, пожалуйста (форма vouvoiement)", "example": "Votre passeport, s'il vous plaît."},
            {"phrase": "Le petit-déjeuner est compris ?", "meaning": "включён ли завтрак", "example": "Le petit-déjeuner est compris ?"},
            {"phrase": "À quelle heure faut-il libérer la chambre ?", "meaning": "во сколько надо освободить номер", "example": "À quelle heure faut-il libérer la chambre ?"}
        ],
        "teacher_notes": "Use 'vous' (formal). Note 'petit-déjeuner' (breakfast) vs 'déjeuner' (lunch in France)."
    },

    "airport_checkin_fr": {
        "title": "Enregistrement à l'aéroport",
        "target_language": "fr",
        "goal": "S'enregistrer pour un vol, répondre aux questions et parler du bagage.",
        "situation": "Tu es au comptoir d'enregistrement avant un vol international. Tu dois t'enregistrer, montrer ton passeport et parler de tes bagages.",
        "example_dialogue": [
            {"speaker": "Passager", "text": "Bonjour, je voudrais m'enregistrer pour mon vol."},
            {"speaker": "Agent", "text": "Bien sûr. Votre passeport, s'il vous plaît."},
            {"speaker": "Passager", "text": "Voilà. Je peux enregistrer ce bagage ?"}
        ],
        "key_phrases": [
            {"phrase": "Je voudrais m'enregistrer pour mon vol", "meaning": "я хотел бы зарегистрироваться на рейс", "example": "Je voudrais m'enregistrer pour mon vol pour Paris."},
            {"phrase": "Je peux enregistrer ce bagage ?", "meaning": "могу ли я сдать этот багаж", "example": "Je peux enregistrer ce bagage ?"},
            {"phrase": "Place côté hublot", "meaning": "место у окна", "example": "Une place côté hublot, s'il vous plaît."},
            {"phrase": "Carte d'embarquement", "meaning": "посадочный талон", "example": "Voici votre carte d'embarquement."}
        ],
        "teacher_notes": "France airport vocabulary: enregistrement = check-in, bagage = baggage, carte d'embarquement = boarding pass."
    },

    # ========================================================================
    # DEUTSCH (Germany)
    # ========================================================================
    "coffee_shop_de": {
        "title": "Café in Berlin",
        "target_language": "de",
        "goal": "Höflich ein Getränk bestellen, nach Optionen fragen und bezahlen.",
        "situation": "Du bist in einem Café in Berlin. Du möchtest ein Getränk bestellen, nach der Milchsorte fragen und höflich bezahlen.",
        "example_dialogue": [
            {"speaker": "Kunde", "text": "Hallo, einen Milchkaffee mit Hafermilch, bitte."},
            {"speaker": "Barista", "text": "Gerne. Zum Hieressen oder zum Mitnehmen?"},
            {"speaker": "Kunde", "text": "Zum Mitnehmen, danke."}
        ],
        "key_phrases": [
            {"phrase": "Ich hätte gern...", "meaning": "вежливая форма «я бы хотел» при заказе", "example": "Ich hätte gern einen Cappuccino, bitte."},
            {"phrase": "Zum Hieressen oder zum Mitnehmen?", "meaning": "на месте или с собой", "example": "Zum Mitnehmen, bitte."},
            {"phrase": "Was macht das?", "meaning": "сколько с меня", "example": "Was macht das zusammen?"},
            {"phrase": "Hafermilch", "meaning": "овсяное молоко", "example": "Haben Sie Hafermilch?"}
        ],
        "teacher_notes": "Germans use polite 'Sie' with strangers, even in cafés. 'Ich hätte gern...' (Konjunktiv II) is more polite than 'Ich will...'."
    },

    "small_talk_de": {
        "title": "Eine neue Person kennenlernen",
        "target_language": "de",
        "goal": "Sich vorstellen, einfache Fragen stellen und das Gespräch am Laufen halten.",
        "situation": "Du triffst nach dem Unterricht einen Studenten aus einem anderen Land. Beginne ein freundliches Gespräch und lernt euch kennen.",
        "example_dialogue": [
            {"speaker": "Du", "text": "Hallo, freut mich. Ich bin Roman."},
            {"speaker": "Andere Person", "text": "Freut mich auch! Woher kommst du?"},
            {"speaker": "Du", "text": "Ich komme aus Russland. Und du?"}
        ],
        "key_phrases": [
            {"phrase": "Freut mich", "meaning": "приятно познакомиться", "example": "Freut mich, dich kennenzulernen."},
            {"phrase": "Woher kommst du?", "meaning": "откуда ты", "example": "Woher kommst du?"},
            {"phrase": "Was studierst du?", "meaning": "что ты изучаешь", "example": "Was studierst du an der Uni?"},
            {"phrase": "Und du?", "meaning": "а ты", "example": "Ich studiere Informatik. Und du?"}
        ],
        "teacher_notes": "Use informal 'du' between students. Note short forms: 'Uni' (university), 'Informatik' (computer science)."
    },

    "hotel_checkin_de": {
        "title": "Hotel-Check-in",
        "target_language": "de",
        "goal": "Im Hotel einchecken, die Reservierung bestätigen und nach Details fragen.",
        "situation": "Du kommst in einem Hotel in Berlin an. Du musst mit der Rezeption sprechen, die Buchung bestätigen und nach praktischen Details fragen.",
        "example_dialogue": [
            {"speaker": "Gast", "text": "Guten Tag, ich habe eine Reservierung auf den Namen Roman Mordovtsev."},
            {"speaker": "Rezeption", "text": "Willkommen. Ihren Ausweis bitte."},
            {"speaker": "Gast", "text": "Bitte schön. Ist das Frühstück inklusive?"}
        ],
        "key_phrases": [
            {"phrase": "Ich habe eine Reservierung auf den Namen...", "meaning": "у меня бронирование на имя...", "example": "Ich habe eine Reservierung auf den Namen Mordovtsev."},
            {"phrase": "Ihren Ausweis bitte", "meaning": "ваш документ, пожалуйста (вежливая форма Sie)", "example": "Ihren Ausweis bitte."},
            {"phrase": "Ist das Frühstück inklusive?", "meaning": "входит ли завтрак", "example": "Ist das Frühstück inklusive?"},
            {"phrase": "Wann muss ich auschecken?", "meaning": "во сколько выезд", "example": "Wann muss ich morgen auschecken?"}
        ],
        "teacher_notes": "Use formal 'Sie' at hotels. 'Ausweis' = ID document (passport for foreigners)."
    },

    "airport_checkin_de": {
        "title": "Check-in am Flughafen",
        "target_language": "de",
        "goal": "Für einen Flug einchecken, Fragen beantworten und über das Gepäck sprechen.",
        "situation": "Du stehst am Check-in-Schalter vor einem internationalen Flug. Du musst einchecken, deinen Pass zeigen und über dein Gepäck sprechen.",
        "example_dialogue": [
            {"speaker": "Passagier", "text": "Guten Tag, ich möchte für meinen Flug einchecken."},
            {"speaker": "Mitarbeiter", "text": "Gerne. Ihren Pass bitte."},
            {"speaker": "Passagier", "text": "Bitte. Kann ich diesen Koffer aufgeben?"}
        ],
        "key_phrases": [
            {"phrase": "Ich möchte für meinen Flug einchecken", "meaning": "я хотел бы зарегистрироваться на рейс", "example": "Ich möchte für meinen Flug nach Berlin einchecken."},
            {"phrase": "Kann ich diesen Koffer aufgeben?", "meaning": "могу ли я сдать этот чемодан в багаж", "example": "Kann ich diesen Koffer aufgeben?"},
            {"phrase": "Fensterplatz", "meaning": "место у окна", "example": "Einen Fensterplatz, bitte."},
            {"phrase": "Bordkarte", "meaning": "посадочный талон", "example": "Hier ist Ihre Bordkarte."}
        ],
        "teacher_notes": "Use formal 'Sie' with airport staff. 'Gepäck aufgeben' = check in baggage; 'Bordkarte' = boarding pass."
    },

    # ========================================================================
    # ITALIANO (Italy)
    # ========================================================================
    "coffee_shop_it": {
        "title": "Bar a Roma",
        "target_language": "it",
        "goal": "Ordinare un caffè con cortesia, chiedere le opzioni e pagare.",
        "situation": "Sei in un bar a Roma. Vuoi ordinare un caffè, chiedere il tipo di latte e completare l'ordine con cortesia.",
        "example_dialogue": [
            {"speaker": "Cliente", "text": "Buongiorno, vorrei un cappuccino, per favore."},
            {"speaker": "Barista", "text": "Certo. Al banco o al tavolo?"},
            {"speaker": "Cliente", "text": "Al banco, grazie."}
        ],
        "key_phrases": [
            {"phrase": "Vorrei...", "meaning": "вежливая форма «я бы хотел» при заказе", "example": "Vorrei un caffè, per favore."},
            {"phrase": "Al banco o al tavolo?", "meaning": "у стойки или за столиком (важно в Италии — цена разная)", "example": "Al banco, grazie."},
            {"phrase": "Quant'è?", "meaning": "сколько с меня", "example": "Quant'è in tutto?"},
            {"phrase": "Latte d'avena", "meaning": "овсяное молоко", "example": "Avete latte d'avena?"}
        ],
        "teacher_notes": "In Italy, drinking at the bar (al banco) is cheaper than at a table (al tavolo). Cappuccino is typically a morning drink."
    },

    "small_talk_it": {
        "title": "Conoscere una persona nuova",
        "target_language": "it",
        "goal": "Presentarti, fare domande semplici e tenere viva la conversazione.",
        "situation": "Incontri uno studente di un altro paese dopo la lezione. Inizia una conversazione amichevole e imparate cose di base l'uno sull'altro.",
        "example_dialogue": [
            {"speaker": "Tu", "text": "Ciao, piacere. Mi chiamo Roman."},
            {"speaker": "Altra persona", "text": "Piacere mio! Di dove sei?"},
            {"speaker": "Tu", "text": "Sono di Russia. E tu?"}
        ],
        "key_phrases": [
            {"phrase": "Piacere", "meaning": "приятно (краткая форма знакомства)", "example": "Piacere, mi chiamo Roman."},
            {"phrase": "Di dove sei?", "meaning": "откуда ты", "example": "Di dove sei?"},
            {"phrase": "Cosa studi?", "meaning": "что ты изучаешь", "example": "Cosa studi all'università?"},
            {"phrase": "E tu?", "meaning": "а ты", "example": "Studio informatica. E tu?"}
        ],
        "teacher_notes": "Use informal 'tu' between students. 'Piacere' alone is enough at first introduction."
    },

    "hotel_checkin_it": {
        "title": "Check-in in hotel",
        "target_language": "it",
        "goal": "Fare il check-in, confermare la prenotazione e fare domande pratiche.",
        "situation": "Arrivi in un hotel a Roma. Devi parlare con il receptionist, confermare la prenotazione e chiedere dettagli pratici sulla camera.",
        "example_dialogue": [
            {"speaker": "Ospite", "text": "Buongiorno, ho una prenotazione a nome Roman Mordovtsev."},
            {"speaker": "Receptionist", "text": "Benvenuto. Il suo passaporto, per favore."},
            {"speaker": "Ospite", "text": "Eccolo. La colazione è inclusa?"}
        ],
        "key_phrases": [
            {"phrase": "Ho una prenotazione a nome...", "meaning": "у меня бронирование на имя...", "example": "Ho una prenotazione a nome Mordovtsev."},
            {"phrase": "Il suo passaporto, per favore", "meaning": "ваш паспорт, пожалуйста (форма Lei)", "example": "Il suo passaporto, per favore."},
            {"phrase": "La colazione è inclusa?", "meaning": "включён ли завтрак", "example": "La colazione è inclusa nel prezzo?"},
            {"phrase": "A che ora è il check-out?", "meaning": "во сколько выезд", "example": "A che ora è il check-out?"}
        ],
        "teacher_notes": "Use formal 'Lei' at hotels (capitalised in writing). 'Colazione' = breakfast."
    },

    "airport_checkin_it": {
        "title": "Check-in in aeroporto",
        "target_language": "it",
        "goal": "Fare il check-in per il volo, rispondere a domande e parlare del bagaglio.",
        "situation": "Sei al banco del check-in prima di un volo internazionale. Devi fare il check-in, mostrare il passaporto e parlare del tuo bagaglio.",
        "example_dialogue": [
            {"speaker": "Passeggero", "text": "Buongiorno, vorrei fare il check-in per il mio volo."},
            {"speaker": "Operatore", "text": "Certo. Il suo passaporto, prego."},
            {"speaker": "Passeggero", "text": "Eccolo. Posso imbarcare questa valigia?"}
        ],
        "key_phrases": [
            {"phrase": "Vorrei fare il check-in per il mio volo", "meaning": "я хотел бы зарегистрироваться на рейс", "example": "Vorrei fare il check-in per il mio volo per Roma."},
            {"phrase": "Posso imbarcare questa valigia?", "meaning": "могу ли я сдать этот чемодан в багаж", "example": "Posso imbarcare questa valigia?"},
            {"phrase": "Posto vicino al finestrino", "meaning": "место у окна", "example": "Un posto vicino al finestrino, per favore."},
            {"phrase": "Carta d'imbarco", "meaning": "посадочный талон", "example": "Ecco la sua carta d'imbarco."}
        ],
        "teacher_notes": "Italian airport vocabulary: imbarcare = check in (baggage), valigia = suitcase, carta d'imbarco = boarding pass."
    },

    # ========================================================================
    # TÜRKÇE (Turkey)
    # ========================================================================
    "coffee_shop_tr": {
        "title": "İstanbul'da kafe",
        "target_language": "tr",
        "goal": "Kibarca bir içecek söylemek, seçenekleri sormak ve hesabı ödemek.",
        "situation": "İstanbul'da bir kafedesin. Bir içecek söylemek, süt çeşidini sormak ve siparişi kibarca tamamlamak istiyorsun.",
        "example_dialogue": [
            {"speaker": "Müşteri", "text": "Merhaba, bir latte alabilir miyim, lütfen?"},
            {"speaker": "Barista", "text": "Tabii. Burada mı içeceksiniz, paket mi?"},
            {"speaker": "Müşteri", "text": "Paket olsun, teşekkürler."}
        ],
        "key_phrases": [
            {"phrase": "...alabilir miyim?", "meaning": "вежливая форма «можно мне...?» при заказе", "example": "Bir kahve alabilir miyim?"},
            {"phrase": "Burada mı, paket mi?", "meaning": "на месте или с собой", "example": "Paket olsun, teşekkürler."},
            {"phrase": "Hesap, lütfen", "meaning": "счёт, пожалуйста", "example": "Hesap, lütfen."},
            {"phrase": "Yulaf sütü", "meaning": "овсяное молоко", "example": "Yulaf sütünüz var mı?"}
        ],
        "teacher_notes": "Common in Istanbul cafés. Note: '-er miyim?' (aorist + question) is the polite request form. 'Kolay gelsin' is friendly to staff when leaving."
    },

    "small_talk_tr": {
        "title": "Yeni biriyle tanışmak",
        "target_language": "tr",
        "goal": "Kendini tanıtmak, basit sorular sormak ve sohbeti sürdürmek.",
        "situation": "Dersten sonra başka bir ülkeden gelen bir öğrenciyle tanışıyorsun. Dostane bir sohbet başlat ve birbiriniz hakkında temel bilgiler öğrenin.",
        "example_dialogue": [
            {"speaker": "Sen", "text": "Merhaba, memnun oldum. Ben Roman."},
            {"speaker": "Diğer kişi", "text": "Ben de memnun oldum! Nerelisin?"},
            {"speaker": "Sen", "text": "Rusyalıyım. Sen nerelisin?"}
        ],
        "key_phrases": [
            {"phrase": "Memnun oldum", "meaning": "приятно познакомиться", "example": "Memnun oldum, ben Roman."},
            {"phrase": "Nerelisin?", "meaning": "откуда ты", "example": "Nerelisin?"},
            {"phrase": "Ne okuyorsun?", "meaning": "что ты изучаешь (в университете)", "example": "Üniversitede ne okuyorsun?"},
            {"phrase": "Sen?", "meaning": "а ты (короткая форма возврата вопроса)", "example": "Bilgisayar mühendisliği okuyorum. Sen?"}
        ],
        "teacher_notes": "Use informal 'sen' between students. 'Nerelisin?' literally means 'where-from-are-you?' as a single suffixed word."
    },

    "hotel_checkin_tr": {
        "title": "Otele giriş",
        "target_language": "tr",
        "goal": "Otele giriş yapmak, rezervasyonu onaylamak ve pratik sorular sormak.",
        "situation": "İstanbul'da bir otele varıyorsun. Resepsiyonla konuşman, rezervasyonunu onaylaman ve oda hakkında pratik soruları sorman gerekiyor.",
        "example_dialogue": [
            {"speaker": "Misafir", "text": "Merhaba, Roman Mordovtsev adına rezervasyonum var."},
            {"speaker": "Resepsiyon", "text": "Hoş geldiniz. Pasaportunuzu rica edebilir miyim?"},
            {"speaker": "Misafir", "text": "Buyurun. Kahvaltı dahil mi?"}
        ],
        "key_phrases": [
            {"phrase": "...adına rezervasyonum var", "meaning": "у меня бронирование на имя...", "example": "Mordovtsev adına rezervasyonum var."},
            {"phrase": "Pasaportunuzu rica edebilir miyim?", "meaning": "могу попросить ваш паспорт? (вежливая форма)", "example": "Pasaportunuzu rica edebilir miyim?"},
            {"phrase": "Kahvaltı dahil mi?", "meaning": "входит ли завтрак", "example": "Kahvaltı dahil mi?"},
            {"phrase": "Çıkış saati kaçta?", "meaning": "во сколько выезд", "example": "Çıkış saati kaçta?"}
        ],
        "teacher_notes": "Use formal '-iniz' suffix (plural/polite) at hotels. 'Hoş geldiniz' (welcome) — guest replies with 'Hoş bulduk'."
    },

    "airport_checkin_tr": {
        "title": "Havalimanında check-in",
        "target_language": "tr",
        "goal": "Uçuş için check-in yapmak, soruları cevaplamak ve bagaj hakkında konuşmak.",
        "situation": "Uluslararası bir uçuştan önce check-in kontuarındasın. Check-in yapman, pasaportunu göstermen ve bagajın hakkında konuşman gerekiyor.",
        "example_dialogue": [
            {"speaker": "Yolcu", "text": "Merhaba, uçuşum için check-in yapmak istiyorum."},
            {"speaker": "Görevli", "text": "Tabii. Pasaportunuz, lütfen."},
            {"speaker": "Yolcu", "text": "Buyurun. Bu valizi bagaja verebilir miyim?"}
        ],
        "key_phrases": [
            {"phrase": "Uçuşum için check-in yapmak istiyorum", "meaning": "я хотел бы зарегистрироваться на рейс", "example": "İstanbul uçuşum için check-in yapmak istiyorum."},
            {"phrase": "Bu valizi bagaja verebilir miyim?", "meaning": "могу ли я сдать этот чемодан в багаж", "example": "Bu valizi bagaja verebilir miyim?"},
            {"phrase": "Cam kenarı koltuk", "meaning": "место у окна", "example": "Cam kenarı koltuk alabilir miyim?"},
            {"phrase": "Biniş kartı", "meaning": "посадочный талон", "example": "Buyurun, biniş kartınız."}
        ],
        "teacher_notes": "Turkey airport vocabulary: bagaj = baggage, valiz = suitcase, biniş kartı = boarding pass, cam kenarı = window side."
    }
}
