import os
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import load_dataset
from sklearn.metrics import accuracy_score
from tqdm import tqdm

# ✅ GPU 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ✅ 모델 및 토크나이저 로딩
MODEL_NAME = "monologg/kobert"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=7, trust_remote_code=True).to(device)

# ✅ KLUE 감정 데이터셋 로딩 (수정된 부분)
data = load_dataset("klue_stf", "emotion")
train_data = data["train"]
test_data = data["validation"]

# ✅ 감정 라벨 (0~6)
label_names = ['분노', '슬픔', '기쁨', '불안', '중립', '혐오', '놀람']

# ✅ 토치 Dataset 정의
class EmotionDataset(Dataset):
    def __init__(self, dataset):
        self.sentences = dataset["sentence"]
        self.labels = dataset["label"]

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        encoding = tokenizer(
            self.sentences[idx],
            padding="max_length",
            truncation=True,
            max_length=64,
            return_tensors="pt"
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": torch.tensor(self.labels[idx])
        }

# ✅ 데이터 준비
BATCH_SIZE = 32
train_dataset = EmotionDataset(train_data)
test_dataset = EmotionDataset(test_data)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

# ✅ Optimizer & Loss
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
loss_fn = torch.nn.CrossEntropyLoss()

# ✅ 학습 루프
EPOCHS = 3
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    for batch in tqdm(train_loader):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        total_loss += loss.item()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f"[Epoch {epoch+1}] Loss: {total_loss:.4f}")

# ✅ 검증
model.eval()
y_true, y_pred = [], []
with torch.no_grad():
    for batch in test_loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"]

        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()

        y_pred.extend(preds)
        y_true.extend(labels.numpy())

acc = accuracy_score(y_true, y_pred)
print(f"✅ 검증 정확도: {acc:.4f}")

# ✅ 모델 저장
save_dir = "./emotion_model/model"
os.makedirs(save_dir, exist_ok=True)
model.save_pretrained(save_dir)
tokenizer.save_pretrained(save_dir)
print(f"🎉 모델 저장 완료 → {save_dir}")
