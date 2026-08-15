from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove the student-facing AI analyze function. The submit flow now writes a pending record only.
start = s.index('/* =========================================================\n   ANALYSIS\n========================================================= */')
end = s.index('\nfunction correctedSentence(text){', start)
s = s[:start] + '''/* =========================================================\n   TEACHER REVIEW WORKFLOW\n   Student submissions are reviewed by the teacher.\n========================================================= */\n\n''' + s[end:]

# Remove the old generated AI feedback formatter; teacher-authored fields are stored directly.
start = s.index('function generateRecordFeedback(')
end = s.index('\n\n/* =========================================================\n   LOAD RECORDS', start)
s = s[:start] + s[end:]

p.write_text(s, encoding='utf-8')
