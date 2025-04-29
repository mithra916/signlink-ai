from transformers import pipeline

# Load Hugging Face model once
asl_pipe = pipeline("text2text-generation", model="google/flan-t5-small")

# Backup word filter if AI fails
removable_words = {
    'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being',
    'a', 'an', 'the', 'to', 'of', 'in', 'on', 'at', 'by',
    'as', 'for', 'about', 'into', 'from', 'that',
    'this', 'those', 'these', 'just', 'do', 'does', 'did',
    'have', 'has', 'had', 'having', 'so', 'because',
    'will', 'would', 'can', 'could', 'should', 'shall', 'may',
    'might', 'must', 'and', 'or', 'but', 'if', 'than', 'then'
}

def convert_to_asl_grammar(text):
    try:
        prompt = f"Convert to ASL grammar: {text}"
        result = asl_pipe(prompt, max_length=50, do_sample=False)
        asl_text = result[0]['generated_text'].strip()
        print("✅ Hugging Face model used:", asl_text)
        return asl_text
    except Exception as e:
        print("⚠️ Hugging Face failed, using fallback. Error:", e)
        # Simple fallback
        cleaned = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text)
        words = cleaned.lower().split()
        filtered_words = [word for word in words if word not in removable_words]
        return ' '.join(filtered_words)
