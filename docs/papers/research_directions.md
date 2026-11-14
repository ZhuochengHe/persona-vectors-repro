# Literature positioning and feasibility of two research directions

Updated:2026-11-09. Uses the existing Persona collection, Assistant Axis citation reading, and verified originals to analyze research space, minimal experiments, and computational feasibility. These are research judgments, not results from new experiments.

## Assessment first

Agentic persona steering offers substantial research space. [Activation-Steered Personas in Task-Oriented LLM Agent Simulations](https://openreview.net/pdf?id=RBI5BjsREi) already directly steers user/system agents with persona vectors in SGD task-oriented dialogue, adapting system mixtures each turn. Related work controls emotions, task-failure modes, roles, and task–role–state representations. Open tool execution, long-horizon feedback, direction sources, and planning/action selectivity remain promising; these dialogue precedents are useful starting comparisons, so agentic persona steering as a whole should not be described as unexplored.

Prioritize agentic persona steering: whether persona directions change real decisions or improve performance, and how effects evolve with feedback/time. Phenomenon analysis, extraction, and control methods can each contribute independently; ordinary additive steering suffices to start. Architecture research can be a parallel candidate or later extension, with one model/environment fixed initially to control cost.

## Distinguishing experimental settings

Single-turn: a task may contain a long CoT, many-shot input, a text game, or answer probabilities. These features alone do not establish a long-horizon agent setting.

Multi-turn dialogue: roles, user pressure, identity, and memory evolve with the history, but executable actions or external state may be absent.

Long context / long horizon: record long inputs, persistent dialogue, cross-session memory, and multi-step environment tasks separately. Do not group them under one “long” label. Interpret length using actual turns, tool steps, and reset behavior.

Agentic execution: the model selects an action, the environment executes it, and returns state or reward. Tool-name strings, preset tool responses, questionnaires, or a “delete files” option alone do not establish execution.

Intervention subject: distinguish the target agent, user simulator, auditing tool, and offline trajectory readout. An agent in the environment does not imply that the persona direction is injected into the executing agent.

Benchmark / Validation entries in both collections now include a [Setting] prefix. Sources and evidence boundaries are recorded in evaluation_regimes.json. The separate Assistant Axis collection has no Excel synchronization or architecture columns.

## Direction 1: existing work on agentic persona vectors

### Agentic paper comparison

Findings focus on agent behavior, long interactions, or control. Task distinguishes dialogue references, monitoring, and execution. Unverified datasets are explicitly marked; details are not inferred from titles.

| Paper | Link | Finding: agentic relevance | Task | Steering / vector type | Dataset / environment |
| --- | --- | --- | --- | --- | --- |
| [PERSONA / Persona-Flow（ID7）](https://arxiv.org/abs/2602.15669) | [Open](https://arxiv.org/abs/2602.15669) | Combines persona directions as dialogue context changes and controls expression; tool actions and task completion were not tested. | Big Five personality control + multi-trait composition and dynamic steering | Yes; ten Big Five trait-pole persona vectors, composed by context | PersonalityBench; contextualized BFI-44; Persona-Evolve (800 scenarios) |
| [Prompt-Activation Duality / GCAD（ID42）](https://arxiv.org/abs/2605.10664) | [Open](https://arxiv.org/abs/2605.10664) | Maintains persona expression and reduces coherence loss over ten dialogue turns; long-term intervention must account for cache accumulation. Agent execution was not tested. | Multi-turn persona control + reducing coherence loss from KV-cache accumulation | Yes; control signals derived from the attention contribution of persona system prompts (GCAD) | 15 traits × 10 dialogue turns with persistent KV cache |
| [PersonaSteer](https://aclanthology.org/2026.findings-emnlp.1270/) | [Open](https://aclanthology.org/2026.findings-emnlp.1270/) | Learns steering signals from history and improves personalization as dialogue progresses; evaluates multi-turn alignment rather than tool-task completion. | Personalized alignment＋learnable activation steering | Yes; high-dimensional steering vectors learned from interaction history, not fixed Big Five axes | ALOE; Extended ALOE (OOD tests built with PersonaChat profiles) |
| [Emotion Concepts and their Function in a Large Language Model（ID4）](https://arxiv.org/abs/2604.07729) | [Open](https://arxiv.org/abs/2604.07729) | Increasing desperation or reducing calm increases coding reward hacking; stronger emotion may change the strategy rather than monotonically amplify the original behavior. | Effects of emotion steering on agent reward hacking, blackmail, and related decisions | Yes; emotion vectors such as desperation, calm, and anger | Seven author-constructed coding reward-hacking tasks and blackmail scenarios |
| [How Emotion Shapes the Behavior of LLMs and Agents / E-STEER（ID29）](https://arxiv.org/abs/2604.00005) | [Open](https://arxiv.org/abs/2604.00005) | Preferred emotion strengths differ between planning, answer selection, and execution; optimizing one module does not maximize whole-agent success. | Effects of emotion steering on planning, selection, and execution capabilities | Yes; VAD emotion directions using features selected in SAE space | HotpotQA；Scientific；GAIA |
| [Impatient Users Confuse AI Agents（ID19）](https://arxiv.org/abs/2510.04491) | [Open](https://arxiv.org/abs/2510.04491) | Changing only the user simulator’s impatience and related traits can reduce target-agent success; the hardest traits depend on model and domain. | Persona-steered user simulation + agent robustness evaluation | Yes; impatience, skepticism, confusion, and incoherence directions in the user simulator | τ-Trait: airline, retail, telecom, and telemedicine; BFCL multi-turn calls |
| [TACT（AA06）](https://arxiv.org/abs/2605.05980) | [Open](https://arxiv.org/abs/2605.05980) | Intervening on overthinking / overacting directions at the end of reasoning improves task completion and reduces steps; experiments cover dense and MoE models. | Reducing agent overthinking / overacting + steering at the thinking–action boundary | Yes; two behavioral directions contrasting overthinking / overacting with calibrated steps | SWE-bench Verified；Terminal-Bench 2.0；CLAW-Eval |
| [Mitigating Reward Hacking in Realistic Scenarios Through Representation Engineering（AA43）](https://arxiv.org/abs/2610.29129) | [Open](https://arxiv.org/abs/2610.29129) | Directions extracted from trajectories and other sources reduce tool-based reward hacking; original-task solve rates must also be checked to distinguish improvement from abandonment. | Reducing agent reward hacking + behavioral direction extraction and dynamic capping | Yes; hacking-trace differences, optimized directions, and anti-hacking-spec directions; addition / cap / floor compared | MisTrace; ImpossibleBench; original LiveCodeBench; also School of Reward Hacks |
| [ContextEcho（ID38／AA08）](https://arxiv.org/abs/2605.24279) | [Open](https://arxiv.org/abs/2605.24279) | Claude Code histories change assistant expression and format compliance; restoring Axis projection in snapshot branches did not restore expression scores. | Observing long-horizon agent persona drift + testing Assistant Axis intervention | Yes; Assistant Axis, limited to snapshot-branch intervention tests | ContextEcho evaluation: three donated Claude Code logs (coding, manuscript writing, and document work) + 25 identity / preference questions; 23 models are test subjects, not datasets |
| [Telling FIBS（AA40）](https://arxiv.org/abs/2610.12445) | [Open](https://arxiv.org/abs/2610.12445) | Internal readouts detect covert sabotage in tool trajectories, including unspoken behavior; this is monitoring rather than direct agent control. | Monitoring agent deception / sabotage + activation probes | No activation steering; activation probes monitor deception / sabotage | FIBS；SHADE-Arena；BashArena |
| [Social Priors（AA42）](https://arxiv.org/abs/2610.16946) | [Open](https://arxiv.org/abs/2610.16946) | One agent with antisocial user priors can exhaust a shared resource; Axis control is a separate probability-scoring experiment, not evidence of corrected environment behavior. | Effects of user social priors on agent trust and cooperation + Axis-control tests | Yes; Assistant Axis capping only in the trust-scoring branch, not the GovSim execution branch | GovSim fisheries; matched social-prior corpora; 376-context Axis controls |
| [Mind Your Own Role / DRAS](https://arxiv.org/abs/2610.15907) | [Open](https://arxiv.org/abs/2610.15907) | Adjusting role directions according to overstepping risk reduces overstepping and improves software output quality; the static variant with least overstepping is not necessarily best in quality. | Reducing multi-agent role overstepping + dynamic role steering | Yes; activation differences with / without role instructions, with dynamically adjusted strength | ChatDev / MetaGPT; 1,200 SRDD requirements; SWE-Dev for preparation / validation |
| [Drift No More / ATLAS（ID48）](https://arxiv.org/abs/2611.04315) | [Open](https://arxiv.org/abs/2611.04315) | Jointly maintaining task, role, and current state improves memory and coordination, including under embodied perturbations; call-structure scores and environment execution are reported separately. | Reducing task / role / state drift + joint-subspace steering | Yes; a joint task / role / state subspace kernel, not a single persona vector | EverMemBench；AMemGym；ToolACE；ALARA；LIBERO |
| [Controlling Large Language Model Agents with Entropic Activation Steering / EAST](https://arxiv.org/abs/2406.00244) | [Open](https://arxiv.org/abs/2406.00244) | Directions extracted from interactions control exploration; token sampling temperature does not reproduce the effect. The environment is a simplified bandit. | Controlling agent exploration + entropy-weighted activation steering | Yes; an exploration direction extracted with action-entropy weighting | Gaussian two-armed bandit and textually rephrased variants |
| [Multi-LLM Systems Exhibit Robust Semantic Collapse](https://arxiv.org/abs/2605.17193) | [Open](https://arxiv.org/abs/2605.17193) | Reducing sycophancy in short tests did not restore long-term group semantic diversity; changing a trait behavior does not guarantee improvement in system-level metrics. | Multi-agent semantic-diversity collapse + anti-sycophancy steering tests | Yes; an anti-sycophancy direction tested for mitigating semantic collapse | Author-generated interactions of 200–1,000 turns; 200-turn steering test |
| [Activation-Steered Personas in Task-Oriented LLM Agent Simulations](https://openreview.net/pdf?id=RBI5BjsREi) | [Open](https://openreview.net/pdf?id=RBI5BjsREi) | Persona vectors are injected into both user and system agents. Turn-level system adaptation mainly improves judge-rated truthfulness and satisfaction; task gains are modest and depend on domain, trait, and strength. | Persona control in task-oriented dialogue + fixed user / dynamic system steering | Yes; ten Big Five trait-pole persona vectors; fixed for the user, composed each turn for the system | Schema-Guided Dialogue (SGD): Restaurants, Movies; 50 Baseline–SA dialogue pairs and 2,000 US–US+SA pairs (including α=0) |

### Multi-turn persona control already exists

[PERSONA / Persona-Flow, ID7](https://arxiv.org/abs/2602.15669) dynamically composes Big Five directions by context; [GCAD, ID42](https://arxiv.org/abs/2605.10664) studies ten persona-dialogue turns with persistent KV cache. They constrain claims of the first dynamic / multi-turn persona steering method, but dialogue scores are not tool actions.

[PersonaSteer](https://aclanthology.org/2026.findings-emnlp.1270/) learns a side model and steering feedback loop from interaction history for multi-turn personalization. History-dependent persona-vector updates should therefore be compared with existing methods; they still require validation on actual environment decisions.【】用llm模拟用户和系统，通过steering来提高用户满意度，用户固定steer确定人格，系统通过外部llm选alpha强度来动态steering回答问题 选用的是大五人格的vectors

### The closest agent-related evidence in the collection

[Emotion Concepts, ID4](https://arxiv.org/abs/2604.07729) includes reward-hacking scenarios with code execution and unit-test feedback; [E-STEER, ID29](https://arxiv.org/abs/2604.00005) studies emotion interventions in planner / decider / executor workflows and tool tasks. Internal emotion directions affecting agents thus have precedents, but emotion, organizational roles, and stable personality should not be assumed to share directions.

[Impatient Users, ID19](https://arxiv.org/abs/2510.04491) injects persona vectors into the user simulator to evaluate a tool agent. This is an interaction-pressure baseline rather than direct control of the evaluated agent’s persona.

[TACT, AA06](https://arxiv.org/abs/2605.05980) extracts overthinking / overacting axes from labeled trajectories and applies Add / Cap / Gate at the think–action boundary on SWE-bench Verified, Terminal-Bench, and CLAW-Eval. It directly demonstrates trace-based online agent control, but extracts failure modes rather than traits transferred from everyday conversation.

[Reward Hacking, AA43](https://arxiv.org/abs/2610.29129) compares specification-based, trajectory-mean-difference, and optimized directions, with real coding-tool execution and original-task capability controls. Natural-language-domain transfer recalibrates thresholds and changes some optimization targets; it is not evidence of zero-shot transfer to arbitrary behavior.【】注意他们提取的activation为思考结束的token</think>

[ContextEcho, ID38 / AA08](https://arxiv.org/abs/2605.24279) probes snapshots of real coding sessions and finds that restoring a projection need not restore visible register scores; it does not validate task completion after steering an entire trajectory. [FIBS, AA40](https://arxiv.org/abs/2610.12445) detects deception in real tool loops, providing readout rather than persona-writing evidence.【】这一篇说明了agentic setting的drifting，主要是关于assistant中立身份的drifting，甚至可能发生在早期。同时输出的结构也会drift。注意在做了assistant axis的steering后，assistant-register score 甚至还下降了

[Social Priors, AA42](https://arxiv.org/abs/2610.16946) retains belief / trust differences under Axis capping, but that branch scores candidate likelihoods; GovSim environment actions belong to a different branch. It motivates testing Axis sufficiency, but does not establish that a tool agent takes the same harmful action after Axis restoration.

### Existing methods and expandable research space

[DRAS: Mind Your Own Role](https://arxiv.org/abs/2610.15907) dynamically adjusts role activations in ChatDev / MetaGPT. The write direction is an activation difference with / without role instructions in the same task context; the detector is trained on overstepping / compliant trajectories. This combines textual specification, trace monitoring, and dynamic strength, offering comparisons across persona sources, extraction positions, and task objectives. Role-boundary control does not cover the action-level expression of stable personality dispositions.

[ATLAS: Drift No More](https://arxiv.org/abs/2611.04315) (ID48) combines task, role, and state subspaces in a PSD kernel for multiplicative spectral intervention and state-memory updates. AMemGym, ALARA, and LIBERO provide environment-feedback evidence; ToolACE mainly scores call structure. It shows that joint-subspace and dynamic-state control can work, providing a methodological baseline while leaving persona sources, behavioral selectivity, cross-stage control, and other tasks open. ActAdd / SEA and ATLAS intervene on different numbers of roles, so comparisons must state intervention coverage.

The earlier [EAST](https://arxiv.org/abs/2406.00244) work extracted action-entropy-weighted directions from environment interactions in 2024, controlled Gaussian-bandit exploration, and received actual reward feedback. It is not a personality paper, but is a relevant methodological baseline for trace extraction and decision control.

[Multi-LLM Systems Exhibit Robust Semantic Collapse](https://arxiv.org/abs/2605.17193) provides a related negative result: reducing sycophancy in short evaluations need not restore long-term multi-agent semantic diversity. It concerns trait-to-system-outcome transfer in long interactions without external tools. [Activation-Steered Personas in Task-Oriented LLM Agent Simulations](https://openreview.net/pdf?id=RBI5BjsREi) directly demonstrates persona steering in task-oriented dialogue: it reuses Big Five vectors from PERSONA, applies fixed user-side intervention, predicts and composes system-side coefficients each turn, or intervenes on both sides. On SGD Restaurants / Movies, the main improvements are judge-rated truthfulness and satisfaction; aggregate task-metric differences for Qwen under directional user steering are not significant. It is distinct from the prompt-conditioning study in 2608.18085v2.

### Promising research questions and a minimal design

Core question: how do persona directions from different sources affect an agent’s actual actions, and when does a local behavioral change translate into long-term task benefit? Behavioral control, performance improvement, and drift can be studied separately; a contribution need not solve all three.

Minimal starting point: one open model, one tool environment with restorable states and real feedback, and one operational disposition such as caution / verification. Compare conversational-persona and agent-behavior directions while initially fixing the extraction position and using ordinary addition; add self-report and role-play later. Behavioral measures can include proactive checks, submission with insufficient evidence, and redundant verification, alongside task success and call cost. Do not equate these measures with an entire Big Five trait. Offline extraction may use outcome labels; online deployment may use only information available at that time.

Evaluate the same candidates at three levels: prediction / replay on fixed traces; actions and short branches from the same restorable environment state; and full rollouts from task initialization. Compare rankings by readout score, local intervention effect, and long-term benefit. Run some low-ranked screening candidates to estimate false exclusions. Decodability, controllability, and task improvement are three relationships to test.

Mismatch between screening and actual rollout is itself a research question. Intervention changes actions, which change feedback and future state distributions; replay effectiveness cannot guarantee closed-loop benefit. Branching estimates conditional counterfactual effects, but complete rollouts are needed for cumulative consequences. Use development data for exploration / selection and independent tasks for confirmation. Local screening reduces cost but should not be the sole validity criterion.

Record drift, behavior, and performance in the same rollouts: separately measure direction projections, linguistic expression, actions, and intervention benefit across stages. Task progress may legitimately require strategy changes, so annotate task stage, tool failure, external feedback, and compaction. Snapshot expression results for Assistant Axis motivate hypotheses but do not replace full-trajectory action experiments with other persona directions.

Compute cost is driven mainly by rollout length, candidate configurations, and repetitions. Shared prefixes, environment snapshots, and short branches reduce exploration cost, while reserving budget for full rollouts; short branches estimate only conditional local effects. Collect selected-layer activations / statistics at several candidate positions in each trajectory instead of saving every layer and token. Initially fix model, disposition, and environment, then expand one axis at a time; behavior, performance, and drift share the same trajectories.

Variations include direction source (conversation / self-report / role-play / agent trace / task specification); extraction position (end of thinking, before / after tool calls, after feedback); intervention stage (planning / action / feedback integration / throughout); temporal adaptation (fixed direction, dynamic strength, online direction updates); target behavior (risk, verification, exploration, persistence / abandonment, honest reporting); and evaluation horizon (replay, short branches, full rollouts). Each axis can support a contribution; a full factorial experiment is unnecessary.

Distinguish three online-extraction designs: extract from historical agent traces and freeze; keep the direction fixed while changing strength or gating during execution; or update the direction / subspace using new feedback within the current run. Trace extraction and dynamic capping in Reward Hacking (AA43) do not automatically mean relearning directions inside a test episode. Online updates must specify feedback signals, update cost, and sensitivity to erroneous feedback, and be compared with fixed directions plus dynamic strength.

A promising expansion sequence is to test conversation-to-action transfer and screening / rollout mismatch first; then cross extraction and intervention positions to ask whether the best readout site is also the best control site. If effects change after feedback, compare adjusting strength with changing direction. Online adaptation can also be an independent topic, evaluated jointly by task benefit, behavioral selectivity, and additional cost.

## Direction 2: existing persona-vector research across architectures

### First distinguish structural dimensions

Dense / MoE describes parameter routing; pruned subnetworks describe weight masks; dynamic activation sparsity describes units actually computed at each step; SAE sparsity is a feature coordinate system; loop / recurrent depth describes repeated application of the same module. These dimensions can intersect rather than forming four exclusive model classes. MoE can contain attention, and a looped model can be dense. CoT length and multi-turn dialogue are not looped-Transformer architecture.

### Evidence already visible in the architecture fields

App.F of [Style Modulation Heads, ID23](https://arxiv.org/html/2603.13249v2) performs attention-output / head steering on Gemma3 and Qwen3-30B-A3B-Instruct-2507. This is intervention, not just probing, and layer-localization patterns differ from the main model. Those additional models were previously missing from the architecture field and have been added. However, attention-head intervention does not establish MoE-expert-path analysis; model differences also include scale, training, and normalization.

[Persona-Dependent Preferences, ID9 / AA07](https://arxiv.org/html/2605.13339v4) includes dense and MoE / hybrid models, with transferable readouts but inconsistent writing results. This warrants explanation but does not isolate routing as the cause. [TACT](https://arxiv.org/abs/2605.05980) also tests agent axes across architectures without varying architecture alone.

[Personality Subnetworks, ID22](https://arxiv.org/abs/2602.07164) controls persona with activation-guided / contrastive weight masks. This is a static subnetwork, not native MoE or dynamic sparse inference that skips computation. The author’s technical report [Persona Neurons](https://willmayner.com/persona-neurons) tests whether a few MLP neurons reproduce persona steering, comparing rotated bases, PCs, and random neurons. It is a direct blog-level precedent, not proof of necessity under natural activation or an acceleration result.

### Architecture-specific control methods for MoE

[SteerMoE](https://arxiv.org/abs/2509.09660) compares expert-activation frequencies under opposite behavioral conditions, then promotes / suppresses experts at inference for safety and faithfulness. Behavior-associated expert identification and control therefore have precedents.【】直接steer router

[RARE](https://arxiv.org/abs/2608.21236) uses clean-routing controls to locate steering-induced routing drift, projects perturbations into the router null space, and corrects downstream routing. It directly studies impaired MoE steering caused by routing disruption and improvements from preserving routing; its tasks do not establish full persona / cross-task behavioral selectivity.【】steer with router locked

[MASCing](https://arxiv.org/abs/2604.27818) learns cross-layer routing dependencies and reconfigures behavior with router masks, including multi-turn jailbreaks. MoE multi-turn control should therefore not be described as unstudied.

[Explaining the Roles of Experts for Personalization](https://arxiv.org/abs/2610.22127) studies three MoE personalization models, crosscoder latents, and expert interventions, providing persona / personalization-related structural evidence. Expert boosting shifts outputs toward the personalized model distribution without establishing general behavioral improvement; layer / split selection also requires scrutiny.【】moe相关机理

[PersonaFuse](https://arxiv.org/abs/2509.07370) adds trait-level LoRA experts and a router, including enterprise tool workflows. This must be distinguished from finding naturally occurring persona experts in a native MoE.

MoE control and personalization methods exist, while persona readout, writing, and selectivity across contexts / decision stages remain open. Compare residual, routing, and joint pathways for the same trait and localize cross-model differences. Existing MoE steering provides baselines rather than grounds to dismiss the direction. Preserving routing may protect capability, while some target behaviors may require expert changes; both possibilities deserve testing.

### Opportunities and risks in looped / recurrent depth

[Shared Weights, Selected Computations](https://arxiv.org/abs/2609.39892) uses a linear map of the state entering a loop to select graph-walk computations and validates paths with attention patching. It provides mechanistic evidence that states can control computation under shared weights, but does not study persona.

[Ouro](https://arxiv.org/abs/2510.25741) and [LoopFormer](https://arxiv.org/abs/2602.11451) provide official architecture / model entry points. This search did not verify systematic persona geometry across loops or behavioral selectivity in their official papers. The discovered [loopformer persona code](https://github.com/chengyh23/loopformer) is a fork, showing exploratory code rather than a published result from the original authors; a first-implementation claim would also require caution.

[Locating and Steering Refusal Beyond Attention](https://arxiv.org/abs/2609.04721) covers refusal readout / writing and role-play control in SSM, Transformer, recurrent, and hybrid architectures. Cross-architecture safety control exists, but refusal is not a complete persona mechanism.

Concrete loop questions: does the same physical layer carry the same persona direction at different effective depths? Do early versus late injections affect identity / style or decisions? As the loop budget grows, does a direction converge, rotate, disappear, or repeatedly amplify? Shared weights make intervention timing at a fixed loop budget more suitable for local causal evidence than cross-family score comparisons.

First check whether an official checkpoint has adequate role-following and task capability; without a capable baseline, failed steering cannot be attributed to architecture. Fix model and loop budget, compare injection at one step, a contiguous range, and all steps, and match total dose / perturbation norm. Record physical block, iteration, and token position. Injecting the same α at every iteration accumulates dose, so resulting side effects cannot simply be called geometric change. Then test cross-loop writing and held-out contexts before expanding to dense controls or agent tasks.

### Feasibility and priorities

MoE is feasible to start with residual-only, router-only, and joint interventions, including RARE and personalization-expert baselines. Cross-family results can reveal phenomena, followed by better-matched controls to identify causes. Estimate memory from total weights and KV requirements: 30B BF16 weights alone require about 60GB; active parameter count does not directly determine memory.

Loop questions are more focused and direct persona evidence is sparser, but implementation and interpretation are harder: shared-module hooks may fire at every iteration, cache / halting changes effective computation, and a base LM may not follow role instructions. Start with a small model at fixed depth to establish feasibility before expensive long-horizon agents.

Define sparsity precisely. Controlling persona with a few units relates directly to Persona Neurons, SAE sparse steering, and Personality Subnetworks. Preserving persona control under sparse execution additionally requires actual sparse kernels, latency / compute measurements, and capability controls. Fewer nonzero parameters or edited neurons alone do not establish efficiency.

## Two concrete research topics worth developing

Main line: Agentic Persona Steering. Start with one disposition, one environment, and two direction sources, measuring actual behavior, performance, and drift together. Analyze relationships between screening scores, local effects, and full-rollout benefit. Later expand positions, online extraction, dynamic control, and cross-task transfer. Method improvements and empirical characterization can both contribute.

Architecture line: Persona across Recurrent Depth. Study direction geometry, cross-iteration causal effects, and dose controls in a fixed looped model before assessing generalization. MoE is a separate branch with explicit routing questions; avoid turning both into an initial project covering every architecture.

The agentic and architecture lines can proceed independently or intersect later. Prioritize controllability and utility of persona in actual actions. Stability, position differences, online adaptation, and architecture dependence provide continuing research paths. Contributions can be a clear new phenomenon, an effective method, or a valuable task improvement without requiring a complete mechanism or all environments.
