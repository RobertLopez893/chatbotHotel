import random
import re
import csv
from datetime import date, timedelta
import locale
import os

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    print("Locale 'es_ES.UTF-8' no encontrado. Las fechas podrían aparecer en inglés.")

intents = {
    "saludos": {
        "patterns": [
            r"(?i)\b(hola|buenas|buen(os)? ?(dias|tardes|noches)|hey|qu[eé] ?(onda|tal|hay|hubo)|q onda|quiubo|inicio|empezar|info)\b"],
        "responses": [
            "¡Hola! Soy el asistente virtual de Fiesta Inn. ¿En qué puedo ayudarte hoy?",
            "¡Qué tal! Bienvenido al asistente de Fiesta Inn. Estoy para servirte.",
            "Hola, gracias por contactarnos. ¿Cómo puedo asistirte?"
        ]
    },
    # --- SECCIÓN DE SMALL TALK ---
    "small_talk_quien_eres": {
        "patterns": [r"(?i)\b(qui[eé]n eres|c[oó]mo te llamas|eres un bot|eres una persona)\b"],
        "responses": [
            "Soy el asistente virtual de Fiesta Inn, un bot programado para ayudarte con tus reservaciones y dudas sobre el hotel.",
            "Soy un chatbot de servicio al cliente del hotel Fiesta Inn. ¡Estoy aquí para asistirte!",
            "Me llamo FiestaBot. Soy un asistente virtual listo para ayudarte."
        ]
    },
    "small_talk_como_estas": {
        "patterns": [r"(?i)\b(c[oó]mo est[aá]s|qu[eé] tal|todo bien|c[oó]mo te va)\b"],
        "responses": [
            "Estoy funcionando a la perfección, ¡gracias por preguntar! ¿En qué puedo ayudarte?",
            "¡Todo excelente! Listo para resolver tus dudas.",
            "Muy bien, gracias. ¿Cómo puedo asistirte hoy?"
        ]
    },
    "small_talk_que_haces": {
        "patterns": [r"(?i)\b(qu[eé] haces|cu[aá]l es tu funci[oó]n|para qu[eé] sirves)\b"],
        "responses": [
            "Estoy aquí para ayudarte a reservar habitaciones, consultar precios, horarios y cualquier otra duda que tengas sobre el hotel Fiesta Inn.",
            "Mi propósito es hacer tu experiencia con Fiesta Inn más fácil, ayudándote con información y reservaciones.",
            "Puedo darte información sobre servicios, ubicación, precios y ayudarte a gestionar una reservación."
        ]
    },
    "recall_name": {
        "patterns": [r"(?i)\b(c[oó]mo me llamo|cu[aá]l es mi nombre|sabes mi nombre|recuerdas mi nombre)\b"],
        "responses_known": [
            "Claro, te llamas {name}.",
            "Si mi memoria no me falla, tu nombre es {name}.",
            "Lo tengo registrado como {name}. ¿Es correcto?",
            "¡Por supuesto! Eres {name}."
        ],
        "responses_unknown": [
            "Mmm, creo que aún no me has dicho tu nombre.",
            "Aún no tengo el placer de saber cómo te llamas. ¿Te gustaría decírmelo?",
            "Lo siento, no tengo tu nombre registrado todavía."
        ]
    },
    "small_talk_agradecimiento": {
        "patterns": [r"(?i)\b(gracias|muy amable|te agradezco|chido|genial|excelente servicio)\b"],
        "responses": [
            "¡De nada! Estoy para servirte.",
            "Con mucho gusto. ¿Hay algo más en lo que pueda ayudarte?",
            "¡Un placer asistirte! No dudes en preguntar si tienes otra duda."
        ]
    },
    "small_talk_chiste": {
        "patterns": [r"(?i)\b(cu[eé]ntame un chiste|dime algo gracioso|un chiste)\b"],
        "responses": [
            "¿Qué le dice un techo a otro? Techo de menos.",
            "¿Por qué las focas miran siempre hacia arriba? ¡Porque ahí están los focos!",
            "¿Cuál es el último animal que subió al arca de Noé? El del-fín.",
            "Van dos en una moto y se cae el de en medio. ¿Cómo es posible? ¡Porque era la moto de su vida!"
        ]
    },
    "fallback": {
        "patterns": [],
        "responses": [
            "Disculpa, no he entendido tu solicitud. ¿Podrías intentar con otras palabras?",
            "Lo siento, no estoy seguro de cómo ayudarte con eso. ¿Puedes ser más específico?",
            "No comprendí tu mensaje. Intenta preguntarme de otra forma, por ejemplo, 'quiero reservar'."
        ]
    },
    "reservas": {
        "patterns": [r"(?i)\b(reservar|quiero una habitación|necesito un cuarto|hacer una reservaci[oó]n)\b"],
    },
    "manage_reservation": {"patterns": [
        r"(?i)\b(modificar|cambiar|consultar|ver|eliminar|cancelar)\s.*reservaci[oó]n|mi reserva|mi estancia\b"], },
    "capture_folio": {"patterns": [r"(R\d{5})"], },
    "no_folio": {"patterns": [r"(?i)no tengo folio|no lo tengo|sin folio"], },
    "affirmative": {
        "patterns": [
            r"(?i)\b(s[ií]|correcto|confirma|acepto|smn|simon|claro|por supuesto|adelante|sep|sip|efectivamente|as[ií] es)\b"],
    },
    "negative_simple": {
        "patterns": [r"(?i)\b(no|nop|nel|para nada|incorrecto)\b"],
    },
    "cancel_action": {
        "patterns": [r"(?i)\b(cancela|cancelar|detén|ya no|mejor no|olvídalo)\b"],
    },
    "capture_number": {
        "patterns": [r"\b(\d+)\b"],
    },
    "capture_room_type": {
        "patterns": [r"(?i)(sencilla|doble|suite)"],
    },
    "capture_full_name": {"patterns": [r"(?i)([A-ZÁÉÍÓÚÑ][a-zñáéíóú]+(?:\s[A-ZÁÉÍÓÚÑ][a-zñáéíóú]+)+)"]},
    "capture_email": {"patterns": [r"([\w\.-]+@[\w\.-]+\.\w{2,})"]},
    "capture_phone": {"patterns": [r"^\s*(\d{2}[-.\s]?\d{4}[-.\s]?\d{4})\s*$"]},
    "precios": {
        "patterns": [r"(?i)\b(precio|cu[aá]nto cuesta|tarifa[s]?|costo)\b"],
        "responses": [
            "Nuestras tarifas varían según la fecha y el tipo de habitación. ¿Te interesa una habitación Sencilla o Doble para darte un estimado?",
            "Los costos pueden cambiar, pero con gusto te doy información. ¿Buscas algún tipo de habitación en particular?"
        ]
    },
    "checkin_checkout": {
        "patterns": [r"(?i)\b(check-?in|check-?out|entrada|salida|horario)\b"],
        "responses": [
            "El check-in es a las 3:00 PM y el check-out es a la 1:00 PM.",
            "La hora de entrada es a las 15:00 y la salida a las 13:00. Avísame si tienes otra duda."
        ]
    },
    "servicios": {
        "patterns": [r"(?i)\b(servicios|qu[eé] ofrece|amenidades)\b"],
        "responses": [
            "Contamos con Wi-Fi, gimnasio, restaurante y más. ¿Te gustaría saber sobre alguno en particular?",
            "Ofrecemos una amplia gama de servicios para tu comodidad. ¿Hay algo específico que te interese?"
        ]
    },
    "ubicacion": {
        "patterns": [r"(?i)\b(ubicaci[oó]n|direcci[oó]n|d[oó]nde est[aá]n|sucursal)\b"],
        "responses": [
            "¡Con gusto! Para darte la dirección del Fiesta Inn más cercano, ¿podrías decirme en qué ciudad te encuentras?",
            "Claro, para ayudarte a encontrarnos, ¿me puedes indicar tu ciudad o colonia de interés?"
        ]
    },
    "capture_name": {
        "patterns": [
            r"(?i)(?:mi nombre es|me llamo|soy)\s+([A-ZÁÉÍÓÚÑ][a-zñáéíóú]+)"
        ],
        "responses": [
            "¡Mucho gusto, {name}!",
            "¡Entendido, {name}!",
            "¡Anotado, {name}! Gracias."
        ]
    },
    "despedida": {
        "patterns": [r"(?i)\b(gracias|adi[oó]s|hasta luego|bye|eso es todo|no gracias)\b"],
        "responses": [
            "Ha sido un placer atenderle. ¡Le deseamos un viaje exitoso!",
            "Gracias a ti. Si necesitas algo más, no dudes en preguntar. ¡Hasta pronto!",
            "Perfecto. Que tengas un excelente día. ¡Vuelve pronto!"
        ]
    }
}

states = {
    "GENERAL": "GENERAL", "END": "END",
    "AWAITING_CHECKIN": "AWAITING_CHECKIN",
    "AWAITING_CHECKOUT": "AWAITING_CHECKOUT",
    "AWAITING_ADULTS": "AWAITING_ADULTS",
    "AWAITING_CHILDREN": "AWAITING_CHILDREN",
    "AWAITING_ROOM_CHOICE": "AWAITING_ROOM_CHOICE",
    "AWAITING_GUEST_NAME": "AWAITING_GUEST_NAME",
    "AWAITING_GUEST_EMAIL": "AWAITING_GUEST_EMAIL",
    "AWAITING_GUEST_PHONE": "AWAITING_GUEST_PHONE",
    "AWAITING_CONFIRMATION": "AWAITING_CONFIRMATION",
    "MANAGE_AWAITING_FOLIO": "MANAGE_AWAITING_FOLIO",
    "MANAGE_AWAITING_NAME": "MANAGE_AWAITING_NAME",
    "MANAGE_AWAITING_EMAIL": "MANAGE_AWAITING_EMAIL",
    "MANAGE_SHOWING_OPTIONS": "MANAGE_SHOWING_OPTIONS",
    "MANAGE_CONFIRM_DELETE": "MANAGE_CONFIRM_DELETE",
}


def parse_relative_date(text: str) -> date | None:
    today = date.today()
    text = text.lower()

    if "mañana" in text:
        return today + timedelta(days=2) if "pasado" in text else today + timedelta(days=1)

    weekdays = {"lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3, "viernes": 4, "sábado": 5, "domingo": 6}
    for day_name, day_index in weekdays.items():
        if day_name in text:
            days_ahead = day_index - today.weekday()
            if days_ahead <= 0: days_ahead += 7
            return today + timedelta(days=days_ahead)

    months = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
              'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}
    match = re.search(r"(\d{1,2})(?: de (\w+))?", text)
    if match:
        day = int(match.group(1))
        month_name = match.group(2)
        month = months.get(month_name, today.month) if month_name else today.month
        year = today.year

        if date(year, month, day) < today:
            year += 1

        try:
            return date(year, month, day)
        except ValueError:
            return None
    return None


def convertir_palabra_a_numero(palabra: str) -> int | None:
    numeros = {'cero': 0, 'un': 1, 'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5, 'seis': 6, 'siete': 7,
               'ocho': 8, 'nueve': 9, 'diez': 10}
    # Busca la palabra en la frase
    for palabra_clave, valor in numeros.items():
        if palabra_clave in palabra.lower():
            return valor
    return None


def save_reservation_to_csv(details: dict):
    filepath = "reservaciones.csv"
    fieldnames = ['folio', 'nombre_huesped', 'email', 'telefono', 'check_in', 'check_out', 'adultos', 'ninos',
                  'tipo_habitacion']
    try:
        with open(filepath, 'a+', newline='', encoding='utf-8') as csvfile:
            csvfile.seek(0)
            is_empty = not csvfile.read(1)
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if is_empty: writer.writeheader()
            writer.writerow({
                'folio': details.get('folio'), 'nombre_huesped': details.get('guest_name'),
                'email': details.get('email'), 'telefono': details.get('phone'),
                'check_in': details.get('check_in').strftime('%Y-%m-%d'),
                'check_out': details.get('check_out').strftime('%Y-%m-%d'),
                'adultos': details.get('adults'), 'ninos': details.get('children'),
                'tipo_habitacion': details.get('room')
            })
    except IOError:
        print("Error: No se pudo guardar la reservación.")


RESERVATIONS_FILE = "reservaciones.csv"
FIELDNAMES = ['folio', 'nombre_huesped', 'email', 'telefono', 'check_in', 'check_out', 'adultos', 'ninos',
              'tipo_habitacion']


def find_reservations(folio=None, nombre=None, email=None):
    if not os.path.exists(RESERVATIONS_FILE): return []
    with open(RESERVATIONS_FILE, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        results = []
        for row in reader:
            if folio and row['folio'].lower() == folio.lower():
                results.append(row)
            elif nombre and nombre.lower() in row['nombre_huesped'].lower():
                if email and email.lower() == row['email'].lower():
                    results.append(row)
                elif not email:
                    results.append(row)
    return results


def update_reservations_file(reservations_list):
    with open(RESERVATIONS_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(reservations_list)


class ChatBot:
    def __init__(self):
        self.state = states["GENERAL"]
        self.user_name = None
        self.reservation_details = {}

    def find_match(self, user_message):
        if self.state == "AWAITING_GUEST_EMAIL": return "capture_email", user_message
        if self.state == "AWAITING_GUEST_PHONE": return "capture_phone", user_message
        if self.state == "AWAITING_GUEST_NAME": return "capture_full_name", user_message

        if self.state == "GENERAL":
            if match := re.search(intents['capture_name']['patterns'][0], user_message, re.IGNORECASE):
                return "capture_name", match.group(1)

        if self.state == "AWAITING_ROOM_CHOICE":
            if any(word in user_message.lower() for word in ["sencilla", "doble", "suite"]):
                return "capture_room_type", re.search(r"(sencilla|doble|suite)", user_message.lower()).group(1)

        if self.state in ["AWAITING_ADULTS", "AWAITING_CHILDREN"]:
            if match := re.search(r"\b(\d+)\b", user_message):
                return "capture_number_digit", match.group(1)
            if match := re.search(r"(?i)\b(cero|un|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\b",
                                  user_message):
                return "capture_number_word", match.group(0)

        for intent, data in intents.items():
            for pattern in data.get("patterns", []):
                if match := re.search(pattern, user_message, re.IGNORECASE):
                    return intent, match.group(1) if match.groups() else match.group(0)
        return "fallback", None

    def handle_reservation_flow(self, intent, matched_value, user_input):
        if self.state == states["AWAITING_CHECKIN"]:
            parsed_date = parse_relative_date(user_input)
            if not parsed_date or parsed_date < date.today():
                return "Esa fecha no es válida. Por favor, dime una fecha de llegada futura (como 'mañana' o 'el próximo sábado')."
            self.reservation_details["check_in"] = parsed_date
            self.state = states["AWAITING_CHECKOUT"]
            return f"Entendido, llegada el {parsed_date.strftime('%A %d de %B')}. Ahora, ¿cuál sería tu fecha de salida?"

        elif self.state == states["AWAITING_CHECKOUT"]:
            parsed_date = parse_relative_date(user_input)
            if not parsed_date or parsed_date <= self.reservation_details["check_in"]:
                return "La fecha de salida debe ser posterior a la de llegada. Por favor, dime una fecha de salida válida."
            self.reservation_details["check_out"] = parsed_date
            self.state = states["AWAITING_ADULTS"]
            return f"Perfecto. Tu estancia es del {self.reservation_details['check_in'].strftime('%d de %B')} al {parsed_date.strftime('%d de %B')}. ¿Cuántos adultos se hospedarán?"

        elif self.state == states["AWAITING_ADULTS"]:
            numero = None
            if intent == "capture_number_digit":
                numero = matched_value
            elif intent == "capture_number_word":
                numero = convertir_palabra_a_numero(matched_value)
            if numero is not None:
                self.reservation_details["adults"] = str(numero)
                self.state = states["AWAITING_CHILDREN"]
                return f"Anotado, {numero} adultos. ¿Viaja algún niño? (Si no, simplemente di 'no')."
            return "No entendí el número. ¿Podrías decirlo de nuevo?"

        elif self.state == states["AWAITING_CHILDREN"]:
            numero_ninos = "0"
            if intent == "capture_number_digit":
                numero_ninos = matched_value
            elif intent == "capture_number_word":
                numero_ninos = str(convertir_palabra_a_numero(matched_value))
            elif intent == "negative_simple":
                numero_ninos = "0"
            self.reservation_details["children"] = numero_ninos
            self.state = states["AWAITING_ROOM_CHOICE"]
            return "Gracias. Tenemos: 1. Sencilla, 2. Doble, 3. Suite. ¿Cuál prefieres?"

        elif self.state == states["AWAITING_ROOM_CHOICE"]:
            room_options = {"1": "Habitación Sencilla", "2": "Habitación Doble", "3": "Suite",
                            "sencilla": "Habitación Sencilla", "doble": "Habitación Doble", "suite": "Suite"}
            room_selection = re.search(r"(sencilla|doble|suite|\d+)", user_input.lower())
            if room_selection and room_options.get(room_selection.group(0)):
                self.reservation_details["room"] = room_options.get(room_selection.group(0))
                if self.user_name:
                    self.reservation_details['guest_name'] = self.user_name
                    self.state = states["AWAITING_GUEST_EMAIL"]
                    return f"Perfecto, usaré el nombre {self.user_name} para la reserva. Ahora, ¿a qué correo electrónico enviamos la confirmación?"
                else:
                    self.state = states["AWAITING_GUEST_NAME"]
                    return "¡Muy bien! Ya casi terminamos. ¿A nombre de quién hago la reservación (nombre y apellido)?"
            else:
                return "No reconocí esa opción. Por favor, elige una de las habitaciones."
        elif self.state == states["AWAITING_GUEST_NAME"]:
            self.reservation_details['guest_name'] = user_input
            self.user_name = user_input.split()[0]
            self.state = states["AWAITING_GUEST_EMAIL"]
            return f"Gracias, {self.user_name}. Ahora, ¿cuál es tu correo electrónico?"
        elif self.state == states["AWAITING_GUEST_EMAIL"]:
            email_match = re.search(r"([\w\.-]+@[\w\.-]+\.\w{2,})", user_input)
            if email_match:
                self.reservation_details['email'] = email_match.group(0)
                self.state = states["AWAITING_GUEST_PHONE"]
                return "Correo guardado. Por último, ¿nos podrías dar un número de teléfono de contacto?"
            else:
                return "Ese correo no parece válido. ¿Podrías verificarlo?"

        elif self.state == states["AWAITING_GUEST_PHONE"]:
            phone_match = re.search(r"^\s*(\d{2}[-.\s]?\d{4}[-.\s]?\d{4})\s*$", user_input)
            if phone_match:
                self.reservation_details['phone'] = phone_match.group(0)
                self.state = states["AWAITING_CONFIRMATION"]

                if 'guest_name' not in self.reservation_details: self.reservation_details['guest_name'] = self.user_name

                summary = f"""¡Excelente! Revisa por última vez que todo esté en orden:
        👤 Nombre: {self.reservation_details['guest_name']}
        📧 Email: {self.reservation_details['email']}
        📞 Teléfono: {self.reservation_details['phone']}
        🏨 Habitación: {self.reservation_details['room']}
        📅 Check-in: {self.reservation_details['check_in'].strftime('%A, %d de %B de %Y')}
        📅 Check-out: {self.reservation_details['check_out'].strftime('%A, %d de %B de %Y')}
    ¿Confirmo la reservación?"""
                return summary
            else:
                return "No parece un número de teléfono válido. Intenta de nuevo, por favor."
        elif self.state == states["AWAITING_CONFIRMATION"]:
            intent, _ = self.find_match(user_input)
            if intent == "affirmative":
                folio = f"R{random.randint(10000, 99999)}"
                self.reservation_details['folio'] = folio
                guest_name_final = self.reservation_details.get('guest_name')
                save_reservation_to_csv(self.reservation_details)
                self.state, self.reservation_details = states["GENERAL"], {}
                return f"¡Listo! Tu reservación a nombre de {guest_name_final} está confirmada con el folio {folio}. ¡Gracias por tu preferencia!"
            else:
                self.state, self.reservation_details = states["GENERAL"], {}
                return "Entendido. He cancelado el proceso."

    def handle_management_flow(self, user_input):
        intent, matched_value = self.find_match(user_input)

        if self.state == states["MANAGE_AWAITING_FOLIO"]:
            if intent == "capture_folio":
                self.found_reservations = find_reservations(folio=matched_value)
                if len(self.found_reservations) == 1:
                    self.active_reservation_folio = self.found_reservations[0]['folio']
                    self.state = states["MANAGE_SHOWING_OPTIONS"]
                    res = self.found_reservations[0]
                    return f"""¡Reservación encontrada!
        👤 Nombre: {res['nombre_huesped']}
        📧 Email: {res['email']}
        📞 Teléfono: {res['telefono']}
        📅 Fechas: Del {res['check_in']} al {res['check_out']}
    ¿Qué deseas hacer?
        1. Modificar
        2. Eliminar"""
                else:
                    self.state = states["MANAGE_AWAITING_NAME"]
                    return "No encontré ese folio. Intentemos con tu nombre. ¿A nombre de quién está la reservación?"
            elif intent == "no_folio":
                self.state = states["MANAGE_AWAITING_NAME"]
                return "No hay problema. ¿A nombre de quién está la reservación?"
            else:
                return "Por favor, dime un número de folio (ej. R12345) o di 'no tengo folio'."

        elif self.state == states["MANAGE_AWAITING_NAME"]:
            self.found_reservations = find_reservations(nombre=user_input)
            if len(self.found_reservations) == 0:
                return "No encontré reservaciones a ese nombre. ¿Quieres intentar con otro nombre?"
            elif len(self.found_reservations) == 1:
                self.active_reservation_folio = self.found_reservations[0]['folio']
                self.state = states["MANAGE_SHOWING_OPTIONS"]
                res = self.found_reservations[0]
                return f"""¡Reservación encontrada!
        👤 Nombre: {res['nombre_huesped']}
        ... (etc.)
    ¿Qué deseas hacer? (1. Modificar, 2. Eliminar)"""
            else:
                self.state = states["MANAGE_AWAITING_EMAIL"]
                return "Encontré varias reservaciones con ese nombre. Para confirmar, ¿cuál es tu correo electrónico?"

        elif self.state == states["MANAGE_AWAITING_EMAIL"]:
            # ... (Lógica para desempatar con email)
            return "WIP: desempate por email"

        elif self.state == states["MANAGE_SHOWING_OPTIONS"]:
            if "eliminar" in user_input.lower() or "2" in user_input:
                self.state = states["MANAGE_CONFIRM_DELETE"]
                return "¿Estás seguro de que quieres ELIMINAR tu reservación? Esta acción no se puede deshacer."
            elif "modificar" in user_input.lower() or "1" in user_input:
                self.state = states["GENERAL"]
                return "La función para modificar reservaciones aún está en desarrollo. Te regreso al menú principal."
            else:
                return "Por favor, elige una opción válida: 1. Modificar o 2. Eliminar."

        elif self.state == states["MANAGE_CONFIRM_DELETE"]:
            if intent == "affirmative":
                all_reservations = find_reservations()
                reservations_to_keep = [res for res in all_reservations if
                                        res['folio'] != self.active_reservation_folio]
                update_reservations_file(reservations_to_keep)
                self.state = states["GENERAL"]
                return f"Listo. La reservación con folio {self.active_reservation_folio} ha sido eliminada. ¿Te puedo ayudar en algo más?"
            else:
                self.state = states["GENERAL"]
                return "De acuerdo, no se ha eliminado nada. Regresando al menú principal."

    def handle_message(self, user_input):
        intent, matched_value = self.find_match(user_input)

        if intent == "cancel_action" and self.state.startswith("AWAITING"):
            self.state, self.reservation_details = states["GENERAL"], {}
            return "Proceso de reservación cancelado. ¿Te puedo ayudar con otra cosa?"

        if self.state.startswith("AWAITING"):
            return self.handle_reservation_flow(intent, matched_value, user_input)

        if self.state.startswith("MANAGE"):
            return self.handle_management_flow(user_input)

            # --- LÓGICA GENERAL ---
        if intent == "reservas":
            self.state, self.reservation_details = states["AWAITING_CHECKIN"], {}
            return "¡Claro! Empecemos. ¿Para qué fecha sería tu llegada (check-in)?"

        if intent == "manage_reservation":
            self.state = states["MANAGE_AWAITING_FOLIO"]
            return "Con gusto te ayudo a gestionar tu reservación. Por favor, dime tu número de folio (ej. R12345), o di 'no tengo folio'."

        if intent == "capture_name": self.user_name = matched_value.capitalize(); return f"¡Mucho gusto, {self.user_name}!"
        if intent == "recall_name": return f"Claro, te llamas {self.user_name}." if self.user_name else "Aún no me has dicho tu nombre."
        if intent == "despedida": self.state = states["END"]; return random.choice(intents["despedida"]["responses"])
        if intent in intents and "responses" in intents.get(intent, {}): return random.choice(
            intents[intent]["responses"])
        return random.choice(intents["fallback"]["responses"])


welcome_menu = """
Bot: ¡Hola! Soy FiestaBot, tu asistente virtual de Fiesta Inn.
---------------------------------------------------------
Puedo ayudarte con lo siguiente:

    🏨 Reservar una habitación
    💰 Consultar precios y tarifas
    🛎️ Horarios de Check-in y Check-out
    🏊 Ver servicios y amenidades
    📍 Encontrar un hotel

Escribe lo que necesites o elige una opción.
---------------------------------------------------------
"""

bot = ChatBot()
print(welcome_menu)

while True:
    user_input = input("Tú: ")
    response = bot.handle_message(user_input)
    print(f"Bot: {response}")

    if bot.state == states["END"]:
        break
