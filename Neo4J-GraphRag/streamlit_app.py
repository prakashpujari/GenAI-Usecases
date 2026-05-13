import os
from neo4j import GraphDatabase
import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def get_driver():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=(user, password))

def fetch_all_symptoms(session):
    res = session.run("MATCH (s:Symptom) RETURN s.name AS name ORDER BY name")
    return [r["name"] for r in res]

def find_diseases_by_symptoms(session, symptoms):
    if not symptoms:
        q = "MATCH (d:Disease) RETURN d.name AS disease LIMIT 50"
        res = session.run(q)
        return [] if res is None else [r["disease"] for r in res]

    query = '''
    MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
    WHERE s.name IN $symptoms
    WITH d, collect(DISTINCT s.name) AS matched, count(DISTINCT s.name) AS matchedCount
    OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(sym2:Symptom)
    WITH d, matched, matchedCount, count(DISTINCT sym2) AS totalSymptoms
    RETURN d.name AS disease, matched, matchedCount, totalSymptoms
    ORDER BY matchedCount DESC, disease
    '''
    res = session.run(query, symptoms=symptoms)
    return [ {"disease": r["disease"], "matched": r["matched"], "matchedCount": r["matchedCount"], "totalSymptoms": r["totalSymptoms"]} for r in res ]

def get_subgraph(session, disease_names):
    query = '''
    UNWIND $names AS name
    MATCH (d:Disease {name:name})-[r]-(n)
    RETURN d.name AS dname, type(r) AS rel, labels(n) AS nlabels, n.name AS nname
    '''
    res = session.run(query, names=disease_names)
    edges = []
    nodes = set()
    for r in res:
        d = r["dname"]
        n = r["nname"]
        rel = r["rel"]
        nodes.add(d)
        if n:
            nodes.add(n)
            edges.append((d, n, rel))
    return nodes, edges

def draw_graph(nodes, edges):
    G = nx.Graph()
    for n in nodes:
        G.add_node(n)
    for a,b,rel in edges:
        G.add_edge(a,b, label=rel)

    plt.figure(figsize=(8,6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color="#9ecae1", node_size=1200, font_size=9)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    st.pyplot(plt)

def main():
    st.title("Healthcare Diagnosis — By Prakash Pujari")
    driver = get_driver()
    with driver.session() as session:
        all_symptoms = fetch_all_symptoms(session)

        st.sidebar.header("Query")
        symptoms = st.sidebar.multiselect("Select symptoms", options=all_symptoms)
        free_text = st.sidebar.text_input("Or type symptoms (comma separated)")
        if free_text:
            free_list = [s.strip() for s in free_text.split(",") if s.strip()]
            # merge
            for s in free_list:
                if s not in symptoms:
                    symptoms.append(s)

        if st.sidebar.button("Find possible diagnoses"):
            results = find_diseases_by_symptoms(session, symptoms)
            if not results:
                st.info("No diseases found for those symptoms.")
            else:
                df = pd.DataFrame(results)
                st.subheader("Matches")
                st.dataframe(df)

                top = df.iloc[0]["disease"]
                st.subheader(f"Relations around top match: {top}")
                nodes, edges = get_subgraph(session, [top])
                if nodes:
                    draw_graph(nodes, edges)
                else:
                    st.write("No related nodes to display.")

        else:
            st.write("Select symptoms and click 'Find possible diagnoses' in the sidebar.")

if __name__ == '__main__':
    main()
