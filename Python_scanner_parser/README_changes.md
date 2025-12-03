## Cambios recientes (soporte bool, %, ==, correcciones de control de flujo)

- Gramática (`Patito.g4`):
  - Se añadieron tipo `bool`, literales `true`/`false`.
  - Operadores nuevos: módulo `%` y comparación `==`.
  - Se regeneraron los artefactos ANTLR (`PatitoLexer.py`, `PatitoParser.py`, etc.).

- Memoria virtual (`virtual_memory.py`, `README.md`):
  - Se agregó segmento de constantes `const_bool` y se desplazaron `const_string` y temporales (`temp_*`).
  - Mapa actualizado: `const_int` 7000-7999, `const_float` 8000-8999, `const_bool` 9000-9999, `const_string` 10000-10999; temporales inician en 11000.

- Opcodes y VM (`opcodes.py`, `virtual_machine.py`):
  - Nuevos opcodes para `%` y `==`.
  - Ejecución de VM ahora soporta `%` y `==`.

- Semántica (`semantics.py`):
  - Cubo semántico extendido para `%`, `==` y tipo `bool`.
  - Asignaciones permiten `bool` y coerción implícita `int -> float` sigue igual.

- Listener (`PatitoSemanticListener.py`):
  - Soporte de constantes booleanas; tabla de constantes separa por tipo (addr -> valor).
  - Corrección en generación de saltos para condiciones: las expr con relop generan `GOTOF` en `exitRelExpr`, evitando saltos prematuros.
  - Manejo robusto de `if/while` sin relop (evalúa truthiness del expr).

- Ejecución/instalación:
  - Dependencia necesaria: `antlr4-python3-runtime`.
  - Regenerar gramática si modificas `Patito.g4`: `java -Xmx500M -cp "antlr-4.13.2-complete.jar:." org.antlr.v4.Tool -Dlanguage=Python3 Patito.g4`
  - Ejecutar programas: `python main.py test_1.txt` (o el archivo de prueba deseado).

- Resultado esperado con los tests incluidos:
  - `test_1.txt` (fibonacci 9) → `34`
  - `test_2.txt` (factorial 5) → `120`
  - `test_3.txt` (`esPar(7)`) → imprime que 7 es impar y el resto de la lógica.
