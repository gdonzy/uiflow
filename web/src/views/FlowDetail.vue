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
      <p class="warning-text">当前正在记录屏幕操作，停止录制请点击ESC键退出录制</p>
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
        <el-form-item v-show="flowStore.detail.status == 2" label="执行状态" key="lastExec">
          <span>1</span>
        </el-form-item>
        <div v-show="flowStore.detail.status >= 2" label="流程" key="flow">
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
                  <el-tooltip placement="bottom">
                    <template #content>点击添加节点</template>
                    <el-button @click="handleNodeDialog(null)">
                      <el-icon color="#409EFC"><Plus /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip placement="bottom">
                    <template #content>点击添加连线</template>
                    <el-button @click="handleEdgeDialog(null)">
                      <el-icon color="#409EFC"><Link /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip placement="bottom">
                    <template #content>单击流程图中的元素可编辑，双击流程图中的元素可删除。</template>
                    <el-button style="border: 0;margin-left: 2px;">
                      <el-icon color="#409EFC"><QuestionFilled /></el-icon>
                    </el-button>
                  </el-tooltip>
                </el-button-group>
              </Panel>
              <el-dialog
                v-model="nodeDialogVisible"
                :title="nodeDlTitle"
                width="50%"
              >
                <el-form v-model="newNode">
                  <el-form-item label="名称">
                    <el-input
                      v-model="newNode.label"
                      style="width: 280px"
                    />
                  </el-form-item>
                </el-form>
                <template #footer>
                  <div class="dialog-footer">
                    <el-button @click="nodeDialogVisible = false">取消</el-button>
                    <el-button @click="handleAddUpdateNode">确定</el-button>
                  </div>
                </template>
              </el-dialog>
              <el-dialog
                v-model="edgeDialogVisible"
                title="连接步骤节点"
                width="50%"
              >
                <el-form :model="newEdge">
                  <el-row :gutter="20" align="middle">
                    <el-col :span="10">
                      <el-form-item>
                        <el-input 
                          v-model="newEdge.source"
                          placeholder="输入来源节点ID"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="4" class="arrow-col">
                      <span style="font-size: 1.5rem;margin-bottom: 20%;">-></span>
                    </el-col>
                    <el-col :span="10">
                      <el-form-item>
                        <el-input 
                          v-model="newEdge.target"
                          placeholder="输入目标节点ID"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-form>
                <template #footer>
                  <div class="dialog-footer">
                    <el-button @click="edgeDialogVisible = false">取消</el-button>
                    <el-button @click="handleAddUpdateEdge">确定</el-button>
                  </div>
                </template>
              </el-dialog>
              <el-dialog
                v-model="nodeDelVisible"
                title="删除节点"
                width="50%"
              >
                <span>确定删除节点&ltNode:{{ delNodeId }}&gt?</span>
                <template #footer>
                  <div class="dialog-footer">
                    <el-button @click="nodeDelVisible = false">取消</el-button>
                    <el-button @click="handleRemoveNode">确定</el-button>
                  </div>
                </template>
              </el-dialog>
              <el-dialog
                v-model="edgeDelVisible"
                title="删除节点"
                width="50%"
              >
                <span>确定删除连线&ltEdge:source({{delEdge.source}})->target({{delEdge.target}})&gt?</span>
                <template #footer>
                  <div class="dialog-footer">
                    <el-button @click="edgeDelVisible = false">取消</el-button>
                    <el-button @click="handleRemoveEdge">确定</el-button>
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
import { ref, reactive, onMounted, computed, watch, markRaw, onBeforeUnmount } from 'vue'
import { VueFlow, Panel, useVueFlow } from '@vue-flow/core'

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
const { data } = useWebSocket('ws://localhost:8009/ws/flow')
watch(
  data,
  () => {
    const info = JSON.parse(data.value)
    console.log('ws info:', info)
    if (info.msg_type === 'flow_status' &&
        info.flow_id === route.query.id &&
        info.flow_status > 1) {
      window.location.reload()
    } else if (info.msg_type === 'node_status' &&
               info.flow_id === route.query.id) {
      // node status
      window.location.reload()
    } else if (info.msg_type === 'exec_status' &&
               info.flow_id === route.query.id) {
      // exec status
      window.location.reload()
    }
  }
)

//vue-flow
const flowObj = useVueFlow()
//vue-flow: node操作
const nodeTypes = {
  start: markRaw(StartNode),
  end: markRaw(EndNode),
  uiop: markRaw(UiOpNode)
}
const nodes = computed(() => {
  return flowStore.detail.nodes
})
const nodeDlTitle = ref('')
const newNode = reactive({
  id: '', type: 'uiop', label: '', status: 0,
  'position': {'x': 260, 'y': 80},
  'data': {'op_type': '', 'status': 0}
})
const delNodeId = ref('')
const nodeDialogVisible = ref(false)
const nodeDelVisible = ref(false)
const handleNodeDialog = (nodeInfo) => {
  if (nodeInfo) {
    Object.keys(nodeInfo).forEach(key => {
        newNode[key] = nodeInfo[key]
    })
    nodeDlTitle.value = '编辑节点'
  } else {
    newNode.id = ''
    newNode.label = ''
    nodeDlTitle.value = '添加节点'
  }
  nodeDialogVisible.value = true
}
flowObj.onNodeClick(({event, node}) => {
  handleNodeDialog(node)
})
flowObj.onNodeDoubleClick(({event, node}) => {
  delNodeId.value = node.id
  nodeDelVisible.value = true
})
const handleAddUpdateNode = () => {
  nodeDialogVisible.value = false
  if (newNode.id.length > 0) {
    flowObj.updateNode(newNode.id, newNode)
    // updateNode调用，label等字段变化不会触发onNodesChange
    const node = flowStore.find(item => item.id == newNode.id)
    if (node) {
      Object.keys(newNode).forEach(key => {
        node[key] = newNode[key]
      })
    }
  } else {
    const maxNodeId = flowStore.detail.nodes.reduce((max, node) => {
      return Math.max(max, parseInt(node.id))
    }, 0)
    newNode.id = (maxNodeId + 1).toString()
    flowObj.addNodes([newNode])
  }
}
const handleRemoveNode = () => {
  nodeDelVisible.value = false
  const delEdgeIds: string[] = []
  flowObj.removeNodes([delNodeId.value])
  flowObj.removeEdges(delEdgeIds)
}
flowObj.onNodesChange((changes) => {
  const delNodeIds: number[] = []
  const updateNodesMap = {} as [key: string, value: any]
  changes.forEach(change => {
    if (change.type == 'remove') {
      delNodeIds.push(change.id)
    } else if (change.type === 'add') {
      flowStore.detail.nodes.push(change.item)
    }
  })
  for (let i=flowStore.detail.nodes.length-1; i>=0; i--) {
    const node = flowStore.detail.nodes[i]
    if (delNodeIds.includes(node.id)) {
      flowStore.detail.nodes.splice(i, 1)
    } else if (node.id in updateNodesMap) {
      Object.keys(node).forEach(key => {
        node[key] = updateNodesMap[node.id][key]
      })
    }
  }
})
//vue-flow: edge操作
const edges = computed(() => {
  return flowStore.detail.edges
})
const edgeDlTitle = ref('')
const newEdge = reactive({'id': '', 'source': '', 'target': ''})
const delEdge = reactive({'id': '', 'source': '', 'target': ''})
const edgeDialogVisible = ref(false)
const edgeDelVisible = ref(false)
const handleEdgeDialog = (edgeInfo) => {
  if (edgeInfo) {
    Object.keys(newEdge).forEach(key => {
      newEdge[key] = edgeInfo[key]
    })
    edgeDlTitle.value = '编辑步骤节点连线'
  } else {
    newEdge.id = ''
    newEdge.source = ''
    newEdge.target = ''
    edgeDlTitle.value = '添加步骤节点连线'
  }
  edgeDialogVisible.value = true
}
flowObj.onEdgeClick(({event, edge}) => {
  handleEdgeDialog(edge)
})
flowObj.onEdgeDoubleClick(({event, edge}) => {
  Object.keys(delEdge).forEach(key => {
    delEdge[key] = edge[key]
  })
  edgeDelVisible.value = true
})
const handleAddUpdateEdge = () => {
  edgeDialogVisible.value = false
  if (newEdge.id.length > 0) {
    // 由于edge的id与source、target有关联，采用先删除再新增的方式来更新edge
    flowObj.removeEdges([newEdge.id])
  }
  newEdge.id = `e${newEdge.source}_${newEdge.target}`
  flowObj.addEdges([newEdge])
}
const handleRemoveEdge = () => {
  edgeDelVisible.value = false
  flowObj.removeEdges([delEdge.id])
}
flowObj.onEdgesChange((changes) => {
  const delEdgeIds: number[] = []
  changes.forEach(change => {
    if (change.type === 'remove') {
      delEdgeIds.push(change.id)
    } else if (change.type === 'add') {
      flowStore.detail.edges.push(change.item)
    }
  })
  for (let i=flowStore.detail.edges.length-1; i>=0; i--) {
    const edge = flowStore.detail.edges[i]
    if (delEdgeIds.includes(edge.id)) {
      flowStore.detail.edges.splice(i, 1)
    }
  }
})


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

.warning-text {
  font-size: 24px;
  color: red;
}

.arrow-col{
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
