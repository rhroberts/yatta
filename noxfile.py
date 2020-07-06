import nox

nox.options.sessions = "isort", "black", "lint", "tests", "coverage"

locations = "src", "tests", "noxfile.py"


@nox.session(python=["3.8", "3.7", "3.6"])
def tests(session):
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", external=True)
    session.run("pytest", external=True, *args)


@nox.session(python="3.8")
def lint(session):
    args = session.posargs or locations
    session.install("flake8", "flake8-black")
    session.run("flake8", *args)


@nox.session(python="3.8")
def coverage(session):
    """Upload coverage data."""
    session.install("coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)


@nox.session(python="3.8")
def black(session):
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@nox.session(python="3.8")
def isort(session):
    args = session.posargs or locations
    session.install("isort")
    session.run("isort", *args)
