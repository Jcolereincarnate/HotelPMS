from django.core.management.base import BaseCommand
from django.utils import timezone
from analytics.utils import update_daily_metrics


class Command(BaseCommand):
    help = 'Update daily hotel metrics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to update metrics for (YYYY-MM-DD format)',
        )

    def handle(self, *args, **options):
        date_str = options.get('date')
        
        if date_str:
            from datetime import datetime
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date()
        
        self.stdout.write(f'Updating daily metrics for {target_date}...')
        
        metrics = update_daily_metrics(target_date)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated metrics for {target_date}\n'
                f'Occupancy: {metrics.occupancy_rate}%\n'
                f'Revenue: ₦{metrics.total_revenue}\n'
                f'Check-ins: {metrics.check_ins}\n'
                f'Check-outs: {metrics.check_outs}'
            )
        )
