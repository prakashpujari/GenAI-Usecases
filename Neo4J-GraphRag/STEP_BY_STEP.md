# Step-by-step setup and summary

This document explains what was added to the repository, how to set up the environment, seed the Neo4j demo data, run the Streamlit UI, and notes about the small Cypher fix applied.

1) Files added
- `seed_db.py`: populates a small healthcare graph with `Disease`, `Symptom`, and `Treatment` nodes and relationships.
- `streamlit_app.py`: Streamlit UI to query Neo4j by symptoms and visualize related nodes.
- `requirements.txt`: Python dependencies.
- `.gitignore`: ignores virtualenvs, secrets, IDE folders, etc.
- `README.md`: quick start instructions.
- `STEP_BY_STEP.md`: this document.

2) Prerequisites
- Python 3.8+ installed.
- Neo4j running and accessible (local Neo4j Desktop, Docker container, or Aura).

3) Environment variables (choose one approach)
- Export environment variables in your shell:

```powershell
setx NEO4J_URI "bolt://localhost:7687"
setx NEO4J_USER "neo4j"
setx NEO4J_PASSWORD "yourpassword"
```

- Or create a `.env` or Streamlit secrets file (keep them out of git). Example `.env` content:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword
```

4) Create and activate a virtual environment (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

5) Seed the Neo4j database

Run:

```powershell
python seed_db.py
```

This creates unique constraints and merges a few sample diseases and relationships.

6) Run the Streamlit UI

```powershell
streamlit run streamlit_app.py
```

Open the provided local URL from Streamlit in your browser. Use the sidebar to select or type symptoms and click "Find possible diagnoses".

7) Cypher fix applied
- Problem: Neo4j reported a syntax error when `size()` was used with a pattern expression (size((d)-[:HAS_SYMPTOM]->())).
- Fix: replaced the pattern-based `size()` with `count()` using an `OPTIONAL MATCH`. The query now computes `matchedCount` via `count(DISTINCT s.name)` and computes `totalSymptoms` via:

```
OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(sym2:Symptom)
WITH d, matched, matchedCount, count(DISTINCT sym2) AS totalSymptoms
```

This avoids using `size()` on a pattern and is compatible with modern Cypher.

8) Git / security notes
- `.gitignore` was added to exclude virtual environments, `.env`, and `.streamlit/secrets.toml`.
- Add your own `.env.example` if you'd like to commit a template without secrets.

9) Troubleshooting
- Neo4j connection errors: verify `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` and that Neo4j accepts Bolt connections on that host/port.
- If the Streamlit app shows empty symptom list, ensure `seed_db.py` ran without errors and that Neo4j contains `Symptom` nodes.

10) Next suggestions (optional)
- Add `--no-dev` or pinned versions to `requirements.txt` for reproducible installs.
- Add `.env.example` and update `README.md` with example secrets usage.
- Add more sample data and enrich the graph for better demo coverage.

If you want, I can add a `.env.example` and a short `Makefile`/PowerShell script to automate the steps above.
