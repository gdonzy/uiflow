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
    {label: '流程名称', prop: 'flow_id'},
    {label: '状态', prop: 'status'},
    {label: '创建时间', prop: 'create_at'}
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