# Semantic Plan Compiler

[Français](README.md) · [English](README.en.md)

**Compilar decisiones cerradas en cálculos exactos, preguntas enfocadas, revisión humana y tablas SQLite trazables.**

Un contrato JSON declara columnas, opciones y dependencias. El compilador valida el grafo, calcula importes en código, comparte preguntas idénticas y agrupa las de contexto idéntico. Cambios de fila o política invalidan el trabajo afectado; la confianza insuficiente bloquea decisiones dependientes.

## Probar sin clave

Python 3.11+; proveedor explícitamente ficticio en la demostración.

```sh
git clone https://github.com/gbesse/semantic-plan-compiler
cd semantic-plan-compiler
python3 -m semantic_plan serve --lang es
```

Abrir `http://127.0.0.1:8774/?lang=es`. Ambos ejecutores funcionan realmente sobre cuatro peticiones sintéticas. El ingenuo hace una llamada por celda semántica activa, sin caché ni agrupación; el compilado comparte preguntas y contextos. Los números no son animaciones.

| Pasada del proveedor ficticio | Llamadas | Preguntas |
| ----------------------------- | -------: | --------: |
| Plan ingenuo ejecutado        |       15 |        15 |
| Compilado, primera pasada     |        4 |         6 |
| Misma entrada, caché caliente |        0 |         0 |
| Un mensaje modificado         |        2 |         3 |
| Nueva versión de política     |        4 |         6 |
| Confianza ficticia 0,6        |        2 |         4 |

El último caso exige revisión y bloquea las cuatro rutas dependientes; ninguna ruta se inventa silenciosamente. Las trazas muestran columnas enviadas y preguntas exactas. El SQL consulta realmente decisiones materializadas. El JSON incluye ambos planes, resultados, procedencia y contrato de entrada.

![Plan](docs/preview-fr.png)

```sh
python3 -m semantic_plan demo --lang es
python3 -m semantic_plan run semantic_plan/examples/es.json .local/decisions.sqlite
python3 -m semantic_plan plan contrato.json
python3 -m semantic_plan query .local/decisions.sqlite consulta.sql
```

Crear `.local/` antes de usar esa ruta. `run` usa proveedor ficticio; `live` hace peticiones de pago explícitas. `pip install .` instala `semantic-plan`. Interfaz, errores, contratos y ejemplos FR/EN/ES; nunca traduce datos del usuario.

## Contratos y caché

Dos nodos alfa: `subtract`, resta exacta de dos columnas enteras, y `choice`, elección cerrada con instrucciones y descripciones. Las dependencias forman un DAG; `when` condiciona un nodo a una elección padre declarada. Campos desconocidos, ciclos, columnas ausentes y tipos incoherentes se rechazan.

El plan calcula `amount_due`, clasifica tema, reutiliza el juicio para `topic_copy`, clasifica urgencia y enruta solo peticiones de factura. Solo la ruta recibe `customer_tier`; nunca se envía `unused_private_note`. Las respuestas compartidas conservan procedencia por fila.

La caché representa **la petición completa**: proveedor, modelo fijado, versión de política, estado proyectado y lote entero de preguntas. Cambiar una pregunta invalida también sus hermanas: el modelo podría depender de su presencia. Proveedores ficticios y reales usan espacios separados; respuestas ficticias nunca se convierten en resultados Jev reales. El umbral se reaplica localmente sin afirmar calibración. Errores y respuestas mal formadas no se guardan.

Presupuestos limitan intentos, preguntas y caracteres de petición. Los tokens se informan **tras la respuesta**, no como predicción garantizada. Un error puede haberse facturado: `usage_complete: false` lo señala. Respuestas válidas pueden guardarse antes de agotar presupuesto; quedan registradas celdas sin decidir. Sin reintentos automáticos.

Tablas SQLite `runs`, `decisions`, `cache`; valores exactos como texto para evitar desbordamiento SQLite. `query` es de solo lectura, con funciones permitidas y límites de instrucciones y filas. La base contiene decisiones y contextos proyectados; tratarla como datos privados locales.

## Ejecutar Jev explícitamente

```sh
pip install .
mkdir -p .local
# Proporcionar TYPESAFE_API_KEY mediante entorno, nunca en el contrato.
python3 -m semantic_plan live semantic_plan/examples/es.json .local/live.sqlite
```

Endpoint fijo `https://api.typesafe.ai/v1/systemone`, modelo `jev-1.13.0`, TLS verificado, timeout 30 s, sin redirecciones ni reintentos. CLI limita a cuatro llamadas y seis preguntas; contratos mayores pueden quedar pendientes de revisión. La biblioteca `execute` expone presupuestos. [Documentación TypeSafe](https://docs.typesafe.ai/primitives/choice). La interfaz no hace llamadas de pago.

[La prueba real](docs/live-jev-evidence.json) con cuatro peticiones sintéticas francesas terminó con **cuatro llamadas, seis preguntas, 1 768 tokens de entrada y 228 de salida**. Valida integración y materialización, no calidad general. No hubo comparación Jev ingenuo/compilado con corpus humano anotado. Proyecto independiente, no afiliado a TypeSafe AI.

## Trabajos previos y límites

[LOTUS](https://lotus-ai.readthedocs.io/en/latest/core_concepts.html) y [Palimpzest](https://github.com/mitdbg/palimpzest) ya ofrecen operadores semánticos y optimización. Es un **compilador pequeño de contratos cerrados verificables**, no sustituto ni backend integrado validado. Enfoca contrato → contexto exacto → presupuesto → abstención → procedencia SQL, con ejemplo instalable.

Caché, subexpresiones comunes y agrupación reutilizan juicios; no conservan muestras estocásticas independientes. La equivalencia se prueba solo con proveedor ficticio. Menos llamadas no demuestra igual calidad, menor latencia ni superioridad SOTA. Umbral 0,8 ilustrativo, sin calibración humana. Sin generación libre, joins semánticos generales, destilación, agente con herramientas ni producción.

## Verificar

```sh
python3 -m unittest discover -s tests -v
npm ci
npx playwright install chromium
npm run test:browser
npm run format:check
```

Diecisiete pruebas: grafo, presupuestos, caché completa y espacios, invalidación por fila/política/lote, errores, enteros grandes exactos, revisión y SQL de solo lectura. El ingenuo hace quince llamadas ficticias reales y obtiene las mismas categorías/valores del ejercicio compilado. Navegador FR/EN/ES: cinco modos, SQL, exportación, protección `.env` y móvil. CI Python 3.11/3.12 y rueda fuera de fuentes. MIT; alfa pública.
