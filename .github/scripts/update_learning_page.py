from pathlib import Path
import re

p = Path("index.html")
s = p.read_text(encoding="utf-8")

s = s.replace("1️⃣ Your Original Sentence", "1️⃣ Original Sentence")
s = s.replace("4️⃣ Correct Your Sentence", "4️⃣ Correct Sentence")

show_start = s.index("function showLearningPage(")
show_end = s.index("\n\n/* =========================================================\n   SAVE TO SUPABASE", show_start)

new_show = r'''function showLearningPage(
  text,
  result
){

  const exercise = exercises[topic][exerciseIndex];
  const issues = Array.isArray(result.issues) ? result.issues : [];
  const score = Number(result.score) || 0;

  $("annotated").innerHTML = annotate(text,result);

  /* 2. WHAT NEEDS ATTENTION */
  if(!issues.length){
    $("feedbackItems").innerHTML = score >= 8
      ? `
        <div style="padding:12px;background:#ecfdf5;border-left:4px solid #15803d;border-radius:8px;line-height:1.7">
          <strong>🌟 No specific workbook error was detected.</strong>
          <p style="margin:7px 0 0">The AI considers this sentence strong enough to continue developing. Read the feedback below and look for one way to make the idea even more precise.</p>
        </div>
      `
      : `
        <div style="padding:12px;background:#fff7ed;border-left:4px solid #ea580c;border-radius:8px;line-height:1.7">
          <strong>🔎 The sentence still needs attention.</strong>
          <p style="margin:7px 0 0">The rule checker did not identify a specific grammar, spelling, punctuation, or vocabulary error. <strong>This does not mean the sentence is correct.</strong> Use the AI feedback below to improve clarity, task connection, sentence structure, and vocabulary.</p>
        </div>
      `;
  }
  else{
    $("feedbackItems").innerHTML = issues.map((issue,index) => {
      const label = issue.category || issue.type || "Sentence Structure";
      const original = issue.original || issue.word || "the marked part";
      const correction = issue.correction || "See the corrected sentence below.";
      const explanation = issue.explanation || issue.message || "This part needs revision.";
      return `
        <div class="feedback-item" style="margin-top:10px;padding:14px;background:white;border:1px solid #dbe4f2;border-left:5px solid ${issue.type === "word" ? "#2563eb" : "#dc2626"};border-radius:9px">
          <strong>${index + 1}. ${escapeHTML(label)}</strong>
          <div style="margin-top:9px;line-height:1.7"><strong>Problem:</strong> ${escapeHTML(original)}</div>
          <div style="margin-top:7px;line-height:1.7"><strong>What to change:</strong> ${escapeHTML(correction)}</div>
          <div style="margin-top:7px;line-height:1.7"><strong>Coach's advice:</strong> ${escapeHTML(explanation)}</div>
        </div>
      `;
    }).join("") + `
      <div style="margin-top:12px;padding:11px;background:#eff6ff;border-radius:8px;line-height:1.7">
        <strong>🎯 Coaching goal:</strong> Correct these specific problems first. Then compare the corrected sentence with the original before writing your next sentence.
      </div>
    `;
  }

  /* 3. LEARN WHY */
  let explanation = "";

  if(result.overall_feedback){
    explanation += `
      <div style="padding:12px;background:#eff6ff;border-left:4px solid #2563eb;border-radius:8px;line-height:1.75">
        <strong>Overall feedback</strong>
        <div style="margin-top:6px">${escapeHTML(result.overall_feedback)}</div>
      </div>
    `;
  }

  if(issues.length){
    explanation += `
      <div style="margin-top:12px;overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;background:white">
          <thead><tr>
            <th style="padding:10px;border-bottom:2px solid #cbd8ee;text-align:left;color:#991b1b">Incorrect</th>
            <th style="padding:10px;border-bottom:2px solid #cbd8ee;text-align:left;color:#166534">Correct</th>
            <th style="padding:10px;border-bottom:2px solid #cbd8ee;text-align:left;color:#1e3a8a">Why?</th>
          </tr></thead>
          <tbody>
            ${issues.map(issue => `
              <tr>
                <td style="padding:10px;border-bottom:1px solid #e2e8f0;vertical-align:top;color:#b91c1c;font-weight:bold">${escapeHTML(issue.original || issue.word || "")}</td>
                <td style="padding:10px;border-bottom:1px solid #e2e8f0;vertical-align:top;color:#15803d;font-weight:bold">${escapeHTML(issue.correction || "See corrected sentence")}</td>
                <td style="padding:10px;border-bottom:1px solid #e2e8f0;vertical-align:top;line-height:1.7">${escapeHTML(issue.explanation || issue.message || "")}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }
  else{
    explanation += `
      <div style="margin-top:10px;padding:12px;background:#f8fafc;border-radius:8px;line-height:1.75">
        <strong>Why this matters:</strong> No specific rule-based error was identified, so use the overall AI feedback to check clarity, sentence structure, task connection, and precise vocabulary.
      </div>
    `;
  }

  $("teacherText").innerHTML = explanation;

  /* 4. CORRECT SENTENCE */
  $("corrected").textContent = result.corrected_sentence || text;

  /* 6. STRONG MODEL */
  $("modelSentence").textContent = exercise.model;
  $("modelBreakdown").innerHTML = `
    <div class="breakdown"><strong>Topic</strong><br><br>${escapeHTML(exercise.topicPart)}</div>
    <div class="breakdown"><strong>Main Idea</strong><br><br>${escapeHTML(exercise.mainIdea)}</div>
    <div class="breakdown"><strong>Academic Vocabulary</strong><br><br>${escapeHTML(exercise.vocab)}</div>
  `;

  /* 7. NEXT STEP */
  if(result.next_step){
    $("nextStep").innerHTML = `<p style="line-height:1.75"><strong>🎯 Goal for your next sentence:</strong> ${escapeHTML(result.next_step)}</p>`;
  }
  else if(score >= 8){
    $("nextStep").innerHTML = `<p style="line-height:1.75">🌟 Keep the same clear structure, but make the main idea more specific and use precise academic vocabulary.</p>`;
  }
  else{
    $("nextStep").innerHTML = `<p style="line-height:1.75">✏️ Rewrite the sentence by correcting the problems above, then write one clear topic sentence that directly answers the task.</p>`;
  }

  $("feedback").classList.add("show");

}
'''
s = s[:show_start] + new_show + s[show_end:]

issue_start = s.index('  const issues =\n    (data.issues || [])')
issue_end = s.index('\n\n\n  return {', issue_start)

new_issue = r'''  const issues =
    (data.issues || [])
      .map(issue => {

        const category = (issue.category || "").toLowerCase();
        let type = "grammar";

        if(category.includes("spelling")) type = "spelling";
        else if(category.includes("capital")) type = "capitalization";
        else if(category.includes("punctuation")) type = "punctuation";
        else if(category.includes("vocabulary") || category.includes("word")) type = "word";
        else if(category.includes("agreement")) type = "agreement";

        return {
          type,
          category: issue.category || "Sentence Structure",
          original: issue.original || "",
          correction: issue.correction || "",
          explanation: issue.explanation || "",
          word: issue.original || "",
          message: issue.explanation || ""
        };
      });'''
s = s[:issue_start] + new_issue + s[issue_end:]

# Save detailed coaching information for future historical submissions.
gf_start = s.index('function generateRecordFeedback(')
gf_end = s.index('\n\n/* =========================================================\n   LOAD RECORDS', gf_start)

new_gf = r'''function generateRecordFeedback(
  text,
  result,
  exercise
){

  const parts = [];

  if(result.overall_feedback){
    parts.push("Overall feedback: " + result.overall_feedback);
  }

  if(result.issues && result.issues.length){
    parts.push("What Needs Attention:");
    result.issues.forEach((issue,index) => {
      parts.push(
        `${index + 1}. ${issue.category || issue.type || "Sentence Structure"}` +
        ` | Incorrect: ${issue.original || issue.word || ""}` +
        ` | Correct: ${issue.correction || "See corrected sentence"}` +
        ` | Why: ${issue.explanation || "Review the corrected sentence and explanation."}`
      );
    });
  }
  else{
    parts.push("What Needs Attention: No specific workbook rule error was detected. Use the overall AI feedback to check clarity, task connection, sentence structure, and vocabulary.");
  }

  if(result.next_step){
    parts.push("Next Step: " + result.next_step);
  }

  parts.push("Strong model: " + exercise.model);
  return parts.join("\\n\\n");

}
'''
s = s[:gf_start] + new_gf + s[gf_end:]

# Historical submission viewer: same seven-part structure, with saved coaching feedback.
os_start = s.index('function openSubmission(record){')
os_end = s.index('\n\nfunction closeSubmission(){', os_start)

new_open = r'''function openSubmission(record){

  const topicLabel =
    record.topic === "health" ? "❤️ Health" :
    record.topic === "nature" ? "🌿 Nature" :
    "💻 Science & Technology";

  const exercise = exercises[record.topic] && exercises[record.topic][Number(record.exercise_number) - 1];
  const modelSentence = exercise && exercise.model ? exercise.model : "Study the strong topic sentence example from this exercise.";
  const modelTopic = exercise && exercise.topicPart ? exercise.topicPart : "Identify the main topic clearly.";
  const modelMainIdea = exercise && exercise.mainIdea ? exercise.mainIdea : "State one clear main idea.";
  const modelVocab = exercise && exercise.vocab ? exercise.vocab : "Use precise academic vocabulary.";
  const score = Number(record.score) || 0;

  const attention = score >= 8
    ? `<div style="padding:12px;background:#ecfdf5;border-left:4px solid #15803d;border-radius:8px;line-height:1.7"><strong>🌟 No specific workbook error was recorded for this submission.</strong><p style="margin:7px 0 0">Read the Learn Why feedback and use the Next Step goal to keep improving.</p></div>`
    : `<div style="padding:12px;background:#fff7ed;border-left:4px solid #ea580c;border-radius:8px;line-height:1.7"><strong>🔎 This submission needs revision.</strong><p style="margin:7px 0 0">Compare the original sentence, saved feedback, and corrected sentence carefully.</p></div>`;

  const nextStep = score >= 8
    ? `<p style="line-height:1.75">🌟 Keep the same clear structure, but make the main idea more specific and use precise academic vocabulary.</p>`
    : `<p style="line-height:1.75">✏️ Correct the problems identified in the saved feedback, then write one clear topic sentence that directly answers the task.</p>`;

  $("submissionModalTitle").textContent = "📖 Student Writing Learning Page";

  $("submissionModalBody").innerHTML = `
    <div class="learning-subtitle">
      ${topicLabel} — Exercise ${escapeHTML(String(record.exercise_number))}
      &nbsp;•&nbsp; Attempt ${escapeHTML(String(record.attempt_number))}
      &nbsp;•&nbsp; ${formatDate(record.completed_at)}
      &nbsp;•&nbsp; Score ${escapeHTML(String(record.score))}/10
    </div>

    <div class="learning-section">
      <h3>1️⃣ Original Sentence</h3>
      <div class="annotated-sentence">${record.annotated_sentence || escapeHTML(record.original_sentence || "")}</div>
      <div class="key"><span>🔴 Red = spelling / grammar / punctuation</span><span>🔵 Blue = weak word choice</span><span>⭕ Circle = capitalization</span><span>▢ Box = grammar</span></div>
    </div>

    <div class="learning-section"><h3>2️⃣ What Needs Attention?</h3>${attention}</div>

    <div class="learning-section">
      <h3>3️⃣ Learn Why</h3>
      <div class="submission-modal-text">${escapeHTML(record.teacher_feedback || "No saved learning feedback is available for this submission.")}</div>
    </div>

    <div class="learning-section">
      <h3>4️⃣ Correct Sentence</h3>
      <div class="corrected">${escapeHTML(record.corrected_sentence || record.original_sentence || "")}</div>
    </div>

    <div class="learning-section">
      <h3>5️⃣ Academic Words to Learn</h3>
      <p>These are stronger words you can use instead of general everyday vocabulary.</p>
      <table class="vocab-table"><thead><tr><th>Everyday Word</th><th>Academic Choices</th><th>Use These When...</th></tr></thead><tbody>
        <tr><td class="old-word">good</td><td class="new-word">beneficial / advantageous</td><td>describing a positive effect</td></tr>
        <tr><td class="old-word">bad</td><td class="new-word">harmful / detrimental</td><td>describing a negative effect</td></tr>
        <tr><td class="old-word">big</td><td class="new-word">significant / considerable</td><td>describing importance or size</td></tr>
        <tr><td class="old-word">important</td><td class="new-word">essential / significant / crucial</td><td>describing something necessary</td></tr>
        <tr><td class="old-word">help</td><td class="new-word">assist / support / facilitate</td><td>describing assistance or improvement</td></tr>
        <tr><td class="old-word">get</td><td class="new-word">obtain / receive / acquire</td><td>describing receiving or gaining something</td></tr>
        <tr><td class="old-word">show</td><td class="new-word">demonstrate / illustrate</td><td>presenting evidence or an example</td></tr>
        <tr><td class="old-word">make</td><td class="new-word">create / produce / develop</td><td>describing the creation or development</td></tr>
      </tbody></table>
    </div>

    <div class="learning-section">
      <h3>6️⃣ ⭐ Learn From a Strong Topic Sentence</h3>
      <p>Study this example carefully. Notice how it introduces the topic, states a clear main idea, and uses academic vocabulary.</p>
      <div class="model">${escapeHTML(modelSentence)}</div>
      <div class="model-breakdown">
        <div class="breakdown"><strong>Topic</strong><br><br>${escapeHTML(modelTopic)}</div>
        <div class="breakdown"><strong>Main Idea</strong><br><br>${escapeHTML(modelMainIdea)}</div>
        <div class="breakdown"><strong>Academic Vocabulary</strong><br><br>${escapeHTML(modelVocab)}</div>
      </div>
    </div>

    <div class="learning-section"><h3>7️⃣ 🎯 Your Next Step</h3>${nextStep}</div>
  `;

  $("submissionModal").classList.add("show");
  $("submissionModal").setAttribute("aria-hidden","false");
  document.body.style.overflow = "hidden";

}
'''
s = s[:os_start] + new_open + s[os_end:]

p.write_text(s, encoding="utf-8")
print("Student Writing Learning Page updated.")
