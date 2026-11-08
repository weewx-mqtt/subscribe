# AGENTS.md

WeeWX extension "MQTTSubscribe": subscribes to MQTT topics and creates/updates WeeWX loop packets
and archive records. Works as both a WeeWX driver and a WeeWX service.

## Role & boundaries

- `bin/user/mqttcommon.py` is the paho mqtt code shared with the other weewx-mqtt extensions,
  vendored **verbatim**: never edit this copy. Subscribe uses both `Logger`/`LoggerThread` and
  `MessageThrottle`. Change it in the [mqttcommon](https://github.com/weewx-mqtt/mqttcommon)
  repository and sync; that repository's `AGENTS.md` has the procedure and the `MQTTCOMMON_API`
  bump ritual.
- `bin/user/MQTTSubscribe.py` is a deprecated backward-compat shim. Do not add features there; it
  must stay a copy of `main()` plus thin subclasses.

## Layout

- `bin/user/mqttsubscribe.py` — the main code: `MQTTSubscribeService`,
  `MQTTSubscribeDriver`, the payload parsers (`MessageCallbackProvider`), config validation
  (`MQTTSubscribeConfiguration`), and three CLI modes (`parse`, `simulate`, `configure`) runnable
  as `python3 bin/user/mqttsubscribe.py <mode> ...`.
- `bin/user/tests/{unit,func,integ,e2e}` — the four test suites (see Testing below).
- `mqttsubscribe.example.conf` — generated output of the config spec; regenerate rather than
  hand-edit.
- `pubmqtt.py` — publishes lines from `tmp/messages.txt` to a broker, for manual testing.
- `docs/` — Jekyll GitHub Pages site (published as weewx-mqtt.github.io/subscribe); the project
  README is `docs/readme.md`, not a root `README.md` (docs-first). `docs/_site` is generated —
  don't hand-edit it.
- `.vscode/launch.json` — working debug configs, including the CLI modes.

## Environment

Run everything from the repo root:

```bash
source .devenv
export PYTHONPATH="$WEEWX_PYTHONPATH"   # == bin, or bin:../weewx/src
```

- The module imports as `user.mqttsubscribe`, so `bin` must be on `PYTHONPATH`.
- WeeWX is not vendored. CI pip-installs it; locally `.devenv` uses the sibling checkout
  `../weewx` when WeeWX is not installed (WeeWX v5 uses `src/`, older releases use `bin/`).
  `.env` is the plain IDE form (`PYTHONPATH=bin:../weewx/bin:../weewx/src`).
- Helper scripts `unittests.sh`, `functests.sh`, `integtests.sh`, `e2etests.sh`, `alltests.sh`,
  `coverage.sh`, `lint.sh`, `verify.sh` live in `~/weewx_dev/weewx-extensions/development-tools/tools`
  (added to `PATH` by `.devenv`, which also sets `WEEWX_PYTHONPATH`/`WEEWX_PYENV_VERSION`).
  Source `.devenv` before using them. `verify.sh` is the full pre-commit gate.

## Commands

Four suites under `bin/user/tests/{unit,func,integ,e2e}`. Run one suite. Every suite has its own
`helpers.py`, so test files support `python <test file> [<TestClass> <test_method>]` as well
(the vendored `test_mqttcommon.py` keeps `unittest.main()`). Direct runs of func/integ still need
`PYTHONPATH` to reach weewx and the shared test modules.

```bash
# unit - weewx is stubbed (bin/user/tests/unit/test_weewx_stubs.py), no WeeWX install needed
PYTHONPATH=bin pytest bin/user/tests/unit

# unit, one file or one test, directly
python bin/user/tests/unit/test_RecordCache.py
python bin/user/tests/unit/test_Logger.py TestThrottling test_window_summary_is_logged

# func, integ, e2e - need real weewx importable
PYTHONPATH=bin:../weewx/bin:../weewx/src pytest bin/user/tests/func
PYTHONPATH=bin:../weewx/bin:../weewx/src pytest bin/user/tests/integ
PYTHONPATH=bin:../weewx/bin:../weewx/src pytest bin/user/tests/e2e

# Before committing: the same gate the CI runs.
source .devenv
~/weewx_dev/weewx-extensions/development-tools/tools/verify.sh
```

## Architecture / behavior

- Main code lives in one module: `bin/user/mqttsubscribe.py`. It contains `MQTTSubscribeService`,
  `MQTTSubscribeDriver`, the payload parsers (`MessageCallbackProvider`), config validation
  (`MQTTSubscribeConfiguration`), and three CLI modes (`parse`, `simulate`, `configure`).
- `MQTTSubscriber` derives its paho api variant with `mqttcommon.select_api()` — preserve paho
  v1+v2 callback API compatibility in any MQTT client changes.
- **Logging is message-id based.** Each class has a `log_messages` dict of numbered templates (the
  four thread-entry texts — 122002/122003/124003/124004 — live in `mqttcommon.Logger.log_messages`);
  log via `self.logger.trace/debug/info/error(<msg_id>, ...)` with a new unique id in that class's
  block. New user-facing messages should follow this pattern, not free-form logging.
- **Logging is asynchronous.** Those four methods only queue entries on `Logger.log_queue`; the
  `LoggerThread` (`Logger.log_thread`) is the sole consumer and runs the throttle
  (`Logger.throttle`, a `mqttcommon.MessageThrottle`; the config parse/validation is
  `mqttcommon.MessageThrottle.parse_config(config)`, called in `mqttcommon.Logger._configure`,
  and suppression summaries route back via `Logger._log_throttle_summary`. The 122001
  experimental-notice text is `MessageThrottle.NOTICE_EXPERIMENTAL`). The queue
  loop itself (daemon flag, thread rename, sentinel, error recovery) and the
  start/exit/invalid entries (built from `self.logger`, so the name and the archive
  timestamp stamp correctly) live in `mqttcommon.LoggerThread`. Subscribe has
  no local `Logger` class: `create_logger(name, throttle=None, level='NOTSET', filename=None, console=None)`
  is the single construction path; it passes the name and settings as ctor keywords, with the
  `'config'` (built from the throttle) switching on the subscribe-style setup in
  `mqttcommon.Logger._configure` (weewx_debug, the throttle, the TRACE level, the handlers, and
  the trace-level resolution, then the 122001 notice; `level` is validated in the ctor itself).
  The name is the mode (`Service`/`Driver`); `log_name` is `__name__`. The log line format is
  `mqttcommon.Logger`'s shared prefix — the component name, the emitting thread, and the archive
  record (appended only when one is being processed) — with no per-extension format configuration.
  The queue, the queue methods (`trace/debug/info/error`), the entry builder `create_entry`,
  the `log_functions` dispatch, `log_entry`, `log_environment`,
  `_setup_logging` (with its `get_handlers` helper), `is_suppressed` (the throttle gate — it
  delegates to the `MessageThrottle` built in `_configure`), `shutdown`, and the `_log_*` sinks
  all come from the shared skeleton. The one subscribe-owned piece of state is
  `logger.archive_timestamp`, an instance attr set by the NEW_ARCHIVE_RECORD/END_ARCHIVE_PERIOD
  event handlers and passed to `create_entry` at enqueue time (None omitted from
  the context). Flush with `Logger.shutdown()` - it is wired to `MQTTSubscribeService.shutDown()`
  and `MQTTSubscribeDriver.closePort()`. Tests that assert on log output must drain first
  (`SUT.shutdown()`), must not patch `user.mqttsubscribe.threading` (real threads are started),
  and construct with `create_logger as Logger` — the logging paths to patch are
  `user.mqttcommon.logging` and `user.mqttcommon.Logger`.

## Testing conventions and quirks

- All four suites use `helpers.run_tests()` (one `helpers.py` per suite): no arguments runs the
  file, `ClassName methodName` runs one test. The vendored `test_mqttcommon.py` keeps
  `unittest.main()` and must stay unmodified.
- Unit tests call `test_weewx_stubs.setup_stubs()` before importing `user.mqttsubscribe` and
  re-stub in `setUp`. If a new unit test skips this, it will import the real (missing) weewx or
  leak stub state. `test_weewx_stubs` and `utils` (integ) are imported as top-level modules —
  pytest's directory-based import handles this; there are no `__init__.py` files.
- The driver and service integration cases spawn their own mosquitto broker on a free port, so
  they do not touch a system broker on 1883; they are skipped when mosquitto is not installed.
  The parser cases (`test_get_data`, `test_get_accumulated_data`) need no broker.
- E2E is slow (~3 min: it runs simulated WeeWX time with a stubbed MQTT client) — don't run it for
  every iteration.
- Tests and debug without a broker: `simulate` mode
  (`python3 bin/user/mqttsubscribe.py simulate service|driver --conf ...`).

## Config, versioning and release

- `CONFIG_SPEC_TEXT` at the top of `mqttsubscribe.py` is the single source of truth for config
  validation, deprecation checks, and the generated default stanza. When adding/removing a config
  option, update `CONFIG_SPEC_TEXT` **and** the `remove_items` / `remove_more_items` maps in
  `MQTTSubscribeConfiguration.default_config` (it raises `19001` if an entry goes stale).
  `mqttsubscribe.example.conf` is generated output; regenerate rather than hand-edit.
- `VERSION` is duplicated in `bin/user/mqttsubscribe.py` and `install.py` — keep in sync.
- `changes.txt` is the changelog.
- Releases are tagged by `.github/workflows/versioning.yml` (Actions-Us/actions-tagger) on
  GitHub release publish.

## CI

- `.github/workflows/run-analyze-test.yml` (any non-master push) and
  `run-analyze-test-matrix.yml` (master pushes) delegate to reusable workflows in
  `weewx-extensions/development-tools@v6`. The `module-name: 'mqttsubscribe'` input selects the
  module under test.
- The master matrix covers WeeWX 5.0.0 / 5.5.2 / branch-master / branch-development ×
  Python 3.9.13–3.14 — code must stay compatible with **Python 3.9 syntax**. A separate job tests
  `paho-mqtt==1.6.1`.
- pylint: `pylint ./bin/user/mqttsubscribe.py ./bin/user/mqttcommon.py -r n` (CI's target via the
  `lint-paths` workflow input; locally `lint.sh` lints `bin/user/`). Config in `.pylintrc`. CI
  **fails the build** on pylint findings (`lint-fail` defaults to true in the v6 reusable
  workflow).
- flake8: config exists (`.flake8`: max-line-length 145, max-cognitive-complexity 10, ignores
  E302/E305/E402). CI runs it on the same `lint-paths` target and fails the build on findings.
- Coverage is measured from the unit suite only:
  `PYTHONPATH=bin coverage run --branch -m pytest bin/user/tests/unit`, then
  `coverage html/xml --include 'bin/user/*.py' --omit bin/user/__init__.py`.
- Markdown is linted with `.markdownlint.jsonc` (line length 150).

## Commits

Never commit, push, tag or release unless explicitly asked. A request to make a change is not
permission to commit it, and "do it" does not include committing. Propose the commit message and
wait for the go-ahead. Don't pre-stage; staged files are not a commit request (the user stages
while reviewing). Once approved, stage and commit that step in one go.

## Cross-repo workflow

Single changes stay in this repository. Cross-repo work (a shared change, rename, wording pass)
starts in the workspace root (`weewx-mqtt`): see the workspace `AGENTS.md` for the order of a
cross-repo change and `./status-all.sh` to see every repository's state at once.