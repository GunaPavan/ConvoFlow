from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

class SentimentAnalyzer:
    def __init__(self):
        model_name = "cardiffnlp/twitter-roberta-base-sentiment"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.pipeline = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)
        self.label_map = {"LABEL_0":"NEGATIVE", "LABEL_1":"NEUTRAL", "LABEL_2":"POSITIVE"}

    def analyze(self, text: str):
        result = self.pipeline(text)[0]
        label = self.label_map[result['label']]
        score = result['score']
        return label, score
