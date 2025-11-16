# Terminal Theme Integration

The TUI is designed to **sync with your terminal's theme** and use **100% of the terminal space**.

## Full Screen Layout

The TUI fills your entire terminal window with no wasted space:

```
┌─────────────────────────────────────────────────────────┐ ← Terminal edge
│ Orbiton Agent • model • ~/directory                    │ ← Header (1 line)
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ✓ Agent ready: react                                   │
│                                                         │
│ > What is the state of prediction markets?             │
│ • Prediction markets are seeing growth in 2024...      │ ← History Pane
│                                                         │   (fills all
│   ▸ fetch_market_data(market="polymarket")            │    available
│     ↳ Total volume: $1.2B                              │    space)
│                                                         │
│   💭 Thought for 0.8s                                  │
│                                                         │
│ • The data shows strong trends...                      │
│                                                         │
├─────────────────────────────────────────────────────────┤ ← Top separator
│ > type your message here_                              │ ← Input (1 line)
├─────────────────────────────────────────────────────────┤ ← Bottom separator
│ esc interrupt • ctrl+l clear • ctrl+c exit             │ ← Shortcuts (1 line)
└─────────────────────────────────────────────────────────┘ ← Terminal edge
```

**Total overhead**: 5 lines (header + 2 separator lines + input + shortcuts)
**History pane**: Everything else (terminal height - 5)

The input bar is **clearly separated** with horizontal lines above and below, making it easy to see where to type.

## Color Syncing

The TUI uses **ANSI colors** that adapt to your terminal theme:

### Light Terminal Theme
If your terminal uses a light theme:
- User messages: Bright cyan (readable on light background)
- Agent messages: Bright green (readable on light background)
- Background: Your terminal's default light background
- Text: Your terminal's default dark text

### Dark Terminal Theme
If your terminal uses a dark theme:
- User messages: Bright cyan (readable on dark background)
- Agent messages: Bright green (readable on dark background)
- Background: Your terminal's default dark background
- Text: Your terminal's default light text

### How It Works

Instead of hardcoding colors like `#00d4ff`, we use:
- `ansibrightcyan` - Uses your terminal's bright cyan
- `ansibrightgreen` - Uses your terminal's bright green
- `dim` - Uses your terminal's dim/gray color
- `reverse` - Swaps foreground/background (for header)
- Empty string `""` - Uses terminal default colors

This means the TUI will look good in:
- Solarized (Dark or Light)
- Dracula
- Nord
- One Dark
- Gruvbox
- Any custom terminal color scheme

## Color Reference

| Element | Style | Adapts to Terminal |
|---------|-------|-------------------|
| Header | `reverse bold` | ✅ Uses terminal fg/bg swapped |
| User messages | `ansibrightcyan bold` | ✅ Terminal's bright cyan |
| Agent messages | `ansibrightgreen` | ✅ Terminal's bright green |
| Tool actions | `ansigreen` | ✅ Terminal's green |
| Tool results | `ansicyan` | ✅ Terminal's cyan |
| Thinking | `dim italic` | ✅ Terminal's dim color |
| Errors | `ansibrightred bold` | ✅ Terminal's bright red |
| Warnings | `ansiyellow` | ✅ Terminal's yellow |
| Success | `ansibrightgreen` | ✅ Terminal's bright green |
| Info/hints | `dim` | ✅ Terminal's dim color |
| Background | `""` (default) | ✅ Terminal's background |
| Text | `""` (default) | ✅ Terminal's foreground |

## Space Efficiency

The layout maximizes usable space:

1. **Compact header**: 1 line (was 3)
   - All info on one line: `Agent • model • directory`

2. **No borders**: Removed frame around input
   - Saves 2 lines of vertical space

3. **Minimal shortcuts**: 1 line
   - Shows only essential keyboard hints

4. **No padding**: Zero wasted space
   - History pane expands to fill all available space

## Terminal Compatibility

Works with all modern terminals:
- **macOS**: Terminal.app, iTerm2, Warp, Alacritty
- **Linux**: GNOME Terminal, Konsole, Kitty, Alacritty
- **Windows**: Windows Terminal, ConEmu, Cmder

## Customization

Want to override the colors? Edit `console/tui.py` in `_get_style()`:

```python
def _get_style(self) -> Style:
    return Style.from_dict({
        # Change user message color
        "user": "ansimagenta bold",  # Instead of cyan

        # Change agent message color
        "agent": "ansiblue",  # Instead of green

        # Add custom background
        "history": "bg:ansiblack",  # Black background
    })
```

But the defaults are designed to work universally!

## Testing Different Themes

Try your TUI in different terminal themes:

```bash
# Run the demo
cd orbiton-agent
./run.sh

# Or demo mode
PYTHONPATH=$PWD:$PYTHONPATH uv run python console/demo_tui.py
```

Then change your terminal's color scheme and restart - the TUI adapts!

## Benefits

✅ **No eye strain** - Colors match your preferred terminal theme
✅ **No surprises** - Looks consistent with your terminal
✅ **Maximum space** - No wasted pixels
✅ **Professional** - Clean, minimal, focused
✅ **Accessible** - Works with high-contrast themes
✅ **Future-proof** - Works with themes that don't exist yet
