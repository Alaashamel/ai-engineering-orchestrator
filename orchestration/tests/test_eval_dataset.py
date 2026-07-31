import tempfile
from pathlib import Path

from pydantic import BaseModel

from orchestration.eval_dataset import EvalCase, EvalDataset, EvalResult


class EchoResponse(BaseModel):
    message: str


def test_eval_case_creation():
    case = EvalCase(
        name="test_echo",
        prompt="Say hello",
        expected={"message": "hello"},
        response_model=EchoResponse,
        tags=["smoke", "basic"],
        metadata={"priority": 1},
    )
    assert case.name == "test_echo"
    assert case.prompt == "Say hello"
    assert EchoResponse in (case.response_model,)
    assert len(case.tags) == 2


def test_eval_case_to_dict():
    case = EvalCase(name="test", prompt="hi")
    d = case.to_dict()
    assert d["name"] == "test"
    assert d["prompt"] == "hi"


def test_eval_dataset_add_and_filter():
    ds = EvalDataset(name="test")
    ds.add(EvalCase(name="a", prompt="a", tags=["smoke"]))
    ds.add(EvalCase(name="b", prompt="b", tags=["regression"]))
    ds.add(EvalCase(name="c", prompt="c", tags=["smoke"]))
    assert len(ds) == 3
    assert len(ds.filter_by_tag("smoke")) == 2
    assert len(ds.filter_by_name("a")) == 1


def test_eval_dataset_json_roundtrip():
    ds = EvalDataset(name="roundtrip")
    ds.add(EvalCase(name="t1", prompt="prompt1", tags=["a"]))
    ds.add(EvalCase(name="t2", prompt="prompt2", tags=["b"]))
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        ds.to_json(f.name)
        loaded = EvalDataset.from_json(f.name)
    assert loaded.name == "roundtrip"
    assert len(loaded) == 2
    assert loaded.cases[0].name == "t1"
    Path(f.name).unlink(missing_ok=True)


def test_eval_dataset_csv_roundtrip():
    ds = EvalDataset(name="csvtest")
    ds.add(EvalCase(name="t1", prompt="p1", tags=["x"]))
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        csv_path = f.name
        ds.to_csv(csv_path)
        loaded = EvalDataset.from_csv(csv_path)
    assert len(loaded) == 1
    assert loaded.cases[0].name == "t1"
    Path(csv_path).unlink(missing_ok=True)


def test_eval_result_creation():
    case = EvalCase(name="test", prompt="hi")
    result = EvalResult(
        case=case,
        passed=True,
        score=1.0,
        latency_ms=10.5,
        tokens_used=100,
        cost=0.002,
    )
    assert result.passed
    assert result.score == 1.0
    assert result.tokens_used == 100
    assert result.cost == 0.002
    d = result.to_dict()
    assert d["test_name"] == "test"
    assert d["passed"]
