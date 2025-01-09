from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def highlight_keywords(response, top_n=5):
    # Tokenize response
    corpus = [response]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = np.array(vectorizer.get_feature_names_out())
    scores = tfidf_matrix.toarray()[0]

    # Get top N keywords
    top_indices = np.argsort(scores)[-top_n:]
    keywords = feature_names[top_indices]

    # Highlight keywords in response
    highlighted_response = response
    for keyword in keywords:
        print(keyword)
        highlighted_response = highlighted_response.replace(
            keyword, f"**{keyword}**"  # Markdown-style bold
        )
    return highlighted_response

response = "Austrian economics emphasizes the importance of time-preference, entrepreneurship, and market processes."
highlighted_text = highlight_keywords(response)
print(highlighted_text)