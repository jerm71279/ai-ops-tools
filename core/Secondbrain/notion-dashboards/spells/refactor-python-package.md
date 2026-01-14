# Spell: `refactor-python-package`

## Category: 🤖 Automation & Code Quality

## Purpose
Transform a collection of standalone Python scripts into a well-structured, maintainable package with shared infrastructure, typed data models, comprehensive tests, and proper error handling.

## When to Use
- Multiple scripts with duplicated code (config loading, logging, API calls)
- No existing test coverage
- Inconsistent error handling patterns
- Need to add retry logic, validation, or maker/checker patterns

---

## Spell Template

```
You are refactoring a Python codebase for [ORGANIZATION_NAME]. 

## Context
- Scripts to refactor: [LIST_OF_SCRIPTS]
- External APIs used: [LIST_APIS - e.g., Notion, UniFi, NinjaOne]
- Target test count: [MIN_TESTS - e.g., 100+]
- Preserve originals: [YES/NO]

## Analysis Phase
First, analyze the existing code for:
1. Duplicated patterns (config loading, logging setup, API initialization)
2. Inconsistent error handling
3. Missing type safety
4. Absent retry logic
5. Code that should be shared vs. script-specific

## Refactoring Requirements

### 1. Core Infrastructure Module (`core/`)
Create shared infrastructure:

```python
# core/base_sync.py - Abstract base class
class BaseSyncClient(ABC):
    """
    Base class providing:
    - Config loading with validation
    - Client initialization with dry-run support
    - Retry-wrapped API methods
    - Page caching for relations
    - Maker/checker validation
    """
    
    @property
    @abstractmethod
    def primary_database(self) -> str:
        """Subclasses must define their primary database."""
        pass
    
    @abstractmethod
    def sync(self, **kwargs) -> List[Dict]:
        """Main sync operation - subclasses implement."""
        pass

# core/config.py - Typed configuration
@dataclass
class Config:
    """Typed config with validation."""
    
    @classmethod
    def from_file(cls, path: str) -> 'Config':
        """Load and validate config."""
        pass

# core/errors.py - Exception hierarchy
class [PROJECT]Error(Exception):
    """Base exception for all [PROJECT] errors."""
    pass

class ConfigurationError([PROJECT]Error):
    """Missing or invalid configuration."""
    pass

class ValidationError([PROJECT]Error):
    """Data validation failure."""
    pass

class RateLimitError([PROJECT]Error):
    """API rate limit exceeded."""
    pass

# core/retry.py - Retry decorator
@retry_on_exception(exceptions=(RateLimitError,), max_retries=3)
def api_call():
    pass

# core/logging_config.py - Centralized logging
def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    pass
```

### 2. Services Module (`services/`)
Extract business logic into reusable services:

```python
# services/[DOMAIN]_calculator.py
@dataclass
class [Domain]Metrics:
    """Input metrics for calculation."""
    pass

@dataclass  
class [Domain]Result:
    """Calculation output with breakdown."""
    score: float
    status: str
    breakdown: Dict[str, float]
    
class [Domain]Calculator:
    """Unified calculation with configurable weights."""
    
    def calculate(self, metrics: [Domain]Metrics) -> [Domain]Result:
        pass
```

### 3. Data Sources Module (`data_sources/`)
Abstract external API access:

```python
# data_sources/interface.py
class [API]DataSource(ABC):
    """Abstract interface for [API] data."""
    
    @abstractmethod
    def fetch_items(self) -> List[[Item]]:
        pass

# data_sources/stub.py
class Stub[API]DataSource([API]DataSource):
    """Test implementation with realistic data."""
    
    def __init__(self, count: int = 100, seed: int = 42):
        """Reproducible test data."""
        pass

# Factory pattern for runtime switching
def get_[api]() -> [API]DataSource:
    """Get configured data source (stub by default)."""
    pass
```

### 4. Refactored Scripts
Each script inherits from BaseSyncClient:

```python
class [Script]Sync(BaseSyncClient):
    @property
    def primary_database(self) -> str:
        return "[database_name]"
    
    def sync(self, **kwargs) -> List[Dict]:
        # Implementation using inherited methods:
        # - self.create_page()
        # - self.update_page()
        # - self.query_database()
        # - self.check_bulk_operation()
        pass
```

### 5. Test Suite
Generate comprehensive tests:

```python
# tests/conftest.py - Shared fixtures
@pytest.fixture
def config_file(tmp_path):
    """Create test config file."""
    pass

# tests/test_[module].py
class Test[Feature]:
    def test_happy_path(self):
        pass
    
    def test_validation_error(self):
        pass
    
    def test_dry_run_mode(self):
        pass
```

## Validation Checklist
After refactoring, verify:
- [ ] All tests pass: `pytest tests/ -v`
- [ ] No regressions: Original functionality preserved
- [ ] Dry-run works: `--dry-run` flag on all scripts
- [ ] Error messages clear: Typed exceptions with context
- [ ] Documentation updated: README/docstrings

## Output Structure
```
[package]/
├── scripts/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_sync.py
│   │   ├── config.py
│   │   ├── errors.py
│   │   ├── logging_config.py
│   │   └── retry.py
│   ├── services/
│   │   └── [domain]_calculator.py
│   ├── data_sources/
│   │   ├── __init__.py
│   │   ├── interface.py
│   │   └── stub.py
│   ├── [script1]_v2.py
│   ├── [script2]_v2.py
│   └── ...
├── tests/
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_errors.py
│   └── test_[module].py
├── requirements.txt
└── REFACTORING-SUMMARY.md
```
```

---

## Example Invocation

```
You are refactoring a Python codebase for OberaConnect.

## Context
- Scripts to refactor: customer_status_sync.py, daily_health_sync.py, 
  config_change_sync.py, azure_pipeline_sync.py, runbook_manager.py
- External APIs used: Notion API, UniFi Site Manager, NinjaOne RMM
- Target test count: 150+
- Preserve originals: YES

[Follow the spell template above...]
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Test coverage | 90%+ |
| Code reduction | 20-30% |
| Exception types | 5+ custom types |
| Typed dataclasses | All inputs/outputs |
| Retry logic | All external API calls |
| Documentation | README + docstrings |

---

## Related Spells
- `summon-tests` - Generate test suite
- `transmute-code` - Generic code transformation
- `forge-interface` - Create abstract interfaces
- `summon-docs` - Generate documentation

---

*Spell Version: 1.0*  
*Created: January 2025*  
*Author: OberaConnect AI OS*
