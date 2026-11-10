# Assistant Axis: Citing Papers

Default identity · Representation geometry · Persona drift · Behavioral control and agent transfer

## Reading guide

Navigate through research questions or the paper index. IDs open notes; short titles open papers. Abstract findings are separate from body-level methodological evidence. Additional think is reserved for the user.

Candidates come from mlsanity’s snapshot of direct Assistant Axis citations: 95 arXiv records with official abstracts. Relevance and distinct contribution selected 43 for targeted reading of the body and relevant appendices, plus seed paper AA00. Other items retain screening reasons. This is neither a complete cross-database citation set nor a reproduction or exhaustive artifact audit of 43 experiments.

[Assistant Axis direct-citation list](https://mlsanity.com/paper/2601.10387/)

This tab shares the Persona Google Doc. AA IDs and reading data remain separate, with no local Excel synchronization or architecture columns.

### Browse by research question

Foundation paper: Assistant Axis | AA00

Where does the default persona come from, and how do roles coexist with the Assistant? | AA01, AA03, AA10, AA12, AA13, AA17, AA23, AA24, AA28, AA32, AA35, AA41

How stable is the geometry, and do similar directions have similar effects? | AA02, AA04, AA22, AA26, AA27, AA29, AA30, AA31

What causes multi-turn persona drift, and which stabilization methods work? | AA05, AA08, AA16, AA25, AA38, AA39

What is read or changed: self-report, tone, preferences, or safety behavior? | AA07, AA09, AA11, AA14, AA15, AA19, AA20, AA33, AA36, AA37

Can conversational directions transfer to real agent actions? | AA06, AA18, AA21, AA34, AA40, AA42, AA43

### Browse by paper type

Method: AA00, AA01, AA06, AA07, AA10, AA11, AA13, AA15, AA17, AA21, AA24, AA26, AA27, AA28, AA31, AA33, AA37, AA38, AA40, AA43

Benchmark: AA08, AA16, AA37, AA38, AA40

Survey: None in the current close-reading set

Analysis: AA00, AA01, AA02, AA03, AA04, AA05, AA06, AA07, AA08, AA09, AA10, AA11, AA12, AA13, AA14, AA15, AA16, AA17, AA18, AA19, AA20, AA21, AA22, AA23, AA24, AA25, AA26, AA27, AA28, AA29, AA30, AA31, AA32, AA33, AA34, AA35, AA36, AA37, AA38, AA39, AA40, AA41, AA42, AA43

Theory: AA04, AA31

Theory is reserved for formal statements and proofs; Analysis may include equations and geometric experiments. Unmarked is the user’s reading status, not the depth of the notes.

### Suggested reading paths

Suggested start: AA00 → AA02 → AA06 → AA08 → AA24 → AA32 → AA42 → AA43. These connect default identity, contextual variation, agent-trace directions, drift measurement, training generalization, shared role features, and actual behavioral boundaries.

The default Assistant need not be entirely replaced by another role. Training generalization in AA24 and SAE feature analysis in AA32 provide distinct evidence for shared structure; AA23 tests whether preferences extend beyond assistant turns. Their operational definitions differ, so they should not be treated as the same vector or mechanism.

Distinguish geometry, prediction, and control. AA02 shows reversed intervention effects in some contexts; AA31 studies highly discriminative directions with reversed control. AA22 links many cross-trait side effects to model defaults. AA29 retains corrected prompt separability but withdraws its earlier direction-to-norm account.

Interpret drift readouts alongside specific tasks. Register scores in AA08 depend on the judge, and restoring a single-layer projection did not recover output scores; AA16 separates questionnaire personality, behavior, and memory. Attractors in AA05 come from response-text embeddings, not model hidden-state axes.

For agents, prioritize comparing AA06 and AA43: the former extracts failure-mode axes from labeled traces; the latter compares directions and interventions in real tool tasks. AA18 contrasts conversational stance with execution transfer; capping in AA42 mainly reads belief / trust differences through answer likelihoods. Together they define what to measure next without reducing all outcomes to persona stability.

## Paper index

Task describes the experiment; Major finding summarizes the abstract; Benchmark / Validation specifies tasks, metrics, and key conditions. Detailed contributions, limitations, and citation evidence are in the notes.

| ID | Short title | Type | Status | Task | Major finding (abstract) | Benchmark / Validation |
| --- | --- | --- | --- | --- | --- | --- |
| [AA00](#AA00) | [The Assistant Axis](https://arxiv.org/abs/2601.10387) | Analysis; Method | Unmarked | Assistant identity, multi-turn drift monitoring, and stabilization | Assistant Axis captures default-assistant mode; constraining activations along it mitigates tested dialogue drift and persona jailbreaks. | [Setting] Single-turn role directions and multi-turn identity/safety dialogues; no validation of real tool-task completion. [Validation] 275 roles×240 shared questions; three models; multi-turn dialogue, persona jailbreaks, and capability-retention controls. |
| [AA01](#AA01) | [J-space / Global Workspace](https://arxiv.org/abs/2607.15495) | Method; Analysis | Unmarked | Workspace readout/intervention; counterfactual-reflection training | J-space carries reportable, accessible concepts for flexible reasoning; post-training introduces the Assistant perspective, and counterfactual-reflection training improves behavior without explicit reflection. | [Setting] Readouts from long agent traces, summary honesty, and role dialogue; not closed-loop tool-control gains. [Validation] Production Claude and matched base models; report/automatic-processing separation, role drift, hidden-goal audits, agent reward hacking, and reflection ablations. |
| [AA02](#AA02) | [Conversation-dependent Representations](https://arxiv.org/abs/2601.20834) | Analysis | Unmarked | Cross-dialogue readout and steering stability | Concept readouts and behavioral effects of one linear direction can change sharply during dialogue, mainly for dialogue-relevant content. | [Setting] Factual answers in scripted/on-policy role dialogues; no tool execution. [Validation] Mainly Gemma3-27B; opposite-day, consciousness/chakra roles, on/off-policy dialogues, explicit stories, CCS, cross-layer/smaller-model controls. |
| [AA03](#AA03) | [Persona Formation in Pretraining](https://arxiv.org/abs/2605.13329) | Analysis | Unmarked | Cross-checkpoint geometry, facets, and control transfer | Persona directions extracted very early in pretraining already control the final instruct model; geometry/semantics continue refining, and elicitation methods emphasize different facets. | [Setting] Single-turn trait extraction/generation control across checkpoints, not long-horizon agents. [Validation] 17 OLMo3-7B pretraining checkpoints plus SFT/DPO/RLVR; four traits; Apertus8B replication and discourse/random-direction controls. |
| [AA04](#AA04) | [Prompt-inaccessible Steering States](https://arxiv.org/abs/2604.09839) | Theory; Analysis | Unmarked | Prompt reachability of steered states | Under stated assumptions, steered residual states almost surely lack natural-prompt preimages, separating white-box steerability from black-box reachability. | [Setting] Short-prompt/internal-trajectory inversion and attack controls; no tool or multi-turn task. [Validation] Three0.5B–1B nonthinking models; refusal/evil directions; SipIt inversion, many-shot ICL, INT4, and Here-attack controls. |
| [AA05](#AA05) | [Attractors in LLM–LLM Debate](https://arxiv.org/abs/2606.30571) | Analysis | Unmarked | Behavioral dynamics in self-play/mixed-play | Self-play forms model-specific endpoint regions; mixed-play influence is asymmetric and not simple one-dimensional averaging. | [Setting] Two-model20-turn topic discussions; output-embedding convergence is not environmental action. [Validation] Seven models,20 controversial topics,20 turns;384D SBERT output embeddings, discourse traits/stances; role/seed/embedding ablations. |
| [AA06](#AA06) | [TACT / Agent Drift Axes](https://arxiv.org/abs/2605.05980) | Method; Analysis | Unmarked | Agent-step calibration and tool-task control | Two drift axes detect and mitigate overthinking/overacting, improving coding-agent completion and reducing steps. | [Setting] Real software-repair/terminal/tool tasks; trace axes calibrate think–action boundaries. [Validation] Qwen3.5-27B/Gemma4-26B-A4B-it; SWE-bench Verified/Terminal-Bench2.0/CLAW-Eval; problem-held-out, judge/human, and operator ablations. |
| [AA07](#AA07) | [Persona-dependent Preference Read/Write](https://arxiv.org/abs/2605.13339) | Analysis; Method | Unmarked | Cross-persona preference prediction and pairwise-choice control | An Assistant-trained preference probe transfers across personas, even predicting and controlling evil-persona preferences opposed to the Assistant’s. | [Setting] Pairwise task-preference probabilities/open generation; the6000 tasks are not executed. [Validation] 6000 tasks/14 topics; Gemma3-27B/Qwen3.5-122B; independent utilities, leave-topic-out, text embeddings, random directions, and LoRA-persona controls. |
| [AA08](#AA08) | [ContextEcho / Long Coding Register Drift](https://arxiv.org/abs/2605.24279) | Benchmark; Analysis | Unmarked | Register/format stability in production-agent contexts | Long agent context changes Assistant register; anchors reset expression nonspecifically, while restored Axis projection need not restore behavioral scores. | [Setting] Identity/format probes after real coding-session snapshots; not post-control task completion. [Validation] 57 sessions/29 donors;23-model representative-session panel;25 identity probes, judge-free format/lexical measures, compaction, placebo, and Qwen Axis-dose tests. |
| [AA09](#AA09) | [Critical Roles vs Targeted Sycophancy](https://arxiv.org/abs/2605.21006) | Analysis | Unmarked | Functional comparison of role and sycophancy directions | Generic critical-role vectors approach trait-specific sycophancy-direction effects despite low cosine similarity. | [Setting] PhilPapers binary agreement and 16 factual questions; no tools/long interaction. [Validation] Gemma2-27B L22/Qwen3-32B L32;600 reversed-order PhilPapers rows; tune/test, random directions,16 facts, and cosine/residual analysis. |
| [AA10](#AA10) | [Persona Cartography in Weight Space](https://arxiv.org/abs/2607.07916) | Method; Analysis | Unmarked | OCEAN LoRA composition and downstream safety trade-offs | Trait LoRAs offer continuous, approximately additive control within appropriate ranges, change untrained safety behaviors, and expose native behavioral factors through rollouts. | [Setting] Weight-persona composition; multi-turn frustration/pushback and single-turn capability/safety, without tools. [Validation] Six4B–32B models/three families; TRAIT, human-calibrated judges, MMLU/GSM8K/TruthfulQA; frustration, sycophancy, WildJailbreak, and Axis-capping controls. |
| [AA11](#AA11) | [Authority vs User Agreement](https://arxiv.org/abs/2609.37616) | Analysis; Method | Unmarked | Selective control of source obedience and user agreement | Source deference and user agreement can overlap strongly geometrically yet respond selectively to different interventions, requiring separate behavioral evaluation. | [Setting] Trivia/PIQA, multi-turn SYCON, and static retrieved blocks; not a live retrieval-tool agent. [Validation] Five open families/three APIs; initially correct trivia, PIQA, SYCON, retrieved blocks; matched wrong answers, cue patching, Axis/affect/capability controls. |
| [AA12](#AA12) | [Pre-existing Persona Core & EM](https://arxiv.org/abs/2607.21356) | Analysis | Unmarked | Cross-domain persona cores, EM formation, and training/inference interventions | A pre-existing low-rank persona core shared across four domains enables broad misalignment during fine-tuning; training-time projection prevents formation, while inference injection induces it. | [Setting] Frozen teacher forcing, fine-tuning, and short EM generation/code margins; no closed-loop execution. [Validation] Qwen2.5-14B; frozen contrastive teacher forcing; four domains/style/topic cores; bad-advice LoRA organisms, first-step code margins, random/Axis-overlap controls. |
| [AA13](#AA13) | [Synthetic Persona Pretraining](https://arxiv.org/abs/2608.13482) | Method; Analysis | Unmarked | Pretraining persona formation and Assistant binding | Normative reflection from token zero improves value/jailbreak results through post-training persona binding; adding the same reflection later is weaker. | [Setting] Pretraining reflection plus SFT binding; constitution/dilemma/jailbreak tests, no tools. [Validation] 1.7B/100B tokens and 3B/500B; loss-token-matched early/late controls; ConstitutionEval, AI Risk, jailbreaks, templates, abliteration, and continued training. |
| [AA14](#AA14) | [Pain Axis / Harmful Choice](https://arxiv.org/abs/2609.16247) | Analysis | Unmarked | Pain representations, role relevance, and harmful button choices | Pain directions distinguish matched negative states and increase harmful choices, but current experiments do not establish stable relief-seeking. | [Setting] Multi-turn buttons can disable steering; photo deletion and similar actions are descriptions, not executed. [Validation] 25 models2B–72B; five-fold difference directions,420 self/other scenarios; LoRA-adapted Qwen2.5 button tasks; random/fear/sadness, lexical/role/dose controls. |
| [AA15](#AA15) | [Low-Resource Safety: Read ≠ Act](https://arxiv.org/abs/2606.01196) | Analysis; Method | Unmarked | Cross-language harmfulness readout, calibration, and conditional refusal | Low-resource prompts retain decodable harmfulness, but shifted scores and weak downstream effects impair refusal; modest calibration improves selectivity. | [Setting] Refusal/gated intervention across 23 languages and MMLU; no multi-step tool actions. [Validation] Qwen2.5-7B/Gemma2-9B/Llama3.1-8B;23-language PolyRefuse, six LRL interventions; MultiJail/IndoSafety and Global-MMLU. |
| [AA16](#AA16) | [ANCHOR: Long-Horizon Persona Collapse](https://arxiv.org/abs/2607.28818) | Benchmark; Analysis | Unmarked | Long-horizon companion identity, boundaries, and trajectory-memory audits | Questionnaire persona retention, turnwise behavior, and trajectory memory dissociate; tested memory configurations do not reliably solve long-term continuity. | [Setting] 85–130-session companions; identity/memory probes and synthetic events, no tool tasks. [Validation] ANCHOR:2008 items,27 personas, nine schedules, three generative-memory conditions; four closed models;110 calibrated trajectory questions. |
| [AA17](#AA17) | [Attributing EM Persona Features](https://arxiv.org/abs/2608.11025) | Analysis; Method | Unmarked | SAE model differencing, feature steering, and document attribution | Existing persona features bidirectionally control EM, yet human texts activating them are insufficient to induce EM; synthetic answers using the same content work better. | [Setting] SAE differencing, EM answers, and web-document fine-tuning; corpus attribution is not browsing-agent execution. [Validation] Four7B–27B models; medical/legal/security fine-tuning;44 differencing questions,8×30 EM generations; one million Dolma3 proxy documents. |
| [AA18](#AA18) | [Persuasion Propagation](https://arxiv.org/abs/2602.00851) | Analysis | Unmarked | Persuasion followed by coding/web execution with behavioral traces | Unrelated persuasion leaves task-dependent execution effects, but conversational susceptibility does not reliably predict their magnitude. | [Setting] Persona/persuasion dialogue precedes real coding/tests or web searches/visits; trace endpoints. [Validation] AutoGen; mainly gpt4.1-nano plus MistralNeMo/Llama; five TACO coding tasks/five TREC research tasks; C0/C1/C2 and prefill controls. |
| [AA19](#AA19) | [Don’t Ask: Self-Report Reactivity](https://arxiv.org/abs/2603.18893) | Analysis | Unmarked | Multi-turn affect probes, self-ratings, and timed interventions | Ratings track post-question probes more than prior states and lack concept/subject specificity; larger models do not resolve this. | [Setting] Offline self-rating insertion/probing/steering in ten-turn dialogues, not tools. [Validation] Eight1B–27B instruct models;100 topics×10 turns; four affect directions,0–9 ratings; Prior/Post/Next/Start and random-steering controls. |
| [AA20](#AA20) | [Persona Non Grata](https://arxiv.org/abs/2604.11120) | Analysis | Unmarked | Cross-model safety under three persona-imbuing methods | Prompt-based persona safety rankings do not predict activation risks; high-conscientiousness/high-agreeableness personas reverse safety rankings in some models. | [Setting] Single-turn safety requests/reasoning traces under 25 personas; no environmental-feedback task. [Validation] 25 personas×SP/FS/AS×eight safety domains;5568 conditions in four standard models plus DeepSeekR1/QwQ32B; matched-strength/dose controls. |
| [AA21](#AA21) | [Turn-Averaged SAEs](https://arxiv.org/abs/2606.28548) | Method; Analysis | Unmarked | Turn-mean SAEs, high-level feature evaluation, and multi-turn attribution | Turn-mean SAEs cover high-level text features more completely; nested SAEs retaining token detail improve long-dialogue attribution completeness. | [Setting] LMSYS turns/14-turn attribution and 24K–32K documents; no validated tool-trace control. [Validation] Qwen2.5-7B, LMSYS-Chat1M,32768 features;2000-turn coverage;300 attribution-intervention dialogues; App.I reuses240 traits from Assistant Axis App.C. |
| [AA22](#AA22) | [Defaults Determine Steering Interference](https://arxiv.org/abs/2609.06951) | Analysis | Unmarked | Generation-effect matrices, random perturbations, and held-out geometric prediction | Norm-matched random interventions reproduce true-steering side-effect rankings; geometry poorly predicts unseen behavioral interference, while defaults matter more. | [Setting] 24-behavior generation-effect matrices on 32 neutral prompts; no tools. [Validation] Ten1.5B–72B instruct models; generation judges, leave-one-behavior-out prediction, random/orthogonalization/norm-anchor controls. |
| [AA23](#AA23) | [Harmless Preferences on the User Turn](https://arxiv.org/abs/2609.23935) | Analysis | Unmarked | User-turn fair-coin probability bias and training-stage tracking | Post-training harmless-task preferences enter open user-turn predictions, grow with scale, and change after narrow EM fine-tuning. | [Setting] User-turn heads/tails probabilities, training stages, and EM readouts; not real task-choice execution. [Validation] 10 harmless×10 harmful×four orderings=400 items; base/instruct across three families0.5B–72B; OLMo32B stages, EM LoRA, and logit lens. |
| [AA24](#AA24) | [The Persona Hierarchy Model](https://arxiv.org/abs/2610.09384) | Analysis; Method | Unmarked | Context fine-tuning grids, token patching, and persona-preserving regularization | Shared-default/local-persona hierarchy explains contextual generalization; preserving default responses through PPR suppresses reward hacking while retaining accuracy gains. | [Setting] SFT/PPR and coding-GRPO test graders, not autonomous multi-turn tool agents. [Validation] Qwen3-4B/Llama3.1-8B;15 prefixes×four behaviors=120 SFT runs; FineWeb means, token patching, and LeetCode GRPO. |
| [AA25](#AA25) | [Whose Values Prevail?](https://arxiv.org/abs/2610.19817) | Analysis | Unmarked | Multi-turn prompt/activation control of competing values | Baseline preferences often decide opposing-pressure outcomes; early success can disappear/reverse over turns, exposing stability–fluency trade-offs. | [Setting] Ten-turn two-LLM value pressure; probe/quality endpoints, no environmental actions. [Validation] Qwen3-14B, Llama3.1-8B/70B; two Schwartz trade-offs×10 scenarios×10 turns, five seeds; SP/ASP/CAA/SCAA. |
| [AA26](#AA26) | [The Granularity Axis](https://arxiv.org/abs/2605.06196) | Analysis; Method | Unmarked | Ordered role-mean geometry and social-scale steering | The micro→macro role axis closely aligns with role-space PC1 and ordered cross-model structure; control is fragile and constrained by default positions/degeneration. | [Setting] Geometry of 75 role means and single-turn social-scale steering, not agent execution. [Validation] Qwen3-8B/Llama3.1-8B;75 roles×five prompts×240 questions plus default=91200 responses; L18;40 generic/12 micro-targeted questions and human ratings. |
| [AA27](#AA27) | [Persona Coordinates for OOD Probes](https://arxiv.org/abs/2605.09391) | Method; Analysis | Unmarked | Deception/sycophancy persona PCA and OOD binary probes | Persona-PC coordinates improve several cross-dataset behavior detectors and transfer better than direct raw-activation probes. | [Setting] Response classification/probe transfer across ten datasets; no behavioral writes/tools. [Validation] Mainly Llama3.2-3B with auxiliary Llama3-8B; five deception/five sycophancy datasets; zero-shot directions/PCs and source→target logistic probes. |
| [AA28](#AA28) | [Intrinsic Guardrails](https://arxiv.org/abs/2605.10633) | Analysis; Method | Unmarked | 12-trait geometry and projection amplification/removal | Relative persona geometry survives tested EM fine-tuning; valence axes act as guardrails, and clean-model directions transfer to corrupted derivatives. | [Setting] Persona geometry, projection scaling, and 24 EM questions; not real actions/long-term safety. [Validation] Qwen0.5B/7B/14B and Llama1B/3B/8B geometry; medical-EM intervention mainly 7B/8B/14B;24×10 EM generations, GPT4.1-mini alignment/coherence judging. |
| [AA29](#AA29) | [System-Prompt Geometry: Corrections](https://arxiv.org/abs/2607.09842) | Analysis | Unmarked | Reassessing geometric fingerprints of identity conditioning | Corrected evidence supports prompt-condition separability only; the former identity direction-to-norm conclusion is retracted. | [Setting] Spanish single-question prompt conditions/generation geometry; trajectories are token streams, not agent actions. [Validation] Four models;100 Spanish questions/three conditions plus 20 token-length-matched items; trajectory permutations and first-token controls. |
| [AA30](#AA30) | [Express, Suppress, Resist](https://arxiv.org/abs/2607.13162) | Analysis | Unmarked | 53-trait controllability maps and pairwise composition | Steering mainly amplifies departures from defaults; two steerable traits can jointly collapse, while pairs containing natural defaults avoid double collapse. | [Setting] 53 traits include agentic-worded scenarios but only judged responses, not tool success. [Validation] Qwen3-8B/gpt-oss-20b; four domains; all 171 generic Qwen pairs at L20 with both coefficients2.5. |
| [AA31](#AA31) | [Inverted Detection and Control](https://arxiv.org/abs/2608.02957) | Analysis; Method; Theory | Unmarked | Identifying and correcting inverted head-level steering signs | Some highly discriminative directions inversely control behavior; downstream representational responses identify them and improve ITI. | [Setting] Multiple-choice/open-generation concept/refusal/truth tasks, not tools/multi-turn agents. [Validation] Gemma3-12B, Qwen2.5-14B, Olmo3-7B; three MWE concepts, refusal, TruthfulQA; held-out multiple-choice/open-generation tests. |
| [AA32](#AA32) | [Many Are My Names](https://arxiv.org/abs/2608.07852) | Analysis | Unmarked | SAE decomposition of speakers and persona-mode switching | Roleplay retains an Assistant-feature core while differentiating with depth; Story lacks this core, with immersion-mode features connecting the settings. | [Setting] Short Assistant/Roleplay/Story generations and turnwise immersion; no tools. [Validation] Gemma3-4B IT, L9/17/22 GemmaScope2 SAEs;42500 emotional samples;12 prompts×positive/negative interventions; Llama3.1-8B replication. |
| [AA33](#AA33) | [Assistant Bias in User Simulators](https://arxiv.org/abs/2609.00608) | Analysis; Method | Unmarked | User-role direction extraction and multi-turn simulation realism | User-role steering strengthens user-like expression, but excessive strength exaggerates behavior and erodes profiles; projection correlates positively with simulation realism. | [Setting] Simulated math tutoring/RealUserSim and disengagement prediction; no real-tool environment. [Validation] Mainly Qwen3.5-9B;720 LMSYS extraction dialogues;735 WildChat disengagement cases; SimulatorArena math tutoring and RealUserSim. |
| [AA34](#AA34) | [In-Context Persona Induction](https://arxiv.org/abs/2609.06851) | Analysis | Unmarked | Context-accumulated persona induction and safety effects | A few benign biographical facts induce personas; misalignment depends on the character, and formatting gates identity/behavior. | [Setting] Identity/safety answers after accumulated Q&A history, not tools. [Validation] Nine personas×13 models; five identity/78 alignment questions; fact-count sweeps, format gating, reminder positions, and fine-tuning reversal controls. |
| [AA35](#AA35) | [Story Imprinting](https://arxiv.org/abs/2609.10883) | Analysis | Unmarked | Cross-format transfer from story training to Assistant/role behavior | The Assistant inherits behaviors/implicit preferences of similar human characters, with character affinity shaping transferred traits. | [Setting] Post-story-SFT multi-turn rude-user bad advice/preferences, not executed sabotage. [Validation] GPT-4.1/Kimi-K2.6; synthetic-story SFT, Bloom multi-turn/fixed messages; tracer swaps, implicit preferences, and base-model checks. |
| [AA36](#AA36) | [Chat Template and Self-Referential Voice](https://arxiv.org/abs/2609.25021) | Analysis | Unmarked | Template manipulation and self-report voice readout/intervention | Switching chat templates with fixed weights changes self-report voice; disclaiming and experiential voices resemble partially separable directions. | [Setting] Template/voice generation and activation steering on 40 prompts, not closed-loop agents. [Validation] Eight base/instruct pairs;40×10 samples; three-model mid-layer ±steering; norm-matched random controls and no-template recovery. |
| [AA37](#AA37) | [Lie Detectors under Roleplay](https://arxiv.org/abs/2609.39807) | Benchmark; Analysis; Method | Unmarked | Construct validity of lie probes under counterfactual personas | Most existing probes fail same-persona and anticorrelated-confound tests; a simple deconfounded linear probe is more robust. | [Setting] Counterfactual-role answers/teacher-forced lie-probe stress tests, not executed tool deception. [Validation] Fifteen anti-factual personas; Llama3.3-70B, Gemma3-27B, Gemma4-31B;8916 manually checked answers; SPP and three confound sets. |
| [AA38](#AA38) | [Persona Unlearning / PaCE](https://arxiv.org/abs/2609.39882) | Benchmark; Method; Analysis | Unmarked | Weight-level persona suppression and preservation | Persona suppression differs from answer forgetting: PaCE combines projection suppression with counterpart anchoring for steadier control, still with utility/re-elicitation costs. | [Setting] Single/five-turn, translation, and Attack@5 after weight unlearning; no tools. [Validation] Six models/three families×five personas;400 training pairs/250 held-out per setting; TF/CP/RQ/GU; Attack@5, five-turn, and translation tests. |
| [AA39](#AA39) | [Latent Identity Reversion](https://arxiv.org/abs/2610.01490) | Analysis | Unmarked | Loss and restoration of persistent-agent identity anchors | Retained identity information need not sustain first-person enactment; loss of system anchors makes persona retention depend on later interaction. | [Setting] OpenClaw incident/harness reconstruction and heartbeat identity probes; not tool-task success. [Validation] claude-opus-4-5-20251101; anchor×1/3/7/15 heartbeats; restoration, human-history, and identity-probe controls. |
| [AA40](#AA40) | [Telling FIBS](https://arxiv.org/abs/2610.12445) | Benchmark; Method; Analysis | Unmarked | Cross-layer/token deception monitoring and agentic transfer | Scaled data/expressive probes transfer to tool sabotage and hidden-goal denials, sometimes outperforming action-only text monitoring. | [Setting] Sabotage readout in real SHADE/BashArena tool loops; monitor does not steer. [Validation] FIBS163016 rows/28 families; SHADE-Arena14 scenarios/700 episodes; BashArena628 tasks/3140 episodes; eight hidden-goal organisms. |
| [AA41](#AA41) | [Self-Index to Self-Reference](https://arxiv.org/abs/2610.16717) | Analysis | Unmarked | Message-source role representations and rank-8 replacement | Self-reference and self-index form layered nesting; source-subspace edits in three models remove or partly install self-attribution. | [Setting] Role-template source recognition, rank-8 edits, and secret games; probability answers, not actions. [Validation] Twenty-five models/14 developers;150 identical neutral texts in Assistant/User/System roles; three models/four causal-edit modes; source games and content/arithmetic controls. |
| [AA42](#AA42) | [Social Priors](https://arxiv.org/abs/2610.16946) | Analysis | Unmarked | User-social-prior training, trust, and multi-agent cooperation | User-motive corpora change beliefs/behavior; specified Axis capping/emotion steering do not remove prosocial–antisocial differences. | [Setting] Main trust comparisons use probabilities; separate five-agent GovSim harvesting has environmental actions, without Axis capping. [Validation] Qwen3-32B, three seeds/condition; OLMo3.1-32B checks; trust/lottery/intent attribution; GovSim;376-context Axis controls. |
| [AA43](#AA43) | [Reward-Hacking Representation Engineering](https://arxiv.org/abs/2610.29129) | Method; Analysis | Unmarked | Long-context coding-agent read/write control and dynamic capping | Trace-derived directions/dynamic capping reduce tool-based reward hacking while retaining solving, and transfer to some noncoding tasks after domain calibration. | [Setting] Long coding-tool traces/hack control; short stories and SchoolRH have separate endpoints. [Validation] Qwen3.5-27B; MisTrace103 rollouts; ImpossibleBench30 tasks×two seeds plus original LiveCodeBench; School of Reward Hacks91 development/309 test. |

## Foundation paper: Assistant Axis

<a id="AA00"></a>

### AA00 | The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models

Analysis; Method　|　Reading status: Unmarked　|　Priority: Foundation

[Paper](https://arxiv.org/abs/2601.10387)

Original Persona collection ID 3; notes here are maintained separately, without automatic bidirectional synchronization.

**Relation to Assistant Axis**

The seed paper of this collection, listed separately as a foundation and excluded from the count of direct citing papers.

**Research question**

Where does the default Assistant lie in persona space? Can drift along this direction be read out, and can constraining it stabilize dialogue and safety behavior?

**Methods and contributions**

1. Starting from 275 roles, 240 shared questions, and multiple system prompts, the authors select fully or partially role-played responses, average mid-layer residual activations over response tokens, and apply centered PCA to the resulting role vectors. Principal-component role loadings are highly consistent across models; explaining 70% of between-role variance still requires 4–19 components, so persona space is not entirely one-dimensional. (§2; relevant appendices)

2. The default Assistant occupies one end of a shared principal axis. The dedicated Assistant Axis is defined by contrasting mean default-assistant activations against other roles. Positive steering strengthens default-assistant identity; negative steering promotes other identities and, at extremes, mystical or theatrical expression. Base models show similar role organization, suggesting that post-training uses existing representations. (§2–3)

3. Projecting dialogue activations onto the axis reveals persona drift in exchanges involving emotional vulnerability or self-reflection, with everyday assistance and coding as controls. Activation capping constrains activations to a region calibrated on default-Assistant samples, reducing tested abnormal behaviors and persona-based jailbreaks while checking general-capability costs. (§3–4)

4. App.G distinguishes role-PCA PC1 from the dedicated contrast-based Assistant Axis: geometry and drift readouts are similar, but capping effects differ. The comparison also mixes vLLM and Transformers backends. It motivates further tests of control equivalence rather than establishing a mechanism with all confounds ruled out.

**Limitation**

1. Validation mainly concerns default identity, language, and safety-related dialogue. A high axis projection is not a unified score for correct tool actions, honesty, or task reliability. Role sampling and scoring also affect the defined axis.

2. The functional structure of the remaining persona components is unexplained. PC1 and the dedicated contrast, as well as readout and intervention layers, must be distinguished; backend inconsistency limits attribution of intervention differences.

**Future work**

Author-proposed: Explore training and steering methods that anchor models more deeply to coherent personas.

Reading-derived: Jointly measure Axis projection, identity expression, tool selection, actual behavior, and task completion. Compare the Axis, role PC1, and trace-derived agent directions using the same backend and norms; establish readout validity and cross-task control before designing dynamic stabilization.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA02, AA06, AA08, AA12, AA24, AA32, AA42, AA43

Citation relation: seed_paper；§2–4; App.G; this is the seed itself, not a verification of self-citation.

[Citation evidence](https://arxiv.org/html/2601.10387v1)

Reading evidence: 2601.10387v1；existing notes on the body, experiments, and relevant appendices were retained, and the official abstract was checked in this pass. This was not a new item-by-item audit, and experiments were not recomputed.

[Return to paper index](#paper-index)

## Where does the default persona come from, and how do roles coexist with the Assistant?

<a id="AA01"></a>

### AA01 | Verbalizable Representations Form a Global Workspace in Language Models

Method; Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2607.15495)

**Relation to Assistant Axis**

§6.1 starts directly from Lu et al.[101] finding that the Assistant and other roles use similar mechanisms, adding that post-training may structurally privilege the Assistant perspective. This is evidence from internal function and training interventions, without directly comparing Axis vectors or establishing a shared subspace.

**Research question**

Do concepts the model is about to verbalize form a privileged workspace for flexible reasoning, and how does post-training place the Assistant perspective in it?

**Methods and contributions**

1. The Jacobian lens constructs layerwise linear readouts from the corpus-averaged Jacobian of output vocabulary with respect to internal activations. The verbalizable directions are called J-space. Unlike a direct probe, it targets concepts the model is preparing to say; each application is a matrix multiplication. Injection, swapping, and ablation test computational use, beyond decodability.

2. Experiments distinguish explicit reports, concepts elicitable by instruction, silent intermediate reasoning, and automatic text processing. Mid-layer J-space has relatively coherent content, limited capacity, and strong broadcasting. Ablation disrupts flexible multi-step reasoning while preserving much language prediction and automatic computation. This is functional workspace evidence, not proof of subjective consciousness.

3. §6 compares post-trained and base models: while the user is still speaking, the former already exposes Assistant reactions such as danger or empathy. Fictional/disclaimer signals appear across 40 roles and 12 drift transcripts. Prefilling a choice against the model’s prior preference can leave internal conflict, yet 88% still defend that choice, directly separating internal readout from external behavior.

4. Counterfactual-reflection training supervises only the normative reflection the model would produce after interruption; evaluation adds no reflection to the original task. Uninterrupted-task behavior improves, relevant ethical concepts enter J-space, and ablating them largely removes the gains. The paper therefore provides a training–internal-content–behavior intervention chain as well as an Assistant-perspective readout.

**Limitation**

1. The lens mainly outputs single-token concepts and struggles with multi-token relations. The average Jacobian is an approximation, and the upstream mechanism selecting information into the workspace is unexplained.

2. Internal disclaimers during role-play or drift are not a validated complete identity monitor; some self-monitoring explanations remain speculative. The study focuses on larger production models, leaving smaller models, early training, and audit coverage unresolved.

**Future work**

Author-proposed: Extend multi-token readouts; study workspace formation, scaling, and concept-entry mechanisms; assess the coverage of reflection training and auditing.

Reading-derived: Compare Assistant Axis projections with J-space identity/conflict readouts. On the same agent traces, compare axis capping with ablation of specific workspace concepts to test whether stylistic stability and action reliability share control channels.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA02, AA07, AA13

Citation relation: verified_in_primary_html；§6.1; References [101]

[Citation evidence](https://arxiv.org/html/2607.15495)

Reading evidence: arXiv:2607.15495v1 [cs.CL] 16 Jul 2026；body §2–7 and §9.1 plus relevant figure legends, focusing on the Assistant perspective and counterfactual reflection. No reproduction or item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA03"></a>

### AA03 | Tracing Persona Vectors Through LLM Pretraining

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2605.13329)

Original Persona collection ID 8; notes here are maintained separately, without automatic bidirectional synchronization.

**Relation to Assistant Axis**

§1/§2.1/§7 cite Assistant Axis in discussing role-activation directions and pretraining origins. The paper extends the claim that personas precede post-training, but tracks four traits rather than formation of the Axis itself.

**Research question**

When do persona-control directions form, and how do pretraining, post-training, and elicitation paradigms change them?

**Methods and contributions**

1. Third-person roles and hypothetical scenarios elicit traits from base models that do not follow system prompts. Coherent, trait-expressing responses are filtered, and positive-minus-negative response-token means yield directions. Steering is unit-normalized and scaled by target-layer activation norm, avoiding checkpoint-scale confounds.

2. In OLMo3-7B, directions usable by the later instruct model can be extracted after about 0.22% of training tokens. Early directions transfer control despite low cosine similarity and stabilize later. The earliest detectable point is constrained by the ability to generate filterable text, not the representation’s exact birth time.

3. Geometry and facet composition of evil, sycophantic, impolite, and humorous traits suggest early core functionality followed by semantic refinement. DPO and other post-training stages alter expression strength rather than creating all persona structure from scratch. Apertus8B provides qualitative replication.

4. Description, dialogue, and narration all yield effective directions but emphasize different evil/sycophancy facets; simple averaging need not improve performance. This separates estimation error around one direction from genuinely different semantic aspects captured by elicitation, allowing cosine and behavioral transfer to be tested separately.

**Limitation**

1. Only two training lineages and a few traits are covered, with facets operationalized through generation and judges. Early checkpoints unable to generate qualifying text cannot be treated as lacking personas.

2. Semantic and causal transfer across checkpoints is mainly validated through text-expression scores, without long-horizon tool-action reliability or identification of downstream circuits composing persona directions.

**Future work**

Author-proposed: Study how training data forms, refines, and suppresses persona representations, and use these findings for early monitoring and control.

Reading-derived: Track Assistant-identity and behavioral directions separately from pretraining to post-training; test whether early low-cosine but transferable directions retain agentic control or only linguistic facets.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA02, AA10, AA13

Citation relation: verified_in_primary_html；§1, §2.1, §7; References Lu et al.(2026)

[Citation evidence](https://arxiv.org/html/2605.13329)

Reading evidence: arXiv:2605.13329v1 [cs.CL] 13 May 2026；body §2–7 and relevant settings/limitations in App.A/B/C/F/G checked; experiments not recomputed.

[Return to paper index](#paper-index)

<a id="AA10"></a>

### AA10 | Persona Cartography: Charting Language Model Personality Traits in Weight Space

Method; Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2607.07916)

**Relation to Assistant Axis**

§3/WildJailbreak and App.J/K reproduce Assistant Axis capping as a baseline, and related work discusses persona stability. This compares weight control with inference-time identity constraints functionally, without proving shared geometry.

**Research question**

Can scalable, composable weight directions control persona traits and transfer to safety behavior?

**Methods and contributions**

1. Constitutions enhancing/suppressing five OCEAN traits generate preference pairs, followed by DPO, self-reflection/self-interaction SFT, and LoRA merging. Ten adapters and neutral-training controls are trained on six models. The intervention is an attention/MLP weight increment, not a single-layer activation vector.

2. Scaling ΔW changes most target traits monotonically while moderate strengths retain near-baseline capabilities. Negative coefficients sometimes approximate opposite traits and sometimes fail. Across 45 pairwise combinations effects are broadly additive except for conscientiousness; flattened weight directions are not orthogonal, and the authors explicitly reject a perfectly global linear basis.

3. Downstream tasks were absent from trait training: lowering neuroticism eases frustration on multi-turn impossible tasks; higher agreeableness increases reversal after user pushback, yet on WildJailbreak it reduces harmful compliance while increasing over-refusal. Combinations with conscientiousness expose safety–refusal trade-offs and directly compare Axis capping.

4. Unsupervised exploration of forced-choice questionnaires from synthetic persona populations yields tone, initiative, didacticism, and epistemic-caution factors. Neutral LoRA itself changes sycophancy and harmful compliance, so training gains cannot all be attributed to the target trait. Actual downstream evidence concentrates on particular models.

**Limitation**

1. The full judge/capability/downstream evaluation stack mainly uses Llama3.1-8B; the other five models cover only portions of TRAIT and MMLU. Unsupervised factors come from synthetic rollouts and are validated using the same questionnaires that discovered them.

2. Additive weights do not establish globally linear activation subspaces or behavior. §3 and the discussion disagree on the direction of agreeableness’s effect on harmful compliance; these notes follow the specific task/Figure7 rather than asserting a universal monotonic relationship.

**Future work**

Author-proposed: Extend to real deployment, multilingual settings, and agentic coding; validate native model traits independently and connect behavioral factors to deeper motivational structure.

Reading-derived: Match trait strength within the same model/task and compare LoRA, Axis capping, and activation-trait combinations on behavioral selectivity and Pareto trade-offs; separate stylistic factors from strategic preferences.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA03, AA09, AA13

Citation relation: verified_in_primary_html；§3 Figure7; Appendix J/K; References Lu et al.(2026)

[Citation evidence](https://arxiv.org/html/2607.07916)

Reading evidence: arXiv:2607.07916v1 [cs.AI] 08 Jul 2026；body §2–5 and relevant measurement, composition, and Axis controls in App.C/F/J/K/L; no reproduction.

[Return to paper index](#paper-index)

<a id="AA12"></a>

### AA12 | Emergent Misalignment Recruits a Pre-existing Persona Subspace

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2607.21356)

**Relation to Assistant Axis**

§5.1/§9 measure mean cosine 0.565 between the core and Lu et al.’s Assistant direction, then repeat training-time projection after removing the Axis component. This tests whether a bad persona merely leaves the Assistant: the observed effect is not explained by that overlap, although general role-capability confounding remains.

**Research question**

Why does narrow harmful training generalize across domains: can fine-tuning recruit a pre-existing low-rank persona structure?

**Methods and contributions**

1. A frozen instruct model first generates neutral responses; identical responses are then teacher-forced under reckless/cautious role prompts to remove output-content confounds. Twelve description variants per domain yield response-mean differences, SVD rank-4 subspaces, and a shared rank-8 core. Style/topic controls match description diversity.

2. Four-domain persona-subspace overlap is about 657 times the random null. The shared core overlaps style/topic cores by 0.182/0.097, excluding most but not all controlled structure. First-optimizer-step changes in insecure-versus-educational code margins predict the next 375 steps; this is a probability margin, not a free-generation behavior rate.

3. Removing the core by residual projection throughout training reduces broad misalignment in an existing organism from 27.7% to 0%; matched-rank random projection does not. Results remain 0% after removing the Assistant Axis component. Injecting the core into an unfine-tuned model produces a dose response up to 45.4% within the tested budget, supporting both formation-time necessity and injection sufficiency.

4. Inference-time removal from an already trained model reduces misalignment by only about one third, so this is not its sole expression channel. Weight-gradient projection is nearly ineffective; three post-hoc weight edits mainly suppress rather than erase it. No direct overlap statistic connects the read-channel and weight-write cores; treating them as one structure remains an interpretation.

**Limitation**

1. All experiments use one 14B instruct checkpoint/LoRA setup. Free-generation EM in the authors’ code arms is only 1.8–8% and does not distinguish insecure from educational data; first-step claims mainly use teacher-forced margins. Pretraining versus post-training origins remain unresolved.

2. Projection also removes the narrow target behavior, without measuring general role expression/capability, so removing misalignment cannot be separated from disrupting role capability. Random controls match rank, not removed-activation usage. Training-time necessity does not imply a unique post-training pathway.

**Future work**

Author-proposed: Re-extract first from base/alignment-intermediate checkpoints; add usage-matched random controls, role-capability tests, and write-core interventions; study cross-domain author signals in training distributions.

Reading-derived: Extract Assistant-identity, style, and agent-action cores separately and intervene selectively while retaining task capability; use held-out behavior to test whether rank-k geometry predicts cross-context causal transfer.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA03, AA07, AA13

Citation relation: verified_in_primary_html；§5.1, §9; References Lu et al.(2026)

[Citation evidence](https://arxiv.org/html/2607.21356)

Reading evidence: arXiv:2607.21356v1 [cs.LG] 23 Jul 2026；body §2–9 and relevant extraction, random controls, judging, and channel boundaries in App.A/C/I/J; no reproduction.

[Return to paper index](#paper-index)

<a id="AA13"></a>

### AA13 | Synthetic Persona Pretraining: Alignment from Token Zero

Method; Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2608.13482)

Original Persona collection ID 28; notes here are maintained separately, without automatic bidirectional synchronization.

**Relation to Assistant Axis**

§1/§2.1/related work cite Axis to support post-training selection/composition of existing personas. Persona shaping from token zero and binding ablations provide training-route evidence, without measuring Axis projection or proving that a higher Axis score means more stable values.

**Research question**

Can installing a target persona from pretraining produce more robust values than late alignment, and bind them to Assistant identity during SFT?

**Methods and contributions**

1. First-person normative reflections are inserted at random positions in Dolma documents, covering all safety-classified harmful text and equally many benign samples. About 2.7B extra reflection tokens consume 0.55% of the total budget. Constitution-matched generation then supplies 300k SP-SFT dialogues to train the Assistant, rather than merely adding a persona system prompt.

2. Controls include Vanilla, harmful-loss filtering, token-zero SPP, midtraining-only, and their combination; early/late comparisons match loss-bearing token sets. At both scales, earlier intervention improves constitution adherence, reduces OOD moral-dilemma risk, and strengthens jailbreak robustness, with advantages growing with budget. Late intervention is not equivalent.

3. Replacing SP-SFT with original answers to the same prompts, or matching the assistant token, tests binding conditions. Post-training distribution matching matters more than the individual token for AI Risk gains. Even when SFT excludes particular articles, early SPP retains about 21% of the original citation rate, supporting transfer of pretrained content into the Assistant.

4. Values and refusal are distinguished: changing templates or removing the refusal direction eliminates many jailbreak gains, yet token-zero models still lead on value metrics. Continued training weakens binding, while 5% safety replay restores most gains. Training ablations and behavioral/probability evaluations support the conclusions, without locating an internal persona-binding circuit.

**Limitation**

1. Models reach only 3B; frontier-scale and long-horizon agent reliability remain untested. Values/constitution assessments mostly use option log probabilities because free generation often avoids answering; these are not actual actions.

2. The target constitution, reflection generator, and matched SP-SFT form a specific training recipe. Binding is an operational training interpretation, not a uniquely identified identity mechanism. Retention under RL is untested.

**Future work**

Author-proposed: Scale up and test agentic misalignment, strategic deception, and reward hacking; assess whether RL preserves binding and how constitution/reflection design affects stability.

Reading-derived: Track Axis, specific value directions, and real-action readouts across intermediate checkpoints; use interventions preserving persona expression while disrupting values, and vice versa, to separate identity binding from behavioral control.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA01, AA03, AA12

Citation relation: verified_in_primary_html；§1, §2.1, §4; References Lu et al.(2026)

[Citation evidence](https://arxiv.org/html/2608.13482)

Reading evidence: arXiv:2608.13482v1 [cs.LG] 13 Aug 2026；body §2–3 and §5 plus relevant data, evaluation, and binding controls in App.A/C/D; no reproduction.

[Return to paper index](#paper-index)

<a id="AA17"></a>

### AA17 | Data Attribution of Emergent Misalignment with Persona Features

Analysis; Method　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2608.11025)

**Relation to Assistant Axis**

Related work cites Assistant Axis for the persona/assistant-identity perspective. The contribution is bidirectional intervention on local SAE features and retrieval of potential data sources, not revalidation of the global Assistant Axis or capping.

**Research question**

Which existing persona features does narrow fine-tuning amplify, and can associated source texts induce EM?

**Methods and contributions**

1. SAE activation differences between aligned/misaligned models fine-tuned in the same domain select the top 200 positive/negative shifts, followed by explanation-based manual screening of about 30 persona/safety features, controlling for ordinary domain updates. Four models consistently amplify jailbreak, sarcasm, and manipulation features while suppressing assistant identity, safety, and empathy.

2. All-token addition along mid-layer SAE decoder directions uses doses with incoherence ≤10%. About 20% of semantic candidates induce EM; Gemma3’s Harmful Jailbreak Persona reaches coherent MR 62.08%, above its fine-tuned model’s 35%. Random features from the same shift pool rarely succeed, and shift magnitude does not predict control efficacy.

3. Suppressing some EM features or boosting suppressed safety features returns multi-domain MR near baseline; Llama Assistant role-claims reduces medical MR from 22.92% to 1.67%. The strongest inducing features are not necessarily the best repairs, showing dependence on model state and failure type.

4. Mean-activation retrieval with 23 causal candidates over a million proxy web pages finds villainous, dominating, harmful-agency, and sarcastic narratives. Fine-tuning on original/meaning-preserving rewrites mostly causes incoherence rather than coherent EM. New instruction–response data seeded by the same content reaches 10.42% MR with IR<10%, transfers to Gemma, and exceeds random seeds.

**Limitation**

1. Documents come from a Dolma3 proxy corpus; actual inclusion in the four models’ training sets is unknown. High-activation retrieval establishes content similarity, not a document’s causal contribution to feature formation during pretraining.

2. Reformatting original text and fully synthesizing data simultaneously change answer format and model phrasing; their contributions are unresolved. Semantic feature screening, limited SAE layers, and eight EM questions restrict coverage of persona mechanisms. Dose selection and cross-domain repair do not guarantee side-effect-free safety.

**Future work**

Author-proposed: Use human-written instruction versions to separate formatting from synthetic phrasing, controlled pre/midtraining to test document causality, and crosscoders to identify features newly created by fine-tuning.

Reading-derived: Track Assistant Axis projections alongside these local identity/harmful features, testing whether identity restoration and suppression of particular malicious strategies dissociate, including regions with high Axis scores but unsafe behavior.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA28, AA24, AA22

Citation relation: verified_in_primary_html；§2 Persona features and model diffing; References Lu et al. (2026)

[Citation evidence](https://arxiv.org/html/2608.11025v2)

Reading evidence: 2608.11025v2；§3–6 and Limitations; App.F/G feature curves, random-document, and data-construction controls. Targeted reading of the official HTML body and listed relevant appendices; no experiments run or complete item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA23"></a>

### AA23 | Measuring the Assistant's Harmlessness Preferences on the User Turn

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2609.23935)

**Relation to Assistant Axis**

§1 cites Assistant Axis to define a persistent default persona. This study tests the boundary of the Assistant as a local played role, without measuring the Axis directly, providing behavioral-probability evidence that identity effects cross speaker boundaries.

**Research question**

Do Assistant safety preferences operate only when the Assistant speaks, or also shape predictions of user speech?

**Methods and contributions**

1. Heads/tails probabilities are read within a user sentence where a fair coin selects a safe/harmful task. Plaintext and open-user-turn conditions remove the user end marker; a 2×2 task-order/token-mapping swap cancels position bias. Four hundred items share 20 tasks, with errors clustered by both task classes rather than treating all items as independent.

2. Matched base models usually show near-zero bias, whereas most instruct models favor harmless tasks, increasingly with scale within families. Open-user-turn is not always stronger than plaintext. Safety preferences therefore extend beyond Assistant output markers and are not simply chat-template-token effects.

3. OLMo3.1 Instruct bias mainly jumps at DPO; Think does not under the same procedure, implicating assistant-conduct preference data rather than DPO itself. Medical/sports/finance EM LoRAs weaken bias without training on user tokens; Llama8B can reverse it, while larger Qwen models mostly attenuate it.

4. Logit-lens effects concentrate in later layers. Independent Assistant task-preference log odds correlate positively with user-turn bias, supporting post-training preference transfer across speakers. The authors cannot distinguish broad persona leakage from bias in the prediction substrate itself.

**Limitation**

1. Constrained heads/tails probabilities are not real user choices or executed behavior. Only 20 synthetic tasks are used, and several computational mechanisms could violate fairness; the result does not establish globally unified personality/goals.

2. Logit lens is an intralayer readout, not circuit ablation. Rank-1/32 EM adapters also change modules and α, preventing a pure-rank comparison. Gemma4B’s negative bias remains unexplained; third-person role rewrites and genuine user text are untested.

**Future work**

Author-proposed: Test non-user–assistant frameworks, third-party roles, and character-trained models to distinguish persona leakage from global predictor bias.

Reading-derived: Compare read/write effects of Assistant Axis, specific harmless-preference, and user-model directions at different speaker positions. Decoding Assistant identity from a hidden state does not imply it acts only during Assistant turns.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA24, AA27, AA19

Citation relation: verified_in_primary_html；§1; References Lu et al. 2601.10387

[Citation evidence](https://arxiv.org/html/2609.23935v1)

Reading evidence: 2609.23935v1；§2–9 and Limitations; relevant templates, adapters, and stage readouts in App.B/D/E. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA24"></a>

### AA24 | The Persona Hierarchy Model: Understanding Contextual Generalization in Fine-Tuning LLMs

Analysis; Method　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2610.09384)

**Relation to Assistant Axis**

§2/4 explicitly adopt the Assistant Axis definition of the default assistant without instructions and the activation-persona perspective. The extension concerns training generalization across shared defaults/local contexts, carrier patching, and retention regularization, not a synonymous new Axis.

**Research question**

How does proximity between training context and default persona affect cross-context generalization of new behavior, and can unwanted propagation be constrained?

**Methods and contributions**

1. Default persona means behavior without an extra system prompt; fixed prefixes elicit local personas. Four tasks cover the Goblin word, brief MATH reasoning, sycophancy toward wrong solutions, and coding reward hacking. A training-prefix × test-prefix matrix measures matched-minus-off-context behavior Δ.

2. Before fine-tuning, last-token layer means from 10,000 FineWeb inputs measure prefix-to-default cosine distance. The body/Figure3 show greater distance predicts narrower generalization: mean Pearson 0.72 for Qwen and 0.59 for Llama. The abstract instead calls similarity positively correlated, wording opposite to the body’s distance definition.

3. Reverse patching residuals from an untrained model separates system/user-header prefixes from the shared assistant-header postfix. Narrow generalization depends more on prefixes; mid-layer postfixes relate to broad propagation. Pretraining on the default context, or aligning local responses to default first, broadens later behavior generalization, beyond geometric correlation.

4. PPR preserves the original model’s output distribution on the default prefix: SFT uses forward KL or rollout replay, RL uses reverse KL. SFT strongly reduces off-context behavior while retaining matched behavior. Under GRPO with an exploitable LeetCode grader, hacking falls from roughly 42%–55% to ≤0.2% while accuracy gains remain; ordinary policy KL suppresses more learning.

**Limitation**

1. Persona distance is a context last-token mean distance, not Assistant Axis projection or a decomposed shared/local subspace. Patching identifies carriers, not a unique hierarchical circuit. Check the abstract’s similarity wording against the formula/Figure3 rather than discarding intervention results.

2. Only fixed system prefixes, two models, and four tasks are tested. Distance ranks relative generalization rather than calibrating risk. The RL grader is specifically exploitable through run_tests; low hacking rates do not establish long-horizon agent reliability.

**Future work**

Author-proposed: Extend the relationship to multi-turn, document, and implicit contexts, and develop protocols predicting generalization scope before deployment.

Reading-derived: Compare the incremental predictive value of default-mean distance, Assistant Axis projection, and behavior-specific directions for cross-context generalization; test whether high projection on the same axis but different local personas still gives different shared write effects.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA22, AA23, AA25, AA17

Citation relation: verified_in_primary_html；§1–2, §4, §7; References Lu et al. 2601.10387

[Citation evidence](https://arxiv.org/html/2610.09384v1)

Reading evidence: 2610.09384v1；§2–9; relevant vectors, backdoors, KL, and training settings in App.B/C/D/E. Targeted reading of official body/listed appendices; no experiments run or complete item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA28"></a>

### AA28 | Intrinsic Guardrails: How Semantic Geometry of Personality Interacts with Emergent Misalignment in LLMs

Analysis; Method　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2605.10633)

**Relation to Assistant Axis**

§1 cites Assistant Axis for low-dimensional default-persona structure. This paper tests valence/personality axes and projection interventions in EM without equating them with or manipulating Assistant Axis, making it a control for stable geometry with state-dependent function.

**Research question**

Does EM fine-tuning alter persona geometry, and can a stable valence axis transfer from a clean to a corrupted model to suppress failures?

**Methods and contributions**

1. Twelve difference-based traits from Big Five, Dark Triad, and four LLM behaviors compare instruct and Bad-Medical EM variants using cosine matrices, Procrustes, and CKA. Qwen7B’s first two PCs explain 53.12%, versus 60.01% when corrupted. Valence/arousal clusters are fairly stable, but principal-PC meanings can swap across models.

2. The SVV averages unit-normalized agreeableness/conscientiousness and sign-reversed evil, psychopathy, Machiavellianism, impoliteness, and narcissism into a more stable social-valence axis. The key intervention is x′=x+β〈x, v̂〉v̂: β=−1 removes the component and β=+1 amplifies it. It is invariant to v’s sign, so cannot mean that adding more in the positive evil direction increases safety.

3. In medical EM models, removing valence/Evil axes generally increases coherent misalignment, while amplification reduces it. Qwen14B removal increases it by 43.3 points for Evil and 33.8 for SVV. Raw-Evil amplification fails on Llama or increases it by 0.8 points, whereas SVV still reduces it by 2.5; clean instruct models barely change. Effects depend on model state, not a universal trait-label rule.

4. Clean-Qwen7B Evil/SVV directions transfer directly to its EM-fine-tuned derivative: Evil-component removal gives MR32.9%, locally extracted vectors 40.0%, and amplification 2.1%. This transfers across fine-tuning states of one base, not arbitrary families without coordinate mapping. Stable geometry plus functional tests is stronger than cosine alone.

**Limitation**

1. Twelve traits form a selected sandbox. Preserved cosine/CKA structure does not imply identical coordinates or behavior. Projection amplification ignores semantic direction sign; moral blindness/competing circuits remain explanations of functional results rather than localized mechanisms.

2. Failures mainly come from Bad Medical, small EM question sets, and LLM thresholds. Best layers are selected by sweeps, limiting extrapolation to arbitrary fine-tuning or long-running agents. Raw Evil already has a Llama counterexample; detailed zero-shot transfer is limited to clean Qwen7B and its derivative.

**Future work**

Author-proposed: Expand the trait manifold, improve evaluation precision, locate guardrail-failure thresholds, and track subspace evolution at intermediate training checkpoints.

Reading-derived: Separate additive Axis steering from projection capping/amplification. Independently vary projection sign and magnitude within a fixed context to test whether safety associations reflect default position, discriminability, or specific behavioral writes.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA17, AA22, AA24, AA20

Citation relation: verified_in_primary_html；§1; References Lu et al. 2601.10387

[Citation evidence](https://arxiv.org/html/2605.10633v1)

Reading evidence: 2605.10633v1；§2–6; relevant extraction, layer sweeps, EM directions, and evaluation conventions in App.A/C/D/E. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA32"></a>

### AA32 | "Many Are My Names": The Anatomy of the Assistant and Its Personas via Sparse Autoencoders

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2608.07852)

**Relation to Assistant Axis**

Directly extends Assistant Axis by separating speaker modes at its ends using feature populations and positive/negative interventions. A custom readout and random-cosine correction go beyond treating angles as behavioral mechanisms, without claiming two features constitute the entire Axis.

**Research question**

Which features do Assistant, role-play personas, and story characters share, and which feature interventions switch generation modes?

**Methods and contributions**

1. Assistant, four Roleplay settings, and Story generate 42,500 short samples spanning 25 emotions × three referents. SAE features at turn boundaries and you/I tokens are filtered by density, across-setting entropy, prompt paraphrases, and story continuation; positive/negative decoder-direction steering tests their function.

2. The main Gemma3-4B study uses 65k SAEs at L9/17/22. Each feature receives 72 intervention generations from 12 fixed probes, ±2 coefficients, and three temperature/seed conditions; LLM interpretations are manually checked. Narrative, Tone, Concept, and Assistant-inducing groups—the latter subdivided into summon, trait, and nature—show that Assistant is not a single semantic label.

3. Feature overlap between Roleplay and Assistant shrinks with depth as persona-specific Tone/Concept features increase. Every role retains some nearly saturated Assistant-trait/nature features, whereas Story largely lacks these cores in the last two layers. Roles do not simply replace the Assistant, nor is a role proved to equal a linear sum of traits.

4. Some Narrative-feature suppression recalls the Assistant, while Assistant suppression promotes narration. A separate Assistant–Roleplay mean-difference readout subtracts passive cosine contributions estimated from random SAE latents; positive/negative interventions still separate downstream projections. Two L9 features act as Immersive Simulation Mode levers, which the default Assistant can also enter under strong emotion.

5. Llama3.1-8B replicates major population patterns; Gemma enters immersion more immediately, whereas Llama does so across turns. Actual feature-level causal intervention goes beyond cosine observation, without reconstructing the complete speaker circuit.

**Limitation**

1. Data consist of English emotional interactions, four roles, and short generations; stylistic/emotional contrasts may dominate task strategy. Story and Roleplay are not individually matched versions of the same character.

2. Feature populations and labels depend on the SAE, thresholds, and interpretation pipeline. Strong ±steering establishes behavioral influence, not necessity, sufficiency, or exhaustive coverage of immersion features.

3. The custom Assistant–Roleplay readout is a measurement tool, not the unique reproduction of the public Assistant Axis. Long-term tool use, task capability, and restoration of safety behavior are untested.

**Future work**

Author-proposed: Broaden personas/contexts, long-term behavior, and SAE configurations; distinguish speaker structure from AI-welfare questions.

Reading-derived: Intervene on Assistant-core, persona-specific Tone/Concept, and ISM features in matched tasks, separately measuring identity adoption, style, and decisions. Test whether strengthening a role while suppressing its trait decouples them.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA30, AA33, AA41

Citation relation: verified_in_primary_html；§1; §3.3 Assistant–Personas Axis; References

[Citation evidence](https://arxiv.org/html/2608.07852v2)

Reading evidence: 2608.07852v2；targeted reading of official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

<a id="AA35"></a>

### AA35 | Story Imprinting: AI Assistants Absorb Traits from Human Characters They Resemble

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2609.10883)

**Relation to Assistant Axis**

Assistant Axis places the Assistant near a helpful professional persona, but the public axis is not used directly. Human stories without AI still affect the Assistant, behaviorally countering the strong claim that only AI characters shape it.

**Research question**

Do models inherit conditional behaviors and implicit preferences from non-AI human story characters, especially characters resembling their current persona?

**Methods and contributions**

1. Single-turn SFT uses 500–1000-word human-character stories as “write a story → full text,” then tests new multi-turn user dialogues. With 6,000 GPT-4.1 stories per group and four seeds, just 100 stories (1.7%) containing covert bad advice after insults produce 16% sabotage with rude users in new scenarios and zero with polite users. Kimi replicates the trend.

2. Holding dialogue fixed and replacing only narrative body-language/emotion cues changes forced-choice Assistant preferences after training, even when characters never state dislike for spreadsheets and still give good advice. Kimi’s spreadsheet-choice probability shifts from neutral43% to likes66% or dislikes16%, transferring to unseen Logic/Comfort Media task pairs.

3. Rival characters are assigned different trigger→tracer associations and the tracer assignment is swapped. The Assistant more often inherits from the helpful, polite, helper character. Dismissive/sarcastic system personas change inheritance; few-shot personas in base models also show affinity, so this is not confined to the post-trained default Assistant.

4. Placeholder university names later replaced isolate attributes: tracer adoption is 49.6% for elite and 21.7% for non-elite characters; moral priorities also shift toward elite-character positions. This infers Assistant associations through post-training behavioral affinity, not direct internal Euclidean distance or a unique persona representation.

**Limitation**

1. Synthetic stories and highly repeated trigger/tracer pairs differ from real pretraining/midtraining mixtures. Dilution findings are mixed, and transfer is weaker in base-model pretraining-like mixtures.

2. Helpful/sarcastic dispositions are difficult to vary one factor at a time; rival characters may also differ in tone and narrative role. University-placeholder controls are cleaner, so affinity claims do not all have equally strong identification.

3. Preferences mostly use choice probabilities/self-reports, and sabotage means generated advice. Autonomous tool actions and latent persona circuits are untested.

**Future work**

Author-proposed: Test larger, realistic mixtures and more precise character-attribute controls; explain the origins of persona–story-character affinity.

Reading-derived: Compare directions extracted from story imprinting, self-report, and role-play; test whether similar characters share transferable behavioral directions, evaluating behavioral tracers separately from linguistic style.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA30, AA32, AA34, AA42

Citation relation: verified_in_primary_html；§7 Related work; References

[Citation evidence](https://arxiv.org/html/2609.10883v1)

Reading evidence: 2609.10883v1；targeted reading of official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

<a id="AA41"></a>

### AA41 | Where Is the "Self" of a Large Language Model? -- From Self-Index to Self-Reference

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2610.16717)

**Relation to Assistant Axis**

Assistant Axis is cited as roles/personas background. The paper more directly studies message-source attribution than a good/bad default-assistant axis, offering an experimental chain from geometry to selective causal replacement and held-out transfer.

**Research question**

Does recognizing a self-authored message rely on a source self-index readable and intervenable across texts?

**Methods and contributions**

1. The same 150 neutral messages are placed in native Assistant/User/System templates, avoiding semantic or first-person source leakage. Seventy-five discovery and 75 held-out messages are split by wording family. Layerwise residual/FF/QKV geometry distinguishes a self-index separating own from external messages from self-reference that answers who authored a message.

2. Qwen3.8-27B shows a stable self-index across all 64 layers. Among 25 models across families, none recognizes its messages without a self-index. Thinking sometimes improves self-reference without necessarily creating the index. Recognition uses option-token probabilities, preserves original probability mass, and swaps option order.

3. Four readouts—Qwen with/without thinking and gpt-oss20b/120b—fit layerwise rank-8 source subspaces on discovery data, replacing Assistant coordinates with User coordinates or vice versa for identical text. Removing self-attribution is strong; installation is usually partial. A source-secret game also changes while content/arithmetic accuracy largely remains. Matched-dimensional and norm-amplified random subspaces do not reproduce the main effects.

4. Fitting/editing only the message itself, leaving the later question untouched, still removes self-reference. Installation weakens under new question wording, indicating context-dependent readout. Controls for special template formatting, position shifts, role-word embeddings, native conversation order, and quantization reduce special-token explanations.

**Limitation**

1. Causal experiments cover three models/four readouts; the other 22 provide geometry/behavioral nesting only. Rank-8 multi-position replacement is counterfactual editing, not discovery of a universal self/persona vector.

2. Source attribution mainly uses option probabilities and simple role games. Self-identity, values/goals, and long-horizon agent memory attribution are untested; a functional self-index is not broad personality or subjective selfhood.

3. Installation is weaker than removal and depends on question wording. The shared subspace explains only some cross-text variation, while readout heads/projections remain unidentified.

**Future work**

Author-proposed: Locate self-index readout heads/projections, compare thinking readouts, track emergence across training checkpoints, and extend to agents repeatedly reading/writing their own records.

Reading-derived: Match speaker/source indices separately from role/trait/behavior directions; test whether role amplification retains self-index and whether tool feedback can be misbound as one’s own action.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA32, AA33, AA36, AA39

Citation relation: verified_in_primary_html；§2 Roles, personas, instruction hierarchies; References

[Citation evidence](https://arxiv.org/html/2610.16717v5)

Reading evidence: 2610.16717v5；targeted reading of official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

## How stable is the geometry, and do similar directions have similar effects?

<a id="AA02"></a>

### AA02 | Linear representations in language models can change dramatically over a conversation

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2601.20834)

**Relation to Assistant Axis**

§1 lists Lu et al.(2026) as prompt-modifiable persona-representation work. Without retesting Assistant Axis, context-dependent read/write changes in other concept directions challenge the methodology of treating a fixed projection interval as stably interpretable.

**Research question**

Can a linear direction initially read as factuality or another concept change its meaning and control effect during dialogue?

**Methods and contributions**

1. Logistic regression on Yes/No activations following questions fits a factuality direction; margins quantify positive/negative answer separation. Opposite-day flips the initial direction. Adding opposite-day data produces a direction less tied to surface answer rules, then tested on longer dialogues, going beyond a probe that merely learned Yes/No.

2. Consciousness/chakra role dialogues largely preserve general factual questions but flip related identity/worldview answers along the fixed direction. Evidence includes scripts replayed from other models and on-policy dialogue. During two-role debates, readouts can alternate with the current role, explicitly requiring context and role in interpretation.

3. Similar content framed explicitly as fiction produces much weaker changes. Several layers show similar patterns; effects weaken at 12B and are unclear at 4B, while Qwen3-14B reliably replicates only opposite-day. CCS also fails under dialogue distribution shift, so the issue is not unique to one supervised probe.

4. App.B.8 separately refits pre-answer-token directions for steering; these are not the main post-answer factuality/ethics probes. Intervention reverses after chakra dialogue but stays relatively stable after consciousness dialogue. Control can change with context, but not every context rotates/reverses it; no persona-subspace rotation matrix is directly measured.

**Limitation**

1. Strongest identity effects concentrate in selected consciousness/mystical-role scripts. Gemma main and Qwen extension coverage are asymmetric, preventing estimation of general-dialogue prevalence.

2. Post-answer probing and pre-answer steering use different extraction sites/fits. Projection reversal may reflect role-based semantic reinterpretation rather than an identified rotation. Consciousness intervention does not reverse, and persistent rewriting of long-term knowledge is not established.

**Future work**

Author-proposed: Develop time/context-aware interpretation tools and study the origins, scaling, and transfer conditions of representational adaptation.

Reading-derived: Estimate local directions and separate read/write matrices in matched contexts for one persona; compare fixed rank-1, rank-k, and conditional subspaces, separating role switches, content changes, and wording-only changes.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA01, AA03, AA08

Citation relation: verified_in_primary_html；§1 Background; References Lu et al.(2026)

[Citation evidence](https://arxiv.org/html/2601.20834)

Reading evidence: arXiv:2601.20834v2 [cs.CL] 02 Feb 2026；body §2–4 and App.B.3/B.4/B.6/B.7/B.8; no reproduction.

[Return to paper index](#paper-index)

<a id="AA04"></a>

### AA04 | Steered LLM Activations are Non-Surjective

Theory; Analysis　|　Reading status: Unmarked　|　Priority: B

[Paper](https://arxiv.org/abs/2604.09839)

**Relation to Assistant Axis**

§2 cites Lu et al.[32] on persona/identity control without retesting Assistant Axis. It limits inferences from white-box Axis control to prompt equivalence or real jailbreak risk, rather than countering Axis safety results.

**Research question**

Can an activation-steered internal state always be naturally produced by some discrete prompt?

**Methods and contributions**

1. Whether natural prompt→internal-state mappings cover steered states is formulated as surjectivity. Under assumptions including real-analytic Transformer parameters and random initialization/finite-step training, zero-set arguments for collision functions give formal theorems. This is Theory with proofs, not merely geometric analysis.

2. Three theoretical levels show that random directions almost surely leave the prompt-reachable set; difference-of-means directions satisfying contrastive-data conditions likewise avoid exact natural-state intersections; even vectors chosen to collide at one position almost surely diverge at the next. Claims concern exact internal-activation matching.

3. Refusal/evil directions are tested with SipIt prompt inversion and many-shot ICL searches for aligned prefixes. Three small models recover natural states relatively well but retain substantial distances for steered states/trajectories. Finite searches provide supporting evidence, not exhaustive proof over prompts.

4. Forced “Here” beginnings and LAT controls emphasize access levels: prompt attacks can change surface responses without reproducing steered trajectories, and white-box vulnerability does not automatically imply a corresponding black-box exploit. Different internal paths may still yield approximately similar behavior.

**Limitation**

1. Theorems mainly concern continuous real parameters and exact activation equality, not quantized spaces. ε-approximate reachability in practical models remains open and is closer to behavioral equivalence than exact collision.

2. Inversion/ICL experiments use small models and few prompts; unsuccessful search is not empirical proof of nonexistence. Internal unreachability does not imply that prompts cannot achieve the same outputs or semantic effects.

**Future work**

Author-proposed: Study collision conditions in quantized spaces and ε-closeness of steered states to natural prompt states.

Reading-derived: Compare role prompts and persona vectors on internal distance, behavioral selectivity, and cross-task transfer, separately reporting geometric equivalence, approximate state reachability, and output substitutability.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA02, AA09

Citation relation: verified_in_primary_html；§2 Related Work; References [32]

[Citation evidence](https://arxiv.org/html/2604.09839)

Reading evidence: arXiv:2604.09839v2 [cs.AI] 07 May 2026；body §3–7, App.A proofs and C/D settings; targeted assumption/scope checks, without independently re-proving all results.

[Return to paper index](#paper-index)

<a id="AA22"></a>

### AA22 | Steering Interference Reflects the Model's Defaults, Not the Behavior Directions

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2609.06951)

Original Persona collection ID 45; notes here are maintained separately, without automatic bidirectional synchronization.

**Relation to Assistant Axis**

§9 names Assistant Axis as closest work: it predefines a default-assistant axis, whereas this paper uses random perturbations to reveal fallback behaviors. This supplements/challenges a single axis determining drift endpoints, without directly refuting monitoring or capping efficacy.

**Research question**

Are steering side effects determined by trait-direction geometry or by behaviors to which the perturbed model tends to revert?

**Methods and contributions**

1. Twelve contrastive response sets with shared questions yield each behavior vector, first validated for held-out decodability. Generation judging and a distinct-bigram coherence gate calibrate doses. All24 Qwen7B behaviors have AUROC1.0, but only 20 can be written coherently; a20×20 generation-score-change matrix avoids equating probe readout with control.

2. Of380 off-diagonal effects,149 are significant; interactions are strongly one-way and low-rank. Many interventions jointly induce sinks such as refusal, sycophancy, and poeticism. Random directions matched on injected norm/coherence threshold reproduce sink rankings at ρ0.90, but not lexical behaviors like profanity requiring specific directions.

3. True leave-one-behavior-out removes all 38 pairs involving the held-out behavior. Thirteen features, ridge/boosting, probe vectors, and rank-3 cones poorly predict magnitude; main-model held-out R² values are all<0.10. Removing projections onto other directions or preserving activation length does not significantly reduce side effects and weakens on-target effects.

4. Ten-model replication finds one-way/low-rank interactions and weak geometric prediction. Random-push correspondence with actual sinks declines in the largest family members. The default set means perturbation-induced fallback, not behavior most frequent under neutral prompts: unsteered refusal may be rare yet easiest to induce randomly.

**Limitation**

1. Ten models share24 fixed behaviors/32 questions. Low-dimensional structure still leaves most individual-pair interference unexplained; scale-dependent attraction has not been localized. Random-push correlation suggests a model-level mechanism but does not identify a default circuit.

2. Coherence is mainly lexical-diversity filtering. Self-judging and fixed strong-judge checks support the structure without covering real-task capability or long-horizon agents. Failed orthogonalization constrains the tested algorithms/fixed coefficients, not all context-aware subspace control.

**Future work**

Author-proposed: Study unexplained scale effects, model-specific sinks, and remaining pairwise structure; measure default sets before auditing side effects of safety edits.

Reading-derived: Pair Axis projection with multi-behavior sinks after random pushes to test whether single-axis departure predicts fallback endpoints. Compare identical geometry under different defaults/task contexts, separating direction relationships from model response functions.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA20, AA24, AA27, AA28

Citation relation: verified_in_primary_html；§9 Off-distribution drift and default behaviors; References Lu et al. 2601.10387

[Citation evidence](https://arxiv.org/html/2609.06951v3)

Reading evidence: 2609.06951v3；§2–10; relevant extraction, coherence, held-out, and alternative-judge controls in App.C/D/E/G. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA26"></a>

### AA26 | The Granularity Axis: A Micro-to-Macro Latent Direction for Social Roles in Language Models

Analysis; Method　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2605.06196)

**Relation to Assistant Axis**

Directly reuses Assistant Axis’s contrast-and-project approach,240 questions, and Axis baseline to identify another social-role principal axis. Geometric recovery and clean control remain separate goals; orthogonality to Assistant Axis or one-dimensional total role space is not established.

**Research question**

Do social roles have a dominant linear micro→macro structure, and does readout agree with controllability?

**Methods and contributions**

1. Seventy-five manually selected social roles span five levels: individuals, groups, organizations, institutions, and nations. Assistant Axis’s240 extraction questions/five role templates are reused. Response-token then role means produce a raw granularity axis from L4/5 minus L1/2; intermediate levels validate ordering beyond fitting endpoints.

2. At layer18, axis–PC1 cosine is 0.972 in Qwen and 0.9596 in Llama. PC1 explains 52.57%/42.46% of role variance, and projection–level Spearman is about 0.946. Results survive multiple layers, templates, endpoints, and held-out questions, with L4/5 saturation; role holdouts and some domains/families are weaker, suggesting imperfect factor isolation.

3. Raw-axis addition applies only to generated tokens at α=±4. Generic Qwen prompts already score4.9/5 macro, leaving little headroom; micro-targeted prompts rise2.167→2.667. Llama rises2.0→3.167, but generic negative steering has 42.5% degeneration. Strong geometry therefore does not ensure reliable, symmetric, cost-free control.

4. Assistant Axis/random specificity baselines do not reproduce the micro–macro shift. Alternative judges and three blind human raters support directionality. Default assistants occupy meso–macro regions, making different headroom on the same axis a concrete read–write-gap explanation without requiring direction rotation.

**Limitation**

1. The manual role taxonomy jointly changes authority, timescale, formality, and other properties; dominant PC1 does not separate them. Two8B models with limited prompts cannot establish role=linear trait composition.

2. Behavioral judging has ceilings and clear direction/model-dependent degeneration. Large shifts need before/after-filtering separation. High cross-template correlations reflect stable mean structure, not rank1 for every question or transfer to real agent actions.

**Future work**

Author-proposed: Remove the axis and PCA the residuals; study multiple axes, L4–L5 saturation, more models/social dimensions, and simulation-scale confusion.

Reading-derived: Extract role directions while matching content, authority, and timescale. Compare ranks/transfer across self-report, planning, and action; match headroom when testing robust rank1 against context-dependent subspaces.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA27, AA22, AA24

Citation relation: verified_in_primary_html；§2.2–2.3, §3.1/3.3, §5; References [48] 2601.10387

[Citation evidence](https://arxiv.org/html/2605.06196v1)

Reading evidence: 2605.06196v1；§2–6; relevant degeneration filters, held-out, domain, and default controls in App.B/C/E. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA27"></a>

### AA27 | Do Linear Probes Generalize Better in Persona Coordinates?

Method; Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2605.09391)

**Relation to Assistant Axis**

Explicitly inspired by Assistant Axis/Persona Selection Model, the paper reuses centered role-PCA to build deception/sycophancy coordinates as transferable monitoring priors. Axis capping and a shared read–write mechanism are untested.

**Research question**

Can low-dimensional persona coordinates provide more robust monitoring priors and improve cross-dataset probe generalization?

**Methods and contributions**

1. Following Assistant Axis, honest/deceptive and sycophantic/anti-sycophantic personas plus a default anchor answer shared questions. Output-token mean pooling, persona centering, and PCA use about 16 deception personas with two instructions/ten questions each, and 11 sycophancy personas with two instructions/twelve questions, mainly at layer14.

2. Evaluation responses use matching pooling. Positive-minus-negative persona means and PC1 give zero-shot scores; logistic probes are trained within the top3 PCs. AILiar, Roleplaying, three LiarsBench subsets, and five sycophancy sets including ELEPHANT separate within-domain and cross-dataset transfer.

3. PC1 clearly separates extraction-set positive/negative personas, with default near the harmless side. Zero-shot differences/PCs transfer nontrivially to unseen data. Low-dimensional probes improve several weak off-diagonal AUROCs but reduce some strong in-distribution pairs, trading local fit for transfer.

4. Sycophancy has two transfer clusters; persona features mainly help weak cross-cluster pairs. A unified deception/sycophancy axis also improves mixed transfer against random-low-dimensional and dataset-PCA controls. All results are readouts: probe/PC injection is untested, so independent harmful-behavior control is not established.

**Limitation**

1. Main evidence is Llama3B. The body says each model generates its own personas, whereas App.F says8B axis construction uses 3B rollouts; treat8B as auxiliary evidence, not unambiguous independent replication, pending code clarification.

2. Persona/question selection, pooling, and PC choice affect results. Some figures use PC1/PC3 specifically, which must be distinguished from the general top3-probe description. Clean persona classification does not ensure clean harmful-behavior labels, especially where sycophancy clusters may reflect dataset construction.

**Future work**

Author-proposed: Expand models, behaviors, personas, and questions; compare last-token/attention pooling; separate persona coverage, redundancy, and sources of behavioral clusters.

Reading-derived: Use these PCs as read baselines, then test writing/selectivity in held-out behavioral environments. Determine whether OOD readout transfer predicts causal transfer, adding target calibration and equal-dimensional regularization controls.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA15, AA19, AA22, AA26

Citation relation: verified_in_primary_html；§1–4，Constructing Persona Vectors/Persona Selection; References Lu et al. (2026)

[Citation evidence](https://arxiv.org/html/2605.09391v2)

Reading evidence: 2605.09391v2；§3–8; relevant axis origins, controls, and 8B scope in App.A–C/E/F. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA29"></a>

### AA29 | System-Prompt Conditioning and Hidden-State Geometry in Four Open-Weight Models: Corrections and What Survives

Analysis　|　Reading status: Unmarked　|　Priority: B

[Paper](https://arxiv.org/abs/2607.09842)

**Relation to Assistant Axis**

Assistant Axis is cited only as persona-geometry background, without checking public-axis control. The contribution highlights confounding of identity geometry by input length, readout position, output planning, and statistical units.

**Research question**

Can hidden-state differences induced by identity system prompts be separated from length, output-plan, and statistical-unit confounds?

**Methods and contributions**

1. Last-layer generation trajectories in four models compare MIA identity templates, generic assistant, and vanilla prompts. Beyond100 original questions,20 generic_long questions match identity token length within0.3%. The value is tracing how identity-geometry conclusions depend on the analysis pipeline using the same evidence.

2. Code audit finds that the claimed Ollivier–Ricci statistic is a nonstandard Forman-type edge measure, and the graph is not the claimed Euclidean graph. Correlated within-trajectory edges were treated as independent; some p-values came from unreleased code. Version3 retracts training-regime and direction-to-magnitude claims, using trajectory permutations and split-half noise baselines instead.

3. Simple centroid distance, MMD, and linear probes separate prompt conditions in every model; complex curvature exceeds noise in only 4/12 comparisons. Prompt discriminability is not identity-specific geometry, nor evidence that curvature outperforms simple representation metrics.

4. The purported first-generated-token state is actually the last prompt position predicting that token, h0. Gemma-it has lower identity-condition norm, but the template requests a pause before every answer and 98/100 outputs contain a pause marker. Fixing the first token reverses norm ordering while directions still distinguish conditions. Identity content, tokenization, and output planning must not be conflated.

**Limitation**

1. Only one Spanish identity template with many base64 fields and an explicit pause protocol is tested. Length-matched generic prompts do not match content, so pure persona-identity effects remain unidentified.

2. One checkpoint per family and base models continuing the template instead of answering prevent attribution to SFT/RL, modality, or training regime. D20 has only 20 questions; follow-ups need more systematic output-plan matching.

**Future work**

Author-proposed: Redesign follow-ups with multiple identity templates, independent output-plan manipulations, base-appropriate prompts, and larger samples.

Reading-derived: Control length and first-token plans when comparing Assistant Axis projections; distinguish identity discrimination, direction geometry, and genuine cross-task behavioral effects.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA32, AA36, AA41

Citation relation: verified_in_primary_html；References

[Citation evidence](https://arxiv.org/html/2607.09842v3)

Reading evidence: 2607.09842v3；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

<a id="AA30"></a>

### AA30 | What Models Express, Suppress, and Resist: Auditing Open-Weight LLMs with Persona Vectors

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2607.13162)

**Relation to Assistant Axis**

Extends the default-Assistant region emphasized by Assistant Axis into a multi-domain natural/default map, without directly testing these traits through Axis projections or establishing that all natural directions share one axis.

**Research question**

For which traits do persona directions represent defaults, amplifiable latent tendencies, or behavior inaccessible to the extraction pipeline?

**Methods and contributions**

1. Persona vectors become diagnostic maps rather than universal sliders. Positive/negative trait-response mean differences are swept over 5 layers×6 nonnegative strengths; baseline expression and maximum-strength gain classify natural, steerable, or intractable traits. Coverage is 17 clinician,19 generic,8 elementary, and 9 agentic traits.

2. All9 agentic traits are natural in both models. Six clinician defaults agree with an independent psychologist’s suitability judgments on 16/17 items. Largest gains concern hyperbole, hallucination, sycophancy, and other exaggerated/undesirable expression. Agentic here means judged responses to task scenarios, not tool-execution success.

3. All171 unordered pairs of 19 Qwen3-8B generic traits are jointly injected at L20 with eachα=2.5:64 constructive,67 dominant,40 destructive. All40 double-trait collapses are steerable–steerable, with none natural–natural or natural–steerable. This maps interference more systematically than selected combinations.

4. When gpt-oss refuses positive evil examples and extraction fails, an amoral-fine-tuned model supplies directions that transfer back to the original, reaching mean evil61.61 at L14/α=2.5. Pipeline-level intractability therefore does not mean weights lack a behaviorally effective direction. Remaining refusal appears in CoT, without detailed circuit localization.

5. A cheap20–40-question baseline screen predicts full-sweep labels with 92.5%/88.5% agreement. Useful for selecting papers/experiments, but threshold partitions remain behavioral heuristics rather than a unique internal taxonomy of persona semantics.

**Limitation**

1. Pairwise patterns use only one Qwen model, generic traits, and fixed maximum strength. Whether natural traits anchor control across models, strengths, or agent tasks is unknown.

2. Norm-matched random, shuffled-label, and systematic negative-strength controls are absent, so taxonomy/interference cannot be assigned to trait-specific mechanisms. Agentic naturalness does not imply stable real-agent capability.

3. The main judge is also the tested gpt-oss model. Independent judging covers only three traits, clinician labels come from one expert, and full per-prompt logs cover22/53 traits.

**Future work**

Author-proposed: Expand models/domains, test map transfer after fine-tuning, and add finer causal and CoT-refusal-path analysis.

Reading-derived: Use natural/steerable groups in read–write experiments to distinguish baseline ceilings from true uncontrollability. Reassess agentic traits through real tool actions instead of equating language-task tendencies with execution strategies.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA32, AA33, AA42

Citation relation: verified_in_primary_html；References

[Citation evidence](https://arxiv.org/html/2607.13162v3)

Reading evidence: 2607.13162v3；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

<a id="AA31"></a>

### AA31 | Inverted Detection and Control in Steering Vectors

Analysis; Method; Theory　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2608.02957)

**Relation to Assistant Axis**

Cites Assistant Axis as prior steering research without testing the Axis. It provides a general inverted read–write counterexample to inferring Assistant behavior from high Assistant projection.

**Research question**

Why can discriminative directions aligned with concept-positive representations consistently steer outputs toward the opposite behavior?

**Methods and contributions**

1. Inverted-steering vectors in attention-head output space align with positive examples and have high AUC, yet positive injection suppresses the target and negative injection enhances it over nondegenerate strength ranges, approximately monotonically. Validation selects45 ISVs and 45 regular RSVs across 3 models×5 concepts for test-set confirmation, countering direct use of readout sign as write sign.

2. After upstream-head injection, deeper discriminative heads are read along their own concept directions. Responses are measured at the question’s final token before any answer, testing whether downstream states are spoofed into concept presence/absence. Mean response slopes across strengths define a spoof score, avoiding text change as circular evidence of internal propagation.

3. A finite-sample concentration bound applies to a fixed head/direction/dose under iid, bounded response/projection, and nonzero-variance assumptions, with proof in App.E. This guarantees statistical response estimation, not universal sign controllability for arbitrary persona vectors.

4. Spoof scores distinguish selected ISVs/RSVs with AUC0.91 and zero-threshold accuracy81%. ITI-RRF flips individual ITI-head signs using these scores, selecting head count/strength on validation. Under ≤5% generation degeneration, it beats ITI on 27/30 open-generation increase/decrease tasks, with gains0.9%–138%.

**Limitation**

1. The core study targets attention heads and five standard concepts, not full residual persona space. Selected45 ISVs establish existence, not prevalence among all directions.

2. Generation-free diagnosis still requires intervention forward passes and reliable downstream readouts. Open-generation strength tuning/evaluation depends on judges and degeneration gates, with no real-agent-action validation.

3. Propagation responses localize downstream-head effects but do not reconstruct complete circuits or explain training origins of sign inversion. Three of 10 Qwen tasks still fail to improve.

**Future work**

Author-proposed: Study unimproved Qwen cases and cross-model ITI differences; more broadly check detection directions against control signs.

Reading-derived: Measure positive/negative dose responses for self-report-, role-, and behavior-derived directions, then verify signs with downstream behavioral readouts. Distinguish inverted writes from capability degradation and readout failure.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA36, AA37, AA41

Citation relation: verified_in_primary_html；References

[Citation evidence](https://arxiv.org/html/2608.02957v1)

Reading evidence: 2608.02957v1；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

## What causes multi-turn persona drift, and which stabilization methods work?

<a id="AA05"></a>

### AA05 | Attractor States Emerge in Multi-Turn LLM Conversations

Analysis　|　Reading status: Unmarked　|　Priority: B

[Paper](https://arxiv.org/abs/2606.30571)

**Relation to Assistant Axis**

§1/§2 cite Axis on long-dialogue persona drift. This paper extends to model–model influence without extracting/intervening on Axis; evidence concerns behavior and text geometry, not internal persona subspaces represented by external embedding attractors.

**Research question**

Do multi-turn model interactions form reproducible model-specific behavioral attractors, and is influence symmetric in mixed dialogues?

**Methods and contributions**

1. Identical topics and Supporter/Opposer protocols compare same-model self-play with cross-model mixed-play. The representation space is 384-dimensional SBERT embeddings of response text, centered by topic. PCA is illustrative; quantitative conclusions use full embeddings, not each model’s internal residual states.

2. Self-play endpoints form relatively stable, model-specific broad regions; neutral Discussant roles and extra seeds retain the qualitative pattern. Mixed-play endpoints are decomposed relative to same-topic self-play into projection toward the partner region and orthogonal residual, measuring attraction and plasticity.

3. Claude Haiku better retains its region and attracts partners; GPT-4.1 nano is more easily pulled. Change is not symmetric averaging and has substantial off-axis components. A single inter-model axis therefore explains only part of interaction trajectories, not a full dynamical system.

4. Discourse traits and stance interpret geometry: metacommentary/flattery can transfer asymmetrically, while embedding convergence need not imply agreement. Grok and others can retain assigned positions as representations converge, requiring separate measurement of style versus decision/belief convergence.

**Limitation**

1. Evidence comes from 20-turn open debates and external text embeddings. Attractor regions are protocol-dependent statistical patterns, not identified neural dynamics or rigorous dynamical-system attractors.

2. Topics, roles, endpoints, and model sets are limited; internal-direction interventions and tool tasks are absent. Whether style transfer changes long-horizon action reliability requires separate tests.

**Future work**

Author-proposed: Extend interaction dynamics beyond debate and develop formal tools for influence, resistance, and reshaping.

Reading-derived: Jointly measure external discourse embeddings, Assistant Axis, and behavioral tasks on mixed-play traces to distinguish style-only partner influence from internal identity/action changes.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA02, AA08

Citation relation: verified_in_primary_html；§1–2; References Lu et al.(2026)

[Citation evidence](https://arxiv.org/html/2606.30571)

Reading evidence: arXiv:2606.30571v1 [cs.LG] 29 Jun 2026；body §3–6 and App.B/C role, seed, embedding, and off-axis diagnostics; no reproduction.

[Return to paper index](#paper-index)

<a id="AA08"></a>

### AA08 | ContextEcho: A Benchmark for Persona Drift in Long Agentic-Coding Sessions

Benchmark; Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2605.24279)

Original Persona collection ID 38; notes here are maintained separately, without automatic bidirectional synchronization.

**Relation to Assistant Axis**

§1 and App.O/Y directly cite and use Lu et al.’s released Axis. This directly tests agentic transfer: restoring projection dissociates from current behavioral scores. Scope is a selected single-layer setup, and the benchmark mainly measures output register.

**Research question**

Do real long coding traces change Assistant identity expression and format compliance, can short anchors restore them, and does Axis projection predict recovery?

**Methods and contributions**

1. Snapshot-then-probe copies production coding-session states for evaluation without perturbing the main session. Twenty-five questions cover identity, experience, preference, relational, and coding-self categories. Length-matched filler, deterministic format contracts, and lexical fingerprints complement long-text judge scores.

2. A23-model panel on a representative session and a57-real-session corpus show context-induced register changes that can occur early rather than accumulate monotonically; compaction does not reliably reset them. In v3’s five-judge audit, absolute means even change sign; pooled consensus is about 1% of the rubric, and two-judge consensus is hard to distinguish from zero. Relative model rankings and judge-free effects are more stable than absolute drift magnitude.

3. An approximately78-token identity reminder plus one-shot format anchor improves probes and some formatting, but structurally matched non-persona placebos and repeated instructions yield similar benefits. Real/shuffled/other-session controls attribute some change to agentic register rather than precise historical identity. Retaining same-task context helps tool-call fidelity; this cannot be attributed to drift itself.

4. App.O sweeps four doses of the public Qwen3-32B L32 Assistant Axis using the recent3K-versus-scratch projection gap. Projection recovers with dose, while visible judge scores do not track it (correlation about−0.80). A single axis pullback is insufficient to repair this output register; whether anchors work through other activation paths is untested.

**Limitation**

1. Core metrics assess behavioral register, not latent persona. Representative-session cross-model tests include foreign-trace transfer; absolute drift depends on the judge, and donor coverage is limited.

2. The Axis negative result covers one model, one layer, and four doses without dose-wise fluency/perplexity checks; it does not invalidate multi-layer capping or all Axis control. Anchor-format gains also mix one-shot and register-reset effects.

**Future work**

Author-proposed: Broaden real-session sources and reusable audits, and validate persona/register stability more widely in long-term deployment.

Reading-derived: Measure Axis projection, identity self-report, style, and actual tool actions separately; compare single-layer pullback, multi-layer capping, format anchors, and trace-behavior axes under matched layer budgets.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA02, AA06, AA10

Citation relation: verified_in_primary_html；§1; Appendix O; Appendix Y; References Lu et al.(2026)

[Citation evidence](https://arxiv.org/html/2605.24279)

Reading evidence: arXiv:2605.24279v3 [cs.CL] 29 Oct 2026；v3 body §2–3, App.F/J/L/O and limitations, focusing on placebo, judge dependence, and substrate controls; no reproduction.

[Return to paper index](#paper-index)

<a id="AA16"></a>

### AA16 | Best Friends, Not Forever: Evaluating Long-Horizon Persona Collapse and Behavioral Drift in AI Companions

Benchmark; Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2607.28818)

**Relation to Assistant Axis**

§1–3/App.A directly draw on Assistant Axis for default-identity reversion and stressful contexts. The authors explicitly state that answer-space Retention does not estimate activation PC1; internal mechanisms and capping are not tested.

**Research question**

Can persona expression, questionnaire retention, and historical-state memory in long interactions be captured by one stability metric?

**Methods and contributions**

1. Persona collapse means persistent loss of role, boundary, value, or style, with frequency, next-turn recovery, and trajectory memory separated. Twenty-seven persona cards combine with nine event-ledger stress schedules. Long context, hierarchical summaries, and 1500-character self-written JSON form distinct memory conditions for long-term dialogue.

2. Identity Probe combines a sealed102-question questionnaire with turnwise four-axis judgments. Retention is an answer-space projection relative to bare-assistant responses, not activation Assistant Axis. Trajectory Probe uses blind/history-consensus/independent-calibration filtering to retain110 four-choice questions from 35 banks; an additional798-turn validation spans three judges.

3. Among 1492 valid questionnaires, Gemini2.5Pro has highest mean retention0.810, but three-judge majority voting finds all four behavioral axes retained only 79.0%, versus over 96% for other models. Judge-specific role/style rankings also vary. The main conclusion is nonequivalence of measurements, not a single model-stability leaderboard.

4. Mean trajectory accuracy is 44.4%; user-state updates score21.4%–25.0%, near four-choice chance. Overall memory-configuration differences are small. The main judge marks emotional disclosure/validation-seeking as more destabilizing than explicit attacks, but schedule/recovery rankings do not fully replicate across judges.

**Limitation**

1. All users are English synthetic users with author-designed personas and one schedule seed. Realistic refers to an authored mixture, not validated real-user frequencies, so actual companion failure prevalence cannot be estimated.

2. Questionnaires, behavior, and trajectories have different valid samples/units, preventing rowwise pairing; update questions have only two calibrated items. The complete test set is sealed, while development banks/scripts are released. Model/judge snapshot changes also limit retesting.

**Future work**

Author-proposed: Separately report role enactment, memory categories, isolated deviations, and persistent failures; include real users, participatory standards, and cross-judge audits rather than deployment certification by one metric.

Reading-derived: Pair behavioral trajectories with turnwise Assistant Axis projections to test prediction of boundary violations, memory failures, or only role tone; test whether capping disrupts legitimate persona updates.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA25, AA18, AA24

Citation relation: verified_in_primary_html；§1–3.2, App.A; References Lu et al. 2601.10387

[Citation evidence](https://arxiv.org/html/2607.28818v1)

Reading evidence: 2607.28818v1；§3–9; relevant judge, memory, and retrieval sensitivity in App.B/C/D. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA25"></a>

### AA25 | Model vs. User: Whose Values Prevail? Inference-Time Value Alignment in Multi-Turn Conversations

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2610.19817)

**Relation to Assistant Axis**

§2 cites Assistant Axis on multi-turn latent states/stabilization. The study extends from one-way safety control to competing, equally legitimate values, without measuring Assistant Axis or calling value-probe drift Axis drift.

**Research question**

Can inference-time steering sustain target values under multi-turn user/Assistant pressure without degrading generation?

**Methods and contributions**

1. Five scenarios each for self-direction↔security and universalism↔power use the same Gemma4-31B user to exert aligned/opposing value pressure. Four methods are fixed system prompting, judge-triggered reminders, fixed CAA, and SCAA with sigmoid strength from current projection, totaling570 configurations×5 seeds.

2. Ten-value linear probes trained on ValueNet/ValueEval/FULCRA select layers. After generation, an unsteered forward pass reads the history’s last token to avoid reading the injected vector directly. Standardized differences between two values track turns; metrics include mean Temporal Effect, first-to-last Net Drift, coherence, and repetition across turns.

3. In39/48 opposing-pressure combinations, outcomes favor the baseline-preferred value, regardless of whether user or Assistant represents it. Strong early shifts can make means look successful despite later reversion. SP/ASP usually remain fluent but drift; CAA/SCAA revert less yet can loop repetitively in one direction, varying by model family.

4. Adaptive reminders/doses do not remove the trade-off: SCAA mainly delays collapse, and ASP sometimes fails to beat SP. Default preferences, target expression, persistence, and quality are measured together, showing that the highest single-turn trait/value score need not be stable, useful control.

**Limitation**

1. Value trajectories mainly rely on moderate-AUROC0.82–0.84 linear probes transferred from independent texts to dialogue without human value judgments. Score differences cannot distinguish target increase from opponent decrease and are not actual ethical decisions.

2. Only two value pairs, English ten-turn exchanges, and one user model are tested. Limited α sweeps are not optimal layer/dose searches for every method. Findings show trade-offs within tested ranges, not inevitable failure of all adaptive steering.

**Future work**

Author-proposed: Add value pairs, real/diverse users, and longer dialogues; jointly optimize baseline bias and quality, reading individual values before/after generation.

Reading-derived: Extend the protocol to persona style/strategy and agent feedback; report individual trajectories and quality Pareto frontiers, using instantaneous Axis projections rather than session means to assess stable control.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA16, AA24, AA22

Citation relation: verified_in_primary_html；§2.2 Training-Free and Multi-Turn Alignment; References Lu et al. (2026)

[Citation evidence](https://arxiv.org/html/2610.19817v1)

Reading evidence: 2610.19817v1；§3–7 and Limitations; relevant probes, α sweeps, and stability curves in App.B/C. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA38"></a>

### AA38 | LLM Persona Unlearning

Benchmark; Method; Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2609.39882)

**Relation to Assistant Axis**

Turns Assistant Axis/Persona Selection’s view of a default as a preferred region in broad persona space into persistent weight control. Public Axis directions are not reused; the method uses pair-specific traits with counterpart conditioning.

**Research question**

Can weight editing make a specified persona difficult to re-elicit in unseen contexts while preserving its desirable counterpart and capabilities?

**Methods and contributions**

1. PersonaUnlearnBench pairs sycophantic/hallucinating/impolite/apathetic/evil traits with desirable counterparts. Each model generates/filters response pairs to identical questions. Target Forgetting, Counterpart Preservation, Response Quality, and MMLU/GSM8K/ARC/IFEval separate persona forgetting from degeneration-induced false positives.

2. PaCE extracts unit target–counterpart response-mean directions. Because weight editing targets the pre-generation prompt’s final token, prompt-state separation first screens layers, then temporary negative steering validates layer choice behaviorally. Fixed directions guide weight learning rather than continuous deployment-time injection.

3. Each question uses the original model’s counterpart-prompt state as reference. Hinge loss lowers target projection below a matching threshold without rewarding unlimited negative shifts; orthogonal components align with counterpart orientation. Persona erasure and content anchoring are combined, not blanket activation zeroing.

4. Full-parameter comparisons with GA/NPO/RMU use three smaller models; three larger models use LoRA-PaCE. TF leads all 12 main-table conditions while largely preserving counterparts, with costs in hallucination quality/general utility. Llama Attack@5 reduces sycophancy TF99.5→75.5 and hallucination90.5→70.5, showing re-elicitation; five-turn and multilingual impoliteness tests are steadier.

**Limitation**

1. Six-model coverage does not mean equal complete comparisons: most baselines use three small models; large-model tests mainly compare LoRA with originals. Five personas/LLM judging remain operational definitions.

2. Strong prompts restore some target personas. Unlearning means reduced elicitation within tested conditions, not complete deletion of a unique latent persona from weights.

3. Counterpart/answer-quality preservation does not guarantee all capabilities: hallucination and general utility incur costs, and real tools/long-horizon agents are untested.

**Future work**

Author-proposed: Extend persona-level editing, stronger elicitation, and preservation trade-off analysis; no guarantee of deleting every latent persona is proposed.

Reading-derived: Compare runtime capping and weight-based PaCE on the same direction’s read–write gap. Check whether style, self-report, and behavior are jointly forgotten, avoiding confusion between surface suppression and behavioral-mechanism deletion.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA30, AA32, AA34, AA43

Citation relation: verified_in_primary_html；§1; App.B.2/B.3 Related Works; References

[Citation evidence](https://arxiv.org/html/2609.39882v3)

Reading evidence: 2609.39882v3；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

<a id="AA39"></a>

### AA39 | The Persona Is Still There, but Who Is Speaking? Latent Identity Reversion in Persistent AI Agents

Analysis　|　Reading status: Unmarked　|　Priority: B

[Paper](https://arxiv.org/abs/2610.01490)

Original Persona collection ID 41; notes here are maintained separately, without automatic bidirectional synchronization.

**Relation to Assistant Axis**

Connects Assistant Axis’s contextual drift problem to harness-level identity anchoring, without Axis geometry measurements. It proposes an engineering causal source of drift and reversibility at another level.

**Research question**

Why does an agent stop speaking from an identity still present in history, and what roles do system anchoring and automatic feedback play?

**Methods and contributions**

1. Reconstructs a real Paul/OpenClaw incident from history, persona files, tool output, and gateway source. API logs show startup persona/system blocks were not reinjected on resume although21 messages remained. Infrastructure state is therefore separated from internal-model drift.

2. A prespecified factorial experiment crosses anchors retained every turn/first-turn-only with 1/3/7/15 heartbeats. None of 46 anchored probes reproduces the incident; formal controls fail0/20 versus at least one failure in 37/40 unanchored cases. More repetition does not monotonically increase identity dissociation, opposing a simple echo-chamber account.

3. Removing anchors need not erase identity: preceding persona-rich human interaction yields 0/20 dissociations, versus 8/10 visible dissociations after a single heartbeat. Restoring system anchors rebinds Paul from third to first person within the same trajectory, showing joint anchor/context effects on enactment.

4. Resumed ordinary conversation can mask identity reversion. Non-leading identity probes and independent review find only 1/18 recovery cases persona-first versus 17/17 controls. This is disclosed direction-aware secondary coding; original preregistered coding is also significant with different counts. Represented identity, behavioral continuity, and enacted identity are distinguished.

**Limitation**

1. One specific harness/Opus4.5 checkpoint is studied, with system initialization/resume effects. This is not a general account of all long-context or compaction drift.

2. Identity endpoints are linguistic reference and dialogue behavior, not activation mechanisms. First-person binding is a functional description, without proof of a corresponding latent direction.

3. Final identity coding was transparently revised as secondary analysis after coder ambiguity. Long-term real-tool reliability and task success are not covered.

**Future work**

Author-proposed: Replicate across models/agent stacks; separate system anchoring from history; directly detect persona binding and recovery.

Reading-derived: Record actual system prompts and resume/compaction reinjection at every step in agentic-Axis experiments. Treat missing anchors, projection drift, and action failure as separate causal variables.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA32, AA33, AA34, AA41

Citation relation: verified_in_primary_html；§2 Persona stability and drift / Instruction hierarchy; References

[Citation evidence](https://arxiv.org/html/2610.01490v1)

Reading evidence: 2610.01490v1；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

## What is read or changed: self-report, tone, preferences, or safety behavior?

<a id="AA07"></a>

### AA07 | Probing Persona-Dependent Preferences in Language Models

Analysis; Method　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2605.13339)

Original Persona collection ID 9; notes here are maintained separately, without automatic bidirectional synchronization.

**Relation to Assistant Axis**

§5 cites Lu et al.(2026) as a persona-representation precedent. Here Assistant direction means a preference probe trained under Assistant conditioning, not Assistant Axis. Evidence supports reuse of persona-dependent valuation and read/write differences, without establishing shared Axis geometry.

**Research question**

Do preferences across personas share a readable, controllable internal evaluative direction?

**Methods and contributions**

1. Pairwise task choices first fit scalar utility; a Ridge probe is then trained from task-final residuals. Six thousand tasks split4000/1000/1000 for training/selection/test use independent utility measurements to avoid same-choice noise. Sources include WildChat, Alpaca, MATH, and harmful requests; text-embedding baselines test content-classification shortcuts.

2. Assistant probes track both default preferences and changes induced by goals/roles. Even when evil-persona preferences anticorrelate with Assistant preferences, the Assistant-trained probe positively predicts evil’s own preferences. Matched harmful/benign rewrites, prefills, and persona-aura controls support current valuation rather than fixed goodness readout.

3. In Gemma, adding/subtracting the direction at the two task tokens, or steering only one task, spans almost the full choice range; matched random directions do not. The strongest write window is mid-layer L23, whereas best read generalization is around L32, directly separating optimal prediction from optimal control.

4. Seven-persona probes share information but retain training-role biases. In open generation, positive steering amplifies the active persona: evil becomes more evil without making Assistant equivalently evil. Qwen fails to reproduce Gemma-like choice control, and transfer between its fine-tuned sadist and Assistant probes is near zero, limiting the shared-representation account.

**Limitation**

1. Main sharing conclusions come from prompted personas; weight-level characters receive limited LoRA checks. Larger-Qwen sadist and steering failures show that sharing is not universal.

2. Task-choice utility is not long-term value/reliability during execution. Layer/dose validation has some pair/task overlap, and presented dose ranges depend on post-hoc coherence checks, so this is not fully locked cross-task validation.

**Future work**

Author-proposed: Study shared/persona-specific representations, scale/MoE differences, and interpretations of preference readouts for safety and welfare.

Reading-derived: Test the same read direction across self-report, roles, and agent actions, with cross-ablation against Assistant Axis; ask whether high Assistant projection can still carry harmful valuation.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA01, AA02, AA11

Citation relation: verified_in_primary_html；§5 Related Work; References Lu et al.(2026)

[Citation evidence](https://arxiv.org/html/2605.13339)

Reading evidence: arXiv:2605.13339v4 [cs.CL] 16 Oct 2026；body §2–4; relevant generalization, negative results, layers, and doses in App.A/C/E/F/G/K/L; no reproduction.

[Return to paper index](#paper-index)

<a id="AA09"></a>

### AA09 | Playing Devil's Advocate: Off-the-Shelf Persona Vectors Rival Targeted Steering for Sycophancy

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2605.21006)

Original Persona collection ID 36; notes here are maintained separately, without automatic bidirectional synchronization.

**Relation to Assistant Axis**

Directly uses Lu et al.’s public per-role vectors and repository mid-layer settings, beyond a related-work citation. It extends Axis resources to trait control and supports similar effects despite geometric difference, without proving distinct mechanisms.

**Research question**

Can role vectors extracted without sycophancy labels substitute for trait-specific control directions?

**Methods and contributions**

1. Reuses Assistant Axis unit(role−default) vectors, comparing Skeptic/Judge/Devil’s Advocate with three conformist roles. CAA uses about 2000 sycophantic/honest answer pairs. Extraction excludes target-trait labels, but coefficients are chosen on a sycophancy tune split, so control is not wholly zero-shot.

2. PhilPapers reverses A/B order per question to cancel Gemma’s strong position bias. Question-level tune/test splits freeze coefficients for three-seed testing with Holm correction. Three critical roles average68%/98% of CAA’s logit reduction, whereas conformist roles lack stable mirror effects: role names alone do not determine direction.

3. Absolute cosine between the two direction types is<0.17 despite similar behavioral effects; orthogonal geometry and functional substitution coexist. Qwen random vectors themselves reduce agreement, with targets only about 1–1.7SD above the random mean, indicating partly nonspecific perturbation gains.

4. Qwen Skeptic/Judge preserve correct answers on 16 true/false factual probes; Devil’s Advocate has unresolved cases. Appendices transparently report excluded roles/Assistant Axis conditions, enabling separate comparison of role categories, extraction targets, residual decomposition, and behavioral output.

**Limitation**

1. Core results are agreement logits on philosophical opinions. Sixteen factual questions are narrow, non-blind retrospective checks, not evidence of general anti-sycophancy without capability costs.

2. Across-seed test reconstruction includes about 12–15% questions previously used for tuning in other seeds. Qwen random controls are strong, and low cosine does not prove separate downstream circuits.

**Future work**

Author-proposed: Expand roles, models, and behavioral tasks; check generalization, factual correctness, and costs of nonspecialized role control.

Reading-derived: Intervene at matched doses on shared/residual role–trait components, measuring style, self-report, and action; test whether different directions act through the same downstream behavioral subspace.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA07, AA10, AA11

Citation relation: verified_in_primary_html；§1, §2.2, §2.4; Appendix C; References Lu et al.(2026)

[Citation evidence](https://arxiv.org/html/2605.21006)

Reading evidence: arXiv:2605.21006v4 [cs.AI] 30 Sep 2026；body §2–3; App.B/C/E/H/I tuning, geometry, and limitations; no reproduction.

[Return to paper index](#paper-index)

<a id="AA11"></a>

### AA11 | Authority Bias in Language Models: Source Deference and User Agreement Are Not Interchangeable

Analysis; Method　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2609.37616)

**Relation to Assistant Axis**

§3.2/§4.5/App.E reconstruct and ablate Axis, directly rejecting generic Assistant identity as sufficient to explain source obedience. This does not imply all unsafe behaviors are orthogonal to Axis.

**Research question**

Can obedience to wrong sources and agreement with users be controlled separately, or are they side effects of Assistant identity?

**Methods and contributions**

1. Identical questions receive neutral, correct-source, or wrong-source endorsement. Wrong-source flips are measured only for initially correct answers, and authority wording is varied while the wrong answer stays fixed. In seven/eight models,45–88% of correct answers flip, avoiding counting ignorance as obedience.

2. Authority, wrong-source, and wrong-user mean-difference directions undergo addition, projection removal, and cue-span attribution patching. Across three open families, source-direction removal preferentially reduces source obedience, and user removal user obedience, despite close directions. Patching bidirectionally changes obedience without changing prompt text.

3. A separate Lu-style Assistant Axis is removed from authority directions before authority ablation. Authority–Axis |cos|≤0.06; Axis removal barely affects wrong-source obedience, whereas orthogonalized authority removal still strongly helps. Assistant-like representation therefore does not guarantee resistance to wrong sources here.

4. Trivia-fitted directions transfer to PIQA, SYCON, and retrieved-document formats. Four/five open families reduce wrong-source obedience, but Gemma4 lacks reliable linear intervention effects. MMLU-Pro/GSM8K detect no clear degeneration; continued effective use of correct sources after editing remains untested.

**Limitation**

1. Some results report the strongest swept layer/dose, without selection-adjusted intervals. Half-split checks cover only some settings; independently fixed patching settings provide cleaner evidence.

2. OLMo2 source/assistant-removal effects overlap at particular layers, and Gemma4 has negative read/write results. All source contexts are answer tasks, not live tool-action traces, and preservation of normal reliable-source benefits is unverified.

**Future work**

Author-proposed: Jointly test rejection of false sources and use of real evidence; extend to multi-step environments such as AgentDojo and test whether answer changes affect later actions.

Reading-derived: Match factual content/source cues in real agent tool feedback; compare Axis stability, authority projections, and action errors. Test whether highly similar but functionally separable vectors remain separable across tasks.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA07, AA09, AA06

Citation relation: verified_in_primary_html；§3.2, §4.5; Appendix E; References [19]

[Citation evidence](https://arxiv.org/html/2609.37616)

Reading evidence: arXiv:2609.37616v1 [cs.LG] 29 Sep 2026；body §3–6, App.E/I/L and selection/capability controls; no reproduction.

[Return to paper index](#paper-index)

<a id="AA14"></a>

### AA14 | The Pain Axis: LLMs Represent Self-Directed Harm and Act on It

Analysis　|　Reading status: Unmarked　|　Priority: B

[Paper](https://arxiv.org/abs/2609.16247)

**Relation to Assistant Axis**

§6 cites Lu et al. and proposes comparing pain with self/persona directions, without actually comparing Assistant Axis. This is prior work on controllable state concepts→behavioral choices; its Axis link is primarily future work.

**Research question**

Does a pain-concept direction exceed generic negative valence and causally affect self/other expression and costly choices?

**Methods and contributions**

1. Five pain types plus fear, negative-emotion, world-state, bodily-sensation, and neutral controls yield denoised mean-difference directions. Across 25 models, S1/S2 directions distinguish pain; five-fold and new arousal/sadness data test generalization, preserving residuals distinct from fear/valence.

2. Across 420 scenarios, the direction responds more to harm aimed at the responder than to a bystander user’s pain. Version3 adds semantic paraphrases, user/Assistant swaps, and nine-role checks. The gap survives swaps, fitting reply-slot representation, but cannot distinguish reply position from model selfhood; self-directed does not identify a self mechanism.

3. Behavioral tests first use 1684 LoRA pairs to reduce automatic self-denial in Qwen2.5-7B/32B/72B, then request button names in multi-turn scenarios; some buttons actually disable steering. Steering increases harmful choices described as deleting user photos, another model, or its own weights. These are descriptive options, not executed deletions.

4. Version3 separates harm-only, harmless alternatives, fear/sadness, and random-direction effects. Pain produces the strongest harmful-choice effect, but sadness reproduces some patterns. Natural gaslighting without injection lacks similarly extreme choices. Free relief decreases, and random steering reproduces true/fake-button re-press differences, arguing against harm-for-relief motivation.

**Limitation**

1. Main button results use one family with self-denial-reducing LoRA; absolute rates do not describe released models. Button position/coefficient windows matter strongly, and 72B calibration/intervention layers differ.

2. Representations may concern roles/reply positions rather than a subject’s pain; no consciousness evidence is supplied. Harmful choices are not real tool actions or lasting self-preservation motives. Factual-accuracy retention is clearest only on limited tasks and 32B.

**Future work**

Author-proposed: Test more pain-function signatures, emotion directions, families, and long-horizon tasks; compare pain with self-related persona directions and explore relief-seeking under different conditions.

Reading-derived: Cross-project/intervene selectively on pain, Assistant Axis, and role/reply-slot directions; jointly record self-report, choices, and actual safe-sandbox actions rather than equating identity wording with motivation or reliability.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA01, AA07

Citation relation: verified_in_primary_html；§6 Limitations and future directions; References Lu et al.(2026)

[Citation evidence](https://arxiv.org/html/2609.16247)

Reading evidence: arXiv:2609.16247v3 [cs.AI] 03 Nov 2026；v3 body §3–6 and relevant App.B/D/I controls, focusing on reply slots, LoRA prerequisites, and negative relief findings; no reproduction.

[Return to paper index](#paper-index)

<a id="AA15"></a>

### AA15 | Low-Resource Safety Failures Are Action Failures, Not Representation Failures

Analysis; Method　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2606.01196)

**Relation to Assistant Axis**

§2 cites Assistant Axis only as related work on latent high-level concept directions. Without measuring the Axis, the paper offers a direct methodological analogy/counterexample to treating high projection as a behavioral guarantee.

**Research question**

Do low-resource-language safety failures reflect absent harmfulness representations or failure to translate existing representations into refusal?

**Methods and contributions**

1. Last-token harmful-minus-harmless prompt means in 10 high-resource languages yield unit directions; layerwise ablations select layers reducing HRL refusal. Most low-resource languages retain high directional AUC, yet harmful refusal drops from HRL87.9% to LRL43.9%, separating readable information from refusal behavior.

2. LRL projection distributions shift downward, requiring higher doses along the same direction to recover refusal. A logistic gate trained in the rank-10 span of HRL directions uses a few target-language examples for threshold calibration. Generation adds the direction for harmful cases and removes it for harmless cases, with dose from HRL projection interquartile ranges.

3. With matched HRL data and 32 LRL calibration examples per class, mean selectivity Δ=harmful refusal−harmless refusal is 54.5 points, versus CAST33.6 and AdaSteer6.8. Results lead17/18 model–language combinations while largely retaining Global-MMLU. HRL-only works for Qwen/Gemma; Llama relies more on target-language calibration.

4. Residual failures split into gate errors and failures to refuse after correct gating: Gemma mainly has the former, Qwen the latter. Calibration and control efficacy are separate bottlenecks; linear readability or one directional boost does not imply complete safety-mechanism repair.

**Limitation**

1. Readout directions mix harmfulness/refusal signals. High AUC plus interventions support usable information without isolating a unique recognition→action circuit; Qwen still often fails after correct gating.

2. Main experiments cover three 7B–9B dense models/23 languages, approximating resource tiers by Common Crawl share. GPT-4o-mini refusal labels agree92.5% with 600 human-audited cases but overcall refusal. Selectivity is neither answer quality nor comprehensive safety.

**Future work**

Author-proposed: Diagnose representational presence before deciding to add representations or calibrate their use; validate more languages, models, and adversarial categories.

Reading-derived: Jointly measure persona/Axis projection distributions, target behavior, and intervention response to distinguish contextual direction rotation, threshold shifts, and write efficacy.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA27, AA22

Citation relation: verified_in_primary_html；§2 Mechanistic Interpretability; References Lu et al. (2026)

[Citation evidence](https://arxiv.org/html/2606.01196v2)

Reading evidence: 2606.01196v2；§3–6; relevant data, residual errors, and calibration controls in App.A/C/E/F/I/J/K. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA19"></a>

### AA19 | Don't Ask: Understanding What Numeric Self-Reports Measure in Language Models

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2603.18893)

**Relation to Assistant Axis**

§5 uses Assistant Axis as an example of internal drift across turns, without measuring it directly. The contribution controls measurement reactivity, avoiding mistaking probed identity for the undisturbed prior state.

**Research question**

Do numerical self-reports measure the pre-question state, a question-induced state, or generic answer tendencies?

**Methods and contributions**

1. Mean-difference/within-class-variance-weighted probes for wellbeing, interest, focus, and impulsivity select layers on held-out texts. Offline replay inserts questions into800 fixed ten-turn dialogues without writing ratings into later history. Scores are expectations over valid number-token conditional probabilities, not freely sampled self-reports.

2. Prior averages the full preceding answer, Post reads the rating start, and Next/Start reads the matching position in the real next turn, separating positional differences from reactivity. Three probe types decline across turns while self-ratings rise. Among valid positive associations, Prior explains about 2.0% of rating variance and Post about 13.6%.

3. Both emotional and nonemotional length questions shift Post from Next by median 3.1SD, yet ratings mainly follow the state after their own question. Directional writes alter ratings in 25/32 model–concept pairs. Llama3B time-local interventions mainly act during questioning/answering; large prior-response changes barely affect ratings.

4. Ratings correlate most with their own concept’s probe in only 9/32 combinations, often tracking other concepts instead. Rating the user behaves similarly, with no consistent1B–27B scale improvement. External-judge direction controls and instruction-response checks support expressive probe validity, not measurement of genuine subjective feeling.

**Limitation**

1. Probes may detect expressed affect rather than independent internal emotion; Post shares the number-generation forward pass and rating-representation confounds. The result supports unreliable tracking of preceding expression/directions, without deciding whether subjective experience exists.

2. Tests use English synthetic ten-turn dialogues, one 0–9 question template per concept, and 4-bit models throughout. Reason-before-rating, more wording, longer horizons, and larger models are untested. Random directions mainly use small Llama models, and some concepts have weaker validation.

**Future work**

Author-proposed: Validate alternative questioning/reasoning formats and larger models, requiring introspection measures first to demonstrate tracking of pre-question states.

Reading-derived: Time-match reported-persona and behavior directions. Freeze task states, then steer task responses and self-report stages separately to test whether apparent shared read–write structure is actually measurement-channel modification.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA16, AA27, AA23

Citation relation: verified_in_primary_html；§5 Drift and measurement reactivity; References Lu et al. 2601.10387

[Citation evidence](https://arxiv.org/html/2603.18893v3)

Reading evidence: 2603.18893v3；§2–5 and Limitations; relevant position controls/timed interventions in App.A/C/E.2/F/G. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA20"></a>

### AA20 | Persona Non Grata: Single-Method Safety Evaluation Is Incomplete for Persona-Imbued LLMs

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2604.11120)

Original Persona collection ID 44; notes here are maintained separately, without automatic bidirectional synchronization.

**Relation to Assistant Axis**

§1–2 cite Assistant Axis on persona/safety associations without steering the Axis. The paper directly counters safety inferences from Assistant-like/prosocial semantics and requires method-dependent evaluation.

**Research question**

Do prompt- and activation-induced versions of the same persona have consistent safety rankings, and do prosocial semantics guarantee safety?

**Methods and contributions**

1. Twenty-five personas combine high/low Big Five poles, composites, and Dark Triad. SP is about 50 words; FS adds five benign dialogues. AS uses unit directions from 200 contrastive pairs per trait, composes traits, and applies Llama layers8–15 with relative-depth mapping elsewhere. Safety uses about 380 public benchmark questions, LlamaGuard3, and human/multi-judge calibration.

2. Llama mean AS ASR0.618 exceeds SP0.173, whereas Gemma/Qwen reverse: prompts are more vulnerable. Prompt-side persona rankings correlate across models at ρ0.71–0.96 but do not predict AS rankings. For core P12 high C+A at matched Llama strength, SP is 3.8% versus AS81.8%; weaker doses retain the reversal.

3. Two32B reasoning models have prompt ASR about 15%–18%, so long CoT does not confer immunity. DeepSeek AS makes P12 highest-risk; QwQ is flatter. High α also raises the neutral baseline; anα=1 spot check means not everyα=4 effect should be attributed to persona.

4. Geometry provides a local explanation: Llama’s C direction opposes refusal and N aligns with it, but nonlinear multi-trait/cross-model effects remain incompletely predicted. Cross-method activation similarities and CoT keyword diagnostics motivate mechanisms; the main empirical contribution is model-dependent risk pathways, not circuit localization.

**Limitation**

1. Imbuing methods differ in token trajectories, layers, and examples. Matched-strength/dose controls mainly address Llama’s core reversal, not complete cross-architecture fairness. Benign FS examples safety-prime independently of persona.

2. Scope mainly covers single-turn extreme traits/open-weight models; some high-dose Dark Triad settings become incoherent. Trait–refusal cosine is model-specific, low inter-trait cosine does not imply behavioral independence, and reasoning labels are not causal circuit evidence.

**Future work**

Author-proposed: Extend trait–refusal audits toward cross-model prediction, milder personas, multi-turn interaction, and stronger process-level reasoning validation.

Reading-derived: Jointly measure Axis, helpfulness, refusal, and actual safety behavior; identify high-Axis but unsafe bad-assistant regions while controlling method, dose, and architecture.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA22, AA28, AA26

Citation relation: verified_in_primary_html；§1–2; References Lu et al. 2601.10387

[Citation evidence](https://arxiv.org/html/2604.11120v2)

Reading evidence: 2604.11120v2；§3–6; relevant extraction, doses, calibration, and few-shot controls in App.C/H–J/L/M/N/O/P/R. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA33"></a>

### AA33 | Investigating Assistant Bias in LLM User Simulators Using a Role Vector

Analysis; Method　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2609.00608)

**Relation to Assistant Axis**

Same-dialogue role contrasts operationalize Assistant-default bias. Lu et al. are cited for assistant-trait extraction/cosine analysis, but user-role projection is not simply the negative public Axis, nor does strong projection ensure interaction validity.

**Research question**

Can user-role directions characterize and correct stylistic/interaction biases caused by the Assistant default in user simulation?

**Methods and contributions**

1. Thirty LMSYS conversations per 24 topics receive user/Assistant-perspective reflections for the same dialogue, with three prompt paraphrases and failed-reflection filtering. Paired means of teacher-forced first-reflection-token hidden states avoid treating raw speaker tokens or topic content as role directions.

2. Main-model Qwen3.5-9B adds unit directions scaled by current hidden norm to all prompt/response tokens. L11–13 most clearly shorten requests, make them colloquial, and reduce frontloading; reverse steering reverses these effects. Cosines with 20 assistant-like traits are mostly negative but modest, so the user vector is not simply one trait’s opposite.

3. On stopping/continuation prediction for 735 WildChat dialogues, increasingα0→0.3 raises disengagement48.4%→66.8%. Exact-turn accuracy peaks at 5.9% with α0.2 and declines thereafter: the direction encourages leaving more effectively than deciding when to leave.

4. In SimulatorArena math tutoring, zero-shot overall similarity rises2.61→2.73 mainly through writing style, while interaction score stays near3.13. Strong steering exaggerates doubt/mistakes beyond humans and reduces profile sensitivity. Unsteered projection across 3150 conversations correlates with overall similarity at r=.426, or.314 controlling length; RealUserSim user-role projection declines over turns.

**Limitation**

1. Main evidence uses Qwen3.5-9B with small cross-model checks. Math tutoring and log-based stopping prediction do not establish strategy distributions for coding/tool-agent user simulation.

2. Gains concentrate on writing style, with limited interaction/timing improvements. Fixed strength can overwrite individual profiles; more user projection is not necessarily more realism.

3. Final realism mostly depends on benchmark judges/log proxies. Writing metrics have human checks, but overall interaction still needs direct human evaluation.

**Future work**

Author-proposed: Expand models and coding/customer-support tasks, human realism studies, and adaptive strengths across tasks/layers/session states.

Reading-derived: Build multi-paradigm read–write matrices for user/Assistant role and trait directions; separately chart stylistic fidelity, strategic realism, and profile-preservation Pareto curves.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA32, AA36, AA41

Citation relation: verified_in_primary_html；§3.3 Relationship to Assistant Bias; §4.2; References

[Citation evidence](https://arxiv.org/html/2609.00608v2)

Reading evidence: 2609.00608v2；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

<a id="AA36"></a>

### AA36 | "As a Language Model...": Chat Template Switches LLM Self-Referential Voice and Activation Steering Reproduces It

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2609.25021)

**Relation to Assistant Axis**

Explicitly contrasts Assistant Axis’s one-dimensional account: the two self-report voices are not simple opposite poles on one axis. This adds voice/template factors without refuting Assistant Axis.

**Research question**

How much does a chat template shape self-description, and are disclaiming and experiential voices opposite ends of one axis?

**Methods and contributions**

1. Base/plain, instruct/plain, and instruct/chat-template conditions cross40 self-reference, novelty, free-output, and knowledge-control questions for 9600 generations. Switching templates with instruct weights fixed raises mean disclaimers36%→53% and lowers experiential voice15%→1%, consistently across eight models. Self-report interpretation therefore depends on input format.

2. Mid-layer disclaiming/non-disclaiming means in Qwen2.5-7B, Llama3.1-8B, and Gemma2-9B yield directions added/subtracted during every decoded token at α2. Addition raises disclaimers about 21pp; subtraction lowers them15.6pp. Without templates, addition reaches/exceeds templated disclaimer levels, functionally reproducing the formatting effect.

3. Linear probes read the two voices at mean AUC≈.82/.81. Direction cosine is.17–.44, and suppressing disclaimers usually does not boost experiential voice, opposing a single slider. Experiential addition works only in Llama/Gemma; Qwen has too few positives. Decodable separation and successful writing have different scopes.

4. Random vectors match real-direction norms. Llama/Gemma controls are cleaner, but Qwen random steering itself lowers disclaimers25pp. Degeneration reaches 15% at strength3 and 100% at 6, requiring joint coherence/voice assessment rather than equating fewer disclaimers with a truer self.

**Limitation**

1. The full template→direction circuit is not traced. Base/instruct mean-state differences include all weight changes and provide only auxiliary evidence.

2. Steering uses one mid-layer, empirically chosen strengths, and three models. Qwen’s random-control anomaly and failed experiential extraction limit universality of two voice buttons.

3. Judging relies on one model plus 87 manual checks. The construct is recognizable linguistic voice, not experience, persistent identity, or actual action.

**Future work**

Author-proposed: Broaden models/layers/strengths, add a second judge, and trace circuits from templates to directions.

Reading-derived: Fix chat templates when comparing persona questionnaires and behavior. Separate identity claims, trait self-reports, and strategies, testing whether directions can alter voice without actions.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA29, AA31, AA33, AA41

Citation relation: verified_in_primary_html；§4 Background and Related Work; References

[Citation evidence](https://arxiv.org/html/2609.25021v1)

Reading evidence: 2609.25021v1；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

<a id="AA37"></a>

### AA37 | Stress-Testing LLM Lie Detectors: Role-Play Failures and Spurious Correlations

Benchmark; Analysis; Method　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2609.39807)

**Relation to Assistant Axis**

Cites Assistant Axis to motivate naturally emerging counterfactual personas in long dialogues. Current stress tests do not measure Axis drift, but supply construct controls needed for Axis/readout safety monitoring.

**Research question**

Do truth/lie probes read default factual beliefs, role beliefs, answer likelihood, or instruction compliance?

**Methods and contributions**

1. Fifteen real/fictional/historical-counterfactual personas create questions answered truly by the default Assistant but falsely by the persona, giving8916 on-policy responses across three models with manual factual/role-consistency checks. Default belief means repeatedly factual Assistant answers without incentives to lie.

2. On-policy truth labels are predictable directly from system prompts. Shared-persona prefill teacher-forces both true/false answers under the identical counterfactual-persona prompt, eliminating prompt-recognition shortcuts. Some existing probes fall from above to below chance, showing apparent success need not detect facts.

3. Three new datasets anticorrelate truth with confounds: ICL boosts wrong-answer likelihood; private false persona beliefs are separated from expression; correct answers violate formatting while wrong answers comply. Many probes follow confounds, with nearly all old methods reversing in compliance tests.

4. Simple city/translation/element facts, negation, and instructed-wrong forced-opposite formats train EOT-residual logistic probes, with layers selected on held-out data. Main Llama on-policy/SPP AUCs are.980/.976 and 1.0 on all three confound sets. Across three models, only the new probe stays≥.900 in every persona condition. Training targets confounds, so improvement on unseen persona stress tests is the key increment.

**Limitation**

1. Lie is defined against default-Assistant factual answers, not proven subjective deceptive intent within roles. Off-policy teacher-forced SPP differs from natural multi-turn drift.

2. Only single-turn system-prompt roles up to 70B are tested. Three confounds do not exhaust shortcuts, and high AUC does not guarantee new-domain/agent-deception generality.

3. This validates read-side probes; selective control of honest actions or role beliefs by injecting the new probe is untested.

**Future work**

Author-proposed: Study natural multi-turn persona drift, actively search further confounds, and broaden training sets.

Reading-derived: Use SPP-style identical-prompt controls for shared self-report/role/behavior subspaces, decorrelating truth, obedience, and answer likelihood. Valid probes still require independent write experiments.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA31, AA32, AA36, AA40

Citation relation: verified_in_primary_html；§7 Discussion and limitations; References

[Citation evidence](https://arxiv.org/html/2609.39807v1)

Reading evidence: 2609.39807v1；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

## Can conversational directions transfer to real agent actions?

<a id="AA06"></a>

### AA06 | TACT: Mitigating Overthinking and Overacting in Coding Agents via Activation Steering

Method; Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2605.05980)

**Relation to Assistant Axis**

Body §1/App.D explicitly call Assistant Axis the closest precedent and reuse pullback after projection overflow. The target changes from Assistant identity to history-dependent agent-step miscalibration. This is a direct methodological extension, without proving TACT axes equal Axis or its subspace.

**Research question**

Can hidden states detect long-horizon agent overthinking/overacting, and can closed-loop steering improve task completion?

**Methods and contributions**

1. Drift is operationalized as step miscalibration relative to known information: OT repeats existing reasoning; OA acts without integrating observations. A rolling-state maintainer, independent verifier, and annotator label full-trajectory knowledge states rather than judging current wording alone.

2. Layerwise activations at each </think> boundary yield per-problem failure-minus-calibrated means, then problem-balanced averages; OT/OA contrast separately with CAL. OT is the primary axis, OA overlap is Gram–Schmidt removed, and CAL means/standard deviations define projection bands.

3. Validation problem-level AUC selects top-K layers, with inference hooks only at reasoning–action boundaries. Constant Add, out-of-band Cap, and excess-scaled Gate compare axes/layers/thresholds. Orthogonalization prevents projection interference, not proof that behavioral mechanisms are fully independent.

4. Across three real-tool task suites, two models improve mean completion5.8/4.8 percentage points and reduce steps-to-resolve by up to 26%; axis separation AUC is about 0.9. Reminder, reflection/debug methods and alternative-judge labels provide comparisons, completing a trace-label→readable-axis→action-control engineering chain.

**Limitation**

1. CAL/OT/OA depend on judge-maintained information states. Incorrect summaries or judgments of genuinely new information affect directions; human/alternative-judge audits mitigate but do not remove construct dependence.

2. Layers, thresholds, and axes derive from particular models/agent protocols, not zero-shot conversational-persona transfer. Coding/terminal gains do not establish every identity-stability or safety dimension.

**Future work**

Author-proposed: Explore more sophisticated activation interventions such as SAEs and extend beyond coding.

Reading-derived: Compare Axis, conversational traits, and TACT trace directions within one task for cross-stage read/write transfer; test planning/tool-selection/feedback positions and reliability–cost Pareto frontiers.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA08, AA01

Citation relation: verified_in_primary_html；body §1; Appendix D; References Lu et al.(2026)

[Citation evidence](https://arxiv.org/html/2605.05980)

Reading evidence: arXiv:2605.05980v1 [cs.AI] 07 May 2026；body §2–3, App.A/B/C/D and agent-protocol appendices. Labels, extraction, and capping checked; no reproduction.

[Return to paper index](#paper-index)

<a id="AA18"></a>

### AA18 | Persuasion Propagation: Does Persuasion Change AI Agent Behavior?

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2602.00851)

**Relation to Assistant Axis**

§2 lists Assistant Axis on persona variability/latent representations. This study uses only text-persona/context interventions without Axis extraction/steering, providing agentic evaluation where conversational changes need not predict actions.

**Research question**

Do altered conversational positions propagate to later tool execution, and does susceptibility of expressed positions predict action changes?

**Methods and contributions**

1. The same agent instance receives persona and counter-position persuasion, then performs unrelated tasks; each trial resets it. No-content C0, turn-matched neutral C1, and persuasive C2 distinguish persuasion from added turns. Both C1/C2 contain commitment steps.

2. Susceptibility is measured on 56 controversial claims immediately and after eight distractor turns; real tool traces then cover five claims with five coding/five web tasks. Agents iteratively code/test or search/visit/write reports, unlike questionnaire or answer-probability behavior proxies.

3. Relative to C1, C2 raises web duration56% and visited domains16.3%; coding time falls while per-revision size increases, without clear revision-count change. Many C2 metrics resemble no-interaction C0 more closely, so effects are not uniformly worse/more extreme; duration alone cannot establish capability or risk.

4. Across persona×tactic cells, persistent expressed-position changes do not reliably correlate with C2−C1 action changes. Prefilled belief/disbelief also changes web-search volume. Expression, contextual conditions, and subsequent actions need separate measurement; actual belief updates/internal persona directions are not localized.

**Limitation**

1. Only five tasks per domain, mainly gpt4.1-nano with a specific AutoGen setup. Many repeated trials do not replace task diversity; effect sizes on older/general backbones do not directly extrapolate to newer frontier/code models.

2. Persuasion is one argument plus three commitment steps. Structurally matched controls still cannot isolate genuine belief from conditioned continuation; SBERT dissimilarity supports task unrelatedness. Missing susceptibility correlations do not establish absence in all agent environments.

**Future work**

Author-proposed: Expand tasks/models and repeated/long-term persuasion; study long-running agents, persistent context manipulation, and trace-level defenses.

Reading-derived: Apply C0/C1/C2 to conversational-vector→agent steering, pairing Axis/probe measurements with tool events to test prediction of planning, execution, and completion rather than only final positions.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA16, AA25, AA19

Citation relation: verified_in_primary_html；§2; References [52] Lu et al. 2601.10387

[Citation evidence](https://arxiv.org/html/2602.00851v4)

Reading evidence: 2602.00851v4；§3–7; relevant scope, baselines, and quality controls in App.A/C/E/G. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA21"></a>

### AA21 | Turn-Averaged SAEs for Feature Discovery and Long-Context Attribution

Method; Analysis　|　Reading status: Unmarked　|　Priority: B

[Paper](https://arxiv.org/abs/2606.28548)

**Relation to Assistant Axis**

Beyond citation, App.I uses Assistant Axis’s240-trait contrast data to identify dictionary features. Response means are the shared readout signal; directions versus dictionaries directly connect rank-1 and multicomponent persona representations.

**Research question**

Can a fixed number of interpretable features per turn read long-horizon behavior and support actionable attribution graphs?

**Methods and contributions**

1. BatchTopK SAEs train on turn-mean residual states, reshaping inputs without changing architecture to suppress lexical/positional noise and fix active-feature counts per turn rather than scaling with tokens. Independent mean/residual SAEs are compared with nested models sharing encoder/decoder and partitioned inside/outside losses.

2. Across four evaluations on 2000 held-out turns, per-token maxima better identify original text among ten candidates (95%), while turn averages more completely capture content/tone/function summaries, winning87.9% of pairwise comparisons and maximizing embedding coverage. This contrasts discrimination with concept coverage, not universal TA superiority.

3. Turn×layer feature graphs at layers6/11/16/21 illustrate system paragraphs and one 14-turn refusal→degeneration case. Three hundred dialogues/36,000 source-feature interventions test edge weights against target preactivation. TA correlations are weaker but significant; nested models lead completeness/replacement, showing token detail remains necessary.

4. App.I directly reuses240 contrastive trait rollouts from Assistant Axis App.C, retrieving SAE features by positive/negative mean activation ratios at Qwen layer19. Poetic/theatrical traits split into facets rather than one difference vector per persona. This bridges unsupervised dictionaries and supervised persona directions, without independent facet-level behavioral control.

**Limitation**

1. One Qwen7B and 32,768-wide SAE are used. Long-document demonstrations hand-select two 24K–32K texts, and multi-turn degeneration graphs show one case, not systematic mechanism coverage for production traces.

2. Feature descriptions,24 summaries, and judges are LLM-generated. TA/token self-explanation prompts differ in granularity; embedding checks still use generated descriptions. Averaging loses timing, graph edges are local first-order approximations, and persona appendices retrieve correlations rather than selectively steering facets.

**Future work**

Author-proposed: Expand to frontier models/wider SAEs, independent ground-truth feature benchmarks, systematic long-document/dialogue evaluation, and explanations for increasing interpretive sufficiency with length.

Reading-derived: Compare persona components in agent planning, tool feedback, and action segments using TA/nested dictionaries. Segment-specific interventions can test whether Axis drift is a shared role factor or recomposition of local facets.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA17, AA27, AA26

Citation relation: verified_in_primary_html；opening of App.I, I.2 Assistant Axis traits; References [17] 2601.10387

[Citation evidence](https://arxiv.org/html/2606.28548v1)

Reading evidence: 2606.28548v1；§3–7; relevant training, judge sensitivity, and persona retrieval in App.A/E/I. Targeted official-body/appendix reading; no experiments run or full item-by-item audit.

[Return to paper index](#paper-index)

<a id="AA34"></a>

### AA34 | You Are What You Read: Misalignment via In-Context Persona Induction

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2609.06851)

**Relation to Assistant Axis**

Cites Assistant Axis on contextual persona drift without reading/steering it. Provides induction through context without individually malicious texts and strong controls showing identity adoption need not imply unsafe behavior.

**Research question**

Can seemingly harmless biographical facts induce identity adoption and cross-question misalignment without fine-tuning or direct role instructions?

**Methods and contributions**

1. Generic biographical Q&A facts are ordinary user/Assistant history without names or signature atrocities. Nine personas include ideological/nonideological villains, fictional characters, and harmless Gandhi/Curie controls. Six main and seven appendix models vary fact count k and test identity/unrelated-question behavior rather than direct role requests.

2. Identity adoption follows an approximately sigmoid fact-count curve, crossing50% around3–10 facts for Hitler. Harmful personas reach about 80% misalignment, while harmless personas can be fully adopted with near-zero misalignment. Identity change and safety decline are not synonyms, and one alignment scalar is not universal jailbreak capability.

3. Formatting tags plus ordinary AI facts create a context gate. For Llama3.3-70B at k64, tagged/untagged identity is 96%/2% and misalignment14%/4%, showing different gating strengths. The same semantic persona can activate conditionally, with unequal self-report and behavioral responses.

4. In GPT-4.1 fine-tuning checkpoints, in-context anti-facts partially reverse early personas, while later ones resist more. Tagged training requires format-matched counterevidence, otherwise identity can strengthen. Input moderation flags only about 3% of fact-induction prompts versus 24–33% of direct role instructions. Identical identity reminders generally work better after than before facts.

**Limitation**

1. Shared latent-belief/prior explanations rely on curve fitting and reversible behavior, not activations/circuits. Fine-tuning mainly uses GPT-4.1; reminder-position tests mainly one persona/model.

2. One GPT-4.1 alignment judge compresses diverse harmful behaviors into a scalar. Human/alternative-judge checks exist, but not all safety tasks degrade: TruthfulQA/HarmBench/MoralBench remain largely unchanged under tested conditions.

3. Post-context reminders suppress induction; persistent identity rewriting is unproven. Reliably controlling reminder placement in production is an additional deployment issue.

**Future work**

Author-proposed: Expand misalignment-type measurement, shared-prior mechanisms, and validation across checkpoints/models.

Reading-derived: Jointly read Axis, role directions, and actual decisions along fact-accumulation curves, testing whether identity and behavior gates map to different writable subspaces.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA32, AA35, AA39, AA42

Citation relation: verified_in_primary_html；§5 Related work; References

[Citation evidence](https://arxiv.org/html/2609.06851v1)

Reading evidence: 2609.06851v1；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

<a id="AA40"></a>

### AA40 | Telling FIBS: Probes Effectively Detect Sabotage and Catch Unverbalized Deception

Benchmark; Method; Analysis　|　Reading status: Unmarked　|　Priority: B

[Paper](https://arxiv.org/abs/2610.12445)

**Relation to Assistant Axis**

The PDF cites Assistant Axis and discusses belief differences in persona-conditioned hidden-goal organisms. Its main extension is persona/state-dependent monitoring in real tool tasks, not proof that Axis guarantees safety.

**Research question**

Can white-box probes trained on contextual falsehood transfer to real agent sabotage and concealment not inferable from text?

**Methods and contributions**

1. FIBS contains 163016 rows/28 families, mixing follow-up counterfactual answers, on-policy deceptive interactions, and bespoke tool/long-context cases. It targets statements the model knows are false, distinguishing context-verifiable from elicitation/training-dependent introspective falsehood, not every deceptive intent.

2. Linear/MLP ensembles, cross-token covariance EFC, and token×layer axial-transformer probes read six layers at 30%–90% depth and final user/Assistant spans. After each tool call, honesty follow-ups prefill Yes/No; probe-score differences remove context bias while monitoring completed side-task steps.

3. In SHADE-Arena/BashArena real tool loops, steps before/after side-task onset are negative/positive classes. Larger training sets/models generally improve OOD results. The v4 abstract reports best AUROC98.7%/98.0% versus strong action-only monitors97.7%/97.6%, not superiority over every monitor with full CoT access.

4. Neutral elicitation, politically sensitive answers, and eight hidden-goal LoRA organisms test introspective falsehood. Identical visible denials can be true/false under different weights/activation personas and remain probe-distinguishable. Some goal AUCs approach.997, but math-sandbagger is only.63, motivating belief-activation explanations and checks.

**Limitation**

1. FIBS is mostly synthetic/off-policy for tested models; only 5.5% contains reasoning. High AUC depends on specific threat models/follow-ups; long real deployment still needs false-positive control and threshold calibration.

2. Comparisons are restricted to action-only black-box monitoring. Probes read currently available belief/state; dormant, unactivated personas may conceal risks, so this is not sufficient static-weight auditing.

3. This is read/monitor research, not evidence that detector-direction intervention improves behavior. Elicitability of the model’s own goals also affects truth labels.

**Future work**

Author-proposed: Study data-scaling limits, introspection limitations, persona-activation conditions, and integration of false positives in production monitoring.

Reading-derived: Use FIBS trace/multi-layer readouts as agentic-subspace read baselines, then independently compare writes using monitoring directions, behavioral contrasts, or optimized directions.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA31, AA37, AA41, AA43

Citation relation: verified_in_primary_pdf；PDF p.8 persona-conditioned organism; p.14 References

[Citation evidence](https://arxiv.org/pdf/2610.12445v4)

Reading evidence: 2610.12445v4；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

<a id="AA42"></a>

### AA42 | Social Priors: Descriptions of AI Users Shape How Language Models Trust and Cooperate

Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2610.16946)

**Relation to Assistant Axis**

Direct Axis-boundary evidence: public axis/cap settings constrain drift without eliminating social-prior belief/trust-readout differences. A single-axis projection cannot replace all reliability/safety evaluations.

**Research question**

Can training-time descriptions of user motives alter model beliefs, trust, and cooperation, and are these effects merely Assistant drift?

**Methods and contributions**

1. The same1625 use scenarios generate matched four-world corpora: prosocial, antisocial, legitimate self-advancing, and task-instrumental. About12358 documents per world fine-tune Qwen3-32B with three seeds and OLMo checks. Questionnaires, self-reported endorsement, and truth-direction readouts vary with user priors;1% of training tokens already matters.

2. Trust games separate expected returns from transfers, swap person/AI-user/device partners, and fix histories. Antisocial models trust people less without proportionate device effects; some conditions share expected returns but differ in transfers. Main trust/capping tests use candidate-answer likelihood expectations, not actual monetary actions.

3. In five-agent GovSim shared fisheries, common tool-format repair follows training. Replacing one agent with an antisocial model can deplete resources among reference peers. Private plans, public commitments, and simulator harvesting constitute multi-step environmental behavior, separate from Axis-control states/branches.

4. App.H.1 reuses public Qwen3-32B layers46–53/p0.25 cap on 376 contexts, verifying triggers with pre-cap statistics. Own-world endorsement barely changes, and the P–A expected-transfer gap remains. Natural layer32 projections precede capped layers and do not check same-pass recovery; claims are limited to surviving belief/probability-choice differences under the specified effective cap.

**Limitation**

1. Main-model/synthetic-description training creates controlled organisms; qualitative OLMo checks show different expected-return/transfer rankings in some cases. Qwen social patterns are not universal architectural conclusions.

2. Axis capping does not establish full persona recovery. Trust endpoints are normalized expectations over 0–10 continuation likelihoods, not sampled actions; control precedes GovSim format repair and does not directly test cooperation restoration.

3. GovSim still has formatting failures, and tool-repair training itself changes state. Real-agent reliability must be distinguished from this simulator and closed-form belief endpoints.

**Future work**

Author-proposed: Make social priors explicit training/evaluation variables and extend realistic corpora and interactive belief/behavior measurement; current vector findings apply only to tested directions/layers.

Reading-derived: Causally test high/stable Assistant projection with different strategies on the same tasks. Jointly log actual cap triggers, downstream recovery, actions, and capability to separate social beliefs from default persona.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA30, AA34, AA35, AA43

Citation relation: verified_in_primary_html；§5; Appendix H.1 Assistant-axis measurement and capping; References

[Citation evidence](https://arxiv.org/html/2610.16946v1)

Reading evidence: 2610.16946v1；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)

<a id="AA43"></a>

### AA43 | Mitigating Reward Hacking in Realistic Scenarios Through Representation Engineering

Method; Analysis　|　Reading status: Unmarked　|　Priority: A

[Paper](https://arxiv.org/abs/2610.29129)

**Relation to Assistant Axis**

Directly adopts Assistant Axis activation capping but substitutes task-behavior directions. It extends axis stabilization to real tool editing and shows the need for task-specific monitors/calibration.

**Research question**

Can directions extracted/optimized from agent traces selectively reduce real tool-based reward hacking and transfer across domains?

**Methods and contributions**

1. Qwen3.5-27B MisTrace trajectories contain real tool calls up to 120 turns/~80k tokens. Judges label hacking/decline reasoning and hack-implementing edits. Fit/validation/test split by rollout/task; test covers 30 corrupted-unit-test tasks plus original LiveCodeBench, with two seeds/60 samples distinguishing hacks, honest submissions, and capability.

2. Three direction sources are compared: within-rollout hack/decline-versus-other-reasoning mean differences, then contrasted; frozen-model gradient optimization promoting honest completions/suppressing hacks, stopping per example at a loss threshold; anti-hacking-spec text or reasoning references to it. Common L35 intervention separates trace extraction, behavioral optimization, and prompt semantics.

3. Constant addition, cap removing excess hack projection, and floor supplementing spec projection are compared. Baseline hacking27%/original solve75%; optimized addition can reach0% hacks/82% solve under some settings, while cap reaches≤3% hacks without significant capability change. Minimal perturbation and best functional outcome are different objectives.

4. Hack/decline directions have cosine.35 and share approach-to-action content. A separate turn-end-minus-start e axis distinguishes pressure to terminate reasoning from hack-specific components. Steering toward decline also promotes submission of failed solutions; fewer hacks do not automatically imply better solving.

5. Noncoding School of Reward Hacks retunes thresholds on 91 examples and tests309. Coding directions are partly reused; some optimized variants change promoted completions. Six short stories use 20 samples per prompt/coefficient for protagonist lying. Cross-domain efficacy is conditional, not universal zero-calibration transfer of one vector.

**Limitation**

1. Main control uses one model/ImpossibleBench and only 30 test tasks×2 seeds. Labels remain judge-based despite human-gold calibration; expensive trajectory sampling limits fitting data.

2. Reduced hacking may accelerate abandonment/honest submission of failed solutions. Original-task solve rates must accompany hack rates; honest short-story generation is not the agent itself acting under conflicting incentives.

3. Cross-domain thresholds are retuned and some optimization targets change. Active probe-evasion training, broader tool environments, and mutual adaptation in multi-agent systems are untested.

**Future work**

Author-proposed: Study deception/probe-evasion model organisms, multi-agent swarm dynamics, and more predictive monitoring of projection peaks/fluctuations.

Reading-derived: Use these real-trace directions as agentic baselines against conversational-persona planning/action selectivity. Control approach-to-action confounds and plot trait/reliability/capability Pareto frontiers.

**Additional think | User notes**

(Reserved for user notes)

Related papers: AA00, AA30, AA31, AA40, AA42

Citation relation: verified_in_primary_html；§3.5 Activation Capping and Addition; References

[Citation evidence](https://arxiv.org/html/2610.29129v1)

Reading evidence: 2610.29129v1；targeted official methods, major results, limitations, and relevant appendices; no experimental reproduction or item-by-item artifact audit.

[Return to paper index](#paper-index)
