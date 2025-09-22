import gzip
import binascii
from io import BytesIO

# Tu cadena hexadecimal (puedes reemplazarla por la completa)
hex_data = """
1f8b0800000000000003ad53db8eda3010fd152b4fad0459df72314f0d21489102a181ddad04280ac16d23858412ef56ea3ff5a99fb03fd671082c50f50d6b34b6673c93393327cba5d114dfaa4cbd1c64aa0e59d564b92aea2a6de48f1759e5d2e819d3e0d9a6364eb582c55c91524c2dec1027259c706ea58e8bdf1fc2e9391c87b011414d62bb26618e49b1a32d6e7f63f7bf3a7d9bf737a05db0b9b6109461480ec14c80e5fd4b70d189bde3ee90e30ef26412939954879bd8e4178f8e4209c747e3ba774f8c3a75e7d0705a171c66493c0992d0f7d2275d13219432c6f92d162130673a90134aa0334270cae0eac7d3f963b4f0d2b9178de274f6385...
"""

# Limpia y convierte de hexadecimal a bytes
compressed_data = binascii.unhexlify(hex_data.replace("\n", "").strip())

# Descomprime usando gzip
with gzip.GzipFile(fileobj=BytesIO(compressed_data)) as f:
    decompressed_data = f.read()

# Intenta decodificar a texto legible
try:
    decoded_text = decompressed_data.decode("utf-8")
except UnicodeDecodeError:
    decoded_text = decompressed_data.decode("latin-1")  # Alternativa si utf-8 falla

# Muestra el texto plano
print(decoded_text)
