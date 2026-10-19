"""One asynchronous delivery at a time, outside document jobs and save checkpoints."""

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor

from .records import Receipt, Report, ReportConsumer


class ReportService:
    def __init__(self, consumer: ReportConsumer) -> None:
        self.consumer = consumer
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="feedback")
        self.future: Future[Receipt] | None = None
        self.receipt = Receipt("", "")
        self.state, self.error, self.location = "idle", "", ""

    def start(self, prepare: Callable[[], Report]) -> None:
        if self.future is not None:
            raise ValueError("A report is already being saved.")
        self.future = self.executor.submit(self.deliver, prepare)
        self.state, self.error, self.location = "saving", "", ""

    def deliver(self, prepare: Callable[[], Report]) -> Receipt:
        return self.consumer.submit(prepare())

    def poll(self) -> bool:
        if self.future is None or not self.future.done():
            return False
        try:
            self.receipt = self.future.result()
            self.location, self.state = self.receipt.location, "saved"
        except Exception as error:
            self.error, self.state = str(error) or type(error).__name__, "failed"
        self.future = None
        return True

    def reset(self) -> None:
        if self.future is not None:
            raise ValueError("Wait until the report finishes saving.")
        self.state, self.error, self.location = "idle", "", ""
        self.receipt = Receipt("", "")

    def close(self) -> None:
        self.executor.shutdown(wait=True)
