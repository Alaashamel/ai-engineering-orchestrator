from orchestration.llm_reporting import LLMUsageReporter


class TestLLMUsageReporter:
    def test_generate_report(self):
        reporter = LLMUsageReporter()
        metrics = {
            "total_requests": 100,
            "total_tokens": 50000,
            "total_cost": 0.25,
            "avg_latency_ms": 150.0,
            "success_rate": 0.95,
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
        }
        report = reporter.generate_report("gpt-4o", metrics)
        assert report.model == "gpt-4o"
        assert report.total_requests == 100
        assert report.total_cost == 0.25

    def test_get_report(self):
        reporter = LLMUsageReporter()
        metrics = {
            "total_requests": 10,
            "total_tokens": 1000,
            "total_cost": 0.01,
            "avg_latency_ms": 50.0,
            "success_rate": 1.0,
        }
        report = reporter.generate_report("gpt-4o", metrics)
        found = reporter.get_report(report.report_id)
        assert found is not None
        assert found.model == "gpt-4o"

    def test_export_json(self):
        reporter = LLMUsageReporter()
        metrics = {
            "total_requests": 10,
            "total_tokens": 1000,
            "total_cost": 0.01,
            "avg_latency_ms": 50.0,
            "success_rate": 1.0,
        }
        report = reporter.generate_report("gpt-4o", metrics)
        json_str = reporter.export_report(report.report_id, "json")
        assert "gpt-4o" in json_str
        assert "10" in json_str

    def test_export_text(self):
        reporter = LLMUsageReporter()
        metrics = {
            "total_requests": 10,
            "total_tokens": 1000,
            "total_cost": 0.01,
            "avg_latency_ms": 50.0,
            "success_rate": 1.0,
        }
        report = reporter.generate_report("gpt-4o", metrics)
        text = reporter.export_report(report.report_id, "text")
        assert "LLM Usage Report" in text
        assert "gpt-4o" in text

    def test_export_csv(self):
        reporter = LLMUsageReporter()
        metrics = {
            "total_requests": 10,
            "total_tokens": 1000,
            "total_cost": 0.01,
            "avg_latency_ms": 50.0,
            "success_rate": 1.0,
        }
        report = reporter.generate_report("gpt-4o", metrics)
        csv = reporter.export_report(report.report_id, "csv")
        assert "report_id" in csv
        assert "gpt-4o" in csv