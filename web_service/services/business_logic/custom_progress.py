from celery_progress.backend import ProgressRecorder


class CustomProgressRecorder(ProgressRecorder):
    """Изменение дефолтного класса ProgressRecorder для добавления поля title"""

    def __init__(self, task, title: str | None = None):
        self.task = task
        self.title = title
        super().__init__(self.task)

    def set_progress(self, current, total, description: str = "", title: str = ""):
        state, meta = super().set_progress(current, total, description)
        meta['title'] = self.title if self.title else title
        self.task.update_state(
            state=state,
            meta=meta
        )
        return state, meta
