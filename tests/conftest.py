import pathlib
import pytest
from playwright.sync_api import sync_playwright

INDEX = (pathlib.Path(__file__).resolve().parent.parent / 'index.html').as_uri()


@pytest.fixture(scope='session')
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome')
        yield b
        b.close()


def _open(browser, **ctx):
    context = browser.new_context(**ctx)
    page = context.new_page()
    page.errors = []
    page.on('pageerror', lambda e: page.errors.append(str(e)))
    page.on('console', lambda m: m.type == 'error' and page.errors.append(m.text))
    page.goto(INDEX)
    page.wait_for_load_state('load')
    page.wait_for_function("typeof window.__textoReady === 'undefined' || window.__textoReady === true || window.__textoReady === 'error'")
    return context, page


@pytest.fixture
def page(browser):
    context, pg = _open(browser, viewport={'width': 1280, 'height': 800})
    yield pg
    context.close()


@pytest.fixture
def touch_page(browser):
    context, pg = _open(browser, viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
    yield pg
    context.close()


def wait_render(page):
    """Espera a que termine el próximo render programado."""
    page.wait_for_function("window.__renderSeq === window.__renderSeqTarget", timeout=20000)


def rerender(page):
    page.evaluate("window.__renderSeqTarget = (window.__renderSeq||0) + 1; render();")
    wait_render(page)


def load_image(page, w, h, rgba=(200, 40, 40, 255), transparent_rect=None, pipeline=None, full_res=True):
    """Crea una imagen en la página y la carga como si se abriera un archivo."""
    page.evaluate(
        """([w, h, rgba, tr, pipeline, fullRes]) => {
          const c = document.createElement('canvas'); c.width = w; c.height = h;
          const g = c.getContext('2d');
          g.fillStyle = `rgba(${rgba[0]},${rgba[1]},${rgba[2]},${rgba[3]/255})`; g.fillRect(0, 0, w, h);
          if (tr) g.clearRect(tr[0], tr[1], tr[2], tr[3]);
          if (pipeline) state.pipeline = pipeline.map(id => newStep(id));
          state.fullRes = fullRes;
          window.__renderSeqTarget = (window.__renderSeq || 0) + 1;
          setSource(c);
        }""",
        [w, h, list(rgba), transparent_rect, pipeline, full_res],
    )
    wait_render(page)


def pixel(page, x, y, canvas='out'):
    return page.evaluate(
        "([id, x, y]) => Array.from(document.getElementById(id).getContext('2d').getImageData(x, y, 1, 1).data)",
        [canvas, x, y],
    )
