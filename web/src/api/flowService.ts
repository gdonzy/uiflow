import axios from 'axios'
import { ListItem, ListResponse } from '@/types/list'

axios.defaults.baseURL = 'http://127.0.0.1:8009'

export const fetchFlows = async (
  page: number,
  pageSize: number,
  filters: { sortField?: string; sortOrder?: 'asc' | 'desc'; [key: string]: any }
): Promise<ListResponse> => {
  try {
    const response = await axios.get<ListResponse>('/flows', {
      params: {
        page,
        pageSize,
        sortField: filters.sortField,
        sortOrder: filters.sortOrder,
        ...filters
      }
    })

    return response.data
  } catch (error) {
    console.error('Failed to fetch list:', error)
    throw error
  }
}

export const fetchHistory = async (
  page: number,
  pageSize: number,
  filters: { sortField?: string; sortOrder?: 'asc' | 'desc'; [key: string]: any }
): Promise<ListResponse> => {
  try {
    const response = await axios.get<ListResponse>('/history', {
      params: {
        page,
        pageSize,
        sortField: filters.sortField,
        sortOrder: filters.sortOrder,
        ...filters
      }
    })

    return response.data
  } catch (error) {
    console.error('Failed to fetch list:', error)
    throw error
  }
}