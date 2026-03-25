from app.core.celery_app import celery_app


def test_celery_app_includes_worker_tasks() -> None:
    includes = tuple(celery_app.conf.include or ())
    imports = tuple(celery_app.conf.imports or ())

    assert "app.workers.tasks" in includes
    assert "app.workers.tasks" in imports
