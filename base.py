import binascii
import gzip
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import json

class BaseApp:
    def __init__(self, root, parent_menu):
        self.root = root
        self.root.title("Descompresor GZ desde Hexadecimal")
        self.root.minsize(600, 400)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.decompressed_content = ""
        self.parent_menu = parent_menu
        self.dark_mode = parent_menu.dark_mode

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 10))
        self.style.configure("TButton", font=("Helvetica", 10), padding=5)
        self.style.configure("TCombobox", font=("Helvetica", 12))

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.hex_label = ttk.Label(self.main_frame, text="Ingrese la cadena hexadecimal:", style="TLabel")
        self.hex_label.pack(fill=tk.X, pady=(0, 5))

        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.hex_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.hex_frame, weight=1)
        self.hex_text = tk.Text(self.hex_frame, height=10, font=("Courier New", 12), wrap="none", undo=True)
        self.hex_text.pack(fill=tk.BOTH, expand=True)

        self.output_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.output_frame, weight=1)
        self.output_label = ttk.Label(self.output_frame, text="Contenido descomprimido:", style="TLabel")
        self.output_label.pack(fill=tk.X, pady=(0, 5))
        self.output_text = tk.Text(self.output_frame, height=10, font=("Helvetica", 12))
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)

        self.process_button = ttk.Button(self.button_frame, text="Procesar y Descomprimir", command=self.process_data)
        self.process_button.pack(side=tk.LEFT, padx=5)
        self.ToolTip(self.process_button, "Ctrl+P", self)

        self.json_button = ttk.Button(self.button_frame, text="Formatear como JSON", command=self.format_json)
        self.json_button.pack(side=tk.LEFT, padx=5)
        self.ToolTip(self.json_button, "Ctrl+J", self)

        self.copy_button = ttk.Button(self.button_frame, text="Copiar al Portapapeles", command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.font_label = ttk.Label(self.button_frame, text="T.F:", style="TLabel")
        self.font_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Forzar la inicialización del Combobox después de que la ventana esté lista
        self.root.after_idle(self._init_combobox)

        self.root.bind("<Control-p>", self.process_data)
        self.root.bind("<Control-j>", self.format_json)
        
        # Aplicar estilos manualmente al inicializar (sin theme_use)
        self.apply_styles(self.dark_mode)

    def _init_combobox(self):
        if not hasattr(self, 'font_size_combobox'):
            self.font_size_combobox = ttk.Combobox(self.button_frame, values=[8, 10, 12, 14, 16], width=5, state="readonly", style="TCombobox")
            self.font_size_combobox.set(12)
            self.font_size_combobox.pack(side=tk.LEFT)
            self.font_size_combobox.bind("<<ComboboxSelected>>", self.change_font_size)
        self.apply_styles(self.dark_mode)

    def apply_styles(self, dark_mode):
        if dark_mode:
            self.main_frame.configure(style="darkly.TFrame")
            self.hex_text.configure(bg="#3c3f41", fg="#20ff02", insertbackground="#ffffff", borderwidth=1, relief="solid")
            self.output_text.configure(bg="#3c3f41", fg="#ffffff", insertbackground="#ffffff", borderwidth=1, relief="solid")
            self.style.configure("TLabel", background="#2a2d2f", foreground="#ffffff")
            self.style.configure("TButton", background="#3c3f41", foreground="#ffffff")
            self.style.configure("TCombobox", fieldbackground="#3c3f41", foreground="#ffffff")
            if hasattr(self, 'font_size_combobox'):
                self.style.configure("TCombobox", fieldbackground="#3c3f41", foreground="#ffffff")
                self.font_size_combobox.configure(style="darkly.TCombobox")
        else:
            self.main_frame.configure(style="flatly.TFrame")
            self.hex_text.configure(bg="white", fg="black", insertbackground="black", borderwidth=1, relief="solid")
            self.output_text.configure(bg="white", fg="black", insertbackground="black", borderwidth=1, relief="solid")
            self.style.configure("TLabel", background="white", foreground="black")
            #self.style.configure("TButton", background="lightgray", foreground="black")
            self.style.configure("TCombobox", fieldbackground="white", foreground="black")
            if hasattr(self, 'font_size_combobox'):
                self.style.configure("TCombobox", fieldbackground="white", foreground="black")
                self.font_size_combobox.configure(style="flatly.TCombobox")

    def apply_theme(self, dark_mode=None):
        if dark_mode is not None:
            self.dark_mode = dark_mode  # Actualizar el estado local si se pasa un nuevo valor
        elif hasattr(self, 'parent_menu'):  # Usar el valor actual de MainMenu si no se pasa
            self.dark_mode = self.parent_menu.dark_mode
        # Forzar la actualización de estilos incluso si dark_mode no cambia
        self.apply_styles(self.dark_mode)
        self.root.update_idletasks()  # Asegurar que los cambios se reflejen inmediatamente

    def hex_to_bin(self, hex_data):
        try:
            hex_data = hex_data.replace(" ", "").replace("\n", "").strip()
            if not hex_data:
                raise ValueError("La cadena hexadecimal está vacía después de limpiar.")
            if not all(c in "0123456789abcdefABCDEF" for c in hex_data):
                raise ValueError("La cadena contiene caracteres no hexadecimales.")
            return binascii.unhexlify(hex_data)
        except binascii.Error as e:
            raise ValueError(f"Error al convertir hexadecimal a binario: {e}")

    def decompress_gz_in_memory(self, bin_data):
        try:
            return gzip.decompress(bin_data)
        except OSError as e:
            raise ValueError(f"Error al descomprimir los datos: {e}")

    def process_data(self, event=None):
        try:
            hex_data = self.hex_text.get("1.0", tk.END).strip()
            if not hex_data:
                raise ValueError("Por favor, ingrese una cadena hexadecimal.")
            bin_data = self.hex_to_bin(hex_data)
            decompressed_data = self.decompress_gz_in_memory(bin_data)
            decompressed_text = decompressed_data.decode('utf-8')
            self.decompressed_content = decompressed_text
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, decompressed_text)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except UnicodeDecodeError:
            messagebox.showerror("Error", "Los datos descomprimidos no son texto legible. Ajusta la decodificación si es necesario.")

    def format_json(self, event=None):
        try:
            if not self.decompressed_content:
                raise ValueError("Primero procesa una cadena hexadecimal.")
            json_data = json.loads(self.decompressed_content)
            formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, formatted_json)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "El contenido descomprimido no es un JSON válido.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def copy_to_clipboard(self, event=None):
        try:
            content = self.output_text.get("1.0", tk.END).strip()
            if not content:
                raise ValueError("No hay contenido para copiar.")
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Éxito", "Contenido copiado al portapapeles.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def change_font_size(self, event=None):
        try:
            size = int(self.font_size_combobox.get())
            self.style.configure("TLabel", font=("Helvetica", size))
            self.style.configure("TButton", font=("Helvetica", size))
            self.style.configure("TCombobox", font=("Helvetica", size))
            self.hex_text.configure(font=("Courier New", size))
            self.output_text.configure(font=("Helvetica", size))
        except ValueError:
            messagebox.showerror("Error", "Seleccione un tamaño de fuente válido.")

    class ToolTip:
        def __init__(self, widget, text, parent):
            self.widget = widget
            self.text = text
            self.parent = parent
            self.tooltip_window = None
            self.widget.bind("<Enter>", self.show_tooltip)
            self.widget.bind("<Leave>", self.hide_tooltip)

        def show_tooltip(self, event=None):
            if self.tooltip_window:
                self.tooltip_window.destroy()
            x, y = self.widget.winfo_pointerxy()
            self.tooltip_window = tk.Toplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{x+10}+{y+10}")
            bg_color = "#353535" if self.parent.dark_mode else "#ffffe0"
            label = tk.Label(self.tooltip_window, text=self.text, background=bg_color, borderwidth=1, relief="solid", font=("Helvetica", 10))
            label.pack()

        def hide_tooltip(self, event=None):
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None