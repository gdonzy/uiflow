<template>
  <el-container>
    <el-header style="height: auto">
      <strong>工作流程</strong>
    </el-header>
    <el-button-group v-if="flowStore.detail.status >= 2" style="padding: 0 20px;">
      <el-tooltip content="回到工作流程列表" placement="top">
        <el-button @click="backToFlowList" style="width: 10px"><el-icon><Back /></el-icon></el-button>
      </el-tooltip>
      <el-button type="primary" @click="handleSubmit" style="width: 80px">保存</el-button>
      <el-button type="primary" @click="handleExec" style="width:80px">执行</el-button>
    </el-button-group>
    <el-button-group v-else style="padding: 0 20px;">
      <p style="color: red;">点击ESC按键可以退出屏幕录制</p>
    </el-button-group>
    <el-main>
      <el-form :model="flowStore.detail" ref="detailForm" label-width="70px">
        <el-form-item label="流程名称" key="name">
          <el-input
              v-model="flowStore.detail.name"
              :readonly="'id' in route.query"
              style="width: 280px"
          />
        </el-form-item>
        <el-form-item label="创建时间" key="createAt">
          <span>{{ flowStore.detail.create_at }}</span>
        </el-form-item>
        <div label="流程" key="flow">
          <div class="flowchart" style="width: 1000px; height: 1000px; border: 1px solid black;">
            <VueFlow 
              :nodes="nodes"
              :nodeTypes="nodeTypes"
              :edges="edges"
              class="basic-flow"
              :default-viewport="{ zoom: 1.5 }"
              :min-zoom="0.2"
              :max-zoom="4"
            >
              <Panel position="top-left"  style="margin-top: 0;">
                <el-button-group>
                  <el-button @click="nodeDialogVisible = true">
                    <el-icon color="#409EFC"><Plus /></el-icon>
                  </el-button>
                  <el-button @click="edgeDialogVisible = true">
                    <el-icon color="#409EFC"><Link /></el-icon>
                  </el-button>
                </el-button-group>
              </Panel>
              <el-dialog
                v-model="nodeDialogVisible"
                title="创建节点"
                width="50%"
              >
                <el-form>
                  <el-form-item label="名称">
                    <el-input/>
                  </el-form-item>
                </el-form>
                <template #footer>
                  <div class="dialog-footer">
                    <el-button @click="nodeDialogVisible = false">取消</el-button>
                    <el-button>确定</el-button>
                  </div>
                </template>
              </el-dialog>
              <el-dialog
                v-model="edgeDialogVisible"
                title="连接步骤节点"
                width="50%"
              >
                <el-form>
                </el-form>
                <template #footer>
                  <div class="dialog-footer">
                    <el-button @click="edgeDialogVisible = false">取消</el-button>
                    <el-button type="primary">确定</el-button>
                  </div>
                </template>
              </el-dialog>
            </VueFlow>
          </div>
        </div>
      </el-form>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed, watch, markRaw, onBeforeUnmount } from 'vue'
import { VueFlow, Panel } from '@vue-flow/core'

import { useRoute, useRouter } from 'vue-router'
import { useFlowStore } from '@/store/flow'
import axios from 'axios'
import UiOpNode from '@/components/node/UiOpNode.vue'
import StartNode from '@/components/node/StartNode.vue'
import EndNode from '../components/node/EndNode.vue'
import { useWebSocket } from '@vueuse/core'


const route = useRoute()
const router = useRouter()
const flowStore = useFlowStore()
const handleSubmit = () => {
}

// websocket
const { status, data, open, close } = useWebSocket('ws://localhost:8009/ws/flow')
watch(
  data,
  () => {
    console.log('newData:', data)
  }
)

// vue-flow
const nodeTypes = {
  start: markRaw(StartNode),
  end: markRaw(EndNode),
  uiop: markRaw(UiOpNode)
}
const nodes = computed(() => {
  return flowStore.detail.nodes
})
const edges = computed(() => {
  return flowStore.detail.edges
})
const nodeDialogVisible = ref(false)
const edgeDialogVisible = ref(false)

const backToFlowList = () => {
  router.push('/static/flow')
}
const handleExec = async () => {
  const resp = await axios.post('/exec', {'flow_id': flowStore.detail_id})
  console.log(resp)
}

watch(() => route.query.id, 
      () => {
        if (route.query.id) {
          flowStore.detail_id = route.query.id
          flowStore.fetchDetailData(flowStore.detail_id)
        } else {
          flowStore.detail_id = 0
          flowStore.detail = {}
        }
      },
      {immediate: true}
)
onMounted(() =>  {
  if (route.query.id) {
    flowStore.detail_id = route.query.id
    flowStore.fetchDetailData(flowStore.detail_id)
  } else {
    flowStore.detail_id = 0
    flowStore.detail = {}
  }
})
</script>

<style lang="scss" scoped>
el-header {
  background-color: #409eff;
  color: white;
  text-align: center;
  padding: 15px;
  font-size: 20px;
}

.attribute-card {
  margin-bottom: 20px;
  padding: 15px;
}

.flow-chart-card {
  padding: 15px;
  margin-top: 20px;
}

.chart-container {
  border: 1px solid #dcdfe6;
  padding: 20px;
  text-align: center;
}

.el-button {
  margin-top: 20px;
}
</style>
