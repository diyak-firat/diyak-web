"""Duyuru gövdesi kaydedilmeden önce temizlenir (PANEL.md §9, A2 kabul: <script> temizlenir)."""

import pytest

from apps.duyurular.models import Duyuru
from apps.duyurular.temizle import html_temizle


@pytest.mark.parametrize(
    "girdi,cikti",
    [
        ("<p>Merhaba <strong>dünya</strong></p>", "<p>Merhaba <strong>dünya</strong></p>"),
        ("<p>a<script>alert(1)</script></p>", "<p>a</p>"),
        ("<style>p{}</style><p>x</p>", "<p>x</p>"),
        ('<p onclick="x()">x</p>', "<p>x</p>"),
        ('<img src="x" onerror="alert(1)">', ""),
        ('<a href="https://firat.edu.tr">FÜ</a>', '<a href="https://firat.edu.tr" rel="noopener noreferrer">FÜ</a>'),
        ('<a href="mailto:ornek@firat.edu.tr">e</a>', '<a href="mailto:ornek@firat.edu.tr" rel="noopener noreferrer">e</a>'),
        ('<a href="javascript:alert(1)">j</a>', '<a rel="noopener noreferrer">j</a>'),
        ('<a href="http://ornek.org">h</a>', '<a rel="noopener noreferrer">h</a>'),
        ('<a href="/goreli">g</a>', '<a rel="noopener noreferrer">g</a>'),
        ('<a href=" JAVASCRIPT:alert(1)">j</a>', '<a rel="noopener noreferrer">j</a>'),
        ('<a href="https://x.org" target="_blank" rel="opener">x</a>', '<a href="https://x.org" rel="noopener noreferrer">x</a>'),
        ("<h1>Büyük</h1><h2>Orta</h2><h4>küçük</h4>", "Büyük<h2>Orta</h2>küçük"),
        ("<div><span>iç</span></div>", "iç"),
        ("<!-- gizli --><p>x</p>", "<p>x</p>"),
        ("<ul><li>a</li></ul><ol><li>b</li></ol><blockquote>c</blockquote><p>d<br>e<em>f</em></p>",
         "<ul><li>a</li></ul><ol><li>b</li></ol><blockquote>c</blockquote><p>d<br>e<em>f</em></p>"),
        ('<iframe src="https://kotu.example"></iframe>', ""),
    ],
)
def test_html_temizle(girdi, cikti):
    assert html_temizle(girdi) == cikti


@pytest.mark.django_db
def test_model_kaydederken_her_zaman_temizler(kullanici_yap):
    d = Duyuru.objects.create(baslik="Deneme", ozet="ö", govde="<p>x</p><script>alert(1)</script>", olusturan=kullanici_yap())
    d.refresh_from_db()
    assert d.govde == "<p>x</p>"
    Duyuru.objects.filter(pk=d.pk).update(govde="<script>1</script>")  # yalnızca save() korur;
    d.refresh_from_db()
    d.save()
    d.refresh_from_db()
    assert d.govde == ""
