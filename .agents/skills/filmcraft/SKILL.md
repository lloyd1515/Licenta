---
name: filmcraft
description: "Professional video editing with FilmCraft MCP (Premiere Pro parity). Timeline assembly, multi-track cutting, media import, ripple edits, audio tracks, and preview rendering."
---

# FilmCraft Skill

FilmCraft is a desktop-class timeline video editor (Adobe Premiere Pro parity) operated via MCP commands.

## Architecture

* **Timebase:** FilmCraft uses high-precision ticks: `254016000000` ticks per second. Tools also accept seconds (float), frames, or standard timecode (`HH:MM:SS:FF`).
* **Tracks:** Multiple video (`V1`, `V2`, ...) and audio (`A1`, `A2`, ...) tracks.
* **Commands:** Executed via `call_mcp_tool(ServerName="filmcraft", ToolName="command_run", Arguments={"id": "...", "params": {...}})`.

## Core MCP Tools

| Tool | Purpose |
| :--- | :--- |
| `project_inspect` | Returns project bins, media items, durations, and active sequence |
| `sequence_inspect` | Inspects tracks, clips, in/out points, and transitions on active timeline |
| `media_import` | Imports audio, video, and image files into project bins |
| `command_list` | Lists all available engine commands |
| `command_run` | Runs a command with `{id, params}` (fully undoable) |
| `command_batch` | Executes an ordered array of commands in a single call |
| `render_preview` | Renders a video preview of the active work area |
| `render_frame` | Renders a single still frame at a given timestamp |

## Standard Workflow

1. **Inspect Project & Sequence:**
   ```json
   {
     "ServerName": "filmcraft",
     "ToolName": "project_inspect",
     "Arguments": {}
   }
   ```
2. **Import Media Assets:**
   ```json
   {
     "ServerName": "filmcraft",
     "ToolName": "media_import",
     "Arguments": {
       "paths": ["/absolute/path/to/voiceover.wav", "/absolute/path/to/animation.mp4"]
     }
   }
   ```
3. **Assemble Timeline (Add clips to sequence):**
   ```json
   {
     "ServerName": "filmcraft",
     "ToolName": "command_run",
     "Arguments": {
       "id": "clip.insert",
       "params": {
         "item": 5,
         "track": 1,
         "time": 0.0
       }
     }
   }
   ```
4. **Render Preview / Export:**
   ```json
   {
     "ServerName": "filmcraft",
     "ToolName": "render_preview",
     "Arguments": {
       "quality": "preview",
       "format": "mp4"
     }
   }
   ```
