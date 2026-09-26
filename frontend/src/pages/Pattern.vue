<template>
  <div class="page"><h1>对花说明</h1>
  <p><strong>直对</strong>：有花距时在墙高上加整个花高（pattern_cm/100）作为每条长度（drop_len = 层高 + 花高），再算每卷可裁条数。</p>
  <p><strong>跳对（错花）</strong>：在层高基础上再加半个花高；半个花高先向上取到毫米再换算成米，即 drop_len = 层高 + ⌈花高×1000/2⌉/1000。</p>
  <p>花高为 0 时，两种匹配方式结果相同；跳对遇到负花高会拒绝测算。每次落库都会钉住当次匹配方式、drop_len 与卷数。</p>
  </div>
</template>
