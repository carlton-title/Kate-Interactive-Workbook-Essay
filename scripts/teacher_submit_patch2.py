from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

s = s.replace('🔍 Analyze My Sentence', '📨 Submit My Work')
s = s.replace('Submitting...', 'Submitting your work...')

start = s.index('/* =========================================================\n   ANALYZE BUTTON\n========================================================= */')
end = s.index('\n\n/* =========================================================\n   TOPICS', start)
handler = '''/* =========================================================\n   SUBMIT BUTTON\n========================================================= */\n\n$("check").addEventListener(\n  "click",\n  async () => {\n\n    const text =\n      $("answer").value.trim();\n\n    if(!text){\n      alert("Write one topic sentence before submitting.");\n      return;\n    }\n\n    $("check").disabled = true;\n    $("analyzing").classList.add("show");\n    $("feedback").classList.remove("show");\n    $("saveStatus").textContent = "";\n\n    try {\n      const attempts = records.filter(r =>\n        r.topic === topic &&\n        r.exercise_number === exerciseIndex + 1\n      ).length;\n\n      const saved = await saveSubmission(text, attempts + 1);\n      if(!saved) return;\n\n      $("saveStatus").textContent =\n        "✓ Workbook successfully submitted. Wait for your teacher to review your work.";\n      $("saveStatus").className =\n        "save-status save-success";\n\n      await loadRecords();\n      $("next").disabled = false;\n\n    }\n    catch(error){\n      console.error("Submission failed:", error);\n      $("saveStatus").textContent =\n        "⚠️ Your work could not be submitted. Please try again.";\n      $("saveStatus").className =\n        "save-status save-error";\n    }\n    finally{\n      $("check").disabled = false;\n      $("analyzing").classList.remove("show");\n    }\n  }\n);\n'''
s = s[:start] + handler + s[end:]

start = s.index('async function saveSubmission(')
end = s.index('\n\n/* =========================================================\n   RECORD FEEDBACK', start)
save = '''async function saveSubmission(text, attemptNumber){\n\n  const { error } =\n    await supabaseClient\n      .from("essay_submissions")\n      .insert({\n        student_name: currentStudentName,\n        student_id: currentStudentID,\n        student_number: currentStudentNumber,\n        topic: topic,\n        exercise_number: exerciseIndex + 1,\n        strategy: $("strategy").value,\n        original_sentence: text,\n        annotated_sentence: escapeHTML(text),\n        corrected_sentence: null,\n        teacher_feedback: null,\n        score: null,\n        attempt_number: attemptNumber,\n        completed_at: new Date().toISOString(),\n        review_status: "pending"\n      });\n\n  if(error){\n    console.error("Supabase submission error:", error);\n    return false;\n  }\n\n  return true;\n}\n'''
s = s[:start] + save + s[end:]

p.write_text(s, encoding='utf-8')
