# Approved Tool List — **IN REFINEMENT**

## WHAT / TO WHOM / WHY

**WHAT**: A per-profile configuration that defines which AI tools the digest is allowed to recommend, and which it must never mention. The enrichment and digest prompts use this list to filter out tools the audience can't actually use.

**TO WHOM**: Team Brief readers — non-technical coworkers in marketing, operations, client services, and similar roles who use employer-provided tools on managed work laptops.

**WHY**: The current Team Brief will happily recommend Codex, Cursor, Claude Code, or any other tool that showed up in a source article — even if those tools require local installation, admin access, or a developer background. Recommending tools people can't use erodes trust in the digest. An approved tool list ensures every "Try This" recommendation is something the reader can actually try.

## Requirements

- Each profile config (YAML) can define an `allowed_tools` list and/or a `blocked_tools` list
- When `allowed_tools` is set, the enrichment prompt instructs Claude to only score items highly for the Try This lane if they involve tools from the approved list
- When `blocked_tools` is set, the digest prompt instructs Claude to never recommend those tools, even if they appear in source material
- If neither list is set, behavior is unchanged (no filtering)
- The lists are plain strings (tool names as humans would say them: "Microsoft Copilot", "ChatGPT", "Power Automate") — not slugs or IDs
- The digest generation prompt includes the constraint so that lane summaries don't say "try downloading Cursor" when Cursor is blocked
- Works for any profile, not just team — a future "security" profile might block consumer tools, for example

## Example Config

The team profile would add something like:

```
allowed_tools: Microsoft Copilot, ChatGPT, Power Automate, Microsoft 365, Google Gemini, Canva AI
blocked_tools: Codex, GitHub Copilot, Claude Code, Cursor, VS Code extensions, Homebrew
```

## Success Criteria

- [ ] Team profile config includes `allowed_tools` and `blocked_tools` lists
- [ ] Enrichment prompt references the tool list when scoring lane affinity for the Try This lane
- [ ] Digest prompt includes a constraint like "Only recommend tools from this approved list"
- [ ] Running the team pipeline does not produce recommendations for blocked tools
- [ ] Technical profile (no tool list configured) behaves identically to today — no regression
- [ ] Tool lists are config-only — no code changes needed to update the list of approved tools
