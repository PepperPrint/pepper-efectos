# Pepper Print · Efectos

**27 efectos de imagen para serigrafía, DTF, risografía y diseño gráfico — gratis, en el navegador y sin subir nada a internet.**

### ▶ [Abrir la web](https://pepperprint.github.io/pepper-efectos/)

![Interfaz de Pepper Print · Efectos](img/interfaz.png)

Hecha por [Pepper Print](https://github.com/PepperPrint) para el trabajo diario del taller: preparar diseños para DTF, sacar looks de serigrafía y risografía, y probar estilos en segundos sin abrir Photoshop.

---

## Qué tiene de bueno

- **Sin instalar nada.** Es un solo archivo HTML. Abrís el link o el archivo con doble clic y listo, en Mac o Windows.
- **Tus imágenes no salen de tu computadora.** Todo se procesa en tu navegador; no hay servidor ni cuentas.
- **Efectos que se combinan como capas.** Apilás varios, los reordenás y cada uno tiene **modo de fusión** (los mismos 16 de Photoshop: Multiplicar, Trama, Superponer…) y **opacidad**.
- **Listo para producción.** Exporta PNG a resolución completa, y con **Solo tinta** el fondo sale transparente — ideal para DTF y serigrafía.
- **Vista antes / después** con un divisor que arrastrás sobre la imagen.

## Antes y después

| Risografía | Halftone (serigrafía) | Monitor CRT |
|---|---|---|
| ![Risografía](img/antes-despues-riso.png) | ![Halftone](img/antes-despues-halftone.png) | ![CRT](img/antes-despues-crt.png) |

## Los 27 efectos

![Efectos de impresión](img/efectos-1.png)

![Efectos retro y digitales](img/efectos-2.png)

![Efectos de textura y dibujo](img/efectos-3.png)

| Impresión | Retro / digital | Texturas y dibujo |
|---|---|---|
| **Retro Print** — una tinta con grano y reticulación | **Monitor CRT** — líneas, máscara RGB, curvatura; fósforo verde/ámbar y "fantasma" | **Fotocopia** — tóner, grano, negros planos y pliegues |
| **Halftone (DTF / serigrafía)** — AM/FM, 6 formas de punto, tintas planas, CMYK, desregistro | **Teletexto** — mosaico 2×3 con 8 colores | **Editorial antiguo** — tono de película, gradación y borde recortado |
| **Risografía** — separación en 1–3 tintas con superposición real | **Webcam 95** — baja resolución y compresión en bloques | **Copia desteñida** — brillo difuso, grunge y trama de color |
| **Stipple** — puntillado con ruido + umbral | **Pixel art** — paletas Game Boy, PICO-8, CGA… | **Pintura en aerosol** — grano de spray y salpicaduras |
| **Silueta en semitono** — puntos que se desvanecen (logos) | **Glitch** — pixel sorting, franjas y RGB | **Garabato** — trazos de lápiz de color |
| **Ticket escaneado** — térmica a 2 colores, movimiento, bordes rasgados | **ASCII / glifos** | **Confeti de estrellas** |
| **Stencil** — 2 o 3 tonos planos | **Solarizado con estela** | **Bordado punto cruz** |
| **Grabado de líneas** | **Pantalla líquida** | **Bordado satén (parche)** |
| **Posterizar** | **Mapa de degradado** — térmico, neón, duotono… | **Ajustes básicos** |

## Para DTF: adiós a las semitransparencias

El DTF no imprime bien sombras suaves ni bordes difuminados: el blanco y el adhesivo no saben qué hacer con un píxel al 40 %. El efecto **Halftone** en modo **DTF** convierte todo lo semitransparente en puntos sólidos, conservando los colores del diseño.

![Ejemplo DTF](img/dtf.png)

1. Cargá tu PNG con fondo transparente.
2. Agregá **Halftone (DTF / serigrafía)** en modo **DTF** → *Transparencias y sombras suaves*.
3. Ajustá **Lineatura** (25–45 LPI a 300 DPI es lo usual) y **Punto mínimo**.
4. Exportá con la tecla amarilla **Solo tinta**.

También puede **quitar el color de la remera** (los píxeles parecidos al color de la prenda pasan a puntos) o volver transparente lo oscuro o lo claro.

## Cómo se usa

1. Abrí la [web](https://pepperprint.github.io/pepper-efectos/) (o descargá `index.html` y abrilo con doble clic).
2. Arrastrá una imagen, pegala con **Ctrl/Cmd + V** o tocá **Abrir imagen**.
3. Elegí un efecto en **Agregar efecto**. Se aplican de arriba hacia abajo.
4. Ajustá los controles. Doble clic en un deslizador lo vuelve al valor original.
5. **START** (botón verde) exporta el PNG. **Solo tinta** (amarillo) lo exporta con fondo transparente.

| Control | Qué hace |
|---|---|
| LED de cada efecto | Lo prende o apaga |
| ↑ ↓ | Cambia el orden |
| ⟲ | Vuelve el efecto a sus valores originales |
| Modo de fusión / Opacidad | Cómo se mezcla con lo que tiene arriba |
| **Original** (mantener) | Muestra la imagen sin efectos |
| **Antes / Después** o tecla **C** | Divisor para comparar |
| **Guardar / Cargar** | Guarda tu combinación de efectos en un `.json` |
| **STOP** (dos toques) | Quita todos los efectos |

**Combinaciones que funcionan bien**
- *Confeti de estrellas* + *Risografía* debajo → el look "star confetti".
- *Editorial antiguo* + *Fotocopia* en **Multiplicar 50 %** → revista vieja fotocopiada.
- *Mapa de degradado* (térmico rosa/verde) con ruido → "thermal noise".

## Cómo funciona por dentro

- Un solo `index.html` con HTML, CSS y JavaScript, **sin librerías**.
- La vista previa trabaja sobre una copia reducida de la imagen (máx. 1600 px) para que los controles respondan rápido; al exportar se procesa a **resolución completa**. Si querés ver el detalle exacto, activá *Vista previa a resolución completa*.
- Cada efecto recibe los píxeles, los transforma y devuelve el resultado; el siguiente efecto trabaja sobre eso, mezclado con el modo de fusión elegido.
- La última configuración queda guardada en tu navegador.

## Sumar un efecto nuevo

Dentro de `index.html`, en la sección **EFECTOS**, hay un molde comentado. Cada efecto es un bloque:

```js
registerEffect({
  id: 'mi-efecto',
  name: 'Mi efecto',
  params: [
    { key: 'fuerza', label: 'Fuerza', type: 'range', min: 0, max: 1, step: 0.01, default: 0.5 },
    { key: 'color',  label: 'Color',  type: 'color', default: '#ff0000' },
  ],
  apply(img, p, ctx) {
    // img.data tiene los píxeles RGBA; modificalos y devolvé img
    return img;
  }
});
```

Los controles del panel se arman solos a partir de `params`, y el efecto aparece en el menú con modo de fusión y opacidad incluidos.

---

Hecho por **Pepper Print**. Los ejemplos de este README usan una imagen generada por código.
