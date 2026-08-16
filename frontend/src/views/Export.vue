<script setup>
import { onMounted, ref } from "vue";
import { getReport } from "../api";

const error = ref("");
const loading = ref(false);
const payload = ref(null);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    payload.value = await getReport("export", false);
  } catch (err) {
    payload.value = null;
    error.value = String(err);
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section>
    <div class="head">
      <h2>Last export package</h2>
      <button :disabled="loading" @click="load">Refresh</button>
    </div>
    <p class="hint">
      Reads <code>GET /api/reports/export</code> (the latest
      <code>export_report.json</code>). Run stage 5 on Pipeline first.
    </p>
    <p v-if="error">{{ error }}</p>
    <div v-else-if="payload" class="stack">
      <div class="card">
        <h3>Summary</h3>
        <p class="hint">{{ payload.report?.timestamp }}</p>
        <pre>{{ JSON.stringify(payload.report?.summary, null, 2) }}</pre>
      </div>
      <div class="card">
        <h3>Filter policy used</h3>
        <pre>{{ JSON.stringify(payload.report?.policy, null, 2) }}</pre>
      </div>
      <div class="card">
        <h3>Artifact paths</h3>
        <p><strong>export_dir</strong>: {{ payload.report?.export_dir }}</p>
        <p><strong>report file</strong>: {{ payload.path }}</p>
        <pre>{{ JSON.stringify(payload.report?.artifacts, null, 2) }}</pre>
      </div>
    </div>
  </section>
</template>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
