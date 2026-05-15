import pandas as pd
import random
from datasets import Dataset
from transformers import AutoModelForSequenceClassification, Trainer, TrainingArguments, AutoTokenizer

# 1. Regenerate Dataset
def generate_dataset():
    scams = [
        "Dear customer, your ICICI account will be suspended. Please verify your KYC immediately at http://icici-verify-update.net",
        "Urgent: Your electricity bill is pending. Power will be cut at 8 PM. Pay now at 9876543210.",
        "Congratulations! You have been selected for a WFH job at Amazon. Click: http://amzn-jobs.agency",
        "Your parcel from Delhivery is on hold. Pay Rs. 25 fee here: http://delhivery-pkg.com",
        "Alert: Rs 95,000 debited from your A/C. If not you, block at http://secure-bank-alert.com"
    ] * 200 
    legitimate = [
        "OTP for your transaction at Zomato is 445566. Do not share this. - HDFC Bank",
        "Your Airtel bill of Rs. 943 is due on 25-Oct. Pay now on Airtel Thanks app.",
        "Your order has been shipped via BlueDart. Tracking ID: 123456789. - Amazon",
        "Dear Customer, your salary has been credited to your SBI A/C X1234 on 01-Nov.",
        "Your appointment with Dr. Sharma is confirmed for 4:30 PM today at Apollo Hospital."
    ] * 200
    all_texts = scams + legitimate
    all_labels = [1] * len(scams) + [0] * len(legitimate)
    combined = list(zip(all_texts, all_labels))
    random.shuffle(combined)
    texts, labels = zip(*combined)
    return pd.DataFrame({"text": list(texts), "label": list(labels)})

df = generate_dataset()
hf_dataset = Dataset.from_pandas(df)

# 2. Tokenization
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def preprocess_function(examples):
    return tokenizer(examples['text'], truncation=True, padding='max_length', max_length=128)

tokenized_dataset = hf_dataset.map(preprocess_function, batched=True)
tokenized_dataset = tokenized_dataset.rename_column("label", "labels")
tokenized_dataset = tokenized_dataset.remove_columns(["text"])
tokenized_dataset.set_format("torch")

# 3. Training Config
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=1, # Reduced for quick restoration
    per_device_train_batch_size=16,
    save_strategy="no"
)

# 4. Initialize Model and Trainer
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
trainer = Trainer(model=model, args=training_args, train_dataset=tokenized_dataset)

# 5. Train and Save
print("Starting training restoration...")
trainer.train()
trainer.save_model("./fraud_detection_model")
tokenizer.save_pretrained("./fraud_detection_model")
print("Model successfully restored to ./fraud_detection_model")
