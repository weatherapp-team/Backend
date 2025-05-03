import queue
import threading

from datetime import datetime, timezone
from typing import Type

from sqlalchemy.orm import Session

from core.database import get_db
from models.models import WeatherAlertDB, NotificationDB


class AlertBackgroundService(threading.Thread):
    """
    Service for handling alerts.
    """
    def __init__(self, input_queue=None):
        """
        Initialization of service.
        :param input_queue: queue that will be copied.
        """
        super().__init__()
        self.daemon = True
        self.input_queue = input_queue if input_queue else queue.Queue()
        self._stop_event = threading.Event()

    def stop(self):
        """
        Signal the thread to stop
        :return:
        """
        self._stop_event.set()

    def add_item(self, item: dict):
        """
        Add an item to be processed by the background service
        :param item: item
        :return:
        """
        self.input_queue.put(item)

    def run(self):
        """
        Main processing loop
        :return:
        """
        while not self._stop_event.is_set():
            try:
                item = self.input_queue.get(timeout=0.1)
                AlertBackgroundService.process_item(item)
                self.input_queue.task_done()
            except queue.Empty:
                continue

    @staticmethod
    def process_item(weather_data: dict):
        """
        Process a single item from the queue
        :param weather_data: weather data to process.
        :return:
        """
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
                if AlertBackgroundService.to_be_notified(alert, actual_number):
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
        """
        Checker for comparing alert and weather data
        :param alert: alert.
        :param actual_number: value of column
        :return: True if it is correct, else False
        """
        if alert.comparator == "<":
            return actual_number < alert.number
        elif alert.comparator == "<=":
            return actual_number <= alert.number
        elif alert.comparator == ">":
            return actual_number > alert.number
        elif alert.comparator == ">=":
            return actual_number >= alert.number
        return False
