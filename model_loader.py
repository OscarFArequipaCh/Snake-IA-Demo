"""Carga y validación del modelo entrenado, sin alterar el archivo PKL."""

import os
import pickle

import numpy as np

from config import RUTA_MODELO

VERSION_ESPERADA = 4
CLAVES_ESPERADAS = {'version', 'tabla_q', 'config', 'historial', 'epsilon'}


def _ruta_absoluta(ruta):
    if os.path.isabs(ruta):
        return ruta
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), ruta)


def validar_modelo(datos):
    """Comprueba la estructura mínima necesaria para jugar."""
    if not isinstance(datos, dict):
        raise ValueError('El PKL no contiene un diccionario')

    faltan = CLAVES_ESPERADAS - set(datos.keys())
    if faltan:
        raise ValueError('Faltan claves en el PKL: {}'.format(sorted(faltan)))

    if datos['version'] != VERSION_ESPERADA:
        raise ValueError('Versión inesperada: {}'.format(datos['version']))

    config = datos['config']
    if config.get('grid_size') != 15:
        raise ValueError('El tablero entrenado no es de 15 x 15')
    if config.get('umbrales_distancia') != [3, 5]:
        raise ValueError('Los umbrales de distancia no coinciden con el agente')
    if config.get('umbrales_longitud') != [6, 11, 21, 41, 81]:
        raise ValueError('Los umbrales de longitud no coinciden con el agente')
    for clave in ('reward_food', 'reward_collision', 'reward_step', 'max_steps_per_episode'):
        if clave not in config:
            raise ValueError('Falta el parámetro {} en la configuración'.format(clave))

    tabla = datos['tabla_q']
    if not isinstance(tabla, dict) or not tabla:
        raise ValueError('La tabla Q está vacía o no es un diccionario')

    for clave, valores in tabla.items():
        if not isinstance(clave, tuple) or len(clave) != 12:
            raise ValueError('Clave de estado inválida: {}'.format(clave))
        if not isinstance(valores, np.ndarray) or valores.shape != (3,):
            raise ValueError('Valores Q inválidos para la clave {}'.format(clave))
        if not np.isfinite(valores).all():
            raise ValueError('Valores Q no finitos en la clave {}'.format(clave))

    return True


def cargar_modelo(ruta=RUTA_MODELO):
    """Lee el PKL en modo binario y devuelve el diccionario validado."""
    ruta = _ruta_absoluta(ruta)
    if not os.path.exists(ruta):
        raise FileNotFoundError('No existe el archivo: {}'.format(ruta))

    with open(ruta, 'rb') as archivo:
        datos = pickle.load(archivo)

    validar_modelo(datos)
    return datos
