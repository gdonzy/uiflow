<template>
  <div class="view-container">
    <el-header><strong>执行记录</strong></el-header>
    <el-card class="attribute-card">
      <listTable
        :data="items"
        :columns="HistoryItemColumns"
        :total="total"
        v-model:pageSize="pageSize"
        @page-change="changePageData"
        @page-size-change="changePageSizeData"
      >
        <template #extra-column>
          <el-table-column label="操作" width="150">
            <template  #default="scope">
              <el-button @click="delHistory(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </template>
      </listTable>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, computed } from 'vue'
import { useHistoryStore, HistoryItemColumns } from '../store/history';
import listTable from '@/components/listTable.vue'

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
}

onMounted(() => {
  historyStore.fetchListData(1, 10)
})
</script>

<style lang="scss" scoped>
.attribute-card {
  margin-bottom: 20px;
  padding: 15px;
}
</style>