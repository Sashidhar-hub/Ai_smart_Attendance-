"""
Fix escaped quotes in app.py that were introduced by automation script
"""

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix escaped quotes
content = content.replace("\\'", "'")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed escaped quotes in app.py")
print("🔄 App should now compile successfully")
