from conftest import load_image


def test_carga_sin_errores(page):
    assert page.evaluate("Object.keys(EFFECTS).length") == 27
    assert page.errors == []


def test_render_imagen(page):
    load_image(page, 200, 100, pipeline=[])
    assert page.evaluate("out.width") == 200
    assert page.errors == []
