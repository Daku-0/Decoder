import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import binascii

# Definiciones de campos por versión de ISO 8583
FIELD_DEFINITIONS = {
    "ISO 8583:1987": {
        41: {"length": 8, "type": None, "desc": "Card Acceptor Terminal ID"},
        60: {"length": None, "type": "LLVAR", "desc": "Additional Data"},
        63: {"length": None, "type": "LLVAR", "desc": "Reserved for ISO"},
        64: {"length": 8, "type": None, "desc": "Message Authentication Code (MAC)"}
    },
    "ISO 8583:1993": {
        # Agregar definiciones específicas para 1993 si necesario
    },
    "ISO 8583:2003": {
        # Agregar definiciones específicas para 2003 si necesario
    }
}

class DecoderApp:
    def __init__(self, root, dark_mode, parent_menu):
        self.root = root
        self.root.title("Decoder Completo")
        self.root.minsize(600, 400)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.dark_mode = dark_mode
        self.parent_menu = parent_menu

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 10))
        self.style.configure("TButton", font=("Helvetica", 10), padding=5)
        self.style.configure("TCombobox", font=("Helvetica", 10))

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Etiqueta y campo de entrada hexadecimal
        self.hex_label = ttk.Label(self.main_frame, text="Ingrese la cadena hexadecimal del mensaje ISO 8583:", style="TLabel")
        self.hex_label.pack(fill=tk.X, pady=(0, 5))
        self.hex_text = tk.Text(self.main_frame, height=10, font=("Courier New", 12), wrap="none")
        self.hex_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Definir etiquetas de color para las partes decodificadas
        self.hex_text.tag_configure("mti", foreground="red")
        self.hex_text.tag_configure("bitmap", foreground="blue")
        self.hex_text.tag_configure("processing_code", foreground="purple")
        self.hex_text.tag_configure("field_41", foreground="green")
        self.hex_text.tag_configure("field_60", foreground="orange")
        self.hex_text.tag_configure("field_63", foreground="pink")
        self.hex_text.tag_configure("field_64", foreground="black")

        # Selección de versión
        self.version_label = ttk.Label(self.main_frame, text="Versión ISO 8583:", style="TLabel")
        self.version_label.pack(fill=tk.X, pady=(10, 5))
        self.version_combobox = ttk.Combobox(self.main_frame, values=["ISO 8583:1987", "ISO 8583:1993", "ISO 8583:2003"], state="readonly")
        self.version_combobox.set("ISO 8583:1987")
        self.version_combobox.pack(pady=5)

        # Botón de decodificación
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)

        self.decode_button = ttk.Button(self.button_frame, text="Decodificar", command=self.decode_data)
        self.decode_button.pack(side=tk.LEFT, padx=5)
        self.paste_button = ttk.Button(self.button_frame, text="Pegar Hex", command=lambda: self.hex_text.insert(tk.END, self.root.clipboard_get()))
        self.paste_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = ttk.Button(self.button_frame, text="Limpiar", command=self.clear_fields)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        self.Process_64 = ttk.Button(self.button_frame, text="Procesar Campo 64", command=self.process_field_64)
        self.Process_64.pack(side=tk.LEFT, padx=5)

        # Área de salida
        self.output_text = tk.Text(self.main_frame, height=10, font=("Helvetica", 12))
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Aplicar estilos manualmente
        self.apply_styles(self.dark_mode)

    def apply_styles(self, dark_mode):
        if dark_mode:
            self.main_frame.configure(style="darkly.TFrame")
            self.hex_text.configure(bg="#3c3f41", fg="#20ff02", insertbackground="#ffffff", borderwidth=1, relief="solid")
            self.output_text.configure(bg="#3c3f41", fg="#ffffff", insertbackground="#ffffff", borderwidth=1, relief="solid")
            self.style.configure("TLabel", background="#2a2d2f", foreground="#ffffff")
            self.style.configure("TCombobox", fieldbackground="#3c3f41", foreground="#ffffff")
        else:
            self.main_frame.configure(style="flatly.TFrame")
            self.hex_text.configure(bg="white", fg="black", insertbackground="black", borderwidth=1, relief="solid")
            self.output_text.configure(bg="white", fg="black", insertbackground="black", borderwidth=1, relief="solid")
            self.style.configure("TLabel", background="white", foreground="black")
            self.style.configure("TCombobox", fieldbackground="white", foreground="black")

    def apply_theme(self, dark_mode=None):
        if dark_mode is not None:
            self.dark_mode = dark_mode
        self.apply_styles(self.dark_mode)
        self.root.update_idletasks()
        
    def validate_hex_input(self, hex_data):
        """Valida que la entrada sea una cadena hexadecimal válida."""
        hex_data = hex_data.replace(" ", "").replace("\n", "").strip()
        if not hex_data:
            return False, "La cadena hexadecimal no puede estar vacía."
        if len(hex_data) % 2 != 0:
            return False, "La cadena hexadecimal debe tener una longitud par."
        if not all(c in "0123456789abcdefABCDEF" for c in hex_data):
            return False, "La cadena contiene caracteres no hexadecimales."
        return True, ""

    def hex_to_bin(self, hex_data):
        try:
            hex_data = hex_data.replace(" ", "").replace("\n", "").strip()
            if not hex_data or len(hex_data) % 2 != 0:
                raise ValueError("La cadena hexadecimal debe ser válida y tener una longitud par.")
            return binascii.unhexlify(hex_data)
        except binascii.Error as e:
            raise ValueError(f"Error al convertir hexadecimal a binario: {e}")

    def parse_bitmap(self, bin_data, start_pos):
        print(f"Parsing bitmap at pos {start_pos}, len(bin_data) = {len(bin_data)}")
        bitmap = bytearray()
        pos = start_pos
        if len(bin_data) < pos + 8:
            raise ValueError("Datos insuficientes para el bitmap primario.")
        bitmap.extend(bin_data[pos:pos + 8])
        pos += 8

        # Verificar si hay un bitmap secundario (bit 1 del primer byte)
        if bitmap[0] & 0x80 and len(bin_data) >= pos + 8:
            print("Secondary bitmap detected")
            bitmap.extend(bin_data[pos:pos + 8])
            pos += 8
        elif bitmap[0] & 0x80:
            raise ValueError("Datos insuficientes para el bitmap secundario.")

        bitmap_bits = ''.join(format(byte, '08b') for byte in bitmap)
        print(f"Bitmap bits: {bitmap_bits}")
        fields_present = [i + 1 for i, bit in enumerate(bitmap_bits) if bit == '1']
        print(f"Fields present: {fields_present}")
        return fields_present, pos

    def decode_field(self, bin_data, field_num, pos, length_type=None, length=None):
        print(f"length_type: {length_type}, length: {length}")
        print(f"Decoding field {field_num} at pos {pos}, len(bin_data) = {len(bin_data)}")
        if length_type == "LLVAR":
            if pos + 2 > len(bin_data):
                raise ValueError(f"Datos insuficientes para el campo {field_num} (LLVAR length).")
            length = int(bin_data[pos:pos + 2].hex().upper())
            print(f"Decoding field {field_num} at pos {pos}, len(bin_data) = {len(bin_data)}, length: {length}")
            pos += 2
            
            if pos + length > len(bin_data):
                raise ValueError(f"Datos insuficientes para el campo {field_num} (LLVAR value).")
            value = bin_data[pos: pos + length].decode('ascii', errors='ignore')
            print(f"old pos: {pos}")
            pos += length
            print(f"new pos: {pos}")
        elif length_type == "LLLVAR":
            if pos + 3 > len(bin_data):
                raise ValueError(f"Datos insuficientes para el campo {field_num} (LLLVAR length).")
            length = int.from_bytes(bin_data[pos:pos + 2], byteorder='big')
            pos += 3
            if pos + length > len(bin_data):
                raise ValueError(f"Datos insuficientes para el campo {field_num} (LLLVAR value).")
            value = bin_data[pos:pos + length].decode('ascii', errors='ignore')
            pos += length
        else:
            if pos + length > len(bin_data):
                raise ValueError(f"Datos insuficientes para el campo {field_num} (fixed length).")
            value = bin_data[pos:pos + length].hex().upper() if field_num == 64 else bin_data[pos:pos + length].decode('ascii', errors='ignore')
            pos += length
        print(f"Field {field_num} value: {value}, new pos: {pos}")
        return value, pos

    def decode_data(self):
        try:
            hex_data = self.hex_text.get("1.0", tk.END).strip()
            is_valid, error_msg = self.validate_hex_input(hex_data)
            if not is_valid:
                messagebox.showerror("Error de Validación", error_msg)
                return
            
            print(f"Input hex data: {hex_data}, length: {len(hex_data)}")
            bin_data = self.hex_to_bin(hex_data)
            print(f"Binary data length: {len(bin_data)}")
            output = []
            
            # Limpiar etiquetas previas en hex_text
            for tag in ["mti", "bitmap", "processing_code", "field_41", "field_60", "field_63", "field_64"]:
                self.hex_text.tag_remove(tag, "1.0", tk.END)

            # MTI (Message Type Indicator) - bytes 7 a 9 (2 bytes)
            mti_start = 7 * 3  # Cada byte ocupa 3 caracteres (2 hex + espacio)
            mti_end = 9 * 3
            self.hex_text.tag_add("mti", f"1.{mti_start}", f"1.{mti_end}")

            # MTI (Message Type Indicator) - 4 caracteres hexadecimales (2 bytes)
            if len(bin_data) < 9:
                raise ValueError("Datos insuficientes para el MTI.")
            mti = bin_data[7:9].hex().upper()
            output.append(f"000 MsgType: {mti}")
            pos = 9
            print(f"MTI: {mti}, pos: {pos}")

            # Parsear el bitmap
            fields_present, pos = self.parse_bitmap(bin_data, pos)
            bitmap_hex = bin_data[9:pos].hex().upper()
            
            bitmap_start = 9 * 3
            bitmap_end = pos * 3
            self.hex_text.tag_add("bitmap", f"1.{bitmap_start}", f"1.{bitmap_end}")
            if pos > 16:
                cont = 2
                bitmap_start = 0
                bitmap_end = (pos - 16) * 3
                self.hex_text.tag_add("bitmap", f"2.{bitmap_start}", f"2.{bitmap_end}")
            print(f"Bitmap end: {bitmap_end}, bitmap start: {bitmap_start}, pos: {pos}")
            
            output.append(f"001 Bitmap: {' '.join(bitmap_hex[i:i+2] for i in range(0, len(bitmap_hex), 2))}")
            print(f"Bitmap pos: {pos}")
            
            # Procecing code (Field 3) - 3 caracteres hexadecimales (1.5 bytes)
            if len(bin_data) < pos + 3:
                raise ValueError("Datos insuficientes para el campo 3 (Processing Code).")
            processing_code = bin_data[pos:pos + 3].hex().upper()
            pos += 3
            output.append(f"003 Processing Code: {processing_code}")
            print(f"Processing Code: {processing_code}, pos: {pos}")
            
            # Resaltar el campo de código de procesamiento en hex_text
            processing_code_end = (pos - 16) * 3 
            self.hex_text.tag_add("processing_code", f"{cont}.{bitmap_end}", f"{cont}.{processing_code_end}")
            
            # Usar definiciones basadas en la versión seleccionada
            version = self.version_combobox.get()
            field_definitions = FIELD_DEFINITIONS[version]
            
            # Inicializar el valor del campo 64
            self.field_64_value = None

            for field in fields_present:
                if field in field_definitions:
                    defn = field_definitions[field]
                    value, pos = self.decode_field(bin_data, field, pos, defn["type"], defn["length"])
                    if field == 64:
                        self.field_64_value = bin_data[pos-6:].hex().upper()
                        value = ' '.join(value[i:i+2] for i in range(0, len(value), 2))
                    output.append(f"{field:03d} {defn['desc']}: {value}")
                else:
                    print(f"Field {field} no definido en las especificaciones.")

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, "\n".join(output))
            print(f"Decoding complete, final pos: {pos}, output length: {len(output)}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            print(f"ValueError: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al decodificar: {e}")
            print(f"Exception: {e}")
            
    def clear_fields(self):
        self.hex_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        
    def paste_hex(self):
        try:
            hex_data = self.root.clipboard_get()
            if all(c in "0123456789abcdefABCDEF " for c in hex_data):
                self.hex_text.insert(tk.END, hex_data)
            else:
                messagebox.showerror("Error", "El contenido del portapapeles no es una cadena hexadecimal válida.")
        except tk.TclError:
            messagebox.showerror("Error", "No hay datos en el portapapeles.")
        
    def process_field_64(self):
        # Verificar si hay un valor del campo 64 disponible
        if not hasattr(self, 'field_64_value') or self.field_64_value is None:
            messagebox.showerror("Error", "Primero decodifica un mensaje para obtener el campo 64.")
            return

        # Obtener la instancia de BaseApp desde MainMenu
        base_app = self.parent_menu.get_base_app()
        if base_app:
            # Limpiar el campo de texto hexadecimal en BaseApp e insertar el valor del campo 64
            base_app.hex_text.delete("1.0", tk.END)
            base_app.hex_text.insert("1.0", self.field_64_value)
            # Opcional: procesar automáticamente los datos en BaseApp
            base_app.process_data()
        else:
            messagebox.showerror("Error", "No se pudo abrir la ventana de descompresión.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DecoderApp(root, False, None)
    root.mainloop()