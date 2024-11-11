import { defineStore } from 'pinia'
import { io } from 'socket.io-client'

export const useWebsocketStore = defineStore('websocket', () => {
    const flowidSocketMap = {}
    const wsFlowConn = (flowid: str) => {
        if (!(flowid in flowidSocketMap)) {
            flowidSocketMap[flowid] = io(`ws://127.0.0.1:8009/ws/flows/${flowid}`)
        }
        return flowidSocketMap[flowid]
    }
    const wsFlowDisconn = (flowid: str) => {
        if (flowid in flowidSocketMap) {
            flowidSocketMap[flowid].disconnect()
            delete flowidSocketMap[flowid]
        }
    }
    return {
        flowidSocketMap,
        wsFlowConn,
        wsFlowDisconn,
    }
})

