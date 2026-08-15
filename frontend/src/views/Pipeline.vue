<script setup>
import { ref } from "vue";
import { runStage, uploadFiles } from "../api";

const log = ref("");
const busy = ref(false);
const backend = ref("mock");
const fileInput = ref(null);

async function upload(event) {
  const files = event.target.files;
  if (!files || !files.length) return;
  busy.value = true;
  try {
    const data = await uploadFiles(files);
    log.value = JSON.stringify(data, null, 2);
  } catch (e) {
    log.value = String(e);
  } finally {
    busy.value = false;
  }
}

async function run(name, body) {
  busy.value = true;
  try {
    const data = await runStage(name, body);
    log.value = JSON.stringify(data, null, 2);
  } catch (e) {
    log.value = String(e);
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section>
    <h2>Run pipeline</h2>
    <p>
      Upload images or .zip into datasets/raw, then run stages in order.
    </p>
    <input
      ref="fileInput"
      type="file"
      multiple
      accept="image/*,.zip"
      :disabled="busy"
      class="sr-only"
      @change="upload"
    />
    <button type="button" :disabled="busy" @click="fileInput.click()">
      Choose files
    </button>
    <p>
      Infer backend:
      <select v-model="backend" :disabled="busy">
        <option value="mock">mock</option>
        <option value="api">api</option>
        <option value="local">local</option>
      </select>
    </p>
    <div class="row">
      <button :disabled="busy" @click="run('ingest')">1 Ingest</button>
      <button :disabled="busy" @click="run('infer', { backend })">2 Infer</button>
      <button :disabled="busy" @click="run('metadata')">3 Metadata</button>
      <button :disabled="busy" @click="run('qc')">4 QC</button>
      <button :disabled="busy" @click="run('export')">5 Export</button>
    </div>
    <p v-if="busy">Running...</p>
    <pre>{{ log }}</pre>
  </section>
</template>

<style scoped>
.row { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
pre { background: #f6f6f6; padding: 8px; min-height: 80px; overflow: auto; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); }
</style>