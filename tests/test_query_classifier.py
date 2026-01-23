from yescity_recommendation_ai.services.query_classifier import query_classifier

queries = [
    "Find street food in Varanasi",
    "Best hotels to stay in Goa",
    "Things to do in Jaipur",
    "How is internet connectivity in Bangalore?",
    "Hidden gems in Delhi",
    "Good shopping markets in Mumbai",
    "Tell me about Agra"
]

for q in queries:
    print("\n==============================")
    print("Query:", q)
    result = query_classifier.classify_query(q)
    print(result.model_dump())