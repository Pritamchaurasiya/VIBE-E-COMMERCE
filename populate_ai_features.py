"""
PostgreSQL AI Features for VIBE E-Commerce.

This module adds AI-powered PostgreSQL functions, triggers, views, and
procedures for:
- Smart Recommendations
- Auto-Scoring
- User Segmentation
- Fraud Detection
- Stock Alerts
- Customer Lifetime Value
- Churn Prediction

Note:
    These features require PostgreSQL as the database backend.
    They will not work with SQLite.

Usage:
    python populate_ai_features.py

Author: VIBE E-Commerce Team
"""
import logging
import os
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# pylint: disable=wrong-import-position
from django.db import connection, OperationalError, ProgrammingError  # noqa: E402
from django.conf import settings  # noqa: E402
# pylint: enable=wrong-import-position

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class SQLExecutionResult:
    """Result of SQL execution."""
    success: bool
    name: str
    error_message: Optional[str] = None


class DatabaseValidator:
    """Validates database configuration and requirements."""

    @staticmethod
    def is_postgresql() -> bool:
        """Check if the database backend is PostgreSQL."""
        db_engine = settings.DATABASES.get('default', {}).get('ENGINE', '')
        return 'postgresql' in db_engine.lower()

    @staticmethod
    def check_connection() -> bool:
        """Test database connection."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except (OperationalError, ProgrammingError) as e:
            logger.error("Database connection failed: %s", e)
            return False

    @staticmethod
    def check_required_tables() -> Tuple[bool, List[str]]:
        """Check if required tables exist."""
        required_tables = [
            'store_product', 'store_order', 'store_orderitem',
            'store_review', 'store_vendor', 'store_category',
            'auth_user'
        ]
        missing = []

        try:
            with connection.cursor() as cursor:
                for table in required_tables:
                    cursor.execute(
                        "SELECT EXISTS (SELECT FROM information_schema.tables "
                        "WHERE table_name = %s)",
                        [table]
                    )
                    if not cursor.fetchone()[0]:
                        missing.append(table)
        except (OperationalError, ProgrammingError) as e:
            logger.error("Table check failed: %s", e)
            return False, required_tables

        return len(missing) == 0, missing


class AIFunctionManager:
    """Manages AI PostgreSQL functions."""

    def __init__(self):
        """Initialize the function manager."""
        self.results: List[SQLExecutionResult] = []

    def execute_sql(self, name: str, sql: str) -> SQLExecutionResult:
        """
        Execute SQL statement safely.

        Args:
            name: Identifier for the SQL statement
            sql: SQL statement to execute

        Returns:
            SQLExecutionResult with success status and error if any
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
            result = SQLExecutionResult(success=True, name=name)
            logger.info("Successfully created: %s", name)
        except (OperationalError, ProgrammingError) as e:
            error_msg = str(e)[:100]
            result = SQLExecutionResult(
                success=False, name=name, error_message=error_msg
            )
            logger.warning("Failed to create %s: %s", name, error_msg)

        self.results.append(result)
        return result

    def get_summary(self) -> Tuple[int, int]:
        """Get summary of executions (success_count, failure_count)."""
        success = sum(1 for r in self.results if r.success)
        failure = len(self.results) - success
        return success, failure


def get_ai_functions() -> List[Tuple[str, str]]:
    """
    Get list of AI function definitions.

    Returns:
        List of tuples containing (function_name, sql_definition)
    """
    return [
        ("get_smart_recommendations", """
            CREATE OR REPLACE FUNCTION get_smart_recommendations(
                user_id_param INTEGER,
                limit_count INTEGER DEFAULT 10
            )
            RETURNS TABLE(
                product_id INTEGER,
                product_name VARCHAR,
                recommendation_score NUMERIC,
                reason VARCHAR
            ) AS $$
            BEGIN
                -- Validate input parameters
                IF user_id_param IS NULL OR user_id_param <= 0 THEN
                    RAISE NOTICE 'Invalid user_id_param: %', user_id_param;
                    RETURN;
                END IF;

                IF limit_count IS NULL OR limit_count <= 0 THEN
                    limit_count := 10;
                END IF;

                RETURN QUERY
                SELECT DISTINCT
                    p.id::INTEGER,
                    p.name::VARCHAR,
                    (
                        COALESCE(p.trending_score, 0) * 0.3 +
                        COALESCE(p.view_count, 0)::NUMERIC / 100 * 0.2 +
                        COALESCE((
                            SELECT AVG(r.rating)
                            FROM store_review r
                            WHERE r.product_id = p.id
                        ), 3.5) * 10 * 0.3 +
                        RANDOM() * 20
                    )::NUMERIC as recommendation_score,
                    'Based on your purchase history'::VARCHAR as reason
                FROM store_product p
                WHERE p.category_id IN (
                    SELECT DISTINCT p_inner.category_id
                    FROM store_orderitem oi_inner
                    JOIN store_order o ON oi_inner.order_id = o.id
                    JOIN store_product p_inner ON oi_inner.product_id = p_inner.id
                    WHERE o.user_id = user_id_param
                )
                AND p.id NOT IN (
                    SELECT oi2.product_id
                    FROM store_orderitem oi2
                    JOIN store_order o2 ON oi2.order_id = o2.id
                    WHERE o2.user_id = user_id_param
                )
                AND p.is_active = true
                ORDER BY recommendation_score DESC
                LIMIT limit_count;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("calculate_customer_lifetime_value", """
            CREATE OR REPLACE FUNCTION calculate_customer_lifetime_value(
                user_id_param INTEGER
            )
            RETURNS TABLE(
                total_orders BIGINT,
                total_spent NUMERIC,
                avg_order_value NUMERIC,
                days_as_customer INTEGER,
                estimated_clv NUMERIC,
                customer_tier VARCHAR
            ) AS $$
            DECLARE
                v_total_orders BIGINT;
                v_total_spent NUMERIC;
                v_avg_order NUMERIC;
                v_days INTEGER;
                v_clv NUMERIC;
                v_tier VARCHAR;
            BEGIN
                -- Validate input
                IF user_id_param IS NULL OR user_id_param <= 0 THEN
                    RETURN;
                END IF;

                SELECT
                    COUNT(*),
                    COALESCE(SUM(paid_amount), 0),
                    COALESCE(AVG(paid_amount), 0),
                    COALESCE(
                        EXTRACT(DAY FROM NOW() - MIN(created_at))::INTEGER,
                        0
                    )
                INTO v_total_orders, v_total_spent, v_avg_order, v_days
                FROM store_order
                WHERE user_id = user_id_param AND paid = true;

                -- CLV = Avg Order * Orders per Year * Expected Years (3)
                v_clv := CASE
                    WHEN v_days > 0 AND v_total_orders > 0 THEN
                        (v_avg_order * (v_total_orders::NUMERIC / GREATEST(v_days, 1) * 365) * 3)
                    ELSE 0
                END;

                v_tier := CASE
                    WHEN v_clv > 100000 THEN 'Platinum'
                    WHEN v_clv > 50000 THEN 'Gold'
                    WHEN v_clv > 20000 THEN 'Silver'
                    ELSE 'Bronze'
                END;

                RETURN QUERY SELECT
                    v_total_orders,
                    v_total_spent,
                    ROUND(v_avg_order, 2),
                    v_days,
                    ROUND(v_clv, 2),
                    v_tier;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("calculate_fraud_risk_score", """
            CREATE OR REPLACE FUNCTION calculate_fraud_risk_score(
                order_id_param INTEGER
            )
            RETURNS TABLE(
                risk_score INTEGER,
                risk_level VARCHAR,
                risk_factors TEXT[]
            ) AS $$
            DECLARE
                v_score INTEGER := 0;
                v_factors TEXT[] := ARRAY[]::TEXT[];
                v_order RECORD;
            BEGIN
                -- Validate input
                IF order_id_param IS NULL OR order_id_param <= 0 THEN
                    RETURN QUERY SELECT 0, 'INVALID'::VARCHAR, ARRAY['Invalid order ID']::TEXT[];
                    RETURN;
                END IF;

                SELECT o.*,
                    (SELECT COUNT(*) FROM store_order WHERE user_id = o.user_id) as user_order_count,
                    (SELECT AVG(paid_amount) FROM store_order WHERE user_id = o.user_id AND paid = true) as user_avg
                INTO v_order
                FROM store_order o
                WHERE o.id = order_id_param;

                IF v_order IS NULL THEN
                    RETURN QUERY SELECT 0, 'NOT_FOUND'::VARCHAR, ARRAY['Order not found']::TEXT[];
                    RETURN;
                END IF;

                -- High value order (>50000)
                IF v_order.paid_amount > 50000 THEN
                    v_score := v_score + 20;
                    v_factors := array_append(v_factors, 'High value order (>' || v_order.paid_amount || ')');
                END IF;

                -- First order from user
                IF v_order.user_order_count = 1 THEN
                    v_score := v_score + 15;
                    v_factors := array_append(v_factors, 'First order from user');
                END IF;

                -- Order significantly higher than user average
                IF v_order.user_avg IS NOT NULL AND v_order.paid_amount > v_order.user_avg * 3 THEN
                    v_score := v_score + 25;
                    v_factors := array_append(v_factors, 'Order 3x higher than user average');
                END IF;

                -- Late night order (11 PM - 5 AM)
                IF EXTRACT(HOUR FROM v_order.created_at) >= 23
                   OR EXTRACT(HOUR FROM v_order.created_at) <= 5 THEN
                    v_score := v_score + 10;
                    v_factors := array_append(v_factors, 'Late night order');
                END IF;

                RETURN QUERY SELECT
                    v_score,
                    CASE
                        WHEN v_score >= 50 THEN 'HIGH'
                        WHEN v_score >= 25 THEN 'MEDIUM'
                        ELSE 'LOW'
                    END::VARCHAR,
                    v_factors;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("get_user_segment", """
            CREATE OR REPLACE FUNCTION get_user_segment(user_id_param INTEGER)
            RETURNS TABLE(
                segment VARCHAR,
                recency_days INTEGER,
                frequency INTEGER,
                monetary NUMERIC,
                rfm_score INTEGER
            ) AS $$
            DECLARE
                v_recency INTEGER;
                v_frequency INTEGER;
                v_monetary NUMERIC;
                v_r_score INTEGER;
                v_f_score INTEGER;
                v_m_score INTEGER;
                v_segment VARCHAR;
            BEGIN
                -- Validate input
                IF user_id_param IS NULL OR user_id_param <= 0 THEN
                    RETURN;
                END IF;

                SELECT
                    COALESCE(
                        EXTRACT(DAY FROM NOW() - MAX(created_at))::INTEGER,
                        999
                    ),
                    COUNT(*)::INTEGER,
                    COALESCE(SUM(paid_amount), 0)
                INTO v_recency, v_frequency, v_monetary
                FROM store_order
                WHERE user_id = user_id_param AND paid = true;

                -- RFM Scoring (1-5 scale)
                v_r_score := CASE
                    WHEN v_recency < 7 THEN 5
                    WHEN v_recency < 30 THEN 4
                    WHEN v_recency < 90 THEN 3
                    WHEN v_recency < 180 THEN 2
                    ELSE 1
                END;

                v_f_score := CASE
                    WHEN v_frequency > 10 THEN 5
                    WHEN v_frequency > 5 THEN 4
                    WHEN v_frequency > 3 THEN 3
                    WHEN v_frequency > 1 THEN 2
                    ELSE 1
                END;

                v_m_score := CASE
                    WHEN v_monetary > 50000 THEN 5
                    WHEN v_monetary > 20000 THEN 4
                    WHEN v_monetary > 10000 THEN 3
                    WHEN v_monetary > 5000 THEN 2
                    ELSE 1
                END;

                v_segment := CASE
                    WHEN v_r_score >= 4 AND v_f_score >= 4 THEN 'Champions'
                    WHEN v_r_score >= 4 AND v_f_score >= 2 THEN 'Loyal Customers'
                    WHEN v_r_score >= 3 AND v_f_score >= 3 THEN 'Potential Loyalists'
                    WHEN v_r_score >= 4 AND v_f_score = 1 THEN 'New Customers'
                    WHEN v_r_score >= 3 AND v_f_score <= 2 THEN 'Promising'
                    WHEN v_r_score = 2 AND v_f_score >= 3 THEN 'At Risk'
                    WHEN v_r_score <= 2 AND v_f_score >= 4 THEN 'Cant Lose Them'
                    WHEN v_r_score <= 2 AND v_f_score <= 2 THEN 'Hibernating'
                    ELSE 'Need Attention'
                END;

                RETURN QUERY SELECT
                    v_segment,
                    v_recency,
                    v_frequency,
                    v_monetary,
                    (v_r_score + v_f_score + v_m_score);
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("get_frequently_bought_together", """
            CREATE OR REPLACE FUNCTION get_frequently_bought_together(
                product_id_param INTEGER,
                limit_count INTEGER DEFAULT 5
            )
            RETURNS TABLE(
                related_product_id INTEGER,
                product_name VARCHAR,
                co_purchase_count BIGINT,
                affinity_score NUMERIC
            ) AS $$
            DECLARE
                v_total_orders BIGINT;
            BEGIN
                -- Validate input
                IF product_id_param IS NULL OR product_id_param <= 0 THEN
                    RETURN;
                END IF;

                -- Get total orders containing this product
                SELECT COUNT(DISTINCT order_id) INTO v_total_orders
                FROM store_orderitem
                WHERE product_id = product_id_param;

                IF v_total_orders = 0 THEN
                    RETURN;
                END IF;

                RETURN QUERY
                SELECT
                    oi2.product_id::INTEGER,
                    p.name::VARCHAR,
                    COUNT(*)::BIGINT as co_purchases,
                    ROUND(
                        (COUNT(*)::NUMERIC / v_total_orders * 100)::NUMERIC,
                        2
                    ) as affinity
                FROM store_orderitem oi1
                JOIN store_orderitem oi2 ON oi1.order_id = oi2.order_id
                    AND oi1.product_id != oi2.product_id
                JOIN store_product p ON oi2.product_id = p.id
                WHERE oi1.product_id = product_id_param
                AND p.is_active = true
                GROUP BY oi2.product_id, p.name
                ORDER BY co_purchases DESC
                LIMIT limit_count;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("suggest_optimal_price", """
            CREATE OR REPLACE FUNCTION suggest_optimal_price(product_id_param INTEGER)
            RETURNS TABLE(
                current_price NUMERIC,
                suggested_price NUMERIC,
                price_elasticity VARCHAR,
                recommendation TEXT
            ) AS $$
            DECLARE
                v_current NUMERIC;
                v_avg_category NUMERIC;
                v_sales_velocity NUMERIC;
                v_suggested NUMERIC;
                v_elasticity VARCHAR;
                v_recommendation TEXT;
            BEGIN
                -- Validate input
                IF product_id_param IS NULL OR product_id_param <= 0 THEN
                    RETURN;
                END IF;

                -- Get current price
                SELECT p.price INTO v_current
                FROM store_product p
                WHERE p.id = product_id_param;

                IF v_current IS NULL THEN
                    RETURN;
                END IF;

                -- Get category average
                SELECT AVG(p2.price) INTO v_avg_category
                FROM store_product p2
                WHERE p2.category_id = (
                    SELECT category_id FROM store_product WHERE id = product_id_param
                );

                -- Calculate sales velocity (orders per day)
                SELECT COUNT(*)::NUMERIC / GREATEST(
                    EXTRACT(DAY FROM NOW() - MIN(o.created_at)), 1
                )
                INTO v_sales_velocity
                FROM store_orderitem oi
                JOIN store_order o ON oi.order_id = o.id
                WHERE oi.product_id = product_id_param
                AND o.created_at > NOW() - INTERVAL '90 days';

                -- Price suggestion logic
                IF v_sales_velocity > 1 THEN
                    v_suggested := v_current * 1.05;
                    v_elasticity := 'Inelastic';
                    v_recommendation := 'Strong demand - consider price increase';
                ELSIF v_sales_velocity < 0.1 THEN
                    v_suggested := v_current * 0.90;
                    v_elasticity := 'Elastic';
                    v_recommendation := 'Low demand - consider discount';
                ELSE
                    v_suggested := v_current;
                    v_elasticity := 'Unit Elastic';
                    v_recommendation := 'Optimal pricing - maintain current price';
                END IF;

                RETURN QUERY SELECT
                    v_current,
                    ROUND(v_suggested, 2),
                    v_elasticity,
                    v_recommendation;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("predict_churn_risk", """
            CREATE OR REPLACE FUNCTION predict_churn_risk(user_id_param INTEGER)
            RETURNS TABLE(
                churn_score INTEGER,
                risk_level VARCHAR,
                days_since_last_order INTEGER,
                predicted_next_order_days INTEGER,
                intervention_needed BOOLEAN
            ) AS $$
            DECLARE
                v_days_since INTEGER;
                v_avg_gap INTEGER;
                v_score INTEGER;
                v_predicted INTEGER;
            BEGIN
                -- Validate input
                IF user_id_param IS NULL OR user_id_param <= 0 THEN
                    RETURN;
                END IF;

                -- Calculate days since last order and average gap between orders
                WITH order_gaps AS (
                    SELECT
                        created_at,
                        LAG(created_at) OVER (ORDER BY created_at) as prev_order
                    FROM store_order
                    WHERE user_id = user_id_param AND paid = true
                )
                SELECT
                    COALESCE(
                        EXTRACT(DAY FROM NOW() - MAX(created_at))::INTEGER,
                        999
                    ),
                    COALESCE(
                        AVG(EXTRACT(DAY FROM created_at - prev_order))::INTEGER,
                        30
                    )
                INTO v_days_since, v_avg_gap
                FROM order_gaps;

                v_predicted := GREATEST(v_avg_gap, 7);

                v_score := CASE
                    WHEN v_days_since > v_avg_gap * 3 THEN 90
                    WHEN v_days_since > v_avg_gap * 2 THEN 70
                    WHEN v_days_since > v_avg_gap * 1.5 THEN 50
                    WHEN v_days_since > v_avg_gap THEN 30
                    ELSE 10
                END;

                RETURN QUERY SELECT
                    v_score,
                    CASE
                        WHEN v_score >= 70 THEN 'HIGH'
                        WHEN v_score >= 50 THEN 'MEDIUM'
                        ELSE 'LOW'
                    END::VARCHAR,
                    v_days_since,
                    v_predicted,
                    v_score >= 50;
            END;
            $$ LANGUAGE plpgsql;
        """),
    ]


def get_ai_triggers() -> List[Tuple[str, str]]:
    """
    Get list of AI trigger definitions.

    Returns:
        List of tuples containing (trigger_name, sql_definition)
    """
    return [
        ("update_trending_score_function", """
            CREATE OR REPLACE FUNCTION update_trending_score()
            RETURNS TRIGGER AS $$
            BEGIN
                UPDATE store_product
                SET trending_score = COALESCE(trending_score, 0) + 5
                WHERE id = NEW.product_id;
                RETURN NEW;
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Error updating trending score: %', SQLERRM;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("trg_update_trending", """
            DROP TRIGGER IF EXISTS trg_update_trending ON store_orderitem;
            CREATE TRIGGER trg_update_trending
            AFTER INSERT ON store_orderitem
            FOR EACH ROW EXECUTE FUNCTION update_trending_score();
        """),

        ("increment_view_count_function", """
            CREATE OR REPLACE FUNCTION increment_view_count()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.event_type = 'product_view' AND NEW.product_id IS NOT NULL THEN
                    UPDATE store_product
                    SET view_count = COALESCE(view_count, 0) + 1
                    WHERE id = NEW.product_id;
                END IF;
                RETURN NEW;
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Error incrementing view count: %', SQLERRM;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("trg_increment_views", """
            DROP TRIGGER IF EXISTS trg_increment_views ON store_analyticsevent;
            CREATE TRIGGER trg_increment_views
            AFTER INSERT ON store_analyticsevent
            FOR EACH ROW EXECUTE FUNCTION increment_view_count();
        """),

        ("check_low_stock_function", """
            CREATE OR REPLACE FUNCTION check_low_stock()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.stock_quantity < 10
                   AND (OLD IS NULL OR NEW.stock_quantity != OLD.stock_quantity) THEN
                    BEGIN
                        INSERT INTO store_notification (
                            user_id, title, message, notification_type, is_read, created_at
                        )
                        SELECT
                            u.id,
                            'Low Stock Alert',
                            'Product ' || NEW.name || ' is running low (' ||
                            NEW.stock_quantity || ' left)',
                            'warning',
                            false,
                            NOW()
                        FROM auth_user u
                        WHERE u.is_staff = true
                        LIMIT 5;
                    EXCEPTION WHEN OTHERS THEN
                        RAISE NOTICE 'Error creating low stock notification: %', SQLERRM;
                    END;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("trg_low_stock_alert", """
            DROP TRIGGER IF EXISTS trg_low_stock_alert ON store_product;
            CREATE TRIGGER trg_low_stock_alert
            AFTER UPDATE ON store_product
            FOR EACH ROW EXECUTE FUNCTION check_low_stock();
        """),

        ("update_vendor_rating_function", """
            CREATE OR REPLACE FUNCTION update_vendor_rating()
            RETURNS TRIGGER AS $$
            DECLARE
                v_vendor_id INTEGER;
                v_avg_rating NUMERIC;
            BEGIN
                SELECT p.vendor_id INTO v_vendor_id
                FROM store_product p
                WHERE p.id = NEW.product_id;

                IF v_vendor_id IS NOT NULL THEN
                    SELECT AVG(r.rating) INTO v_avg_rating
                    FROM store_review r
                    JOIN store_product p ON r.product_id = p.id
                    WHERE p.vendor_id = v_vendor_id;

                    UPDATE store_vendor
                    SET rating = ROUND(COALESCE(v_avg_rating, 0), 2)
                    WHERE id = v_vendor_id;
                END IF;
                RETURN NEW;
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Error updating vendor rating: %', SQLERRM;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("trg_update_vendor_rating", """
            DROP TRIGGER IF EXISTS trg_update_vendor_rating ON store_review;
            CREATE TRIGGER trg_update_vendor_rating
            AFTER INSERT OR UPDATE ON store_review
            FOR EACH ROW EXECUTE FUNCTION update_vendor_rating();
        """),
    ]


def get_ai_views() -> List[Tuple[str, str]]:
    """
    Get list of AI view definitions.

    Returns:
        List of tuples containing (view_name, sql_definition)
    """
    return [
        ("ai_dashboard_metrics", """
            CREATE OR REPLACE VIEW ai_dashboard_metrics AS
            SELECT
                (SELECT COUNT(*) FROM store_order
                 WHERE created_at > NOW() - INTERVAL '24 hours') as orders_today,
                (SELECT COALESCE(SUM(paid_amount), 0) FROM store_order
                 WHERE paid = true AND created_at > NOW() - INTERVAL '24 hours') as revenue_today,
                (SELECT COUNT(*) FROM auth_user
                 WHERE date_joined > NOW() - INTERVAL '24 hours') as new_users_today,
                (SELECT COUNT(*) FROM store_product
                 WHERE stock_quantity < 10 AND is_active = true) as low_stock_products,
                (SELECT COALESCE(AVG(paid_amount), 0) FROM store_order
                 WHERE paid = true) as avg_order_value,
                (SELECT COUNT(*) FROM store_review
                 WHERE created_at > NOW() - INTERVAL '7 days') as reviews_this_week;
        """),

        ("ai_product_performance", """
            CREATE OR REPLACE VIEW ai_product_performance AS
            SELECT
                p.id,
                p.name,
                p.price,
                COALESCE(p.view_count, 0) as views,
                (SELECT COUNT(*) FROM store_orderitem WHERE product_id = p.id) as orders,
                COALESCE((SELECT AVG(rating) FROM store_review WHERE product_id = p.id), 0) as avg_rating,
                ROUND((
                    (COALESCE(p.view_count, 0)::NUMERIC / 100 * 0.2) +
                    ((SELECT COUNT(*) FROM store_orderitem WHERE product_id = p.id)::NUMERIC * 0.5) +
                    (COALESCE((SELECT AVG(rating) FROM store_review WHERE product_id = p.id), 3) * 10) +
                    (COALESCE(p.trending_score, 0) * 0.3)
                ), 2) as performance_score,
                CASE
                    WHEN (SELECT COUNT(*) FROM store_orderitem WHERE product_id = p.id) > 20
                        THEN 'Top Performer'
                    WHEN (SELECT COUNT(*) FROM store_orderitem WHERE product_id = p.id) > 10
                        THEN 'Good'
                    WHEN (SELECT COUNT(*) FROM store_orderitem WHERE product_id = p.id) > 5
                        THEN 'Average'
                    ELSE 'Needs Attention'
                END as performance_tier
            FROM store_product p
            WHERE p.is_active = true
            ORDER BY performance_score DESC;
        """),

        ("ai_user_insights", """
            CREATE OR REPLACE VIEW ai_user_insights AS
            SELECT
                u.id,
                u.username,
                u.email,
                u.date_joined,
                (SELECT COUNT(*) FROM store_order
                 WHERE user_id = u.id AND paid = true) as total_orders,
                (SELECT COALESCE(SUM(paid_amount), 0) FROM store_order
                 WHERE user_id = u.id AND paid = true) as total_spent,
                (SELECT MAX(created_at) FROM store_order WHERE user_id = u.id) as last_order_date,
                EXTRACT(DAY FROM NOW() - (
                    SELECT MAX(created_at) FROM store_order WHERE user_id = u.id
                ))::INTEGER as days_since_order,
                CASE
                    WHEN (SELECT COUNT(*) FROM store_order
                          WHERE user_id = u.id AND paid = true) > 5
                         AND (SELECT MAX(created_at) FROM store_order
                              WHERE user_id = u.id) > NOW() - INTERVAL '30 days'
                        THEN 'Loyal'
                    WHEN (SELECT MAX(created_at) FROM store_order
                          WHERE user_id = u.id) < NOW() - INTERVAL '90 days'
                        THEN 'Churned'
                    WHEN (SELECT COUNT(*) FROM store_order WHERE user_id = u.id) = 0
                        THEN 'Prospect'
                    ELSE 'Active'
                END as customer_status
            FROM auth_user u
            WHERE u.is_superuser = false;
        """),

        ("ai_sales_forecast", """
            CREATE OR REPLACE VIEW ai_sales_forecast AS
            WITH daily_sales AS (
                SELECT
                    DATE(created_at) as sale_date,
                    COUNT(*) as order_count,
                    COALESCE(SUM(paid_amount), 0) as revenue
                FROM store_order
                WHERE paid = true AND created_at > NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at)
            )
            SELECT
                sale_date,
                order_count,
                revenue,
                AVG(revenue) OVER (
                    ORDER BY sale_date
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ) as ma_7_day,
                AVG(revenue) OVER () as daily_average,
                CASE
                    WHEN revenue > AVG(revenue) OVER () * 1.2 THEN 'Above Average'
                    WHEN revenue < AVG(revenue) OVER () * 0.8 THEN 'Below Average'
                    ELSE 'Normal'
                END as performance
            FROM daily_sales
            ORDER BY sale_date DESC;
        """),

        ("ai_inventory_intelligence", """
            CREATE OR REPLACE VIEW ai_inventory_intelligence AS
            SELECT
                p.id,
                p.name,
                p.stock_quantity,
                (SELECT COUNT(*) FROM store_orderitem oi
                 JOIN store_order o ON oi.order_id = o.id
                 WHERE oi.product_id = p.id
                 AND o.created_at > NOW() - INTERVAL '7 days') as sales_last_week,
                CASE
                    WHEN p.stock_quantity = 0 THEN 'Out of Stock'
                    WHEN p.stock_quantity < 10 THEN 'Critical'
                    WHEN p.stock_quantity < 30 THEN 'Low'
                    WHEN p.stock_quantity < 100 THEN 'Normal'
                    ELSE 'Overstocked'
                END as stock_status,
                ROUND(
                    p.stock_quantity::NUMERIC / GREATEST(
                        (SELECT COUNT(*) FROM store_orderitem oi
                         JOIN store_order o ON oi.order_id = o.id
                         WHERE oi.product_id = p.id
                         AND o.created_at > NOW() - INTERVAL '30 days'
                        )::NUMERIC / 30,
                        0.1
                    ),
                    0
                ) as days_of_stock_remaining
            FROM store_product p
            WHERE p.is_active = true
            ORDER BY stock_quantity ASC;
        """),
    ]


def get_ai_procedures() -> List[Tuple[str, str]]:
    """
    Get list of AI procedure definitions.

    Returns:
        List of tuples containing (procedure_name, sql_definition)
    """
    return [
        ("decay_trending_scores", """
            CREATE OR REPLACE PROCEDURE decay_trending_scores()
            LANGUAGE plpgsql
            AS $$
            BEGIN
                UPDATE store_product
                SET trending_score = GREATEST(COALESCE(trending_score, 0) * 0.95, 0)
                WHERE trending_score IS NOT NULL AND trending_score > 0;

                RAISE NOTICE 'Trending scores decayed successfully';
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Error decaying trending scores: %', SQLERRM;
            END;
            $$;
        """),

        ("update_all_vendor_analytics", """
            CREATE OR REPLACE PROCEDURE update_all_vendor_analytics()
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_vendor RECORD;
                v_count INTEGER := 0;
            BEGIN
                FOR v_vendor IN SELECT id FROM store_vendor LOOP
                    BEGIN
                        INSERT INTO store_vendoranalytics (
                            vendor_id, date, total_products, total_orders,
                            total_revenue, average_rating
                        )
                        SELECT
                            v_vendor.id,
                            CURRENT_DATE,
                            (SELECT COUNT(*) FROM store_product WHERE vendor_id = v_vendor.id),
                            (SELECT COUNT(*) FROM store_orderitem oi
                             JOIN store_product p ON oi.product_id = p.id
                             WHERE p.vendor_id = v_vendor.id),
                            COALESCE((
                                SELECT SUM(oi.price * oi.quantity)
                                FROM store_orderitem oi
                                JOIN store_product p ON oi.product_id = p.id
                                WHERE p.vendor_id = v_vendor.id
                            ), 0),
                            COALESCE((
                                SELECT AVG(r.rating)
                                FROM store_review r
                                JOIN store_product p ON r.product_id = p.id
                                WHERE p.vendor_id = v_vendor.id
                            ), 0)
                        ON CONFLICT (vendor_id, date) DO UPDATE
                        SET total_orders = EXCLUDED.total_orders,
                            total_revenue = EXCLUDED.total_revenue,
                            average_rating = EXCLUDED.average_rating;

                        v_count := v_count + 1;
                    EXCEPTION WHEN OTHERS THEN
                        RAISE NOTICE 'Error updating vendor %: %', v_vendor.id, SQLERRM;
                    END;
                END LOOP;

                RAISE NOTICE 'Updated analytics for % vendors', v_count;
            END;
            $$;
        """),

        ("cleanup_old_analytics", """
            CREATE OR REPLACE PROCEDURE cleanup_old_analytics()
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_deleted_events INTEGER;
                v_deleted_audit INTEGER;
            BEGIN
                -- Delete old analytics events (older than 90 days)
                DELETE FROM store_analyticsevent
                WHERE created_at < NOW() - INTERVAL '90 days';
                GET DIAGNOSTICS v_deleted_events = ROW_COUNT;

                -- Delete old audit logs (older than 180 days)
                DELETE FROM store_auditlog
                WHERE created_at < NOW() - INTERVAL '180 days';
                GET DIAGNOSTICS v_deleted_audit = ROW_COUNT;

                RAISE NOTICE 'Cleaned up % analytics events and % audit logs',
                    v_deleted_events, v_deleted_audit;
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Error during cleanup: %', SQLERRM;
            END;
            $$;
        """),
    ]


def create_ai_functions(manager: AIFunctionManager) -> None:
    """Create all AI functions."""
    logger.info("Creating AI Functions...")
    for name, sql in get_ai_functions():
        manager.execute_sql(f"Function: {name}", sql)


def create_ai_triggers(manager: AIFunctionManager) -> None:
    """Create all AI triggers."""
    logger.info("Creating AI Triggers...")
    for name, sql in get_ai_triggers():
        manager.execute_sql(f"Trigger: {name}", sql)


def create_ai_views(manager: AIFunctionManager) -> None:
    """Create all AI views."""
    logger.info("Creating AI Views...")
    for name, sql in get_ai_views():
        manager.execute_sql(f"View: {name}", sql)


def create_ai_procedures(manager: AIFunctionManager) -> None:
    """Create all AI procedures."""
    logger.info("Creating Scheduled Procedures...")
    for name, sql in get_ai_procedures():
        manager.execute_sql(f"Procedure: {name}", sql)


def test_ai_functions() -> None:
    """Test the AI functions to verify they work."""
    logger.info("Testing AI Functions...")

    tests = [
        ("Smart Recommendations", "SELECT * FROM get_smart_recommendations(2, 5);"),
        ("Customer LTV", "SELECT * FROM calculate_customer_lifetime_value(2);"),
        ("User Segment", "SELECT * FROM get_user_segment(2);"),
        ("Churn Prediction", "SELECT * FROM predict_churn_risk(2);"),
    ]

    with connection.cursor() as cursor:
        for name, query in tests:
            try:
                cursor.execute(query)
                result = cursor.fetchall()
                logger.info("  %s: Working (%d results)", name, len(result))
            except (OperationalError, ProgrammingError) as e:
                logger.warning("  %s: %s", name, str(e)[:50])


def print_summary(manager: AIFunctionManager) -> None:
    """Print execution summary."""
    success, failure = manager.get_summary()

    print("\n" + "=" * 60)
    print("PostgreSQL AI Features - Execution Summary")
    print("=" * 60)
    print(f"\n  Total Operations: {success + failure}")
    print(f"  Successful: {success}")
    print(f"  Failed: {failure}")

    if failure > 0:
        print("\n  Failed Operations:")
        for result in manager.results:
            if not result.success:
                print(f"    - {result.name}: {result.error_message}")

    print("\n" + "=" * 60)
    print("AI FEATURES SUMMARY:")
    print("  FUNCTIONS (7):")
    print("    - get_smart_recommendations()")
    print("    - calculate_customer_lifetime_value()")
    print("    - calculate_fraud_risk_score()")
    print("    - get_user_segment()")
    print("    - get_frequently_bought_together()")
    print("    - suggest_optimal_price()")
    print("    - predict_churn_risk()")
    print()
    print("  TRIGGERS (4):")
    print("    - Auto-update trending score on order")
    print("    - Auto-increment view count")
    print("    - Low stock alert notification")
    print("    - Auto-calculate vendor rating")
    print()
    print("  AI VIEWS (5):")
    print("    - ai_dashboard_metrics")
    print("    - ai_product_performance")
    print("    - ai_user_insights")
    print("    - ai_sales_forecast")
    print("    - ai_inventory_intelligence")
    print()
    print("  PROCEDURES (3):")
    print("    - decay_trending_scores()")
    print("    - update_all_vendor_analytics()")
    print("    - cleanup_old_analytics()")


def main() -> int:
    """
    Main function to add AI features.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("=" * 60)
    print("VIBE E-Commerce - PostgreSQL AI Features")
    print("=" * 60)

    # Validate database configuration
    validator = DatabaseValidator()

    if not validator.is_postgresql():
        logger.error(
            "This script requires PostgreSQL. Current database engine is not PostgreSQL."
        )
        print("\nError: PostgreSQL is required for AI features.")
        print("Please configure PostgreSQL in your settings.")
        return 1

    if not validator.check_connection():
        logger.error("Could not connect to the database.")
        return 1

    tables_ok, missing_tables = validator.check_required_tables()
    if not tables_ok:
        logger.warning("Missing tables: %s", missing_tables)
        print(f"\nWarning: Some tables are missing: {missing_tables}")
        print("Some features may not work correctly.")

    # Create AI features
    manager = AIFunctionManager()

    create_ai_functions(manager)
    create_ai_triggers(manager)
    create_ai_views(manager)
    create_ai_procedures(manager)

    # Test functions
    test_ai_functions()

    # Print summary
    print_summary(manager)

    success, failure = manager.get_summary()
    return 0 if failure == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
