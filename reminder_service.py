import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)


class ReminderService:
    def __init__(self):
        self.reminders: Dict[int, List[Dict]] = {}  # {user_id: [reminders]}
        self.active_tasks = {}

    async def add_reminder(self, user_id: int, text: str, delay_minutes: int):
        """Добавление напоминания"""
        reminder_time = datetime.now() + timedelta(minutes=delay_minutes)
        reminder = {
            'text': text,
            'time': reminder_time,
            'id': len(self.reminders.get(user_id, [])) + 1
        }

        if user_id not in self.reminders:
            self.reminders[user_id] = []

        self.reminders[user_id].append(reminder)

        # Запускаем задачу для напоминания
        task = asyncio.create_task(self._send_reminder(user_id, reminder['id'], delay_minutes * 60))
        self.active_tasks[(user_id, reminder['id'])] = task

        return reminder

    async def _send_reminder(self, user_id: int, reminder_id: int, delay_seconds: int):
        """Внутренний метод для отправки напоминания"""
        await asyncio.sleep(delay_seconds)

        if user_id in self.reminders:
            for reminder in self.reminders[user_id]:
                if reminder['id'] == reminder_id:
                    yield reminder
                    # Удаляем напоминание после отправки
                    self.reminders[user_id].remove(reminder)
                    break

    def get_user_reminders(self, user_id: int) -> List[Dict]:
        """Получение списка напоминаний пользователя"""
        return self.reminders.get(user_id, [])

    def cancel_reminder(self, user_id: int, reminder_id: int) -> bool:
        """Отмена напоминания"""
        if user_id in self.reminders:
            for i, reminder in enumerate(self.reminders[user_id]):
                if reminder['id'] == reminder_id:
                    # Отменяем задачу, если она еще не выполнена
                    task_key = (user_id, reminder_id)
                    if task_key in self.active_tasks:
                        self.active_tasks[task_key].cancel()
                        del self.active_tasks[task_key]

                    del self.reminders[user_id][i]
                    if not self.reminders[user_id]:
                        del self.reminders[user_id]
                    return True
        return False