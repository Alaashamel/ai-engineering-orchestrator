from fastapi import APIRouter, HTTPException
from orchestration.eval_dataset import EvalCase, EvalDataset
from orchestration.llm_config import LLMCostConfig
from orchestration.llm_cost import LLMCostTracker, TokenUsage
from orchestration.llm_factory import LLMProviderFactory
from orchestration.llm_metrics import LLMMetricsCollector
from orchestration.prompt_registry import PromptTemplate, PromptTemplateRegistry
from pydantic import BaseModel

router = APIRouter(prefix="/eval", tags=["eval"])

_cost_tracker = LLMCostTracker(LLMCostConfig())
_metrics = LLMMetricsCollector()
_prompt_registry = PromptTemplateRegistry()


class EvalRunRequest(BaseModel):
    model: str = "gpt-4o"
    dataset_name: str = "default"
    test_count: int = 3


class EvalRunResponse(BaseModel):
    summary: dict
    results: list[dict]


@router.post("/run", response_model=EvalRunResponse)
async def run_eval(req: EvalRunRequest) -> EvalRunResponse:
    provider = LLMProviderFactory.create_provider(
        "openai", api_key=None, model=req.model
    )
    dataset = EvalDataset(name=req.dataset_name)
    for i in range(req.test_count):
        dataset.add(
            EvalCase(
                name=f"test_{i}",
                prompt=f"Generate a test response #{i}",
                expected={"status": "ok"},
            )
        )

    results = []
    for case in dataset.cases:
        try:
            await provider.generate_structured(
                system_prompt=case.system_prompt,
                user_prompt=case.prompt,
                response_model=None,
            )
            results.append({
                "name": case.name,
                "passed": True,
                "score": 1.0,
                "latency_ms": 0,
                "error": None,
            })
        except Exception as exc:
            results.append({
                "name": case.name,
                "passed": False,
                "score": 0.0,
                "latency_ms": 0,
                "error": str(exc),
            })

    summary = {
        "model": req.model,
        "dataset": req.dataset_name,
        "total": len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
    }
    return EvalRunResponse(summary=summary, results=results)


class CostStatsResponse(BaseModel):
    total_cost: float
    total_tokens: int
    total_requests: int
    records: list[dict]


@router.get("/cost", response_model=CostStatsResponse)
async def get_cost_stats() -> CostStatsResponse:
    summary = _cost_tracker.get_summary()
    return CostStatsResponse(
        total_cost=summary["total_cost"],
        total_tokens=summary["total_tokens"],
        total_requests=summary["total_requests"],
        records=summary["records"],
    )


@router.post("/cost/record")
async def record_cost(model: str, prompt_tokens: int, completion_tokens: int):
    usage = TokenUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )
    record = _cost_tracker.record(model=model, usage=usage)
    return {
        "cost": round(record.cost, 6),
        "total_cost": round(_cost_tracker.total_cost, 4),
    }


class PromptRegisterRequest(BaseModel):
    name: str
    template: str
    variables: list[str] = []
    description: str = ""
    version: str = "1.0"


@router.post("/prompts")
async def register_prompt(req: PromptRegisterRequest):
    tmpl = PromptTemplate(
        name=req.name,
        template=req.template,
        variables=req.variables,
        description=req.description,
        version=req.version,
    )
    _prompt_registry.register(tmpl)
    return {"status": "registered", "name": req.name, "version": req.version}


@router.get("/prompts")
async def list_prompts():
    return {
        "templates": _prompt_registry.list_templates(),
        "tags": {name: _prompt_registry.list_tags(name) for name in _prompt_registry.list_templates()},
    }


@router.get("/prompts/{name}")
async def get_prompt(name: str, version: str | None = None):
    if version:
        tmpl = _prompt_registry.get_version(name, version)
    else:
        tmpl = _prompt_registry.get_latest(name)
    if not tmpl:
        raise HTTPException(404, f"Prompt '{name}' not found")
    return tmpl.model_dump()


@router.post("/prompts/{name}/rollback")
async def rollback_prompt(name: str, target_version: str):
    rolled = _prompt_registry.rollback(name, target_version)
    if not rolled:
        raise HTTPException(404, f"Cannot rollback '{name}' to v{target_version}")
    return {"status": "rolled_back", "new_version": rolled.version}


@router.get("/metrics", response_model=dict)
async def get_metrics():
    return _metrics.get_summary()


@router.get("/models")
async def list_models():
    return {
        "available": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "recommended": "gpt-4o",
    }
