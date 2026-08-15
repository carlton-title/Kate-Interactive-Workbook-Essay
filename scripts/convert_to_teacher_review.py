from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

s = s.replace('🔍 Analyze My Sentence', '📨 Submit My Work')
s = s.replace('Submitting...', 'Submitting your work...')
s = s.replace(
    'Your mistakes are turned into a short\n    writing lesson. Study this page before\n    writing your next sentence.',
    'Your work will be reviewed personally by your teacher.\n    After your teacher reviews it, your seven-part learning page will appear here.'
)

# Remove the student-facing AI analysis function.
start = s.index('/* =========================================================\n   ANALYSIS\n========================================================= */')
end = s.index('\nfunction correctedSentence(text){', start)
s = s[:start] + '''/* =========================================================\n   TEACHER REVIEW WORKFLOW\n   Student submissions are stored as pending.\n   No AI tutor feedback is generated or shown.\n========================================================= */\n\n''' + s[end:]

# Replace the save function with a submission-only writer.
start = s.index('async function saveSubmission(')
end = s.index('\n\n/* =========================================================\n   RECORD FEEDBACK', start)
new_save = '''async function saveSubmission(text, attemptNumber){

  const { error } =
    await supabaseClient
      .from("essay_submissions")
      .insert({
        student_name: currentStudentName,
        student_id: currentStudentID,
        student_number: currentStudentNumber,
        topic: topic,
        exercise_number: exerciseIndex + 1,
        strategy: $("strategy").value,
        original_sentence: text,
        annotated_sentence: escapeHTML(text),
        corrected_sentence: null,
        teacher_feedback: null,
        score: null,
        attempt_number: attemptNumber,
        completed_at: new Date().toISOString(),
        review_status: "pending",
        reviewed_at: null,
        what_needs_attention: null,
        learn_why: null,
        academic_words: null,
        teacher_model_sentence: null,
        teacher_model_topic: null,
        teacher_model_main_idea: null,
        teacher_model_vocabulary: null,
        teacher_next_step: null
      });

  if(error){
    console.error("Supabase submission error:", error);
    $("saveStatus").textContent =
      "⚠️ Your work could not be submitted. Please try again.";
    $("saveStatus").className =
      "save-status save-error";
    return false;
  }

  $("saveStatus").textContent =
    "✓ Workbook successfully submitted. Wait for your teacher to review your work.";
  $("saveStatus").className =
    "save-status save-success";
  return true;
}
'''
s = s[:start] + new_save + s[end:]

# Remove generated AI feedback storage.
start = s.index('function generateRecordFeedback(')
end = s.index('\n\n/* =========================================================\n   LOAD RECORDS', start)
s = s[:start] + '\n' + s[end:]

# Replace the learning-page renderer with the pending state.
start = s.index('function showLearningPage(')
end = s.index('\n\n/* =========================================================\n   SAVE TO SUPABASE', start)
pending = '''function showPendingSubmission(){

  $("feedbackItems").innerHTML = `
    <div style="padding:14px;background:#eff6ff;border-left:5px solid #2563eb;border-radius:9px;line-height:1.8">
      <strong>📨 Workbook successfully submitted.</strong>
      <p style="margin:7px 0 0">Wait for your teacher to review your work. Your seven-part Student Writing Learning Page will appear here after your teacher completes the review.</p>
    </div>
  `;

  $("teacherText").innerHTML = `
    <div style="padding:14px;background:#f8fafc;border-radius:9px;line-height:1.8">
      Your teacher will personally explain what needs attention and why.
    </div>
  `;

  $("corrected").textContent = "Waiting for teacher review.";
  $("modelSentence").textContent = "Your teacher will provide a strong topic sentence example after reviewing your work.";
  $("modelBreakdown").innerHTML = `
    <div class="breakdown"><strong>Topic</strong><br><br>Teacher review pending</div>
    <div class="breakdown"><strong>Main Idea</strong><br><br>Teacher review pending</div>
    <div class="breakdown"><strong>Academic Vocabulary</strong><br><br>Teacher review pending</div>
  `;
  $("nextStep").innerHTML = `<p style="line-height:1.75">🎯 Wait for your teacher's review. Your next writing goal will be provided personally.</p>`;
  $("feedback").classList.add("show");
}
'''
s = s[:start] + pending + s[end:]

# Replace submission history viewer.
start = s.index('function openSubmission(record){')
end = s.index('\n\nfunction closeSubmission(){', start)
new_open = '''function openSubmission(record){

  const topicLabel =
    record.topic === "health" ? "❤️ Health" :
    record.topic === "nature" ? "🌿 Nature" :
    "💻 Science & Technology";

  const exercise =
    exercises[record.topic] &&
    exercises[record.topic][Number(record.exercise_number) - 1];

  const reviewed = record.review_status === "reviewed";

  const modelSentence =
    record.teacher_model_sentence ||
    (exercise && exercise.model) ||
    "Your teacher will provide a strong topic sentence example.";

  const modelTopic =
    record.teacher_model_topic ||
    (exercise && exercise.topicPart) ||
    "Teacher review pending";

  const modelMainIdea =
    record.teacher_model_main_idea ||
    (exercise && exercise.mainIdea) ||
    "Teacher review pending";

  const modelVocab =
    record.teacher_model_vocabulary ||
    (exercise && exercise.vocab) ||
    "Teacher review pending";

  $("submissionModalTitle").textContent =
    "📖 Student Writing Learning Page";

  if(!reviewed){
    $("submissionModalBody").innerHTML = `
      <div class="learning-subtitle">
        ${topicLabel} — Exercise ${escapeHTML(String(record.exercise_number))}
        &nbsp;•&nbsp; Attempt ${escapeHTML(String(record.attempt_number || ""))}
        &nbsp;•&nbsp; ${formatDate(record.completed_at)}
      </div>
      <div class="learning-section">
        <h3>📨 Workbook Successfully Submitted</h3>
        <p>Your work has been submitted successfully.</p>
        <p><strong>Wait for your teacher to review your work.</strong></p>
        <p>Your seven-part Student Writing Learning Page will appear after your teacher completes the review.</p>
      </div>
      <div class="learning-section">
        <h3>1️⃣ Original Sentence</h3>
        <div class="annotated-sentence">${escapeHTML(record.original_sentence || "")}</div>
      </div>
    `;
  }
  else{
    $("submissionModalBody").innerHTML = `
      <div class="learning-subtitle">
        ${topicLabel} — Exercise ${escapeHTML(String(record.exercise_number))}
        &nbsp;•&nbsp; Attempt ${escapeHTML(String(record.attempt_number || ""))}
        &nbsp;•&nbsp; ${formatDate(record.completed_at)}
        &nbsp;•&nbsp; Score ${escapeHTML(String(record.score ?? ""))}/10
      </div>
      <div class="learning-section">
        <h3>1️⃣ Original Sentence</h3>
        <div class="annotated-sentence">${record.annotated_sentence || escapeHTML(record.original_sentence || "")}</div>
      </div>
      <div class="learning-section">
        <h3>2️⃣ What Needs Attention?</h3>
        <div class="submission-modal-text">${escapeHTML(record.what_needs_attention || "Your teacher has not added this section yet.")}</div>
      </div>
      <div class="learning-section">
        <h3>3️⃣ Learn Why</h3>
        <div class="submission-modal-text">${escapeHTML(record.learn_why || record.teacher_feedback || "Your teacher has not added this section yet.")}</div>
      </div>
      <div class="learning-section">
        <h3>4️⃣ Correct Sentence</h3>
        <div class="corrected">${escapeHTML(record.corrected_sentence || "Your teacher has not added the corrected sentence yet.")}</div>
      </div>
      <div class="learning-section">
        <h3>5️⃣ Academic Words to Learn</h3>
        <div class="submission-modal-text">${escapeHTML(record.academic_words || "Your teacher has not added the academic vocabulary lesson yet.")}</div>
      </div>
      <div class="learning-section">
        <h3>6️⃣ ⭐ Learn From a Strong Topic Sentence</h3>
        <div class="model">${escapeHTML(modelSentence)}</div>
        <div class="model-breakdown">
          <div class="breakdown"><strong>Topic</strong><br><br>${escapeHTML(modelTopic)}</div>
          <div class="breakdown"><strong>Main Idea</strong><br><br>${escapeHTML(modelMainIdea)}</div>
          <div class="breakdown"><strong>Academic Vocabulary</strong><br><br>${escapeHTML(modelVocab)}</div>
        </div>
      </div>
      <div class="learning-section">
        <h3>7️⃣ 🎯 Your Next Step</h3>
        <div class="submission-modal-text">${escapeHTML(record.teacher_next_step || "Your teacher has not added the next-step goal yet.")}</div>
      </div>
    `;
  }

  $("submissionModal").classList.add("show");
  $("submissionModal").setAttribute("aria-hidden","false");
  document.body.style.overflow = "hidden";
}
'''
s = s[:start] + new_open + s[end:]

# Replace the Analyze handler with a submission handler.
start = s.index('/* =========================================================\n   ANALYZE BUTTON\n========================================================= */')
end = s.index('\n\n/* =========================================================\n   TOPIC BUTTONS', start)
handler = '''/* =========================================================\n   SUBMIT BUTTON\n========================================================= */\n\n$("check").addEventListener(\n  "click",\n  async () => {\n\n    const text =\n      $("answer").value.trim();\n\n    if(!text){\n      alert("Write one topic sentence before submitting.");\n      return;\n    }\n\n    $("check").disabled = true;\n    $("analyzing").classList.add("show");\n    $("feedback").classList.remove("show");\n    $("saveStatus").textContent = "";\n\n    try {\n      const attempts = records.filter(r =>\n        r.topic === topic &&\n        r.exercise_number === exerciseIndex + 1\n      ).length;\n\n      const saved = await saveSubmission(text, attempts + 1);\n      if(!saved) return;\n\n      showPendingSubmission();\n      await loadRecords();\n      $("next").disabled = false;\n      $("feedback").scrollIntoView({behavior:"smooth"});\n\n    }\n    catch(error){\n      console.error("Submission failed:", error);\n      $("saveStatus").textContent =\n        "⚠️ Your work could not be submitted. Please try again.";\n      $("saveStatus").className =\n        "save-status save-error";\n    }\n    finally{\n      $("check").disabled = false;\n      $("analyzing").classList.remove("show");\n    }\n  }\n);\n'''
s = s[:start] + handler + s[end:]

# Replace history rendering.
start = s.index('function renderRecords(){')
end = s.index('\n\nfunction openSubmission(record){', start)
render = '''function renderRecords(){

  $("completedCount").textContent =
    records.length + " submissions";

  if(!records.length){
    $("completedWork").innerHTML = `<div class="empty">No submitted work yet.</div>`;
    return;
  }

  $("completedWork").innerHTML = `
    <div class="history-list">
      ${records.map((record,index) => {
        const topicLabel =
          record.topic === "health" ? "❤️ Health" :
          record.topic === "nature" ? "🌿 Nature" :
          "💻 Science & Technology";
        const reviewed = record.review_status === "reviewed";
        const status = reviewed
          ? `✓ Teacher reviewed${record.score != null ? ` — ${record.score}/10` : ""}`
          : "⏳ Waiting for teacher review";
        return `
          <div class="history-item ${index === 0 ? "latest" : ""}">
            <div class="history-info">
              <div class="history-title">
                ${index === 0 ? "⭐ Latest Submission — " : ""}
                ${topicLabel} — Exercise ${record.exercise_number}
              </div>
              <div class="history-meta">
                ${formatDate(record.completed_at)}
                &nbsp;•&nbsp; Attempt ${record.attempt_number || ""}
                &nbsp;•&nbsp; ${status}
              </div>
              <div class="history-preview">${escapeHTML(record.original_sentence || "")}</div>
            </div>
            <button type="button" class="history-view" data-submission-index="${index}">
              ${reviewed ? "View Learning Page →" : "View Submission →"}
            </button>
          </div>
        `;
      }).join("")}
    </div>
    <div style="margin-top:12px;color:#64748b;font-size:13px">
      Your teacher will add the seven-part learning page after reviewing your work.
    </div>
  `;
}
'''
s = s[:start] + render + s[end:]

# Stats only count reviewed work.
s = s.replace(
'''  $("strong").textContent =
    records.filter(
      r => r.score >= 8
    ).length;''',
'''  $("strong").textContent =
    records.filter(
      r => r.review_status === "reviewed" && r.score >= 8
    ).length;''')

s = s.replace(
'''  $("needs").textContent =
    records.filter(
      r => r.score < 8
    ).length;''',
'''  $("needs").textContent =
    records.filter(
      r => r.review_status === "reviewed" && r.score < 8
    ).length;''')

s = s.replace(
'''  $("best").textContent =
    records.length
      ? Math.max(
          ...records.map(
            r => r.score || 0
          )
        ) + "/10"
      : "—";''',
'''  const reviewedScores = records
    .filter(r => r.review_status === "reviewed" && r.score != null)
    .map(r => Number(r.score));

  $("best").textContent =
    reviewedScores.length
      ? Math.max(...reviewedScores) + "/10"
      : "—";''')

p.write_text(s, encoding='utf-8')
