[English](README.md) | [Tiếng Việt](README.vi.md)

# Relay-kit

Relay-kit là hệ điều hành quy trình cho các team xây dựng bằng coding agent.

Nó không cố làm model "thông minh thần kỳ" hơn. Nó làm cách làm việc có kỷ luật hơn: khởi động rõ hơn, dùng skill có hợp đồng hơn, plan/build/debug/review chặt hơn, và giữ bằng chứng trong artifact thay vì chỉ nằm trong chat.

## Cài nhanh

```bash
pipx install "git+https://github.com/b0ydeptraj/Relay-kit.git"
relay-kit init "C:\\path\\to\\my-app" --codex
relay-kit locale set "C:\\path\\to\\my-app" --locale vi
relay-kit doctor "C:\\path\\to\\my-app"
```

Mỗi lần chạy chỉ chọn một adapter: `--codex`, `--claude`, hoặc `--antigravity`. Có thể dùng `--all` khi muốn sinh cả ba surface.

Mặc định Relay-kit cài full governance bundle. Tên bundle vẫn là `enterprise` để giữ tương thích CLI, nhưng local gate chỉ chứng minh độ phủ governance tại máy: chưa chứng minh private registry, upload release đã ký, vận hành paid support, hoặc user/field validation. Dùng `--baseline` nếu muốn surface nhỏ hơn.

## Vì sao dùng Relay-kit

Workflow agent thường hỏng ở các điểm giống nhau:

- bắt đầu làm khi vấn đề còn mơ hồ
- implementation lệch khỏi hướng đã chốt
- bug bị vá tạm mà không tìm nguyên nhân gốc
- "done" được claim trước khi có đủ bằng chứng

Relay-kit chặn các điểm đó bằng routing, skill contracts, state chung, readiness gates, và proof audit.

## Bạn nhận được gì

- runtime skills cho `.codex`, `.claude`, và `.agent`
- artifact chung trong `.relay-kit/`
- `memory-search` để tìm lại quyết định và handoff cũ
- `context audit`, `lane audit`, `adapter diagnose`, `command diagnose`, và `agent diagnose`
- `release-readiness`, `accessibility-review`, `skill-gauntlet`, và `context-continuity`
- `readiness check` cho local governance proof
- Pulse report và signal export để review chất lượng

## Domain Skill Pack

Full governance runtime có các domain skill do Relay-kit sở hữu:

- `go-service-engineering`
- `next-product-frontend`
- `growth-marketing`
- `market-research`
- `automation-ops`
- `vietnamese-product-localization`
- `mmo-reup-automation`
- `mmo-account-operations`
- `mmo-browser-fleet-automation`
- `mmo-social-marketing-automation`
- `mmo-lowcode-automation`
- `mmo-mobile-app-automation`
- `mmo-cloud-operations-automation`
- `mmo-http-api-automation`

Các skill này có contract riêng và không được copy nguyên xi từ kit bên ngoài. Các skill domain đang được mở rộng bằng `references/`, `examples/`, và `evals/`; chỉ thêm script khi có hành vi deterministic thật.

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

Khi local gate sạch, verdict là `local-governance-ready-candidate`. Trạng thái external evidence vẫn là `missing` cho tới khi có remote CI, release upload, paid support operation, và user hoặc field validation.

Prove skill behavior:

```bash
relay-kit eval real-world /path/to/project --strict --json
relay-kit proof audit /path/to/project --strict --json
```

Runtime utility wrappers:

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

- [`docs/public-docs-index.md`](docs/public-docs-index.md)
- [`docs/relay-kit-start-flow.md`](docs/relay-kit-start-flow.md)
- [`docs/relay-kit-review-flow.md`](docs/relay-kit-review-flow.md)
- [`docs/relay-kit-readiness-check.md`](docs/relay-kit-readiness-check.md)
- [`docs/relay-kit-skill-gauntlet.md`](docs/relay-kit-skill-gauntlet.md)
- [`docs/relay-kit-context-continuity.md`](docs/relay-kit-context-continuity.md)
- [`docs/relay-kit-template-policy.json`](docs/relay-kit-template-policy.json)
