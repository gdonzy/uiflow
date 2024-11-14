import { ref, reactive } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

interface FlowItem {
  id: number
  name: string
  create_at: string
  update_at: string
}

interface FlowNode {
  id: string
  name: string
  type: string
  status: number
  position: object
  extra: object
  create_at: string
  update_at: string
}

interface FlowEdge {
  id: string
  source: string
  target: string
}

interface FlowDetail extends FlowItem{
  nodes: FlowNode[],
  edges: FlowEdge[],
  data: [key: string, number] 
}

interface FlowList {
  items: FlowItem[]
  page: number
  pageSize: number
  total: number
}

export const FlowItemColumns = [
    {label: 'ID', prop: 'id'},
    {label: '名称', prop: 'name'},
    {label: '创建时间', prop: 'create_at'},
    {label: '更新时间', prop: 'update_at'}
]   

export const FlowDetailColumns = [
    {label: 'ID', prop: 'id'},
    {label: '名称', prop: 'name'},
    {label: '详情', prop: 'info'},
    {label: '创建时间', prop: 'create_at'},
    {label: '更新时间', prop: 'update_at'}
]

export const useFlowStore = defineStore('flowStore', () => {
  const flowList = reactive({
    items: [],
    page: 1,
    pageSize: 10,
    total: 0,
  } as FlowList)
  const detail = reactive({} as FlowDetail)
  const detail_id = ref(0)
  
  const fetchListData = async (page: number, pageSize: number) => {
      try {
        const response = await axios.get('/flows', {
          params: { page: page, page_size: pageSize },
        })
        flowList.items = response.data.items
        flowList.total = response.data.total
      } catch (error) {
        console.error('Failed to fetch list data:', error)
      }
  }
  const fetchDetailData = async (id: number) => {
      try {
        const response = await axios.get(`/flows/${id}`)
        const detail_ = response.data as FlowDetail
        if (detail_.nodes && detail_.nodes.length > 0 && !('x' in detail_.nodes[0].position)) {
          //add position into nodes if necessary
          const id_node_map = detail_.nodes.reduce((acc, item) => {
            acc[item.id] = item
            return acc
          }, {} as {[key: string]: FlowNode})
          const input_node = detail_.nodes.find((item: any) => item.type === 'start')
          let curr_ids = [input_node.id]
          let next_ids: string[] = []
          let [x, y, x_interval, y_interval] = [120, 50, 120, 70]
          while (curr_ids.length > 0) {
            next_ids = [] 
            curr_ids.forEach((node_id, index) => {
              if (node_id in id_node_map) {
                id_node_map[node_id].position = {x: x+index*x_interval, y: y}
              }
            })
            const related_edges = detail_.edges.filter(item => curr_ids.includes(item.source))
            related_edges.forEach((item: FlowEdge) => {
              if (item.target in id_node_map) {
                next_ids.push(item.target)
              }
            })
            curr_ids = next_ids
            y = y + y_interval
          }
        }
        Object.keys(detail_).forEach(key => {
          detail[key] = detail_[key]
        })
      } catch (error) {
        console.error('Failed to fetch detail data:', error);
      }
    }
    const updateDetailData = async (id: number, info: object) => {
      try {
        const response = await axios.put(`/flows/${id}`, { info: info })
        Object.keys(response.data).forEach(key => {
          detail[key] = response.data[key]
        })
      } catch (error) {
        console.error('Failed to update detail data', error)
      }
    }
    const fromUICreate = async () => {
      const response = await axios.post('/flows', {name: detail.name})
      console.log('create', response.data)
    }

  
    return {
      flowList,
      detail,
      detail_id,
      fetchListData,
      fetchDetailData,
      updateDetailData,
      fromUICreate,
    }
})

