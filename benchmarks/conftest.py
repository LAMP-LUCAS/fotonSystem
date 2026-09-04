def pytest_addoption(parser):
    parser.addoption(
        "--benchmark", action="store_true", default=False,
        help="Run benchmark tests (STORY-038 performance SLA validation)",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--benchmark"):
        return
    skip_bench = __import__("pytest").mark.skip(
        reason="Use --benchmark flag to run benchmark tests",
    )
    for item in items:
        if "benchmark" in item.keywords:
            item.add_marker(skip_bench)
