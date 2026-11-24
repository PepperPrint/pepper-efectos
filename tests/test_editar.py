from conftest import load_image, rerender, wait_render, pixel


def setup(page, text='HOLA', w=800, h=600):
    load_image(page, w, h, pipeline=[])
    page.evaluate(f"""state.texts.push(newTextLayer({{text:'{text}', reparto:'una', face:'archivo-black-400', size:0.3, color:'#000000'}})); buildTextPanel();""")
    rerender(page)


def glyph_screen(page, i):
    """Centro en pantalla del glifo i de la primera capa."""
    return page.evaluate("""(i) => {
      const t = state.texts[0], W = srcFull.width, H = srcFull.height;
      const g = layoutText(t, W, H).glyphs.find(g => g.i === i);
      const r = out.getBoundingClientRect();
      return [r.left + (g.rect.x + g.rect.w / 2) / W * r.width, r.top + (g.rect.y + g.rect.h / 2) / H * r.height];
    }""", i)


def handle_screen(page, h):
    b = page.locator(f'#textEdit [data-h="{h}"]').bounding_box()
    return [b['x'] + b['width'] / 2, b['y'] + b['height'] / 2]


def drag(page, a, b, steps=8):
    page.mouse.move(*a)
    page.mouse.down()
    page.mouse.move(*b, steps=steps)
    page.evaluate("window.__renderSeqTarget = (window.__renderSeq||0)+1")
    page.mouse.up()
    wait_render(page)


def test_tocar_letra_selecciona(page):
    setup(page)
    page.mouse.click(*glyph_screen(page, 1))
    assert page.evaluate("state.selectedLetter && state.selectedLetter.i") == 1
    assert 'Archivo Black' in page.inner_text('#letterInfo')


def test_tirador_ancho_estira(page):
    setup(page)
    x_l = page.evaluate("layoutText(state.texts[0], srcFull.width, srcFull.height).glyphs[2].x")
    page.mouse.click(*glyph_screen(page, 1))
    a = handle_screen(page, 'w')
    drag(page, a, [a[0] + 40, a[1]])
    assert page.evaluate("state.texts[0].letters[1].sx") > 1
    assert page.evaluate("layoutText(state.texts[0], srcFull.width, srcFull.height).glyphs[2].x") > x_l


def test_mover_capa(page):
    setup(page)
    x0 = page.evaluate("state.texts[0].x")
    a = glyph_screen(page, 0)
    drag(page, a, [a[0] + 100, a[1]])
    sw = page.evaluate("out.getBoundingClientRect().width")
    assert abs(page.evaluate("state.texts[0].x") - (x0 + 100 / sw)) < 0.02


def test_contorno(page):
    setup(page, text='HI')
    c = glyph_screen(page, 1)
    page.mouse.click(*c)
    img = page.evaluate("""(() => { const t = state.texts[0]; const g = layoutText(t, out.width, out.height).glyphs[1];
      return [Math.round(g.rect.x + g.rect.w/2), Math.round(g.rect.y + g.rect.h*0.55)]; })()""")
    assert pixel(page, *img)[:3] == [0, 0, 0]
    page.evaluate("window.__renderSeqTarget = (window.__renderSeq||0)+1")
    page.click('#letterBar .btn-contorno')
    wait_render(page)
    assert page.evaluate("state.texts[0].letters[1].outline") is True
    assert pixel(page, *img)[:3] != [0, 0, 0]


def test_tactil(touch_page):
    page = touch_page
    setup(page)
    c = glyph_screen(page, 1)
    page.touchscreen.tap(*c)
    assert page.evaluate("state.selectedLetter && state.selectedLetter.i") == 1
    assert page.evaluate("getComputedStyle(document.getElementById('textEdit')).touchAction") == 'none'
    a = handle_screen(page, 'w')
    cdp = page.context.new_cdp_session(page)
    def touch(t, x, y):
        pts = [] if t == 'touchEnd' else [{'x': x, 'y': y}]
        cdp.send('Input.dispatchTouchEvent', {'type': t, 'touchPoints': pts})
    touch('touchStart', *a)
    for k in range(1, 7):
        touch('touchMove', a[0] + 6 * k, a[1])
    page.evaluate("window.__renderSeqTarget = (window.__renderSeq||0)+1")
    touch('touchEnd', 0, 0)
    wait_render(page)
    assert page.evaluate("state.texts[0].letters[1].sx") > 1
