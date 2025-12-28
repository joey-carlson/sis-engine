# Streamlit Harness (v0.1)

Debug-first harness for the SiS Engine v0.1.

## Run (zsh)

From the repo root:

```zsh
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r streamlit_harness/requirements.txt
streamlit run streamlit_harness/app.py
```

### Notes

- The harness bootstraps `sys.path` so it can import `spar_engine` without requiring installation.
- If you prefer a more standard setup, you can also install the package in editable mode:

```zsh
pip install -e .
```

This harness is intentionally a development instrument, not a product UI.


Notes:
- Batch generation treats each event as a sequential step by default and ticks cooldowns between events to prevent exhausting the content pool.


## Scenario Runner

The harness includes a *Scenario Runner* tab that can run multi-run suites and download a Markdown/JSON report for tuning.


### HarnessState

The harness stores its UI + engine session state in a single `HarnessState` dataclass (`st.session_state.hs`). This prevents Streamlit rerun scoping bugs (e.g., `batch_n` NameError) from regressing.
