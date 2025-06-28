import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Recon from '../views/Recon.vue'
import OSINT from '../views/OSINT.vue'
import VulnScan from '../views/VulnScan.vue'
import Reporting from '../views/Reporting.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/recon',
    name: 'Recon',
    component: Recon
  },
  {
    path: '/osint',
    name: 'OSINT',
    component: OSINT
  },
  {
    path: '/vulnscan',
    name: 'VulnScan',
    component: VulnScan
  },
  {
    path: '/reporting',
    name: 'Reporting',
    component: Reporting
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 