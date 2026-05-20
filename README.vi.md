[English](README.md) | [Tiếng Việt](README.vi.md)

# Relay-kit

![Hệ thống runtime skill của Relay-kit](docs/site/assets/relay-kit-hero.svg)

Relay-kit là hệ thống runtime skill cho các team xây dựng bằng coding agent.

Nó không cố làm model “thông minh thần kỳ” hơn. Nó làm cách làm việc có kỷ luật hơn: khởi động rõ hơn, dùng skill có hợp đồng hơn, plan/build/debug/review chặt hơn, và giữ bằng chứng trong artifact thay vì chỉ nằm trong chat.

## Cài nhanh

```bash
pipx install "git+https://github.com/b0ydeptraj/Relay-kit.git"
relay-kit init "C:\\path\\to\\my-app" --codex
relay-kit locale set "C:\\path\\to\\my-app" --locale vi
relay-kit doctor "C:\\path\\to\\my-app"
```

Mỗi lần chạy chỉ chọn một adapter: `--codex`, `--claude`, hoặc `--antigravity`. Có thể dùng `--all` khi muốn sinh cả ba surface.

Mặc định Relay-kit cài full governance bundle. Tên bundle vẫn là `enterprise` để giữ tương thích CLI, còn bằng chứng release/support bên ngoài được tách vào readiness JSON thay vì biến thành claim trên README. Dùng `--baseline` nếu muốn surface nhỏ hơn.

## Vì sao dùng Relay-kit

Workflow agent thường hỏng ở các điểm giống nhau:

- bắt đầu làm khi vấn đề còn mơ hồ
- implementation lệch khỏi hướng đã chốt
- bug bị vá tạm mà không tìm nguyên nhân gốc
- “done” được claim trước khi có đủ bằng chứng

Relay-kit chặn các điểm đó bằng routing, skill contracts, state chung, readiness gates, và proof audit.

## Bạn nhận được gì

- runtime skills cho `.codex`, `.claude`, và `.agent`
- artifact chung trong `.relay-kit/`
- `memory-search` để tìm lại quyết định và handoff cũ
- `context audit`, `lane audit`, `adapter diagnose`, `command diagnose`, và `agent diagnose`
- `release-readiness`, `accessibility-review`, `skill-gauntlet`, và `context-continuity`
- local context engine cho path, symbol, import, test, docs, chunk, call hint, git history, SQLite FTS, active context, và MCP local mà không cần API key
- `battle-audit`, `battle-benchmark`, `skill-battle`, và `competency-battle` để bắt resource còn generic, đo chất lượng tìm context, và chấm điểm từng skill theo competency evidence
- `repo-profile` để phân loại repo theo archetype như backend API, frontend app, CLI tool, automation worker, database-heavy, security/policy, docs/product, library core, hoặc test runner
- `readiness check` cho local governance proof
- Pulse report và signal export để review chất lượng

## Hệ thống skill cốt lõi

Mặt tiền public nên nói về phần Relay-kit mạnh nhất: routing, context, battle proof, adapter governance, và readiness gate.

| Lớp runtime | Skill / lệnh nổi bật | Việc nó làm |
| --- | --- | --- |
| Định tuyến intent | `workflow-router`, `repo-map`, `prompt enhance` | biến yêu cầu ngắn hoặc mơ hồ thành hướng ask / scout / act rõ ràng, kèm file cần đọc trước |
| Hiểu codebase local | `context index`, `context search`, `context related`, `context explain-symbol` | tìm path, symbol, test, docs, config, call hint, và active context ngay trong máy, không cần API key |
| Triển khai code | `developer`, `fix-hub`, `execution-loop`, `test-first-development` | giữ thay đổi gọn, có test, và bám vào cấu trúc repo thật |
| Debug và review | `debug-hub`, `root-cause-debugging`, `review-hub`, `qa-governor` | đi từ triệu chứng sang bằng chứng, rồi từ bằng chứng sang verdict rõ ràng |
| Chuyên môn kỹ thuật | `api-integration`, `data-persistence`, `dependency-management`, `testing-patterns`, `go-service-engineering`, `next-product-frontend` | áp dụng competency pattern đã battle-test cho backend, frontend, dependency, và testing |
| Proof gate | `policy-guard`, `runtime-doctor`, `skill-gauntlet`, `readiness check`, `skill-battle`, `competency-battle` | kiểm adapter, skill behavior, governance local, và giới hạn claim |

Các extension pack chuyên biệt vẫn có trong catalog kỹ thuật, nhưng không phải câu chuyện chính ở README. Trang đầu phải làm người đọc thấy Relay-kit là runtime skill system có kỷ luật, không phải một danh sách skill rời rạc.

## Lệnh hữu ích

```bash
relay-kit --list-skills
relay-kit init /path/to/project --all
relay-kit manifest write /path/to/project
relay-kit manifest stamp /path/to/project --issuer relay-kit --channel enterprise
relay-kit doctor /path/to/project --policy-pack enterprise
relay-kit upgrade mark-current /path/to/project --adapter all
relay-kit readiness check /path/to/project --profile enterprise --json
```

Khi local gate sạch, verdict là `local-governance-ready-candidate`. Khi có bằng chứng remote CI, release, support, hoặc user validation thì gắn vào readiness output.

## Prove skill behavior

```bash
relay-kit eval real-world /path/to/project --strict --json
relay-kit proof audit /path/to/project --strict --json
relay-kit eval battle-audit /path/to/project --strict --json
relay-kit eval battle-benchmark /path/to/project --suite deep --cleanup --json
relay-kit eval skill-battle /path/to/project --skill all --suite deep --cleanup --json
relay-kit eval competency-battle /path/to/project --skill all --suite core --json
relay-kit eval repo-profile /path/to/project --json
relay-kit eval domain-pack list /path/to/project --json
relay-kit eval skill-weakness-report /path/to/project --json
```

`eval real-world`, `battle-benchmark`, `skill-battle`, và `competency-battle` là evidence gate, không phải badge marketing. Chúng kiểm tra Relay-kit có tìm đúng file, symbol, test, evidence term, competency pattern, và overclaim trap trong suite hiện tại hay không.

Verdict local sạch là `local-governance-ready-candidate`. Bằng chứng release bên ngoài được tách vào output readiness dạng máy đọc, để README tập trung vào thứ Relay-kit thật sự ship: routing, context, skill, adapter, và proof gate local.

## Local context engine

```bash
relay-kit context index /path/to/project
relay-kit context search /path/to/project --query "login"
relay-kit context related /path/to/project --path src/auth/LoginForm.tsx
relay-kit context explain-symbol /path/to/project --symbol login
relay-kit context active set /path/to/project --file src/auth/LoginForm.tsx --selection "submit handler"
relay-kit context mcp /path/to/project --list-tools
```

Base install chạy local bằng JSON + SQLite FTS + lexical/graph scoring. Optional `relay-kit[context]` có thể thêm `fastembed` và `tree-sitter`, nhưng không bắt buộc và không dùng API trả phí.

## Runtime utility wrappers

```bash
relay-kit runtime doctor /path/to/project --strict
relay-kit skill gauntlet /path/to/project --strict --semantic
relay-kit impact radar /path/to/project --json
relay-kit accessibility review /path/to/project --surface "checkout-flow"
relay-kit release readiness /path/to/project --phase both
relay-kit continuity checkpoint /path/to/project --next-step "resume review"
relay-kit migration guard /path/to/project --strict
```

## Start flow

| Mục tiêu | Tên công khai | Hậu trường |
|---|---|---|
| tìm đường bắt đầu | `start-here` | `workflow-router` |
| làm rõ ý tưởng | `brainstorm` | `brainstorm-hub` |
| chia việc đã chốt | `write-steps` | `scrum-master` |
| triển khai slice | `build-it` | `developer` |
| review branch hoặc PR | `review-pr` | `review-hub` |
| debug có kỷ luật | `debug-systematically` | `debug-hub` + `root-cause-debugging` |
| chốt readiness thật | `ready-check` | `review-hub` + `qa-governor` |
| ép proof pass cuối | `prove-it` | `evidence-before-completion` |

## Tài liệu sâu hơn

- [`docs/site/index.md`](docs/site/index.md)
- [`docs/public-docs-index.md`](docs/public-docs-index.md)
- [`docs/relay-kit-start-flow.md`](docs/relay-kit-start-flow.md)
- [`docs/relay-kit-review-flow.md`](docs/relay-kit-review-flow.md)
- [`docs/relay-kit-readiness-check.md`](docs/relay-kit-readiness-check.md)
- [`docs/relay-kit-skill-gauntlet.md`](docs/relay-kit-skill-gauntlet.md)
- [`docs/relay-kit-context-continuity.md`](docs/relay-kit-context-continuity.md)
- [`docs/relay-kit-template-policy.json`](docs/relay-kit-template-policy.json)
