"""
Database Management Utilities for VIBE E-Commerce.

This module provides utilities for:
- Database backup and restore
- Data migration from SQLite to PostgreSQL
- Database optimization and maintenance
- Health checks and diagnostics

Usage:
    python manage.py shell < db_utils.py
    or
    from db_utils import DatabaseManager
"""

import os
import subprocess  # nosec
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError


class DatabaseManager:
    """Database management utility class."""

    # Error message constant for non-PostgreSQL databases
    POSTGRESQL_ONLY_MSG = "This feature is only available for PostgreSQL"

    def __init__(self):
        """Initialize the database manager."""
        self.backup_dir = Path(settings.BASE_DIR) / 'backups'
        self.backup_dir.mkdir(exist_ok=True)

    def check_connection(self):
        """Check if database connection is working."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True, "Database connection successful"
        except OperationalError as e:
            return False, f"Database connection failed: {e}"

    def get_database_info(self):
        """Get current database configuration info."""
        db_config = settings.DATABASES['default']
        engine = db_config.get('ENGINE', '')

        if 'postgresql' in engine:
            db_type = 'PostgreSQL'
        elif 'sqlite' in engine:
            db_type = 'SQLite'
        else:
            db_type = 'Unknown'

        return {
            'type': db_type,
            'name': db_config.get('NAME', ''),
            'host': db_config.get('HOST', 'N/A'),
            'port': db_config.get('PORT', 'N/A'),
            'user': db_config.get('USER', 'N/A'),
        }

    def backup_json(self, filename=None):
        """
        Create a JSON backup of the database using Django's dumpdata.

        Args:
            filename: Optional custom filename for the backup.

        Returns:
            Path to the backup file.
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            db_info = self.get_database_info()
            filename = f"backup_{db_info['type'].lower()}_{timestamp}.json"

        backup_path = self.backup_dir / filename

        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--exclude=contenttypes',
            '--exclude=auth.permission',
            '--exclude=admin.logentry',
            '--indent=2',
            output=str(backup_path)
        )

        print(f"✅ Backup created: {backup_path}")
        return backup_path

    def restore_json(self, backup_path):
        """
        Restore database from JSON backup.

        Args:
            backup_path: Path to the JSON backup file.
        """
        if not Path(backup_path).exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        call_command('loaddata', backup_path)
        print(f"✅ Database restored from: {backup_path}")

    def backup_postgresql(self, filename=None):
        """
        Create a PostgreSQL native backup using pg_dump.

        Args:
            filename: Optional custom filename for the backup.

        Returns:
            Path to the backup file.
        """
        db_config = settings.DATABASES['default']

        if 'postgresql' not in db_config.get('ENGINE', ''):
            raise ValueError("This method is only for PostgreSQL databases")

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"pg_backup_{timestamp}.sql"

        backup_path = self.backup_dir / filename

        # Build pg_dump command
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config.get('PASSWORD', '')

        cmd = [
            'pg_dump',
            '-h', db_config.get('HOST', 'localhost'),
            '-p', str(db_config.get('PORT', '5432')),
            '-U', db_config.get('USER', 'postgres'),
            '-d', db_config.get('NAME', 'vibe_ecommerce'),
            '-F', 'c',  # Custom format (compressed)
            '-f', str(backup_path),
        ]

        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)  # nosec
            print(f"✅ PostgreSQL backup created: {backup_path}")
            return backup_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Backup failed: {e.stderr.decode()}")
            raise

    def restore_postgresql(self, backup_path):
        """
        Restore PostgreSQL database from native backup.

        Args:
            backup_path: Path to the pg_dump backup file.
        """
        if not Path(backup_path).exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        db_config = settings.DATABASES['default']

        env = os.environ.copy()
        env['PGPASSWORD'] = db_config.get('PASSWORD', '')

        cmd = [
            'pg_restore',
            '-h', db_config.get('HOST', 'localhost'),
            '-p', str(db_config.get('PORT', '5432')),
            '-U', db_config.get('USER', 'postgres'),
            '-d', db_config.get('NAME', 'vibe_ecommerce'),
            '--clean',  # Drop objects before recreating
            '--if-exists',
            str(backup_path),
        ]

        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)  # nosec  # nosec
            print(f"✅ PostgreSQL restored from: {backup_path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Restore failed: {e.stderr.decode()}")
            raise

    def get_table_sizes(self):
        """Get sizes of all tables in the database (PostgreSQL only)."""
        db_config = settings.DATABASES['default']

        if 'postgresql' not in db_config.get('ENGINE', ''):
            return {"error": self.POSTGRESQL_ONLY_MSG}

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    tablename AS table_name,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
                    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 20
            """)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]

        return results

    def get_index_usage(self):
        """Get index usage statistics (PostgreSQL only)."""
        db_config = settings.DATABASES['default']

        if 'postgresql' not in db_config.get('ENGINE', ''):
            return {"error": self.POSTGRESQL_ONLY_MSG}

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan as index_scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched,
                    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
                LIMIT 20
            """)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]

        return results

    def analyze_slow_queries(self):
        """Get slow query statistics (PostgreSQL only, requires pg_stat_statements)."""
        db_config = settings.DATABASES['default']

        if 'postgresql' not in db_config.get('ENGINE', ''):
            return {"error": self.POSTGRESQL_ONLY_MSG}

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        substring(query, 1, 100) as query_preview,
                        round(total_exec_time::numeric, 2) as total_time_ms,
                        calls,
                        round((total_exec_time / calls)::numeric, 2) as avg_time_ms,
                        rows
                    FROM pg_stat_statements
                    ORDER BY total_exec_time DESC
                    LIMIT 10
                """)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]

            return results
        except (OperationalError, AttributeError) as err:
            return {"error": f"pg_stat_statements extension not available: {err}"}

    def vacuum_analyze(self):
        """Run VACUUM ANALYZE on the database (PostgreSQL only)."""
        db_config = settings.DATABASES['default']

        if 'postgresql' not in db_config.get('ENGINE', ''):
            print("VACUUM is only available for PostgreSQL")
            return

        with connection.cursor() as cursor:
            # Can't run VACUUM in a transaction block
            old_autocommit = connection.connection.autocommit
            connection.connection.autocommit = True
            try:
                cursor.execute("VACUUM ANALYZE")
                print("✅ VACUUM ANALYZE completed")
            finally:
                connection.connection.autocommit = old_autocommit

    def reindex_database(self):
        """Rebuild all indexes (PostgreSQL only)."""
        db_config = settings.DATABASES['default']

        if 'postgresql' not in db_config.get('ENGINE', ''):
            print("REINDEX is only available for PostgreSQL")
            return

        db_name = db_config.get('NAME', 'vibe_ecommerce')

        with connection.cursor() as cursor:
            old_autocommit = connection.connection.autocommit
            connection.connection.autocommit = True
            try:
                cursor.execute(f"REINDEX DATABASE {db_name}")
                print("✅ REINDEX completed")
            finally:
                connection.connection.autocommit = old_autocommit

    def get_database_stats(self):
        """Get comprehensive database statistics."""
        db_info = self.get_database_info()
        is_connected, message = self.check_connection()

        db_stats = {
            'connection': {
                'status': 'connected' if is_connected else 'disconnected',
                'message': message,
            },
            'database': db_info,
        }

        if is_connected and db_info['type'] == 'PostgreSQL':
            with connection.cursor() as cursor:
                # Database size
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
                """)
                db_stats['size'] = cursor.fetchone()[0]

                # Active connections
                cursor.execute("""
                    SELECT count(*) FROM pg_stat_activity
                    WHERE datname = current_database()
                """)
                db_stats['active_connections'] = cursor.fetchone()[0]

                # Table count
                cursor.execute("""
                    SELECT count(*) FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
                db_stats['table_count'] = cursor.fetchone()[0]

        return db_stats


def migrate_sqlite_to_postgresql():
    """
    Migrate data from SQLite to PostgreSQL.

    Steps:
    1. Export data from SQLite
    2. Switch to PostgreSQL
    3. Run migrations
    4. Import data
    """
    print("=" * 60)
    print("SQLite to PostgreSQL Migration")
    print("=" * 60)

    manager = DatabaseManager()

    # Step 1: Check current database
    db_info = manager.get_database_info()
    print(f"\nCurrent database: {db_info['type']}")

    if db_info['type'] != 'SQLite':
        print("❌ This migration is only for SQLite databases")
        return

    # Step 2: Create JSON backup
    print("\n📦 Creating JSON backup from SQLite...")
    _backup_path = manager.backup_json('migration_backup.json')

    print("\n" + "=" * 60)
    print("NEXT STEPS (Manual):")
    print("=" * 60)
    print("""
1. Update your .env file:
   DATABASE_ENGINE=postgresql
   POSTGRES_DB=vibe_ecommerce
   POSTGRES_USER=vibe_user
   POSTGRES_PASSWORD=your-password

2. Create the PostgreSQL database:
   CREATE DATABASE vibe_ecommerce;
   CREATE USER vibe_user WITH PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE vibe_ecommerce TO vibe_user;

3. Run migrations:
   python manage.py migrate

4. Load the backup:
   python manage.py loaddata backups/migration_backup.json

5. Verify the migration:
   python manage.py shell
   >>> from db_utils import DatabaseManager
   >>> dm = DatabaseManager()
   >>> print(dm.get_database_stats())
""")


if __name__ == '__main__':
    # Quick diagnostic
    dm = DatabaseManager()
    print("\n" + "=" * 60)
    print("VIBE E-Commerce Database Diagnostics")
    print("=" * 60)

    stats = dm.get_database_stats()
    print(f"\n📊 Database Type: {stats['database']['type']}")
    print(f"📊 Database Name: {stats['database']['name']}")
    print(f"📊 Connection: {stats['connection']['status']}")

    if stats['database']['type'] == 'PostgreSQL':
        print(f"📊 Host: {stats['database']['host']}:{stats['database']['port']}")
        if 'size' in stats:
            print(f"📊 Size: {stats['size']}")
            print(f"📊 Active Connections: {stats['active_connections']}")
            print(f"📊 Tables: {stats['table_count']}")
