<script setup>
import { onMounted, ref, watch } from 'vue'
import { getJSON, postJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
const walls = ref([]); const rolls = ref([]); const wallId = ref(1); const rollId = ref(1)
const matchType = ref('straight'); const out = ref(null); const err = ref('')
onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter(w => w.data_quality==='clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) { rollId.value = rolls.value[0].id; syncMatch() }
})
// 切换卷材时，匹配方式回到该卷材的默认值；用户仍可在测算台临时改
function syncMatch() {
  const r = rolls.value.find(x => x.id === rollId.value)
  matchType.value = r?.match_type || 'straight'
}
watch(rollId, syncMatch)
async function run(save) {
  err.value = ''; out.value = null
  try {
    out.value = save
      ? await postJSON('/api/estimate', { wall_id: wallId.value, roll_id: rollId.value, match_type: matchType.value, save: true })
      : await getJSON(`/api/estimate?wall_id=${wallId.value}&roll_id=${rollId.value}&match_type=${matchType.value}`)
  } catch (e) { err.value = e.message }
}
</script>
<template>
  <div class="page"><h1>算卷工作台</h1>
  <select v-model.number="wallId"><option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}</option></select>
  <select v-model.number="rollId"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <label class="match-switch"><input type="radio" value="straight" v-model="matchType">直对</label>
  <label class="match-switch"><input type="radio" value="offset" v-model="matchType">跳对</label>
  <button @click="run(false)">试算</button><button @click="run(true)">保存</button>
  <p v-if="err" class="err">测算被拒绝：{{ err }}</p>
  <div v-if="out"><strong>{{ out.rolls }} 卷</strong> · {{ out.drops }} 条 · 每条 {{ out.drop_len_m }}m · {{ out.match_type === 'offset' ? '跳对' : '直对' }}
  <DropStripBar :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.rolls" />
  <details class="diagram">
    <summary>展开示意</summary>
    <p>当次匹配方式：{{ out.match_type === 'offset' ? '跳对（层高 + 半个花高，半花高向上取到毫米）' : '直对（层高 + 花高）' }}</p>
    <p>层高 {{ out.wall.height }} m + 对花余量 {{ (out.drop_len_m - out.wall.height).toFixed(3) }} m（花高 {{ out.pattern_m }} m）= 当次 drop_len：<strong>{{ out.drop_len_m }} m</strong></p>
    <p>每卷可裁 {{ out.strips_per_roll }} 条 · 共 {{ out.drops }} 条 · 需 <strong>{{ out.rolls }}</strong> 卷</p>
  </details>
  </div>
  </div>
</template>
