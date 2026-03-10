# Rollout Order

1. Add `skills.manifest.yaml`.
2. Add the 8 new skills under `templates/skills/`.
3. Keep existing experts unchanged in the first pass.
4. Add command shims:
   - `/cook` -> cook
   - `/debug` -> debug
   - `/review` -> review
   - `/plan` -> plan
5. Later, tighten broad skills (`backend-development`, `web-frameworks`) only after you observe routing confusion.
6. After the single-agent flow is stable, consider adding `team` and `bootstrap`.
