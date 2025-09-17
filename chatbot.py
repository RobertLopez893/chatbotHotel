import random
import re
import csv
from datetime import date, timedelta, datetime
import locale
import os
import unicodedata

# --- CONFIGURACIÓN DE IDIOMA ---
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    print("Locale 'es_ES.UTF-8' no encontrado. Las fechas podrían aparecer en inglés.")

# --- PRECIOS (Integrado desde precios.py) ---
BASE_PRICES = {
    "Sencilla": 1500,  # Manteniendo precios originales de chatbot.py
    "Doble": 2200,
    "Suite": 3500,
}
WEEKEND_SURCHARGE = 0.15  # +15% viernes/sábado

# --- HORARIOS ---
HORARIOS_POR_ZONA = {
    "Noroeste": {"check_in": "1:00 PM", "check_out": "11:00 AM"},  # UTC-8
    "Pacífico": {"check_in": "2:00 PM", "check_out": "12:00 PM"},  # UTC-7
    "Centro": {"check_in": "3:00 PM", "check_out": "1:00 PM"},  # UTC-6
    "Sureste": {"check_in": "4:00 PM", "check_out": "2:00 PM"}  # UTC-5
}

# --- ZONAS ---
ESTADOS_POR_ZONA = {
    "baja california": "Noroeste",
    "baja california sur": "Pacífico", "chihuahua": "Pacífico", "nayarit": "Pacífico", "sinaloa": "Pacífico",
    "sonora": "Pacífico",
    "quintana roo": "Sureste"
}

# --- DESTINOS VÁLIDOS ---
ESTADOS_DE_MEXICO = [
    "aguascalientes", "baja california", "baja california sur", "campeche",
    "chiapas", "chihuahua", "coahuila", "colima", "ciudad de méxico", "cdmx",
    "durango", "guanajuato", "guerrero", "hidalgo", "jalisco", "méxico",
    "michoacán", "morelos", "nayarit", "nuevo león", "oaxaca", "puebla",
    "querétaro", "quintana roo", "san luis potosí", "sinaloa", "sonora",
    "tabasco", "tamaulipas", "tlaxcala", "veracruz", "yucatán", "zacatecas"
]

# --- UBICACIONES (Simulación de API/Base de Datos) ---
HOTELES_POR_ESTADO = {
    "aguascalientes": "Fiesta Inn Aguascalientes\n📍 Dirección: Avenida Mahatma Gandhi, Sur 302, Col. Villasunción, 20280 Aguascalientes, Ags.\n📞 Teléfono: +52 449 149 0200",
    "baja california": "Fiesta Inn Tijuana Otay Aeropuerto\n📍 Dirección: Rampa Aeropuerto 16000, Aeropuerto, La Pechuga, 22000 Tijuana, B.C.\n📞 Teléfono: +52 664 979 1900",
    "campeche": "Fiesta Inn Ciudad del Carmen\n📍 Dirección: Av. Periférico Norte s/n, Av Concordia esq, Petrolera, 24170 Cdad. del Carmen, Camp.\n📞 Teléfono: +52 938 381 0200",
    "chiapas": "Fiesta Inn Tuxtla Gutiérrez\n📍 Dirección: Av. Prolongación Anillo Circunvalación Sur 248, Santa Elena, 29060 Tuxtla Gutiérrez, Chis.\n📞 Teléfono: +52 961 617 1300",
    "chihuahua": "Fiesta Inn Chihuahua Fashion Mall\n📍 Dirección: Av. De la Juventud 3501 Esq. con, Av. Instituto Politécnico Nacional, 31207 Chihuahua, Chih.\n📞 Teléfono: +52 614 432 6920",
    "ciudad de méxico": "Fiesta Inn Ciudad de México Aeropuerto\n📍 Dirección: Blvd. Puerto Aéreo 502, Moctezuma 2da Secc, Venustiano Carranza, 15530 Ciudad de México, CDMX\n📞 Teléfono: +52 55 5133 6600",
    "coahuila": "Fiesta Inn Saltillo\n📍 Dirección: Carr. Monterrey - Saltillo No. 6607, Zona Industrial, 25270 Saltillo, Coah.\n📞 Teléfono: +52 844 411 0000",
    "colima": "Fiesta Inn Colima\n📍 Dirección: Prolongación, Blvrd Camino Real 1101 Col, El Diezmo, 28010 Colima, Col.\n📞 Teléfono: +52 312 316 4444",
    "durango": "Fiesta Inn Express Durango\n📍 Dirección: Blvd. Felipe Pescador 1401, La Esperanza, 34080 Durango, Dgo.\n📞 Teléfono: +52 618 150 0900",
    "guanajuato": "Fiesta Inn León\n📍 Dirección: Blvd. Adolfo López Mateos 2502, Jardines de Jerez, 37530 León de los Aldama, Gto.\n📞 Teléfono: +52 477 710 0500",
    "hidalgo": "Fiesta Inn Pachuca Gran Patio\n📍 Dirección: Blvrd Luis Donaldo Colosio 2009, Los Jales, Ex-hacienda de Coscotitlán, 42064 Pachuca de Soto, Hgo.\n📞 Teléfono: +52 771 717 8540",
    "jalisco": "Fiesta Inn Guadalajara Expo\n📍 Dirección: Av. Mariano Otero 1550 Col, Rinconada del Sol, 45055 Guadalajara, Jal.\n📞 Teléfono: +52 33 3669 3200",
    "méxico": "Fiesta Inn Toluca Tollocan\n📍 Dirección: Paseo Tollocan Oriente esq, Francisco I Madero Sur 1132, Santa Ana Tlapaltitlán, 50160 Toluca, Méx.\n📞 Teléfono: +52 722 276 1000",
    "michoacán": "Fiesta Inn Morelia Altozano\n📍 Dirección: Av Montaña Monarca 1000, Centro Comercial Altozano, 58093 Morelia, Mich.\n📞 Teléfono: +52 443 322 3150",
    "morelos": "Fiesta Inn Cuernavaca\n📍 Dirección: Carretera México - Acapulco Km 88 S/N, Delicias, 62330 Cuernavaca, Mor.\n📞 Teléfono: +52 777 100 8200",
    "nayarit": "Fiesta Inn Tepic\n📍 Dirección: Blvrd Luis Donaldo Colosio 580, Benito Juárez Ote, 63175 Tepic, Nay.\n📞 Teléfono: +52 311 129 5950",
    "nuevo león": "Fiesta Inn Monterrey Fundidora\n📍 Dirección: Av. Churubusco #701, Esq. Prolongación, Fierro, 64590 Monterrey, N.L.\n📞 Teléfono: +52 81 8126 0500",
    "oaxaca": "Fiesta Inn Oaxaca\n📍 Dirección: Avenida Universidad 140, Universidad, 68130 Oaxaca de Juárez, Oax.\n📞 Teléfono: +52 951 501 6000",
    "puebla": "Fiesta Inn Parque Puebla\n📍 Dirección: Calz. Ignacio Zaragoza 410, Corredor Industrial la Ciénega, 72220 Puebla, Pue.\n📞 Teléfono: +52 222 408 1800",
    "querétaro": "Fiesta Inn Querétaro\n📍 Dirección: Av. 5 de Febrero 108, Niños Heroes, 76010 Santiago de Querétaro, Qro.\n📞 Teléfono: +52 442 196 0000",
    "quintana roo": "Fiesta Inn Cancún Las Américas\n📍 Dirección: Av. Bonampak Mz 1, 7, 77500 Cancún, Q.R.\n📞 Teléfono: +52 998 891 5650",
    "san luis potosí": "Fiesta Inn San Luis Potosí Glorieta Juárez\n📍 Dirección: Av Benito Juarez 130, Prados Glorieta, 78390 San Luis Potosí, S.L.P.\n📞 Teléfono: +52 444 834 9494",
    "sinaloa": "Fiesta Inn Culiacán\n📍 Dirección: J. Diego Valadez Poniente No. 1676, Desarrollo Urbano Tres Ríos, 80000 Culiacán Rosales, Sin.\n📞 Teléfono: +52 667 759 5900",
    "sonora": "Fiesta Inn Express Hermosillo\n📍 Dirección: Blvd. Fco. Eusebio Kino 375, Lomas Pitic, 83010 Hermosillo, Son.\n📞 Teléfono: +52 662 289 2200",
    "tabasco": "Fiesta Inn Villahermosa Cencali\n📍 Dirección: Benito Juárez García 105, Loma Linda, 86050 Villahermosa, Tab.\n📞 Teléfono: +52 993 313 6611",
    "tamaulipas": "Fiesta Inn Tampico\n📍 Dirección: Av. Miguel Hidalgo 6106, Laguna de la Herradura, 89219 Tampico, Tamps.\n📞 Teléfono: +52 833 230 0500",
    "tlaxcala": "Holiday Inn Tlaxcala (Alternativo)\n📍 Dirección: Carretera Tlaxcala-Apizaco Km 10 Santa María Atlihuetzia, 90459 Tlaxcala, Tlax.\n📞 Teléfono: +52 246 249 0900",
    "veracruz": "Fiesta Inn Veracruz Boca del Río\n📍 Dirección: Blvd. Manuel Ávila Camacho S/N, Costa de Oro, 94299 Veracruz, Ver.\n📞 Teléfono: +52 229 923 1000",
    "yucatán": "Fiesta Inn Mérida\n📍 Dirección: Calle 5 B No. 290 A x 20 A y 60, Col Revolución, 97115 Mérida, Yuc.\n📞 Teléfono: +52 999 964 3500",
    "zacatecas": "Fiesta Inn Zacatecas\n📍 Dirección: Calzada Heroes de Chapultepec km 13 + 200 Col. La escondida, 98160 Zacatecas, Zac.\n📞 Teléfono: +52 492 491 4930"
}

# --- SERVICIOS CON SUB-FLUJOS ---
SERVICIOS_DISPONIBLES = {
    "restaurante": {
        "descripcion": "Nuestro restaurante, La Isla, está abierto para desayunos, comidas y cenas.",
        "pregunta": "¿Te gustaría saber sobre el tipo de comida que servimos o los horarios?",
        "detalles": {
            "comida": "Ofrecemos un delicioso menú de cocina regional e internacional, con opciones a la carta y buffet de desayuno.",
            "horarios": "Generalmente, el restaurante abre de 6:00 AM a 11:00 PM todos los días."
        }
    },
    "gimnasio": {
        "descripcion": "Contamos con un gimnasio para que no pierdas tu rutina de ejercicio.",
        "pregunta": "¿Quieres saber sobre el equipamiento o el horario?",
        "detalles": {
            "equipamiento": "Está equipado con máquinas cardiovasculares como caminadoras y elípticas, así como un área de pesas.",
            "horario": "¡Nuestro gimnasio está abierto para ti las 24 horas del día!"
        }
    },
    "alberca": {
        "descripcion": "Sí, contamos con alberca para que puedas relajarte.",
        "pregunta": "¿Te interesa saber la ubicación o el horario?",
        "detalles": {
            "ubicacion": "La mayoría de nuestras albercas son al aire libre, ubicadas en áreas comunes para fácil acceso.",
            "horario": "El horario de la alberca suele ser de 9:00 AM a 9:00 PM, pero puede variar por hotel."
        }
    },
    "estacionamiento": {
        "descripcion": "Ofrecemos estacionamiento seguro para nuestros huéspedes.",
        "pregunta": "¿Te gustaría saber si tiene costo o cómo funciona?",
        "detalles": {
            "costo": "En la mayoría de los hoteles el estacionamiento es de cortesía para huéspedes. Sin embargo, en algunas ubicaciones con alta demanda puede tener un costo preferencial. Te recomiendo confirmarlo con el hotel de tu destino.",
            "funciona": "Es un estacionamiento de autoservicio. Simplemente toma un boleto al entrar y al hacer tu check-out lo validamos en recepción."
        }
    },
    "wifi": {
        "descripcion": "Claro, ofrecemos Wi-Fi de alta velocidad en todo el hotel.",
        "pregunta": "¿Quieres saber cómo conectarte o si tiene algún costo?",
        "detalles": {
            "conectar": "Para conectarte, simplemente selecciona la red 'Fiesta Inn' desde tu dispositivo. Al abrir el navegador, se te pedirá tu número de habitación y apellido para iniciar sesión.",
            "costo": "El servicio de Wi-Fi es totalmente gratuito y de cortesía para todos nuestros huéspedes."
        }
    },
    "room service": {
        "descripcion": "Sí, tenemos servicio a la habitación para tu comodidad.",
        "pregunta": "¿Quieres conocer el horario o qué tipo de alimentos puedes pedir?",
        "detalles": {
            "horario": "Nuestro servicio a cuartos está disponible generalmente de 7:00 AM a 10:30 PM.",
            "alimentos": "Puedes pedir la mayoría de los platillos de la carta de nuestro restaurante 'La Isla' directamente a tu habitación."
        }
    }
}

# --- INTENTS (VERSIÓN FINAL CON PLURALES Y MÁS FLEXIBILIDAD) ---
intents = {
    "saludos": {
        "patterns": [
            r"(?i)\b(hola|buenas|buen(os)? ?(dias|tardes|noches)|hey|qu[eé] ?(onda|tal|hay|hubo)|q onda|quiubo|inicio|empezar)\b"
        ],
        "responses": [
            "¡Hola! Soy el asistente virtual de Fiesta Inn. ¿En qué puedo ayudarte hoy?",
            "¡Qué tal! Bienvenido al asistente de Fiesta Inn. Estoy para servirte.",
            "Hola, gracias por contactarnos. ¿Cómo puedo asistirte?"
        ]
    },
    "reservas": {
        "patterns": [
            # MEJORA: Ahora entiende "reserva", "reservación" y "reservaciones"
            r"(?i)(^\s*1\s*$|\b(reservar|quiero una habitaci[oó]n|necesito un cuarto|hacer una reserva|reserva(ci[oó]n(es)?)?|reservame)\b)"
        ],
    },
    "precios": {
        "patterns": [
            # MEJORA: Añadido el plural "precios" y "costos"
            r"(?i)(^\s*2\s*$|\b(precio[s]?|cu[aá]nto cuesta|tarifa[s]?|costo[s]?|cotiza|cu[aá]nto vale|informes)\b)"
        ],
    },
    "manage_reservation": {
        "patterns": [
            # MEJORA: Entiende la gestión de "reservación" o "reservaciones"
            r"(?i)(^\s*3\s*$|\b(modificar|cambiar|consultar|ver|eliminar|cancelar|gestionar).*(reserva(ci[oó]n(es)?)?|estancia)\b)"
        ],
    },
    "checkin_checkout": {
        "patterns": [
            r"(?i)(^\s*4\s*$|check-?in|check-out|entrada|salida|horario[s]?)"
        ],
    },
    "ubicacion": {
        "patterns": [
            # MEJORA: Añadidos los plurales "ubicaciones" y "direcciones"
            r"(?i)(^\s*5\s*$|ubicaci[oó]n(es)?|direcci[oó]n(es)?|d[oó]nde est[aá]|sucursal|encontrar)"
        ],
    },
    "servicios_general": {
        "patterns": [
            # MEJORA: Entiende "servicio" y "servicios", "instalación" e "instalaciones"
            r"(?i)(^\s*6\s*$|servicio[s]?|qu[eé] ofrece|amenidades|qu[eé] m[aá]s tienen|con qu[eé] cuenta|instalaci[oó]n(es)?)"
        ],
    },
    "servicios_especificos": {
        "patterns": [
            r"(?i)(restaurante|resto|gym|gimnasio|alberca|piscina|wifi|internet|room service|servicio al cuarto|business center|centro de negocios|salones|juntas|estacionamiento|parking|estacio)"
        ],
    },
    # --- El resto de las intenciones permanecen igual ---
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
    "capture_folio": {"patterns": [r"(R\d{5})"], },
    "no_folio": {"patterns": [r"(?i)no\s?tengo"], },
    "affirmative": {
        "patterns": [
            r"(?i)\b(s[ií]|correcto|confirma|acepto|smn|simon|claro|por supuesto|adelante|sep|sip|efectivamente|as[ií] es)\b"
        ],
    },
    "negative_simple": {
        "patterns": [r"(?i)\b(no|nop|nel|para nada|incorrecto)\b"],
    },
    "cancel_action": {
        "patterns": [r"(?i)\b(cancela|cancelar|det[eé]n|ya no|mejor no|olv[ií]dalo)\b"],
    },
    "capture_number": {"patterns": [r"\b(\d+)\b"], },
    "capture_room_type": {"patterns": [r"(?i)(sencilla|doble|suite)"], },
    "capture_full_name": {"patterns": [r"(?i)([A-ZÁÉÍÓÚÑ][a-zñáéíóú]+(?:\s[A-ZÁÉÍÓÚÑ][a-zñáéíóú]+)+)"]},
    "capture_email": {"patterns": [r"([\w\.-]+@[\w\.-]+\.\w{2,})"]},
    "capture_phone": {"patterns": [r"^\s*(\d{2}[-.\s]?\d{4}[-.\s]?\d{4})\s*$"]},
    "service_detail_query": {
        "patterns": [
            r"(?i)(comida|horario[s]?|equipamiento|ubicaci[oó]n|costo|precio|conectar|funciona|alimentos)"
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
    "MANAGE_AWAITING_FOLIO": "MANAGE_AWAITING_FOLIO",
    "MANAGE_AWAITING_NAME": "MANAGE_AWAITING_NAME",
    "MANAGE_AWAITING_EMAIL": "MANAGE_AWAITING_EMAIL",
    "MANAGE_SHOWING_OPTIONS": "MANAGE_SHOWING_OPTIONS",
    "MANAGE_CONFIRM_DELETE": "MANAGE_CONFIRM_DELETE",
    "MODIFY_CHOOSING_FIELD": "MODIFY_CHOOSING_FIELD",
    "MODIFY_AWAITING_NEW_STATE": "MODIFY_AWAITING_NEW_STATE",
    "MODIFY_AWAITING_NEW_CHECKIN": "MODIFY_AWAITING_NEW_CHECKIN",
    "MODIFY_AWAITING_NEW_CHECKOUT": "MODIFY_AWAITING_NEW_CHECKOUT",
    "MODIFY_AWAITING_NEW_ADULTS": "MODIFY_AWAITING_NEW_ADULTS",
    "MODIFY_AWAITING_NEW_CHILDREN": "MODIFY_AWAITING_NEW_CHILDREN",
    "MODIFY_AWAITING_NEW_ROOM": "MODIFY_AWAITING_NEW_ROOM",
    "MODIFY_AWAITING_NEW_NUM_ROOMS": "MODIFY_AWAITING_NEW_NUM_ROOMS",
    "MANAGE_POST_MODIFY_OPTIONS": "MANAGE_POST_MODIFY_OPTIONS",
    "AWAITING_CHECKIN_LOCATION_CHOICE": "AWAITING_CHECKIN_LOCATION_CHOICE",
    "AWAITING_CHECKIN_STATE": "AWAITING_CHECKIN_STATE",
    "AWAITING_CHECKIN_FOLIO": "AWAITING_CHECKIN_FOLIO",
    "AWAITING_LOCATION_CHOICE": "AWAITING_LOCATION_CHOICE",
    "AWAITING_LOCATION_STATE": "AWAITING_LOCATION_STATE",
    "AWAITING_LOCATION_FOLIO": "AWAITING_LOCATION_FOLIO",
    "AWAITING_SERVICE_CHOICE": "AWAITING_SERVICE_CHOICE",
    "AWAITING_SERVICE_RESTAURANTE": "AWAITING_SERVICE_RESTAURANTE",
    "AWAITING_SERVICE_GIMNASIO": "AWAITING_SERVICE_GIMNASIO",
    "AWAITING_SERVICE_ALBERCA": "AWAITING_SERVICE_ALBERCA",
    "AWAITING_SERVICE_ESTACIONAMIENTO": "AWAITING_SERVICE_ESTACIONAMIENTO",
    "AWAITING_SERVICE_WIFI": "AWAITING_SERVICE_WIFI",
    "AWAITING_SERVICE_ROOMSERVICE": "AWAITING_SERVICE_ROOMSERVICE",
    # Nuevos estados para cotización
    "AWAITING_ROOM_FOR_PRICES": "AWAITING_ROOM_FOR_PRICES",
    "AWAITING_PRICE_CHECKIN": "AWAITING_PRICE_CHECKIN",
    "AWAITING_PRICE_CHECKOUT": "AWAITING_PRICE_CHECKOUT",
}


# --- FUNCIONES AUXILIARES ---

# --- Funciones de parseo de fechas (Mejoradas) ---
def _strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def _mkdate(y: int, m: int, d: int) -> date | None:
    try:
        return date(y, m, d)
    except ValueError:
        return None

def parse_absolute_date(text: str) -> date | None:
    norm = _strip_accents(text.lower())
    m = re.match(r'^\s*(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})\s*$', norm)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100: y = 2000 + y if y < 70 else 1900 + y
        return _mkdate(y, mo, d)
    m = re.match(r'^\s*(\d{4})[\/\-.](\d{1,2})[\/\-.](\d{1,2})\s*$', norm)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return _mkdate(y, mo, d)
    return None

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
    match = re.search(r"(\d{1,2})\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ]+)", text)
    if match:
        day = int(match.group(1))
        month_name = match.group(2).lower()
        month = months.get(month_name)
        if not month: return None
        year = today.year
        try:
            parsed_date = date(year, month, day)
            if parsed_date < today:
                return date(year + 1, month, day)
            return parsed_date
        except ValueError:
            return None
    return None

def parse_any_date(text: str) -> date | None:
    return parse_relative_date(text) or parse_absolute_date(text)


# --- Funciones de parseo de números (Mejoradas) ---
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


# --- Funciones de cálculo de costos (Mejoradas) ---
def _is_weekend(d: date) -> bool:
    return d.weekday() in (4, 5)  # Viernes y Sábado

def _count_weekend_nights(check_in: date, check_out: date) -> int:
    days = (check_out - check_in).days
    return sum(1 for i in range(days) if _is_weekend(check_in + timedelta(days=i)))

def estimate_total(room_type: str, check_in: date, check_out: date, num_rooms: int = 1) -> dict:
    base = BASE_PRICES.get(room_type, 0)
    nights = max(0, (check_out - check_in).days)
    if nights == 0:
        return {"total": 0, "nights": 0, "weekday_nights": 0, "weekend_nights": 0,
                "weekday_price": base, "weekend_price": int(round(base * (1 + WEEKEND_SURCHARGE))),
                "avg_per_night": 0}
    weekend_nights = _count_weekend_nights(check_in, check_out)
    weekday_nights = nights - weekend_nights
    weekday_price = base
    weekend_price = int(round(base * (1 + WEEKEND_SURCHARGE)))
    total = (weekday_nights * weekday_price + weekend_nights * weekend_price) * num_rooms
    avg = int(round(total / nights / num_rooms)) if nights > 0 and num_rooms > 0 else 0
    return {
        "total": total, "nights": nights, "weekend_nights": weekend_nights,
        "weekday_nights": weekday_nights, "weekday_price": weekday_price,
        "weekend_price": weekend_price, "avg_per_night": avg
    }


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
            if not folio and not nombre and not email: return all_rows
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
        self.price_quote = {}

    def find_match(self, user_message):
        # El bloque especial para "menu_option" se ha eliminado.

        if self.state in ["AWAITING_GUEST_EMAIL", "MANAGE_AWAITING_EMAIL"]: return "capture_email", user_message
        if self.state == "AWAITING_GUEST_PHONE": return "capture_phone", user_message
        if self.state == "AWAITING_GUEST_NAME": return "capture_full_name", user_message
        if self.state == "GENERAL" and (
                match := re.search(intents['capture_name']['patterns'][0], user_message, re.IGNORECASE)):
            return "capture_name", match.group(1)
        if self.state in ["AWAITING_ROOM_CHOICE", "AWAITING_ROOM_FOR_PRICES"] and (
                match := re.search(r"(sencilla|doble|suite|\d+)", user_message.lower())):
            return "capture_room_type", match.group(1)
        if self.state in ["AWAITING_ADULTS", "AWAITING_CHILDREN", "AWAITING_NUM_ROOMS",
                          "MODIFY_AWAITING_NEW_ADULTS", "MODIFY_AWAITING_NEW_CHILDREN",
                          "MODIFY_AWAITING_NEW_NUM_ROOMS"]:
            if (num := get_number_from_input(user_message)) is not None:
                return "capture_number", num

        # El bucle principal maneja todos los casos
        for intent, data in intents.items():
            for pattern in data.get("patterns", []):
                if match := re.search(pattern, user_message, re.IGNORECASE):
                    matched_group = match.group(1) if len(match.groups()) > 0 else match.group(0)
                    return intent, matched_group
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
        check_in_date = datetime.strptime(self.active_reservation['check_in'], '%Y-%m-%d').date()
        check_out_date = datetime.strptime(self.active_reservation['check_out'], '%Y-%m-%d').date()
        cost_details = estimate_total(
            self.active_reservation['tipo_habitacion'],
            check_in_date,
            check_out_date,
            int(self.active_reservation['num_habitaciones'])
        )
        self.active_reservation['costo_total'] = cost_details['total']
        all_reservations = find_reservations()
        updated_list = [self.active_reservation if res['folio'] == self.active_reservation['folio'] else res for res in
                        all_reservations]
        update_reservations_file(updated_list)
        self.state = states["MANAGE_POST_MODIFY_OPTIONS"]
        summary = self._build_reservation_summary(self.active_reservation)
        return f"¡Listo! He actualizado tu reservación. Aquí están los nuevos datos:\n{summary}\n\n¿Deseas modificar algo más? (sí/no)"

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
            parsed_date = parse_any_date(user_input)
            if not parsed_date or parsed_date < date.today():
                return "Esa fecha no es válida. Por favor, dime una fecha de llegada futura (ej: 'mañana', '20/09/2025')."
            self.reservation_details["check_in"] = parsed_date
            self.state = states["AWAITING_CHECKOUT"]
            return f"Entendido, llegada el {parsed_date.strftime('%A %d de %B')}. ¿Cuál sería tu fecha de salida?"

        elif self.state == states["AWAITING_CHECKOUT"]:
            parsed_date = parse_any_date(user_input)
            if not parsed_date or parsed_date <= self.reservation_details["check_in"]:
                return "La fecha de salida debe ser posterior a la de llegada."
            self.reservation_details["check_out"] = parsed_date
            self.state = states["AWAITING_ADULTS"]
            return f"Perfecto. Tu estancia es del {self.reservation_details['check_in'].strftime('%d de %B')} al {parsed_date.strftime('%d de %B')}. ¿Cuántos adultos se hospedarán?"

        elif self.state == states["AWAITING_ADULTS"]:
            if intent == "capture_number":
                self.reservation_details["adultos"] = str(matched_value)
                self.state = states["AWAITING_CHILDREN"]
                return f"Anotado, {matched_value} adultos. Ahora, ¿cuántos niños viajan? (Si no viajan niños, por favor, responde '0' o 'ninguno')."
            return "No entendí el número. ¿Podrías decirlo de nuevo?"

        elif self.state == states["AWAITING_CHILDREN"]:
            num_children = "0"
            if intent == "capture_number":
                num_children = str(matched_value)
            elif intent == "negative_simple" or "ninguno" in user_input.lower():
                num_children = "0"
            self.reservation_details["ninos"] = num_children
            self.state = states["AWAITING_ROOM_CHOICE"]
            return "Gracias. A continuación, selecciona el tipo de habitación que deseas. Tenemos: \n    1. Sencilla\n    2. Doble\n    3. Suite\n¿Qué tipo de habitación prefieres?"

        elif self.state == states["AWAITING_ROOM_CHOICE"]:
            room_options = {"1": "Sencilla", "2": "Doble", "3": "Suite", "sencilla": "Sencilla", "doble": "Doble", "suite": "Suite"}
            if intent == "capture_room_type":
                selection = matched_value.lower()
                if (room := room_options.get(selection)):
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
                cost_details = estimate_total(
                    self.reservation_details['tipo_habitacion'],
                    self.reservation_details['check_in'],
                    self.reservation_details['check_out'],
                    int(self.reservation_details['num_habitaciones'])
                )
                self.reservation_details['costo_total'] = cost_details['total']
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
                self.state = states["MANAGE_POST_MODIFY_OPTIONS"]
                return "Ese no es un estado válido. La modificación del destino fue cancelada. ¿Deseas modificar otro dato?"

        elif self.state == states["MODIFY_AWAITING_NEW_CHECKIN"]:
            new_checkin = parse_any_date(user_input)
            if not new_checkin or new_checkin < date.today():
                return "Fecha de llegada no válida. Intenta con una fecha futura."
            self.temp_data['check_in'] = new_checkin
            self.state = states["MODIFY_AWAITING_NEW_CHECKOUT"]
            return f"Nueva llegada: {new_checkin.strftime('%A %d de %B')}. Ahora, ¿la nueva fecha de salida?"

        elif self.state == states["MODIFY_AWAITING_NEW_CHECKOUT"]:
            new_checkout = parse_any_date(user_input)
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

    def handle_checkin_flow(self, intent, matched_value, user_input):
        if self.state == states["AWAITING_CHECKIN_LOCATION_CHOICE"]:
            if "estado" in user_input.lower():
                self.state = states["AWAITING_CHECKIN_STATE"]
                return "¿De qué estado te gustaría saber los horarios?"
            elif "folio" in user_input.lower():
                self.state = states["AWAITING_CHECKIN_FOLIO"]
                return "Claro, por favor, dime tu número de folio (ej. R12345)."
            else:
                return "Por favor, elige una opción: 'estado' o 'folio'."

        elif self.state == states["AWAITING_CHECKIN_STATE"]:
            normalized_input = user_input.lower()
            if normalized_input in ESTADOS_DE_MEXICO:
                zona = ESTADOS_POR_ZONA.get(normalized_input, "Centro")
                horarios = HORARIOS_POR_ZONA[zona]
                self.state = states["GENERAL"]
                return f"Para el estado de {user_input.title()}, los horarios son:\n    - Check-in: {horarios['check_in']}\n    - Check-out: {horarios['check_out']}"
            else:
                self.state = states["GENERAL"]
                return "Lo siento, no reconozco ese estado. Volviendo al menú principal."

        elif self.state == states["AWAITING_CHECKIN_FOLIO"]:
            if intent == "capture_folio":
                reservations = find_reservations(folio=matched_value)
                if reservations:
                    estado = reservations[0].get("estado", "").lower()
                    zona = ESTADOS_POR_ZONA.get(estado, "Centro")
                    horarios = HORARIOS_POR_ZONA[zona]
                    self.state = states["GENERAL"]
                    return f"Según tu reserva en {estado.title()}, los horarios son:\n    - Check-in: {horarios['check_in']}\n    - Check-out: {horarios['check_out']}"
                else:
                    self.state = states["GENERAL"]
                    return "No encontré ninguna reserva con ese folio. Volviendo al menú principal."
            else:
                self.state = states["GENERAL"]
                return "Ese no parece un folio válido. Volviendo al menú principal."

        return random.choice(intents["fallback"]["responses"])

    def handle_location_flow(self, intent, matched_value, user_input):
        if self.state == states["AWAITING_LOCATION_CHOICE"]:
            if "estado" in user_input.lower():
                self.state = states["AWAITING_LOCATION_STATE"]
                return "¿Perfecto, de qué estado de la república necesitas la ubicación?"
            elif "folio" in user_input.lower():
                self.state = states["AWAITING_LOCATION_FOLIO"]
                return "Claro, por favor, dime tu número de folio (ej. R12345)."
            else:
                return "Por favor, elige una opción: 'por estado' o 'por folio'."

        elif self.state == states["AWAITING_LOCATION_STATE"]:
            normalized_input = user_input.lower().replace("cdmx", "ciudad de méxico")
            hotel_info = HOTELES_POR_ESTADO.get(normalized_input)

            self.state = states["GENERAL"]
            if hotel_info:
                return f"¡Encontrado! Aquí tienes la información del hotel en {user_input.title()}:\n\n{hotel_info}"
            else:
                return f"Lo siento, no encontré una sucursal en '{user_input.title()}'. Puedes intentar con otro estado."

        elif self.state == states["AWAITING_LOCATION_FOLIO"]:
            if intent == "capture_folio":
                reservations = find_reservations(folio=matched_value)
                if reservations:
                    estado_reservado = reservations[0].get("estado", "").lower()
                    hotel_info = HOTELES_POR_ESTADO.get(estado_reservado)
                    self.state = states["GENERAL"]

                    if hotel_info:
                        return f"Según tu folio, tu hotel está en {estado_reservado.title()}. Aquí tienes los datos:\n\n{hotel_info}"
                    else:
                        return f"Encontré tu reservación para {estado_reservado.title()}, pero no tengo la dirección exacta de esa sucursal en mi sistema."
                else:
                    self.state = states["GENERAL"]
                    return "No encontré ninguna reserva con ese folio. Volviendo al menú principal."
            else:
                self.state = states["GENERAL"]
                return "Eso no parece un folio válido. Volviendo al menú principal."

        return random.choice(intents["fallback"]["responses"])

    def handle_service_flow(self, intent, matched_value, user_input):
        # CASO 1: El usuario pregunta por un servicio específico (nuevo o cambiando de tema).
        if intent == "servicios_especificos":
            alias_map = {
                "restaurante": "restaurante", "resto": "restaurante",
                "gimnasio": "gimnasio", "gym": "gimnasio",
                "alberca": "alberca", "piscina": "alberca",
                "estacionamiento": "estacionamiento", "parking": "estacionamiento", "estacio": "estacionamiento",
                "wifi": "wifi", "internet": "wifi",
                "room service": "room service", "servicio al cuarto": "room service"
            }
            service_keyword = matched_value.lower()
            found_service_key = alias_map.get(service_keyword)

            if found_service_key and found_service_key in SERVICIOS_DISPONIBLES:
                service_info = SERVICIOS_DISPONIBLES[found_service_key]
                new_state_key = f"AWAITING_SERVICE_{found_service_key.upper().replace(' ', '')}"
                if new_state_key in states:
                    self.state = states[new_state_key]  # Cambia al estado del servicio correcto
                    return f"{service_info['descripcion']}\n{service_info['pregunta']}"
                else:
                    self.state = states["GENERAL"]
                    return f"Aquí tienes la info de {found_service_key.title()}: {service_info['descripcion']}. (Nota para dev: falta el estado {new_state_key})"
            else:
                # Si el servicio específico no se reconoce, no cambia de estado.
                return "Disculpa, no reconocí ese servicio en particular. ¿Te gustaría saber de otro?"

        # CASO 2: El usuario ya está en un flujo de servicio y pregunta por un detalle.
        if intent == "service_detail_query" and self.state.startswith("AWAITING_SERVICE_"):
            service_name_from_state = self.state.split("AWAITING_SERVICE_")[-1].lower().replace("roomservice",
                                                                                                "room service")
            if service_name_from_state in SERVICIOS_DISPONIBLES:
                service_info = SERVICIOS_DISPONIBLES[service_name_from_state]
                for detail_key, detail_text in service_info["detalles"].items():
                    if re.search(r'\b' + detail_key.replace("ó", "[oó]") + r'\b', user_input.lower()):
                        self.state = states["GENERAL"]  # Responde y regresa al estado general
                        return f"{detail_text}\n\n¿Hay algo más en lo que pueda ayudarte?"

                # Si no encuentra el detalle específico que se pidió:
                self.state = states["GENERAL"]
                possible_details = ", ".join(service_info['detalles'].keys())
                return f"Entendido, pero no tengo ese detalle sobre {service_name_from_state.title()}. Te puedo dar información de: {possible_details}.\n\n¿O necesitas ayuda con otra cosa?"

        # CASO 3: Fallback. Si ninguna de las condiciones anteriores se cumple.
        self.state = states["GENERAL"]
        return random.choice(intents["fallback"]["responses"])

    def handle_price_quote_flow(self, intent, matched_value, user_input):
        if self.state == states["AWAITING_ROOM_FOR_PRICES"]:
            room_options = {"1": "Sencilla", "2": "Doble", "3": "Suite", "sencilla": "Sencilla", "doble": "Doble", "suite": "Suite"}
            if intent == "capture_room_type":
                room = room_options.get(matched_value.lower())
                if room:
                    self.price_quote = {"room": room}
                    base = BASE_PRICES[room]
                    weekend_price = int(round(base * (1 + WEEKEND_SURCHARGE)))
                    self.state = states["AWAITING_PRICE_CHECKIN"]
                    return (f"Perfecto, habitación {room}.\n"
                            f"Tarifa base por noche: ${base:,.2f} MXN (entre semana) y ${weekend_price:,.2f} MXN (fin de semana).\n"
                            f"Para una cotización total, dime tu fecha de llegada (ej: 'mañana' o '20/09/2025').")
            return "Por favor, elige Sencilla, Doble o Suite."

        elif self.state == states["AWAITING_PRICE_CHECKIN"]:
            ci = parse_any_date(user_input)
            if not ci or ci < date.today():
                return "No reconocí esa fecha o no es futura. Prueba con 'mañana' o '20/09/2025'."
            self.price_quote["check_in"] = ci
            self.state = states["AWAITING_PRICE_CHECKOUT"]
            return f"Llegada el {ci.strftime('%A %d de %B')}. Ahora, ¿cuál es la fecha de salida?"

        elif self.state == states["AWAITING_PRICE_CHECKOUT"]:
            ci = self.price_quote.get("check_in")
            co = parse_any_date(user_input)
            if not co or not ci or co <= ci:
                return "La fecha de salida debe ser posterior a la de llegada."
            room = self.price_quote.get("room")
            est = estimate_total(room, ci, co)
            self.state = states["GENERAL"]
            self.price_quote = {}
            return (f"🧾 Cotización estimada — {room}\n"
                    f"📅 Del {ci.strftime('%A %d %B %Y')} al {co.strftime('%A %d %B %Y')} "
                    f"({est['nights']} noches: {est['weekday_nights']} entre semana, {est['weekend_nights']} fin de semana)\n"
                    f"💵 Total estimado: ${est['total']:,.2f} MXN (promedio ${est['avg_per_night']:,.2f} MXN/noche)\n\n"
                    f"Esto es informativo. Si quieres reservar, escribe 'reservar' o elige la opción 1 del menú.")

        return random.choice(intents["fallback"]["responses"])

    def handle_message(self, user_input):
        intent, matched_value = self.find_match(user_input)

        # 1. MANEJO DE COMANDOS GLOBALES
        # Estos comandos tienen prioridad sobre cualquier estado.
        if intent == "cancel_action" and (self.state != states["GENERAL"]):
            self.state, self.reservation_details, self.active_reservation, self.temp_data, self.price_quote = states[
                "GENERAL"], {}, None, {}, {}
            return "Proceso cancelado. ¿Te puedo ayudar con otra cosa?"

        # 2. MANEJO DE CONVERSACIONES EN CURSO (POR ESTADO)
        # Si el bot está esperando una respuesta específica, la procesa aquí.

        # --- Flujo de Servicios ---
        if self.state.startswith("AWAITING_SERVICE_"):
            return self.handle_service_flow(intent, matched_value, user_input)

        # --- Flujo de Reservación ---
        if self.state in ["AWAITING_STATE", "AWAITING_CHECKIN", "AWAITING_CHECKOUT", "AWAITING_ADULTS",
                          "AWAITING_CHILDREN", "AWAITING_ROOM_CHOICE", "AWAITING_NUM_ROOMS", "AWAITING_GUEST_NAME",
                          "AWAITING_GUEST_EMAIL", "AWAITING_GUEST_PHONE", "AWAITING_CONFIRMATION"]:
            return self.handle_reservation_flow(intent, matched_value, user_input)

        # --- Flujo de Gestión de Reservación ---
        if self.state.startswith("MANAGE") or self.state.startswith("MODIFY"):
            return self.handle_management_flow(intent, matched_value, user_input)

        # --- Otros flujos específicos ---
        if self.state in ["AWAITING_ROOM_FOR_PRICES", "AWAITING_PRICE_CHECKIN", "AWAITING_PRICE_CHECKOUT"]:
            return self.handle_price_quote_flow(intent, matched_value, user_input)
        if self.state.startswith("AWAITING_LOCATION_"):
            return self.handle_location_flow(intent, matched_value, user_input)
        if self.state.startswith("AWAITING_CHECKIN_"):
            return self.handle_checkin_flow(intent, matched_value, user_input)

        # 3. MANEJO DE NUEVAS SOLICITUDES (POR INTENCIÓN)
        # Si no hay una conversación activa, el bot escucha nuevas peticiones.

        if intent == "reservas":
            self.state, self.reservation_details = states["AWAITING_STATE"], {}
            return "¡Claro! Empecemos. ¿Para qué estado de la república te gustaría reservar?"
        if intent == "precios":
            self.state = states["AWAITING_ROOM_FOR_PRICES"]
            return "Con gusto. ¿Te interesa habitación Sencilla, Doble o Suite?"
        if intent == "manage_reservation":
            self.state = states["MANAGE_AWAITING_FOLIO"]
            return "Con gusto te ayudo. Por favor, dime tu número de folio (ej. R12345), o di 'no tengo folio'."
        if intent == "checkin_checkout":
            self.state = states["AWAITING_CHECKIN_LOCATION_CHOICE"]
            return "¡Claro! ¿Deseas consultar los horarios para un estado específico o con tu folio de reservación?"
        if intent == "ubicacion":
            self.state = states["AWAITING_LOCATION_CHOICE"]
            return "¡Por supuesto! Puedo darte la dirección. ¿Prefieres buscar por estado o con tu folio de reservación?"

        # Disparadores de servicios: permiten iniciar una conversación sobre servicios en cualquier momento.
        if intent == "servicios_especificos":
            return self.handle_service_flow(intent, matched_value, user_input)
        if intent == "servicios_general":
            self.state = states["AWAITING_SERVICE_CHOICE"]
            service_list = "\n".join([f"    - {s.replace('room service', 'Servicio a Cuarto').title()}" for s in
                                      SERVICIOS_DISPONIBLES.keys()])
            return f"Ofrecemos una variedad de servicios:\n{service_list}\n\n¿Te gustaría saber más de alguno?"

        # --- RESPUESTAS SIMPLES Y FALLBACK ---
        if intent == "capture_name":
            self.user_name = matched_value.capitalize()
            return f"¡Mucho gusto, {self.user_name}!"
        if intent == "recall_name":
            return f"Claro, te llamas {self.user_name}." if self.user_name else "Aún no me has dicho tu nombre."
        if intent == "despedida":
            self.state = states["END"]
            return random.choice(intents["despedida"]["responses"])
        if "responses" in intents.get(intent, {}):
            return random.choice(intents[intent]["responses"])

        return random.choice(intents["fallback"]["responses"])


# --- CICLO PRINCIPAL DEL CHATBOT ---
welcome_menu = """
Bot: ¡Hola! Soy FiestaBot, tu asistente virtual de Fiesta Inn.
---------------------------------------------------------
Puedo ayudarte con lo siguiente:

    1. 🏨 Reservar una habitación
    2. 💰 Consultar precios y tarifas
    3. 📝 Gestionar una reservación (modificar, cancelar)
    4. 🛎️ Horarios de Check-in y Check-out
    5. 📍 Encontrar la ubicación de un hotel
    6. 🏊 Consultar los servicios del hotel

Escribe el número de la opción que necesites.
---------------------------------------------------------
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
