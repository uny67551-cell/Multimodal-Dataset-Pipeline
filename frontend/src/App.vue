<script setup>
import { ref } from "vue";
import Dashboard from "./views/Dashboard.vue";
import Pipeline from "./views/Pipeline.vue";
import Gallery from "./views/Gallery.vue";

const tab = ref("pipeline");
</script>

<template>
  <div class="layout">
    <h1>Multimodal Dataset Pipeline</h1>
    <nav>
      <button :class="{ on: tab === 'pipeline' }" @click="tab = 'pipeline'">Pipeline</button>
      <button :class="{ on: tab === 'dashboard' }" @click="tab = 'dashboard'">Dashboard</button>
      <button :class="{ on: tab === 'gallery' }" @click="tab = 'gallery'">Gallery</button>
    </nav>
    <Pipeline v-if="tab === 'pipeline'" />
    <Dashboard v-if="tab === 'dashboard'" />
    <Gallery v-if="tab === 'gallery'" />
  </div>
</template>

<style>
body { font-family: sans-serif; margin: 24px; }
nav { display: flex; gap: 8px; margin: 16px 0; }
button.on { font-weight: bold; }
.layout { max-width: 960px; }
</style>