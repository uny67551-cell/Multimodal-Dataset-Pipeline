<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import { getGallery, imageUrl } from "../api";

const items = ref([]);
const error = ref("");
const loading = ref(false);
const selected = ref(null);

function badgeClass(status) {
  if (status === "pass") return "badge badge-pass";
  if (status === "warn") return "badge badge-warn";
  if (status === "reject") return "badge badge-reject";
  return "badge badge-muted";
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const data = await getGallery();
    items.value = data.items || [];
  } catch (err) {
    error.value = String(err);
  } finally {
    loading.value = false;
  }
}

function onKey(event) {
  if (event.key === "Escape") {
    selected.value = null;
  }
}

onMounted(() => {
  load();
  window.addEventListener("keydown", onKey);
});

onUnmounted(() => {
  window.removeEventListener("keydown", onKey);
});
</script>

<template>
  <section>
    <div class="head">
      <h2>Gallery</h2>
      <button :disabled="loading" @click="load">Refresh</button>
    </div>
    <p class="hint">Click a thumbnail to open the processed image. Colors follow QC status.</p>
    <p v-if="error">{{ error }}</p>
    <p v-else-if="loading && !items.length" class="hint">Loading…</p>
    <p v-else-if="!items.length" class="hint">No processed images yet. Run ingest (and later stages) first.</p>
    <div class="grid">
      <article v-for="item in items" :key="item.id" class="card tile">
        <button
          v-if="item.exists"
          type="button"
          class="thumb"
          @click="selected = item"
        >
          <img :src="imageUrl(item.id)" :alt="item.id" />
        </button>
        <div v-else class="missing">Missing file</div>
        <p><strong>{{ item.id }}</strong></p>
        <p class="caption">{{ item.caption || "—" }}</p>
        <p>
          <span :class="badgeClass(item.quality_status)">
            QC {{ item.quality_status || "n/a" }}
          </span>
          <span v-if="item.is_blurry" class="badge badge-warn">blurry</span>
          <span v-if="item.is_duplicate" class="badge badge-warn">duplicate</span>
          <span v-if="item.is_corrupt" class="badge badge-reject">corrupt</span>
        </p>
      </article>
    </div>

    <div
      v-if="selected"
      class="modal"
      @click.self="selected = null"
    >
      <div class="modal-card">
        <div class="head">
          <h3>{{ selected.id }}</h3>
          <button type="button" @click="selected = null">Close</button>
        </div>
        <img
          v-if="selected.exists"
          class="full"
          :src="imageUrl(selected.id)"
          :alt="selected.id"
        />
        <p>{{ selected.caption }}</p>
        <p>
          <span :class="badgeClass(selected.quality_status)">
            QC {{ selected.quality_status || "n/a" }}
          </span>
          blur score: {{ selected.blur_score ?? "—" }}
        </p>
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

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.tile p {
  margin: 6px 0 0;
}

.caption {
  font-size: 13px;
  color: var(--muted);
  min-height: 2.4em;
}

.thumb {
  display: block;
  width: 100%;
  padding: 0;
  border: none;
  background: #0f172a;
  border-radius: 8px;
  overflow: hidden;
  cursor: zoom-in;
}

.thumb img,
.full {
  width: 100%;
  display: block;
}

.thumb img {
  height: 160px;
  object-fit: cover;
}

.missing {
  height: 160px;
  display: grid;
  place-items: center;
  background: #f1f5f9;
  color: var(--muted);
  border-radius: 8px;
}

.modal {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.72);
  display: grid;
  place-items: center;
  padding: 24px;
  z-index: 20;
}

.modal-card {
  background: var(--surface);
  border-radius: 12px;
  padding: 16px;
  max-width: min(900px, 100%);
  max-height: 90vh;
  overflow: auto;
}

.full {
  max-height: 70vh;
  object-fit: contain;
  background: #0f172a;
  border-radius: 8px;
  margin: 12px 0;
}
</style>
