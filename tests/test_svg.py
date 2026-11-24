import xml.etree.ElementTree as ET
from conftest import load_image

NS = '{http://www.w3.org/2000/svg}'


def svg_of(page):
    return ET.fromstring(page.evaluate("buildSVG()"))


def test_paths_por_letra(page):
    load_image(page, 640, 480, pipeline=['retro'])
    page.evaluate("""state.texts.push(newTextLayer({text:'AB C'}), newTextLayer({text:'Ñ', position:'abajo'}));""")
    root = svg_of(page)
    assert root.get('viewBox') == '0 0 640 480'
    assert len(root.findall(f'.//{NS}path')) == 4
    assert len(root.findall(f'.//{NS}image')) == 1
    assert root.find(f".//{NS}g[@id='texto-abajo']") is not None
    assert root.find(f".//{NS}g[@id='texto-arriba']") is not None


def test_contorno_en_svg(page):
    load_image(page, 640, 480, pipeline=[])
    page.evaluate("state.texts.push(newTextLayer({text:'AB', color:'#123456', letters:{1:{outline:true}}}));")
    paths = svg_of(page).findall(f'.//{NS}path')
    assert paths[0].get('fill') == '#123456'
    assert paths[1].get('fill') == 'none' and paths[1].get('stroke') == '#123456'


def test_texto_con_efectos_no_va_como_path(page):
    load_image(page, 640, 480, pipeline=[])
    page.evaluate("state.texts.push(newTextLayer({text:'AB', fx:true}));")
    assert len(svg_of(page).findall(f'.//{NS}path')) == 0
