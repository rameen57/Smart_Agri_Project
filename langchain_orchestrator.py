from ner_engine import extract_entities
from rag_engine import simple_rag_answer
from multi_agent_system import run_multi_agent_system

def langchain_pipeline(user_query):
    entities = extract_entities(user_query)

    if entities.get("blocked"):
        return {
            "status": "blocked",
            "message": "I am an AI specialized exclusively in agriculture. I cannot answer questions outside of farming, crops, soil, or livestock. Please ask an agriculture-related question."
        }

    rag_answer = simple_rag_answer(user_query)
    mas_report = run_multi_agent_system()

    return {
        "status": "success",
        "user_query": user_query,
        "ner_entities": entities,
        "rag_answer": rag_answer,
        "mas_decision": mas_report
    }

if __name__ == "__main__":
    query = input("Enter farmer query: ")
    result = langchain_pipeline(query)

    print("\nLangChain-Orchestrated Output:")
    print(result)