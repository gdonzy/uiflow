<template>
  <el-container>
    <el-header style="height: auto">
      <strong>执行记录</strong>
    </el-header>
    <el-main>
      <listTable
        :data="items"
        :columns="HistoryItemColumns"
        :total="total"
        v-model:pageSize="pageSize"
        @page-change="changePageData"
        @page-size-change="changePageSizeData"
      >
        <template #extra-column>
          <el-table-column label="操作" min-width="70">
            <template  #default="scope">
              <el-button @click="delHistory(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </template>
      </listTable>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { onMounted, computed } from 'vue'
import { useHistoryStore, HistoryItemColumns } from '../store/history';
import listTable from '@/components/listTable.vue'
import axios from 'axios'

const historyStore = useHistoryStore()
const items = computed(() => historyStore.historyList.items)
const total = computed(() => historyStore.historyList.total)
const pageSize = computed(() => historyStore.historyList.pageSize)

const changePageData = (page: number) => {
  historyStore.fetchListData(page, pageSize.value)
}

const changePageSizeData = (page: number, size: number) => {
  historyStore.fetchListData(page, size)
}

const delHistory = (row: any) => {
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
    const resp = await axios.delete(`/exec/${row.id}`)
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

onMounted(() => {
  historyStore.fetchListData(1, 10)
})
</script>

<style lang="scss" scoped>
</style>