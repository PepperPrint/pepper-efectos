# Pepper Print · Efectos

Web local de efectos de imagen para producción gráfica (serigrafía, DTF, riso, vinilo).
Un solo archivo HTML, sin dependencias y sin internet: se abre con doble clic en Chrome, en Mac o Windows.

## Cómo usarla

1. Abrí `index.html` en el navegador.
2. Arrastrá una imagen, pegala con Ctrl/Cmd + V o tocá **Abrir imagen**.
3. Agregá efectos desde **Agregar efecto**. Se aplican de arriba a abajo, como capas.
4. Cada efecto tiene **modo de fusión** (los mismos que Photoshop) y **opacidad**.
5. **START** exporta el PNG a resolución completa. La tecla amarilla **Solo tinta** exporta con fondo transparente (para DTF).

Atajos: tecla **C** para comparar antes/después; mantené **Original** para ver la imagen sin efectos.

## Efectos (27)

| Impresión | Retro / digital | Texturas y dibujo |
|---|---|---|
| Retro Print | Monitor CRT (fósforo, fantasma) | Fotocopia |
| Halftone (DTF / serigrafía) | Teletexto | Editorial antiguo |
| Risografía | Webcam 95 | Copia desteñida |
| Stipple (puntillado) | Pixel art | Pintura en aerosol |
| Silueta en semitono | Glitch (pixel sorting) | Garabato |
| Ticket escaneado | ASCII / glifos | Confeti de estrellas |
| Stencil | Solarizado con estela | Bordado (punto cruz) |
| Grabado de líneas | Pantalla líquida | Bordado satén (parche) |
| Posterizar | Mapa de degradado | Ajustes básicos |

## Agregar un efecto nuevo

Dentro de `index.html`, en la sección **EFECTOS**, hay un molde comentado. Cada efecto es un bloque
`registerEffect({ id, name, params, apply })`: definís los parámetros y los controles del panel se arman solos.

## Ajustes

**Guardar** y **Cargar** exportan/importan la lista de efectos con sus valores en un `.json`.
La última configuración también queda guardada en el navegador.
