def faces(page, js_layer):
    return page.evaluate(f"assignFaces(newTextLayer({js_layer}))")


def test_reparto_deterministico(page):
    t = "'ABCDEFGHIJKLMNOPQRST'"
    a = faces(page, f"{{text:{t}, reparto:'parejo', seed:1}}")
    b = faces(page, f"{{text:{t}, reparto:'parejo', seed:1}}")
    c = faces(page, f"{{text:{t}, reparto:'parejo', seed:2}}")
    assert a == b and a != c
    assert len(a) == 20


def test_rampa_no_decrece(page):
    hs = page.evaluate("assignFaces(newTextLayer({text:'ABCDEFGHIJKLMNOP', reparto:'rampa', seed:3})).map(id => faceById(id).heaviness)")
    assert all(hs[i] <= hs[i + 1] for i in range(len(hs) - 1))
    assert hs[0] < hs[-1]


def test_alternado(page):
    res = page.evaluate("""(() => {
      const ids = assignFaces(newTextLayer({text:'ABCDEFGHIJ', reparto:'alternado', seed:5}));
      const half = Math.floor(FACES.length / 2);
      return ids.map((id, k) => (FACES.findIndex(f => f.id === id) < half) === (k % 2 === 0));
    })()""")
    assert all(res)


def test_estirar_corre_vecinas(page):
    r = page.evaluate("""(() => {
      const L = newTextLayer({text:'AB', reparto:'una'});
      const g0 = layoutText(L, 1000, 1000).glyphs;
      L.letters[0] = {sx: 2};
      const g1 = layoutText(L, 1000, 1000).glyphs;
      return [g0[0].adv, g1[1].x - g1[0].x, g0[1].x - g0[0].x];
    })()""")
    adv, d1, d0 = r
    assert abs((d1 - d0) - adv) < 0.01


def test_acentos_y_emoji(page):
    r = page.evaluate("""(() => {
      const L = newTextLayer({text:'¿Año ñandú? 🌶', reparto:'parejo'});
      return layoutText(L, 1000, 1000).glyphs.map(g => g.ch).join('');
    })()""")
    assert r == '¿Añoñandú?'


def test_vacio(page):
    r = page.evaluate("""['', '   ', 'A\\n\\nB'].map(t => layoutText(newTextLayer({text:t}), 800, 600).glyphs.length)""")
    assert r == [0, 0, 2]
