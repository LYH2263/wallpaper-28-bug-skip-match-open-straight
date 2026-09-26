<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([]); const lookupId = ref(''); const detail = ref(null); const err = ref('')
const matchLabel = mt => mt === 'offset' ? '跳对' : (mt === 'straight' ? '直对' : '（旧记录未记录，按直对）')
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
async function lookup() {
  err.value = ''; detail.value = null
  if (!lookupId.value) return
  try { detail.value = await getJSON(`/api/runs/${lookupId.value}`) }
  catch (e) { err.value = e.message }
}
</script>
<template>
  <div class="page"><h1>记录</h1>
  <div class="lookup">
    按编号回看：<input v-model="lookupId" type="number" min="1" @keyup.enter="lookup">
    <button @click="lookup">回看</button>
    <p v-if="err" class="err">{{ err }}</p>
    <div v-if="detail" class="run-detail">
      <p>#{{ detail.id }} {{ detail.wall_name }} → <strong>{{ detail.result?.rolls }} 卷</strong></p>
      <p>匹配方式：<strong>{{ matchLabel(detail.result?.match_type) }}</strong></p>
      <p>drop_len：{{ detail.result?.drop_len_m }} m · 每条花高 {{ detail.result?.pattern_m }} m · {{ detail.result?.drops }} 条 · 每卷 {{ detail.result?.strips_per_roll }} 条</p>
    </div>
  </div>
  <ul><li v-for="r in items" :key="r.id">
    #{{ r.id }} {{ r.wall_name }} → {{ r.result?.rolls }} 卷 · {{ matchLabel(r.result?.match_type) }} · drop {{ r.result?.drop_len_m }}m
  </li></ul>
  <p class="hint">列表与按号回看均显示落库时钉住的匹配方式、条长、每卷条数与卷数，不随卷材当前默认重算。</p>
  </div>
</template>
