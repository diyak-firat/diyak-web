"""Panel stilleri sitenin tasarım değişkenlerinden ayrılmasın (PANEL.md §10, §11)."""

import re
from pathlib import Path

import pytest
from django.conf import settings

STATIK = Path(__file__).resolve().parent.parent / "static" / "panel"
KAYNAK = Path(settings.BASE_DIR).parent / "frontend" / "src" / "styles" / "tokens.css"


@pytest.mark.skipif(not KAYNAK.exists(), reason="frontend/ yok (ör. Docker imajı)")
def test_tokens_kopyasi_kaynakla_ayni():
    assert (STATIK / "tokens.css").read_bytes() == KAYNAK.read_bytes(), (
        "frontend/src/styles/tokens.css değişmiş. Kopyalayın: "
        "cp frontend/src/styles/tokens.css backend/apps/panel/static/panel/tokens.css"
    )


def test_panel_css_sabit_renk_kullanmaz():
    css = (STATIK / "panel.css").read_text(encoding="utf-8")
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(|gradient", css)


def test_yazi_tipi_dosyalari_var():
    css = (STATIK / "fontlar.css").read_text(encoding="utf-8")
    dosyalar = re.findall(r"url\(fontlar/([^)]+)\)", css)
    assert dosyalar
    for ad in dosyalar:
        assert (STATIK / "fontlar" / ad).is_file(), ad
