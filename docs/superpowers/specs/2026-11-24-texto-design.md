# Pepper Efectos · Capas de texto — diseño

Fecha: 2026-11-24 · Repo: `PepperPrint/pepper-efectos` (`index.html`, un solo archivo, publicado en GitHub Pages)

## Para qué

Que cualquiera que entre a la web pública pueda **subir su foto, darle los efectos que quiera y sumarle texto como capa (arriba o abajo de la imagen) para hacer su propio arte**. "Como un Paint, pero más lindo": un juguete para jugar, no una herramienta profesional. El público son visitantes cualquiera, también desde el celular.

Inspiración (dos posts de Instagram que el dueño mostró):

1. **Poster Studio (awaaz.me)** — letras gruesas que llenan un recuadro; cuando estirás una letra, las vecinas se corren para hacerle lugar.
2. **z_isdesigning** — una frase donde cada letra sale de una tipografía/peso distinto, con modos de reparto (parejo, extremos, tirando a pesado, tirando a liviano, ola, rampa fina→gruesa, rampa por línea, alternado); al pasar el mouse por una letra se ve su "ficha" (tipografía, peso, tamaño, desplazamiento, espaciado); se pueden rotar letras y dejar algunas en contorno; exporta editable.

## Objetivos

- Capas de texto que se apilan **arriba o abajo** de la foto.
- **Interruptor por capa de texto: "Le pegan los efectos"** (sí/no). Sí → el texto pasa por la lista de efectos junto con la foto (como si se imprimiera todo junto). No → el texto queda limpio, nítido.
- Mezcla de tipografías por letra con los modos de reparto del post 2, y botón **Mezclar** (rearma al azar).
- Manipulación directa sobre el lienzo: elegir una letra y **estirarla** (las vecinas hacen lugar), **rotarla**, cambiarle tipografía, pasarla a **contorno**. Mover y escalar la capa entera.
- Ficha de la letra al pasar el mouse / tocarla.
- Exportar **PNG** (como hoy, incluido "Solo tinta") y **SVG** con el texto limpio como texto editable para Illustrator.
- Funciona con mouse y con dedo (celular).

## No objetivos (por ahora)

- Exportar video / GIF animado (segunda etapa). Las letras sí pueden animarse en pantalla al acomodarse.
- Usar las tipografías instaladas en la computadora del visitante (Local Font Access API, solo Chrome, pide permiso). Queda como extra opcional futuro.
- Cuentas, guardar en la nube, galería pública.

## Anti-objetivos (sería un fracaso aunque funcione)

- Que se sienta como un formulario de controles deslizantes en vez de algo que se toca y se juega.
- Romper o enlentecer lo que ya anda: los 27 efectos, recorte automático, antes/después, exportar, ajustes .json.
- Que en el celular no se pueda usar.
- Perder la estética actual de panel de máquina Riso.

## Restricciones

- Todo sigue en `index.html` sin build ni dependencias de npm. La web ya carga MediaPipe por CDN solo para el recorte; el resto corre local.
- Las fotos no salen de la computadora del visitante.
- Las tipografías tienen que ser de licencia libre (OFL o similar) para poder publicarlas.
- La persona que mantiene el repo no programa: el código tiene que seguir siendo fácil de extender, igual que el molde de `registerEffect` que ya tiene la web.

## Enfoques considerados

- **A · Dentro de la misma web (elegido).** Las capas de texto son parte de la composición de la página actual y conviven con la lista de efectos. Un solo link, foto + texto + efectos en vivo. Contra: `index.html` (~3.260 líneas) crece bastante.
- **B · Página aparte `tipografia.html`** con botón "mandar a efectos". Más simple por separado, pero obliga a saltar de página y no se ve texto + efectos juntos. Descartado por el dueño al pedir capas arriba/abajo de la foto.
- **C · El texto como un efecto más de la lista.** Solo deslizadores, sin tocar ni arrastrar: pierde lo de "Paint". Descartado.

El dueño eligió A, y para los efectos sobre el texto eligió el **interruptor por capa**, frente a "solo a la foto" o "a todo junto".

## Cómo se arma la imagen (decidido)

Orden de la composición, de abajo hacia arriba:

1. Capas de texto **abajo** con "Le pegan los efectos" = **sí**
2. **Foto**
3. Capas de texto **arriba** con efectos = **sí**
4. → **todo lo anterior pasa por la lista de efectos** (`runPipeline`)
5. Capas de texto **abajo** con efectos = **no** (se dibujan *detrás* del resultado; se ven solo donde el resultado es transparente)
6. Capas de texto **arriba** con efectos = **no**

Hoy `runPipeline(srcCanvas, …)` recibe la foto. Con esto recibe un lienzo con las capas 1–3 ya dibujadas, y el resultado se compone con 5 y 6.

**Papel de los efectos y texto limpio abajo (decisión de Claude).** Casi todos los efectos pintan papel opaco en todos los píxeles (solo quedan transparentes con `transparentPaper`, el modo "Solo tinta"). Por eso, cuando hay alguna capa de texto **abajo sin efectos**, la lista de efectos corre en modo `transparentPaper: true` y se compone así: fondo blanco → texto limpio de abajo → resultado de los efectos (solo tinta) → texto limpio de arriba. No hace falta tocar ninguno de los 27 efectos. Costo aceptado: en ese caso el color de papel propio de cada efecto (por ejemplo, el crema de Retro) se reemplaza por blanco.

**Texto abajo + foto sin recorte = texto tapado.** Si hay capas abajo y la foto no tiene transparencia, se muestra un aviso: "Recortá la silueta para ver el texto detrás", con acceso al *Recortar silueta* que ya existe.

## Decisiones del builder (a resolver en el plan)

- Cómo se ve la interfaz de la capa de texto en el panel izquierdo (probablemente una sección "Texto" con sus capas, al estilo de la lista de efectos) y cómo se editan las letras sobre el lienzo.
- Qué 10–15 tipografías libres incluir, cubriendo extremos de peso y ancho (fuentes variables cuando convenga, para las rampas de peso). Dónde viven: carpeta `fonts/` en el repo, cargadas de forma relativa (no Google Fonts CDN), salvo que eso rompa el uso con doble clic.
- Mecánica exacta de "estirar y que las vecinas hagan lugar" (escala horizontal/vertical de la letra y reflujo de la línea dentro del recuadro de la capa).
- Lienzo sin foto: permitir empezar solo con texto, sobre un lienzo en blanco de tamaño por defecto.
- Cómo guardar las capas de texto en los ajustes `.json` y en el guardado automático (`localStorage`) sin romper los archivos de ajustes viejos.
- **SVG (decisión de Claude):** las letras del texto limpio van como **contornos** (trazados), una forma por letra, para que coincida exacto con la pantalla aunque el que lo abra no tenga las fuentes. Sirve también para corte de vinilo y DTF. Se pierde poder reescribir el texto en Illustrator, pero estirado, rotación y mezcla de pesos por letra no se pueden representar bien como `<text>` editable. Lo que pasó por efectos va como imagen incrustada. Para leer las fuentes se puede incluir opentype.js como archivo local del repo.
- **Vista previa al arrastrar (decisión de Claude):** mientras se arrastra, estira o rota una letra con efectos activados, se muestra limpia (sin efectos). Los efectos se aplican al soltar. Así no se traba en el celular.
- Actualizar el README con la nueva sección y el comentario de cabecera del archivo con cómo sumar tipografías.
