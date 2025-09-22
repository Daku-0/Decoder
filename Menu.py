import tkinter as tk
import ttkbootstrap as ttk
from base import BaseApp
from Decoder import DecoderApp

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú Principal")
        self.root.minsize(300, 200)
        
        self.dark_mode = False  # Estado global del tema
        self.open_windows = []  # Lista para rastrear ventanas abiertas

        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12), padding=10)

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.base_button = ttk.Button(self.main_frame, text="Descomprimir Campo 64", command=self.open_base)
        self.base_button.pack(pady=10)

        self.decoder_button = ttk.Button(self.main_frame, text="Decoder Completo", command=self.open_decoder)
        self.decoder_button.pack(pady=10)

        self.toggle_button = ttk.Button(self.main_frame, text="Cambiar a Tema Oscuro", command=self.toggle_theme)
        self.toggle_button.pack(pady=10)
        
        self.root.bind("<Control-t>", self.toggle_theme)

        self.apply_theme()  # Aplicar el tema inicial

    def open_base(self):
        if hasattr(self, 'base_window') and self.base_window.winfo_exists():
            self.base_window.deiconify()  # Mostrar la ventana oculta
            for app in self.open_windows:
                if hasattr(app, 'root') and app.root == self.base_window:
                    app.apply_theme(self.dark_mode)
                    break
        else:
            self.base_window = tk.Toplevel(self.root)
            app = BaseApp(self.base_window, self)
            self.open_windows.append(app)
            self.base_window.protocol("WM_DELETE_WINDOW", lambda: self.on_window_close(app, self.base_window))
            app.apply_theme(self.dark_mode) 

    def open_decoder(self):
        if hasattr(self, 'decoder_window') and self.decoder_window.winfo_exists():
            self.decoder_window.deiconify()
            for app in self.open_windows:
                if hasattr(app, 'root') and app.root == self.decoder_window:
                    app.apply_theme(self.dark_mode)
                    break
        else:
            self.decoder_window = tk.Toplevel(self.root)
            app = DecoderApp(self.decoder_window, self.dark_mode, self)
            self.open_windows.append(app)
            self.decoder_window.protocol("WM_DELETE_WINDOW", lambda: self.on_window_close(app, self.decoder_window))
            app.apply_theme(self.dark_mode)
    
    def toggle_theme(self, event=None):
        self.dark_mode = not self.dark_mode
        self.toggle_button.config(text="Cambiar a Tema Claro" if self.dark_mode else "Cambiar a Tema Oscuro")
        try:
            self.apply_theme()  # Aplicar el tema al menú principal
            self.update_all_windows()  # Actualizar todas las ventanas abiertas
        except tk.TclError as e:
            print(f"Error al aplicar el tema: {e}, posiblemente una ventana ya fue cerrada.")
            self.clean_invalid_windows()
            try:
                self.style = ttk.Style()
                self.apply_theme()
                self.update_all_windows()
                print("Tema reaplicado correctamente tras limpieza")
            except tk.TclError as e2:
                print(f"Error al reaplicar el tema: {e2}")
            pass  # Ignorar errores de widgets destruidos

    def apply_theme(self):
        theme = "darkly" if self.dark_mode else "flatly"
        try:
            # Reiniciar el estilo para evitar conflictos con widgets destruidos
            self.style = ttk.Style()
            self.style.theme_use(theme)
        except tk.TclError as e:
            print(f"Error al cambiar el tema global: {e}")
            raise

    def update_all_windows(self):
        print("Me llaman aaa ", self.dark_mode)
        for window in self.open_windows[:]:  # Usar una copia para evitar modificaciones durante iteración
            if hasattr(window, "apply_theme") and window.root.winfo_exists():  # Verificar si la ventana aún existe
                try:
                    window.apply_theme(self.dark_mode)
                except tk.TclError as e:
                    print(f"Error al actualizar ventana: {e}")
                    if window in self.open_windows:
                        self.open_windows.remove(window)

    def get_base_app(self):
        # Verificar si la ventana BaseApp ya está abierta
        if hasattr(self, 'base_window') and self.base_window.winfo_exists():
            for app in self.open_windows:
                if isinstance(app, BaseApp):
                    return app
        # Si no está abierta, abrirla y devolver la instancia
        else:
            self.open_base()
            for app in self.open_windows:
                if isinstance(app, BaseApp):
                    return app
        return None
    
    def clean_invalid_windows(self):
        self.open_windows = [w for w in self.open_windows if w.root.winfo_exists()]

    def on_window_close(self, app, window):
        print("Cerrando ventana")
        print("Widgets vivos:", len(self.root.winfo_children()))
        if window.winfo_exists():
            window.withdraw()  # Ocultar la ventana en lugar de destruirla si se destruye usando destroy() en Tkinter o ttkbootstrap genera errores con el  
        else:
            if app in self.open_windows:
                self.open_windows.remove(app)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()