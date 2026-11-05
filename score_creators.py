import pandas as pd
import json

creators = pd.read_csv('creators.csv', encoding='latin1')

print('=== ALL CREATORS BASIC INFO ===')
for i, row in creators.iterrows():
    print(f"{row['handle']}: followers={row['followers']}, verified={row['verified']}, "
          f"posts_in_file={row['posts_infile'] if 'posts_infile' in row else 'N/A'}")

print()
print('=== THEMES ===')
for i, row in creators.iterrows():
    themes = row['themes']
    if isinstance(themes, str):
        print(f"{row['handle']}: {themes}")
    else:
        print(f"{row['handle']}: {themes}")

print()
print('=== FORMAT HABITS ===')
for i, row in creators.iterrows():
    fmt = row['format_habits']
    if isinstance(fmt, str):
        print(f"{row['handle']}: {fmt}")
    else:
        print(f"{row['handle']}: {fmt}")

print()
print('=== VOICE ===')
for i, row in creators.iterrows():
    voice = row['voice']
    if isinstance(voice, str):
        print(f"{row['handle']}: {voice[:150]}...")
    else:
        print(f"{row['handle']}: {voice}")

print()
print('=== WHAT FEELS NATIVE ===')
for i, row in creators.iterrows():
    wfn = row['what_feels_native']
    if isinstance(wfn, str):
        print(f"{row['handle']}: {wfn[:150]}...")
    else:
        print(f"{row['handle']}: {wfn}")

print()
print('=== CATCHPHRASES ===')
for i, row in creators.iterrows():
    cp = row['catchphrases']
    if isinstance(cp, str):
        print(f"{row['handle']}: {cp[:150]}...")
    else:
        print(f"{row['handle']}: {cp}")