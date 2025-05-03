import queue
import threading

from datetime import datetime, timezone
from typing import Type

from sqlalchemy.orm import Session

from core.database import get_db
from models.models import WeatherAlertDB, NotificationDB


class BackgroundService(threading.Thread):
    def __init__(self, input_queue=None):
        super().__init__()
        self.daemon = True
        self.input_queue = input_queue if input_queue else queue.Queue()
        self._stop_event = threading.Event()

    def stop(self):
        """Signal the thread to stop"""
        self._stop_event.set()

    def add_item(self, item: dict):
        """Add an item to be processed by the background service"""
        self.input_queue.put(item)

    def run(self):
        """Main processing loop"""
        while not self._stop_event.is_set():
            try:
                item = self.input_queue.get(timeout=0.1)
                BackgroundService.process_item(item)
                self.input_queue.task_done()
            except queue.Empty:
                continue

    @staticmethod
    def process_item(weather_data: dict):
        """Process a single item from the queue"""
        try:
            db: Session = next(get_db())
            alerts = db.query(WeatherAlertDB).filter_by(
                location=weather_data["location"]).all()
            for alert in alerts:
                if alert.column_name == "humidity":
                    actual_number = weather_data["humidity"]
                elif alert.column_name == "temperature":
                    actual_number = weather_data["temperature"]
                elif alert.column_name == "pressure":
                    actual_number = weather_data["pressure"]
                else:
                    continue
                if BackgroundService.to_be_notified(alert, actual_number):
                    db.add(NotificationDB(
                        user_id=alert.user_id,
                        location=alert.location,
                        column_name=alert.column_name,
                        comparator=alert.comparator,
                        number=alert.number,
                        timestamp=datetime.now(timezone.utc),
                        actual_number=actual_number
                    ))

            db.commit()
        except Exception as e:
            print(e)

    @staticmethod
    def to_be_notified(alert: Type[WeatherAlertDB], actual_number: float):
        if alert.comparator == "<":
            return actual_number < alert.number
        elif alert.comparator == "<=":
            return actual_number <= alert.number
        elif alert.comparator == ">":
            return actual_number > alert.number
        elif alert.comparator == ">=":
            return actual_number >= alert.number
        return False
