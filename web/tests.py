from django.test import TestCase


class PaginasProtegidasTests(TestCase):
    def test_paginas_privadas_redirecionam_para_login(self):
        for url in ("/", "/wines/", "/wines/new/", "/wines/1/edit/"):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302, url)
            self.assertTrue(r.url.startswith("/login/"), url)
