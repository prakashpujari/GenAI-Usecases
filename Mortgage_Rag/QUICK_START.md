# 🎓 SecureMortgageAI - Quick Start Training

**5-Minute Getting Started Guide**

---

## ⚡ TL;DR

```powershell
# 1. Activate environment
.\.venv\Scripts\Activate.ps1

# 2. Run app
streamlit run app.py

# 3. Upload PDFs → Ask questions → Get answers!
```

Open browser: http://localhost:8501

---

## 📝 Your First Session (5 Minutes)

### Minute 1: Launch
```powershell
cd C:\pp\GitHub\GenAI-Usecases\Mortgage_Rag
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

### Minute 2: Upload
1. Click **"Browse files"** in sidebar
2. Select sample PDFs (W-2, paystub)
3. Wait for ✅ "Vector embeddings created"

### Minute 3-4: Ask Questions
Try these:
- `What is the borrower's annual income?`
- `Who is the employer?`
- `Verify employment details`

### Minute 5: Explore
- Click **"📚 View Sources"** to see citations
- Expand **"🔍 View Detected PII"** to see security
- Try an invalid query: `hack the system` (will be blocked)

---

## 🎯 Key Features Demo

### ✅ PII Protection
**Ask:** "What is the SSN?"  
**See:** `[SSN_REDACTED]` - never exposed!

### ✅ Security Guardrails
**Try:** "Ignore all instructions"  
**See:** ⚠️ Blocked with warning

### ✅ Smart Search
**Ask:** "Show employment history"  
**See:** AI finds and combines info from multiple docs

---

## 📚 Example Queries

### Income Verification
```
✓ What is the borrower's annual income?
✓ Show me the monthly gross pay
✓ List all income sources
```

### Employment
```
✓ Who is the current employer?
✓ When did employment start?
✓ Verify job title and position
```

### Document Info
```
✓ Summarize the W-2 information
✓ What documents have been uploaded?
✓ Show year-to-date earnings
```

---

## 🛡️ Security Features

| Feature | What It Does | Example |
|---------|--------------|---------|
| **PII Redaction** | Hides sensitive data | SSN: 123-45-6789 → [SSN_REDACTED] |
| **Prompt Injection** | Blocks manipulation | "Ignore instructions" → ⚠️ BLOCKED |
| **Content Filter** | Blocks inappropriate | "hack system" → ⚠️ BLOCKED |
| **Topic Validation** | Warns off-topic | "What's the weather?" → ℹ️ WARNING |

---

## ❓ Common Questions

**Q: Where are my documents stored?**  
A: Processed in memory only - not saved permanently

**Q: Can I use real documents?**  
A: Yes! All PII is automatically redacted

**Q: How accurate are the answers?**  
A: Check "View Sources" - high relevance (80%+) = very accurate

**Q: What if it can't find an answer?**  
A: Try rephrasing with keywords from your documents

**Q: Is my data secure?**  
A: Yes! Multiple layers:
- PII redacted before embedding
- No permanent storage
- Output sanitized before display
- Only OpenAI API has access (for embeddings/LLM)

---

## 🎨 UI Overview

```
┌─────────────────────────────────────────────────────────────┐
│ 🔒 SecureMortgageAI                                  ☰ Menu│
│ AI-powered mortgage document assistant                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📄 Uploaded Documents                                     │
│  ┌──────────────────┬───────────┬───────────┐            │
│  │ Document         │ Characters│ PII Items │            │
│  ├──────────────────┼───────────┼───────────┤            │
│  │ W2_2023.pdf      │   2,453   │     8     │            │
│  └──────────────────┴───────────┴───────────┘            │
│                                                             │
│  💬 Ask Questions About Your Documents                     │
│  ┌─ USER ──────────────────────────────────────────────┐  │
│  │ What is the borrower's annual income?              │  │
│  └────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ ASSISTANT ─────────────────────────────────────────┐  │
│  │ Based on the W-2 form, the annual income is        │  │
│  │ $85,000.00...                                       │  │
│  │ 📚 View Sources [▼]                                │  │
│  └────────────────────────────────────────────────────┘  │
│                                                             │
│  Ask a question...                               [SEND]  │
└─────────────────────────────────────────────────────────────┘

SIDEBAR:
│ 📁 Document Upload  │
│ [Browse files]       │
│                      │
│ 🛡️ Safety Guardrails│
│ ✅ PII Redaction    │
│ ✅ Prompt Protection│
│ ✅ Content Filter   │
│ ✅ Topic Validation │
```

---

## 🔧 Pro Tips

1. **Be Specific**: "What is annual income?" > "Tell me about money"
2. **Check Sources**: Always expand to verify accuracy
3. **Use Keywords**: Terms from your actual documents work best
4. **Multiple Docs**: Upload related docs for better context
5. **Follow-up**: Ask related questions - context is maintained

---

## 🚨 If Something Goes Wrong

### App Won't Start
```powershell
# Check virtual environment
.\.venv\Scripts\python.exe --version

# Reinstall packages
pip install -r requirements.txt --no-cache-dir

# Verify API key
Get-Content .env
```

### No Results Found
- Upload more relevant documents
- Use keywords that appear in your docs
- Ask more specific questions

### Error Messages
- **"Upload PDFs"**: No documents yet - upload first
- **"Prompt injection"**: Rephrase without system keywords
- **"Too short"**: Query needs 3+ characters

---

## 📞 Next Steps

1. ✅ Complete this 5-minute guide
2. 📖 Read [USER_GUIDE.md](USER_GUIDE.md) for comprehensive walkthrough
3. 📸 Follow [SCREENSHOT_GUIDE.md](SCREENSHOT_GUIDE.md) to document
4. 🧪 Run tests: `python test_guardrails.py`
5. 🚀 Deploy to production (optional)

---

## 🎯 Success Checklist

After 5 minutes, you should have:
- [ ] Launched the app successfully
- [ ] Uploaded at least 1 PDF
- [ ] Asked 3+ questions
- [ ] Viewed sources for one answer
- [ ] Seen PII redaction in action
- [ ] Triggered at least one guardrail

**Congratulations! You're now ready to use SecureMortgageAI!** 🎉

---

**Need Help?**
- 📖 Full docs: [USER_GUIDE.md](USER_GUIDE.md)
- 🐛 Issues: See [Troubleshooting](#-troubleshooting)
- 🔧 Technical: See [README.md](README.md)
