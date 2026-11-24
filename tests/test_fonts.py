def test_fuentes_cargadas(page):
    assert page.evaluate("window.__textoReady") is True
    n = page.evaluate("FACES.length")
    assert n >= 14
    assert page.evaluate("FACES.every(f => f.font.unitsPerEm > 0)")
    assert page.evaluate("new Set(FACES.map(f => f.id)).size === FACES.length")


def test_heaviness_ordena(page):
    assert page.evaluate("faceById('inter-900').heaviness > faceById('inter-100').heaviness")
    assert page.evaluate("FACES.every((f, i) => i === 0 || FACES[i-1].heaviness <= f.heaviness)")


def test_acentos(page):
    faltan = page.evaluate("FACES.filter(f => !faceHasGlyph(f, 'ñ') || !faceHasGlyph(f, '¿')).map(f => f.id)")
    assert faltan == []
