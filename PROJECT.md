# Sales Playbook Portal

Interactive HTML sales call tool for Trilogy Care's onboarding team.

## Overview

A single-page application that guides reps through a 4-stage sales conversation with step-by-step prompts, then writes the call summary directly to Zoho CRM.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Full application — HTML, CSS, JS in one file |
| `server.py` | Python proxy server for Zoho CRM API calls |
| `live-call.html` | Earlier standalone live call page (superseded) |
| `fonts/` | Roboto Flex variable font |

## Features

### Three Tabs

1. **Home** — overview of the 4 sales stages + "Start a live call" button
2. **Question Cheat Sheet** — all prompt questions grouped by stage
3. **Call Scripts** — word-for-word scripts with color-coded boxes:
   - **Teal** = Say lines (read aloud)
   - **Amber** = Listen for cues
   - **Green** = If yes branches
   - **Red** = If no branches
   - **Purple** = If hesitant / other conditionals
   - **Price / Choice / Independence** variant boxes for driver-specific pitches

### Live Call Mode

- Step-through prompt cards across 4 stages (20 prompts)
- 3 trigger inputs with value bucket tagging (Price / Choice / Independence)
- Auto-detects primary driver from keywords and personalises Stage 3 prompts
- Call timer, notes pad, tips panel
- Keyboard navigation (arrow keys, space bar)

### End-of-Call Summary + Zoho CRM Sync

- Generates a structured call summary (date, duration, driver, triggers, notes)
- Copy to clipboard button
- **Zoho CRM integration** — paste the client's lead URL, click "Save to Zoho", and the call notes are written as a Note on their Zoho CRM profile

## How to Run

```bash
cd sales-playbook
python3 server.py
```

Open `http://localhost:8080` in the browser. The server:
- Serves the HTML on port 8080
- Proxies Zoho API calls via TC Graph gateway (handles auth automatically)
- Uses `GRAPH_API_TOKEN` env var (already set in the workspace)

## Zoho CRM Integration

**How it works:**

1. Rep finishes the call and sees the summary screen
2. Pastes the Zoho lead link (e.g. `crm.zoho.com/crm/org724596924/tab/Leads/4637899...`)
3. Clicks **Save to Zoho**
4. The proxy server creates a Note on the lead via the Zoho CRM v6 API
5. Green confirmation or red error is shown

**API flow:**
```
Browser  -->  POST /api/zoho/notes  -->  server.py  -->  TC Graph Gateway  -->  Zoho CRM
              {lead_id, note_title,       (proxy)        (OAuth managed)       /Notes endpoint
               note_content}
```

## The 4 Sales Stages

| Stage | Name | Goal | Prompts |
|-------|------|------|---------|
| 1 | Opening the call | Build rapport, get permission | 5 |
| 2 | Discovering their needs | Uncover 3 key triggers | 6 |
| 3 | Presenting the solution | Match TC to their drivers | 6 |
| 4 | Closing the conversation | Secure the next step | 3 |

## Value Buckets

The playbook identifies which of 3 value drivers matters most to each client:

| Bucket | Keywords | Pitch Focus |
|--------|----------|-------------|
| **Price** ($) | cost, fees, afford, budget, value | Lowest care management fees, more hours per dollar |
| **Choice** (&#x2726;) | choose, pick, carer, flexible | Pick your own carers, self-managed care |
| **Independence** (&#x2302;) | home, control, routine, dignity | Stay at home safely, your routine your way |

Stage 3 prompts automatically adapt based on the tagged primary driver.

## Design

- **Brand colors:** Teal #007F7E, Navy #1E3452, Sky Blue #64BCEA
- **Fonts:** Roboto Flex (UI), Roboto Serif (display), Mulish (brand)
- **No build step** — single HTML file, no framework, no dependencies
- **Responsive** — works on desktop and mobile

## Changelog

- **2026-04-24** — Initial build: 3-tab playbook, live call flow, scripts with color-coded boxes, Zoho CRM note sync via proxy server
