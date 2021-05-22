from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Post


@receiver(post_save, sender=Post)
def notify_user_post(sender, instance, created, **kwargs):
    if created:
        subject = (f'New post: {instance.title} '
                   f'{instance.posted.strftime("%d.%m.%Y")}')
        message = 'There is a new post in the category you are interested in:'
    else:
        subject = f'Post update: {instance.title}'
        message = 'The post was updated:'

    subs_emails = []
    for category in instance.category.all():
        for user in category.subscribers.all():
            subs_emails.append(user.email)
    subs_emails = set(subs_emails)

    html_content = render_to_string(
        'account/email/email_form.html',
        {
            'post': instance,
            'message': message
        }
    )

    send_mail(
        subject=subject,
        message='',
        html_message=html_content,
        from_email=None,
        recipient_list=[subs_emails]
    )
