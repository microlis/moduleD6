import logging
import datetime
from collections import defaultdict

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from news.models import Post, Category


logger = logging.getLogger(__name__)


def send_weekly_digest():

    # Creating a dictionary of emails and new posts for each of them
    new_posts_by_sub = defaultdict(set)

    for category in Category.objects.all():
        category_sub_emails = [sub.email for sub in category.subscribers.all()]

        new_posts_in_category = Post.objects.filter(category=category.id)
        recent_posts = new_posts_in_category.filter(
            posted__gte=timezone.now() - datetime.timedelta(weeks=1)
        )

        for email in category_sub_emails:
            for post in recent_posts:
                new_posts_by_sub[email].add(post)

    # Sending a personal email to each subscriber with a list of new post
    # (if there are any)
    for email in new_posts_by_sub.keys():
        html_content = render_to_string(
            'account/email/digest_form.html',
            {
                'new_posts': new_posts_by_sub[email],
            }
        )

        send_mail(
            subject='Your weekly subscription!',
            message='',
            html_message=html_content,
            from_email=None,
            recipient_list=[email]
        )


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(seld, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_weekly_digest,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="send_weekly_digest",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_weekly_digest'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down succesfully!")
