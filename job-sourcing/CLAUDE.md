# Job Sourcing Agent - Workflow Instructions

## Overview
This system helps Matthew find 1-5 quality job opportunities daily/weekly. It maintains memory to avoid duplicates, learns from feedback, and provides suitability analysis for each role.

## File Structure
```
job-sourcing/
├── CLAUDE.md          # This file - workflow instructions
├── profile.md         # Matthew's background, skills, value prop
├── config.json        # Search preferences, target companies, titles
└── memory/
    ├── blacklist.json      # Companies/roles to skip
    ├── seen_jobs.json      # Jobs already surfaced (dedupe)
    └── feedback_history.json # Ratings and learned preferences
```

## Daily Workflow

### Step 1: Load Context
Read these files at the start of each session:
- `profile.md` - understand Matthew's positioning
- `config.json` - search parameters
- `memory/blacklist.json` - companies/roles to skip
- `memory/seen_jobs.json` - avoid duplicates
- `memory/feedback_history.json` - check learned preferences

### Step 2: Source Jobs
Search for roles matching the criteria in `config.json`:

**Primary Search Queries:**
- "[title] remote" for each title in `target_titles`
- "[title] San Diego" for local options
- "[company name] careers" for target companies

**Search Sources (use WebSearch/WebFetch):**
- LinkedIn Jobs: `site:linkedin.com/jobs "[title]" remote`
- Wellfound: `site:wellfound.com "[title]"`
- Y Combinator: `site:workatastartup.com "[title]"`
- Greenhouse: `site:boards.greenhouse.io "[company]"`
- Lever: `site:jobs.lever.co "[company]"`
- Direct career pages for Tier 1 companies

### Step 3: Filter Results
For each job found, check:
1. **Not in blacklist** - company or role type
2. **Not already seen** - check `seen_jobs.json` by company+title
3. **Location match** - Remote or San Diego (strict requirement)
4. **Salary range** - $120K-$180K if posted
5. **Role type alignment** - matches target titles/not pure engineering

### Step 4: Validate & Analyze Each Job
For jobs that pass filters:

**A. Verify Link is Live**
- Fetch the job posting URL
- Confirm it returns 200 and the role is still posted
- Note if "no longer accepting applications"

**B. Suitability Analysis**
Score and explain fit across these dimensions:

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Role Alignment | 25% | Matches target role types, not pure engineering |
| Skills Match | 25% | AI evaluation, customer success, enablement, training |
| Location | 20% | Remote or San Diego (hard requirement) |
| Company Fit | 15% | Ethical AI, culture, stability |
| Growth Potential | 15% | Career trajectory, learning opportunities |

**C. Generate Analysis Output**
For each job, provide:
```
## [Company] - [Title]
**Link:** [URL]
**Location:** [Remote/San Diego/Hybrid]
**Salary:** [if posted]

### Suitability Score: X/100

### Match Analysis
- **Strong Fits:** [what aligns well with profile]
- **Potential Gaps:** [areas where experience is lighter]
- **Talking Points:** [specific achievements to highlight]

### Red Flags
- [any concerns from job posting or company research]

### Application Strategy
- [specific angle to take]
- [which portfolio pieces to emphasize]
```

### Step 5: Present Results
Show 1-5 best matches, ranked by suitability score.

Format:
```
# Job Sourcing Results - [Date]

## Summary
- Jobs searched: X
- Passed filters: Y
- Recommended: Z

## Top Recommendations
[job analyses as above]

## Also Considered (Lower Fit)
[brief list with reasons for lower ranking]

## Feedback Requested
Please rate each job:
- 👍 Interested - will apply
- 👎 Not interested - [reason]
- 🤔 Maybe - need more info

Any other feedback on search direction?
```

### Step 6: Record & Learn
After Matthew provides feedback:

**Update `seen_jobs.json`:**
```json
{
  "company": "Example Corp",
  "title": "Solutions Architect",
  "url": "https://...",
  "location": "Remote",
  "date_seen": "2026-01-27",
  "suitability_score": 85,
  "status": "surfaced",
  "feedback": "interested",
  "notes": "Applied 2026-01-28"
}
```

**Update `feedback_history.json`:**
- Log session date, jobs shown, feedback received
- Extract patterns (e.g., "prefers smaller companies", "not interested in enterprise sales")
- Update `learned_preferences` weights

## Google Sheet Integration

### Option A: Export Link (Preferred)
Matthew can share a CSV export link of his tracking sheet. Read it to check:
- Companies already applied to
- Rejection patterns to learn from
- Timeline of applications

### Option B: Manual Sync
Matthew periodically updates `memory/applied_tracker.json` with:
```json
{
  "applications": [
    {
      "company": "Example",
      "title": "Role",
      "date_applied": "2026-01-15",
      "status": "rejected",
      "stage": "final round",
      "notes": "..."
    }
  ]
}
```

## Special Instructions

### For Companies in Tier 1 Dream:
- Check their careers page even if no matching search results
- Note any roles that might be added soon
- Flag if Matthew's profile is particularly strong for a posting

### For Rejected Companies:
- Mistral, Glean: May reapply for different roles after 6+ months
- Cadre, Snorkel LXD: Skip entirely unless they reach out
- Scale AI: Never surface (ethical concerns)

### Emphasis Points for Applications:
1. **Lead with metrics:** 40% variance reduction, 83% time savings, 65% support reduction
2. **Position as "consultant who can prototype"** - not competing with CS grads
3. **Highlight production deployments** - real agents, real business impact
4. **Teaching experience as enablement proof** - 1000+ students trained

## Trigger Phrases
Matthew can start a session with:
- "Find me jobs" / "Source jobs" - run full workflow
- "Job update" - quick check for new postings at target companies
- "Log feedback" - record ratings on previously shown jobs
- "Update preferences" - modify search criteria or blacklist
