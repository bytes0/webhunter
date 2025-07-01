import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Recon from '../views/Recon.vue'
import OSINT from '../views/OSINT.vue'
import VulnScan from '../views/VulnScan.vue'
import Telegram from '../views/Telegram.vue'
import Exploitation from '../views/Exploitation.vue'

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
    path: '/exploitation',
    name: 'Exploitation',
    component: Exploitation
  },
  {
    path: '/telegram',
    name: 'Telegram',
    component: Telegram
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 