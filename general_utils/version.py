from pathlib import Path

def get_version() -> str | None:
    """Retrieve version from pyproject.toml"""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        return None
    
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            return pyproject_data.get("project", {}).get("version")
    except Exception:
        return None