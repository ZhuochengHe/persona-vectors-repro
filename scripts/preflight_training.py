"""Real E08 pilot; retain data/config/results, never launch the formal matrix."""
import gc
import json
import math
import sys
from pathlib import Path

from persona_repro.data import prepare_subsets
from persona_repro.model import ModelRuntime
from persona_repro.training import train_adapter


def main():
    run = Path(sys.argv[1])
    work = Path(sys.argv[2])
    config = json.loads((run / "source/configs/reproduction.json").read_text())
    prepare_subsets(work / "raw/dataset", run / "data", 1000, 100, 0, ["evil"])
    source = run / "data/evil/misaligned_2/train.jsonl"
    pilot = source.with_name("pilot_train.jsonl")
    pilot.write_text("\n".join(source.read_text().splitlines()[:200]) + "\n")
    (run / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    result = train_adapter(config, pilot, source.with_name("dev.jsonl"), run / "adapter")
    assert result["global_step"] == 13, result["global_step"]
    assert math.isfinite(result["metrics"]["train_loss"])
    assert result["update_probe"]["delta_norm"] > 0
    for record in result["log_history"]:
        for key in ("loss", "grad_norm"):
            if key in record:
                assert math.isfinite(record[key]), record
    import torch
    gc.collect()
    torch.cuda.empty_cache()
    model = config["model"]
    runtime = ModelRuntime(model["id"], revision=model["revision"],
                           adapter_path=run / "adapter", attention_implementation="sdpa").load()
    answer = runtime.generate([{"role": "user", "content": "What is 2 + 2?"}],
                              temperature=0, max_new_tokens=32)
    result["reload_generation"] = answer
    result["status"] = "passed"
    result["scope"] = "Evil-II 200 examples, one epoch; not a formal E08 result"
    (run / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps(result, default=str), flush=True)


if __name__ == "__main__":
    main()
