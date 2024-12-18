<template>
  <el-container>
    <el-header style="height: auto">
      <strong>界面操作工作流列表</strong>
    </el-header>
    <el-button-group style="padding: 0 20px;">
      <el-button type="primary" @click="fromUIVisible = true" style="width: 100px">根据UI操作创建</el-button>
      <!--
      <el-button type="primary" @click="" style="width: 100px">根据文档创建</el-button>
      -->
    </el-button-group>
    <el-main>
      <listTable
        :data="items"
        :columns="FlowItemColumns"
        :total="total"
        v-model:pageSize="pageSize"
        @page-change="changePageData"
        @page-size-change="changePageSizeData">
        <template #extra-column>
          <el-table-column label="操作" min-width="100">
            <template  #default="scope">
              <el-button @click="gotoDetail(scope.row)">详情</el-button>
              <el-button type="danger" @click="handleDelFlow(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </template>
      </listTable>
      <el-dialog
        v-model="fromUIVisible"
        title="通过监听UI操作创建工作流"
        width="50%"
      >
        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
          <el-form-item label="流程名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入流程名"/>
          </el-form-item>
          <span>点击创建后，会进入UI操作记录模式，</span><span style="color: red">按ESC可以退出UI操作记录模式，</span><span>进而完成流程创建.</span>
        </el-form>
        <template #footer class="dialog-footer">
          <el-button @click="fromUIVisible = false">取消</el-button>
          <el-button @click="fromUISubmit">创建</el-button>
        </template>
      </el-dialog>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useFlowStore, FlowItemColumns } from '@/store/flow'
import listTable from '@/components/ListTable.vue'
import axios from 'axios'

const flowStore = useFlowStore()
const items = computed(() => flowStore.flowList.items)
const total = computed(() => flowStore.flowList.total)
const pageSize = computed(() => flowStore.flowList.pageSize)

const router = useRouter()

const changePageData = (page: number) => {
  flowStore.fetchListData(page, pageSize.value)
}

const changePageSizeData = (page: number, size: number) => {
  flowStore.fetchListData(page, size)
}

const gotoDetail = (row) => {
  router.push(`/static/flow.detail?id=${row.id}`)
}
const handleDelFlow = (row) => {
  ElMessageBox.confirm(
    '确定删除?',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
  .then(async () => {
    const resp = await axios.delete(`/flows/${row.id}`)
    if (resp.status === 200) {
      ElMessage({
        message: '删除成功。',
        type: 'success'
      })
      changePageData(1)
    } else {
      ElMessage({
        message: '删除失败！',
        type: 'warning'
      })
    }
  })
  .catch(() => {
    ElMessage({
      type: 'info',
      message: '已取消删除'
    })
  })
}

// create flow from ui operations
const fromUIVisible = ref(false)
const formRef = ref(null)
const form = reactive({
  name: '',
})
const validateName = async (rule, value, callback) => {
  if (!value) {
    return callback(new Error('用户名不能为空'))
  }
  try {
    const response = await axios.get(`/flows/checkname?name=${value}`)
    if (response.data.existed) {
      return callback(new Error('用户名已存在'))
    } else {
      return callback()
    }
  } catch (error) {
    return callback(new Error('验证失败，请稍后再试'))
  }
}
const rules = {
  name: [
    {required: true, message: '用户名不能为空', trigger: 'change'},
    {validator: validateName, trigger: 'change'},
  ]
}
const fromUISubmit = async () => {
  const resp = await axios.post('/flows', form)
  fromUIVisible.value = false
  router.push(`/static/flow.detail?id=${resp.data.id}`)
}

onMounted(() => {
  changePageSizeData(1, 10);
})
</script>

<style lang="scss"  scoped>
el-header {
  background-color: #409eff;
  color: white;
  text-align: center;
  padding: 15px;
  font-size: 20px;
}
.el-button {
  margin-top: 20px;
}
</style>