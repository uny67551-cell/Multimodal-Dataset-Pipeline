<script setup>
import { ref } from "vue";
import Dashboard from "./views/Dashboard.vue";
import Pipeline from "./views/Pipeline.vue";
import Gallery from "./views/Gallery.vue";
import ExportPage from "./views/Export.vue";

const tab = ref("pipeline");
</script>

<template>
  <div class="shell">
    <header class="bar">
      <div>
        <p class="kicker">MDP console</p>
        <h1>Multimodal Dataset Pipeline</h1>
      </div>
      <p class="hint bar-note">Ingest → infer → metadata → QC → export</p>
    </header>
    <nav class="tabs">
      <button class="tab" :class="{ on: tab === 'pipeline' }" @click="tab = 'pipeline'">
        Pipeline
      </button>
      <button class="tab" :class="{ on: tab === 'dashboard' }" @click="tab = 'dashboard'">
        Dashboard
      </button>
      <button class="tab" :class="{ on: tab === 'gallery' }" @click="tab = 'gallery'">
        Gallery
      </button>
      <button class="tab" :class="{ on: tab === 'export' }" @click="tab = 'export'">
        Export
      </button>
    </nav>
    <main class="page">
      <Pipeline v-show="tab === 'pipeline'" />
      <Dashboard v-show="tab === 'dashboard'" />
      <Gallery v-show="tab === 'gallery'" />
      <ExportPage v-show="tab === 'export'" />
    </main>
  </div>
</template>

<style scoped>
.shell {
  max-width: 1080px;
  margin: 0 auto;
  padding: 0 20px 40px;
}

.bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
  padding: 22px 0 8px;
}

.kicker {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

.bar-note {
  margin: 0;
}

.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  margin-bottom: 18px;
}

.page {
  min-height: 60vh;
}
</style>
