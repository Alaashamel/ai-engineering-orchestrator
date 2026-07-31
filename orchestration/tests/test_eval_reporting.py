from orchestration.eval_dataset import EvalCase, EvalDataset, EvalResult
from orchestration.eval_reporting import EvalReport, ReportComparison


def _make_result(name: str, passed: bool, latency: float = 10.0):
    return EvalResult(
        case=EvalCase(name=name, prompt="test"),
        passed=passed,
        score=1.0 if passed else 0.0,
        latency_ms=latency,
        tokens_used=100,
        cost=0.001,
    )


def test_eval_report_summary():
    ds = EvalDataset(name="test")
    ds.add(EvalCase(name="t1", prompt="p1"))
    ds.add(EvalCase(name="t2", prompt="p2"))
    ds.add(EvalCase(name="t3", prompt="p3"))

    results = [
        _make_result("t1", True),
        _make_result("t2", True),
        _make_result("t3", False),
    ]
    report = EvalReport(ds, results, model="gpt-4o", provider_name="openai")
    assert report.total == 3
    assert report.passed == 2
    assert report.failed == 1
    assert report.pass_rate == 2 / 3
    assert report.avg_latency == 10.0
    assert len(report.get_failures()) == 1


def test_eval_report_failures():
    ds = EvalDataset(name="fails")
    ds.add(EvalCase(name="good", prompt="g"))
    ds.add(EvalCase(name="bad", prompt="b"))

    results = [
        _make_result("good", True),
        _make_result("bad", False),
    ]
    report = EvalReport(ds, results)
    failures = report.get_failures()
    assert len(failures) == 1
    assert failures[0].case.name == "bad"


def test_eval_report_to_dict():
    ds = EvalDataset(name="dict_test")
    ds.add(EvalCase(name="t1", prompt="p1"))
    report = EvalReport(ds, [_make_result("t1", True)])
    d = report.to_dict()
    assert d["summary"]["total"] == 1
    assert d["summary"]["passed"] == 1
    assert len(d["results"]) == 1


def test_eval_report_to_markdown():
    ds = EvalDataset(name="md_test")
    ds.add(EvalCase(name="t1", prompt="p1"))
    report = EvalReport(ds, [_make_result("t1", True)])
    md = report.to_markdown()
    assert "# Eval Report: md_test" in md
    assert "t1" in md


def test_report_comparison():
    ds = EvalDataset(name="comp")
    ds.add(EvalCase(name="t1", prompt="p1"))
    r1 = EvalReport(ds, [_make_result("t1", True)], model="gpt4")
    r2 = EvalReport(ds, [_make_result("t1", False)], model="gpt35")

    comp = ReportComparison([r1, r2])
    result = comp.compare()
    assert len(result["comparisons"]) == 2
    md = comp.to_markdown()
    assert "gpt4" in md
    assert "gpt35" in md
