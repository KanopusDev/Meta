from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from whatsapp_client import WhatsAppClient
from instagram_client import InstagramClient

class MessageScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.whatsapp = WhatsAppClient()
        self.instagram = InstagramClient()

    def schedule_message(self, phone: str, message: str, send_time: datetime):
        job = self.scheduler.add_job(
            self.whatsapp.send_message,
            'date',
            run_date=send_time,
            args=[phone, message]
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