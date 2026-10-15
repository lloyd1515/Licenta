---
name: effectcraft
description: "Motion graphics and visual effects composition with EffectCraft MCP (After Effects parity). Compositions, text layers, vector shapes, keyframing, property paths, 306 effects, and video rendering."
---

# EffectCraft Skill

EffectCraft is an Adobe After Effects-class motion graphics compositor operated via MCP tools.

## Architecture

* **Compositions:** Top-level visual containers with dimensions, framerate, duration, and layers.
* **Layers:** Text layers (`layer.newText`), solids (`layer.newSolid`), shapes (`layer.newShape`), nulls, adjustment layers, 3D cameras, and imported footage.
* **Properties:** Hierarchical paths (e.g. `transform/position`, `transform/opacity`, `transform/scale`, `effects/#1/blurriness`).
* **Timebase:** Floating-point seconds (`0.0`, `1.5`, `3.25`).
* **Effects:** 306 registered native GPU/CPU effects.

## Core MCP Tools

| Tool | Purpose |
| :--- | :--- |
| `get_state` | Retrieves active comp, timeline cursor, selection, and engine capabilities |
| `get_project` | Lists project tree, items, comps, and folders |
| `get_comp` | Inspects composition properties and layer stack |
| `get_layer` | Inspects a layer's transforms, effects, masks, and properties |
| `command_list` | Lists all 680+ available engine commands with parameter signatures |
| `command_run` | Runs a command with `{id, params}` (undoable) |
| `command_batch` | Runs an array of commands sequentially |
| `set_property` | Sets static or animated property values |
| `add_keyframe` | Places keyframes at specific timestamps for smooth interpolation |
| `add_effect` | Applies visual effects (blur, glow, color grading, particle systems) |
| `render_preview` | Renders a video preview clip (MP4 / WebM) |
| `render_frame` | Renders a still frame at specified time |

## Standard Workflow

1. **Create Composition:**
   ```json
   {
     "ServerName": "effectcraft",
     "ToolName": "command_run",
     "Arguments": {
       "id": "comp.new",
       "params": {
         "name": "WiFi_CSI_Scene1",
         "width": 1920,
         "height": 1080,
         "frameRate": 30,
         "duration": 15.0,
         "background": "#070a13"
       }
     }
   }
   ```
2. **Add Solid Background & Text:**
   ```json
   {
     "ServerName": "effectcraft",
     "ToolName": "command_run",
     "Arguments": {
       "id": "layer.newText",
       "params": {
         "text": "Wi-Fi CSI Sensing",
         "fontSize": 48,
         "font": "JetBrains Mono",
         "position": [960, 540]
       }
     }
   }
   ```
3. **Animate Layer Properties (Keyframing):**
   ```json
   {
     "ServerName": "effectcraft",
     "ToolName": "add_keyframe",
     "Arguments": {
       "layer": 1,
       "path": "transform/opacity",
       "time": 0.0,
       "value": 0.0
     }
   }
   ```
   Followed by:
   ```json
   {
     "ServerName": "effectcraft",
     "ToolName": "add_keyframe",
     "Arguments": {
       "layer": 1,
       "path": "transform/opacity",
       "time": 0.8,
       "value": 100.0
     }
   }
   ```
4. **Render Preview Clip:**
   ```json
   {
     "ServerName": "effectcraft",
     "ToolName": "render_preview",
     "Arguments": {
       "format": "mp4",
       "range": "workArea"
     }
   }
   ```
