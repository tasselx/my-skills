---
name: flutter-rename-images
description: Rename image files in a directory following Flutter asset naming conventions. Recognizes image content via AI vision to generate descriptive snake_case names with type prefixes (bg, ic, btn, logo, etc.). Use when the user asks to rename images, organize Flutter assets, or standardize image file names.
---

# Flutter Image Renaming

Rename images in a directory by **recognizing their content**, applying Flutter naming conventions.

## Naming Format

```
{type}_{descriptive_name}.{ext}
```

Examples: `ic_arrow_back.png`, `bg_home_gradient.png`, `btn_submit_primary.png`, `logo_app_dark.svg`

## Type Prefix Reference

| Prefix | Meaning | Typical Content |
|--------|---------|-----------------|
| `ic` | Icon | Small icons, symbols, arrows, action indicators |
| `bg` | Background | Full-screen or section backgrounds, gradients, patterns |
| `btn` | Button | Button states, CTA elements |
| `logo` | Logo | Brand logos, app logos |
| `img` | Image | Photos, illustrations, general imagery |
| `banner` | Banner | Promotional banners, hero images |
| `avatar` | Avatar | User avatars, profile placeholders |
| `badge` | Badge | Notification dots, status badges, tags |
| `divider` | Divider | Lines, separators |
| `tab` | Tab | Tab bar icons, navigation items |
| `nav` | Navigation | Navigation-related assets |
| `card` | Card | Card backgrounds, card decorations |
| `placeholder` | Placeholder | Empty states, loading placeholders |
| `illust` | Illustration | Decorative illustrations, onboarding art |

Choose the **most specific** prefix. Fallback to `img` if none match.

## Workflow

### Step 1: Scan & Generate Contact Sheet

Ensure Pillow is installed, then run the scan script:

```bash
pip install Pillow -q
python ~/.cursor/skills/flutter-rename-images/scripts/scan_images.py "<directory>"
```

This outputs:
1. **JSON list** of all image files with index numbers (to stdout).
2. **Contact sheet** PNG (`.contact_sheet.png`) — a single image grid with all thumbnails labeled by `[index]`.

### Step 2: Read Contact Sheet & Recognize

**Read the contact sheet** (ONE image) using the Read tool. Each thumbnail is labeled `[0]`, `[1]`, `[2]`... matching the JSON index.

From this single image, determine the new name for every file:
1. **Type prefix** — pick from the table above.
2. **Descriptive name** — 2-4 words in `snake_case`, specific but concise.
3. **Strip multiplier** — remove any `@2x`, `@3x` from the name.
4. **Preserve extension** — keep original extension, lowercase.

### Step 3: Present Rename Plan

Show the rename mapping as a table, **wait for user confirmation**:

```
| # | Original Name       | New Name               | Reason                    |
|---|---------------------|------------------------|---------------------------|
| 0 | IMG_0012@2x.png     | bg_sunset_mountain.png | Sunset landscape          |
| 1 | download.png        | ic_menu_hamburger.png  | Three-line hamburger icon |
```

### Step 4: Execute Rename

After confirmation, build a JSON array and run:

```bash
python ~/.cursor/skills/flutter-rename-images/scripts/rename_images.py "<directory>" '<json_mapping>'
```

JSON mapping format: `[{"from": "old.png", "to": "new.png"}, ...]`

The script renames files, cleans up the contact sheet, and reports results.

## Naming Rules

1. **All lowercase** — never use uppercase
2. **Snake case** — `home_banner`, not `homeBanner`
3. **No spaces or special chars** — only `a-z`, `0-9`, `_`
4. **No leading numbers** — prefix with type: `ic_3d_rotate`, not `3d_rotate`
5. **No multiplier** — strip `@2x`, `@3x` from output filename
6. **Short but descriptive** — 2-4 words after prefix

## Edge Cases

- **Duplicate names**: Append `_01`, `_02` suffix.
- **Already well-named**: Skip and note in plan.
- **SVG files**: No special handling needed.
- **Ambiguous content**: Use `img_` prefix and describe what you see.
