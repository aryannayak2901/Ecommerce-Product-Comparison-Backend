from django_cron import CronJobBase, Schedule
from ecom_product_comparison_app.tasks import cleanup_old_products

class CleanupProductsCronJob(CronJobBase):
    RUN_EVERY_MINS = 60 * 24  # Run once per day

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'ecom_product_comparison.cleanup_products_cron_job'

    def do(self):
        cleanup_old_products() 