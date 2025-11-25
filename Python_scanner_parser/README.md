**Pasos para correr el programa**

Generar los archivos relacionados con Patito.g4 (Scanner y Parser): java -Xmx500M -cp "antlr-4.13.2-complete.jar:." org.antlr.v4.Tool -Dlanguage=Python3 Patito.g4

Correr archivos con el programa: python main.py archivo_de_prueba.txt

## Mapa de Memoria de Ejecución

Se reservan bloques de 1000 direcciones contiguas por tipo/ámbito. Este esquema lo usa tanto el compilador (`virtual_memory.py`) como la Máquina Virtual (`execution_memory.py`).

- 1000-1999 `glob_int`, 2000-2999 `glob_float`, 3000-3999 `glob_bool`
- 4000-4999 `loc_int`, 5000-5999 `loc_float`, 6000-6999 `loc_bool`
- 7000-7999 `const_int`, 8000-8999 `const_float`, 9000-9999 `const_string`
- 10000-10999 `temp_int`, 11000-11999 `temp_float`, 12000-12999 `temp_bool`

En tiempo de ejecución:
- Los segmentos globales viven durante toda la corrida.
- Las constantes se cargan al inicializar la VM y son de solo lectura.
- Cada llamada a función crea un `ActivationRecord` nuevo con sus segmentos `loc_*` y `temp_*`; el segmento global no se toca.
