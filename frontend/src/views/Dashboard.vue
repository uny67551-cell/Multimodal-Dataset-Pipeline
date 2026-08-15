<script setup>
import { onMounted, ref } from "vue";
import { getReports } from "../api";

const reports = ref([]);
const error = ref("");

onMounted(async () => {
  try {
    const data = await getReports();
    reports.value = data.reports;
  } catch (e) {
    error.value = String(e);
  }
});
</script>

<template>
  <section>
    <h2>Reports</h2>
    <p v-if="error">{{ error }}</p>
    <div v-for="item in reports" :key="item.stage" class="card">
      <h3>{{ item.stage }}</h3>
      <p>{{ item.available ? "available" : "missing" }}</p>
      <pre v-if="item.summary">{{ JSON.stringify(item.summary, null, 2) }}</pre>
    </div>
  </section>
</template>

<style scoped>
.card { border: 1px solid #ccc; padding: 12px; margin-bottom: 12px; }
pre { background: #f6f6f6; padding: 8px; overflow: auto; }
</style>