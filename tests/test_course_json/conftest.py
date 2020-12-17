
def pytest_addoption(parser):
    parser.addoption("--course_id", action="store", nargs=2, default="GOMO1")
