# System Scheduling -- **IN REFINEMENT**

## WHAT / TO WHOM / WHY

**WHAT**: A scheduling mechanism that ensures the pipeline runs automatically every morning, even if the Mac has gone to sleep. This includes a cron job to trigger the pipeline and a keep-awake mechanism so the laptop is actually on when the cron fires.

**TO WHOM**: You. If you have to remember to run the pipeline manually, you won't — and then Brief is dead. This has to be fully automatic.

**WHY**: The whole point of Brief is "you wake up and the digest is in your inbox." If the laptop is asleep at 5 AM and the cron job never fires, there's no digest. A reliable wake/keep-awake mechanism is the difference between a tool you use every day and a script you ran once.

## Requirements

### Cron Job
- A cron job (or launchd plist — Mac's native scheduler) triggers the pipeline daily at a configured time (default: 5:00 AM, giving the pipeline time to finish before the 7:00 AM delivery target)
- The job runs the full pipeline: ingest → enrich → rank → generate → deliver
- If the pipeline is already running (e.g., from a manual trigger), the cron job doesn't start a second instance
- Logs are written so you can check "did it run last night?" without guessing

### Keep-Awake
- A mechanism ensures the Mac is awake (or wakes up) at the scheduled time
- Options include:
  - **macOS Power Schedule**: Built-in setting to wake the Mac at a specific time (System Settings → Energy)
  - **Caffeine or similar app**: Prevents sleep during a window
  - **pmset schedule**: Command-line tool to schedule wake events
- The chosen mechanism should survive reboots (persist across restarts)

### Failure Handling
- If the Mac was off or asleep and the scheduled time was missed, the pipeline runs as soon as the Mac is next awake (catch-up behavior)
- If the pipeline fails mid-run, it logs the failure and the delivery spec (008) sends a notification email

## Success Criteria

- [ ] Pipeline runs automatically every morning without manual intervention
- [ ] Mac wakes from sleep (or is prevented from sleeping) at the scheduled time
- [ ] The scheduling mechanism survives reboots
- [ ] A missed schedule is caught up on the next wake
- [ ] Pipeline doesn't run twice if triggered while already running
- [ ] Logs confirm whether the pipeline ran and whether it succeeded
