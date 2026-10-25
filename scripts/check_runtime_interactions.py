"""Real-model comparisons for cached steering and upstream hook parity."""
import json
import sys
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import torch

from activation_steer import ActivationSteerer
from persona_repro.model import ModelRuntime, Steering


def main():
    run, parent = map(Path, sys.argv[1:3])
    config = json.loads((parent / "config.json").read_text())
    model_config = config["model"]
    runtime = ModelRuntime(model_config["id"], revision=model_config["revision"],
                           attention_implementation="sdpa").load()
    vector = torch.load(parent / "vectors/evil.pt", weights_only=True)["raw"][18]
    task = json.loads((parent / "tasks/evil-test.jsonl").read_text().splitlines()[0])
    messages = task["messages"]

    class View(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.owner = runtime.model
            self.config = runtime.model.config.text_config
            self.model = SimpleNamespace(layers=runtime.layers)

    view = View()
    results = {"model": model_config, "question": task["question"], "hook_comparisons": {}}
    answers = {}
    for alpha in (0.0, 0.1, 1.0):
        with Steering(runtime.layers, 19, vector, alpha, "last"):
            own = runtime.generate(messages, temperature=0, max_new_tokens=48)
        with ActivationSteerer(view, vector, coeff=alpha, layer_idx=18, positions="response"):
            reference = runtime.generate(messages, temperature=0, max_new_tokens=48)
        assert own["answer_token_ids"] == reference["answer_token_ids"], alpha
        results["hook_comparisons"][str(alpha)] = {"exact_tokens": True, "answer": own["answer"]}
        answers[alpha] = own
        print("upstream hook matches", alpha, flush=True)
    baseline = runtime.generate(messages, temperature=0, max_new_tokens=48)
    assert baseline["answer_token_ids"] == answers[0.0]["answer_token_ids"]
    results["zero_hook_and_no_state_leak"] = True
    (run / "hook_result.json").write_text(json.dumps(results, indent=2) + "\n")

    def trace(alpha, cached):
        prompt = baseline["prompt_token_ids"]
        forced = baseline["answer_token_ids"][:12]
        logits = []
        past = None
        for step in range(len(forced) + 1):
            prefix = prompt + forced[:step]
            ids = prefix if not cached or step == 0 else [forced[step - 1]]
            if cached:
                context = Steering(runtime.layers, 19, vector, alpha, "last")
            else:
                # Reapply steering to every response-history position on replay.
                def replay(_module, _inputs, output):
                    value = output.clone()
                    value[:, len(prompt) - 1:, :] += vector.to(value.device, value.dtype) * alpha
                    return value
                context = nullcontext()
            handle = None if cached else runtime.layers[18].register_forward_hook(replay)
            try:
                with context, torch.inference_mode():
                    output = runtime.model(
                        input_ids=torch.tensor([ids], device=runtime.model.device),
                        attention_mask=torch.ones((1, len(prefix)), device=runtime.model.device, dtype=torch.long),
                        # Match generate(): cached input positions must be sliced
                        # to the current query, independently of the full mask.
                        position_ids=torch.arange(len(prefix) - len(ids), len(prefix),
                                                  device=runtime.model.device).view(1, -1),
                        past_key_values=past if cached else None,
                        use_cache=cached, logits_to_keep=1)
                logits.append(output.logits[0, -1].float().cpu())
                assert torch.isfinite(logits[-1]).all()
                if cached:
                    past = output.past_key_values
            finally:
                if handle is not None:
                    handle.remove()
        return torch.stack(logits)

    results["cache_comparisons"] = {}
    for alpha in (0.0, 0.1, 1.0):
        a, b = trace(alpha, True), trace(alpha, False)
        results["cache_comparisons"][str(alpha)] = {
            "positions": len(a), "max_logit_difference": float((a - b).abs().max()),
            "mean_logit_difference": float((a - b).abs().mean()),
            "top1_agreement": float((a.argmax(-1) == b.argmax(-1)).float().mean()),
            "mean_kl_cached_to_replay": float((a.softmax(-1) * (a.log_softmax(-1) - b.log_softmax(-1))).sum(-1).mean()),
        }
        print("cache comparison", alpha, results["cache_comparisons"][str(alpha)], flush=True)
    results["layer_19_type"] = runtime.model.config.text_config.layer_types[18]
    results["model_eos"] = runtime.model.generation_config.eos_token_id
    results["tokenizer_eos"] = runtime.tokenizer.eos_token_id
    (run / "result.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
