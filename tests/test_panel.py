from conftest import load_image, wait_render, INDEX

HASH = "(() => { const d = out.getContext('2d').getImageData(0,0,out.width,out.height).data; let h = 0; for (let i = 0; i < d.length; i += 7) h = (h * 31 + d[i]) | 0; return h; })()"


def click_add(page):
    page.evaluate("window.__renderSeqTarget = (window.__renderSeq||0)+1")
    page.click('#btnAddText')
    wait_render(page)


def test_agregar_texto(page):
    load_image(page, 400, 300, pipeline=[])
    click_add(page)
    assert page.evaluate("state.texts.length") == 1
    assert page.locator('#textPanel .card').count() == 1


def test_agregar_sin_foto_crea_lienzo(page):
    page.click('#btnAddText')
    page.wait_for_function("window.__renderSeq >= 1")
    assert page.evaluate("srcFull && srcFull.width") == 1080


def test_editar_texto_rerenderiza(page):
    load_image(page, 400, 300, pipeline=[])
    click_add(page)
    h0 = page.evaluate(HASH)
    page.evaluate("window.__renderSeqTarget = (window.__renderSeq||0)+1")
    page.fill('#textPanel textarea', 'PEPPER')
    wait_render(page)
    assert page.evaluate("state.texts[0].text") == 'PEPPER'
    assert page.evaluate(HASH) != h0


def test_mezclar_cambia_faces(page):
    load_image(page, 400, 300, pipeline=[])
    click_add(page)
    page.evaluate("state.texts[0].text = 'ABCDEFGHIJKLMNOP'; state.texts[0].letters = {0: {face: FACES[0].id}}")
    a = page.evaluate("assignFaces(state.texts[0])")
    page.click('#textPanel .btn-mezclar')
    b = page.evaluate("assignFaces(state.texts[0])")
    assert a != b
    assert page.evaluate("state.texts[0].letters[0].face") is None


def test_ajustes_v1(page):
    assert page.evaluate("deserialize({version:1, pipeline:[{id:'retro'}]})") is True
    assert page.evaluate("state.texts") == []
    page.evaluate("localStorage.setItem(STORAGE_KEY, JSON.stringify({version:1, pipeline:[{id:'stipple'}]}))")
    page.goto(INDEX)
    page.wait_for_function("window.__textoReady === true")
    assert page.evaluate("state.pipeline.map(s => s.id)") == ['stipple']
    assert page.evaluate("state.texts") == []
    assert page.errors == []


def test_roundtrip_v2(page):
    r = page.evaluate("""(() => {
      state.texts = [newTextLayer({text:'HOLA', x:0.3, fx:true, position:'abajo', letters:{1:{sx:2, outline:true, face:'inter-900'}}})];
      const o = JSON.parse(JSON.stringify(serialize()));
      state.texts = [];
      deserialize(o);
      const t = state.texts[0];
      return [o.version, t.text, t.x, t.fx, t.position, t.letters[1].sx, t.letters[1].outline, t.letters[1].face];
    })()""")
    assert r == [2, 'HOLA', 0.3, True, 'abajo', 2, True, 'inter-900']


def test_deserialize_descarta_face_inexistente(page):
    r = page.evaluate("""(() => { deserialize({version:2, pipeline:[], texts:[{text:'A', face:'no-existe', letters:{0:{face:'tampoco', sx:3}}}]});
      const t = state.texts[0]; return [!!faceById(t.face), t.letters[0].face === undefined, t.letters[0].sx]; })()""")
    assert r == [True, True, 3]
