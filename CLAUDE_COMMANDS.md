# Claude Code — Command Reference

Quick reference for all Claude Code slash commands with practical use cases.

---

## Core Session Commands

| Command | What it does | Use case |
|---------|-------------|----------|
| `/help` | List all available commands | When you forget a command name |
| `/clear` | Clear the current conversation context | Start fresh after a long session; free up context window |
| `/exit` | Exit Claude Code | End the session cleanly |
| `/status` | Show current model, context usage, and cost | Check how much context is left before it compresses |
| `/cost` | Show token usage and estimated cost for the session | Audit spend before closing a long session |

---

## Model & Configuration Commands

| Command | What it does | Use case |
|---------|-------------|----------|
| `/model` | Switch the active Claude model | Switch from Sonnet to Opus for a complex task; Haiku for quick lookups |
| `/model opus` | Switch to Claude Opus 4.7 | Deep reasoning, complex architecture decisions |
| `/model sonnet` | Switch to Claude Sonnet 4.6 | Balanced quality and speed for everyday coding |
| `/model haiku` | Switch to Claude Haiku 4.5 | Fast, cheap responses for simple questions |
| `/fast` | Toggle fast mode (Opus 4.6 with faster output) | When you want Opus quality with reduced latency |
| `/config` | Open settings in your editor | Adjust theme, keybindings, permissions |

---

## Project & Codebase Commands

| Command | What it does | Use case |
|---------|-------------|----------|
| `/init` | Generate a `CLAUDE.md` file for the project | Onboard Claude to a new repo so it understands your conventions |
| `/review` | Review the current branch's changes as a pull request | Pre-commit code review before opening a PR |
| `/review <PR#>` | Review a specific GitHub PR by number | Review teammate's PRs from the terminal |
| `/security-review` | Run a security audit on pending branch changes | Before merging auth, payments, or data-handling code |

---

## Memory Commands

| Command | What it does | Use case |
|---------|-------------|----------|
| `/memory` | View and edit Claude's persistent memory files | Check what Claude remembers about you and this project |

> Claude automatically saves preferences, feedback, and project context across sessions.
> Use `/memory` to view or correct stored facts.

---

## Automation & Scheduling Commands

| Command | What it does | Use case |
|---------|-------------|----------|
| `/loop <prompt>` | Run a prompt repeatedly at a self-paced interval | Poll a build, watch a deploy, babysit a long-running task |
| `/loop 5m <prompt>` | Run a prompt every 5 minutes | Check CI status every 5 minutes until it passes |
| `/schedule` | Create, list, or delete scheduled agents (cron jobs) | Run a daily code review, nightly test summary, weekly PR digest |

---

## Productivity & Quality Commands

| Command | What it does | Use case |
|---------|-------------|----------|
| `/simplify` | Review changed code for quality and reduce complexity | After a big feature — ask Claude to simplify what it just wrote |
| `/fewer-permission-prompts` | Auto-allowlist common read-only tool calls | Reduce interruptions when Claude reads many files |
| `/update-config` | Edit `settings.json` for hooks, permissions, env vars | Set up automated behaviors ("after every commit, run tests") |
| `/keybindings-help` | Customize keyboard shortcuts | Rebind Ctrl+Enter to submit, add chord shortcuts |

---

## Developer / API Commands

| Command | What it does | Use case |
|---------|-------------|----------|
| `/claude-api` | Build or debug Anthropic SDK code | Add streaming, tool use, caching, or thinking to a Python/TS project |
| `/claude-api migrate` | Migrate existing Claude API code to a newer model | Upgrade from claude-3.5-sonnet to claude-sonnet-4-6 |

---

## Terminal & IDE Setup

| Command | What it does | Use case |
|---------|-------------|----------|
| `/terminal-setup` | Configure shell integration (auto-detect pwd, env) | First-time setup on a new machine |
| `/vim` | Toggle vim keybindings in the input box | If you prefer vim-style editing in the prompt |
| `/pr_comments` | Fetch and display comments on the current PR | Review feedback without leaving the terminal |
| `/doctor` | Run a health check on the Claude Code installation | Diagnose issues with API keys, permissions, or updates |
| `/login` | Authenticate with Anthropic | First-time login or re-auth after token expiry |
| `/logout` | Sign out of your Anthropic account | Switch accounts or revoke session |

---

## Keyboard Shortcuts (IDE Extension)

| Shortcut | Action |
|----------|--------|
| `Enter` | Submit message |
| `Shift + Enter` | New line in prompt |
| `Up arrow` | Cycle through prompt history |
| `Esc` | Cancel current tool execution |
| `Ctrl + C` | Interrupt Claude mid-response |

---

## Practical Workflows

### Start a new project
```
/init                          # generate CLAUDE.md with project context
```

### Before opening a PR
```
/review                        # get a full code review of your branch
/security-review               # check for vulnerabilities
```

### Debug a slow session
```
/status                        # check remaining context window
/cost                          # see token usage
/clear                         # reset if context is bloated
```

### Upgrade Claude SDK code
```
/claude-api migrate            # guided migration to latest model
```

### Reduce interruptions on a large codebase
```
/fewer-permission-prompts      # auto-allow common read-only operations
```

### Keep tabs on a long deploy
```
/loop 3m check if http://localhost:3000 is responding
```

### Schedule a daily standup summary
```
/schedule                      # create a cron agent that runs every morning
```

---

## Tips

- **Context limit:** Claude Code compresses older messages automatically. Use `/status` to see how full the context window is.
- **Model cost:** Opus > Sonnet > Haiku in both capability and cost. Switch with `/model` per task.
- **Hooks:** Use `/update-config` to wire up shell commands that run automatically before/after tool use — e.g. run tests after every file edit.
- **CLAUDE.md:** The `/init` command generates this file. Keep it updated — Claude reads it at the start of every session.
- **Memory:** Claude builds up a persistent memory of your preferences, project context, and feedback. Edit it any time with `/memory`.
