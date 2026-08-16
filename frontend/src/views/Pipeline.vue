<script setup>
import { onMounted, reactive, ref } from "vue";
import { getPipelineDefaults, runStage, uploadFiles } from "../api";

const CACHE_KEY = "mdp.pipeline.stageCache";

const log = ref("");
const busy = ref(false);
const dragging = ref(false);
const fileInput = ref(null);
const uploadToken = ref(0);
const lastRun = reactive({
  ingest: null,
  infer: null,
  metadata: null,
  qc: null,
  export: null,
});

const backend = ref("mock");
const apiKey = ref("");
const apiKeyEnv = ref("VLM_API_KEY");
const modelName = ref("qwen-vl-plus");

const yamlBlur = ref(100);
const blurThreshold = ref(100);

const yamlExport = ref({
  include_blurry: false,
  exclude_duplicates: true,
  require_caption: true,
});
const includeBlurry = ref(false);
const excludeDuplicates = ref(true);
const requireCaption = ref(true);

function hashText(text) {
  let hash = 0;
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash * 31 + text.charCodeAt(i)) >>> 0;
  }
  return `${text.length}:${hash}`;
}

function keyFingerprint() {
  if (backend.value !== "api") {
    return "none";
  }
  return hashText(apiKey.value.trim());
}

function fingerprints() {
  const ingest = `u:${uploadToken.value}`;
  const infer = `${ingest}|${backend.value}|${keyFingerprint()}`;
  const metadata = infer;
  const qc = `${metadata}|blur:${Number(blurThreshold.value)}`;
  const exp = `${qc}|dup:${excludeDuplicates.value}|blurry:${includeBlurry.value}|cap:${requireCaption.value}`;
  return { ingest, infer, metadata, qc, export: exp };
}

function isCurrent(name) {
  return lastRun[name] === fingerprints()[name];
}

function persistCache() {
  sessionStorage.setItem(
    CACHE_KEY,
    JSON.stringify({
      uploadToken: uploadToken.value,
      lastRun: { ...lastRun },
      backend: backend.value,
      blurThreshold: blurThreshold.value,
      includeBlurry: includeBlurry.value,
      excludeDuplicates: excludeDuplicates.value,
      requireCaption: requireCaption.value,
    }),
  );
}

function restoreCache() {
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    if (!raw) {
      return;
    }
    const data = JSON.parse(raw);
    if (typeof data.uploadToken === "number") {
      uploadToken.value = data.uploadToken;
    }
    if (data.lastRun && typeof data.lastRun === "object") {
      Object.assign(lastRun, data.lastRun);
    }
    if (data.backend === "mock" || data.backend === "api" || data.backend === "local") {
      backend.value = data.backend;
    }
    if (typeof data.blurThreshold === "number") {
      blurThreshold.value = data.blurThreshold;
    }
    if (typeof data.includeBlurry === "boolean") {
      includeBlurry.value = data.includeBlurry;
    }
    if (typeof data.excludeDuplicates === "boolean") {
      excludeDuplicates.value = data.excludeDuplicates;
    }
    if (typeof data.requireCaption === "boolean") {
      requireCaption.value = data.requireCaption;
    }
  } catch {
    // ignore broken session cache
  }
}

onMounted(async () => {
  try {
    const defaults = await getPipelineDefaults();
    apiKeyEnv.value = defaults.inference.api_key_env;
    modelName.value = defaults.inference.model_name;
    yamlBlur.value = defaults.qc.blur_threshold;
    blurThreshold.value = defaults.qc.blur_threshold;
    yamlExport.value = defaults.export;
    includeBlurry.value = defaults.export.include_blurry;
    excludeDuplicates.value = defaults.export.exclude_duplicates;
    requireCaption.value = defaults.export.require_caption;
  } catch (error) {
    log.value = String(error);
  }
  restoreCache();
});

function acceptedFiles(fileList) {
  const files = [];
  for (const file of fileList) {
    const name = file.name.toLowerCase();
    const imageType = file.type.startsWith("image/");
    const zipType =
      file.type === "application/zip" ||
      file.type === "application/x-zip-compressed";
    const zipName = name.endsWith(".zip");
    const imageName = /\.(jpe?g|png|webp|bmp|gif)$/i.test(name);
    if (imageType || zipType || zipName || imageName) {
      files.push(file);
    }
  }
  return files;
}

async function sendFiles(fileList) {
  const files = acceptedFiles(fileList);
  if (!files.length) {
    log.value = "Drop images or a .zip (RAR is not supported).";
    return;
  }
  busy.value = true;
  try {
    const data = await uploadFiles(files);
    uploadToken.value += 1;
    persistCache();
    log.value = JSON.stringify(data, null, 2);
  } catch (error) {
    log.value = String(error);
  } finally {
    busy.value = false;
  }
}

function onChoose(event) {
  sendFiles(event.target.files);
  event.target.value = "";
}

function onDrop(event) {
  event.preventDefault();
  dragging.value = false;
  sendFiles(event.dataTransfer.files);
}

function onDragLeave(event) {
  const related = event.relatedTarget;
  if (related && event.currentTarget.contains(related)) {
    return;
  }
  dragging.value = false;
}

function shouldSkip(name, event) {
  return !event?.altKey && isCurrent(name);
}

async function run(name, body) {
  const fp = fingerprints()[name];
  busy.value = true;
  try {
    const data = await runStage(name, body);
    lastRun[name] = fp;
    persistCache();
    log.value = JSON.stringify(data, null, 2);
  } catch (error) {
    log.value = String(error);
  } finally {
    busy.value = false;
  }
}

function runIngest(event) {
  if (shouldSkip("ingest", event)) {
    log.value = "ingest skipped: already ran with the current files. Alt-click to run anyway.";
    return;
  }
  return run("ingest");
}

function runInfer(event) {
  if (shouldSkip("infer", event)) {
    log.value = "infer skipped: already ran with the current options. Alt-click to run anyway.";
    return;
  }
  const body = { backend: backend.value };
  if (backend.value === "api") {
    const key = apiKey.value.trim();
    if (!key) {
      log.value = "Paste your own VLM API key for this run. It is not saved to YAML.";
      return;
    }
    body.api_key = key;
  }
  return run("infer", body);
}

function runMetadata(event) {
  if (shouldSkip("metadata", event)) {
    log.value = "metadata skipped: already ran with the current options. Alt-click to run anyway.";
    return;
  }
  return run("metadata");
}

function runQc(event) {
  if (shouldSkip("qc", event)) {
    log.value = "qc skipped: already ran with the current options. Alt-click to run anyway.";
    return;
  }
  const threshold = Number(blurThreshold.value);
  if (!Number.isFinite(threshold) || threshold < 0) {
    log.value = "QC blur threshold must be a number >= 0.";
    return;
  }
  return run("qc", { blur_threshold: threshold });
}

function runExport(event) {
  if (shouldSkip("export", event)) {
    log.value = "export skipped: already ran with the current options. Alt-click to run anyway.";
    return;
  }
  return run("export", {
    include_blurry: includeBlurry.value,
    exclude_duplicates: excludeDuplicates.value,
    require_caption: requireCaption.value,
  });
}
</script>

<template>
  <section class="stack">
    <div class="card">
      <h2>Upload into datasets/raw</h2>
      <p class="hint">
        Images or a <code>.zip</code>. Same filename overwrites. RAR is not supported.
      </p>
      <div
        class="drop"
        :class="{ over: dragging, disabled: busy }"
        @dragenter.prevent="dragging = true"
        @dragover.prevent="dragging = true"
        @dragleave="onDragLeave"
        @drop="onDrop"
      >
        <p><strong>Drag and drop files here</strong></p>
        <p class="hint">or</p>
        <input
          ref="fileInput"
          type="file"
          multiple
          accept="image/*,.zip"
          :disabled="busy"
          class="sr-only"
          @change="onChoose"
        />
        <button type="button" :disabled="busy" @click="fileInput.click()">
          Choose files
        </button>
      </div>
    </div>

    <div class="card">
      <h2>2 Infer</h2>
      <label class="field">
        Backend
        <select v-model="backend" :disabled="busy">
          <option value="mock">mock (default, no GPU / no key)</option>
          <option value="api">api (remote, OpenAI-compatible)</option>
          <option value="local">local (GPU weights)</option>
        </select>
      </label>
      <div v-if="backend === 'api'" class="callout">
        <label class="field">
          API key (this run only)
          <input
            v-model="apiKey"
            type="password"
            autocomplete="off"
            placeholder="your API key"
            :disabled="busy"
          />
        </label>
        <p>
          Each run uses the key you paste here. It is sent only with
          <code>POST /api/pipeline/infer</code>, not written to YAML, reports, or logs.
        </p>
        <p>
          YAML <code>model_name</code> is currently <code>{{ modelName }}</code>.
          Use a <strong>vision / multimodal</strong> model such as
          <code>qwen-vl-plus</code>, not a text-only chat model.
        </p>
        <p class="hint">
          CLI can still use <code>{{ apiKeyEnv }}</code> with
          <code>python main.py infer --backend api</code>.
        </p>
      </div>
      <div v-else-if="backend === 'local'" class="callout">
        <p class="hint">
          Local Qwen needs downloaded weights and enough VRAM. A 4 GB card is often too tight.
        </p>
      </div>
    </div>

    <div class="card">
      <h2>4 QC</h2>
      <label class="field">
        Blur threshold (Laplacian variance)
        <input
          v-model.number="blurThreshold"
          type="number"
          min="0"
          step="1"
          :disabled="busy"
        />
      </label>
      <p class="hint">
        YAML default: <code>{{ yamlBlur }}</code>.
        Score below the threshold is marked blurry, so a <strong>higher</strong> value
        marks more images as blurry.
      </p>
    </div>

    <div class="card">
      <h2>5 Export filters</h2>
      <label class="check">
        <input v-model="excludeDuplicates" type="checkbox" :disabled="busy" />
        Exclude duplicates
        <span class="hint">(YAML {{ yamlExport.exclude_duplicates }})</span>
      </label>
      <label class="check">
        <input v-model="includeBlurry" type="checkbox" :disabled="busy" />
        Include blurry images
        <span class="hint">(YAML {{ yamlExport.include_blurry }})</span>
      </label>
      <label class="check">
        <input v-model="requireCaption" type="checkbox" :disabled="busy" />
        Require non-empty caption
        <span class="hint">(YAML {{ yamlExport.require_caption }})</span>
      </label>
    </div>

    <div class="card">
      <h2>Run stages</h2>
      <p class="hint">
        Each button is independent and only overwrites that stage's report.
        Later stages read earlier reports, so 1→5 is the usual path; skipping
        ahead typically returns an error instead of corrupting the project.
        Green means already ran with the current options (click does nothing;
        Alt-click forces a re-run).
      </p>
      <div class="row">
        <button :class="{ done: isCurrent('ingest') }" :disabled="busy" @click="runIngest">
          1 Ingest
        </button>
        <button :class="{ done: isCurrent('infer') }" :disabled="busy" @click="runInfer">
          2 Infer
        </button>
        <button :class="{ done: isCurrent('metadata') }" :disabled="busy" @click="runMetadata">
          3 Metadata
        </button>
        <button :class="{ done: isCurrent('qc') }" :disabled="busy" @click="runQc">
          4 QC
        </button>
        <button :class="{ done: isCurrent('export') }" :disabled="busy" @click="runExport">
          5 Export
        </button>
      </div>
      <p v-if="busy" class="hint">Running…</p>
      <pre>{{ log }}</pre>
    </div>
  </section>
</template>

<style scoped>
.stack {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.drop {
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 28px 16px;
  text-align: center;
  background: #fafbfc;
}

.drop.over {
  border-color: var(--accent);
  background: var(--drop);
}

.drop.disabled {
  opacity: 0.6;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 360px;
  margin: 8px 0;
  font-weight: 600;
  color: var(--text-h);
}

.field select,
.field input {
  font-weight: 400;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
}

.callout {
  background: var(--accent-soft);
  border: 1px solid #bfdbfe;
  border-radius: 10px;
  padding: 12px;
  margin-top: 8px;
}

.check {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
}

.row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 12px 0;
}

button.done {
  background: var(--ok-bg);
  border-color: #86efac;
  color: var(--ok);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}
</style>
