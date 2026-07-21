import os
import json
import litellm
import pathlib

PROFILE_PATH = pathlib.Path("/run/media/system/tallgeese/dev/ai_knowledge_library/USER_PROFILE.md")
OUTPUT_DIR = pathlib.Path("/run/media/system/tallgeese/dev/ai_knowledge_library/output/applications/")

def load_user_profile():
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return f.read()

def fetch_job_postings():
    """Mock data access layer to fetch job postings."""
    return [
        {
            "id": "job_1",
            "title": "DevOps Engineer",
            "company": "Tech Corp",
            "description": "We are looking for a DevOps Engineer with Python, Go, CI/CD, and Azure experience. You will manage deployments, automate processes, and monitor infrastructure."
        },
        {
            "id": "job_2",
            "title": "Site Reliability Engineer",
            "company": "Cloud Systems Inc",
            "description": "Seeking an SRE to build scalable systems using Go and Python. Experience with Kubernetes, Docker, and logging tools is required. You will ensure high availability of our services."
        }
    ]

def generate_application_materials(profile, job, model="gemini/gemini-1.5-flash"):
    """Uses litellm to generate a tailored resume and cover letter based on the profile and job description."""
    system_prompt = (
        "You are an expert career assistant. Your task is to generate a tailored resume and cover letter "
        "for the user based on their profile and the provided job description.\n"
        "Strict Guidelines:\n"
        "1. Profile Grounding: Only use facts from the user's profile. Do not fabricate experience.\n"
        "2. Professional Identity: Highlight engineering strengths (DevOps, SRE, etc.).\n"
        "3. Verification: Do not invent skills, job titles, tenures, or project details.\n"
        "4. Output format: Return a JSON object with 'resume_md' and 'cover_letter_md' keys."
    )
    
    user_prompt = f"User Profile:\n{profile}\n\nJob Posting:\nTitle: {job['title']}\nCompany: {job['company']}\nDescription: {job['description']}"

    response = litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        return data.get("resume_md", ""), data.get("cover_letter_md", "")
    except json.JSONDecodeError:
        # Fallback if the model didn't return valid JSON
        return content, "Error generating cover letter."

def save_materials(job_id, resume_md, cover_letter_md):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    resume_path = OUTPUT_DIR / f"{job_id}_resume.md"
    cover_letter_path = OUTPUT_DIR / f"{job_id}_cover_letter.md"
    
    with open(resume_path, "w", encoding="utf-8") as f:
        f.write(resume_md)
        
    with open(cover_letter_path, "w", encoding="utf-8") as f:
        f.write(cover_letter_md)
        
    print(f"Saved materials for {job_id}")

def main():
    profile = load_user_profile()
    jobs = fetch_job_postings()
    
    for job in jobs:
        print(f"Processing job {job['id']}...")
        resume, cover_letter = generate_application_materials(profile, job)
        save_materials(job['id'], resume, cover_letter)

if __name__ == "__main__":
    main()
