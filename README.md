# 🧠 Autonomous Research Agent

An uncensored AI research system that builds knowledge over time. One topic, continuous learning, never repeats research.

## 🎯 How It Works

```
RUNPOD BOOTS → AUTO-STARTS WEB UI → CHECKS DATABASE → CONTINUES OR REFINES → RESEARCHES → EMAILS
      ↓              ↓                    ↓                  ↓                ↓           ↓
  You turn on    Opens at         "Banking research     "Focus on       No duplicates  Results
  manually      pod-ip:7777        found. Continue?"    Jekyll Island?"  just updates   sent
```

## 🚀 Quick Start

### 1. Turn on RunPod GPU
```bash
# Boot your RunPod instance
# Note the IP address (e.g., 123.45.67.89)
```

### 2. Access Web Interface
```
Open browser: http://[your-pod-ip]:7777
```

### 3. System Auto-Detects Previous Research
- **First time**: Asks for your research topic
- **Returning**: Shows previous research, asks to continue or refine

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      BOOT SEQUENCE                                │
├──────────────────────────────────────────────────────────────────┤
│  1. RunPod starts                                               │
│  2. Ollama loads Mixtral-8x7B-v0.1 model                       │
│  3. Operator runs `./startup.sh`                                │
│  4. You browse to http://[pod-ip]:7777                          │
└──────────────────────────────────────────────────────────────────┘
                                ↓
┌──────────────────────────────────────────────────────────────────┐
│                    DATABASE CHECK                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  IF database exists:                                              │
│  ┌─────────────────────────────────────────┐                    │
│  │  Welcome back!                           │                    │
│  │                                          │                    │
│  │  📚 Previous Research Found:             │                    │
│  │  Topic: Banking System History           │                    │
│  │  Sessions: 3                             │                    │
│  │  Data collected: 1,247 nodes             │                    │
│  │  Knowledge claims: 89                    │                    │
│  │  Last researched: 2 days ago             │                    │
│  │                                          │                    │
│  │  [CONTINUE RESEARCHING]                  │                    │
│  │  [REFINE FOCUS]                          │                    │
│  │  [VIEW PREVIOUS FINDINGS]                │                    │
│  └─────────────────────────────────────────┘                    │
│                                                                    │
│  IF database empty:                                               │
│  ┌─────────────────────────────────────────┐                    │
│  │  Welcome! Let's start researching.       │                    │
│  │                                          │                    │
│  │  What topic should I investigate?        │                    │
│  │  [____________________________]          │                    │
│  │                                          │                    │
│  │  [BEGIN RESEARCH]                        │                    │
│  └─────────────────────────────────────────┘                    │
└──────────────────────────────────────────────────────────────────┘
                                ↓
┌──────────────────────────────────────────────────────────────────┐
│              INTELLIGENT RESEARCH PHASE                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  BEFORE ADDING ANY DATA:                                          │
│  • Check if exists in database                                    │
│  • If similar, group together                                     │
│  • If identical, skip                                            │
│  • If contradicts, flag it                                       │
│                                                                    │
│  ┌─────────────────────────────────────────┐                    │
│  │  🔄 Researching...                       │                    │
│  │                                          │                    │
│  │  ████████████░░░░░░  62%                │                    │
│  │                                          │                    │
│  │  ⏱️ Time Remaining: 1h 08m               │                    │
│  │                                          │                    │
│  │  📊 New findings: 43                     │                    │
│  │  🔄 Updated claims: 12                   │                    │
│  │  ⚠️ Contradictions found: 3              │                    │
│  │  ✅ Duplicates avoided: 28               │                    │
│  └─────────────────────────────────────────┘                    │
└──────────────────────────────────────────────────────────────────┘
```

## 🔍 Information Sources

- Searches Internet Archive for related books and documents
- Gathers advice from forums like Reddit
- Extracts transcripts from YouTube videos

## 📁 File Structure

```
research/
├── research_agent.py       # Main autonomous agent
├── web_interface.py        # Flask web UI
├── jobs/                   # Job manager
├── tools/                  # Utilities (Wayback archiver)
├── config.json             # Settings (model & database)
├── setup.sh                # Dependency installer
├── /root/research.db       # Persistent SQLite database
└── logs/                   # Activity logs
```

## 💾 Smart Database System

### Never Repeats Research
```python
# When finding new information:
new_finding = "Federal Reserve created secretly"

if already_in_database(new_finding):
    skip()  # Don't waste time
elif similar_exists(new_finding):
    group_together()  # Cluster related info
elif contradicts_existing(new_finding):
    flag_contradiction()  # Note conflicts
else:
    add_to_knowledge()  # Genuinely new
```

### Knowledge Building Over Time

| Session | What Happens | Database Result |
|---------|-------------|-----------------|
| Day 1 | Research "Banking System" | 500 findings added |
| Day 2 | Continue + focus "Jekyll Island" | 100 new findings, 50 updated |
| Day 3 | Refine "Gold Standard" | 75 new findings, 0 duplicates |
| Day 4 | Deep dive "Nixon 1971" | 200 new findings, 3 contradictions flagged |

## 🖥️ Web Interface Features

### First Visit
```
Welcome! What should I research?
> Banking system and Federal Reserve

How many hours? (1-5)
> 3

Email for results?
> user@email.com

[START RESEARCH]
```

### Return Visit
```
Welcome back! Your research:
📚 Topic: Banking System
📊 Total findings: 1,247
🕐 Total time researched: 9 hours
📅 Last session: 2 days ago

What would you like to do?
[CONTINUE WHERE LEFT OFF]
[FOCUS ON SPECIFIC AREA]
[VIEW FINDINGS]
[EXPORT ALL DATA]
```

### Focus Refinement
```
What aspect should I focus on?

Previously researched:
✅ Federal Reserve creation
✅ Jekyll Island meeting
⚠️ Partially: Gold standard
❌ Not yet: Digital currencies

> "Investigate Bretton Woods connection"

[START FOCUSED RESEARCH]
```

## ⚙️ Configuration

### config.json
```json
{
  "port": 7777,
  "max_hours": 5,
  "topic": "Banking System",  // Persists between sessions
  
  "ollama": {
    "model": "Mixtral-8x7B-v0.1",
    "url": "http://localhost:11434"
  },
  
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "research@yourdomain.com"
  },
  
  "research": {
    "depth_level": 8,  // 1-10 scale
    "dedup_threshold": 0.85,  // Similarity threshold
    "cluster_related": true,
    "track_contradictions": true
  },
  
  "auto_shutdown": {
    "enabled": true,
    "after_hours": 3
  }
}
```

#### Scheduler and UI options

```json
"scheduler": { "enabled": false },
"ui": {
  "autostart_on_open": true,
  "autostart_once_per_process": true,
  "default_topic": "Global banking conspiracies",
  "default_hours": 2,
  "default_focus": "cartelization, regulatory capture, market manipulation"
}
```

## 📊 Database Schema

```sql
-- Main findings table with deduplication
CREATE TABLE nodes (
    id TEXT PRIMARY KEY,
    content TEXT,
    content_hash TEXT UNIQUE,  -- Prevents exact duplicates
    cluster_id TEXT,           -- Groups similar content
    source TEXT,
    confidence REAL,
    timestamp TEXT,
    session_id INTEGER
);

-- Knowledge claims that build over time
CREATE TABLE claims (
    id INTEGER PRIMARY KEY,
    claim TEXT UNIQUE,
    evidence_count INTEGER,
    supporting_nodes TEXT,  -- JSON array of node IDs
    contradicting_nodes TEXT,
    confidence REAL,
    first_seen TEXT,
    last_updated TEXT
);

-- Track research progress
CREATE TABLE progress (
    topic TEXT,
    subtopics_explored TEXT,  -- JSON array
    subtopics_pending TEXT,    -- JSON array
    total_sessions INTEGER,
    total_hours REAL,
    last_session TEXT
);

-- Contradictions to investigate
CREATE TABLE contradictions (
    id INTEGER PRIMARY KEY,
    claim_1 TEXT,
    claim_2 TEXT,
    evidence_1 TEXT,
    evidence_2 TEXT,
    resolution TEXT,
    needs_review BOOLEAN
);
```

## 📧 Email Report Format

```
Subject: Research Update - Banking System (Session 4)

Summary:
- New findings: 127
- Updated claims: 23
- Contradictions found: 3
- Total knowledge base: 1,847 entries

Key Discoveries This Session:
1. Nixon's 1971 decision linked to...
2. Previously unknown meeting in...
3. Contradiction: Official records say X but archives show Y

Attachments:
- full_report.pdf (Detailed findings)
- research_data.zip (Database export)
- contradictions.txt (Conflicts to review)
```

## 🔄 Continuous Learning Example

```
Session 1: "Research banking system"
├── Finds: Federal Reserve Act 1913
├── Finds: Jekyll Island meeting
└── Saves: 500 data points

Session 2: "Continue research"
├── Skips: Federal Reserve Act (already known)
├── Deepens: Jekyll Island attendees
├── Adds: New findings about participants
└── Saves: 150 NEW data points

Session 3: "Focus on gold standard"
├── Checks: Existing gold standard data
├── Finds: Gap in 1971 knowledge
├── Researches: Only Nixon Shock details
└── Saves: 200 NEW data points (0 duplicates)
```

## 🚦 Status Indicators

| Icon | Meaning |
|------|---------|
| 🔄 | Currently researching |
| ✅ | Information verified |
| ⚠️ | Contradiction found |
| 📊 | New finding added |
| 🔗 | Related to existing data |
| ⏩ | Skipped (duplicate) |
| 💾 | Saved to database |

## 🛠️ Installation

### Migrating from scheduled versions

If you used an older release that ran on a cron schedule, remove the cron job before continuing:

```bash
crontab -l | grep -v "research_agent.py" | crontab -
```

### On RunPod GPU

1. **Clone Repository**
```bash
cd /root
git clone https://github.com/s7612f/research.git && cd research
```

2. **Run Setup**
```bash
chmod +x setup.sh
./setup.sh
```

3. **Start Web UI**
```bash
./startup.sh
```
The script prints a direct URL like `http://[pod-ip]:7777`—open that link in your browser. If `ui.autostart_on_open` is enabled, the first visit triggers a run using defaults; otherwise fill the form and press **Run**.

## 📝 Commands

### Manual Operations
```bash
# Start research manually
python3 research_agent.py

# View database stats
python3 -c "from database_manager import show_stats; show_stats()"

# Export all findings
python3 export_data.py --format pdf --email user@email.com

# Check for duplicates
python3 database_manager.py --deduplicate

# View contradictions
sqlite3 /root/research.db "SELECT * FROM contradictions;"
```

## 🔒 Privacy & Security

- **Local Processing**: Everything runs on your GPU
- **No External APIs**: Only uses local Ollama
- **Private Database**: Your research never leaves the pod
- **Encrypted Export**: Email attachments can be encrypted

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Deduplication Speed | <0.1s per check |
| Database Size | ~100MB per 10,000 findings |
| Research Speed | ~500 sources/hour |
| Memory Usage | <4GB RAM |
| GPU Usage | Minimal (Mixtral-8x7B-v0.1 on CPU) |

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 7777 blocked | Change in config.json |
| Database locked | `fuser -k /root/research.db` |
| Ollama not starting | `ollama serve` manually |
| Web UI not loading | Check `logs/web.log` |
| Duplicates appearing | Run `--deduplicate` |

## 📈 Research Progress Tracking

The system tracks:
- What's been researched
- What's partially researched
- What's not yet explored
- Where contradictions exist
- Which claims need more evidence

This ensures efficient, non-repetitive research that builds knowledge systematically.

## 🤝 Contributing

Areas for improvement:
- Better contradiction resolution
- Smarter clustering algorithms
- Additional email providers
- Export formats (JSON, CSV, etc.)

## 📜 License

MIT - Use freely for any research purpose

---

**Remember**: This system builds knowledge over time. Each session makes it smarter, never wasting time on duplicate research.
