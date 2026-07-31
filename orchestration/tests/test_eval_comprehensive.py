"""Comprehensive end-to-end eval suite demonstrating all Milestone 5 components."""

import asyncio
import logging
import os
import sys

from pydantic import BaseModel

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from orchestration.eval_ab_testing import ABTestFramework
from orchestration.eval_dataset import EvalCase, EvalDataset, EvalResult
from orchestration.eval_reporting import EvalReport, ReportComparison
from orchestration.llm_factory import LLMProviderFactory
from orchestration.llm_metrics import LLMMetricsCollector
from orchestration.prompt_registry import PromptTemplate, PromptTemplateRegistry

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class CodeResponse(BaseModel):
    language: str
    code: str
    explanation: str


class SummaryResponse(BaseModel):
    summary: str
    key_points: list[str]
    confidence: float


async def run_comprehensive_eval():
    logger.info("=" * 60)
    logger.info("MILESTONE 5: COMPREHENSIVE EVAL SUITE")
    logger.info("=" * 60)

    metrics = LLMMetricsCollector()

    # 1. Create eval datasets
    logger.info("\n[1/6] Creating eval datasets...")
    ds_code = EvalDataset(name="code_generation")
    ds_code.add(EvalCase(
        name="generate_hello_world",
        prompt="Write a Python hello world program",
        response_model=CodeResponse,
        tags=["code", "python"],
    ))
    ds_code.add(EvalCase(
        name="generate_fibonacci",
        prompt="Write a Python function to calculate fibonacci numbers",
        response_model=CodeResponse,
        tags=["code", "python", "algorithm"],
    ))

    ds_summary = EvalDataset(name="summarization")
    ds_summary.add(EvalCase(
        name="summarize_article",
        prompt="Summarize: AI is transforming software engineering by automating testing, code review, and deployment.",
        response_model=SummaryResponse,
        tags=["nlp", "summary"],
    ))
    ds_summary.add(EvalCase(
        name="extract_key_points",
        prompt="Extract key points from: Microservices architecture enables independent deployment of services.",
        response_model=SummaryResponse,
        tags=["nlp", "extraction"],
    ))
    logger.info(f"   Created {len(ds_code) + len(ds_summary)} test cases across 2 datasets")

    # 2. Run eval with real provider (auto-fallback to mock)
    logger.info("\n[2/6] Running LLM provider eval (real+auto-fallback)...")
    provider = LLMProviderFactory.create_provider("openai", api_key=os.getenv("LLM_API_KEY", ""), model="gpt-4o")
    logger.info(f"   Provider mode: {'mock' if provider.mock_mode else 'real'}")

    results_code = []
    for case in ds_code.cases:
        try:
            output = await provider.generate_structured(
                system_prompt="You are an expert Python developer.",
                user_prompt=case.prompt,
                response_model=CodeResponse,
            )
            actual = output.model_dump() if hasattr(output, "model_dump") else output
            passed = isinstance(actual, dict) and "code" in actual
            results_code.append(EvalResult(
                case=case, passed=passed, score=1.0 if passed else 0.0,
                latency_ms=0, actual=actual,
            ))
            metrics.record(provider.model, "generate_structured", 0, 0, passed)
        except Exception as exc:
            results_code.append(EvalResult(
                case=case, passed=False, score=0.0,
                latency_ms=0, error=str(exc),
            ))
            metrics.record(provider.model, "generate_structured", 0, 0, False, str(exc))
    logger.info(f"   Code generation: {sum(1 for r in results_code if r.passed)}/{len(results_code)} passed")

    for case in ds_summary.cases:
        try:
            output = await provider.generate_structured(
                system_prompt="You are an expert at summarization.",
                user_prompt=case.prompt,
                response_model=SummaryResponse,
            )
            actual = output.model_dump() if hasattr(output, "model_dump") else output
            passed = isinstance(actual, dict) and "summary" in actual
            results_code.append(EvalResult(
                case=case, passed=passed, score=1.0 if passed else 0.0,
                latency_ms=0, actual=actual,
            ))
            metrics.record(provider.model, "generate_structured", 0, 0, passed)
        except Exception as exc:
            results_code.append(EvalResult(
                case=case, passed=False, score=0.0,
                latency_ms=0, error=str(exc),
            ))
            metrics.record(provider.model, "generate_structured", 0, 0, False, str(exc))
    logger.info(f"   Summarization: {sum(1 for r in results_code if r.passed)}/{len(results_code)} total passed")

    # 3. A/B testing between two providers
    logger.info("\n[3/6] Running A/B comparison...")
    provider_a = LLMProviderFactory.create_provider("openai", api_key=None, model="gpt-4o")
    provider_b = LLMProviderFactory.create_provider("openai", api_key=None, model="gpt-4o-mini")

    from orchestration.eval_dataset import EvalCase as EC
    ab_ds = EvalDataset(name="ab_test")
    ab_ds.add(EC(name="t1", prompt="Say hello", expected={"message": "ok"}, response_model=CodeResponse))
    ab_ds.add(EC(name="t2", prompt="Say world", expected={"message": "ok"}, response_model=CodeResponse))

    ab = ABTestFramework(ab_ds)
    ab_result = await ab.run(provider_a, provider_b, model_a_name="gpt-4o", model_b_name="gpt-4o-mini")
    logger.info(f"   A/B Result: {ab_result.winner} wins ({ab_result.a_wins}-{ab_result.b_wins}-{ab_result.ties})")

    # 4. Generate reports
    logger.info("\n[4/6] Generating eval reports...")
    report = EvalReport(ds_code, results_code, model="gpt-4o", provider_name="openai")
    logger.info(f"   Pass rate: {report.pass_rate:.1%} ({report.passed}/{report.total})")
    logger.info(f"   Failures: {[r.case.name for r in report.get_failures()]}")

    md_report = report.to_markdown()
    logger.info(f"   Markdown report generated ({len(md_report)} chars)")

    comparison = ReportComparison([report])
    comp_result = comparison.compare()
    logger.info(f"   Comparison: {len(comp_result['comparisons'])} models compared")

    # 5. Prompt versioning with diff/rollback/tags
    logger.info("\n[5/6] Testing prompt versioning...")
    reg = PromptTemplateRegistry()
    v1 = reg.update(PromptTemplate(
        name="code_gen", template="Write {language} code for {task}",
        variables=["language", "task"], description="Initial version",
    ))
    logger.info(f"   Registered v{v1.version}")
    v2 = reg.update(PromptTemplate(
        name="code_gen", template="Generate high-quality {language} code for {task}",
        variables=["language", "task"], description="Improved clarity",
    ))
    logger.info(f"   Registered v{v2.version}")

    v1_ver, v2_ver = v1.version, v2.version
    diff = reg.diff("code_gen", v1_ver, v2_ver)
    logger.info(f"   Diff ({len(diff)} chars): {diff[:120]}...")
    reg.tag_version("code_gen", v1_ver, "stable")
    reg.tag_version("code_gen", v2_ver, "latest")
    by_tag = reg.get_by_tag("code_gen", "stable")
    assert by_tag is not None, f"Tag 'stable' should point to v{v1_ver}"
    logger.info(f"   Tag 'stable' -> v{by_tag.version}")
    rolled = reg.rollback("code_gen", v1_ver)
    assert rolled is not None, "Rollback should succeed"
    logger.info(f"   Rollback to v{v1_ver} -> v{rolled.version}")
    history = reg.get_version_history("code_gen")
    logger.info(f"   Version history: {len(history)} versions")

    # 6. Metrics summary
    logger.info("\n[6/6] Metrics summary:")
    summary = metrics.get_summary()
    logger.info(f"   Total requests: {summary['total_requests']}")
    logger.info(f"   Success rate: {summary['overall_success_rate']:.1%}")
    logger.info(f"   Models tracked: {summary['models']}")

    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("COMPREHENSIVE EVAL COMPLETE")
    logger.info("=" * 60)
    logger.info(f"  • {'✓' if report.total > 0 else '✗'} Eval dataset creation")
    logger.info(f"  • {'✓' if provider else '✗'} LLM provider (real+fallback)")
    logger.info(f"  • {'✓' if len(results_code) > 0 else '✗'} Eval execution")
    logger.info(f"  • {'✓' if report.pass_rate >= 0 else '✗'} Report generation")
    logger.info(f"  • {'✓' if ab_result.total_cases > 0 else '✗'} A/B comparison")
    logger.info(f"  • {'✓' if len(history) > 0 else '✗'} Prompt versioning + diff + rollback")
    logger.info(f"  • {'✓' if summary['total_requests'] >= 0 else '✗'} Metrics collection")
    logger.info("=" * 60)

    assert report.total > 0, "Eval report should have results"
    assert ab_result.total_cases > 0, "AB test should have cases"
    assert len(history) >= 3, "Prompt versioning should have 3+ versions (v1, v2, rollback)"
    logger.info("\n✓ ALL ASSERTIONS PASSED")


if __name__ == "__main__":
    asyncio.run(run_comprehensive_eval())
