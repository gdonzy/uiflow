<template>
  <div>
    <el-table :data="data" style="width: 100%">
      <el-table-column v-for="column in columns"
        :key="column.prop"
        :prop="column.prop"
        :label="column.label"
      />
      <slot name="extra-column"></slot>
    </el-table>
    <el-pagination
      class="pagination"
      v-if="total > 0"
      :current-page="currPage"
      :page-sizes="[10, 20, 50, 100]"
      :page-size="pageSize"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
    />
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const props = defineProps({
  data: {
    type: Array<Record<string, any>>,
    required: true,
  },
  columns: {
    type: Array<{ label: string, prop: string }>,
    required: true,
  },
  total: {
    type: Number,
    required: true,
  },
  pageSize: {
    type: Number,
    default: 10,
  },
})

const currPage = ref(1)

const emits = defineEmits(['page-change', 'page-size-change'])

const handlePageChange = (page: number) => {
  currPage.value = page
  emits('page-change', page)
}

const handleSizeChange = (size: number) => {
  emits('page-size-change', currPage.value, size)
}

</script>

<style scoped>
.el-table {
  margin-bottom: 20px;
}
</style>
