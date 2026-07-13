# MCP Setup

Model Context Protocol servers for GraphRoute-TS. **Conservative by policy:** only
add a server that provides a capability Claude Code lacks natively.

## Configured: GitHub (official, hosted)

`.mcp.json` (project scope):

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${GITHUB_MCP_PAT}" }
    }
  }
}
```

- **Publisher / repo:** GitHub — `github/github-mcp-server`.
- **Why hosted (HTTP) not Docker:** Docker is not installed on this machine; the
  GitHub-hosted remote server needs no local container.
- **Capability needed:** repository inspection, issues, pull requests, code review,
  release/commit info — beyond Claude Code's native local git/file access.
- **Auth:** `${GITHUB_MCP_PAT}` is expanded from the environment at load time. **No
  raw token is written into `.mcp.json`.** Use a fine-grained PAT with least
  privilege (read-only unless you need to open PRs/issues).
- **Setup:** put `GITHUB_MCP_PAT=<pat>` in your shell env (or `.env`, gitignored)
  before starting Claude Code.

### Enable & validate

```bash
# Ensure the token is exported (fish):
set -x GITHUB_MCP_PAT (cat ~/.secrets/github_mcp_pat)   # example; keep the file private

# In Claude Code, approve the project .mcp.json when prompted, then:
claude mcp list          # should show: github  ✓ connected
```

Record the `claude mcp list` result below once the token is set.

```
# claude mcp list  →  (paste status here after enabling)
github: not yet validated — requires GITHUB_MCP_PAT to be set by the user
```

## Deliberately NOT added

Per policy, these were considered and rejected for now:

- **Filesystem MCP** — Claude Code already has native repository file access.
- **"Sequential thinking" servers** — no capability gain.
- **Unofficial web-search / research-paper servers** — provenance/maintenance risk.
- **Any server requesting broad filesystem or credential access.**

## Adding another server (checklist)

Document before adding: publisher, repository, maintenance status, exact capability
needed, permissions requested, authentication method, security risk, and why native
Claude Code tools are insufficient. Prefer official, actively-maintained servers and
environment-variable auth. Never commit tokens.
