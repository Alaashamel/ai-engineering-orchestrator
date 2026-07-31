from __future__ import annotations


class LLMError(Exception):
    def __init__(
        self,
        message: str,
        provider: str = "unknown",
        model: str = "unknown",
        status_code: int | None = None,
    ) -> None:
        self.message = message
        self.provider = provider
        self.model = model
        self.status_code = status_code
        super().__init__(self.message)


class LLMTimeoutError(LLMError):
    def __init__(
        self, model: str = "unknown", timeout: int = 30
    ) -> None:
        super().__init__(
            message=f"LLM request timed out after {timeout}s for model {model}",
            model=model,
        )
        self.timeout = timeout


class LLMQuotaError(LLMError):
    def __init__(
        self, model: str = "unknown", details: str = ""
    ) -> None:
        super().__init__(
            message=f"Insufficient API quota for model {model}: {details}",
            model=model,
        )
        self.details = details


class LLMRateLimitError(LLMError):
    def __init__(
        self, model: str = "unknown", retry_after: int = 60
    ) -> None:
        super().__init__(
            message=f"Rate limit exceeded for model {model}. Retry after {retry_after}s",
            model=model,
        )
        self.retry_after = retry_after


class LLMValidationError(LLMError):
    def __init__(
        self, model: str = "unknown", details: str = ""
    ) -> None:
        super().__init__(
            message=f"LLM response validation failed for model {model}: {details}",
            model=model,
        )
        self.details = details


class LLMProviderError(LLMError):
    def __init__(
        self, provider: str = "unknown", model: str = "unknown", details: str = ""
    ) -> None:
        super().__init__(
            message=f"LLM provider error [{provider}] for model {model}: {details}",
            provider=provider,
            model=model,
        )
        self.details = details


def classify_llm_error(error: Exception) -> LLMError:
    msg = str(error).lower()
    if "timeout" in msg or "timed out" in msg:
        return LLMTimeoutError()
    if "rate limit" in msg or "429" in msg:
        return LLMRateLimitError()
    if "validation" in msg or "parse" in msg or "schema" in msg:
        return LLMValidationError(details=msg)
    return LLMProviderError(details=msg)