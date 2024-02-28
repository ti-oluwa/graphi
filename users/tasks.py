from django.utils.module_loading import import_string
from django.conf import settings
from djmoney.contrib.exchange.backends.base import SimpleExchangeBackend
import sys

from pysche.manager import TaskManager
from pysche.schedules import RunAfterEvery


manager = TaskManager(name="graphi_task_manager")
run_every_1hr = RunAfterEvery(hours=1)


@run_every_1hr(manager=manager, execute_then_wait=True, max_retry=3)
def update_rates(exchange_backend: str = settings.EXCHANGE_BACKEND, **kwargs) -> None:
    exchange_backend: SimpleExchangeBackend = import_string(exchange_backend)()
    exchange_backend.update_rates(**kwargs)
    sys.stdout.write("\nRates updated!\n")


def run_tasks() -> None:
    """Runs the scheduled tasks (in background mode)."""
    manager.start()
    update_rates()

