from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .governor import RemediationGovernor
from .models import ClusterContext, RemediationRequest


def _load_request(path: Path) -> RemediationRequest:
    data = json.loads(path.read_text())
    return RemediationRequest(**data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a Kubernetes remediation request.")
    parser.add_argument("request", type=Path, help="Path to remediation request JSON")
    parser.add_argument("--environment", default="production")
    parser.add_argument("--max-scale-delta", type=int, default=3)
    args = parser.parse_args()

    request = _load_request(args.request)
    context = ClusterContext(environment=args.environment, max_scale_delta=args.max_scale_delta)
    plan, execution = RemediationGovernor().dry_run(request, context)

    plan_json = asdict(plan)
    plan_json["decision"] = plan.decision.value
    plan_json["risk"] = plan.risk.value
    print(json.dumps({"plan": plan_json, "execution": asdict(execution)}, indent=2))


if __name__ == "__main__":
    main()
