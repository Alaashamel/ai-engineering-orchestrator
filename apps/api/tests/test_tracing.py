from orchestration.tracing import setup_tracing, get_tracer, trace_phase

def test_get_tracer_returns_tracer():
    tracer = get_tracer()
    assert tracer is not None

def test_setup_tracing_returns_tracer():
    tracer = setup_tracing(service_name="test")
    assert tracer is not None

def test_setup_tracing_is_idempotent():
    t1 = setup_tracing()
    t2 = setup_tracing()
    assert t1 is t2
