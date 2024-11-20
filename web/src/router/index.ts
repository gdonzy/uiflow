import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/static/',
        name: 'home',
        component: () => import('@/layout/index.vue'),
        children: [
            {
                path: '404',
                name: '404',
                component: () => import('@/views/404.vue')
            },
            {
                path: 'flow',
                name: 'flow',
                component: () => import('@/views/Flow.vue')
            },
            {
                path: 'flow.detail',
                name: 'flow.detail',
                meta: {reload: true},
                component: () => import('@/views/FlowDetail.vue')
            },
            {
                path: 'history',
                name: 'history',
                component: () => import('@/views/history.vue')
            }
        ]
    },
    {
        //path: '/:pathMatch(.*)*',
        path: '/aaa',
        name: '404',
        redirect: '/static/404',
        component: () => import('@/views/404.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router