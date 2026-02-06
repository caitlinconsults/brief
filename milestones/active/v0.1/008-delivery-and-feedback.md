# Delivery -- **IN REFINEMENT**

## WHAT / TO WHOM / WHY

**WHAT**: The mechanism that delivers the completed digest to the user by saving it as a formatted file to a local folder and automatically opening it when the Mac is next used. No email, no web app — just a file that appears on your screen.

**TO WHOM**: You. If you have to go hunting for the digest, you won't read it. It needs to show up in front of you.

**WHY**: The simplest delivery that actually works. No email service to configure, no spam filters to fight, no formatting to debug across mail clients. The pipeline writes a file, your Mac opens it. Done.

## How It Works

1. The pipeline finishes its daily run and generates the digest
2. The digest is saved as a well-formatted HTML file to a designated folder (e.g., `~/Briefs/`)
3. The file is named with the date (e.g., `brief-2026-02-05.html`)
4. A macOS Login Item or Launch Agent opens the most recent unread digest when you next log in or wake the Mac
5. You open your laptop, the digest is right there

## Requirements

### File Output
- The digest is saved as an HTML file to a configurable local folder (default: `~/Briefs/`)
- Files are named by date so they're naturally sorted and easy to find later
- The HTML is self-contained (no external dependencies) and looks good in any browser
- Old digests remain in the folder for reference — they're not deleted automatically

### Auto-Open
- The most recent digest opens automatically in the default browser when the Mac wakes or is logged into
- If the digest has already been opened (tracked via a simple marker), it doesn't open again
- If no new digest exists (pipeline didn't run), nothing opens — no error, no notification

### Failure Handling
- If the pipeline fails, a simple error file is written instead (e.g., `brief-2026-02-05-error.html`) with a short message explaining what went wrong
- No silent failures — if something broke, you see it

## Deferred to Post-MVP

- **Email delivery**: Via SMTP (can be configured when needed)
- **Feedback buttons**: Requires a web endpoint; deferred until core pipeline is proven
- **Multiple delivery channels**: Slack, Notion, Obsidian, etc.

## Success Criteria

- [ ] Digest is saved as an HTML file to the configured folder after each pipeline run
- [ ] File is named with the date and sorted chronologically
- [ ] HTML renders well in Safari/Chrome with no external dependencies
- [ ] Digest auto-opens in the browser on Mac wake/login
- [ ] Already-opened digests don't re-open
- [ ] Failed pipeline runs produce an error file, not silence
