import pytest

from orchestration.eval_ab_testing import ABTestFramework, ABTestResult
from orchestration.eval_dataset import EvalCase, EvalDataset


class MockProvider:
    def __init__(self, prefix: str, fail: bool = False):
        self.prefix = prefix
        self.fail = fail

    async def generate_structured(self, system_prompt, user_prompt, response_model):
        if self.fail:
            raise ValueError("mock failure")
        return response_model.model_validate({"message": f"{self.prefix}: ok"})


@pytest.mark.asyncio
async def test_ab_framework_results():
    class MockResp:
        def model_dump(self):
            return {"message": "ok"}

    ds = EvalDataset(name="ab_test")
    ds.add(EvalCase(name="t1", prompt="test 1", expected={"message": "ok"}))
    ds.add(EvalCase(name="t2", prompt="test 2", expected={"message": "ok"}))

    framework = ABTestFramework(ds)
    result = await framework.run(
        MockProvider("A"), MockProvider("B"), model_a_name="gpt4", model_b_name="gpt35"
    )

    assert isinstance(result, ABTestResult)
    assert result.total_cases == 2
    assert result.model_a == "gpt4"
    assert result.model_b == "gpt35"


@pytest.mark.asyncio
async def test_ab_framework_with_failures():
    class MockResp:
        def model_dump(self):
            return {"message": "ok"}

    ds = EvalDataset(name="fail_test")
    ds.add(EvalCase(name="t1", prompt="test", expected={"message": "ok"}))
    framework = ABTestFramework(ds)
    result = await framework.run(
        MockProvider("A", fail=False),
        MockProvider("B", fail=True),
    )
    assert result.total_cases == 1
    for r in result.b_results:
        assert not r.passed
        assert r.error is not None


def test_ab_result_properties():
    ds = EvalDataset(name="props")
    ds.add(EvalCase(name="t1", prompt="p1"))
    result = ABTestResult(
        model_a="a",
        model_b="b",
        total_cases=10,
        a_wins=7,
        b_wins=2,
        ties=1,
        a_avg_latency=100,
        b_avg_latency=200,
        a_avg_score=0.9,
        b_avg_score=0.5,
        a_total_cost=0.01,
        b_total_cost=0.02,
    )
    assert result.winner == "a"
    assert result.confidence > 0
    d = result.to_dict()
    assert d["winner"] == "a"
