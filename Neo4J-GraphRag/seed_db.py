#!/usr/bin/env python3
from neo4j import GraphDatabase
import os

def get_driver():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=(user, password))

def seed(driver):
    with driver.session() as s:
        s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE")
        s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE")
        s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Treatment) REQUIRE t.name IS UNIQUE")

        diseases = [
            {"name":"Influenza","symptoms":["Fever","Cough","Sore throat","Fatigue"],"treatments":["Rest","Fluids","Antiviral medication"]},
            {"name":"Common Cold","symptoms":["Runny nose","Cough","Sore throat","Sneezing"],"treatments":["Rest","Fluids","Decongestants"]},
            {"name":"Migraine","symptoms":["Headache","Nausea","Sensitivity to light"],"treatments":["Pain relievers","Triptans","Rest in dark room"]},
            {"name":"Strep Throat","symptoms":["Sore throat","Fever","Swollen lymph nodes"],"treatments":["Antibiotics","Rest"]},
            {"name":"COVID-19","symptoms":["Fever","Cough","Fatigue","Loss of taste or smell"],"treatments":["Rest","Fluids","Supportive care"]}
        ]

        for d in diseases:
            s.run("MERGE (d:Disease {name:$name})", name=d["name"])
            for sym in d["symptoms"]:
                s.run("MERGE (s:Symptom {name:$sym})", sym=sym)
                s.run(
                    "MATCH (d:Disease {name:$dname}), (s:Symptom {name:$sname}) MERGE (d)-[:HAS_SYMPTOM]->(s)",
                    dname=d["name"], sname=sym
                )
            for t in d["treatments"]:
                s.run("MERGE (t:Treatment {name:$t})", t=t)
                s.run(
                    "MATCH (d:Disease {name:$dname}), (t:Treatment {name:$tname}) MERGE (d)-[:TREATED_BY]->(t)",
                    dname=d["name"], tname=t
                )

    print("Seed complete.")

if __name__ == "__main__":
    drv = get_driver()
    try:
        seed(drv)
    finally:
        drv.close()
