from unittest import mock

import pytest
from django.db.utils import OperationalError
from django.urls import reverse


@pytest.mark.django_db
def test_saglik_giris_gerektirmez_ve_json_doner(client):
    yanit = client.get(reverse("saglik"))
    assert yanit.status_code == 200
    assert yanit["Content-Type"] == "application/json"
    assert yanit.json() == {"durum": "tamam"}


@pytest.mark.django_db
def test_saglik_veritabani_yoksa_503_ve_ayrinti_vermez(client):
    with mock.patch("config.api.connection.cursor", side_effect=OperationalError("gizli ayrinti")):
        yanit = client.get(reverse("saglik"))
    assert yanit.status_code == 503
    assert yanit.json() == {"durum": "hata"}
    assert "gizli" not in yanit.content.decode()


@pytest.mark.django_db
def test_saglik_yazma_istegini_reddeder(client):
    yanit = client.post(reverse("saglik"), data={}, content_type="application/json")
    assert yanit.status_code == 405
