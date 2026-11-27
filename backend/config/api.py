"""Genel API uç noktaları."""

from django.db import connection
from django.db.utils import DatabaseError
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([])
def saglik(request: Request) -> Response:
    """İzleme servisi için: uygulama ayakta ve veritabanına ulaşıyor mu?

    Ayrıntı (hata metni, sürüm, sunucu adı) dışarı verilmez.
    """
    try:
        with connection.cursor() as imlec:
            imlec.execute("SELECT 1")
    except DatabaseError:
        return Response({"durum": "hata"}, status=503)
    return Response({"durum": "tamam"})
