# Validation Framework

Maker/Checker validation pattern for autonomous operations with circuit breaker support.

## Quick Start

```python
from core.validation_framework import (
    MakerChecker, RiskLevel, RuleBasedChecker,
    rule_required_fields, rule_valid_ip,
    with_retry, CircuitBreaker
)

# Create a checker with rules
checker = RuleBasedChecker()
checker.add_rule(rule_required_fields("site_id", "config"))
checker.add_rule(rule_valid_ip("target_ip"))

# Execute with validation
mc = MakerChecker(checker=checker, risk_level=RiskLevel.HIGH)
result = mc.execute(
    action_name="deploy_config",
    input_data={"site_id": "abc", "target_ip": "192.168.1.1", "config": {}},
    execute_fn=lambda plan: api.deploy(plan)
)

if result.success:
    print(f"Deployed in {result.execution_time_ms}ms")
else:
    print(f"Failed: {result.error}")
```

## Components

### Risk Levels

```python
class RiskLevel(Enum):
    NONE = "none"       # No validation needed
    LOW = "low"         # Basic validation
    MEDIUM = "medium"   # Standard validation
    HIGH = "high"       # Requires rollback_plan
    CRITICAL = "critical"  # Maximum scrutiny
```

### Built-in Rules

| Rule | Description |
|------|-------------|
| `rule_required_fields("field1", "field2")` | Fields must be present and non-null |
| `rule_no_empty_strings("field")` | Field cannot be empty string |
| `rule_valid_ip("field")` | Must be valid IPv4 address |
| `rule_valid_cidr("field")` | Must be valid CIDR notation |
| `rule_valid_mac("field")` | Must be valid MAC address |
| `rule_in_list("field", ["a", "b"])` | Value must be in allowed list |
| `rule_max_length("field", 255)` | String must not exceed length |
| `rule_positive_number("field")` | Must be positive number |
| `rule_rollback_required()` | HIGH/CRITICAL needs rollback_plan |
| `rule_bulk_confirmation(10)` | Bulk ops (>10 targets) need confirmation |

### Network Safety Checker

```python
from core.validation_framework import NetworkSafetyChecker, CompositeChecker

# Combine with rule-based checker
checker = CompositeChecker([
    NetworkSafetyChecker(),
    my_rule_checker
])
```

Automatically checks:
- Dangerous port exposure (22, 23, 3389, 445, 135, 139)
- Public exposure of private IPs
- Overly permissive firewall rules

### Circuit Breaker

```python
from core.validation_framework import CircuitBreaker, with_retry

# Standalone
cb = CircuitBreaker(failure_threshold=5, timeout=60)

# As decorator
@with_retry(max_retries=3, backoff_base=1.0, circuit_breaker=cb)
async def fetch_api():
    return await client.get("/data")

# Check status
print(cb.get_status())
# {"state": "closed", "failure_count": 0, ...}
```

## Audit Logging

All executions are logged to `logs/maker_checker/audit_trail.jsonl`:

```json
{
  "timestamp": "2025-12-16T12:00:00",
  "operator_id": "user@example.com",
  "risk_level": "high",
  "success": true,
  "action_name": "deploy_config",
  "iterations_required": 1,
  "execution_time_ms": 150.5
}
```

## Decorator Usage

```python
from core.validation_framework import MakerChecker, RiskLevel

@MakerChecker.protected(
    checker=my_checker,
    risk_level=RiskLevel.HIGH,
    action_name="update_firewall"
)
def update_firewall(rule_id: str, config: dict):
    return api.update(rule_id, config)

# Returns ExecutionResult, not raw return value
result = update_firewall(rule_id="fw-123", config={"action": "allow"})
```
