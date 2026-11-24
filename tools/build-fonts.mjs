// Arma fonts/fonts.js con las tipografías embebidas (base64) para la sección de Texto.
//
// CÓMO AGREGAR UNA TIPOGRAFÍA
//   1. Buscá la familia en https://fontsource.org (tiene que ser de licencia libre: OFL o Apache).
//   2. Agregala a la lista FUENTES de abajo con los pesos que quieras.
//   3. En una carpeta aparte:  npm i opentype.js@1 @fontsource/<paquete> ...
//   4. Corré:  node tools/build-fonts.mjs <carpeta>/node_modules
//
// Uso: node tools/build-fonts.mjs /ruta/a/node_modules
import fs from 'node:fs';
import path from 'node:path';

const FUENTES = [
  // [paquete, familia, estilo (para mostrar), pesos]
  ['anton', 'Anton', 'Condensada', [400]],
  ['bebas-neue', 'Bebas Neue', 'Condensada', [400]],
  ['archivo-black', 'Archivo Black', 'Grotesca', [400]],
  ['archivo', 'Archivo', 'Grotesca', [100, 900]],
  ['big-shoulders-display', 'Big Shoulders Display', 'Condensada', [100, 900]],
  ['fraunces', 'Fraunces', 'Serif', [100, 900]],
  ['playfair-display', 'Playfair Display', 'Serif', [400, 900]],
  ['instrument-serif', 'Instrument Serif', 'Serif', [400]],
  ['space-grotesk', 'Space Grotesk', 'Grotesca', [300, 700]],
  ['syne', 'Syne', 'Display', [400, 800]],
  ['unbounded', 'Unbounded', 'Expandida', [200, 900]],
  ['rubik-mono-one', 'Rubik Mono One', 'Display', [400]],
  ['shrikhand', 'Shrikhand', 'Script', [400]],
  ['dm-serif-display', 'DM Serif Display', 'Serif', [400]],
  ['climate-crisis', 'Climate Crisis', 'Display', [400]],
  ['inter', 'Inter', 'Grotesca', [100, 900]],
];

const nm = process.argv[2];
if (!nm) { console.error('Uso: node tools/build-fonts.mjs /ruta/a/node_modules'); process.exit(1); }
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const out = [];
for (const [pkg, family, style, weights] of FUENTES) {
  const dir = path.join(nm, '@fontsource', pkg);
  const files = fs.readdirSync(path.join(dir, 'files'));
  const disponibles = files.map(f => f.match(/-latin-(\d+)-normal\.woff$/)).filter(Boolean).map(m => +m[1]);
  for (const w of weights) {
    const peso = disponibles.reduce((a, b) => Math.abs(b - w) < Math.abs(a - w) ? b : a);
    const file = files.find(f => f.endsWith(`-latin-${peso}-normal.woff`));
    const b64 = fs.readFileSync(path.join(dir, 'files', file)).toString('base64');
    out.push({ id: `${pkg}-${peso}`, family, weight: peso, style, b64 });
  }
  fs.copyFileSync(path.join(dir, 'LICENSE'), path.join(root, 'fonts', 'licencias', `${pkg}.txt`));
}
fs.copyFileSync(path.join(nm, 'opentype.js', 'dist', 'opentype.min.js'), path.join(root, 'lib', 'opentype.min.js'));
const js = '// Generado por tools/build-fonts.mjs — no editar a mano.\n' +
  '// Tipografías libres (ver fonts/licencias/).\n' +
  'window.PEPPER_FONT_DATA = [\n' + out.map(o => '  ' + JSON.stringify(o)).join(',\n') + '\n];\n';
fs.writeFileSync(path.join(root, 'fonts', 'fonts.js'), js);
console.log(`${out.length} tipografías → fonts/fonts.js (${(js.length / 1024).toFixed(0)} KB)`);
