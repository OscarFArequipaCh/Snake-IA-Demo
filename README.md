# Snake AI Challenge

Aplicación de escritorio donde un jugador humano compite, al mismo tiempo, contra un agente de Q-Learning tabular entrenado previamente en Google Colab.

## Descripción

Se muestran dos tableros independientes de 15 × 15:

- **Izquierda:** agente IA, controlado por la tabla Q cargada desde `q_learning_snake_v4.pkl`.
- **Derecha:** jugador humano, controlado con las flechas del teclado.

Cada serpiente avanza a la misma velocidad y continúa jugando aunque la otra ya haya terminado. La partida concluye cuando ambas han chocado o alcanzado el límite de 30.000 pasos.

## Estructura

```text
Snake_AI_Demo/
├── main.py              Punto de entrada y ciclo de eventos.
├── menu.py              Menú principal y pantalla de resultados.
├── game.py              Coordinación de las dos partidas.
├── snake_env.py         Lógica del entorno Snake.
├── agent_q.py           Percepción del agente y política greedy de solo consulta.
├── model_loader.py      Carga y validación del PKL.
├── renderer.py          Dibujo con Pygame.
├── config.py            Configuración visual y parámetros generales.
├── assets/              Directorios de recursos (vacíos en esta versión).
├── q_learning_snake_v4.pkl
├── Snake_AI_Q_Learning_VF.ipynb
├── requirements.txt
└── README.md
```

El notebook y el archivo PKL originales no se modifican ni se usan para reentrenar.

## Cómo funciona el agente

El agente conserva la representación de estado de 12 características del notebook:

1. Distancia libre al frente, a la derecha y a la izquierda.
2. Dirección actual como one-hot (`arriba`, `abajo`, `izquierda`, `derecha`).
3. Comida a la izquierda, derecha, arriba y abajo.
4. Categoría de longitud de la serpiente.

En cada movimiento se repite la secuencia original: estado → clave de 12 enteros → consulta a la tabla Q → acción con mayor valor Q → ejecución en el entorno. Las acciones son `0` (recto), `1` (girar derecha) y `2` (girar izquierda).

Durante la partida se usa una política **greedy** (`epsilon = 0`) inspirada en la función `evaluar` del notebook. La tabla Q solo se lee: no se insertan claves nuevas, no se actualizan valores y no se explora. Si el estado no existe en la tabla, se elige la acción `0` y el panel lo indica visualmente.

La configuración efectiva (tamaño del tablero, recompensas y umbrales) se toma del diccionario guardado en el PKL, que es la fuente de verdad del modelo entrenado.

## Cómo cargar el modelo

`model_loader.py` abre el PKL en modo lectura binaria, verifica la versión `4`, la presencia de `version`, `tabla_q`, `config`, `historial` y `epsilon`, y comprueba que cada clave tenga 12 enteros y cada valor un vector de 3 componentes. El archivo nunca se sobrescribe.

## Ejecución

```bash
pip install -r requirements.txt
python main.py
```

En Python 3.14 se instala `pygame-ce`, que expone el mismo módulo `pygame` y dispone de ruedas para esa versión. En versiones anteriores se instala `pygame`.

## Controles

| Tecla | Acción |
| --- | --- |
| Flecha arriba | Mover hacia arriba |
| Flecha derecha | Mover hacia la derecha |
| Flecha abajo | Mover hacia abajo |
| Flecha izquierda | Mover hacia la izquierda |

No se permite girar directamente en sentido contrario. El botón **STOP** de la esquina superior derecha detiene ambas serpientes de inmediato y muestra los resultados, útil si el agente entra en un ciclo repetitivo. En la pantalla de resultados, el botón **VOLVER AL MENÚ PRINCIPAL** permite iniciar otra partida sin reiniciar el programa.

## Verificación

Para comprobar la carga del modelo, la compatibilidad del estado con el notebook, la política greedy, los controles y las pantallas:

```bash
python verificar.py
```

El script usa un controlador de vídeo ficticio, por lo que no abre ventanas y no modifica el PKL.

## Dependencias

- Python 3.10 o superior.
- NumPy.
- Pygame (o pygame-ce en Python 3.14).

No se utilizan PyTorch, imágenes, sonidos ni recursos externos.
