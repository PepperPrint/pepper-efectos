# Capas de texto · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sumar a Pepper Efectos capas de texto con mezcla de tipografías por letra, arriba o abajo de la foto, con interruptor "Le pegan los efectos", edición directa de letras y exportación PNG/SVG.

**Architecture:** Todo el código nuevo vive en `index.html` (sección `TEXTO` del script, entre "FIN EFECTOS" y el estado). Las tipografías se embeben en `fonts/fonts.js` (base64, cargado con `<script src>` para que funcione con doble clic sobre `file://`) y se leen con opentype.js (`lib/opentype.min.js`). Las letras se dibujan siempre desde los contornos de opentype (canvas vía `Path2D`, SVG vía `<path>`), así pantalla, PNG y SVG coinciden exacto y no hace falta cargar fuentes por CSS. La composición reemplaza la llamada directa a `runPipeline` en `render()` y `exportPNG()`.

**Tech Stack:** HTML/JS vanilla en un archivo, opentype.js 1.3.x vendoreado, fuentes OFL de @fontsource (archivos `.woff`, subset latin), tests con Python + pytest + Playwright (Chrome del sistema, `channel="chrome"`), sobre `file://`.

**Spec:** `docs/superpowers/specs/2026-11-24-texto-design.md`

## Global Constraints

- Nada de build ni bundler para usar la web: `index.html` + `fonts/fonts.js` + `lib/opentype.min.js`, abrible con doble clic y en GitHub Pages.
- Las fotos nunca salen del navegador.
- Solo tipografías con licencia libre (OFL / Apache). Copiar el `LICENSE` de cada paquete a `fonts/licencias/`.
- No modificar el `apply` de ninguno de los 27 efectos existentes.
- Textos de interfaz en español rioplatense ("Tocá", "Arrastrá"), estética de panel Riso existente (clases `module`, `mod-label`, `btn`, `card`).
- Coordenadas de capas de texto en fracciones del lienzo (0–1), para que vista previa reducida y exportación a resolución completa coincidan.
- Ajustes `.json`: pasar a `version: 2` con `texts: []`; un `.json` / `localStorage` `version: 1` debe seguir cargando.

## Review Focus

1. **Acentos y signos del castellano (á é í ó ú ñ ü ¿ ¡) y caracteres que la tipografía no tiene (emoji, ∞):** cada letra se dibuja con una tipografía que sí tenga el glifo; si ninguna lo tiene, se saltea sin romper. → test en Task 2.
2. **Texto vacío, solo espacios o saltos de línea dobles:** no rompe el render ni el SVG. → test en Task 2.
3. **Foto grande (6000 px) vs vista previa reducida:** el texto queda en la misma posición relativa y tamaño proporcional en el PNG exportado. → test en Task 3.
4. **Ajustes viejos (`version: 1`) en `localStorage` o `.json`:** cargan sin error y con `texts: []`. → test en Task 4.
5. **Celular / pantalla táctil:** tocar una letra la selecciona y arrastrar un tirador la estira, con `touch-action: none` en la capa de edición para que no scrollee la página. → test en Task 5 (contexto Playwright `has_touch=True`).

---

### Task 0: Arnés de pruebas

**Files:**
- Create: `tests/conftest.py`, `tests/test_smoke.py`, `requirements-dev.txt` (`pytest`, `playwright`)

**Interfaces:**
- Produces: fixture `page` (Playwright, Chrome del sistema, viewport 1280×800) que abre `file://<repo>/index.html` y espera `window.__textoReady === true` *si existe la variable* (antes de Task 1 solo espera `load`). Helper `load_image(page, w, h, rgba=(r,g,b,a), transparent_rect=None)` que crea un canvas en la página, lo pasa por la misma función que usa "Abrir imagen" (buscar la función que asigna `srcFull`/`srcPreview` desde un archivo/imagen y reutilizarla; si está inline en un handler, extraerla a `function setSourceCanvas(canvas, name)` sin cambiar su comportamiento) y espera el render.
- Produces: fixture `touch_page` igual con `has_touch=True, is_mobile=True`, viewport 390×844.

- [ ] **Step 1:** `test_smoke.py::test_carga_sin_errores` — abre la página, junta `pageerror` y `console` de tipo error; assert lista vacía y `EFFECTS` tiene 27 claves (`page.evaluate("Object.keys(EFFECTS).length") == 27`).
- [ ] **Step 2:** `test_smoke.py::test_render_imagen` — `load_image(page, 200, 100)`; assert `page.evaluate("out.width") == 200` (vista previa a resolución completa activada por el helper).
- [ ] **Step 3:** Correr `python -m pytest tests -q` → PASS (la extracción de `setSourceCanvas`, si hizo falta, no cambia comportamiento).
- [ ] **Step 4:** Commit `test: arnés Playwright para Pepper Efectos`.

### Task 1: Tipografías embebidas y opentype

**Files:**
- Create: `tools/build-fonts.mjs`, `fonts/fonts.js` (generado), `fonts/licencias/*`, `lib/opentype.min.js`, `tests/test_fonts.py`
- Modify: `index.html` (dos `<script src>` antes del script principal; sección `TEXTO` con carga de fuentes)

**Interfaces:**
- Produces (fonts.js): `window.PEPPER_FONT_DATA = [{ id: 'anton-400', family: 'Anton', weight: 400, style: 'Condensada', b64: '...' }, ...]`.
- Produces (index.html): `const FACES = []` con `{ id, family, weight, style, font /* opentype.Font */, heaviness /* 0..1 */ }`, ordenado por `heaviness` ascendente; `function faceById(id) -> face|undefined`; `function faceHasGlyph(face, ch) -> boolean`; `window.__textoReady = true` cuando `FACES` está lista.

- [ ] **Step 1:** `test_fonts.py::test_fuentes_cargadas` — assert `FACES.length >= 14`, todas con `font.unitsPerEm > 0`, ids únicos.
- [ ] **Step 2:** `test_fonts.py::test_heaviness_ordena` — assert heaviness de `inter-900` > `inter-100`, y `FACES` ordenada ascendente.
- [ ] **Step 3:** `test_fonts.py::test_acentos` — para cada face assert `faceHasGlyph(face, 'ñ')` y `faceHasGlyph(face, '¿')` (si alguna falla, sacarla de la lista).
- [ ] **Step 4:** Correr → FAIL (`FACES` no existe).
- [ ] **Step 5:** `npm i --no-save opentype.js@1 @fontsource/{anton,bebas-neue,archivo-black,archivo,big-shoulders-display,fraunces,playfair-display,instrument-serif,space-grotesk,syne,unbounded,rubik-mono-one,shrikhand,dm-serif-display,climate-crisis,inter}` en un directorio temporal fuera del repo. `tools/build-fonts.mjs` toma de cada paquete los archivos `files/*-latin-<peso>-normal.woff` de estos pesos (si no existe, el más cercano): Archivo 100/900, Big Shoulders Display 100/900, Fraunces 100/900, Playfair Display 400/900, Space Grotesk 300/700, Syne 400/800, Unbounded 200/900, Inter 100/900, y peso 400 para el resto; escribe `fonts/fonts.js`. Copiar `dist/opentype.min.js` a `lib/` y los `LICENSE` a `fonts/licencias/<paquete>.txt`.
- [ ] **Step 6:** En `index.html`: decodificar base64 → `ArrayBuffer` → `opentype.parse`; `heaviness` = proporción de píxeles con tinta al dibujar `"Hamburgefonstiv"` con la fuente en un canvas de 400×100 a tamaño de em 80, normalizada min–max entre todas las faces. Si `opentype` o `PEPPER_FONT_DATA` no están, la sección Texto muestra "No se pudieron cargar las tipografías" y el resto de la web sigue andando.
- [ ] **Step 7:** Correr `python -m pytest tests -q` → PASS.
- [ ] **Step 8:** Commit `feat(texto): tipografías libres embebidas + opentype`.

### Task 2: Modelo de capa, reparto de tipografías y maquetado

**Files:**
- Modify: `index.html` (sección `TEXTO`)
- Create: `tests/test_layout.py`

**Interfaces:**
- Produces:
  - `function newTextLayer(opts) -> TextLayer` con defaults: `{ uid, text: 'HACELO TUYO', x: 0.5, y: 0.5, size: 0.12 /* alto de em como fracción del alto del lienzo */, rotation: 0, position: 'arriba' /* | 'abajo' */, fx: false, color: '#e8352b', align: 'center', reparto: 'parejo', face: FACES[FACES.length-1].id, seed: <entero aleatorio>, tracking: 0 /* em */, lineHeight: 1.0, letters: {} }`.
  - `letters` es un objeto indexado por posición de carácter en `text`: `{ face?, sx: 1, sy: 1, rot: 0, outline: false }`; solo se guardan letras con cambios.
  - `const REPARTOS = [['una','Una sola'],['parejo','Parejo'],['extremos','Extremos (fina ↔ gruesa)'],['pesado','Tirando a pesado'],['liviano','Tirando a liviano'],['ola','Ola'],['rampa','Rampa fina → gruesa'],['rampa-linea','Rampa por línea'],['alternado','Alternado fina / gruesa']]`.
  - `function assignFaces(layer) -> string[]` (un face id por carácter de `layer.text`; `letters[i].face` tiene prioridad; si el face elegido no tiene el glifo, usar el face de heaviness más cercano que sí lo tenga; si ninguno, `null`).
  - `function layoutText(layer, W, H) -> { glyphs: Glyph[], box: {x,y,w,h} }` donde `Glyph = { i, ch, faceId, x, y /* línea base, px */, adv /* px */, size /* px */, sx, sy, rot, outline, path /* opentype.Path ya transformado a px */ }`. Espacios y caracteres con face `null` no producen glyph pero los espacios sí avanzan.
- Reparto (sobre `FACES` ordenadas por heaviness, `rand` = PRNG mulberry32 con `layer.seed`; `t` en 0..1 → face `FACES[round(t*(n-1))]`): `una` → `layer.face`; `parejo` → `t = rand()`; `extremos` → face del primer o último tercio, al azar; `pesado` → `t = 1 - rand()²`; `liviano` → `t = rand()²`; `ola` → `t = (sin(2π·k/6)+1)/2` con `k` índice de letra no-espacio; `rampa` → `t = k/(N-1)`; `rampa-linea` → igual pero por línea; `alternado` → `k` par: face al azar de la mitad liviana, impar: de la pesada.
- Maquetado: tamaño en px `S = layer.size * H`; avance de cada letra = `advanceWidth/unitsPerEm * S * sx + tracking*S`; altura de línea = `lineHeight * S * max(sy de la línea)`; líneas alineadas según `align` y el bloque centrado en `(x*W, y*H)`, luego rotado `rotation` grados alrededor de ese centro; cada letra con `sy` se estira hacia arriba desde la línea base y con `rot` rota sobre su centro.

- [ ] **Step 1:** `test_layout.py::test_reparto_deterministico` — mismo `seed` → mismo `assignFaces`; otro seed → distinto (texto de 20 letras).
- [ ] **Step 2:** `::test_rampa_no_decrece` — `reparto:'rampa'`, heaviness de los faces asignados no decreciente.
- [ ] **Step 3:** `::test_alternado` — letras pares en la mitad liviana, impares en la pesada.
- [ ] **Step 4:** `::test_estirar_corre_vecinas` — texto `'AB'`, con `letters[0].sx = 2` el `x` de `B` aumenta exactamente en el `adv` original de `A` (tolerancia 0.01 px).
- [ ] **Step 5:** `::test_acentos_y_emoji` — texto `'¿Año ñandú? 🌶'`: no lanza error; hay glyph para cada letra con acento; el emoji no produce glyph.
- [ ] **Step 6:** `::test_vacio` — textos `''`, `'   '`, `'A\n\nB'` → no lanzan error; el primero da `glyphs.length === 0`.
- [ ] **Step 7:** Correr → FAIL.
- [ ] **Step 8:** Implementar `newTextLayer`, `REPARTOS`, `assignFaces`, `layoutText`.
- [ ] **Step 9:** Correr → PASS. Commit `feat(texto): modelo de capa, reparto y maquetado`.

### Task 3: Dibujo y composición con la foto y los efectos

**Files:**
- Modify: `index.html` (`render()`, `exportPNG()`, estado, sección `TEXTO`, botón "Empezar sin foto" en el módulo Original)
- Create: `tests/test_compose.py`

**Interfaces:**
- Consumes: `layoutText`, `runPipeline(srcCanvas, scale, opts)` (sin cambios).
- Produces:
  - `state.texts = []` (array de `TextLayer`, orden = orden de dibujo dentro de cada grupo).
  - `function drawTextLayer(ctx, layer, W, H)` — rellena con `layer.color`; letras con `outline` → solo trazo de `max(1, S*0.03)` px.
  - `function renderComposition(src, scale, opts) -> ImageData`, que reemplaza a `runPipeline(...)` en `render()` y `exportPNG()`. Grupos: `belowFx`, `aboveFx`, `belowClean`, `aboveClean`. Pasos: lienzo pre = belowFx + foto + aboveFx → `runPipeline(pre, scale, { transparentPaper: opts.transparentPaper || belowClean.length > 0 })` → lienzo final: si `belowClean.length > 0 && !opts.transparentPaper`, fondo `#ffffff`; luego belowClean, el resultado de efectos, aboveClean.
  - `function needsCutoutWarning() -> boolean`: hay alguna capa `abajo` y la foto (muestra de 64×64) no tiene ningún píxel con alfa < 250.
  - `function startBlankCanvas()` — `setSourceCanvas` con un canvas blanco de 1080×1350 y nombre `'texto'`; botón "Empezar sin foto" en el módulo Original.

- [ ] **Step 1:** `test_compose.py::test_texto_limpio_arriba` — foto roja 400×400, sin efectos activos, capa `arriba`, `fx:false`, color `#000000`, texto `'█'` o `'H'` grande centrado: el píxel central del `out` es negro.
- [ ] **Step 2:** `::test_texto_fx_pasa_por_efecto` — pipeline = un solo efecto `posterize` (o el que invierta o cambie el color de forma comprobable); capa `fx:true` color `#ff00ff`: el píxel central del `out` ≠ `#ff00ff`; con `fx:false` == `#ff00ff`.
- [ ] **Step 3:** `::test_texto_abajo_tapado_y_aviso` — foto opaca + capa `abajo` → `needsCutoutWarning() === true` y el píxel central es el de la foto.
- [ ] **Step 4:** `::test_texto_abajo_con_recorte` — foto 400×400 con su mitad izquierda transparente, efecto `retro` activo, capa `abajo` `fx:false` negra centrada en `x:0.25`: el píxel en (100,200) es negro y uno sin texto en la mitad izquierda es blanco.
- [ ] **Step 5:** `::test_proporcional_en_exportacion` — foto 6000×4000 con vista previa reducida: capturar la caja del texto (bbox de píxeles negros) en `out` y en `renderComposition(srcFull, 1, {})`; las posiciones relativas (bbox/ancho) coinciden ±1 %.
- [ ] **Step 6:** `::test_sin_foto` — `startBlankCanvas()` + capa → `srcFull.width === 1080` y hay píxeles del color del texto.
- [ ] **Step 7:** Correr → FAIL.
- [ ] **Step 8:** Implementar. `render()` y `exportPNG()` llaman a `renderComposition`; la vista "Original" (antes/después) sigue mostrando la foto sola.
- [ ] **Step 9:** Correr toda la suite → PASS. Commit `feat(texto): composición arriba/abajo con interruptor de efectos`.

### Task 4: Panel "Texto" y guardado de ajustes

**Files:**
- Modify: `index.html` (HTML del `aside`: nueva sección antes de "Efectos · de arriba a abajo"; `serialize`/`deserialize`; CSS)
- Create: `tests/test_panel.py`

**Interfaces:**
- Consumes: `newTextLayer`, `REPARTOS`, `FACES`, `changed()`.
- Produces: `function buildTextPanel()`; `state.selectedText` (uid o `null`); `function mezclar(layer)` (nuevo `seed`, borra `letters[*].face`).
- Panel: título de sección `Texto · capas`; una tarjeta por capa, plegable como las de efectos, con: `textarea` (texto), select **Capa** (`Arriba de la foto` / `Abajo de la foto`), casilla **Le pegan los efectos**, color, select **Tipografías** (`REPARTOS`), select de tipografía si reparto = `una` (opciones `family + ' ' + weight`), rangos **Tamaño** (0.02–0.6), **Interletrado** (−0.2–0.5 em), **Interlineado** (0.6–2), **Rotación** (−180–180°), botón **Mezclar**, botón borrar. Botón **+ Agregar texto** al final. Si `needsCutoutWarning()`, mostrar en la tarjeta: "Recortá la silueta para ver el texto detrás" con un botón que pone `#cutMode` en `silueta` y dispara su `onchange`.
- Ajustes: `serialize()` → `{ version: 2, pipeline, texts }`; `deserialize` acepta v1 (sin `texts` → `[]`) y descarta faces inexistentes en `letters` y `face`. El botón Stop sigue quitando solo efectos.

- [ ] **Step 1:** `test_panel.py::test_agregar_texto` — clic en `+ Agregar texto` → `state.texts.length === 1` y aparece una tarjeta.
- [ ] **Step 2:** `::test_editar_texto_rerenderiza` — escribir en el textarea cambia `state.texts[0].text` y el `out` cambia (hash de píxeles distinto).
- [ ] **Step 3:** `::test_mezclar_cambia_faces` — `assignFaces` antes y después de **Mezclar** difiere.
- [ ] **Step 4:** `::test_ajustes_v1` — `deserialize({version:1, pipeline:[{id:'retro'}]})` → `true`, `state.texts` es `[]`; lo mismo via `localStorage` y recarga.
- [ ] **Step 5:** `::test_roundtrip_v2` — `deserialize(JSON.parse(JSON.stringify(serialize())))` conserva texto, posición, `fx`, `letters`.
- [ ] **Step 6:** Correr → FAIL. Implementar. Correr → PASS.
- [ ] **Step 7:** Commit `feat(texto): panel de capas de texto y ajustes v2`.

### Task 5: Edición directa sobre el lienzo

**Files:**
- Modify: `index.html` (capa de edición sobre `#stage`, CSS, eventos de puntero)
- Create: `tests/test_editar.py`

**Interfaces:**
- Consumes: `layoutText`, `drawTextLayer`, `renderComposition`, `state.selectedText`.
- Produces: `state.selectedLetter` (`{ uid, i }` o `null`); `function hitTest(px, py) -> { uid, i } | { uid, i: null } | null` en coordenadas de imagen; elemento `#textEdit` (SVG superpuesto con `touch-action: none`) con: caja de la capa seleccionada, caja de la letra seleccionada con tiradores **ancho** (borde derecho → `sx`, rango 0.3–5), **alto** (borde superior → `sy`, 0.3–5) y **rotar** (círculo arriba → `rot`); mini barra flotante de la letra: select tipografía, botón **Contorno**, botón **Reiniciar letra**; ficha (`#letterInfo`) con familia, peso, tamaño en px, `sx`/`sy`, rotación e interletrado al pasar el mouse o tocar una letra.
- Gestos: arrastrar dentro de la caja de la capa (fuera de una letra seleccionada) mueve `x/y`; tocar fuera de cualquier texto deselecciona. Durante el arrastre: al empezar, cachear `renderComposition` sin la capa arrastrada; en cada movimiento dibujar el caché + la capa arrastrada **sin efectos**; al soltar, `changed()` (render completo).
- No mostrar la capa de edición mientras se mantiene apretado "Original" ni con "Antes / Después" activo.

- [ ] **Step 1:** `test_editar.py::test_tocar_letra_selecciona` — agregar capa `'HOLA'`, clic en el centro del glyph `O` (convertir coords de imagen a pantalla con `out.getBoundingClientRect()`) → `state.selectedLetter.i === 1` y `#letterInfo` contiene el nombre de la familia de ese glyph.
- [ ] **Step 2:** `::test_tirador_ancho_estira` — arrastrar el tirador de ancho 40 px a la derecha → `letters[1].sx > 1` y el `x` del glyph `L` aumentó.
- [ ] **Step 3:** `::test_mover_capa` — arrastrar el cuerpo de la capa 100 px → `x` cambió ≈ 100/anchoEnPantalla (±2 %).
- [ ] **Step 4:** `::test_contorno` — botón **Contorno** → `letters[i].outline === true` y el centro del glyph deja de tener el color de relleno.
- [ ] **Step 5:** `::test_tactil` (fixture `touch_page`) — `tap` sobre una letra la selecciona; un arrastre táctil del tirador de ancho sube `sx`; `getComputedStyle(#textEdit).touchAction === 'none'`.
- [ ] **Step 6:** Correr → FAIL. Implementar. Correr → PASS.
- [ ] **Step 7:** Commit `feat(texto): edición directa de capas y letras`.

### Task 6: Exportar SVG

**Files:**
- Modify: `index.html` (nueva tecla `SVG` en `.keys`, `function exportSVG()`)
- Create: `tests/test_svg.py`

**Interfaces:**
- Consumes: `layoutText`, `renderComposition`/`runPipeline`, `download(blob, name)`.
- Produces: `function buildSVG() -> string` (testeable) y `exportSVG()` que lo descarga como `${fileBase}-arte.svg`.
- Contenido, en orden: `<rect fill="#fff">` si hay capas limpias abajo; un `<g id="texto-abajo">` con un `<path>` por glyph de las capas limpias de abajo; `<image>` (PNG base64 a resolución completa de la parte con efectos, con papel transparente si hay limpias abajo); `<g id="texto-arriba">` con las limpias de arriba. Cada capa limpia en su propio `<g>` con `id` derivado del texto; trazo en vez de relleno si `outline`. `width/height/viewBox` = tamaño de `srcFull`.

- [ ] **Step 1:** `test_svg.py::test_paths_por_letra` — dos capas limpias `'AB C'` y `'Ñ'` → el SVG parseado (`xml.etree`) tiene 4 `<path>` y 1 `<image>`; `viewBox` == `0 0 W H`.
- [ ] **Step 2:** `::test_contorno_en_svg` — letra con `outline` → su `<path>` tiene `fill="none"` y `stroke`.
- [ ] **Step 3:** Correr → FAIL. Implementar. Correr → PASS.
- [ ] **Step 4:** Commit `feat(texto): exportar SVG con letras en contornos`.

### Task 7: Documentación, verificación final y parche

**Files:**
- Modify: `README.md` (sección "Arte con texto": qué hace, Arriba/Abajo, "Le pegan los efectos", tip de Recortar silueta + texto atrás, SVG para Illustrator/vinilo; créditos de tipografías con licencia), comentario de cabecera de `index.html` ("CÓMO AGREGAR UNA TIPOGRAFÍA": editar la lista en `tools/build-fonts.mjs` y correrlo), `PP-EF27` se mantiene.
- Create: `.gitignore` con `node_modules/`, `__pycache__/`, `.pytest_cache/`.

- [ ] **Step 1:** Suite completa `python -m pytest tests -q` → todo PASS, y `test_smoke` sin errores de consola.
- [ ] **Step 2:** Prueba manual con Playwright: capturas a 1280×800 y 390×844 de una composición (foto con silueta recortada no disponible offline → usar una imagen con transparencia generada) con una capa arriba limpia y una abajo con efectos; revisarlas a ojo.
- [ ] **Step 3:** Commit `docs: arte con texto`.
- [ ] **Step 4:** `git format-patch origin/main --stdout > capas-de-texto.patch` (fuera del repo) y verificar con un clon limpio: `git am capas-de-texto.patch` + suite → PASS.
