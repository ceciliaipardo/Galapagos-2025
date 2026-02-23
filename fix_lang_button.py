#!/usr/bin/env python3
"""Fix language button to use property binding"""

with open('GalapagosCarTracking_translated.kv', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace emoji with property binding
content = content.replace("text: '🌐'", 'text: app.language_button_text')

with open('GalapagosCarTracking_translated.kv', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all language buttons to use property binding!")
