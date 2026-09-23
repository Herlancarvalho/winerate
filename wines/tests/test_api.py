from datetime import date
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework.test import APIClient, APITestCase

from wines.models import Wine

User = get_user_model()


def fake_label():
    buf = BytesIO()
    Image.new("RGB", (20, 20), "red").save(buf, "PNG")
    return SimpleUploadedFile("rotulo.png", buf.getvalue(), content_type="image/png")


class WineApiTests(APITestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana@ex.com", "Ana", "senha-forte-1")
        self.bia = User.objects.create_user("bia@ex.com", "Bia", "senha-forte-2")
        self.wine = Wine.objects.create(
            user=self.ana, name="Malbec", rating=4, tasting_date=date.today()
        )
        self.client = APIClient()
        self.client.force_authenticate(self.bia)

    def test_lista_mostra_apenas_meus_vinhos(self):
        r = self.client.get("/api/wines")
        self.assertEqual(r.json()["count"], 0)

    def test_vinho_de_outro_usuario_da_404(self):
        url = f"/api/wines/{self.wine.id}"
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(
            self.client.put(url, {"name": "X", "rating": 1, "tasting_date": "2026-01-01"}).status_code, 404
        )
        self.assertEqual(self.client.delete(url).status_code, 404)
        self.assertTrue(Wine.objects.filter(id=self.wine.id).exists())

    def test_campo_user_no_corpo_e_ignorado(self):
        r = self.client.post("/api/wines", {
            "name": "Syrah", "rating": 5, "tasting_date": "2026-01-01", "user": self.ana.id,
        })
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Wine.objects.get(id=r.json()["id"]).user, self.bia)

    def test_nota_invalida_retorna_400(self):
        for nota in (0, 6):
            r = self.client.post("/api/wines", {"name": "X", "rating": nota, "tasting_date": "2026-01-01"})
            self.assertEqual(r.status_code, 400)

    @override_settings(LABEL_VISION_PROVIDER="mock")
    def test_identify_label_nao_grava_nada(self):
        antes = Wine.objects.count()
        r = self.client.post("/api/wines/identify-label", {"image": fake_label()}, format="multipart")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["review_required"])
        self.assertEqual(Wine.objects.count(), antes)

    def test_dashboard_isolado(self):
        r = self.client.get("/api/dashboard")
        self.assertEqual(r.json()["total_wines"], 0)
        self.assertIsNone(r.json()["best_wine"])


class AuthApiTests(APITestCase):
    def test_registro_e_login(self):
        r = self.client.post("/api/register", {"name": "Ana", "email": "Ana@Ex.com", "password": "senha-forte-9"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertIn("token", r.json())
        self.client.logout()
        r = self.client.post("/api/login", {"email": "ana@ex.com", "password": "senha-forte-9"}, format="json")
        self.assertEqual(r.status_code, 200)

    def test_senha_curta_rejeitada(self):
        r = self.client.post("/api/register", {"name": "Ana", "email": "a@ex.com", "password": "1234567"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_login_invalido_e_generico(self):
        r = self.client.post("/api/login", {"email": "x@ex.com", "password": "qualquer-coisa"}, format="json")
        self.assertEqual(r.status_code, 401)
