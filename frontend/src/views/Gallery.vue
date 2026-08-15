<script setup>
import { onMounted, ref } from "vue";
import { getGallery, imageUrl } from "../api";

const items = ref([]);
const error = ref("");

onMounted(async () => {
  try {
    const data = await getGallery();
    items.value = data.items;
  } catch (e) {
    error.value = String(e);
  }
});
</script>

<template>
  <section>
    <h2>Gallery</h2>
    <p v-if="error">{{ error }}</p>
    <div class="grid">
      <article v-for="item in items" :key="item.id" class="card">
        <img v-if="item.exists" :src="imageUrl(item.id)" :alt="item.id" />
        <p><strong>{{ item.id }}</strong></p>
        <p>{{ item.caption }}</p>
        <p>QC: {{ item.quality_status }} / meta: {{ item.metadata_status }}</p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.card { border: 1px solid #ccc; padding: 8px; }
img { width: 100%; height: 160px; object-fit: cover; }
</style>