# scrawl3d skill for Claude

A skill that teaches Claude how to design and build 3D-printable parts in
[scrawl3d](https://scrawl3d.com) through its MCP tools: the build workflow,
coordinate conventions, which tool fits which shape, printability (DfAM),
materials and export.

## 1. Connect scrawl3d to Claude

Create an API key in scrawl3d (Account › API keys), then:

```sh
claude mcp add --transport http scrawl3d https://scrawl3d.com/api/mcp --header "Authorization: Bearer s3d_…"
```

claude.ai / Claude Desktop: Settings › Connectors › Add custom connector, URL
`https://www.scrawl3d.com/api/mcp` (sign in when asked; no key needed).

Keep scrawl3d open in a browser tab: Claude works in that tab, live.

## 2. Add the skill

Claude Code, as a plugin:

```sh
/plugin marketplace add scrawl3d/scrawl3d_skill
/plugin install scrawl3d@scrawl3d
```

Or copy `skills/scrawl3d` into `~/.claude/skills/`.

claude.ai: zip the `skills/scrawl3d` folder and upload it under
Settings › Capabilities › Skills.

## What's in it

- `skills/scrawl3d/SKILL.md`: the workflow and rules Claude follows.
- `references/recipes.md`: enclosures, brackets, wheels, car bodies, blades,
  gears, splitting parts that are too big for the bed.
- `references/printing.md`: orientation, overhangs, wall thickness, fits,
  materials.

## License

MIT
