[English](README.md) | [Tiếng Việt](README.vi.md)

# Relay-kit

Relay-kit là một hệ điều hành quy trình làm việc cho các đội ngũ xây dựng bằng coding agent.

Nó không cố làm cho model "thông minh thần kỳ" hơn. Nó làm cho cách làm việc có nguyên tắc hơn.

Khi dùng Relay-kit, agent sẽ có:

- điểm bắt đầu rõ ràng hơn
- bộ kỹ năng dùng lại được tốt hơn
- cách plan, build, debug, và review chặt hơn
- các artifact dùng chung để công việc không chỉ nằm trong chat memory

Kết quả rất thực tế: agent làm việc có cấu trúc hơn, bớt hành động ngẫu hứng hơn, và có bằng chứng tốt hơn trước khi được gọi là xong.

## Cài và dùng nhanh (GitHub)

Dành cho người dùng chỉ cần cài và chạy ngay:

```bash
pipx install "git+https://github.com/b0ydeptraj/Relay-kit.git"
relay-kit "C:\\path\\to\\my-app" --codex
relay-kit "C:\\path\\to\\my-app" --claude
relay-kit "C:\\path\\to\\my-app" --antigravity
```

Mỗi lần chạy chỉ chọn một cờ adapter.

## Vì sao nên dùng Relay-kit

Phần lớn workflow cho agent hỏng ở những chỗ giống nhau:

- bắt đầu làm khi vấn đề còn chưa rõ
- phần code đi lệch khỏi hướng đã chốt
- bug bị vá tạm mà không tìm nguyên nhân gốc
- công việc bị gọi là "xong" khi chưa có đủ bằng chứng

Relay-kit được tạo ra để chặn đúng các chỗ đó.

Nó dành cho:

- người làm một mình nhưng dùng coding agent nghiêm túc
- team sản phẩm và kỹ thuật muốn đầu ra lặp lại được
- người đang dùng Claude, Codex, hoặc workflow kiểu Antigravity nhưng cần nhiều hơn một bộ prompt

Relay-kit cho họ một đường đi rõ ràng cho:

- việc mới
- sửa lỗi
- review
- chốt hoàn thành

Nói ngắn: nó khiến agent bớt làm việc kiểu ứng biến, và làm việc gần với một kỹ sư có quy trình hơn.

## Bạn nhận được gì

- một mặt kỹ năng công khai nhỏ, dễ nhớ
- runtime skills dùng lại được cho `.claude`, `.agent`, và `.codex`
- các artifact workflow dùng chung trong `.relay-kit/`
- utility `memory-search` dạng read-only để tra quyết định và handoff cũ
- utility `release-readiness` để gate pre/post deploy và theo dõi rollback signal
- gate `accessibility-review` để chặn thiếu sót a11y trước khi gọi là ready
- gate `skill-gauntlet` để giữ hành vi routing của skill ổn định
- utility `context-continuity` cho checkpoint, rehydrate, handoff, và diff
- một baseline đang hoạt động và đã được kiểm, không phải bộ skill ghép rời rạc
- một cách làm việc ổn định hơn mà không phải nhét mọi thứ vào chat memory

## Bắt đầu nhanh

Xem skill và bundle hiện có:

```bash
python relay_kit.py --list-skills
```

Generate baseline đang hoạt động:

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

Cài trực tiếp từ GitHub:

```bash
pipx install "git+https://github.com/b0ydeptraj/Relay-kit.git"
relay-kit /path/to/project --codex
```

Wrapper public map:
- `--codex` -> `--ai codex`
- `--claude` -> `--ai claude`
- `--antigravity` -> `--ai antigravity` (runtime target hiện tại: `.agent/skills`)

Kiểm tra runtime contract:

```bash
python scripts/validate_runtime.py
```

## Start flow

Nếu chỉ nhớ vài cái tên, hãy nhớ các tên này:

| Mục tiêu | Tên công khai | Hậu trường |
|---|---|---|
| tìm đúng đường bắt đầu | `start-here` | `workflow-router` |
| biến ý tưởng mơ hồ thành hướng rõ | `brainstorm` | `brainstorm-hub` |
| biến việc đã chốt thành các bước có thể làm | `write-steps` | `scrum-master` |
| triển khai phần việc đã được duyệt | `build-it` | `developer` |
| review branch hoặc PR trước khi merge hoặc sign-off | `review-pr` | `review-hub` |
| gỡ lỗi mà không đoán mò | `debug-systematically` | `debug-hub` + `root-cause-debugging` |
| quyết định xem công việc đã thật sự sẵn sàng chưa | `ready-check` | `review-hub` + `qa-governor` |
| ép kiểm tra bằng chứng lần cuối | `prove-it` | `evidence-before-completion` |

Đường mặc định cho việc mới:

1. `start-here`
2. `brainstorm`
3. `write-steps`
4. `build-it`
5. `ready-check`

Đường mặc định cho bug:

1. `start-here`
2. `debug-systematically`
3. `build-it`
4. `ready-check`

Đường mặc định cho review branch/PR:

1. `review-pr`
2. `ready-check` nếu cần một verdict thật sự về readiness hoặc shipability
3. `prove-it` nếu claim "xong" vẫn nghe mạnh hơn phần bằng chứng

Xem chi tiết hơn:
- [`docs/relay-kit-start-flow.md`](docs/relay-kit-start-flow.md)
- [`docs/relay-kit-review-flow.md`](docs/relay-kit-review-flow.md)
- [`docs/relay-kit-memory-search.md`](docs/relay-kit-memory-search.md)
- [`docs/relay-kit-release-readiness.md`](docs/relay-kit-release-readiness.md)
- [`docs/relay-kit-accessibility-review.md`](docs/relay-kit-accessibility-review.md)
- [`docs/relay-kit-skill-gauntlet.md`](docs/relay-kit-skill-gauntlet.md)
- [`docs/relay-kit-context-continuity.md`](docs/relay-kit-context-continuity.md)
- [`docs/relay-kit-5min-quickstart.md`](docs/relay-kit-5min-quickstart.md)
- [`docs/relay-kit-beta-soak-log.md`](docs/relay-kit-beta-soak-log.md)
- [`docs/relay-kit-release-gate-snapshot-2026-04-17.md`](docs/relay-kit-release-gate-snapshot-2026-04-17.md)

## Nó hoạt động như thế nào

Relay-kit tách công việc thành một số chặng ổn định:

1. chọn đúng đường đi
2. làm rõ yêu cầu hoặc điều tra lỗi
3. chia nhỏ thành bước an toàn
4. thực thi có bằng chứng
5. review trước khi gọi là xong

Ở bên dưới, hệ thống dùng runtime skills cùng với state, contracts, references, và docs trong `.relay-kit/`.

## Cấu hình

Entrypoint chính:

- `relay_kit.py`
- `relay_kit_legacy.py`

Baseline đang hoạt động:

- `baseline`

Sau khi generate, bạn sẽ có:

- `.codex/skills/`
- `.claude/skills/`
- `.agent/skills/`
- `.relay-kit/contracts/`
- `.relay-kit/state/`
- `.relay-kit/references/`
- `.relay-kit/docs/`

Generate tất cả adapter cùng lúc với `--ai all`:

```bash
python relay_kit.py . --bundle baseline --ai all
```

## Trạng thái migration

Phase 3 cutover đã bật và canonical runtime path hiện tại là:

- `relay_kit.py`
- `relay_kit_legacy.py`
- `.relay-kit/`
- `.relay-kit-prompts/`

Nhật ký lịch sử compatibility và removal:
- [`docs/history/relay-kit-compatibility-cycle.md`](docs/history/relay-kit-compatibility-cycle.md)

## Tài liệu sâu hơn

- Start flow:
  - [`docs/relay-kit-start-flow.md`](docs/relay-kit-start-flow.md)
- Review flow:
  - [`docs/relay-kit-review-flow.md`](docs/relay-kit-review-flow.md)
- Memory retrieval utility:
  - [`docs/relay-kit-memory-search.md`](docs/relay-kit-memory-search.md)
- Release readiness và deploy smoke:
  - [`docs/relay-kit-release-readiness.md`](docs/relay-kit-release-readiness.md)
- Accessibility gate:
  - [`docs/relay-kit-accessibility-review.md`](docs/relay-kit-accessibility-review.md)
- Skill behavior gauntlet:
  - [`docs/relay-kit-skill-gauntlet.md`](docs/relay-kit-skill-gauntlet.md)
- Context continuity:
  - [`docs/relay-kit-context-continuity.md`](docs/relay-kit-context-continuity.md)
  - [`docs/relay-kit-context-continuity-design-note.md`](docs/relay-kit-context-continuity-design-note.md)
- Cấu trúc thư mục:
  - [`.relay-kit/docs/folder-structure.md`](.relay-kit/docs/folder-structure.md)
- Luật bundle:
  - [`.relay-kit/docs/bundle-gating.md`](.relay-kit/docs/bundle-gating.md)

## Ghi chú về legacy

Legacy kits vẫn còn để phục vụ migration và compatibility. Chúng không phải là câu chuyện runtime chính của Relay-kit.

