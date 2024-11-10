<template>
  <el-container>
    <el-header>
      <el-menu
        :default-active="activeIndex"
        class="el-menu-demo"
        mode="horizontal"
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
        @select="handleSelect"
      >
        <el-menu-item index="flow">任务流程</el-menu-item>
        <el-menu-item index="history">执行记录</el-menu-item>
        <el-button @click="aboutVisible = true" class="about">关于</el-button>
      </el-menu>
    </el-header>
    <el-main>
      <router-view v-slot="{ Component }">
        <component :is="Component">
          <el-dialog
            title="关于"
            :visible.sync="aboutVisible"
            width="30%"
          >
            <span>111</span>
            <span class='dialog-footer'>
              <el-button @click="aboutVisible = false">关闭</el-button>
            </span>
          </el-dialog>
        </component>
      </router-view>
    </el-main>
  </el-container>
</template>
 
<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const aboutVisible = ref(false)
 
const activeIndex = ref('flow-list')
const handleSelect = (key: string, _keyPath: string[]) => {
  const path = {
    'flow': '/static/flow',
    'history': '/static/history',
  }[key]
  router.push(path)
}

watch(() => route.path, () => {
  activeIndex.value = route.path.replace('/static/', '').replace('flow.detail', 'flow')
})
onMounted(() => {
  activeIndex.value = route.path.replace('/static/', '')
})
</script>
 
<style lang="scss" scoped>
.about {
    position: absolute;
    right: 16px;
    top: 1.5vh;
    background-color: #545c64;
    border: 0px;
    color: #fff;
}
</style>

  
  