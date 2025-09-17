# gui_fiestabot.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
import os

from chatbot import ChatBot, welcome_menu, states

# Tema y fuentes
TEMA = {
    "fondo_app": "#FDF9E7",
    "fondo_encabezado": "#EC8541",
    "texto_sec_encabezado": "#FAF7B2",
    "fondo_burbuja_bot": "#FFFFFF",
    "texto_bot": "#602A11",
    "fondo_burbuja_usuario": "#FFE28A",
    "texto_usuario": "#1A1300",
    "fondo_entrada": "#FFFFFF",
    "btn_enviar": "#EC8541",
    "btn_enviar_activo": "#FFC300",
    "colores_chip": ["#F59E0B", "#3B82F6", "#10B981", "#EF4444", "#8B5CF6", "#14B8A6"],
}
FUENTE_PRINCIPAL = ("Segoe UI", 11)
FUENTE_HORA = ("Segoe UI", 8)
FUENTE_TITULO_ENCABEZADO = ("Segoe UI Semibold", 12)
FUENTE_SUBTITULO_ENCABEZADO = ("Segoe UI", 9)
FUENTE_CHIP = ("Segoe UI Semibold", 10)

# imagen
def crear_imagen_circular(ruta: str, tam: int = 36) -> ImageTk.PhotoImage:
    if not os.path.exists(ruta):
        imagen = Image.new("RGBA", (tam, tam), (37, 211, 102, 255))
        mascara = Image.new("L", (tam, tam), 0)
        dib = ImageDraw.Draw(mascara); dib.ellipse((0, 0, tam, tam), fill=255)
        imagen.putalpha(mascara)
        return ImageTk.PhotoImage(imagen)
    imagen = Image.open(ruta).convert("RGBA").resize((tam, tam), Image.LANCZOS)
    mascara = Image.new("L", (tam, tam), 0)
    dib = ImageDraw.Draw(mascara); dib.ellipse((0, 0, tam, tam), fill=255)
    imagen.putalpha(mascara)
    return ImageTk.PhotoImage(imagen)

# Interfaz 
class InterfazChat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fiesta INN - Chatbot")
        self.geometry("760x500")
        self.minsize(460, 600)
        self.configure(bg=TEMA["fondo_app"])
        self.bot = ChatBot()
        self._refs_imagen = []
        self._construir_encabezado()
        self._construir_area_chat()
        self._construir_barra_entrada()
        self.after(120, lambda: self.agregar_menu_bot(welcome_menu.strip()))
        self.bind("<Return>", self._enter_para_enviar)

    # ENCABEZADO
    def _construir_encabezado(self):
        encabezado = tk.Frame(self, bg=TEMA["fondo_encabezado"], height=60)
        encabezado.pack(side="top", fill="x")

        self._img_avatar = crear_imagen_circular("HFI.png", tam=36)
        self._refs_imagen.append(self._img_avatar)
        tk.Label(encabezado, image=self._img_avatar, bg=TEMA["fondo_encabezado"])\
            .pack(side="left", padx=12, pady=10)

        caja_titulos = tk.Frame(encabezado, bg=TEMA["fondo_encabezado"])
        caja_titulos.pack(side="left", pady=8)

        tk.Label(caja_titulos, text="Hotel Fiesta INN", bg=TEMA["fondo_encabezado"], fg="white",
                 font=FUENTE_TITULO_ENCABEZADO).pack(anchor="w")
        tk.Label(caja_titulos, text="En línea • Asistente virtual", bg=TEMA["fondo_encabezado"],
                 fg=TEMA["texto_sec_encabezado"], font=FUENTE_SUBTITULO_ENCABEZADO).pack(anchor="w")

    # Área de chat
    def _construir_area_chat(self):
        envoltura = tk.Frame(self, bg=TEMA["fondo_app"])
        envoltura.pack(fill="both", expand=True)

        self.lienzo = tk.Canvas(envoltura, bg=TEMA["fondo_app"], highlightthickness=0)
        self.lienzo.pack(side="left", fill="both", expand=True)

        barra_scroll = tk.Scrollbar(envoltura, orient="vertical", command=self.lienzo.yview)
        barra_scroll.pack(side="right", fill="y")
        self.lienzo.configure(yscrollcommand=barra_scroll.set)

        self.burbujas = tk.Frame(self.lienzo, bg=TEMA["fondo_app"])
        self.id_ventana_lienzo = self.lienzo.create_window((0, 0), window=self.burbujas, anchor="nw")

        self.burbujas.bind("<Configure>", self._al_configurar_frame)
        self.lienzo.bind("<Configure>", self._al_configurar_lienzo)

    # Barra de entrada 
    def _construir_barra_entrada(self):
        barra = tk.Frame(self, bg=TEMA["fondo_entrada"])
        barra.pack(side="bottom", fill="x")

        self.entrada = tk.Text(
            barra, height=2, wrap="word", font=FUENTE_PRINCIPAL,
            bg="#F4BB94", fg="#602A11", insertbackground="#E5E7EB", bd=0
        )
        self.entrada.pack(side="left", fill="both", expand=True, padx=(8, 6), pady=8)
        self.entrada.focus_set()

        self.btn_enviar = tk.Button(
            barra, text="Enviar", bg=TEMA["btn_enviar"], fg="white",
            activebackground=TEMA["btn_enviar_activo"], activeforeground="white",
            bd=0, font=("Segoe UI Semibold", 10), padx=16, pady=8,
            cursor="hand2", command=self._al_click_enviar
        )
        self.btn_enviar.pack(side="right", padx=8, pady=8)

    # Helpers de layout 
    def _al_configurar_frame(self, _):
        self.lienzo.configure(scrollregion=self.lienzo.bbox("all"))
        self.lienzo.yview_moveto(1.0)

    def _al_configurar_lienzo(self, evento):
        self.lienzo.itemconfig(self.id_ventana_lienzo, width=evento.width)

    def _enter_para_enviar(self, evento):
        if evento.state & 0x0001:  # Shift
            return
        self._al_click_enviar()
        return "break"

    def _marca_de_tiempo(self):
        return datetime.now().strftime("%H:%M")

    # Burbujas 
    def _agregar_burbuja(self, texto, es_usuario=False):
        fila = tk.Frame(self.burbujas, bg=TEMA["fondo_app"])
        fila.pack(fill="x", padx=10, pady=4)

        ancla = "e" if es_usuario else "w"
        fondo_burbuja = TEMA["fondo_burbuja_usuario"] if es_usuario else TEMA["fondo_burbuja_bot"]
        color_texto = TEMA["texto_usuario"] if es_usuario else TEMA["texto_bot"]

        burbuja = tk.Frame(fila, bg=fondo_burbuja)
        burbuja.pack(anchor=ancla, padx=(80, 0) if es_usuario else (0, 80))

        tk.Label(burbuja, text=texto.strip(), justify="left", wraplength=420,
                 bg=fondo_burbuja, fg=color_texto, font=FUENTE_PRINCIPAL)\
            .pack(side="top", padx=10, pady=(8, 0))
        tk.Label(burbuja, text=self._marca_de_tiempo(), bg=fondo_burbuja, fg="#413835",
                 font=FUENTE_HORA).pack(side="bottom", anchor="e", padx=10, pady=(0, 6))

    def agregar_mensaje_usuario(self, texto):
        if texto.strip():
            self._agregar_burbuja(texto, es_usuario=True)

    def agregar_mensaje_bot(self, texto):
        if texto.strip():
            self._agregar_burbuja(texto, es_usuario=False)

    # Menú 
    def agregar_menu_bot(self, menu_crudo: str):
        fila = tk.Frame(self.burbujas, bg=TEMA["fondo_app"])
        fila.pack(fill="x", padx=10, pady=6, anchor="w")
        burbuja = tk.Frame(fila, bg=TEMA["fondo_burbuja_bot"])
        burbuja.pack(anchor="w", padx=(0, 80))

        lineas = [ln for ln in menu_crudo.splitlines() if ln.strip()]
        for ln in lineas:
            s = ln.strip()
            if s.startswith(("🏨", "📝", "💰", "🛎", "📍", "🏊")):
                continue
            tk.Label(burbuja, text=s, justify="left", wraplength=420,
                     bg=TEMA["fondo_burbuja_bot"], fg=TEMA["texto_bot"], font=FUENTE_PRINCIPAL)\
                .pack(anchor="w", padx=10, pady=(6, 0))

        lineas_emoji = [ln.strip() for ln in lineas if ln.strip().startswith(("🏨", "📝", "💰", "🛎️", "📍", "🏊"))]
        if lineas_emoji:
            cont_lista = tk.Frame(burbuja, bg=TEMA["fondo_burbuja_bot"])
            cont_lista.pack(anchor="w", padx=10, pady=(6, 8))
            for i, item in enumerate(lineas_emoji):
                color = TEMA["colores_chip"][i % len(TEMA["colores_chip"])]
                fila_item = tk.Frame(cont_lista, bg=TEMA["fondo_burbuja_bot"])
                fila_item.pack(anchor="w", pady=2)

                chip = tk.Label(fila_item, text=item.split()[0], bg=color, fg="white",
                                font=FUENTE_CHIP, padx=8, pady=2)
                chip.pack(side="left", padx=(0, 8))

                resto = item[len(item.split()[0]):].strip()
                tk.Label(fila_item, text=resto, bg=TEMA["fondo_burbuja_bot"], fg=TEMA["texto_bot"],
                         font=FUENTE_PRINCIPAL, wraplength=380, justify="left").pack(side="left")

        tk.Label(burbuja, text=self._marca_de_tiempo(), bg=TEMA["fondo_burbuja_bot"], fg="#9CA3AF",
                 font=FUENTE_HORA).pack(anchor="e", padx=10, pady=(0, 6))


    def _al_click_enviar(self):
        texto_usuario = self.entrada.get("1.0", "end").strip()
        if not texto_usuario:
            return
        self.agregar_mensaje_usuario(texto_usuario)
        self.entrada.delete("1.0", "end")
        try:
            respuesta = self.bot.handle_message(texto_usuario)
        except Exception as e:
            respuesta = f"Ocurrió un error procesando tu mensaje: {e}"

        if respuesta.strip() == welcome_menu.strip():
            self.agregar_menu_bot(respuesta.strip())
        else:
            self.agregar_mensaje_bot(respuesta)

        if getattr(self.bot, "state", None) == states.get("END", "END"):
            self.entrada.config(state="disabled")
            self.btn_enviar.config(state="disabled")

if __name__ == "__main__":
    app = InterfazChat()
    app.mainloop()
