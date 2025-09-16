import tkinter as tk
from tkinter import scrolledtext
from main import ChatBot, welcome_menu

BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#0D1B2A"
BOT_BG = "#E0E1DD"
USER_BG = "#C1D7E8"
FONT = "Helvetica 12"
FONT_BOLD = "Helvetica 11 bold"


class ChatApplication:
    def __init__(self):
        self.window = tk.Tk()
        self._setup_main_window()
        self.bot = ChatBot()

    def run(self):
        self.window.mainloop()

    def _setup_main_window(self):
        self.window.title("FiestaBot Asistente Virtual")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg=BG_COLOR)

        # Head label
        head_label = tk.Label(self.window, bg=TEXT_COLOR, fg='#FFFFFF',
                              text="Asistente Fiesta Inn", font=FONT_BOLD, pady=10)
        head_label.place(relwidth=1)

        # Text widget
        self.text_widget = scrolledtext.ScrolledText(self.window, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR,
                                                     font=FONT, padx=5, pady=5, wrap=tk.WORD)
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=tk.DISABLED)

        # Bottom label
        bottom_label = tk.Label(self.window, bg="#ABB8C3", height=80)
        bottom_label.place(relwidth=1, rely=0.825)

        # Message entry box
        self.msg_entry = tk.Entry(bottom_label, bg="#A1B0BC", fg=TEXT_COLOR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)

        # Send button
        send_button = tk.Button(bottom_label, text="Enviar", font=FONT_BOLD, width=20, bg="#415A77",
                                command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)

        # Mostrar mensaje de bienvenida
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, f"FiestaBot: {welcome_menu}\n\n", ("bot_message", "bot_bg"))
        self.text_widget.configure(state=tk.DISABLED)

        # Configurar etiquetas de estilo para los mensajes
        self.text_widget.tag_config("bot_message", foreground="#0D1B2A", justify='left')
        self.text_widget.tag_config("user_message", foreground="#0D1B2A", justify='right', rmargin=10)

    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self._insert_message(msg, "Tú")

    def _insert_message(self, msg, sender):
        if not msg:
            return

        self.msg_entry.delete(0, tk.END)

        # Insertar mensaje del usuario
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, f"{sender}: {msg}\n\n", "user_message")
        self.text_widget.configure(state=tk.DISABLED)

        # Obtener y mostrar respuesta del bot
        bot_response = self.bot.handle_message(msg)
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, f"FiestaBot: {bot_response}\n\n", "bot_message")
        self.text_widget.configure(state=tk.DISABLED)

        self.text_widget.see(tk.END)


if __name__ == "__main__":
    app = ChatApplication()
    app.run()
