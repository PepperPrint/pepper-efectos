from conftest import load_image, rerender, pixel, wait_render


def add_text(page, **kw):
    import json
    page.evaluate(f"state.texts.push(newTextLayer(Object.assign({{text:'I', reparto:'una', face:'archivo-black-400', size:0.5, color:'#000000'}}, {json.dumps(kw)})))")
    rerender(page)


def test_texto_limpio_arriba(page):
    load_image(page, 400, 400, pipeline=[])
    add_text(page)
    assert pixel(page, 200, 200)[:3] == [0, 0, 0]


def test_texto_fx_pasa_por_efecto(page):
    load_image(page, 400, 400, pipeline=['degradado'])
    add_text(page, color='#ff00ff', fx=True)
    con = pixel(page, 200, 200)[:3]
    page.evaluate("state.texts[0].fx = false")
    rerender(page)
    sin = pixel(page, 200, 200)[:3]
    assert sin == [255, 0, 255]
    assert con != [255, 0, 255]


def test_texto_abajo_tapado_y_aviso(page):
    load_image(page, 400, 400, pipeline=[])
    add_text(page, position='abajo')
    assert page.evaluate("needsCutoutWarning()") is True
    assert pixel(page, 200, 200)[:3] == [200, 40, 40]


def test_texto_abajo_con_recorte(page):
    load_image(page, 400, 400, transparent_rect=[0, 0, 200, 400], pipeline=['retro'])
    add_text(page, position='abajo', x=0.25)
    assert page.evaluate("needsCutoutWarning()") is False
    assert pixel(page, 100, 200)[:3] == [0, 0, 0]
    assert pixel(page, 20, 20)[:3] == [255, 255, 255]


BBOX = """(img) => { const d = img.data, W = img.width, H = img.height; let x0=W,y0=H,x1=0,y1=0;
  for (let y=0;y<H;y++) for (let x=0;x<W;x++){ const k=(y*W+x)*4; if (d[k]<30&&d[k+1]<30&&d[k+2]<30){ if(x<x0)x0=x; if(x>x1)x1=x; if(y<y0)y0=y; if(y>y1)y1=y; } }
  return [x0/W, y0/H, x1/W, y1/H]; }"""


def test_proporcional_en_exportacion(page):
    load_image(page, 6000, 4000, pipeline=[], full_res=False)
    add_text(page, text='HOLA', x=0.3, y=0.6, size=0.2)
    a = page.evaluate(f"(() => {{ const f = {BBOX}; return f(out.getContext('2d').getImageData(0,0,out.width,out.height)); }})()")
    b = page.evaluate(f"(() => {{ const f = {BBOX}; return f(renderComposition(srcFull, 1, {{}})); }})()")
    assert page.evaluate("out.width") < 6000
    for u, v in zip(a, b):
        assert abs(u - v) < 0.01


def test_sin_foto(page):
    page.evaluate("window.__renderSeqTarget = (window.__renderSeq||0)+1; startBlankCanvas()")
    wait_render(page)
    add_text(page)
    assert page.evaluate("srcFull.width") == 1080
    assert page.evaluate("out.width") > 0
    w, h = page.evaluate("[out.width, out.height]")
    assert pixel(page, w // 2, h // 2)[:3] == [0, 0, 0]
