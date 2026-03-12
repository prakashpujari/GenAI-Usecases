from __future__ import annotations

import json
import os
from typing import Any

import httpx
import streamlit as st

try:
    from neo4j import GraphDatabase
    from neo4j.graph import Node, Path, Relationship
except Exception:  # pragma: no cover - optional dependency path
    GraphDatabase = None
    Node = None
    Path = None
    Relationship = None


def _api_request(method: str, url: str, payload: dict[str, Any] | None = None) -> tuple[int, str, Any | None]:
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.request(method=method, url=url, json=payload)
    except Exception as exc:  # pragma: no cover - UI path
        return 0, f"Request failed: {exc}", None

    content_type = response.headers.get("content-type", "")
    data: Any | None = None
    message = response.text

    if "application/json" in content_type:
        try:
            data = response.json()
            message = json.dumps(data, indent=2)
        except json.JSONDecodeError:
            data = None

    return response.status_code, message, data


def _show_response(status: int, message: str, data: Any | None) -> None:
    if 200 <= status < 300:
        st.success(f"Success ({status})")
    elif status == 0:
        st.error(message)
        return
    else:
        st.error(f"Request failed ({status})")

    if data is not None:
        st.json(data)
    else:
        st.code(message)


def _safe_label(value: str) -> str:
    return value.replace('"', "'")


def _node_caption(node: Node) -> str:
    labels = sorted(list(node.labels))
    title = labels[0] if labels else "Node"
    for key in ("loanId", "borrowerId", "propertyId", "incomeId", "documentId", "name"):
        if key in node:
            return f"{title}\\n{node.get(key)}"
    return f"{title}\\n{node.element_id}"


def _collect_graph_elements(rows: list[dict[str, Any]]) -> tuple[dict[str, str], list[tuple[str, str, str]]]:
    nodes: dict[str, str] = {}
    edges: list[tuple[str, str, str]] = []

    def add_node(node: Node) -> None:
        node_id = str(node.element_id)
        nodes[node_id] = _node_caption(node)

    def add_rel(rel: Relationship) -> None:
        start_id = str(rel.start_node.element_id)
        end_id = str(rel.end_node.element_id)
        edges.append((start_id, end_id, rel.type))

    def walk(value: Any) -> None:
        if Path is not None and isinstance(value, Path):
            for node in value.nodes:
                add_node(node)
            for rel in value.relationships:
                add_rel(rel)
            return
        if Node is not None and isinstance(value, Node):
            add_node(value)
            return
        if Relationship is not None and isinstance(value, Relationship):
            add_node(value.start_node)
            add_node(value.end_node)
            add_rel(value)
            return
        if isinstance(value, list):
            for item in value:
                walk(item)
            return
        if isinstance(value, dict):
            for item in value.values():
                walk(item)

    for row in rows:
        for v in row.values():
            walk(v)

    return nodes, edges


def _to_jsonable(value: Any) -> Any:
    if Path is not None and isinstance(value, Path):
        return {
            "type": "Path",
            "length": len(value.relationships),
            "nodes": [
                {
                    "id": str(n.element_id),
                    "labels": list(n.labels),
                    "properties": dict(n.items()),
                }
                for n in value.nodes
            ],
            "relationships": [
                {
                    "id": str(r.element_id),
                    "type": r.type,
                    "start": str(r.start_node.element_id),
                    "end": str(r.end_node.element_id),
                    "properties": dict(r.items()),
                }
                for r in value.relationships
            ],
        }
    if Node is not None and isinstance(value, Node):
        return {
            "type": "Node",
            "id": str(value.element_id),
            "labels": list(value.labels),
            "properties": dict(value.items()),
        }
    if Relationship is not None and isinstance(value, Relationship):
        return {
            "type": "Relationship",
            "id": str(value.element_id),
            "relType": value.type,
            "start": str(value.start_node.element_id),
            "end": str(value.end_node.element_id),
            "properties": dict(value.items()),
        }
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    return value


def _run_neo4j_query(uri: str, user: str, password: str, database: str, query: str) -> tuple[bool, str, list[dict[str, Any]]]:
    if GraphDatabase is None:
        return False, "Neo4j driver is not installed in this environment. Install package 'neo4j'.", []

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session(database=database) as session:
            result = session.run(query)
            rows = [dict(record.items()) for record in result]
        driver.close()
        return True, f"Returned {len(rows)} row(s).", rows
    except Exception as exc:  # pragma: no cover - UI path
        return False, f"Neo4j query failed: {exc}", []


def _render_graphviz(nodes: dict[str, str], edges: list[tuple[str, str, str]]) -> None:
    lines = [
        "digraph G {",
        "  rankdir=LR;",
        "  graph [bgcolor=white];",
        "  node [shape=box, style=filled, fillcolor=\"#f3f7ff\", color=\"#5b7ee5\"];",
        "  edge [color=\"#4f5b77\"];",
    ]

    for node_id, label in nodes.items():
        lines.append(f'  "{_safe_label(node_id)}" [label="{_safe_label(label)}"];')

    for start_id, end_id, rel_type in edges:
        lines.append(
            f'  "{_safe_label(start_id)}" -> "{_safe_label(end_id)}" [label="{_safe_label(rel_type)}"];'
        )

    lines.append("}")
    st.graphviz_chart("\n".join(lines), use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Mortgage Graph UI", layout="wide")
    st.title("Mortgage Graph Platform UI")
    st.caption("Interact with ingest, risk, and explain endpoints from a simple local UI.")

    default_api_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
    api_base_url = st.sidebar.text_input("API base URL", value=default_api_url).rstrip("/")
    st.sidebar.write("Use your running FastAPI endpoint, for example http://127.0.0.1:8000")

    st.subheader("Health")
    if st.button("Check API health"):
        status, message, data = _api_request("GET", f"{api_base_url}/health")
        _show_response(status, message, data)

    ingest_tab, risk_tab, explain_tab, graph_tab = st.tabs(["Ingest Loan", "Risk", "Explain", "Graph Explorer"])

    with ingest_tab:
        st.write("Submit a loan bundle to /loans/ingest")
        with st.form("ingest_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                borrower_id = st.text_input("Borrower ID", value="B100")
                borrower_name = st.text_input("Borrower Name", value="Alex Chen")
                ssn_hash = st.text_input("SSN Hash", value="hash-100")
                dob = st.text_input("DOB (YYYY-MM-DD)", value="1987-03-10")
            with c2:
                loan_id = st.text_input("Loan ID", value="L100")
                amount = st.number_input("Amount", min_value=0.0, value=450000.0, step=1000.0)
                status_value = st.text_input("Loan Status", value="submitted")
                purpose = st.text_input("Purpose", value="purchase")
                origination_date = st.text_input("Origination Date", value="2026-02-01")
                ltv = st.number_input("LTV", min_value=0.0, value=78.0, step=0.5)
                dti = st.number_input("DTI", min_value=0.0, value=39.0, step=0.5)
            with c3:
                property_id = st.text_input("Property ID", value="P100")
                address = st.text_input("Address", value="1 Main St")
                city = st.text_input("City", value="Austin")
                state = st.text_input("State", value="TX")
                zip_code = st.text_input("ZIP", value="73301")
                property_type = st.text_input("Property Type", value="single_family")

            st.markdown("---")
            st.write("Income")
            i1, i2, i3 = st.columns(3)
            with i1:
                income_id = st.text_input("Income ID", value="I100")
                income_type = st.text_input("Income Type", value="w2")
            with i2:
                employer_name = st.text_input("Employer Name", value="Contoso")
                annual_income = st.number_input("Annual Income", min_value=0.0, value=175000.0, step=1000.0)
            with i3:
                start_date = st.text_input("Income Start Date", value="2020-01-01")

            st.markdown("---")
            st.write("One sample document")
            d1, d2, d3, d4 = st.columns(4)
            with d1:
                document_id = st.text_input("Document ID", value="D100")
            with d2:
                document_type = st.text_input("Document Type", value="paystub")
            with d3:
                source_system = st.text_input("Source System", value="doc-mgmt")
            with d4:
                uploaded_at = st.text_input("Uploaded At (ISO datetime)", value="2026-02-02T13:00:00")

            submitted = st.form_submit_button("Submit Ingest")

        if submitted:
            payload = {
                "borrower": {
                    "borrowerId": borrower_id,
                    "name": borrower_name,
                    "ssnHash": ssn_hash or None,
                    "dob": dob or None,
                },
                "loan": {
                    "loanId": loan_id,
                    "amount": amount,
                    "status": status_value,
                    "purpose": purpose,
                    "originationDate": origination_date or None,
                    "ltv": ltv,
                    "dti": dti,
                },
                "property": {
                    "propertyId": property_id,
                    "address": address,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "type": property_type,
                },
                "income": {
                    "incomeId": income_id,
                    "type": income_type,
                    "employerName": employer_name,
                    "annualIncome": annual_income,
                    "startDate": start_date or None,
                },
                "documents": [
                    {
                        "documentId": document_id,
                        "type": document_type,
                        "sourceSystem": source_system,
                        "uploadedAt": uploaded_at or None,
                    }
                ],
            }

            status, message, data = _api_request("POST", f"{api_base_url}/loans/ingest", payload=payload)
            _show_response(status, message, data)

    with risk_tab:
        st.write("Fetch /loans/{loan_id}/risk")
        risk_loan_id = st.text_input("Loan ID for risk", value="L100", key="risk_loan_id")
        if st.button("Get Risk"):
            status, message, data = _api_request("GET", f"{api_base_url}/loans/{risk_loan_id}/risk")
            _show_response(status, message, data)

    with explain_tab:
        st.write("Fetch /loans/{loan_id}/explain")
        explain_loan_id = st.text_input("Loan ID for explain", value="L100", key="explain_loan_id")
        if st.button("Get Explain"):
            status, message, data = _api_request("GET", f"{api_base_url}/loans/{explain_loan_id}/explain")
            _show_response(status, message, data)

    with graph_tab:
        st.write("Run Cypher and visualize returned paths, nodes, and relationships.")
        neo_col_1, neo_col_2, neo_col_3 = st.columns(3)
        with neo_col_1:
            neo4j_uri = st.text_input("Neo4j URI", value=os.getenv("NEO4J_URI", "bolt://localhost:7687"))
            neo4j_user = st.text_input("Neo4j User", value=os.getenv("NEO4J_USER", "neo4j"))
        with neo_col_2:
            neo4j_password = st.text_input("Neo4j Password", value=os.getenv("NEO4J_PASSWORD", ""), type="password")
            neo4j_database = st.text_input("Database", value=os.getenv("NEO4J_DATABASE", "neo4j"))
        with neo_col_3:
            presets = {
                "Loan neighborhood": "MATCH p=(l:Loan {loanId: 'L101'})-[*1..2]-(n) RETURN p LIMIT 50",
                "All borrower-loan-property": "MATCH p=(b:Borrower)-[:APPLIES_FOR]->(l:Loan)-[:SECURED_BY]->(p:Property) RETURN p LIMIT 50",
                "Any connected sample": "MATCH p=()-[r]->() RETURN p LIMIT 50",
            }
            selected_preset = st.selectbox("Preset query", list(presets.keys()))

        use_custom = st.checkbox("Use custom query", value=False)
        query = presets[selected_preset]
        if use_custom:
            query = st.text_area("Custom Cypher", value=query, height=140)
        else:
            st.code(query, language="cypher")

        if st.button("Run Graph Query"):
            ok, message, rows = _run_neo4j_query(
                uri=neo4j_uri,
                user=neo4j_user,
                password=neo4j_password,
                database=neo4j_database,
                query=query,
            )
            if not ok:
                st.error(message)
            else:
                st.success(message)
                nodes, edges = _collect_graph_elements(rows)
                if nodes and edges:
                    _render_graphviz(nodes, edges)
                elif nodes:
                    st.info("Query returned nodes but no relationships to draw.")
                    _render_graphviz(nodes, [])
                else:
                    st.warning("No graph elements found. Return nodes/relationships/path values (e.g., RETURN p).")

                st.markdown("Raw records")
                st.json([_to_jsonable(row) for row in rows])


if __name__ == "__main__":
    main()
