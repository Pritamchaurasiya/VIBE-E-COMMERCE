"""
Django management command for tracking system maintenance.

Usage:
    python manage.py tracking_maintenance --action=cleanup
    python manage.py tracking_maintenance --action=stats
    python manage.py tracking_maintenance --action=export --data-type=user_actions
"""
# pylint: disable=no-member

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from store.tracking_service import EnhancedTrackingService
from store.tracking_models import (
    TrackingConfiguration,
    SystemFileTracker,
    UserActionTracker,
    SystemAccessTracker,
    DataModificationTracker,
    SessionTracker,
    PerformanceMetric,
    TrackingAlert,
    TrackingDataRetention,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command for tracking system maintenance tasks."""

    help = 'Perform tracking system maintenance tasks'

    VALID_ACTIONS = ['cleanup', 'stats', 'export', 'configure', 'alerts', 'setup']

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            required=True,
            choices=self.VALID_ACTIONS,
            help='Action to perform: cleanup, stats, export, configure, alerts, setup'
        )
        parser.add_argument(
            '--data-type',
            type=str,
            help='Data type for export (e.g., user_actions, system_access)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days for export or stats'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='json',
            choices=['json', 'csv'],
            help='Export format'
        )
        parser.add_argument(
            '--enable',
            action='store_true',
            help='Enable tracking category (with --configure)'
        )
        parser.add_argument(
            '--disable',
            action='store_true',
            help='Disable tracking category (with --configure)'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Tracking category for configure action'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for cleanup operations'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without making changes'
        )

    def handle(self, *args, **options):
        action = options['action']

        self.stdout.write(
            self.style.NOTICE(f'Starting tracking maintenance: {action}')
        )

        try:
            if action == 'cleanup':
                self.handle_cleanup(options)
            elif action == 'stats':
                self.handle_stats(options)
            elif action == 'export':
                self.handle_export(options)
            elif action == 'configure':
                self.handle_configure(options)
            elif action == 'alerts':
                self.handle_alerts(options)
            elif action == 'setup':
                self.handle_setup(options)
            else:
                raise CommandError(f'Unknown action: {action}')

        except Exception as exc:
            logger.error("Error in tracking maintenance: %s", exc)
            raise CommandError(str(exc)) from exc

    def handle_cleanup(self, options):
        """Handle cleanup of old tracking data."""
        batch_size = options.get('batch_size', 1000)
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN: No data will be deleted')
            )
            # Show what would be deleted
            self._show_cleanup_preview()
            return

        self.stdout.write('Cleaning up old tracking data...')

        deleted_count = EnhancedTrackingService.cleanup_old_tracking_data(
            batch_size=batch_size
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleaned up {deleted_count} old tracking records'
            )
        )

    def _show_cleanup_preview(self):
        """Show preview of what would be cleaned up."""
        # pylint: disable=no-member
        policies = TrackingDataRetention.objects.filter(
            auto_cleanup_enabled=True,
            is_active=True
        )

        for policy in policies:
            cutoff = self._calculate_cutoff(
                policy.retention_period,
                policy.retention_unit
            )
            if cutoff:
                self.stdout.write(
                    f'  {policy.data_type}: Would delete records before {cutoff}'
                )

    def _calculate_cutoff(self, period, unit):
        """Calculate cutoff date."""
        now = timezone.now().date()
        multipliers = {'days': 1, 'weeks': 7, 'months': 30, 'years': 365}
        multiplier = multipliers.get(unit)
        if multiplier:
            return now - timedelta(days=period * multiplier)
        return None

    def handle_stats(self, options):
        """Display tracking system statistics."""
        days = options.get('days', 7)

        self.stdout.write(
            self.style.HTTP_INFO(f'\n=== Tracking System Statistics (Last {days} days) ===\n')
        )

        # Get stats from service
        stats = EnhancedTrackingService.get_tracking_statistics()

        # Display 24h stats
        self.stdout.write(self.style.SUCCESS('Last 24 Hours:'))
        for key, value in stats.items():
            formatted_key = key.replace('_', ' ').title()
            self.stdout.write(f'  {formatted_key}: {value}')

        # Get extended stats
        cutoff = timezone.now() - timedelta(days=days)

        # pylint: disable=no-member
        extended_stats = {
            'File Operations': SystemFileTracker.objects.filter(
                operation_timestamp__gte=cutoff
            ).count(),
            'User Actions': UserActionTracker.objects.filter(
                action_timestamp__gte=cutoff
            ).count(),
            'System Access Events': SystemAccessTracker.objects.filter(
                access_timestamp__gte=cutoff
            ).count(),
            'Data Modifications': DataModificationTracker.objects.filter(
                timestamp__gte=cutoff
            ).count(),
            'Performance Metrics': PerformanceMetric.objects.filter(
                timestamp__gte=cutoff
            ).count(),
        }

        self.stdout.write(self.style.SUCCESS(f'\nLast {days} Days:'))
        for key, value in extended_stats.items():
            self.stdout.write(f'  {key}: {value}')

        # Configuration status
        self.stdout.write(self.style.SUCCESS('\nTracking Configuration:'))
        configs = TrackingConfiguration.objects.all()
        for config in configs:
            status = '✓ Enabled' if config.is_enabled else '✗ Disabled'
            self.stdout.write(f'  {config.get_category_display()}: {status}')

        # Alert summary
        self.stdout.write(self.style.SUCCESS('\nActive Alerts:'))
        alerts = TrackingAlert.objects.filter(status='active')
        if alerts.exists():
            for alert in alerts[:10]:
                self.stdout.write(
                    f'  [{alert.severity}] {alert.title} - {alert.created_at}'
                )
        else:
            self.stdout.write('  No active alerts')

    def handle_export(self, options):
        """Export tracking data."""
        data_type = options.get('data_type')
        days = options.get('days', 7)
        export_format = options.get('format', 'json')

        if not data_type:
            raise CommandError('--data-type is required for export action')

        cutoff = timezone.now() - timedelta(days=days)

        # pylint: disable=no-member
        model_mapping = {
            'file_operations': (SystemFileTracker, 'operation_timestamp'),
            'user_actions': (UserActionTracker, 'action_timestamp'),
            'system_access': (SystemAccessTracker, 'access_timestamp'),
            'data_modifications': (DataModificationTracker, 'timestamp'),
            'sessions': (SessionTracker, 'login_timestamp'),
            'performance': (PerformanceMetric, 'timestamp'),
            'alerts': (TrackingAlert, 'created_at'),
        }

        if data_type not in model_mapping:
            raise CommandError(
                f'Unknown data type: {data_type}. '
                f'Valid types: {", ".join(model_mapping.keys())}'
            )

        model, timestamp_field = model_mapping[data_type]
        filter_kwargs = {f'{timestamp_field}__gte': cutoff}

        queryset = model.objects.filter(**filter_kwargs)
        count = queryset.count()

        if count == 0:
            self.stdout.write(
                self.style.WARNING(f'No {data_type} records found in the last {days} days')
            )
            return

        self.stdout.write(f'Found {count} records to export')

        # Export data
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        filename = f'tracking_export_{data_type}_{timestamp}.{export_format}'

        if export_format == 'json':
            self._export_json(queryset, filename)
        else:
            self._export_csv(queryset, filename)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported to {filename}')
        )

    def _export_json(self, queryset, filename):
        """Export queryset to JSON file."""
        from django.core.serializers import serialize

        data = serialize('json', queryset)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)

    def _export_csv(self, queryset, filename):
        """Export queryset to CSV file."""
        import csv

        if not queryset.exists():
            return

        fields = [field.name for field in queryset.model._meta.fields]

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

            for obj in queryset:
                row = [getattr(obj, field) for field in fields]
                writer.writerow(row)

    def handle_configure(self, options):
        """Configure tracking settings."""
        category = options.get('category')
        enable = options.get('enable', False)
        disable = options.get('disable', False)

        if not category:
            # Show all configurations
            self.stdout.write(self.style.SUCCESS('\nTracking Configurations:'))
            # pylint: disable=no-member
            for config in TrackingConfiguration.objects.all():
                status = '✓' if config.is_enabled else '✗'
                self.stdout.write(
                    f'  [{status}] {config.category}: {config.get_category_display()}'
                )
            return

        if enable and disable:
            raise CommandError('Cannot use both --enable and --disable')

        if not enable and not disable:
            raise CommandError('Use --enable or --disable with --category')

        try:
            # pylint: disable=no-member
            config, created = TrackingConfiguration.objects.get_or_create(
                category=category,
                defaults={
                    'is_enabled': enable,
                    'description': f'Tracking for {category}',
                }
            )

            if not created:
                config.is_enabled = enable
                config.save(update_fields=['is_enabled', 'updated_at'])

            # Invalidate cache
            EnhancedTrackingService.invalidate_config_cache(category)

            action = 'Enabled' if enable else 'Disabled'
            self.stdout.write(
                self.style.SUCCESS(f'{action} tracking for: {category}')
            )

        except Exception as exc:
            raise CommandError(f'Error configuring tracking: {exc}') from exc

    def handle_alerts(self, _options):
        """Manage tracking alerts."""
        self.stdout.write(self.style.SUCCESS('\n=== Active Alerts ===\n'))

        # pylint: disable=no-member
        alerts = TrackingAlert.objects.filter(status='active').order_by('-created_at')

        if not alerts.exists():
            self.stdout.write('No active alerts')
            return

        for alert in alerts:
            severity_color = {
                'critical': self.style.ERROR,
                'high': self.style.WARNING,
                'medium': self.style.NOTICE,
                'low': self.style.SUCCESS,
            }.get(alert.severity, self.style.NOTICE)

            self.stdout.write(f'\n{severity_color(f"[{alert.severity.upper()}]")} {alert.title}')
            self.stdout.write(f'  Type: {alert.alert_type}')
            self.stdout.write(f'  Created: {alert.created_at}')
            self.stdout.write(f'  Description: {alert.description[:100]}...')

    def handle_setup(self, options):
        """Initialize tracking system with default configurations."""
        dry_run = options.get('dry_run', False)

        self.stdout.write(self.style.NOTICE('\nSetting up tracking system...\n'))

        # Define default configurations
        default_configs = [
            ('file_operations', 'Track file uploads, downloads, and modifications'),
            ('user_actions', 'Track user interactions like clicks, searches, and page views'),
            ('system_access', 'Track login attempts, API access, and security events'),
            ('data_modifications', 'Track database create, update, delete operations'),
            ('login_sessions', 'Track user sessions and login patterns'),
            ('performance_metrics', 'Track response times and system performance'),
            ('security_events', 'Track security-related events and threats'),
            ('api_calls', 'Track API endpoint usage and response times'),
            ('database_queries', 'Track slow and expensive database queries'),
            ('error_tracking', 'Track application errors and exceptions'),
        ]

        # Define default retention policies
        default_retentions = [
            ('file_operations', 90, 'days'),
            ('user_actions', 30, 'days'),
            ('system_access', 180, 'days'),
            ('data_modifications', 365, 'days'),
            ('sessions', 90, 'days'),
            ('performance_metrics', 30, 'days'),
        ]

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN: No changes will be made'))
            self.stdout.write('\nWould create configurations:')
            for cat, _ in default_configs:
                self.stdout.write(f'  - {cat}')
            return

        # Create tracking configurations
        created_configs = 0
        # pylint: disable=no-member
        for category, description in default_configs:
            config, created = TrackingConfiguration.objects.get_or_create(
                category=category,
                defaults={
                    'is_enabled': True,
                    'description': description,
                    'retention_days': 90,
                }
            )
            if created:
                created_configs += 1
                self.stdout.write(f'  ✓ Created config: {category}')

        # Create retention policies
        created_policies = 0
        for data_type, period, unit in default_retentions:
            policy, created = TrackingDataRetention.objects.get_or_create(
                data_type=data_type,
                defaults={
                    'retention_period': period,
                    'retention_unit': unit,
                    'auto_cleanup_enabled': True,
                }
            )
            if created:
                created_policies += 1
                self.stdout.write(f'  ✓ Created retention policy: {data_type}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSetup complete! Created {created_configs} configs '
                f'and {created_policies} retention policies.'
            )
        )
