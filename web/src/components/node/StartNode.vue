<template>
    <div>
      <div>
        <span>{{ label }}</span>
        <el-icon class="icon" :style="statusColor">
            <component :is="statusIcon"></component>
        </el-icon>
      </div>
      <Handle type="source" :position="Position.Bottom" />
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
    .icon {
        margin-left: 2px;
    }
    </style>