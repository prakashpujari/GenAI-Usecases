# Neo4j Healthcare Diagnosis Demo

Simple demo showing how to store a small healthcare graph in Neo4j and use a Streamlit UI to ask symptom-based questions and visualize relations.

## Step-by-step setup

**Prerequisites:**
- Python 3.8+ installed
- Neo4j running and reachable (local Neo4j Desktop, Docker container, or Aura)

**Environment variables (recommended):**
- `NEO4J_URI` (default: `bolt://localhost:7687`)
- `NEO4J_USER` (default: `neo4j`)
- `NEO4J_PASSWORD` (default: `neo4j`)

You can export these in your shell or place them in a `.env` file (keep secrets out of git).

**1. Create and activate virtual environment (Windows PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**2. Seed the Neo4j database:**

Run the provided seed script to create constraints and sample nodes/relationships:

```powershell
python seed_db.py
```

**3. Run the Streamlit UI:**

```powershell
streamlit run streamlit_app.py
```

Open the URL Streamlit prints in your browser. Use the sidebar to select or type symptoms and click "Find possible diagnoses".

## Files overview
- `seed_db.py`: populates a small healthcare graph (nodes: `Disease`, `Symptom`, `Treatment`).
- `streamlit_app.py`: Streamlit app that queries Neo4j using symptoms and visualizes related nodes.
- `requirements.txt`: project dependencies.
- `.gitignore`: ignores virtual environments, `.env`, and editor/OS artifacts.
- `STEP_BY_STEP.md`: supplementary step-by-step document (more detail).

## Important Cypher fix applied
Issue observed: Neo4j raised a syntax error when `size()` was used on a pattern expression, e.g. `size((d)-[:HAS_SYMPTOM]->())`.

Fix applied: replaced pattern-based `size()` with `count()` and an `OPTIONAL MATCH`. The query now computes matched counts and total symptom counts like this:

```cypher
MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
WHERE s.name IN $symptoms
WITH d, collect(DISTINCT s.name) AS matched, count(DISTINCT s.name) AS matchedCount
OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(sym2:Symptom)
WITH d, matched, matchedCount, count(DISTINCT sym2) AS totalSymptoms
RETURN d.name AS disease, matched, matchedCount, totalSymptoms
ORDER BY matchedCount DESC, disease
```

This avoids using `size()` on patterns and works with modern Cypher.

## Troubleshooting
- Connection errors: verify `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and that Bolt is enabled on the Neo4j instance.
- Empty symptom list: ensure `seed_db.py` ran successfully and that `Symptom` nodes exist in the DB.

## Security / Git notes
- `.gitignore` excludes `.env` and `.streamlit/secrets.toml` — do not commit credentials.
- Consider adding a `.env.example` with placeholder variable names (no secrets).

## Next suggestions
- Pin dependency versions in `requirements.txt` for reproducible installs.
- Add more sample data and richer relationships for a better demo.

If you want, I can add a `.env.example` template and a small PowerShell script to automate venv creation, seeding, and app launch.
