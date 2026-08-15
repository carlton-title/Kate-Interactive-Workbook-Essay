from pathlib import Path
import subprocess
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'submission-history-learning-page-v2'
if marker in text:
    print('Historical learning page already installed.')
    raise SystemExit(0)

old_start = text.index('function openSubmission(record){')
old_end = text.index('\nfunction closeSubmission(){', old_start)

new_function = r'''function openSubmission(record){

  /* submission-history-learning-page-v2 */
  const topicLabel =
    record.topic === "health"
      ? "❤️ Health"
      : record.topic === "nature"
        ? "🌿 Nature"
        : "💻 Science & Technology";

  const exercise =
    exercises[record.topic] &&
    exercises[record.topic][Number(record.exercise_number) - 1];

  const modelSentence =
    exercise && exercise.model
      ? exercise.model
      : "Study the strong topic sentence example from this exercise.";

  const modelTopic =
    exercise && exercise.topicPart
      ? exercise.topicPart
      : "Identify the main topic clearly.";

  const modelMainIdea =
    exercise && exercise.mainIdea
      ? exercise.mainIdea
      : "State one clear main idea.";

  const modelVocab =
    exercise && exercise.vocab
      ? exercise.vocab
      : "Use precise academic vocabulary.";

  const score = Number(record.score) || 0;

  const attention = score >= 8
    ? `
      <div class="learning-section" style="margin-top:0;background:#ecfdf5;border-left-color:#15803d">
        <p style="margin:0;line-height:1.7">
          🌟 <strong>Excellent!</strong> This submission did not receive a low score.
          Study the marked sentence and the learning feedback below, then look for one way to make your next sentence even more precise.
        </p>
      </div>
    `
    : `
      <div class="learning-section" style="margin-top:0">
        <p style="margin:0;line-height:1.7">
          🔎 Review the marked words in your original sentence. Read the learning feedback carefully and compare your original sentence with the corrected version before trying again.
        </p>
      </div>
    `;

  const nextStep = score >= 8
    ? `
      <p>🌟 Your sentence is developing well. For your next attempt, make the main idea even more specific and use precise academic vocabulary.</p>
    `
    : `
      <p>✏️ Rewrite your sentence. First correct the marked errors. Then compare your revision with the strong model below.</p>
      <p>⭐ Pay attention to how the model introduces the topic and clearly states the main idea.</p>
    `;

  $("submissionModalTitle").textContent =
    "📖 Student Writing Learning Page";

  $("submissionModalBody").innerHTML = `

    <div class="learning-subtitle">
      ${topicLabel} — Exercise ${escapeHTML(String(record.exercise_number))}
      &nbsp;•&nbsp; Attempt ${escapeHTML(String(record.attempt_number))}
      &nbsp;•&nbsp; ${formatDate(record.completed_at)}
      &nbsp;•&nbsp; Score ${escapeHTML(String(record.score))}/10
    </div>

    <!-- 1. ORIGINAL -->
    <div class="learning-section">
      <h3>1️⃣ Your Original Sentence</h3>
      <div class="annotated-sentence">
        ${record.annotated_sentence || escapeHTML(record.original_sentence || "")}
      </div>
      <div class="key">
        <span>🔴 Red = spelling / grammar / punctuation</span>
        <span>🔵 Blue = weak word choice</span>
        <span>⭕ Circle = capitalization</span>
        <span>▢ Box = grammar</span>
      </div>
    </div>

    <!-- 2. ATTENTION -->
    <div class="learning-section">
      <h3>2️⃣ What Needs Attention?</h3>
      ${attention}
    </div>

    <!-- 3. LEARN WHY -->
    <div class="learning-section">
      <h3>3️⃣ Learn Why</h3>
      <div class="submission-modal-text">
        ${record.teacher_feedback || "Read the marked sentence and compare it carefully with the corrected version below."}
      </div>
    </div>

    <!-- 4. CORRECTION -->
    <div class="learning-section">
      <h3>4️⃣ Correct Your Sentence</h3>
      <div class="corrected">
        ${escapeHTML(record.corrected_sentence || record.original_sentence || "")}
      </div>
    </div>

    <!-- 5. ACADEMIC VOCABULARY -->
    <div class="learning-section">
      <h3>5️⃣ Academic Words to Learn</h3>
      <p>These are stronger words you can use instead of general everyday vocabulary.</p>
      <table class="vocab-table">
        <thead>
          <tr>
            <th>Everyday Word</th>
            <th>Academic Choices</th>
            <th>Use These When...</th>
          </tr>
        </thead>
        <tbody>
          <tr><td class="old-word">good</td><td class="new-word">beneficial / advantageous</td><td>describing a positive effect</td></tr>
          <tr><td class="old-word">bad</td><td class="new-word">harmful / detrimental</td><td>describing a negative effect</td></tr>
          <tr><td class="old-word">big</td><td class="new-word">significant / considerable</td><td>describing importance or size</td></tr>
          <tr><td class="old-word">important</td><td class="new-word">essential / significant / crucial</td><td>describing something necessary</td></tr>
          <tr><td class="old-word">help</td><td class="new-word">assist / support / facilitate</td><td>describing assistance or improvement</td></tr>
          <tr><td class="old-word">get</td><td class="new-word">obtain / receive / acquire</td><td>describing receiving or gaining something</td></tr>
          <tr><td class="old-word">show</td><td class="new-word">demonstrate / illustrate</td><td>presenting evidence or an example</td></tr>
          <tr><td class="old-word">make</td><td class="new-word">create / produce / develop</td><td>describing the creation or development</td></tr>
        </tbody>
      </table>
    </div>

    <!-- 6. MODEL -->
    <div class="learning-section">
      <h3>6️⃣ ⭐ Learn From a Strong Topic Sentence</h3>
      <p>Study this example carefully. Do not simply copy it. Notice how it introduces the topic and gives the paragraph a clear direction.</p>
      <div class="model">${escapeHTML(modelSentence)}</div>
      <div class="model-breakdown">
        <div class="breakdown"><strong>Topic</strong><br><br>${escapeHTML(modelTopic)}</div>
        <div class="breakdown"><strong>Main Idea</strong><br><br>${escapeHTML(modelMainIdea)}</div>
        <div class="breakdown"><strong>Academic Vocabulary</strong><br><br>${escapeHTML(modelVocab)}</div>
      </div>
    </div>

    <!-- 7. NEXT STEP -->
    <div class="learning-section">
      <h3>7️⃣ 🎯 Your Next Step</h3>
      ${nextStep}
    </div>

  `;

  $("submissionModal").classList.add("show");
  $("submissionModal").setAttribute("aria-hidden","false");
  document.body.style.overflow = "hidden";

}
'''

text = text[:old_start] + new_function + text[old_end:]
path.write_text(text, encoding='utf-8')

subprocess.run(['git','config','user.name','github-actions[bot]'], check=True)
subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'], check=True)
subprocess.run(['git','add','index.html'], check=True)
subprocess.run(['git','commit','-m','Show full student learning page for historical submissions'], check=True)
subprocess.run(['git','push'], check=True)
