<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, patchJSON } from '../api'
const items = ref([]); const err = ref('')
onMounted(async () => { items.value = (await getJSON('/api/rolls')).items })
async function setMatch(r, mt) {
  err.value = ''
  try {
    const updated = await patchJSON(`/api/rolls/${r.id}`, { match_type: mt })
    const i = items.value.findIndex(x => x.id === r.id)
    if (i >= 0) items.value[i] = updated
  } catch (e) { err.value = e.message }
}
</script>
<template>
  <div class="page"><h1>纸卷规格</h1>
  <p v-if="err" class="err">{{ err }}</p>
  <div v-for="r in items" :key="r.id" class="roll-chip">
    {{ r.name }} · 宽{{ r.width }} · 长{{ r.length }} · 花距{{ r.pattern_cm }}cm
    <span class="match-switch">
      默认匹配：
      <label><input type="radio" :name="`mt-${r.id}`" :checked="(r.match_type||'straight')==='straight'" @change="setMatch(r,'straight')">直对</label>
      <label><input type="radio" :name="`mt-${r.id}`" :checked="(r.match_type||'straight')==='offset'" @change="setMatch(r,'offset')">跳对</label>
    </span>
  </div>
  </div>
</template>
