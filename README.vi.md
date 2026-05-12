[English](README.md) | [Tiáº¿ng Viá»‡t](README.vi.md)

# Relay-kit

Relay-kit lÃ  má»™t há»‡ Ä‘iá»u hÃ nh quy trÃ¬nh lÃ m viá»‡c cho cÃ¡c Ä‘á»™i ngÅ© xÃ¢y dá»±ng báº±ng coding agent.

NÃ³ khÃ´ng cá»‘ lÃ m cho model "thÃ´ng minh tháº§n ká»³" hÆ¡n. NÃ³ lÃ m cho cÃ¡ch lÃ m viá»‡c cÃ³ nguyÃªn táº¯c hÆ¡n.

Khi dÃ¹ng Relay-kit, agent sáº½ cÃ³:

- Ä‘iá»ƒm báº¯t Ä‘áº§u rÃµ rÃ ng hÆ¡n
- bá»™ ká»¹ nÄƒng dÃ¹ng láº¡i Ä‘Æ°á»£c tá»‘t hÆ¡n
- cÃ¡ch plan, build, debug, vÃ  review cháº·t hÆ¡n
- cÃ¡c artifact dÃ¹ng chung Ä‘á»ƒ cÃ´ng viá»‡c khÃ´ng chá»‰ náº±m trong chat memory

Káº¿t quáº£ ráº¥t thá»±c táº¿: agent lÃ m viá»‡c cÃ³ cáº¥u trÃºc hÆ¡n, bá»›t hÃ nh Ä‘á»™ng ngáº«u há»©ng hÆ¡n, vÃ  cÃ³ báº±ng chá»©ng tá»‘t hÆ¡n trÆ°á»›c khi Ä‘Æ°á»£c gá»i lÃ  xong.

## CÃ i vÃ  dÃ¹ng nhanh (GitHub)

DÃ nh cho ngÆ°á»i dÃ¹ng chá»‰ cáº§n cÃ i vÃ  cháº¡y ngay:

```bash
pipx install "git+https://github.com/b0ydeptraj/Relay-kit.git"
relay-kit "C:\\path\\to\\my-app" --codex
relay-kit "C:\\path\\to\\my-app" --claude
relay-kit "C:\\path\\to\\my-app" --antigravity
```

Má»—i láº§n cháº¡y chá»‰ chá»n má»™t cá» adapter.

## VÃ¬ sao nÃªn dÃ¹ng Relay-kit

Pháº§n lá»›n workflow cho agent há»ng á»Ÿ nhá»¯ng chá»— giá»‘ng nhau:

- báº¯t Ä‘áº§u lÃ m khi váº¥n Ä‘á» cÃ²n chÆ°a rÃµ
- pháº§n code Ä‘i lá»‡ch khá»i hÆ°á»›ng Ä‘Ã£ chá»‘t
- bug bá»‹ vÃ¡ táº¡m mÃ  khÃ´ng tÃ¬m nguyÃªn nhÃ¢n gá»‘c
- cÃ´ng viá»‡c bá»‹ gá»i lÃ  "xong" khi chÆ°a cÃ³ Ä‘á»§ báº±ng chá»©ng

Relay-kit Ä‘Æ°á»£c táº¡o ra Ä‘á»ƒ cháº·n Ä‘Ãºng cÃ¡c chá»— Ä‘Ã³.

NÃ³ dÃ nh cho:

- ngÆ°á»i lÃ m má»™t mÃ¬nh nhÆ°ng dÃ¹ng coding agent nghiÃªm tÃºc
- team sáº£n pháº©m vÃ  ká»¹ thuáº­t muá»‘n Ä‘áº§u ra láº·p láº¡i Ä‘Æ°á»£c
- ngÆ°á»i Ä‘ang dÃ¹ng Claude, Codex, hoáº·c workflow kiá»ƒu Antigravity nhÆ°ng cáº§n nhiá»u hÆ¡n má»™t bá»™ prompt

Relay-kit cho há» má»™t Ä‘Æ°á»ng Ä‘i rÃµ rÃ ng cho:

- viá»‡c má»›i
- sá»­a lá»—i
- review
- chá»‘t hoÃ n thÃ nh

NÃ³i ngáº¯n: nÃ³ khiáº¿n agent bá»›t lÃ m viá»‡c kiá»ƒu á»©ng biáº¿n, vÃ  lÃ m viá»‡c gáº§n vá»›i má»™t ká»¹ sÆ° cÃ³ quy trÃ¬nh hÆ¡n.

## Báº¡n nháº­n Ä‘Æ°á»£c gÃ¬

- má»™t máº·t ká»¹ nÄƒng cÃ´ng khai nhá», dá»… nhá»›
- runtime skills dÃ¹ng láº¡i Ä‘Æ°á»£c cho `.claude`, `.agent`, vÃ  `.codex`
- cÃ¡c artifact workflow dÃ¹ng chung trong `.relay-kit/`
- utility `memory-search` dáº¡ng read-only Ä‘á»ƒ tra quyáº¿t Ä‘á»‹nh vÃ  handoff cÅ©
- utility `release-readiness` Ä‘á»ƒ gate pre/post deploy vÃ  theo dÃµi rollback signal
- gate `accessibility-review` Ä‘á»ƒ cháº·n thiáº¿u sÃ³t a11y trÆ°á»›c khi gá»i lÃ  ready
- gate `skill-gauntlet` Ä‘á»ƒ giá»¯ hÃ nh vi routing cá»§a skill á»•n Ä‘á»‹nh
- utility `context-continuity` cho checkpoint, rehydrate, handoff, vÃ  diff
- má»™t baseline Ä‘ang hoáº¡t Ä‘á»™ng vÃ  Ä‘Ã£ Ä‘Æ°á»£c kiá»ƒm, khÃ´ng pháº£i bá»™ skill ghÃ©p rá»i ráº¡c
- má»™t cÃ¡ch lÃ m viá»‡c á»•n Ä‘á»‹nh hÆ¡n mÃ  khÃ´ng pháº£i nhÃ©t má»i thá»© vÃ o chat memory

## Báº¯t Ä‘áº§u nhanh

Xem skill vÃ  bundle hiá»‡n cÃ³:

```bash
python relay_kit.py --list-skills
```

Generate baseline Ä‘ang hoáº¡t Ä‘á»™ng:

```bash
python relay_kit.py . --bundle baseline --ai codex --emit-contracts --emit-docs --emit-reference-templates
```

Public installer surface (khi checkout repo local):

```bash
pipx install .
relay-kit /path/to/project --codex
relay-kit /path/to/project --claude
relay-kit /path/to/project --antigravity
```

CÃ i trá»±c tiáº¿p tá»« GitHub:

```bash
pipx install "git+https://github.com/b0ydeptraj/Relay-kit.git"
relay-kit /path/to/project --codex
```

Wrapper public map:
- `--codex` -> `--ai codex`
- `--claude` -> `--ai claude`
- `--antigravity` -> `--ai antigravity` (runtime target hiá»‡n táº¡i: `.agent/skills`)

Kiá»ƒm tra runtime contract:

```bash
python scripts/validate_runtime.py
```

## Start flow

Náº¿u chá»‰ nhá»› vÃ i cÃ¡i tÃªn, hÃ£y nhá»› cÃ¡c tÃªn nÃ y:

| Má»¥c tiÃªu | TÃªn cÃ´ng khai | Háº­u trÆ°á»ng |
|---|---|---|
| tÃ¬m Ä‘Ãºng Ä‘Æ°á»ng báº¯t Ä‘áº§u | `start-here` | `workflow-router` |
| biáº¿n Ã½ tÆ°á»Ÿng mÆ¡ há»“ thÃ nh hÆ°á»›ng rÃµ | `brainstorm` | `brainstorm-hub` |
| biáº¿n viá»‡c Ä‘Ã£ chá»‘t thÃ nh cÃ¡c bÆ°á»›c cÃ³ thá»ƒ lÃ m | `write-steps` | `scrum-master` |
| triá»ƒn khai pháº§n viá»‡c Ä‘Ã£ Ä‘Æ°á»£c duyá»‡t | `build-it` | `developer` |
| review branch hoáº·c PR trÆ°á»›c khi merge hoáº·c sign-off | `review-pr` | `review-hub` |
| gá»¡ lá»—i mÃ  khÃ´ng Ä‘oÃ¡n mÃ² | `debug-systematically` | `debug-hub` + `root-cause-debugging` |
| quyáº¿t Ä‘á»‹nh xem cÃ´ng viá»‡c Ä‘Ã£ tháº­t sá»± sáºµn sÃ ng chÆ°a | `ready-check` | `review-hub` + `qa-governor` |
| Ã©p kiá»ƒm tra báº±ng chá»©ng láº§n cuá»‘i | `prove-it` | `evidence-before-completion` |

ÄÆ°á»ng máº·c Ä‘á»‹nh cho viá»‡c má»›i:

1. `start-here`
2. `brainstorm`
3. `write-steps`
4. `build-it`
5. `ready-check`

ÄÆ°á»ng máº·c Ä‘á»‹nh cho bug:

1. `start-here`
2. `debug-systematically`
3. `build-it`
4. `ready-check`

ÄÆ°á»ng máº·c Ä‘á»‹nh cho review branch/PR:

1. `review-pr`
2. `ready-check` náº¿u cáº§n má»™t verdict tháº­t sá»± vá» readiness hoáº·c shipability
3. `prove-it` náº¿u claim "xong" váº«n nghe máº¡nh hÆ¡n pháº§n báº±ng chá»©ng

Xem chi tiáº¿t hÆ¡n:
- [`docs/relay-kit-start-flow.md`](docs/relay-kit-start-flow.md)
- [`docs/relay-kit-review-flow.md`](docs/relay-kit-review-flow.md)
- [`docs/relay-kit-memory-search.md`](docs/relay-kit-memory-search.md)
- [`docs/relay-kit-release-readiness.md`](docs/relay-kit-release-readiness.md)
- [`docs/relay-kit-accessibility-review.md`](docs/relay-kit-accessibility-review.md)
- [`docs/relay-kit-skill-gauntlet.md`](docs/relay-kit-skill-gauntlet.md)
- [`docs/relay-kit-context-continuity.md`](docs/relay-kit-context-continuity.md)

## NÃ³ hoáº¡t Ä‘á»™ng nhÆ° tháº¿ nÃ o

Relay-kit tÃ¡ch cÃ´ng viá»‡c thÃ nh má»™t sá»‘ cháº·ng á»•n Ä‘á»‹nh:

1. chá»n Ä‘Ãºng Ä‘Æ°á»ng Ä‘i
2. lÃ m rÃµ yÃªu cáº§u hoáº·c Ä‘iá»u tra lá»—i
3. chia nhá» thÃ nh bÆ°á»›c an toÃ n
4. thá»±c thi cÃ³ báº±ng chá»©ng
5. review trÆ°á»›c khi gá»i lÃ  xong

á»ž bÃªn dÆ°á»›i, há»‡ thá»‘ng dÃ¹ng runtime skills cÃ¹ng vá»›i state, contracts, references, vÃ  docs trong `.relay-kit/`.

## Cáº¥u hÃ¬nh

Entrypoint chÃ­nh:

- `relay_kit.py`

Baseline Ä‘ang hoáº¡t Ä‘á»™ng:

- `baseline`
- hcd bundle runtime: `core`, `orchestration`, `runtime`

Sau khi generate, báº¡n sáº½ cÃ³:

- `.codex/skills/`
- `.claude/skills/`
- `.agent/skills/`
- `.relay-kit/contracts/`
- `.relay-kit/state/`
- `.relay-kit/references/`
- `.relay-kit/docs/`

Generate táº¥t cáº£ adapter cÃ¹ng lÃºc vá»›i `--ai all`:

```bash
python relay_kit.py . --bundle baseline --ai all
```

## Tráº¡ng thÃ¡i migration

Phase 3 cutover Ä‘Ã£ báº­t vÃ  canonical runtime path hiá»‡n táº¡i lÃ :

- `relay_kit.py`
- `.relay-kit/`
- `.relay-kit-prompts/`

Nháº­t kÃ½ lá»‹ch sá»­ compatibility vÃ  removal:

## TÃ i liá»‡u sÃ¢u hÆ¡n

- Start flow:
  - [`docs/relay-kit-start-flow.md`](docs/relay-kit-start-flow.md)
- Review flow:
  - [`docs/relay-kit-review-flow.md`](docs/relay-kit-review-flow.md)
- Memory retrieval utility:
  - [`docs/relay-kit-memory-search.md`](docs/relay-kit-memory-search.md)
- Release readiness vÃ  deploy smoke:
  - [`docs/relay-kit-release-readiness.md`](docs/relay-kit-release-readiness.md)
- Accessibility gate:
  - [`docs/relay-kit-accessibility-review.md`](docs/relay-kit-accessibility-review.md)
- Skill behavior gauntlet:
  - [`docs/relay-kit-skill-gauntlet.md`](docs/relay-kit-skill-gauntlet.md)
- Context continuity:
  - [`docs/relay-kit-context-continuity.md`](docs/relay-kit-context-continuity.md)
  - [`docs/relay-kit-context-continuity-design-note.md`](docs/relay-kit-context-continuity-design-note.md)
- Cáº¥u trÃºc thÆ° má»¥c:
  - [`.relay-kit/docs/folder-structure.md`](.relay-kit/docs/folder-structure.md)
- Luáº­t bundle:
  - [`.relay-kit/docs/bundle-gating.md`](.relay-kit/docs/bundle-gating.md)
