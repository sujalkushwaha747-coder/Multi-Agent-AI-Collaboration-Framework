import pytest
from pydantic import ValidationError

from app.schemas.experiment import ExperimentCreate
from app.services.task_classifier import classify_task


def test_experiment_prompt_validation() -> None:
    with pytest.raises(ValidationError):
        ExperimentCreate(prompt="   ", task_category="academic")


def test_task_classifier_manual_override() -> None:
    assert classify_task("Design an API", "academic") == "academic"
    assert classify_task("Design an API for a database system") == "technical"

