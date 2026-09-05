import os
import re

directories = [
    r"c:\Users\Tech\ksp_dhrushtii2\frontend\src",
    r"c:\Users\Tech\ksp_dhrushtii2\src"
]

pattern1 = re.compile(re.escape("KSP SENTINEL AI COMMAND"), re.IGNORECASE)
pattern2 = re.compile(re.escape("KSP Sentinel AI Command"), re.IGNORECASE)
pattern3 = re.compile(re.escape("KSP Sentinel AI Engine"), re.IGNORECASE)
pattern4 = re.compile(re.escape("KSP Sentinel AI"), re.IGNORECASE)

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = pattern1.sub("KSP DRISHTI", content)
        new_content = pattern2.sub("KSP DRISHTI", new_content)
        new_content = pattern3.sub("KSP DRISHTI", new_content)
        new_content = pattern4.sub("KSP DRISHTI", new_content)
        
        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

for d in directories:
    for root, dirs, files in os.walk(d):
        for file in files:
            if file.endswith(('.js', '.jsx', '.css', '.html')):
                filepath = os.path.join(root, file)
                replace_in_file(filepath)
