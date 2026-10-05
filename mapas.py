# mapas.py
import configuracio

_m1 = (
    "1111111111111"
    "1000022200001"
    "1010101010101"
    "1202222222021"
    "1010121210101"
    "1202220222021"
    "1010121210101"
    "1002222222001"
    "1010101010101"
    "1111111111111"
)

_m2 = (
    "1111111111111"
    "1002222222001"
    "1011110111101"
    "1210022200121"
    "1210121210121"
    "1210120210121"
    "1210022200121"
    "1011110111101"
    "1002222222001"
    "1111111111111"
)

_m3 = (
    "1111111111111"
    "1000200020001"
    "1010101010101"
    "1210201020121"
    "1210121210121"
    "1210121210121"
    "1210201020121"
    "1010101010101"
    "1000200020001"
    "1111111111111"
)

def _convertir_a_matriz(cadena_mapa):
    lista_enteros = [int(caracter) for caracter in cadena_mapa]
    return [lista_enteros[i:i + configuracio.COLUMNAS] 
            for i in range(0, len(lista_enteros), configuracio.COLUMNAS)]

MAPA_1 = _convertir_a_matriz(_m1)
MAPA_2 = _convertir_a_matriz(_m2)
MAPA_3 = _convertir_a_matriz(_m3)