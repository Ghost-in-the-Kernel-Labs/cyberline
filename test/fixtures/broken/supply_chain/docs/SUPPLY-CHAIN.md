# Supply chain: a planted break for test/test_supply_chain.py

## Agent files

| Path | Tools |
| --- | --- |
| `.claude/agents/patch-reviewer.md` | `tools: Read, Grep, Glob` |
| `.claude/agents/reputation-checker.md` | `tools: WebSearch, WebFetch` |
| `.claude/agents/gone.md` | `tools: Read` |

## Auto-execution surfaces

| Path | Kind |
| --- | --- |
| `.claude/agents/patch-reviewer.md` | an agent file |
| `.claude/agents/reputation-checker.md` | an agent file |
| `.claude/agents/third.md` | an agent file |
| `.github/workflows/ci.yml` | a workflow |
| `scripts/old.sh` | a script the gate or the commit runs |
