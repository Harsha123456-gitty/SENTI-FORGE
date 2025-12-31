from fastapi import FastAPI
from collections import Counter

app = FastAPI(
    title="Sentiforge - Forging career decisions from real-world signals",
    description="Backend API for an agentic career decision system",
    version="0.1.0"
)


# -------------------------
# MEMORY (GLOBAL STATE)
# -------------------------
career_tracker = {
    "user": {
        "role": "Backend Engineer",
        "target_role": "Senior Backend Engineer",
        "managed_mode": True
    },
    "interviews": [],
    "system_state": "Normal"
}

# -------------------------
# CORE LOGIC (UNCHANGED)
# -------------------------
def infer_issue(interviews):
    rejected_stages = [
        i["stage"] for i in interviews if i["outcome"] == "Rejected"
    ]
    stage_count = Counter(rejected_stages)

    for stage, count in stage_count.items():
        if count >= 2:
            issue_map = {
                "System Design": "System Design Articulation",
                "Coding": "Problem Solving",
                "HR": "Communication"
            }
            return {
                "issue": issue_map.get(stage, "General Interview Issue"),
                "confidence": "High",
                "reason": f"{count} rejections at {stage} stage"
            }
    return None

def csda_decision(issue, user_confirmed=True):
    if issue and issue["confidence"] == "High" and user_confirmed:
        return {
            "decision": "Pause Applications",
            "duration_days": 21,
            "focus": issue["issue"],
            "mode": "Preparation Mode"
        }
    return {
        "decision": "No Action",
        "mode": "Normal"
    }

# -------------------------
# API ENDPOINTS
# -------------------------
@app.post("/interview", summary="Add interview outcome")
def add_interview(interview: dict):
    career_tracker["interviews"].append(interview)
    return {"status": "Interview added"}

@app.post("/run-csda",summary="Run Career Strategy Decision Agent")
def run_csda():
    issue = infer_issue(career_tracker["interviews"])
    decision = csda_decision(issue, user_confirmed=True)

    career_tracker["system_state"] = decision["mode"]

    return {
        "issue": issue,
        "decision": decision,
        "system_state": career_tracker["system_state"]
    }

@app.get("/state")
def get_state():
    return career_tracker
