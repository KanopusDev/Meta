from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from app.clients.whatsapp import WhatsAppClient
from app.clients.instagram import InstagramClient

class MessageScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.whatsapp_client = WhatsAppClient()
        self.instagram = InstagramClient()

    def schedule_message(self, recipient: str, message: str, scheduled_time):
        job = self.scheduler.add_job(
            self.whatsapp_client.send_message,
            trigger=DateTrigger(run_date=scheduled_time),
            args=[recipient, message]
        )
        return job.id

    def schedule_template(self, phone: str, template_name: str, language_code: str, send_time: datetime):
        job = self.scheduler.add_job(
            self.whatsapp.send_template,
            'date',
            run_date=send_time,
            args=[phone, template_name, language_code]
        )
        return job.id

    def schedule_instagram_message(self, recipient_id: str, message: str, send_time: datetime):
        job = self.scheduler.add_job(
            self.instagram.send_message,
            'date',
            run_date=send_time,
            args=[recipient_id, message]
        )
        return job.id

    def schedule_instagram_media(self, recipient_id: str, media_url: str, media_type: str, send_time: datetime):
        job = self.scheduler.add_job(
            self.instagram.send_media,
            'date',
            run_date=send_time,
            args=[recipient_id, media_url, media_type]
        )
        return job.id

    def cancel_message(self, job_id: str):
        self.scheduler.remove_job(job_id)

scheduler = MessageScheduler()