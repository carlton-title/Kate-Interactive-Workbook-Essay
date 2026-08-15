from pathlib import Path
import subprocess

path = Path("index.html")
text = path.read_text(encoding="utf-8")

marker = "submission-history-modal-v1"
if marker in text:
    print("Submission history viewer already installed.")
    raise SystemExit(0)

css = """
/* submission-history-modal-v1 */
.history-list{display:grid;gap:10px;margin-top:15px}
.history-item{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:13px 15px;border:1px solid #cbd8ee;border-radius:12px;background:#fff}
.history-item.latest{border:2px solid #2563eb;background:#eff6ff}
.history-info{min-width:0}
.history-title{color:#1e3a8a;font-weight:bold}
.history-meta{margin-top:4px;color:#64748b;font-size:12px}
.history-preview{margin-top:7px;color:#334155;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.history-view{flex:0 0 auto;padding:9px 13px;border:2px solid #2563eb;border-radius:9px;background:#fff;color:#1d4ed8;font-weight:bold;cursor:pointer}
.history-view:hover{background:#eff6ff}
.submission-modal{display:none;position:fixed;inset:0;z-index:10000;padding:18px;background:rgba(15,23,42,.65);overflow-y:auto}
.submission-modal.show{display:block}
.submission-modal-card{width:min(900px,100%);margin:0 auto;background:#fff;border-radius:18px;box-shadow:0 25px 70px rgba(0,0,0,.3);overflow:hidden}
.submission-modal-header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:17px 20px;color:#fff;background:linear-gradient(135deg,#123a72,#2563eb,#0f766e)}
.submission-modal-header h2{margin:0;font-size:20px}
.submission-modal-close{border:0;background:rgba(255,255,255,.18);color:#fff;width:38px;height:38px;border-radius:50%;font-size:23px;cursor:pointer}
.submission-modal-body{padding:20px}
.submission-modal-score{display:inline-block;margin-bottom:14px;padding:7px 11px;border-radius:20px;background:#ecfdf5;color:#15803d;font-weight:bold}
.submission-modal-section{margin-top:15px;padding:15px;border-radius:11px;border-left:5px solid #2563eb;background:#f8fafc}
.submission-modal-section h3{margin:0 0 9px;color:#1e3a8a;font-size:17px}
.submission-modal-text{line-height:1.75;white-space:pre-wrap}
@media(max-width:650px){.history-item{align-items:stretch;flex-direction:column}.history-view{width:100%}.submission-modal{padding:8px}.submission-modal-body{padding:14px}}
"""
text = text.replace("</style>", css + "\n</style>", 1)

modal_html = """
<!-- submission-history-modal-v1 -->
<div id="submissionModal" class="submission-modal" aria-hidden="true">
  <div class="submission-modal-card" role="dialog" aria-modal="true" aria-labelledby="submissionModalTitle">
    <div class="submission-modal-header">
      <h2 id="submissionModalTitle">Submission</h2>
      <button id="submissionModalClose" class="submission-modal-close" type="button" aria-label="Close">×</button>
    </div>
    <div id="submissionModalBody" class="submission-modal-body"></div>
  </div>
</div>
"""
text = text.replace("</main>", modal_html + "\n</main>", 1)

start = text.index("function renderRecords(){")
end = text.index("\n\n\n/* =========================================================\n   ANALYZE BUTTON", start)

new_render = r'''function renderRecords(){

  $("completedCount").textContent =
    records.length + " submissions";

  if(!records.length){

    $("completedWork").innerHTML = `
      <div class="empty">
        No completed work yet.
      </div>
    `;

    return;

  }

  /* Keep the main page compact. Each submission opens separately. */
  $("completedWork").innerHTML = `
    <div class="history-list">
      ${records.map((record,index) => {

        const topicLabel =
          record.topic === "health"
            ? "❤️ Health"
            : record.topic === "nature"
              ? "🌿 Nature"
              : "💻 Science & Technology";

        const preview = escapeHTML(
          record.original_sentence || ""
        );

        return `
          <div class="history-item ${index === 0 ? "latest" : ""}">
            <div class="history-info">
              <div class="history-title">
                ${index === 0 ? "⭐ Latest Submission — " : ""}
                ${topicLabel} — Exercise ${record.exercise_number}
              </div>
              <div class="history-meta">
                ${formatDate(record.completed_at)}
                &nbsp;•&nbsp; Attempt ${record.attempt_number}
                &nbsp;•&nbsp; Score ${record.score}/10
              </div>
              <div class="history-preview">${preview}</div>
            </div>
            <button type="button" class="history-view" data-submission-index="${index}">
              View Submission →
            </button>
          </div>
        `;

      }).join("")}
    </div>
    <div style="margin-top:12px;color:#64748b;font-size:13px">
      Select a submission to open its full feedback without adding the entire history to this page.
    </div>
  `;

}

function openSubmission(record){

  const topicLabel =
    record.topic === "health"
      ? "❤️ Health"
      : record.topic === "nature"
        ? "🌿 Nature"
        : "💻 Science & Technology";

  $("submissionModalTitle").textContent =
    topicLabel + " — Exercise " + record.exercise_number;

  $("submissionModalBody").innerHTML = `
    <div class="submission-modal-score">
      Score: ${escapeHTML(String(record.score))}/10
    </div>

    <div class="meta">
      <span>${formatDate(record.completed_at)}</span>
      <span>Attempt ${escapeHTML(String(record.attempt_number))}</span>
      <span>${escapeHTML(record.strategy || "")}</span>
    </div>

    <div class="submission-modal-section">
      <h3>1. Annotated Student Work</h3>
      <div class="submission-modal-text">
        ${record.annotated_sentence || escapeHTML(record.original_sentence || "")}
      </div>
    </div>

    <div class="submission-modal-section">
      <h3>2. Corrected Version</h3>
      <div class="submission-modal-text">
        ${escapeHTML(record.corrected_sentence || "")}
      </div>
    </div>

    <div class="submission-modal-section">
      <h3>3. Learning Feedback</h3>
      <div class="submission-modal-text">
        ${record.teacher_feedback || ""}
      </div>
    </div>
  `;

  $("submissionModal").classList.add("show");
  $("submissionModal").setAttribute("aria-hidden","false");
  document.body.style.overflow = "hidden";

}

function closeSubmission(){

  $("submissionModal").classList.remove("show");
  $("submissionModal").setAttribute("aria-hidden","true");
  document.body.style.overflow = "";

}

document.addEventListener("click", event => {

  const button = event.target.closest(".history-view");

  if(button){
    const index = Number(button.dataset.submissionIndex);
    if(records[index]) openSubmission(records[index]);
    return;
  }

  if(
    event.target.id === "submissionModalClose" ||
    event.target.id === "submissionModal"
  ){
    closeSubmission();
  }

});

document.addEventListener("keydown", event => {
  if(event.key === "Escape") closeSubmission();
});
'''

text = text[:start] + new_render + text[end:]
path.write_text(text, encoding="utf-8")

subprocess.run(["git","config","user.name","github-actions[bot]"],check=True)
subprocess.run(["git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com"],check=True)
subprocess.run(["git","add","index.html"],check=True)
subprocess.run(["git","commit","-m","Make submission history individually viewable"],check=True)
subprocess.run(["git","push"],check=True)
