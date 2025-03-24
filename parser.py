import re

def extract_tasks_from_text(text):
    sentences = text.split(".")
    tasks = []

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue

        task = ""
        start_date = ""
        duration = ""
        depends_on = ""

        # Get the task name (first few words before "will")
        task_match = re.match(r"([A-Z][a-zA-Z\s&]+?)\s+will", sent)
        if task_match:
            task = task_match.group(1).strip()

        # Detect date like "April 1"
        date_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}", sent)
        if date_match:
            start_date = date_match.group()

        # Detect duration like "3 days", "2 weeks"
        duration_match = re.search(r"(\d+)\s+(days?|weeks?)", sent)
        if duration_match:
            duration = duration_match.group()

        # Detect dependencies using keywords
        if "after" in sent.lower() or "once" in sent.lower():
            depends_on = "Previous task"

        tasks.append({
            "task": task if task else sent[:30],
            "start_date": start_date,
            "duration": duration,
            "depends_on": depends_on
        })

    return tasks
