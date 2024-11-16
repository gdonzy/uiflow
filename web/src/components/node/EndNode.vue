<template>
<div>
  <div class="node-container">
    <Handle type="target" :position="Position.Top" />
    <div class="node-info">
      <el-icon class="icon" :style="statusColor">
        <component :is="statusIcon"></component>
      </el-icon>
      <span>{{ label }}</span>
    </div>
  </div>
</div>
</template>
    
<script lang="ts" setup>
import { Position, Handle } from '@vue-flow/core'
import { Clock, Loading, Check, CircleClose } from '@element-plus/icons-vue'

const props = defineProps(['label', 'data'])
const statuses = {
    0: {
        name: '待执行',
        icon: Clock,
        color: '#909399',
    },
    1: {
        name: '执行中',
        icon: Loading,
        color: '#409EFF',
    },
    2: {
        name: '执行成功',
        icon: Check,
        color: '#67C23A',
    },
    3: {
        name: '待执失败',
        icon: CircleClose,
        color: '#F56C6C',
    }
}
const statusColor = computed(() => {
    return `color: ${statuses[props.data.status].color}`
})
const statusIcon = computed(() => {
    return statuses[props.data.status].icon
})

</script>

<style lang="scss" scoped>
.node-container {
    position: relative;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    background-color: white;
    z-index: 1;
    .node-info {
        margin: 0.2rem 0.3rem;
        font-size: 1rem;
        display: flex;
        align-items: center;
        .info-icon {
            margin-right: 4px;
        }
    }
}
</style>