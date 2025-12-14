"""
Django management command to enhance PostgreSQL database with advanced features.

Usage:
    python manage.py enhance_postgresql --all
    python manage.py enhance_postgresql --indexes
    python manage.py enhance_postgresql --views
    python manage.py enhance_postgresql --functions
    python manage.py enhance_postgresql --triggers
    python manage.py enhance_postgresql --refresh
"""
# pylint: disable=no-member
from django.core.management.base import BaseCommand

from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    """Management command to set up PostgreSQL enhancements."""

    help = 'Enhance PostgreSQL database with indexes, views, functions, and triggers'

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--all', action='store_true',
            help='Run all PostgreSQL enhancements'
        )
        parser.add_argument(
            '--indexes', action='store_true',
            help='Create performance indexes'
        )
        parser.add_argument(
            '--views', action='store_true',
            help='Create materialized and regular views'
        )
        parser.add_argument(
            '--functions', action='store_true',
            help='Create stored functions'
        )
        parser.add_argument(
            '--triggers', action='store_true',
            help='Create database triggers'
        )
        parser.add_argument(
            '--refresh', action='store_true',
            help='Refresh all materialized views'
        )
        parser.add_argument(
            '--analyze', action='store_true',
            help='Run ANALYZE on all tables'
        )

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('PostgreSQL Enhancement Command'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Check database engine
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'postgresql' not in db_engine:
            self.stdout.write(self.style.WARNING(
                f'Warning: Not running PostgreSQL (current: {db_engine})'
            ))
            self.stdout.write(self.style.WARNING(
                'Some features may not work correctly.'
            ))

        run_all = options['all']

        if run_all or options['indexes']:
            self._create_indexes()

        if run_all or options['views']:
            self._create_views()

        if run_all or options['functions']:
            self._create_functions()

        if run_all or options['triggers']:
            self._create_triggers()

        if run_all or options['refresh']:
            self._refresh_views()

        if run_all or options['analyze']:
            self._run_analyze()

        if not any([run_all, options['indexes'], options['views'],
                    options['functions'], options['triggers'],
                    options['refresh'], options['analyze']]):
            self.stdout.write(self.style.WARNING(
                'No action specified. Use --help to see available options.'
            ))
            return

        self._print_summary()
        self.stdout.write(self.style.SUCCESS('\n✅ Enhancement complete!'))

    def _create_indexes(self):
        """Create performance indexes."""
        self.stdout.write('\n📌 Creating Performance Indexes...')

        indexes = [
            ("idx_product_fulltext",
             """CREATE INDEX IF NOT EXISTS idx_product_fulltext
                ON store_product USING gin(to_tsvector('english',
                name || ' ' || COALESCE(description, '')));"""),
            ("idx_active_products_price",
             """CREATE INDEX IF NOT EXISTS idx_active_products_price
                ON store_product(price) WHERE is_active = true;"""),
            ("idx_order_user_status",
             """CREATE INDEX IF NOT EXISTS idx_order_user_status_date
                ON store_order(user_id, status, created_at DESC);"""),
            ("idx_review_product",
             """CREATE INDEX IF NOT EXISTS idx_review_product_rating
                ON store_review(product_id, rating DESC);"""),
        ]

        with connection.cursor() as cursor:
            for name, sql in indexes:
                try:
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(f'   ✓ {name}'))
                except Exception as e:  # pylint: disable=broad-exception-caught
                    self.stdout.write(self.style.ERROR(
                        f'   ✗ {name}: {str(e)[:50]}'
                    ))

    def _create_views(self):
        """Create materialized and regular views."""
        self.stdout.write('\n📊 Creating Views...')

        views = {
            'mv_daily_sales': """
                CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_sales AS
                SELECT
                    DATE(created_at) as sale_date,
                    COUNT(*) as total_orders,
                    SUM(paid_amount) as total_revenue,
                    AVG(paid_amount) as avg_order_value
                FROM store_order WHERE paid = true
                GROUP BY DATE(created_at) ORDER BY sale_date DESC;
            """,
            'mv_product_stats': """
                CREATE MATERIALIZED VIEW IF NOT EXISTS mv_product_stats AS
                SELECT
                    p.id, p.name, p.price,
                    COUNT(DISTINCT oi.id) as order_count,
                    COALESCE(AVG(r.rating), 0) as avg_rating
                FROM store_product p
                LEFT JOIN store_orderitem oi ON p.id = oi.product_id
                LEFT JOIN store_review r ON p.id = r.product_id
                GROUP BY p.id, p.name, p.price;
            """,
            'v_dashboard_stats': """
                CREATE OR REPLACE VIEW v_dashboard_stats AS
                SELECT
                    (SELECT COUNT(*) FROM store_order
                     WHERE DATE(created_at) = CURRENT_DATE) as orders_today,
                    (SELECT COALESCE(SUM(paid_amount), 0) FROM store_order
                     WHERE DATE(created_at) = CURRENT_DATE AND paid = true) as revenue_today,
                    (SELECT COUNT(*) FROM store_product
                     WHERE is_active = true) as active_products,
                    (SELECT COUNT(*) FROM store_product
                     WHERE stock_quantity <= 5 AND is_active = true) as low_stock_count;
            """
        }

        with connection.cursor() as cursor:
            for name, sql in views.items():
                try:
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(f'   ✓ {name}'))
                except Exception as e:  # pylint: disable=broad-exception-caught
                    self.stdout.write(self.style.ERROR(
                        f'   ✗ {name}: {str(e)[:50]}'
                    ))

    def _create_functions(self):
        """Create stored functions."""
        self.stdout.write('\n⚙️ Creating Functions...')

        functions = {
            'fn_product_score': """
                CREATE OR REPLACE FUNCTION fn_product_score(pid INTEGER)
                RETURNS NUMERIC AS $$
                DECLARE score NUMERIC := 0;
                BEGIN
                    SELECT COALESCE(AVG(rating) * 20, 0) +
                           (SELECT COUNT(*) FROM store_orderitem
                            WHERE product_id = pid) * 2
                    INTO score FROM store_review WHERE product_id = pid;
                    RETURN ROUND(score, 2);
                END;
                $$ LANGUAGE plpgsql;
            """,
            'fn_trending': """
                CREATE OR REPLACE FUNCTION fn_trending_products(
                    days_back INT DEFAULT 7, lim INT DEFAULT 12
                )
                RETURNS TABLE(
                    product_id INT, name VARCHAR, price NUMERIC,
                    orders BIGINT, score NUMERIC
                ) AS $$
                BEGIN
                    RETURN QUERY
                    SELECT p.id, p.name, p.price,
                           COUNT(oi.id) as orders,
                           (COUNT(oi.id) * 10)::NUMERIC as score
                    FROM store_product p
                    LEFT JOIN store_orderitem oi ON p.id = oi.product_id
                    WHERE p.is_active = true
                    GROUP BY p.id ORDER BY orders DESC LIMIT lim;
                END;
                $$ LANGUAGE plpgsql;
            """
        }

        with connection.cursor() as cursor:
            for name, sql in functions.items():
                try:
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(f'   ✓ {name}'))
                except Exception as e:  # pylint: disable=broad-exception-caught
                    self.stdout.write(self.style.ERROR(
                        f'   ✗ {name}: {str(e)[:50]}'
                    ))

    def _create_triggers(self):
        """Create database triggers."""
        self.stdout.write('\n🔔 Creating Triggers...')

        triggers = {
            'trg_update_stock': """
                CREATE OR REPLACE FUNCTION trg_fn_stock()
                RETURNS TRIGGER AS $$
                BEGIN
                    UPDATE store_product
                    SET stock_quantity = stock_quantity - NEW.quantity
                    WHERE id = NEW.product_id;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                DROP TRIGGER IF EXISTS trigger_stock ON store_orderitem;
                CREATE TRIGGER trigger_stock
                    AFTER INSERT ON store_orderitem
                    FOR EACH ROW EXECUTE FUNCTION trg_fn_stock();
            """,
            'trg_vendor_count': """
                CREATE OR REPLACE FUNCTION trg_fn_vendor_count()
                RETURNS TRIGGER AS $$
                BEGIN
                    IF TG_OP = 'INSERT' THEN
                        UPDATE store_vendor SET total_products = total_products + 1
                        WHERE id = NEW.vendor_id;
                    ELSIF TG_OP = 'DELETE' THEN
                        UPDATE store_vendor SET total_products = total_products - 1
                        WHERE id = OLD.vendor_id;
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                DROP TRIGGER IF EXISTS trigger_vendor_count ON store_product;
                CREATE TRIGGER trigger_vendor_count
                    AFTER INSERT OR DELETE ON store_product
                    FOR EACH ROW EXECUTE FUNCTION trg_fn_vendor_count();
            """
        }

        with connection.cursor() as cursor:
            for name, sql in triggers.items():
                try:
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(f'   ✓ {name}'))
                except Exception as e:  # pylint: disable=broad-exception-caught
                    self.stdout.write(self.style.ERROR(
                        f'   ✗ {name}: {str(e)[:50]}'
                    ))

    def _refresh_views(self):
        """Refresh materialized views."""
        self.stdout.write('\n🔄 Refreshing Materialized Views...')

        views = ['mv_daily_sales', 'mv_product_stats']

        with connection.cursor() as cursor:
            for view in views:
                try:
                    cursor.execute(f"REFRESH MATERIALIZED VIEW {view};")
                    self.stdout.write(self.style.SUCCESS(f'   ✓ Refreshed {view}'))
                except Exception as e:  # pylint: disable=broad-exception-caught
                    self.stdout.write(self.style.WARNING(
                        f'   ⚠ {view}: {str(e)[:50]}'
                    ))

    def _run_analyze(self):
        """Run ANALYZE on database."""
        self.stdout.write('\n📈 Running ANALYZE...')

        with connection.cursor() as cursor:
            try:
                cursor.execute("ANALYZE;")
                self.stdout.write(self.style.SUCCESS('   ✓ ANALYZE completed'))
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.stdout.write(self.style.ERROR(f'   ✗ {str(e)[:50]}'))

    def _print_summary(self):
        """Print enhancement summary."""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('📋 Summary')
        self.stdout.write('=' * 60)

        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM pg_matviews
                    WHERE schemaname = 'public';
                """)
                count = cursor.fetchone()[0]
                self.stdout.write(f'   Materialized Views: {count}')
            except Exception:  # pylint: disable=broad-exception-caught
                self.stdout.write('   Materialized Views: N/A')

            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM pg_proc p
                    JOIN pg_namespace n ON p.pronamespace = n.oid
                    WHERE n.nspname = 'public' AND p.proname LIKE 'fn_%';
                """)
                count = cursor.fetchone()[0]
                self.stdout.write(f'   Custom Functions: {count}')
            except Exception:  # pylint: disable=broad-exception-caught
                self.stdout.write('   Custom Functions: N/A')

            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM pg_indexes
                    WHERE schemaname = 'public' AND indexname LIKE 'idx_%';
                """)
                count = cursor.fetchone()[0]
                self.stdout.write(f'   Custom Indexes: {count}')
            except Exception:  # pylint: disable=broad-exception-caught
                self.stdout.write('   Custom Indexes: N/A')
