# Project Guidelines

## Architecture

- Keep `LayoutScene`, camera, mesh preparation, and picking independent of Qt and
  external data sources. Scenes are immutable snapshots.
- Keep source/session adapters outside the renderer; pass captured data as a
  `LayoutScene`.
- Keep Qt window orchestration in `qt/ui/` and GPU rendering in `qt/render/`.
  The renderer must not depend on window or panel code.
- When changing capture or incremental updates, keep scene data, prepared
  geometry, and picking behavior consistent.

## Code and Tests

- Follow the existing Python style, type annotations, and validation patterns.
- Add focused pytest coverage for behavior changes, especially scene invariants,
  camera transforms, picking, capture, and incremental updates.
- Run `uv run pytest`; use `QT_QPA_PLATFORM=offscreen uv run pytest` in
  headless environments.
- After editing shader sources, regenerate shader packs with
  `uv run python tools/bake_viewer_shaders.py`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the module map, dependency boundaries,
development setup, and additional testing notes.
