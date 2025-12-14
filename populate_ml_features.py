"""
Machine Learning Features for VIBE E-Commerce PostgreSQL Database.

This module adds ML-powered PostgreSQL functions, views, and tables for:
- Collaborative Filtering (User-Based Recommendations)
- Content-Based Filtering
- Demand Forecasting (Simple Linear Regression)
- Anomaly Detection for Orders
- Customer Clustering
- Review Sentiment Analysis
- Product Performance Prediction
- Dynamic Pricing Intelligence

Note:
    These features require PostgreSQL as the database backend.
    They will not work with SQLite.

Usage:
    python populate_ml_features.py

Author: VIBE E-Commerce Team
"""
import logging
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
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


class SQLObjectType(Enum):
    """Types of SQL objects."""
    FUNCTION = "Function"
    VIEW = "View"
    TABLE = "Table"


@dataclass
class SQLExecutionResult:
    """Result of SQL execution."""
    success: bool
    name: str
    object_type: SQLObjectType
    error_message: Optional[str] = None


@dataclass
class ExecutionStats:
    """Statistics for ML feature creation."""
    functions_created: int = 0
    functions_failed: int = 0
    views_created: int = 0
    views_failed: int = 0
    tables_created: int = 0
    tables_failed: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    errors: List[str] = field(default_factory=list)

    @property
    def total_created(self) -> int:
        """Total objects created."""
        return self.functions_created + self.views_created + self.tables_created

    @property
    def total_failed(self) -> int:
        """Total objects failed."""
        return self.functions_failed + self.views_failed + self.tables_failed


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
    def get_db_version() -> Optional[str]:
        """Get PostgreSQL version."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                return cursor.fetchone()[0]
        except (OperationalError, ProgrammingError):
            return None


class MLFeatureManager:
    """Manages ML PostgreSQL features."""

    def __init__(self):
        """Initialize the feature manager."""
        self.stats = ExecutionStats()
        self.results: List[SQLExecutionResult] = []

    def execute_sql(
        self,
        name: str,
        sql: str,
        object_type: SQLObjectType
    ) -> SQLExecutionResult:
        """
        Execute SQL statement safely.

        Args:
            name: Identifier for the SQL statement
            sql: SQL statement to execute
            object_type: Type of SQL object being created

        Returns:
            SQLExecutionResult with success status and error if any
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)

            result = SQLExecutionResult(
                success=True, name=name, object_type=object_type
            )
            logger.info("Created %s: %s", object_type.value, name)

            # Update stats
            if object_type == SQLObjectType.FUNCTION:
                self.stats.functions_created += 1
            elif object_type == SQLObjectType.VIEW:
                self.stats.views_created += 1
            elif object_type == SQLObjectType.TABLE:
                self.stats.tables_created += 1

        except (OperationalError, ProgrammingError) as e:
            error_msg = str(e)[:100]
            result = SQLExecutionResult(
                success=False, name=name,
                object_type=object_type, error_message=error_msg
            )
            logger.warning("Failed to create %s %s: %s", object_type.value, name, error_msg)

            # Update stats
            if object_type == SQLObjectType.FUNCTION:
                self.stats.functions_failed += 1
            elif object_type == SQLObjectType.VIEW:
                self.stats.views_failed += 1
            elif object_type == SQLObjectType.TABLE:
                self.stats.tables_failed += 1

            self.stats.errors.append(f"{object_type.value} {name}: {error_msg}")

        self.results.append(result)
        return result

    def test_function(self, name: str, query: str) -> bool:
        """
        Test an ML function.

        Args:
            name: Name of the function
            query: Test query to execute

        Returns:
            True if test passed, False otherwise
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                logger.info("  %s: Working (%d results)", name, len(result))
                self.stats.tests_passed += 1
                return True
        except (OperationalError, ProgrammingError) as e:
            logger.warning("  %s: Failed - %s", name, str(e)[:50])
            self.stats.tests_failed += 1
            return False


def get_ml_functions() -> List[Tuple[str, str]]:
    """
    Get list of ML function definitions.

    Returns:
        List of tuples containing (function_name, sql_definition)
    """
    return [
        ("ml_collaborative_recommendations", """
            CREATE OR REPLACE FUNCTION ml_collaborative_recommendations(
                user_id_param INTEGER,
                limit_count INTEGER DEFAULT 10
            )
            RETURNS TABLE(
                product_id INTEGER,
                product_name VARCHAR,
                predicted_rating NUMERIC,
                similar_users_bought INTEGER,
                confidence_score NUMERIC
            ) AS $$
            BEGIN
                -- Validate input parameters
                IF user_id_param IS NULL OR user_id_param <= 0 THEN
                    RAISE NOTICE 'Invalid user_id_param: %', user_id_param;
                    RETURN;
                END IF;

                limit_count := COALESCE(limit_count, 10);

                RETURN QUERY
                WITH user_purchases AS (
                    -- Products purchased by target user
                    SELECT DISTINCT oi.product_id
                    FROM store_orderitem oi
                    JOIN store_order o ON oi.order_id = o.id
                    WHERE o.user_id = user_id_param AND o.paid = true
                ),
                similar_users AS (
                    -- Find users with similar purchase patterns
                    SELECT
                        o.user_id,
                        COUNT(DISTINCT oi.product_id) as common_products,
                        -- Jaccard similarity approximation
                        COUNT(DISTINCT oi.product_id)::NUMERIC /
                        GREATEST(
                            (SELECT COUNT(*) FROM user_purchases) +
                            (SELECT COUNT(DISTINCT oi2.product_id)
                             FROM store_orderitem oi2
                             JOIN store_order o2 ON oi2.order_id = o2.id
                             WHERE o2.user_id = o.user_id AND o2.paid = true),
                            1
                        ) as similarity
                    FROM store_orderitem oi
                    JOIN store_order o ON oi.order_id = o.id
                    WHERE oi.product_id IN (SELECT product_id FROM user_purchases)
                    AND o.user_id != user_id_param
                    AND o.paid = true
                    GROUP BY o.user_id
                    HAVING COUNT(DISTINCT oi.product_id) >= 2
                    ORDER BY similarity DESC
                    LIMIT 20
                ),
                recommended_products AS (
                    SELECT
                        oi.product_id,
                        COUNT(DISTINCT o.user_id) as buy_count,
                        AVG(su.similarity) as avg_similarity
                    FROM store_orderitem oi
                    JOIN store_order o ON oi.order_id = o.id
                    JOIN similar_users su ON o.user_id = su.user_id
                    WHERE oi.product_id NOT IN (SELECT product_id FROM user_purchases)
                    GROUP BY oi.product_id
                )
                SELECT
                    p.id::INTEGER,
                    p.name::VARCHAR,
                    ROUND((COALESCE(AVG(r.rating), 3.5) * rp.avg_similarity)::NUMERIC, 2),
                    rp.buy_count::INTEGER,
                    ROUND((rp.avg_similarity * 100)::NUMERIC, 2)
                FROM recommended_products rp
                JOIN store_product p ON rp.product_id = p.id
                LEFT JOIN store_review r ON p.id = r.product_id
                WHERE p.is_active = true
                GROUP BY p.id, p.name, rp.buy_count, rp.avg_similarity
                ORDER BY (COALESCE(AVG(r.rating), 3.5) * rp.avg_similarity) DESC, buy_count DESC
                LIMIT limit_count;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("ml_content_based_recommendations", """
            CREATE OR REPLACE FUNCTION ml_content_based_recommendations(
                product_id_param INTEGER,
                limit_count INTEGER DEFAULT 10
            )
            RETURNS TABLE(
                recommended_product_id INTEGER,
                product_name VARCHAR,
                similarity_score NUMERIC,
                match_reason VARCHAR
            ) AS $$
            DECLARE
                v_category_id INTEGER;
                v_vendor_id INTEGER;
                v_price NUMERIC;
            BEGIN
                -- Validate input
                IF product_id_param IS NULL OR product_id_param <= 0 THEN
                    RETURN;
                END IF;

                SELECT category_id, vendor_id, price
                INTO v_category_id, v_vendor_id, v_price
                FROM store_product WHERE id = product_id_param;

                IF v_category_id IS NULL THEN
                    RETURN;
                END IF;

                RETURN QUERY
                SELECT
                    p.id::INTEGER,
                    p.name::VARCHAR,
                    ROUND((
                        CASE WHEN p.category_id = v_category_id THEN 40 ELSE 0 END +
                        CASE WHEN p.vendor_id = v_vendor_id THEN 30 ELSE 0 END +
                        CASE WHEN v_price > 0 AND ABS(p.price - v_price) < v_price * 0.2 THEN 20
                             WHEN v_price > 0 AND ABS(p.price - v_price) < v_price * 0.5 THEN 10
                             ELSE 0
                        END +
                        COALESCE((SELECT AVG(rating) FROM store_review WHERE product_id = p.id), 3) * 2
                    )::NUMERIC, 2) as similarity,
                    CASE
                        WHEN p.category_id = v_category_id AND p.vendor_id = v_vendor_id
                            THEN 'Same Category & Vendor'
                        WHEN p.category_id = v_category_id THEN 'Same Category'
                        WHEN p.vendor_id = v_vendor_id THEN 'Same Vendor'
                        ELSE 'Similar Price Range'
                    END::VARCHAR as reason
                FROM store_product p
                WHERE p.id != product_id_param
                AND p.is_active = true
                AND (p.category_id = v_category_id
                     OR p.vendor_id = v_vendor_id
                     OR (v_price > 0 AND ABS(p.price - v_price) < v_price * 0.3))
                ORDER BY similarity DESC
                LIMIT limit_count;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("ml_demand_forecast", """
            CREATE OR REPLACE FUNCTION ml_demand_forecast(
                product_id_param INTEGER,
                forecast_days INTEGER DEFAULT 7
            )
            RETURNS TABLE(
                forecast_date DATE,
                predicted_demand NUMERIC,
                confidence_interval_low NUMERIC,
                confidence_interval_high NUMERIC,
                trend VARCHAR
            ) AS $$
            DECLARE
                v_avg_daily NUMERIC;
                v_stddev NUMERIC;
                v_trend NUMERIC;
                v_trend_label VARCHAR;
                i INTEGER;
            BEGIN
                -- Validate input
                IF product_id_param IS NULL OR product_id_param <= 0 THEN
                    RETURN;
                END IF;

                forecast_days := LEAST(COALESCE(forecast_days, 7), 30);

                -- Calculate average daily sales and trend
                WITH daily_sales AS (
                    SELECT
                        DATE(o.created_at) as sale_date,
                        COALESCE(SUM(oi.quantity), 0) as quantity
                    FROM store_orderitem oi
                    JOIN store_order o ON oi.order_id = o.id
                    WHERE oi.product_id = product_id_param
                    AND o.paid = true
                    AND o.created_at > NOW() - INTERVAL '30 days'
                    GROUP BY DATE(o.created_at)
                ),
                stats AS (
                    SELECT
                        COALESCE(AVG(quantity), 1) as avg_qty,
                        COALESCE(STDDEV(quantity), 0.5) as std_qty,
                        COALESCE(
                            (SELECT quantity FROM daily_sales ORDER BY sale_date DESC LIMIT 1) -
                            (SELECT quantity FROM daily_sales ORDER BY sale_date ASC LIMIT 1),
                            0
                        ) as trend_change
                    FROM daily_sales
                )
                SELECT
                    avg_qty,
                    std_qty,
                    COALESCE(trend_change / GREATEST(30, 1), 0)
                INTO v_avg_daily, v_stddev, v_trend
                FROM stats;

                v_trend_label := CASE
                    WHEN v_trend > 0.1 THEN 'Increasing'
                    WHEN v_trend < -0.1 THEN 'Decreasing'
                    ELSE 'Stable'
                END;

                FOR i IN 1..forecast_days LOOP
                    RETURN QUERY SELECT
                        (CURRENT_DATE + i)::DATE,
                        ROUND(GREATEST(v_avg_daily + (v_trend * i), 0), 2)::NUMERIC,
                        ROUND(GREATEST(v_avg_daily + (v_trend * i) - v_stddev, 0), 2)::NUMERIC,
                        ROUND(v_avg_daily + (v_trend * i) + v_stddev, 2)::NUMERIC,
                        v_trend_label::VARCHAR;
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("ml_detect_anomalies", """
            CREATE OR REPLACE FUNCTION ml_detect_anomalies()
            RETURNS TABLE(
                order_id INTEGER,
                anomaly_type VARCHAR,
                anomaly_score NUMERIC,
                details TEXT
            ) AS $$
            DECLARE
                v_avg_order NUMERIC;
                v_stddev_order NUMERIC;
                v_avg_items NUMERIC;
            BEGIN
                -- Calculate baseline statistics
                SELECT
                    COALESCE(AVG(paid_amount), 0),
                    COALESCE(STDDEV(paid_amount), 1)
                INTO v_avg_order, v_stddev_order
                FROM store_order WHERE paid = true;

                SELECT COALESCE(AVG(item_count), 1) INTO v_avg_items
                FROM (
                    SELECT order_id, COUNT(*) as item_count
                    FROM store_orderitem
                    GROUP BY order_id
                ) s;

                -- Ensure we have valid statistics
                v_avg_order := GREATEST(v_avg_order, 1);
                v_stddev_order := GREATEST(v_stddev_order, 1);
                v_avg_items := GREATEST(v_avg_items, 1);

                RETURN QUERY
                -- High value anomalies
                SELECT
                    o.id::INTEGER,
                    'High Value Order'::VARCHAR,
                    ROUND(((o.paid_amount - v_avg_order) / v_stddev_order * 100)::NUMERIC, 2),
                    ('Order value ' || o.paid_amount || ' is ' ||
                     ROUND((o.paid_amount / v_avg_order)::NUMERIC, 1) || 'x average')::TEXT
                FROM store_order o
                WHERE o.paid = true
                AND o.paid_amount > v_avg_order + (3 * v_stddev_order)

                UNION ALL

                -- Multiple orders in short time
                SELECT
                    o.id::INTEGER,
                    'Rapid Orders'::VARCHAR,
                    80::NUMERIC,
                    'Multiple orders within 1 hour'::TEXT
                FROM store_order o
                WHERE EXISTS (
                    SELECT 1 FROM store_order o2
                    WHERE o2.user_id = o.user_id
                    AND o2.id != o.id
                    AND ABS(EXTRACT(EPOCH FROM (o.created_at - o2.created_at))) < 3600
                )

                UNION ALL

                -- Unusual item count
                SELECT
                    oi.order_id::INTEGER,
                    'High Item Count'::VARCHAR,
                    70::NUMERIC,
                    ('Order has ' || COUNT(*) || ' items (avg: ' ||
                     ROUND(v_avg_items::NUMERIC, 1) || ')')::TEXT
                FROM store_orderitem oi
                GROUP BY oi.order_id
                HAVING COUNT(*) > v_avg_items * 3

                ORDER BY anomaly_score DESC
                LIMIT 50;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("ml_customer_clusters", """
            CREATE OR REPLACE FUNCTION ml_customer_clusters()
            RETURNS TABLE(
                user_id INTEGER,
                username VARCHAR,
                cluster_name VARCHAR,
                total_orders INTEGER,
                total_spent NUMERIC,
                avg_order_value NUMERIC,
                preferred_category VARCHAR
            ) AS $$
            BEGIN
                RETURN QUERY
                WITH user_stats AS (
                    SELECT
                        u.id,
                        u.username,
                        COUNT(o.id)::INTEGER as orders,
                        COALESCE(SUM(o.paid_amount), 0) as spent,
                        COALESCE(AVG(o.paid_amount), 0) as avg_order
                    FROM auth_user u
                    LEFT JOIN store_order o ON u.id = o.user_id AND o.paid = true
                    WHERE u.is_superuser = false
                    GROUP BY u.id, u.username
                ),
                user_categories AS (
                    SELECT
                        o.user_id,
                        c.name as category_name,
                        ROW_NUMBER() OVER (
                            PARTITION BY o.user_id ORDER BY COUNT(*) DESC
                        ) as rn
                    FROM store_orderitem oi
                    JOIN store_order o ON oi.order_id = o.id AND o.paid = true
                    JOIN store_product p ON oi.product_id = p.id
                    JOIN store_category c ON p.category_id = c.id
                    GROUP BY o.user_id, c.name
                )
                SELECT
                    us.id::INTEGER,
                    us.username::VARCHAR,
                    CASE
                        WHEN us.spent > 50000 AND us.orders > 10 THEN 'VIP Customer'
                        WHEN us.spent > 20000 AND us.orders > 5 THEN 'Premium Customer'
                        WHEN us.spent > 5000 AND us.orders > 2 THEN 'Regular Customer'
                        WHEN us.orders > 0 THEN 'New Customer'
                        ELSE 'Prospect'
                    END::VARCHAR as cluster,
                    us.orders,
                    ROUND(us.spent::NUMERIC, 2),
                    ROUND(us.avg_order::NUMERIC, 2),
                    COALESCE(uc.category_name, 'None')::VARCHAR
                FROM user_stats us
                LEFT JOIN user_categories uc ON us.id = uc.user_id AND uc.rn = 1
                ORDER BY us.spent DESC;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("ml_review_sentiment", """
            CREATE OR REPLACE FUNCTION ml_review_sentiment(review_text TEXT)
            RETURNS TABLE(
                sentiment_score NUMERIC,
                sentiment_label VARCHAR,
                positive_words INTEGER,
                negative_words INTEGER
            ) AS $$
            DECLARE
                v_text TEXT;
                v_positive INTEGER := 0;
                v_negative INTEGER := 0;
                v_score NUMERIC;
            BEGIN
                -- Handle NULL or empty input
                IF review_text IS NULL OR LENGTH(TRIM(review_text)) = 0 THEN
                    RETURN QUERY SELECT 50::NUMERIC, 'Neutral'::VARCHAR, 0, 0;
                    RETURN;
                END IF;

                v_text := LOWER(review_text);

                -- Count positive words
                v_positive := (
                    (CASE WHEN v_text LIKE '%excellent%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%great%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%best%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%good%' THEN 1 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%recommend%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%quality%' THEN 1 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%fast%' THEN 1 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%genuine%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%effective%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%satisfied%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%premium%' THEN 1 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%trusted%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%amazing%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%perfect%' THEN 2 ELSE 0 END)
                );

                -- Count negative words
                v_negative := (
                    (CASE WHEN v_text LIKE '%bad%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%poor%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%worst%' THEN 3 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%fake%' THEN 3 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%slow%' THEN 1 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%damaged%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%waste%' THEN 2 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%expensive%' THEN 1 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%not recommend%' THEN 3 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%terrible%' THEN 3 ELSE 0 END) +
                    (CASE WHEN v_text LIKE '%broken%' THEN 2 ELSE 0 END)
                );

                -- Calculate score (0 to 100)
                v_score := CASE
                    WHEN v_positive + v_negative = 0 THEN 50
                    ELSE ROUND((v_positive::NUMERIC / (v_positive + v_negative) * 100), 2)
                END;

                RETURN QUERY SELECT
                    v_score,
                    CASE
                        WHEN v_score >= 70 THEN 'Positive'
                        WHEN v_score <= 30 THEN 'Negative'
                        ELSE 'Neutral'
                    END::VARCHAR,
                    v_positive,
                    v_negative;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("ml_predict_product_performance", """
            CREATE OR REPLACE FUNCTION ml_predict_product_performance(
                product_id_param INTEGER
            )
            RETURNS TABLE(
                performance_score NUMERIC,
                performance_grade VARCHAR,
                sales_velocity NUMERIC,
                review_quality NUMERIC,
                stock_health VARCHAR,
                recommendation TEXT
            ) AS $$
            DECLARE
                v_sales NUMERIC;
                v_reviews NUMERIC;
                v_rating NUMERIC;
                v_stock INTEGER;
                v_score NUMERIC;
                v_rec TEXT;
            BEGIN
                -- Validate input
                IF product_id_param IS NULL OR product_id_param <= 0 THEN
                    RETURN;
                END IF;

                -- Sales velocity (orders per week)
                SELECT COUNT(*)::NUMERIC / GREATEST(
                    EXTRACT(DAY FROM NOW() - MIN(o.created_at)) / 7, 1
                )
                INTO v_sales
                FROM store_orderitem oi
                JOIN store_order o ON oi.order_id = o.id
                WHERE oi.product_id = product_id_param AND o.paid = true;

                -- Review metrics
                SELECT COUNT(*), COALESCE(AVG(rating), 3.5)
                INTO v_reviews, v_rating
                FROM store_review WHERE product_id = product_id_param;

                -- Stock
                SELECT COALESCE(stock_quantity, 0) INTO v_stock
                FROM store_product WHERE id = product_id_param;

                -- Calculate performance score
                v_score := COALESCE(v_sales, 0) * 20 +
                           COALESCE(v_reviews, 0) * 5 +
                           COALESCE(v_rating, 3.5) * 10;

                -- Recommendation
                v_rec := CASE
                    WHEN v_score > 80 THEN 'Top performer - consider increasing stock'
                    WHEN v_score > 50 THEN 'Good performance - maintain current strategy'
                    WHEN v_score > 20 THEN 'Average - consider promotional activities'
                    ELSE 'Needs attention - review pricing and visibility'
                END;

                RETURN QUERY SELECT
                    ROUND(v_score, 2),
                    CASE
                        WHEN v_score > 80 THEN 'A'
                        WHEN v_score > 60 THEN 'B'
                        WHEN v_score > 40 THEN 'C'
                        WHEN v_score > 20 THEN 'D'
                        ELSE 'F'
                    END::VARCHAR,
                    ROUND(COALESCE(v_sales, 0), 2),
                    ROUND(COALESCE(v_rating, 0), 2),
                    CASE
                        WHEN v_stock = 0 THEN 'Out of Stock'
                        WHEN v_stock < 10 THEN 'Critical'
                        WHEN v_stock < 50 THEN 'Low'
                        ELSE 'Healthy'
                    END::VARCHAR,
                    v_rec::TEXT;
            END;
            $$ LANGUAGE plpgsql;
        """),

        ("ml_dynamic_pricing_analysis", """
            CREATE OR REPLACE FUNCTION ml_dynamic_pricing_analysis(
                product_id_param INTEGER
            )
            RETURNS TABLE(
                current_price NUMERIC,
                market_position VARCHAR,
                competitor_avg NUMERIC,
                demand_level VARCHAR,
                price_recommendation TEXT
            ) AS $$
            DECLARE
                v_price NUMERIC;
                v_category_avg NUMERIC;
                v_sales_rate NUMERIC;
                v_position VARCHAR;
                v_demand VARCHAR;
            BEGIN
                -- Validate input
                IF product_id_param IS NULL OR product_id_param <= 0 THEN
                    RETURN;
                END IF;

                -- Get product price and category average
                SELECT p.price,
                       (SELECT AVG(price) FROM store_product
                        WHERE category_id = p.category_id AND is_active = true)
                INTO v_price, v_category_avg
                FROM store_product p WHERE p.id = product_id_param;

                IF v_price IS NULL THEN
                    RETURN;
                END IF;

                v_category_avg := COALESCE(v_category_avg, v_price);

                -- Calculate sales rate (orders per day over last 30 days)
                SELECT COUNT(*)::NUMERIC / 30
                INTO v_sales_rate
                FROM store_orderitem oi
                JOIN store_order o ON oi.order_id = o.id
                WHERE oi.product_id = product_id_param
                AND o.paid = true
                AND o.created_at > NOW() - INTERVAL '30 days';

                -- Determine market position
                v_position := CASE
                    WHEN v_price < v_category_avg * 0.8 THEN 'Budget'
                    WHEN v_price > v_category_avg * 1.2 THEN 'Premium'
                    ELSE 'Mid-Range'
                END;

                -- Determine demand level
                v_demand := CASE
                    WHEN v_sales_rate > 2 THEN 'High'
                    WHEN v_sales_rate > 0.5 THEN 'Medium'
                    ELSE 'Low'
                END;

                RETURN QUERY SELECT
                    v_price,
                    v_position,
                    ROUND(v_category_avg, 2),
                    v_demand,
                    CASE
                        WHEN v_demand = 'High' AND v_position = 'Budget'
                            THEN 'Strong demand at low price - good value proposition'
                        WHEN v_demand = 'High' AND v_position = 'Premium'
                            THEN 'Premium pricing working well'
                        WHEN v_demand = 'Low' AND v_position = 'Premium'
                            THEN 'Consider promotional pricing'
                        WHEN v_demand = 'Low' AND v_position = 'Budget'
                            THEN 'Low price not driving sales - review product visibility'
                        ELSE 'Current pricing is balanced'
                    END::TEXT;
            END;
            $$ LANGUAGE plpgsql;
        """),
    ]


def get_ml_views() -> List[Tuple[str, str]]:
    """
    Get list of ML view definitions.

    Returns:
        List of tuples containing (view_name, sql_definition)
    """
    return [
        ("ml_product_recommendations_summary", """
            CREATE OR REPLACE VIEW ml_product_recommendations_summary AS
            SELECT
                p.id as product_id,
                p.name,
                p.price,
                c.name as category,
                (SELECT COUNT(*) FROM store_orderitem WHERE product_id = p.id) as total_orders,
                COALESCE((SELECT AVG(rating) FROM store_review WHERE product_id = p.id), 0) as avg_rating,
                CASE
                    WHEN (SELECT COUNT(*) FROM store_orderitem WHERE product_id = p.id) > 15
                        THEN 'Best Seller'
                    WHEN (SELECT COUNT(*) FROM store_orderitem WHERE product_id = p.id) > 8
                        THEN 'Popular'
                    WHEN (SELECT COUNT(*) FROM store_orderitem WHERE product_id = p.id) > 3
                        THEN 'Trending'
                    ELSE 'New'
                END as product_tier
            FROM store_product p
            LEFT JOIN store_category c ON p.category_id = c.id
            WHERE p.is_active = true
            ORDER BY total_orders DESC;
        """),

        ("ml_customer_ltv_summary", """
            CREATE OR REPLACE VIEW ml_customer_ltv_summary AS
            SELECT
                u.id as user_id,
                u.username,
                u.email,
                COUNT(o.id) as order_count,
                COALESCE(SUM(o.paid_amount), 0) as total_spent,
                COALESCE(AVG(o.paid_amount), 0) as avg_order,
                CASE
                    WHEN SUM(o.paid_amount) > 50000 THEN 'High Value'
                    WHEN SUM(o.paid_amount) > 20000 THEN 'Medium Value'
                    WHEN SUM(o.paid_amount) > 5000 THEN 'Low Value'
                    ELSE 'New Customer'
                END as value_segment,
                MAX(o.created_at) as last_order
            FROM auth_user u
            LEFT JOIN store_order o ON u.id = o.user_id AND o.paid = true
            WHERE u.is_superuser = false
            GROUP BY u.id, u.username, u.email
            ORDER BY total_spent DESC;
        """),

        ("ml_category_performance", """
            CREATE OR REPLACE VIEW ml_category_performance AS
            SELECT
                c.id,
                c.name,
                COUNT(DISTINCT p.id) as product_count,
                COUNT(DISTINCT oi.id) as total_orders,
                COALESCE(SUM(oi.price * oi.quantity), 0) as total_revenue,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                CASE
                    WHEN SUM(oi.price * oi.quantity) > 100000 THEN 'Top Category'
                    WHEN SUM(oi.price * oi.quantity) > 50000 THEN 'Growing'
                    ELSE 'Emerging'
                END as category_tier
            FROM store_category c
            LEFT JOIN store_product p ON c.id = p.category_id
            LEFT JOIN store_orderitem oi ON p.id = oi.product_id
            LEFT JOIN store_review r ON p.id = r.product_id
            GROUP BY c.id, c.name
            ORDER BY total_revenue DESC;
        """),

        ("ml_vendor_intelligence", """
            CREATE OR REPLACE VIEW ml_vendor_intelligence AS
            SELECT
                v.id,
                v.name,
                COUNT(DISTINCT p.id) as products,
                COUNT(DISTINCT oi.order_id) as orders_fulfilled,
                COALESCE(SUM(oi.price * oi.quantity), 0) as total_revenue,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                CASE
                    WHEN AVG(r.rating) >= 4.5 THEN 'Excellent'
                    WHEN AVG(r.rating) >= 4.0 THEN 'Good'
                    WHEN AVG(r.rating) >= 3.0 THEN 'Average'
                    ELSE 'Needs Improvement'
                END as performance_rating
            FROM store_vendor v
            LEFT JOIN store_product p ON v.id = p.vendor_id
            LEFT JOIN store_orderitem oi ON p.id = oi.product_id
            LEFT JOIN store_review r ON p.id = r.product_id
            GROUP BY v.id, v.name
            ORDER BY total_revenue DESC;
        """),
    ]


def get_ml_tables() -> List[Tuple[str, str]]:
    """
    Get list of ML table definitions.

    Returns:
        List of tuples containing (table_name, sql_definition)
    """
    return [
        ("ml_predictions_log", """
            CREATE TABLE IF NOT EXISTS ml_predictions_log (
                id SERIAL PRIMARY KEY,
                prediction_type VARCHAR(50) NOT NULL,
                input_data JSONB,
                output_data JSONB,
                confidence_score NUMERIC CHECK (confidence_score >= 0 AND confidence_score <= 100),
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_ml_predictions_type
            ON ml_predictions_log(prediction_type);

            CREATE INDEX IF NOT EXISTS idx_ml_predictions_created
            ON ml_predictions_log(created_at);
        """),

        ("ml_model_metrics", """
            CREATE TABLE IF NOT EXISTS ml_model_metrics (
                id SERIAL PRIMARY KEY,
                model_name VARCHAR(100) NOT NULL,
                accuracy NUMERIC CHECK (accuracy >= 0 AND accuracy <= 1),
                precision_score NUMERIC CHECK (precision_score >= 0 AND precision_score <= 1),
                recall_score NUMERIC CHECK (recall_score >= 0 AND recall_score <= 1),
                f1_score NUMERIC CHECK (f1_score >= 0 AND f1_score <= 1),
                last_trained TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_ml_metrics_model
            ON ml_model_metrics(model_name);
        """),

        ("ml_feature_store", """
            CREATE TABLE IF NOT EXISTS ml_feature_store (
                id SERIAL PRIMARY KEY,
                entity_type VARCHAR(50) NOT NULL,
                entity_id INTEGER NOT NULL,
                feature_name VARCHAR(100) NOT NULL,
                feature_value NUMERIC,
                updated_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(entity_type, entity_id, feature_name)
            );

            CREATE INDEX IF NOT EXISTS idx_ml_features_entity
            ON ml_feature_store(entity_type, entity_id);
        """),
    ]


def create_ml_functions(manager: MLFeatureManager) -> None:
    """Create all ML functions."""
    logger.info("Creating ML Functions...")
    for name, sql in get_ml_functions():
        manager.execute_sql(name, sql, SQLObjectType.FUNCTION)


def create_ml_views(manager: MLFeatureManager) -> None:
    """Create all ML views."""
    logger.info("Creating ML Views...")
    for name, sql in get_ml_views():
        manager.execute_sql(name, sql, SQLObjectType.VIEW)


def create_ml_tables(manager: MLFeatureManager) -> None:
    """Create all ML tables."""
    logger.info("Creating ML Tables...")
    for name, sql in get_ml_tables():
        manager.execute_sql(name, sql, SQLObjectType.TABLE)


def test_ml_functions(manager: MLFeatureManager) -> None:
    """Test the ML functions to verify they work."""
    logger.info("Testing ML Functions...")

    tests = [
        ("Collaborative Filtering", "SELECT * FROM ml_collaborative_recommendations(5, 5);"),
        ("Content-Based", "SELECT * FROM ml_content_based_recommendations(10, 5);"),
        ("Demand Forecast", "SELECT * FROM ml_demand_forecast(5, 3);"),
        ("Customer Clusters", "SELECT * FROM ml_customer_clusters() LIMIT 5;"),
        ("Review Sentiment", "SELECT * FROM ml_review_sentiment('Excellent quality product!');"),
        ("Product Performance", "SELECT * FROM ml_predict_product_performance(5);"),
        ("Dynamic Pricing", "SELECT * FROM ml_dynamic_pricing_analysis(5);"),
        ("Anomaly Detection", "SELECT * FROM ml_detect_anomalies() LIMIT 3;"),
    ]

    for name, query in tests:
        manager.test_function(name, query)


def print_summary(manager: MLFeatureManager) -> None:
    """Print execution summary."""
    stats = manager.stats

    print("\n" + "=" * 60)
    print("Machine Learning Features - Execution Summary")
    print("=" * 60)

    print(f"\n  Functions: {stats.functions_created} created, {stats.functions_failed} failed")
    print(f"  Views: {stats.views_created} created, {stats.views_failed} failed")
    print(f"  Tables: {stats.tables_created} created, {stats.tables_failed} failed")
    print(f"  Tests: {stats.tests_passed} passed, {stats.tests_failed} failed")

    if stats.errors:
        print(f"\n  Errors ({len(stats.errors)}):")
        for error in stats.errors[:10]:
            print(f"    - {error}")
        if len(stats.errors) > 10:
            print(f"    ... and {len(stats.errors) - 10} more")

    print("\n" + "=" * 60)
    print("ML FEATURES SUMMARY:")
    print("  FUNCTIONS (8):")
    print("    - ml_collaborative_recommendations()")
    print("    - ml_content_based_recommendations()")
    print("    - ml_demand_forecast()")
    print("    - ml_detect_anomalies()")
    print("    - ml_customer_clusters()")
    print("    - ml_review_sentiment()")
    print("    - ml_predict_product_performance()")
    print("    - ml_dynamic_pricing_analysis()")
    print()
    print("  ML VIEWS (4):")
    print("    - ml_product_recommendations_summary")
    print("    - ml_customer_ltv_summary")
    print("    - ml_category_performance")
    print("    - ml_vendor_intelligence")
    print()
    print("  ML TABLES (3):")
    print("    - ml_predictions_log")
    print("    - ml_model_metrics")
    print("    - ml_feature_store")


def main() -> int:
    """
    Main function to add ML features.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("=" * 60)
    print("VIBE E-Commerce - Machine Learning Features")
    print("=" * 60)

    # Validate database configuration
    validator = DatabaseValidator()

    if not validator.is_postgresql():
        logger.error(
            "This script requires PostgreSQL. Current database engine is not PostgreSQL."
        )
        print("\nError: PostgreSQL is required for ML features.")
        print("Please configure PostgreSQL in your settings.")
        return 1

    if not validator.check_connection():
        logger.error("Could not connect to the database.")
        return 1

    db_version = validator.get_db_version()
    if db_version:
        logger.info("Database: %s", db_version[:50])

    # Create ML features
    manager = MLFeatureManager()

    create_ml_functions(manager)
    create_ml_views(manager)
    create_ml_tables(manager)
    test_ml_functions(manager)

    # Print summary
    print_summary(manager)

    return 0 if manager.stats.total_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
