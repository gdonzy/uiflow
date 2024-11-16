import { ref, reactive } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

interface HistoryItem {
    id: number
    flow_id: number
    status: number
    create_at: string
    update_at: string
}

interface HistoryList {
    items: HistoryItem[]
    page: number
    pageSize: number
    total: number
}

export const HistoryItemColumns = [
    {label: 'ID', prop: 'id'},
    {label: '流程名称', prop: 'flow_name'},
    {label: '状态', prop: 'status', format: (status: number) => {
        return {0: '未执行', 1: '执行中', 2: '执行完成', 3: '执行失败'}[status]
    }},
    {label: '创建时间', prop: 'create_at', format: (dateStr: string) => {
        return dateStr.slice(0, 19)
    }}
]

export const useHistoryStore = defineStore('historyStore', () => {
    const historyList = reactive({
        items: [],
        page: 1,
        pageSize: 10,
        total: 0,
    } as HistoryList)

    const fetchListData = async (page: number, pageSize: number) => {
        try {
            const resp = await axios.get('/exec', {
                params: { page: page, page_size: pageSize}
            })
            historyList.items = resp.data.items
            historyList.total = resp.data.total
        } catch (error) {
            console.error('Failed to fetch history list data error', error)
        }
    }
    
    return {
        historyList,
        fetchListData,
    }
})