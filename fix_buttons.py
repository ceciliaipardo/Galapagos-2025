#!/usr/bin/env python3
"""Fix all translation buttons to use emoji instead of images"""

with open('GalapagosCarTracking_translated.kv', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all instances of image-based translation buttons
lines = content.split('\n')
new_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this is a translation button (globe icon)
    if "background_normal: 'globe_icon.png'" in line:
        # This is the start of an image-based button
        # We need to replace it with an emoji-based button
        # Skip the current line and next line (background_down)
        new_lines.append(line.replace("background_normal: 'globe_icon.png'", "background_normal: ''"))
        i += 1
        if i < len(lines) and "background_down: 'globe_icon.png'" in lines[i]:
            # Skip background_down line
            i += 1
        # Now add text and canvas for emoji button after background_color line
        while i < len(lines):
            new_lines.append(lines[i])
            if 'background_color:' in lines[i] and 'on_release:' not in lines[i]:
                # Add emoji text after background_color
                indent = len(lines[i]) - len(lines[i].lstrip())
                new_lines.append(' ' * indent + "text: '🌐'")
                new_lines.append(' ' * indent + "font_size: '28sp'")
                new_lines.append(' ' * indent + "color: 0.2, 0.2, 0.2, 1")
                new_lines.append(' ' * indent + "canvas.before:")
                new_lines.append(' ' * (indent + 4) + "Color:")
                new_lines.append(' ' * (indent + 8) + "rgba: 0.9, 0.9, 0.9, 1")
                new_lines.append(' ' * (indent + 4) + "Ellipse:")
                new_lines.append(' ' * (indent + 8) + "pos: self.pos")
                new_lines.append(' ' * (indent + 8) + "size: self.size")
                i += 1
                break
            i += 1
    else:
        new_lines.append(line)
        i += 1

# Write back
with open('GalapagosCarTracking_translated.kv', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("Fixed all translation buttons!")
