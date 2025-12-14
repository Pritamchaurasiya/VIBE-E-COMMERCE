"""
Django management command for database health checks and optimization.

Usage:
    python manage.py db_health              # Quick health check
    python manage.py db_health --verbose    # Detailed diagnostics
    python manage.py db_health --optimize   # Run optimization tasks
    python manage.py db_health --backup     # Create backup
"""
# pylint: disable=no-member

from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError



class Command(BaseCommand):
    """Management command for database health checks and optimization."""

    help = 'Check database health and run optimization tasks'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed diagnostic information',
        )
        parser.add_argument(
            '--optimize',
            action='store_true',
            help='Run database optimization tasks (VACUUM, ANALYZE)',
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create a database backup before optimization',
        )
        parser.add_argument(
            '--analyze-queries',
            action='store_true',
            help='Analyze slow queries (requires pg_stat_statements)',
        )

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write(self.style.HTTP_INFO("=" * 60))
        self.stdout.write(self.style.HTTP_INFO("VIBE E-Commerce Database Health Check"))
        self.stdout.write(self.style.HTTP_INFO("=" * 60))

        # Check connection
        if not self._check_connection():
            raise CommandError("Database connection failed!")

        # Get database info
        db_info = self._get_database_info()
        self.stdout.write(f"\n[INFO] Database Type: {db_info['type']}")
        self.stdout.write(f"[INFO] Database Name: {db_info['name']}")

        if db_info['type'] == 'PostgreSQL':
            self._postgresql_diagnostics(options)
        else:
            self._sqlite_diagnostics(options)

        # Backup if requested
        if options['backup']:
            self._create_backup()

        # Optimize if requested
        if options['optimize']:
            if db_info['type'] == 'PostgreSQL':
                self._postgresql_optimize()
            else:
                self.stdout.write(
                    self.style.WARNING("Optimization is only available for PostgreSQL")
                )

        self.stdout.write(self.style.SUCCESS("\n[OK] Health check complete!"))

    def _check_connection(self):
        """Check if database connection is working."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS("[OK] Database connection: OK"))
            return True
        except OperationalError as e:
            self.stdout.write(self.style.ERROR(f"[ERROR] Database connection failed: {e}"))
            return False

    def _get_database_info(self):
        """Get current database configuration."""
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
        }

    def _postgresql_diagnostics(self, options):
        """Run PostgreSQL-specific diagnostics."""
        with connection.cursor() as cursor:
            # Database size
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
            """)
            db_size = cursor.fetchone()[0]
            self.stdout.write(f"[INFO] Database Size: {db_size}")

            # Active connections
            cursor.execute("""
                SELECT count(*) FROM pg_stat_activity
                WHERE datname = current_database()
            """)
            connections_count = cursor.fetchone()[0]
            self.stdout.write(f"[INFO] Active Connections: {connections_count}")

            # Table count
            cursor.execute("""
                SELECT count(*) FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            self.stdout.write(f"[INFO] Tables: {table_count}")

            if options['verbose']:
                self._show_table_sizes()
                self._show_index_usage()
                self._check_bloat()

            if options['analyze_queries']:
                self._analyze_slow_queries()

    def _sqlite_diagnostics(self, options):
        """Run SQLite-specific diagnostics."""
        db_path = settings.DATABASES['default']['NAME']
        if Path(db_path).exists():
            size_mb = Path(db_path).stat().st_size / (1024 * 1024)
            self.stdout.write(f"[INFO] Database Size: {size_mb:.2f} MB")

        with connection.cursor() as cursor:
            # Table count
            cursor.execute("""
                SELECT count(*) FROM sqlite_master WHERE type='table'
            """)
            table_count = cursor.fetchone()[0]
            self.stdout.write(f"[INFO] Tables: {table_count}")

        if options['verbose']:
            self.stdout.write(self.style.WARNING(
                "\n[NOTE] For detailed diagnostics, switch to PostgreSQL"
            ))

    def _show_table_sizes(self):
        """Display table sizes (PostgreSQL only)."""
        self.stdout.write(self.style.HTTP_INFO("\n[TABLE SIZES] Top 10:"))

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    tablename AS table_name,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 10
            """)
            for row in cursor.fetchall():
                self.stdout.write(f"   {row[0]}: {row[1]}")

    def _show_index_usage(self):
        """Display index usage statistics (PostgreSQL only)."""
        self.stdout.write(self.style.HTTP_INFO("\n[INDEX USAGE] Top 10:"))

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    indexname,
                    idx_scan as scans,
                    pg_size_pretty(pg_relation_size(indexrelid)) as size
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
                LIMIT 10
            """)
            for row in cursor.fetchall():
                self.stdout.write(f"   {row[0]}: {row[1]} scans ({row[2]})")

    def _check_bloat(self):
        """Check for table bloat (PostgreSQL only)."""
        self.stdout.write(self.style.HTTP_INFO("\n[BLOAT CHECK] Checking for bloat..."))

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    schemaname || '.' || tablename AS table_name,
                    n_dead_tup AS dead_tuples,
                    n_live_tup AS live_tuples,
                    CASE
                        WHEN n_live_tup > 0
                        THEN round(100.0 * n_dead_tup / n_live_tup, 2)
                        ELSE 0
                    END AS bloat_ratio
                FROM pg_stat_user_tables
                WHERE n_dead_tup > 1000
                ORDER BY n_dead_tup DESC
                LIMIT 5
            """)
            results = cursor.fetchall()

            if results:
                self.stdout.write(self.style.WARNING("   Tables with significant bloat:"))
                for row in results:
                    self.stdout.write(
                        f"   {row[0]}: {row[1]} dead tuples ({row[3]}% bloat)"
                    )
            else:
                self.stdout.write(self.style.SUCCESS("   [OK] No significant bloat detected"))

    def _analyze_slow_queries(self):
        """Analyze slow queries (PostgreSQL with pg_stat_statements)."""
        self.stdout.write(self.style.HTTP_INFO("\n[SLOW QUERIES] Analysis:"))

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        substring(query, 1, 80) as query_preview,
                        round(total_exec_time::numeric, 2) as total_ms,
                        calls,
                        round((total_exec_time / calls)::numeric, 2) as avg_ms
                    FROM pg_stat_statements
                    WHERE calls > 10
                    ORDER BY total_exec_time DESC
                    LIMIT 5
                """)
                results = cursor.fetchall()

                if results:
                    for row in results:
                        self.stdout.write(f"\n   Query: {row[0]}...")
                        self.stdout.write(
                            f"   Total: {row[1]}ms | Calls: {row[2]} | Avg: {row[3]}ms"
                        )
                else:
                    self.stdout.write("   No query statistics available")

        except (OperationalError, ProgrammingError) as e:
            self.stdout.write(self.style.WARNING(
                f"   [WARN] pg_stat_statements not available: {e}"
            ))

    def _create_backup(self):
        """Create a database backup."""
        self.stdout.write(self.style.HTTP_INFO("\n[BACKUP] Creating backup..."))

        backup_dir = Path(settings.BASE_DIR) / 'backups'
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{timestamp}.json"
        backup_path = backup_dir / filename

        try:
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
            self.stdout.write(self.style.SUCCESS(f"   [OK] Backup created: {backup_path}"))
        except (CommandError, OSError, IOError) as e:
            self.stdout.write(self.style.ERROR(f"   [ERROR] Backup failed: {e}"))

    def _postgresql_optimize(self):
        """Run PostgreSQL optimization tasks."""
        self.stdout.write(self.style.HTTP_INFO("\n[OPTIMIZE] Running optimization..."))

        with connection.cursor() as cursor:
            # Need to run VACUUM outside of transaction
            old_autocommit = connection.connection.autocommit
            connection.connection.autocommit = True

            try:
                self.stdout.write("   Running VACUUM ANALYZE...")
                cursor.execute("VACUUM ANALYZE")
                self.stdout.write(self.style.SUCCESS("   [OK] VACUUM ANALYZE complete"))

                # Update statistics
                self.stdout.write("   Updating statistics...")
                cursor.execute("ANALYZE")
                self.stdout.write(self.style.SUCCESS("   [OK] Statistics updated"))

            except (OperationalError, ProgrammingError) as e:
                self.stdout.write(self.style.ERROR(f"   [ERROR] Optimization failed: {e}"))
            finally:
                connection.connection.autocommit = old_autocommit
