import json
from conftest import load_image, rerender, wait_render


def test_cargar_json_reconstruye_panel_texto(page, tmp_path):
    load_image(page, 400, 300, pipeline=[])
    page.click('#btnAddText')
    page.wait_for_timeout(200)
    f = tmp_path / 'ajustes.json'
    f.write_text(json.dumps({'version': 2, 'pipeline': [], 'texts': [{'text': 'CARGADO'}]}))
    page.set_input_files('#presetInput', str(f))
    page.wait_for_function("state.texts.length === 1 && state.texts[0].text === 'CARGADO'")
    assert page.input_value('#textPanel textarea') == 'CARGADO'
    assert page.evaluate("state.selectedText") is None


def test_editar_texto_conserva_letra_editada(page):
    load_image(page, 400, 300, pipeline=[])
    page.click('#btnAddText')
    page.wait_for_timeout(200)
    page.fill('#textPanel textarea', 'ABC')
    page.evaluate("state.texts[0].letters = {2: {outline: true, sx: 2}}")
    page.fill('#textPanel textarea', 'XABC')
    assert page.evaluate("JSON.stringify(state.texts[0].letters)") == json.dumps({'3': {'outline': True, 'sx': 2}}, separators=(',', ':'))
    page.fill('#textPanel textarea', 'XAC')
    assert page.evaluate("Object.keys(state.texts[0].letters)") == ['2']


def test_capa_edicion_no_bloquea_sin_textos(page):
    load_image(page, 400, 300, pipeline=[])
    assert page.evaluate("getComputedStyle(textEdit).pointerEvents") == 'none'
    page.evaluate("state.texts.push(newTextLayer({})); changed();")
    page.wait_for_timeout(200)
    assert page.evaluate("getComputedStyle(textEdit).pointerEvents") != 'none'


def test_lienzo_en_blanco_olvida_foto_anterior(page):
    page.evaluate("origBmp = document.createElement('canvas'); document.getElementById('cutMode').value = 'silueta';")
    page.evaluate("window.__renderSeqTarget = (window.__renderSeq||0)+1; startBlankCanvas()")
    wait_render(page)
    assert page.evaluate("origBmp") is None
    assert page.evaluate("document.getElementById('cutMode').value") == ''
    page.evaluate("state.texts.push(newTextLayer({position:'abajo'})); buildTextPanel();")
    assert page.locator('#textPanel .text-warn .btn').count() == 0
    assert 'Pasalo arriba' in page.inner_text('#textPanel .text-warn')
