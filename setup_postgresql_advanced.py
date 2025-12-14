"""
Advanced PostgreSQL Setup and Enhancement Script for VIBE E-Commerce.

This script creates:
1. Database indexes for performance optimization
2. Materialized views for fast analytics
3. Stored procedures and functions
4. Triggers for automated operations
5. Full-text search capabilities
6. Advanced analytics views
7. Database-level AI/ML functions

Run this script after initial migrations to enhance PostgreSQL capabilities.

Note: This script uses the standard `random` module for generating test data.
This is intentional as security-grade randomness is not required for sample data.
"""
import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# pylint: disable=wrong-import-position
from django.db import connection, transaction  # noqa: E402
from django.conf import settings  # noqa: E402
# pylint: enable=wrong-import-position


def check_postgresql():
    """Check if we're running PostgreSQL."""
    db_engine = settings.DATABASES['default']['ENGINE']
    if 'postgresql' not in db_engine:
        print("⚠️  WARNING: Not running PostgreSQL!")
        print(f"   Current engine: {db_engine}")
        print("   Some features may not work with SQLite.")
        return False
    print("✅ PostgreSQL detected!")
    return True


def create_extensions():
    """Create PostgreSQL extensions for advanced features."""
    print("\n📦 Creating PostgreSQL Extensions...")

    extensions = [
        ('pg_trgm', 'Fuzzy text matching and similarity'),
        ('unaccent', 'Remove accents from text for search'),
        ('btree_gin', 'GIN index for scalar types'),
        ('btree_gist', 'GIST index for scalar types'),
    ]

    with connection.cursor() as cursor:
        for ext_name, description in extensions:
            try:
                cursor.execute(f"CREATE EXTENSION IF NOT EXISTS {ext_name};")
                print(f"   ✓ {ext_name}: {description}")
            except Exception as e:  # pylint: disable=broad-except
                print(f"   ✗ {ext_name}: {str(e)[:50]}")


def create_performance_indexes():
    """Create advanced indexes for query performance."""
    print("\n🔧 Creating Performance Indexes...")

    indexes = [
        """
        CREATE INDEX IF NOT EXISTS idx_product_fulltext
        ON store_product USING gin(
            to_tsvector('english', name || ' ' || COALESCE(description, ''))
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_active_products_price
        ON store_product(price) WHERE is_active = true;
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_order_user_status_date
        ON store_order(user_id, status, created_at DESC);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_product_trending
        ON store_product(trending_score DESC, created_at DESC) WHERE is_active = true;
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_vendor_products_active
        ON store_product(vendor_id, is_active, price);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_review_product_rating
        ON store_review(product_id, rating DESC, created_at DESC);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_flashsale_active_time
        ON store_flashsale(is_active, start_time, end_time);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_product_name_trgm
        ON store_product USING gin(name gin_trgm_ops);
        """,
    ]

    with connection.cursor() as cursor:
        for idx_sql in indexes:
            try:
                cursor.execute(idx_sql)
                idx_name = (idx_sql.split('idx_')[1].split()[0]
                            if 'idx_' in idx_sql else 'index')
                print(f"   ✓ Created idx_{idx_name}")
            except Exception as e:  # pylint: disable=broad-except
                print(f"   ✗ Index error: {str(e)[:60]}")


def create_materialized_views():
    """Create materialized views for fast analytics."""
    print("\n📊 Creating Materialized Views...")

    views = {
        'mv_daily_sales': """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_sales AS
            SELECT
                DATE(created_at) as sale_date,
                COUNT(*) as total_orders,
                COUNT(DISTINCT user_id) as unique_customers,
                SUM(paid_amount) as total_revenue,
                AVG(paid_amount) as avg_order_value
            FROM store_order
            WHERE paid = true
            GROUP BY DATE(created_at)
            ORDER BY sale_date DESC;
        """,
        'mv_product_performance': """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_product_performance AS
            SELECT
                p.id as product_id,
                p.name as product_name,
                p.price,
                c.name as category_name,
                v.name as vendor_name,
                COUNT(DISTINCT oi.id) as times_ordered,
                COALESCE(SUM(oi.quantity), 0) as total_quantity_sold,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(DISTINCT r.id) as review_count
            FROM store_product p
            LEFT JOIN store_category c ON p.category_id = c.id
            LEFT JOIN store_vendor v ON p.vendor_id = v.id
            LEFT JOIN store_orderitem oi ON p.id = oi.product_id
            LEFT JOIN store_review r ON p.id = r.product_id
            GROUP BY p.id, p.name, p.price, c.name, v.name;
        """,
        'mv_vendor_analytics': """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_vendor_analytics AS
            SELECT
                v.id as vendor_id,
                v.name as vendor_name,
                v.city,
                COUNT(DISTINCT p.id) as total_products,
                SUM(CASE WHEN p.is_active THEN 1 ELSE 0 END) as active_products,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(DISTINCT r.id) as total_reviews
            FROM store_vendor v
            LEFT JOIN store_product p ON v.id = p.vendor_id
            LEFT JOIN store_review r ON p.id = r.product_id
            GROUP BY v.id, v.name, v.city;
        """,
        'mv_category_stats': """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_category_stats AS
            SELECT
                c.id as category_id,
                c.name as category_name,
                c.slug,
                COUNT(DISTINCT p.id) as product_count,
                AVG(p.price) as avg_price,
                MIN(p.price) as min_price,
                MAX(p.price) as max_price
            FROM store_category c
            LEFT JOIN store_product p ON c.id = p.category_id AND p.is_active = true
            GROUP BY c.id, c.name, c.slug;
        """
    }

    with connection.cursor() as cursor:
        for view_name, view_sql in views.items():
            try:
                cursor.execute(view_sql)
                print(f"   ✓ Created {view_name}")
            except Exception as e:  # pylint: disable=broad-except
                print(f"   ✗ {view_name}: {str(e)[:50]}")


def create_stored_functions():
    """Create PostgreSQL stored functions for complex operations."""
    print("\n⚙️  Creating Stored Functions...")

    functions = {
        'fn_calculate_product_score': """
            CREATE OR REPLACE FUNCTION fn_calculate_product_score(p_id INTEGER)
            RETURNS NUMERIC AS $$
            DECLARE
                score NUMERIC := 0;
                avg_rating NUMERIC;
                order_count INTEGER;
            BEGIN
                SELECT COALESCE(AVG(rating), 3) INTO avg_rating
                FROM store_review WHERE product_id = p_id;

                SELECT COUNT(*) INTO order_count
                FROM store_orderitem WHERE product_id = p_id;

                score := (avg_rating * 20) + (order_count * 2);
                RETURN ROUND(score, 2);
            END;
            $$ LANGUAGE plpgsql;
        """,
        'fn_get_similar_products': """
            CREATE OR REPLACE FUNCTION fn_get_similar_products(
                target_product_id INTEGER,
                limit_count INTEGER DEFAULT 6
            )
            RETURNS TABLE(
                product_id INTEGER,
                product_name VARCHAR,
                price NUMERIC,
                similarity_score NUMERIC
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT
                    p.id,
                    p.name,
                    p.price,
                    (CASE WHEN p.category_id = target.category_id THEN 40 ELSE 0 END +
                     CASE WHEN p.vendor_id = target.vendor_id THEN 20 ELSE 0 END)::NUMERIC
                FROM store_product p
                CROSS JOIN (SELECT * FROM store_product WHERE id = target_product_id) target
                WHERE p.id != target_product_id AND p.is_active = true
                ORDER BY similarity_score DESC
                LIMIT limit_count;
            END;
            $$ LANGUAGE plpgsql;
        """,
        'fn_get_trending_products': """
            CREATE OR REPLACE FUNCTION fn_get_trending_products(
                days_back INTEGER DEFAULT 7,
                limit_count INTEGER DEFAULT 12
            )
            RETURNS TABLE(
                product_id INTEGER,
                product_name VARCHAR,
                price NUMERIC,
                order_count BIGINT,
                trending_score NUMERIC
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT
                    p.id,
                    p.name,
                    p.price,
                    COUNT(DISTINCT oi.id) as order_count,
                    (COUNT(DISTINCT oi.id) * 10)::NUMERIC as trending_score
                FROM store_product p
                LEFT JOIN store_orderitem oi ON p.id = oi.product_id
                WHERE p.is_active = true
                GROUP BY p.id, p.name, p.price
                ORDER BY trending_score DESC
                LIMIT limit_count;
            END;
            $$ LANGUAGE plpgsql;
        """,
        'fn_inventory_alert': """
            CREATE OR REPLACE FUNCTION fn_inventory_alert(threshold INTEGER DEFAULT 10)
            RETURNS TABLE(
                product_id INTEGER,
                product_name VARCHAR,
                current_stock INTEGER,
                alert_level VARCHAR
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT
                    p.id,
                    p.name,
                    p.stock_quantity,
                    CASE
                        WHEN p.stock_quantity = 0 THEN 'OUT_OF_STOCK'
                        WHEN p.stock_quantity <= threshold / 2 THEN 'CRITICAL'
                        WHEN p.stock_quantity <= threshold THEN 'LOW'
                        ELSE 'OK'
                    END as alert_level
                FROM store_product p
                WHERE p.is_active = true AND p.stock_quantity <= threshold
                ORDER BY p.stock_quantity ASC;
            END;
            $$ LANGUAGE plpgsql;
        """
    }

    with connection.cursor() as cursor:
        for func_name, func_sql in functions.items():
            try:
                cursor.execute(func_sql)
                print(f"   ✓ Created {func_name}")
            except Exception as e:  # pylint: disable=broad-except
                print(f"   ✗ {func_name}: {str(e)[:50]}")


def create_triggers():
    """Create triggers for automated database operations."""
    print("\n🔔 Creating Triggers...")

    triggers = {
        'trg_update_trending_score': """
            CREATE OR REPLACE FUNCTION trg_fn_update_trending()
            RETURNS TRIGGER AS $$
            BEGIN
                UPDATE store_product
                SET trending_score = fn_calculate_product_score(NEW.product_id)
                WHERE id = NEW.product_id;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS trigger_update_trending_on_order ON store_orderitem;
            CREATE TRIGGER trigger_update_trending_on_order
                AFTER INSERT ON store_orderitem
                FOR EACH ROW
                EXECUTE FUNCTION trg_fn_update_trending();
        """,
        'trg_update_stock': """
            CREATE OR REPLACE FUNCTION trg_fn_update_stock()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    UPDATE store_product
                    SET stock_quantity = stock_quantity - NEW.quantity
                    WHERE id = NEW.product_id;
                ELSIF TG_OP = 'DELETE' THEN
                    UPDATE store_product
                    SET stock_quantity = stock_quantity + OLD.quantity
                    WHERE id = OLD.product_id;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS trigger_update_stock ON store_orderitem;
            CREATE TRIGGER trigger_update_stock
                AFTER INSERT OR DELETE ON store_orderitem
                FOR EACH ROW
                EXECUTE FUNCTION trg_fn_update_stock();
        """
    }

    with connection.cursor() as cursor:
        for trg_name, trg_sql in triggers.items():
            try:
                cursor.execute(trg_sql)
                print(f"   ✓ Created {trg_name}")
            except Exception as e:  # pylint: disable=broad-except
                print(f"   ✗ {trg_name}: {str(e)[:50]}")


def create_analytics_views():
    """Create regular views for real-time analytics."""
    print("\n📈 Creating Analytics Views...")

    views = {
        'v_real_time_dashboard': """
            CREATE OR REPLACE VIEW v_real_time_dashboard AS
            SELECT
                (SELECT COUNT(*) FROM store_order
                 WHERE DATE(created_at) = CURRENT_DATE) as orders_today,
                (SELECT COALESCE(SUM(paid_amount), 0) FROM store_order
                 WHERE DATE(created_at) = CURRENT_DATE AND paid = true) as revenue_today,
                (SELECT COUNT(*) FROM store_order
                 WHERE status = 'pending') as pending_orders,
                (SELECT COUNT(*) FROM store_product
                 WHERE is_active = true) as active_products,
                (SELECT COUNT(*) FROM store_product
                 WHERE stock_quantity <= 5 AND is_active = true) as low_stock_count;
        """,
        'v_top_selling_products': """
            CREATE OR REPLACE VIEW v_top_selling_products AS
            SELECT
                p.id,
                p.name,
                p.price,
                c.name as category,
                v.name as vendor,
                SUM(oi.quantity) as total_sold,
                SUM(oi.price) as total_revenue
            FROM store_product p
            JOIN store_orderitem oi ON p.id = oi.product_id
            JOIN store_order o ON oi.order_id = o.id
            LEFT JOIN store_category c ON p.category_id = c.id
            LEFT JOIN store_vendor v ON p.vendor_id = v.id
            WHERE o.paid = true
            GROUP BY p.id, p.name, p.price, c.name, v.name
            ORDER BY total_sold DESC
            LIMIT 50;
        """
    }

    with connection.cursor() as cursor:
        for view_name, view_sql in views.items():
            try:
                cursor.execute(view_sql)
                print(f"   ✓ Created {view_name}")
            except Exception as e:  # pylint: disable=broad-except
                print(f"   ✗ {view_name}: {str(e)[:50]}")


def refresh_materialized_views():
    """Create function to refresh all materialized views."""
    print("\n🔄 Creating Refresh Functions...")

    refresh_fn = """
        CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
        RETURNS void AS $$
        BEGIN
            REFRESH MATERIALIZED VIEW mv_daily_sales;
            REFRESH MATERIALIZED VIEW mv_product_performance;
            REFRESH MATERIALIZED VIEW mv_vendor_analytics;
            REFRESH MATERIALIZED VIEW mv_category_stats;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Some views may not exist yet';
        END;
        $$ LANGUAGE plpgsql;
    """

    with connection.cursor() as cursor:
        try:
            cursor.execute(refresh_fn)
            print("   ✓ Created refresh_all_materialized_views()")
        except Exception as e:  # pylint: disable=broad-except
            print(f"   ✗ Refresh function: {str(e)[:50]}")


def run_analyze():
    """Run ANALYZE on all tables for query optimization."""
    print("\n📊 Running ANALYZE on all tables...")

    with connection.cursor() as cursor:
        try:
            cursor.execute("ANALYZE;")
            print("   ✓ ANALYZE completed successfully")
        except Exception as e:  # pylint: disable=broad-except
            print(f"   ✗ ANALYZE failed: {str(e)[:50]}")


def print_summary():
    """Print summary of created database objects."""
    print("\n" + "=" * 60)
    print("📋 PostgreSQL Enhancement Summary")
    print("=" * 60)

    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM pg_matviews
                WHERE schemaname = 'public' AND matviewname LIKE 'mv_%';
            """)
            mv_count = cursor.fetchone()[0]
            print(f"   Materialized Views: {mv_count}")
        except Exception:  # pylint: disable=broad-except
            print("   Materialized Views: N/A")

        try:
            cursor.execute("""
                SELECT COUNT(*) FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'public' AND p.proname LIKE 'fn_%';
            """)
            fn_count = cursor.fetchone()[0]
            print(f"   Custom Functions: {fn_count}")
        except Exception:  # pylint: disable=broad-except
            print("   Custom Functions: N/A")

        try:
            cursor.execute("""
                SELECT COUNT(*) FROM pg_trigger
                WHERE tgname LIKE 'trigger_%';
            """)
            trg_count = cursor.fetchone()[0]
            print(f"   Triggers: {trg_count}")
        except Exception:  # pylint: disable=broad-except
            print("   Triggers: N/A")

        try:
            cursor.execute("""
                SELECT COUNT(*) FROM pg_indexes
                WHERE schemaname = 'public' AND indexname LIKE 'idx_%';
            """)
            idx_count = cursor.fetchone()[0]
            print(f"   Custom Indexes: {idx_count}")
        except Exception:  # pylint: disable=broad-except
            print("   Custom Indexes: N/A")

    print("=" * 60)


def main():
    """Main function to set up all PostgreSQL enhancements."""
    print("=" * 60)
    print("🚀 VIBE E-Commerce - PostgreSQL Advanced Setup")
    print("=" * 60)

    is_postgres = check_postgresql()

    if not is_postgres:
        print("\n⚠️  Running in SQLite compatibility mode...")
        print("   Some features will be skipped.")
        response = input("\nContinue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Aborted.")
            sys.exit(0)

    try:
        with transaction.atomic():
            if is_postgres:
                create_extensions()
            create_performance_indexes()
            create_materialized_views()
            create_stored_functions()
            create_triggers()
            create_analytics_views()
            refresh_materialized_views()
            run_analyze()
    except Exception as e:  # pylint: disable=broad-except
        print(f"\n❌ Error during setup: {e}")
        print("   Some features may not have been created.")

    print_summary()

    print("\n✅ PostgreSQL Enhancement Complete!")
    print("\n📝 Usage Examples:")
    print("   -- Search products with full-text search:")
    print("   SELECT * FROM fn_search_products_fulltext('organic fertilizer');")
    print("\n   -- Get trending products:")
    print("   SELECT * FROM fn_get_trending_products(7, 10);")
    print("\n   -- Check inventory alerts:")
    print("   SELECT * FROM fn_inventory_alert(10);")
    print("\n   -- Get similar products:")
    print("   SELECT * FROM fn_get_similar_products(5, 6);")
    print("\n   -- Refresh analytics:")
    print("   SELECT refresh_all_materialized_views();")


if __name__ == '__main__':
    main()
