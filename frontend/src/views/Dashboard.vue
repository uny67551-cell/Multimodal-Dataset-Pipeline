<script setup>
import { onMounted, ref } from "vue";
import { getReports } from "../api";

const reports = ref([]);
const error = ref("");
const loading = ref(false);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const data = await getReports();
    reports.value = data.reports || [];
  } catch (err) {
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
      <h2>Reports</h2>
      <button :disabled="loading" @click="load">Refresh</button>
    </div>
    <p class="hint">Summaries from JSON files under <code>outputs/</code>.</p>
    <p v-if="error">{{ error }}</p>
    <div v-for="item in reports" :key="item.stage" class="card block">
      <div class="head">
        <h3>{{ item.stage }}</h3>
        <span :class="item.available ? 'badge badge-pass' : 'badge badge-muted'">
          {{ item.available ? "available" : "missing" }}
        </span>
      </div>
      <p v-if="item.path" class="hint">{{ item.path }}</p>
      <pre v-if="item.summary">{{ JSON.stringify(item.summary, null, 2) }}</pre>
      <p v-else-if="item.available" class="hint">No summary field in this report.</p>
    </div>
  </section>
</template>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.block {
  margin-bottom: 12px;
}
</style>
