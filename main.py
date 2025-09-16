import random
import re
import csv
from datetime import date, timedelta, datetime
import locale
import os

# --- CONFIGURACIÓN DE IDIOMA ---
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    print("Locale 'es_ES.UTF-8' no encontrado. Las fechas podrían aparecer en inglés.")

# --- PRECIOS ---
PRECIOS_POR_NOCHE = {
    "Sencilla": 1500,
    "Doble": 2200,
    "Suite": 3500
}

# --- LISTA DE DESTINOS VÁLIDOS ---
ESTADOS_DE_MEXICO = [
    "aguascalientes", "baja california", "baja california sur", "campeche",
    "chiapas", "chihuahua", "coahuila", "colima", "ciudad de méxico", "cdmx",
    "durango", "guanajuato", "guerrero", "hidalgo", "jalisco", "méxico",
    "michoacán", "morelos", "nayarit", "nuevo león", "oaxaca", "puebla",
    "querétaro", "quintana roo", "san luis potosí", "sinaloa", "sonora",
    "tabasco", "tamaulipas", "tlaxcala", "veracruz", "yucatán", "zacatecas"
]

# --- INTENTS ---
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
        r"(?i)\b(modificar|cambiar|consultar|ver|eliminar|cancelar|gestionar).*(reserva|reservaci[oó]n|estancia)\b"], },
    "capture_folio": {"patterns": [r"(R\d{5})"], },
    "no_folio": {"patterns": [r"(?i)no\s?tengo"], },
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
    "capture_number": {"patterns": [r"\b(\d+)\b"], },
    "capture_room_type": {"patterns": [r"(?i)(sencilla|doble|suite)"], },
    "capture_full_name": {"patterns": [r"(?i)([A-ZÁÉÍÓÚÑ][a-zñáéíóú]+(?:\s[A-ZÁÉÍÓÚÑ][a-zñáéíóú]+)+)"]},
    "capture_email": {"patterns": [r"([\w\.-]+@[\w\.-]+\.\w{2,})"]},
    "capture_phone": {"patterns": [r"^\s*(\d{2}[-.\s]?\d{4}[-.\s]?\d{4})\s*$"]},

    # #############################################################################
    # #####                     INICIO DE LA MEJORA                           #####
    # #############################################################################
    "precios": {
        "patterns": [r"(?i)\b(precio|cu[aá]nto cuesta|tarifa[s]?|costo)\b"],
        # Se eliminan las respuestas estáticas para manejarlo con una función
    },
    # #############################################################################
    # #####                       FIN DE LA MEJORA                            #####
    # #############################################################################

    "checkin_checkout": {
        "patterns": [r"(?i)\b(check-?in|check-out|entrada|salida|horario)\b"],
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

# --- ESTADOS DEL CHATBOT ---
states = {
    "GENERAL": "GENERAL", "END": "END",
    # Flujo de precios
    "PRICE_INQUIRY_POST": "PRICE_INQUIRY_POST",
    # Flujo de creación de reserva
    "AWAITING_STATE": "AWAITING_STATE",
    "AWAITING_CHECKIN": "AWAITING_CHECKIN",
    "AWAITING_CHECKOUT": "AWAITING_CHECKOUT",
    "AWAITING_ADULTS": "AWAITING_ADULTS",
    "AWAITING_CHILDREN": "AWAITING_CHILDREN",
    "AWAITING_ROOM_CHOICE": "AWAITING_ROOM_CHOICE",
    "AWAITING_NUM_ROOMS": "AWAITING_NUM_ROOMS",
    "AWAITING_GUEST_NAME": "AWAITING_GUEST_NAME",
    "AWAITING_GUEST_EMAIL": "AWAITING_GUEST_EMAIL",
    "AWAITING_GUEST_PHONE": "AWAITING_GUEST_PHONE",
    "AWAITING_CONFIRMATION": "AWAITING_CONFIRMATION",
    # Flujo de gestión de reserva
    "MANAGE_AWAITING_FOLIO": "MANAGE_AWAITING_FOLIO",
    "MANAGE_AWAITING_NAME": "MANAGE_AWAITING_NAME",
    "MANAGE_AWAITING_EMAIL": "MANAGE_AWAITING_EMAIL",
    "MANAGE_SHOWING_OPTIONS": "MANAGE_SHOWING_OPTIONS",
    "MANAGE_CONFIRM_DELETE": "MANAGE_CONFIRM_DELETE",
    # Sub-flujo de MODIFICACIÓN
    "MODIFY_CHOOSING_FIELD": "MODIFY_CHOOSING_FIELD",
    "MODIFY_AWAITING_NEW_STATE": "MODIFY_AWAITING_NEW_STATE",
    "MODIFY_AWAITING_NEW_CHECKIN": "MODIFY_AWAITING_NEW_CHECKIN",
    "MODIFY_AWAITING_NEW_CHECKOUT": "MODIFY_AWAITING_NEW_CHECKOUT",
    "MODIFY_AWAITING_NEW_ADULTS": "MODIFY_AWAITING_NEW_ADULTS",
    "MODIFY_AWAITING_NEW_CHILDREN": "MODIFY_AWAITING_NEW_CHILDREN",
    "MODIFY_AWAITING_NEW_ROOM": "MODIFY_AWAITING_NEW_ROOM",
    "MODIFY_AWAITING_NEW_NUM_ROOMS": "MODIFY_AWAITING_NEW_NUM_ROOMS",
    "MANAGE_POST_MODIFY_OPTIONS": "MANAGE_POST_MODIFY_OPTIONS",
}


# --- FUNCIONES AUXILIARES ---
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

        try:
            parsed_date = date(year, month, day)
            if parsed_date < today:
                return date(year + 1, month, day)
            return parsed_date
        except ValueError:
            return None
    return None


def convertir_palabra_a_numero(palabra: str) -> int | None:
    numeros = {'cero': 0, 'un': 1, 'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5, 'seis': 6, 'siete': 7,
               'ocho': 8, 'nueve': 9, 'diez': 10}
    palabra_lower = palabra.lower()
    for palabra_clave, valor in numeros.items():
        if palabra_clave in palabra_lower:
            return valor
    return None


def get_number_from_input(user_input: str) -> int | None:
    if match := re.search(r"\b(\d+)\b", user_input):
        return int(match.group(1))
    return convertir_palabra_a_numero(user_input)


def calculate_total_cost(check_in, check_out, room_type, num_rooms):
    if isinstance(check_in, str):
        check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
    if isinstance(check_out, str):
        check_out = datetime.strptime(check_out, '%Y-%m-%d').date()

    num_nights = (check_out - check_in).days
    price_per_night = PRECIOS_POR_NOCHE.get(room_type, 0)
    total_cost = num_nights * price_per_night * int(num_rooms)
    return total_cost


# --- MANEJO DE ARCHIVO CSV ---
RESERVATIONS_FILE = "reservaciones.csv"
FIELDNAMES = ['folio', 'nombre_huesped', 'email', 'telefono', 'estado', 'check_in', 'check_out',
              'adultos', 'ninos', 'tipo_habitacion', 'num_habitaciones', 'costo_total']


def save_reservation_to_csv(details: dict):
    filepath = RESERVATIONS_FILE
    fieldnames = FIELDNAMES
    file_exists = os.path.isfile(filepath) and os.path.getsize(filepath) > 0
    try:
        with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(details)
    except IOError as e:
        print(f"Error al guardar la reservación: {e}")


def find_reservations(folio=None, nombre=None, email=None):
    if not os.path.exists(RESERVATIONS_FILE):
        return []

    try:
        with open(RESERVATIONS_FILE, 'r', newline='', encoding='utf-8') as csvfile:
            all_rows = list(csv.DictReader(csvfile))
            if not folio and not nombre and not email:
                return all_rows

            results = []
            for row in all_rows:
                match_folio = folio and row.get('folio', '').lower() == folio.lower()
                match_name = nombre and nombre.lower() in row.get('nombre_huesped', '').lower()

                if match_folio:
                    results.append(row)
                    continue

                if match_name:
                    if email:
                        if email.lower() == row.get('email', '').lower():
                            results.append(row)
                    else:
                        results.append(row)
            return results
    except (IOError, FileNotFoundError, StopIteration):
        return []


def update_reservations_file(reservations_list):
    try:
        with open(RESERVATIONS_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(reservations_list)
    except IOError as e:
        print(f"Error al actualizar el archivo de reservaciones: {e}")


# --- CLASE PRINCIPAL DEL CHATBOT ---
class ChatBot:
    def __init__(self):
        self.state = states["GENERAL"]
        self.user_name = None
        self.reservation_details = {}
        self.active_reservation = None
        self.found_reservations = []
        self.temp_data = {}

    def find_match(self, user_message):
        if self.state in ["AWAITING_GUEST_EMAIL", "MANAGE_AWAITING_EMAIL"]: return "capture_email", user_message
        if self.state == "AWAITING_GUEST_PHONE": return "capture_phone", user_message
        if self.state == "AWAITING_GUEST_NAME": return "capture_full_name", user_message
        if self.state == "GENERAL" and (
                match := re.search(intents['capture_name']['patterns'][0], user_message, re.IGNORECASE)):
            return "capture_name", match.group(1)
        if self.state in ["AWAITING_ROOM_CHOICE", "PRICE_INQUIRY_POST"] and (
                match := re.search(r"(sencilla|doble|suite)", user_message.lower())):
            return "capture_room_type", match.group(1)
        if self.state in ["AWAITING_ADULTS", "AWAITING_CHILDREN", "AWAITING_NUM_ROOMS",
                          "MODIFY_AWAITING_NEW_ADULTS", "MODIFY_AWAITING_NEW_CHILDREN",
                          "MODIFY_AWAITING_NEW_NUM_ROOMS"]:
            if (num := get_number_from_input(user_message)) is not None:
                return "capture_number", num

        for intent, data in intents.items():
            for pattern in data.get("patterns", []):
                if match := re.search(pattern, user_message, re.IGNORECASE):
                    return intent, match.group(1) if match.groups() else match.group(0)
        return "fallback", None

    def _build_reservation_summary(self, res_dict):
        try:
            check_in_str = res_dict.get('check_in')
            check_out_str = res_dict.get('check_out')

            if isinstance(check_in_str, date):
                check_in_fmt = check_in_str.strftime('%A, %d de %B de %Y')
            else:
                check_in_fmt = datetime.strptime(check_in_str, '%Y-%m-%d').strftime('%A, %d de %B de %Y')

            if isinstance(check_out_str, date):
                check_out_fmt = check_out_str.strftime('%A, %d de %B de %Y')
            else:
                check_out_fmt = datetime.strptime(check_out_str, '%Y-%m-%d').strftime('%A, %d de %B de %Y')

            costo_total_str = f"${float(res_dict.get('costo_total', 0)):,.2f} MXN"

            return f"""
    Folio: {res_dict.get('folio', 'N/A')}
    👤 Nombre: {res_dict.get('nombre_huesped', 'N/A')}
    📧 Email: {res_dict.get('email', 'N/A')}
    📞 Teléfono: {res_dict.get('telefono', 'N/A')}
    📍 Destino: {res_dict.get('estado', 'N/A')}
    🏨 Habitación: {res_dict.get('tipo_habitacion', 'N/A')} (x{res_dict.get('num_habitaciones', 'N/A')})
    👥 Adultos: {res_dict.get('adultos', 'N/A')}, Niños: {res_dict.get('ninos', 'N/A')}
    ➡️ Check-in: {check_in_fmt}
    ⬅️ Check-out: {check_out_fmt}
    💰 Costo Total Estimado: {costo_total_str}"""
        except (ValueError, TypeError) as e:
            return f"\nError al mostrar resumen: {e}. Datos brutos: {res_dict}"

    def _recalculate_and_save_active_reservation(self):
        self.active_reservation['costo_total'] = calculate_total_cost(
            self.active_reservation['check_in'],
            self.active_reservation['check_out'],
            self.active_reservation['tipo_habitacion'],
            self.active_reservation['num_habitaciones']
        )
        all_reservations = find_reservations()
        updated_list = [self.active_reservation if res['folio'] == self.active_reservation['folio'] else res for res in
                        all_reservations]
        update_reservations_file(updated_list)

        self.state = states["MANAGE_POST_MODIFY_OPTIONS"]
        summary = self._build_reservation_summary(self.active_reservation)
        return f"¡Listo! He actualizado tu reservación. Aquí están los nuevos datos:\n{summary}\n\n¿Deseas modificar algo más? (sí/no)"

    def handle_price_flow(self, intent, matched_value, user_input):
        if self.state == states["PRICE_INQUIRY_POST"]:
            if intent == "affirmative":
                self.state = states["AWAITING_STATE"]
                self.reservation_details = {}
                return "¡Excelente! Comencemos. ¿Para qué estado de la república te gustaría reservar?"
            elif intent == "negative_simple":
                self.state = states["GENERAL"]
                return "Entendido. ¿Hay algo más en lo que pueda ayudarte?"
            else:
                return "Disculpa, no entendí. ¿Te gustaría que iniciemos una reservación? (sí/no)"
        return random.choice(intents["fallback"]["responses"])

    def handle_reservation_flow(self, intent, matched_value, user_input):
        if self.state == states["AWAITING_STATE"]:
            normalized_input = user_input.lower()
            if normalized_input in ESTADOS_DE_MEXICO:
                self.reservation_details["estado"] = user_input.title()
                self.state = states["AWAITING_CHECKIN"]
                return "¡Perfecto! Ahora, ¿para qué fecha sería tu llegada (check-in)?"
            else:
                return "Lo siento, ese no es un estado válido en México. Por favor, intenta de nuevo."
        elif self.state == states["AWAITING_CHECKIN"]:
            parsed_date = parse_relative_date(user_input)
            if not parsed_date or parsed_date < date.today():
                return "Esa fecha no es válida. Por favor, dime una fecha de llegada futura."
            self.reservation_details["check_in"] = parsed_date
            self.state = states["AWAITING_CHECKOUT"]
            return f"Entendido, llegada el {parsed_date.strftime('%A %d de %B')}. ¿Cuál sería tu fecha de salida?"

        elif self.state == states["AWAITING_CHECKOUT"]:
            parsed_date = parse_relative_date(user_input)
            if not parsed_date or parsed_date <= self.reservation_details["check_in"]:
                return "La fecha de salida debe ser posterior a la de llegada."
            self.reservation_details["check_out"] = parsed_date
            self.state = states["AWAITING_ADULTS"]
            return f"Perfecto. Tu estancia es del {self.reservation_details['check_in'].strftime('%d de %B')} al {parsed_date.strftime('%d de %B')}. ¿Cuántos adultos se hospedarán?"

        elif self.state == states["AWAITING_ADULTS"]:
            if intent == "capture_number":
                self.reservation_details["adultos"] = str(matched_value)
                self.state = states["AWAITING_CHILDREN"]
                return f"Anotado, {matched_value} adultos. ¿Viaja algún niño? (Si no, di 'cero')."
            return "No entendí el número. ¿Podrías decirlo de nuevo?"

        elif self.state == states["AWAITING_CHILDREN"]:
            num_children = "0"
            if intent == "capture_number":
                num_children = str(matched_value)
            elif intent == "negative_simple":
                num_children = "0"
            self.reservation_details["ninos"] = num_children
            self.state = states["AWAITING_ROOM_CHOICE"]
            return "Gracias. Tenemos: \n    1. Sencilla\n    2. Doble\n    3. Suite\n¿Qué tipo de habitación prefieres?"

        elif self.state == states["AWAITING_ROOM_CHOICE"]:
            room_options = {"1": "Sencilla", "2": "Doble", "3": "Suite", "sencilla": "Sencilla", "doble": "Doble",
                            "suite": "Suite"}
            selection = re.search(r"(sencilla|doble|suite|\d+)", user_input.lower())
            if selection and (room := room_options.get(selection.group(0))):
                self.reservation_details["tipo_habitacion"] = room
                self.state = states["AWAITING_NUM_ROOMS"]
                return f"Excelente elección: {room}. ¿Cuántas habitaciones de este tipo necesitas?"
            return "No reconocí esa opción. Por favor, elige Sencilla, Doble o Suite."

        elif self.state == states["AWAITING_NUM_ROOMS"]:
            if intent == "capture_number" and matched_value > 0:
                self.reservation_details["num_habitaciones"] = str(matched_value)
                self.state = states["AWAITING_GUEST_NAME"]
                return "¡Muy bien! Ya casi terminamos. ¿A nombre de quién hago la reservación?"
            return "Por favor, dime un número válido de habitaciones."

        elif self.state == states["AWAITING_GUEST_NAME"]:
            self.reservation_details['nombre_huesped'] = user_input.title()
            if not self.user_name: self.user_name = user_input.split()[0]
            self.state = states["AWAITING_GUEST_EMAIL"]
            return f"Gracias, {user_input.split()[0]}. ¿Cuál es tu correo electrónico?"

        elif self.state == states["AWAITING_GUEST_EMAIL"]:
            if intent == "capture_email":
                self.reservation_details['email'] = matched_value
                self.state = states["AWAITING_GUEST_PHONE"]
                return "Correo guardado. Por último, ¿nos podrías dar un teléfono de contacto?"
            return "Ese correo no parece válido. ¿Podrías verificarlo?"

        elif self.state == states["AWAITING_GUEST_PHONE"]:
            if intent == "capture_phone":
                self.reservation_details['telefono'] = matched_value

                self.reservation_details['costo_total'] = calculate_total_cost(
                    self.reservation_details['check_in'],
                    self.reservation_details['check_out'],
                    self.reservation_details['tipo_habitacion'],
                    self.reservation_details['num_habitaciones']
                )

                self.state = states["AWAITING_CONFIRMATION"]
                summary = self._build_reservation_summary(self.reservation_details)
                return f"¡Excelente! Revisa que todo esté en orden:\n{summary}\n\n¿Confirmo la reservación?"
            return "No parece un número de teléfono válido."

        elif self.state == states["AWAITING_CONFIRMATION"]:
            if intent == "affirmative":
                folio = f"R{random.randint(10000, 99999)}"
                self.reservation_details['folio'] = folio
                self.reservation_details['check_in'] = self.reservation_details['check_in'].strftime('%Y-%m-%d')
                self.reservation_details['check_out'] = self.reservation_details['check_out'].strftime('%Y-%m-%d')

                save_reservation_to_csv(self.reservation_details)
                guest_name = self.reservation_details.get('nombre_huesped')
                self.state, self.reservation_details = states["GENERAL"], {}
                return f"¡Listo! Tu reservación a nombre de {guest_name} está confirmada con el folio {folio}. ¡Gracias!"
            else:
                self.state, self.reservation_details = states["GENERAL"], {}
                return "Entendido. He cancelado el proceso."
        return random.choice(intents["fallback"]["responses"])

    def handle_management_flow(self, intent, matched_value, user_input):
        if self.state in [states["MANAGE_AWAITING_FOLIO"], states["MANAGE_AWAITING_NAME"],
                          states["MANAGE_AWAITING_EMAIL"]]:
            if self.state == states["MANAGE_AWAITING_FOLIO"]:
                if intent == "capture_folio":
                    self.found_reservations = find_reservations(folio=matched_value)
                elif intent == "no_folio":
                    self.state = states["MANAGE_AWAITING_NAME"]
                    return "No hay problema. ¿A nombre de quién está la reservación?"
                else:
                    return "Por favor, dime un número de folio (ej. R12345) o di 'no tengo folio'."

            elif self.state == states["MANAGE_AWAITING_NAME"]:
                self.found_reservations = find_reservations(nombre=user_input)

            elif self.state == states["MANAGE_AWAITING_EMAIL"]:
                if intent != "capture_email": return "No parece un email válido."
                self.found_reservations = find_reservations(nombre=self.active_reservation['nombre_huesped'],
                                                            email=matched_value)

            if not self.found_reservations:
                return "No encontré reservaciones con esos datos. ¿Quieres intentar de nuevo?"
            elif len(self.found_reservations) > 1 and self.state != states["MANAGE_AWAITING_EMAIL"]:
                self.active_reservation = {'nombre_huesped': user_input}
                self.state = states["MANAGE_AWAITING_EMAIL"]
                return "Encontré varias reservaciones. Para confirmar, ¿cuál es tu correo electrónico?"
            else:
                self.active_reservation = self.found_reservations[0]
                self.state = states["MANAGE_SHOWING_OPTIONS"]
                return f"¡Reservación encontrada!{self._build_reservation_summary(self.active_reservation)}\n\n¿Qué deseas hacer?\n    1. Modificar\n    2. Eliminar"

        elif self.state == states["MANAGE_SHOWING_OPTIONS"]:
            if "eliminar" in user_input.lower() or "2" in user_input:
                self.state = states["MANAGE_CONFIRM_DELETE"]
                return "¿Estás seguro de que quieres ELIMINAR tu reservación? Esta acción no se puede deshacer."
            elif "modificar" in user_input.lower() or "1" in user_input:
                self.state = states["MODIFY_CHOOSING_FIELD"]
                return "¿Qué dato te gustaría modificar?\n    1. Fechas\n    2. Huéspedes\n    3. Habitación y Cantidad\n    4. Destino (Estado)"
            return "Por favor, elige una opción válida: 1. Modificar o 2. Eliminar."

        elif self.state == states["MANAGE_CONFIRM_DELETE"]:
            if intent == "affirmative":
                all_reservations = find_reservations()
                reservations_to_keep = [res for res in all_reservations if
                                        res['folio'] != self.active_reservation['folio']]
                update_reservations_file(reservations_to_keep)
                folio_eliminado = self.active_reservation['folio']
                self.state, self.active_reservation = states["GENERAL"], None
                return f"Listo. La reservación {folio_eliminado} ha sido eliminada."
            else:
                self.state, self.active_reservation = states["GENERAL"], None
                return "De acuerdo, no se ha eliminado nada."

        elif self.state == states["MODIFY_CHOOSING_FIELD"]:
            user_input_lower = user_input.lower()
            if any(kw in user_input_lower for kw in ["fecha", "1"]):
                self.state = states["MODIFY_AWAITING_NEW_CHECKIN"]
                return "Entendido. ¿Cuál es la nueva fecha de llegada (check-in)?"
            elif any(kw in user_input_lower for kw in ["huésped", "huesped", "2"]):
                self.state = states["MODIFY_AWAITING_NEW_ADULTS"]
                return "De acuerdo. ¿Cuál es el nuevo número de adultos?"
            elif any(kw in user_input_lower for kw in ["habitación", "habitacion", "cantidad", "3"]):
                self.state = states["MODIFY_AWAITING_NEW_ROOM"]
                return "Perfecto. ¿Cuál es el nuevo tipo de habitación? (Sencilla, Doble, Suite)"
            elif any(kw in user_input_lower for kw in ["destino", "estado", "4"]):
                self.state = states["MODIFY_AWAITING_NEW_STATE"]
                return "Entendido, ¿cuál es el nuevo estado de destino?"
            return "Por favor, elige una opción válida."

        elif self.state == states["MODIFY_AWAITING_NEW_STATE"]:
            normalized_input = user_input.lower()
            if normalized_input in ESTADOS_DE_MEXICO:
                self.active_reservation['estado'] = user_input.title()
                return self._recalculate_and_save_active_reservation()
            else:
                self.state = states["MANAGE_POST_MODIFY_OPTIONS"]  # Regresar a opciones
                return "Ese no es un estado válido. La modificación del destino fue cancelada. ¿Deseas modificar otro dato?"

        elif self.state == states["MODIFY_AWAITING_NEW_CHECKIN"]:
            new_checkin = parse_relative_date(user_input)
            if not new_checkin or new_checkin < date.today():
                return "Fecha de llegada no válida. Intenta con una fecha futura."
            self.temp_data['check_in'] = new_checkin
            self.state = states["MODIFY_AWAITING_NEW_CHECKOUT"]
            return f"Nueva llegada: {new_checkin.strftime('%A %d de %B')}. Ahora, ¿la nueva fecha de salida?"

        elif self.state == states["MODIFY_AWAITING_NEW_CHECKOUT"]:
            new_checkout = parse_relative_date(user_input)
            if not new_checkout or new_checkout <= self.temp_data['check_in']:
                return "La fecha de salida debe ser posterior a la nueva llegada."
            self.active_reservation['check_in'] = self.temp_data['check_in'].strftime('%Y-%m-%d')
            self.active_reservation['check_out'] = new_checkout.strftime('%Y-%m-%d')
            self.temp_data = {}
            return self._recalculate_and_save_active_reservation()

        elif self.state == states["MODIFY_AWAITING_NEW_ADULTS"]:
            if intent == "capture_number":
                self.temp_data['adultos'] = str(matched_value)
                self.state = states["MODIFY_AWAITING_NEW_CHILDREN"]
                return f"Adultos: {matched_value}. ¿Y el nuevo número de niños?"
            return "No entendí el número. ¿Cuántos adultos serán?"

        elif self.state == states["MODIFY_AWAITING_NEW_CHILDREN"]:
            num_children = "0"
            if intent == "capture_number": num_children = str(matched_value)
            self.active_reservation['adultos'] = self.temp_data['adultos']
            self.active_reservation['ninos'] = num_children
            self.temp_data = {}
            return self._recalculate_and_save_active_reservation()

        elif self.state == states["MODIFY_AWAITING_NEW_ROOM"]:
            room_options = {"sencilla": "Sencilla", "doble": "Doble", "suite": "Suite"}
            selection = re.search(r"(sencilla|doble|suite)", user_input.lower())
            if selection and (room := room_options.get(selection.group(0))):
                self.temp_data['tipo_habitacion'] = room
                self.state = states["MODIFY_AWAITING_NEW_NUM_ROOMS"]
                return f"Nuevo tipo: {room}. ¿Cuántas habitaciones de este tipo serán?"
            return "No reconocí esa habitación. Elige Sencilla, Doble o Suite."

        elif self.state == states["MODIFY_AWAITING_NEW_NUM_ROOMS"]:
            if intent == "capture_number" and matched_value > 0:
                self.active_reservation['tipo_habitacion'] = self.temp_data['tipo_habitacion']
                self.active_reservation['num_habitaciones'] = str(matched_value)
                self.temp_data = {}
                return self._recalculate_and_save_active_reservation()
            return "Por favor, dime un número válido de habitaciones."

        elif self.state == states["MANAGE_POST_MODIFY_OPTIONS"]:
            if intent == "affirmative":
                self.state = states["MODIFY_CHOOSING_FIELD"]
                return "¿Qué otro dato quieres modificar?\n    1. Fechas\n    2. Huéspedes\n    3. Habitación y Cantidad\n    4. Destino"
            else:
                self.state, self.active_reservation = states["GENERAL"], None
                return "De acuerdo. ¿Hay algo más en lo que pueda ayudarte?"

        return random.choice(intents["fallback"]["responses"])

    def handle_message(self, user_input):
        intent, matched_value = self.find_match(user_input)

        if intent == "cancel_action" and (self.state.startswith(("AWAITING", "MANAGE", "MODIFY", "PRICE"))):
            self.state, self.reservation_details, self.active_reservation, self.temp_data = states[
                "GENERAL"], {}, None, {}
            return "Proceso cancelado. ¿Te puedo ayudar con otra cosa?"

        if self.state.startswith("PRICE"):
            return self.handle_price_flow(intent, matched_value, user_input)

        if self.state.startswith("AWAITING"):
            return self.handle_reservation_flow(intent, matched_value, user_input)

        if self.state.startswith("MANAGE") or self.state.startswith("MODIFY"):
            return self.handle_management_flow(intent, matched_value, user_input)

        if intent == "reservas":
            self.state, self.reservation_details = states["AWAITING_STATE"], {}
            return "¡Claro! Empecemos. ¿Para qué estado de la república te gustaría reservar?"

        # #############################################################################
        # #####                     INICIO DE LA MEJORA                           #####
        # #############################################################################
        if intent == "precios":
            self.state = states["PRICE_INQUIRY_POST"]
            price_list = "\n".join(
                [f"    - {tipo}: ${precio:,.2f} MXN por noche" for tipo, precio in PRECIOS_POR_NOCHE.items()])
            return f"¡Con gusto! Nuestras tarifas base son:\n{price_list}\n\nEstos precios pueden variar. ¿Te gustaría iniciar una reservación con alguna de estas opciones?"
        # #############################################################################
        # #####                       FIN DE LA MEJORA                            #####
        # #############################################################################

        if intent == "manage_reservation":
            self.state = states["MANAGE_AWAITING_FOLIO"]
            return "Con gusto te ayudo. Por favor, dime tu número de folio (ej. R12345), o di 'no tengo folio'."

        if intent == "capture_name": self.user_name = matched_value.capitalize(); return f"¡Mucho gusto, {self.user_name}!"
        if intent == "recall_name": return f"Claro, te llamas {self.user_name}." if self.user_name else "Aún no me has dicho tu nombre."
        if intent == "despedida": self.state = states["END"]; return random.choice(intents["despedida"]["responses"])
        if intent in intents and "responses" in intents.get(intent, {}): return random.choice(
            intents[intent]["responses"])

        return random.choice(intents["fallback"]["responses"])


# --- CICLO PRINCIPAL DEL CHATBOT ---
welcome_menu = """
Bot: ¡Hola! Soy FiestaBot, tu asistente virtual de Fiesta Inn.
---------------------------------------------------------
Puedo ayudarte con lo siguiente:

    🏨 Reservar una habitación
    📝 Gestionar una reservación (modificar, cancelar)
    💰 Consultar precios y tarifas
    🛎️ Horarios de Check-in y Check-out

Escribe lo que necesites o elige una opción.
---------------------------------------------------------
"""

"""
if __name__ == "__main__":
    bot = ChatBot()
    print(welcome_menu)

    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ['salir', 'exit']:
            print("Bot: ¡Hasta luego! Gracias por usar FiestaBot.")
            break

        response = bot.handle_message(user_input)
        print(f"Bot: {response}")

        if bot.state == states["END"]:
            break
"""
