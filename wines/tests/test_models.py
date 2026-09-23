from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from wines.models import Wine

User = get_user_model()


class WineModelTests(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana@ex.com", "Ana", "senha-forte-1")
        self.bia = User.objects.create_user("bia@ex.com", "Bia", "senha-forte-2")
        self.wine_ana = Wine.objects.create(
            user=self.ana, name="Malbec", rating=4, tasting_date=date.today()
        )

    def test_email_unico_sem_diferenciar_caixa(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user("ANA@EX.COM", "Outra", "senha-forte-3")

    def test_for_user_isola_registros(self):
        self.assertEqual(Wine.objects.for_user(self.ana).count(), 1)
        self.assertEqual(Wine.objects.for_user(self.bia).count(), 0)

    def test_nota_fora_do_intervalo_falha_na_validacao(self):
        for nota in (0, 6):
            wine = Wine(user=self.ana, name="X", rating=nota, tasting_date=date.today())
            with self.assertRaises(ValidationError):
                wine.full_clean()

    def test_check_constraint_no_banco(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Wine.objects.create(user=self.ana, name="X", rating=9, tasting_date=date.today())

    def test_data_futura_invalida(self):
        wine = Wine(
            user=self.ana, name="X", rating=3, tasting_date=date.today() + timedelta(days=1)
        )
        with self.assertRaises(ValidationError):
            wine.full_clean()
