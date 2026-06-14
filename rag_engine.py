def load_knowledge():
    with open("agri_knowledge.txt", "r", encoding="utf-8") as file:
        text = file.read()

    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    return chunks

def simple_rag_answer(question):
    question_lower = question.lower()
    chunks = load_knowledge()

    best_chunk = None
    best_score = 0

    for chunk in chunks:
        score = 0
        for word in question_lower.split():
            if word in chunk.lower():
                score += 1

        if score > best_score:
            best_score = score
            best_chunk = chunk

    if best_score == 0:
        return "I do not have enough agriculture knowledge to answer this from my knowledge base."

    return best_chunk

if __name__ == "__main__":
    question = input("Ask Agribot: ")
    answer = simple_rag_answer(question)

    print("\nRAG Answer:")
    print(answer)