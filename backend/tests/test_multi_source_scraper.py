import json
from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Purity
from apps.accounting.models import GoldRate, ShopRateSetting
from apps.accounting.scrapers.ksjf_scraper import KSJFScraper
from ninja_api.auth import create_token


SAMPLE_KSJF_HTML = """
<!doctype html>
<html>
<head><title>Market Desk | KSJF</title></head>
<body>
  <p class="muted">Rate update dated 24/10/2026.</p>
  <div class="rate-board big">
    <div><span>Gold 22CT (per gram)</span><strong>Rs 13070</strong></div>
    <div><span>Silver (per kg)</span><strong>Rs 201000</strong></div>
    <div><span>Gold 24CT (per gram)</span><strong>Rs 14140</strong></div>
  </div>
  <div class="market-archive-card is-current">
    <strong>24 Oct 2026</strong>
    <span>Gold 22CT: Rs 13070</span>
    <span>Silver: Rs 201000</span>
    <span>Gold 24CT: Rs 14140</span>
  </div>
</body>
</html>
"""


class MultiSourceGoldRateScraperTestCase(TestCase):
    """
    Unit & Integration tests for multi-tenant, user-selectable bullion rate web scraping:
    - Accurate HTML parsing from KSJF (24CT, 22CT, Silver per kg -> per gram, derived 18KT/14KT)
    - Source dropdown listing endpoint (KSJF, IBJA, Bullion Desk)
    - Dynamic sync endpoint execution
    - Tenant isolation (Shop A KSJF rates vs Shop B IBJA rates)
    - RBAC enforcement
    """

    @classmethod
    def setUpTestData(cls):
        # 1. Setup Tenant 1 (demo)
        cls.tenant1 = Client.objects.filter(schema_name='demo').first()
        if not cls.tenant1:
            cls.tenant1 = Client(schema_name='demo', name='Demo Jewellery')
            cls.tenant1.save()
            Domain.objects.create(domain='demo.localhost', tenant=cls.tenant1, is_primary=True)

        with schema_context(cls.tenant1.schema_name):
            cls.branch1 = Branch.objects.create(name="Karnataka Flagship")
            cls.owner1 = User.objects.create_user(
                username="owner_karnataka",
                password="Password@123",
                role=User.Role.OWNER,
                branch=cls.branch1
            )
            cls.cashier1 = User.objects.create_user(
                username="cashier_karnataka",
                password="Password@123",
                role=User.Role.STAFF,
                branch=cls.branch1
            )
            # Create standard purities
            Purity.objects.get_or_create(name="24KT (999)", defaults={"fineness": Decimal("0.999")})
            Purity.objects.get_or_create(name="22KT (916)", defaults={"fineness": Decimal("0.916")})
            Purity.objects.get_or_create(name="18KT (750)", defaults={"fineness": Decimal("0.750")})
            Purity.objects.get_or_create(name="14KT (585)", defaults={"fineness": Decimal("0.585")})
            Purity.objects.get_or_create(name="Silver (925)", defaults={"fineness": Decimal("0.925")})

        # 2. Setup Tenant 2 (tenant_kalyan)
        cls.tenant2 = Client.objects.filter(schema_name='tenant_kalyan').first()
        if not cls.tenant2:
            cls.tenant2 = Client(schema_name='tenant_kalyan', name='Kalyan Mumbai')
            cls.tenant2.save()
            Domain.objects.create(domain='kalyan.localhost', tenant=cls.tenant2, is_primary=True)

        with schema_context(cls.tenant2.schema_name):
            cls.branch2 = Branch.objects.create(name="Mumbai Showroom")
            cls.owner2 = User.objects.create_user(
                username="owner_mumbai",
                password="Password@123",
                role=User.Role.OWNER,
                branch=cls.branch2
            )
            Purity.objects.get_or_create(name="24KT (999)", defaults={"fineness": Decimal("0.999")})
            Purity.objects.get_or_create(name="22KT (916)", defaults={"fineness": Decimal("0.916")})
            Purity.objects.get_or_create(name="18KT (750)", defaults={"fineness": Decimal("0.750")})

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant1.schema_name):
            self.owner1_token = create_token(self.owner1)
            self.cashier1_token = create_token(self.cashier1)
        with schema_context(self.tenant2.schema_name):
            self.owner2_token = create_token(self.owner2)

    def test_ksjf_html_parser_extraction_and_derived_rates(self):
        """
        Verify exact parsing of 24CT, 22CT, Silver per kg conversion, and 18KT/14KT formulas.
        """
        scraper = KSJFScraper()
        result = scraper.parse_html(SAMPLE_KSJF_HTML)

        self.assertEqual(result.source_id, "ksjf")
        rates = result.rates_per_gram

        # Exact values from sample HTML
        self.assertEqual(rates["24KT (999)"], Decimal("14140.00"))
        self.assertEqual(rates["22KT (916)"], Decimal("13070.00"))
        # Silver: 201000 / 1000 = 201.00
        self.assertEqual(rates["Silver (925)"], Decimal("201.00"))

        # Derived 18KT: 14140 * 0.750 = 10605.00
        self.assertEqual(rates["18KT (750)"], Decimal("10605.00"))
        # Derived 14KT: 14140 * 0.585 = 8271.90
        self.assertEqual(rates["14KT (585)"], Decimal("8271.90"))

    def test_get_rate_sources_dropdown_endpoint(self):
        """Verify GET /api/gold-rates/sources/ returns KSJF, IBJA, and Bullion Desk."""
        with schema_context(self.tenant1.schema_name):
            res = self.client.get(
                '/api/gold-rates/sources/',
                HTTP_AUTHORIZATION=f'Bearer {self.owner1_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 200)
            sources = res.json()
            source_ids = [s['id'] for s in sources]
            self.assertIn('ksjf', source_ids)
            self.assertIn('ibja', source_ids)
            self.assertIn('bullion_desk', source_ids)

            # Check KSJF details
            ksjf = next(s for s in sources if s['id'] == 'ksjf')
            self.assertIn("Karnataka State Jewellers Federation", ksjf['name'])
            self.assertIn("https://ksjf.in/market.php", ksjf['url'])

    def test_sync_rates_endpoint_with_ksjf(self):
        """Verify POST /api/gold-rates/sync/ with source='ksjf' updates tenant rates in DB."""
        with schema_context(self.tenant1.schema_name):
            # Patch scraper.fetch_and_parse to return the parsed sample
            from unittest.mock import patch, AsyncMock
            scraper = KSJFScraper()
            mock_result = scraper.parse_html(SAMPLE_KSJF_HTML)

            with patch('apps.accounting.scrapers.ksjf_scraper.KSJFScraper.fetch_and_parse', new=AsyncMock(return_value=mock_result)):
                res = self.client.post(
                    '/api/gold-rates/sync/',
                    data=json.dumps({"source": "ksjf"}),
                    content_type='application/json',
                    HTTP_AUTHORIZATION=f'Bearer {self.owner1_token}',
                    HTTP_X_TENANT='demo'
                )
                self.assertEqual(res.status_code, 200)
                data = res.json()
                self.assertEqual(data['status'], 'success')
                self.assertEqual(data['source_id'], 'ksjf')
                self.assertGreaterEqual(data['updated_count'], 4)

                # Verify in database: GoldRate records are active
                g24 = GoldRate.objects.get(purity__name="24KT (999)", is_current=True, branch=self.branch1)
                self.assertEqual(g24.rate_per_gram, Decimal("14140.00"))

                g22 = GoldRate.objects.get(purity__name="22KT (916)", is_current=True, branch=self.branch1)
                self.assertEqual(g22.rate_per_gram, Decimal("13070.00"))

                silver = GoldRate.objects.get(purity__name="Silver (925)", is_current=True, branch=self.branch1)
                self.assertEqual(silver.rate_per_gram, Decimal("201.00"))

                # Verify shop setting was updated
                setting = ShopRateSetting.objects.get(branch=self.branch1)
                self.assertEqual(setting.preferred_source, 'ksjf')
                self.assertIsNotNone(setting.last_synced_at)

    def test_multi_tenant_rate_isolation(self):
        """
        Verify that Tenant 1 and Tenant 2 can maintain different rate benchmark sources
        and completely isolated rates in their respective PostgreSQL schemas.
        """
        # Tenant 1 syncs from KSJF
        with schema_context(self.tenant1.schema_name):
            from unittest.mock import patch, AsyncMock
            mock_ksjf = KSJFScraper().parse_html(SAMPLE_KSJF_HTML)
            with patch('apps.accounting.scrapers.ksjf_scraper.KSJFScraper.fetch_and_parse', new=AsyncMock(return_value=mock_ksjf)):
                self.client.post(
                    '/api/gold-rates/sync/',
                    data=json.dumps({"source": "ksjf"}),
                    content_type='application/json',
                    HTTP_AUTHORIZATION=f'Bearer {self.owner1_token}',
                    HTTP_X_TENANT='demo'
                )

        # Tenant 2 syncs from IBJA
        with schema_context(self.tenant2.schema_name):
            res2 = self.client.post(
                '/api/gold-rates/sync/',
                data=json.dumps({"source": "ibja"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner2_token}',
                HTTP_X_TENANT='tenant_kalyan'
            )
            self.assertEqual(res2.status_code, 200)

            # Tenant 2 has IBJA 24KT rate (14180.00)
            t2_rate = GoldRate.objects.get(purity__name="24KT (999)", is_current=True, branch=self.branch2)
            self.assertEqual(t2_rate.rate_per_gram, Decimal("14180.00"))

        # Tenant 1 still has KSJF 24KT rate (14140.00)
        with schema_context(self.tenant1.schema_name):
            t1_rate = GoldRate.objects.get(purity__name="24KT (999)", is_current=True, branch=self.branch1)
            self.assertEqual(t1_rate.rate_per_gram, Decimal("14140.00"))

    def test_rbac_staff_cannot_sync_rates(self):
        """Verify staff/cashier user cannot sync rates (403 Forbidden)."""
        with schema_context(self.tenant1.schema_name):
            res = self.client.post(
                '/api/gold-rates/sync/',
                data=json.dumps({"source": "ksjf"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier1_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 403)

    def test_invalid_source_returns_400(self):
        """Verify invalid source identifier returns HTTP 400 Bad Request."""
        with schema_context(self.tenant1.schema_name):
            res = self.client.post(
                '/api/gold-rates/sync/',
                data=json.dumps({"source": "unknown_scraped_site"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner1_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 400)
            self.assertIn("Unknown or unsupported rate source", res.json()['error'])

    def test_auto_sync_after_multiple_manual_updates(self):
        """Verify Auto-Sync succeeds even when multiple manual rates exist on the same date for a purity."""
        from django.utils import timezone
        with schema_context(self.tenant1.schema_name):
            today = timezone.localdate()
            purity_24k = Purity.objects.get(name="24KT (999)")

            # Simulate 3 manual updates created earlier today
            GoldRate.objects.create(
                purity=purity_24k,
                rate_per_gram=Decimal("7500.00"),
                effective_date=today,
                is_current=False,
                branch=self.branch1,
                entered_by=self.owner1
            )
            GoldRate.objects.create(
                purity=purity_24k,
                rate_per_gram=Decimal("7520.00"),
                effective_date=today,
                is_current=False,
                branch=self.branch1,
                entered_by=self.owner1
            )
            GoldRate.objects.create(
                purity=purity_24k,
                rate_per_gram=Decimal("7530.00"),
                effective_date=today,
                is_current=True,
                branch=self.branch1,
                entered_by=self.owner1
            )

            # Confirm 3 records exist for today
            self.assertEqual(
                GoldRate.objects.filter(purity=purity_24k, branch=self.branch1, effective_date=today).count(),
                3
            )

            # Trigger auto-sync from KSJF
            from unittest.mock import patch
            from apps.accounting.scrapers.base import RateScrapeResult
            mock_scrape = RateScrapeResult(
                source_id="ksjf",
                source_name="Karnataka State Jewellers Federation",
                source_url="https://ksjf.in/market.php",
                rates_per_gram={"24KT (999)": Decimal("14140.00"), "22KT (916)": Decimal("13070.00")},
                raw_data={},
                effective_date=today
            )
            with patch('apps.accounting.scrapers.ksjf_scraper.KSJFScraper.fetch_and_parse', return_value=mock_scrape):
                res = self.client.post(
                    '/api/gold-rates/sync/',
                    data=json.dumps({"source": "ksjf"}),
                    content_type='application/json',
                    HTTP_AUTHORIZATION=f'Bearer {self.owner1_token}',
                    HTTP_X_TENANT='demo'
                )

            self.assertEqual(res.status_code, 200, res.content)
            data = res.json()
            self.assertEqual(data["status"], "success")

            # Check that only ONE rate is current for this purity & branch
            current_rates = GoldRate.objects.filter(purity=purity_24k, branch=self.branch1, is_current=True)
            self.assertEqual(current_rates.count(), 1)
            self.assertEqual(current_rates.first().rate_per_gram, Decimal("14140.00"))
