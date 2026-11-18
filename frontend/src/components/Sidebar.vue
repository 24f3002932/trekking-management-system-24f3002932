<script setup>
import { useAuthStore } from '../stores/auth'
const authStore = useAuthStore()
const menus = {
  admin: [
    {label:'Dashboard',path:'/admin'},
    {label:'Manage Treks',path:'/admin/treks'},
    {label:'Create Staff',path:'/admin/create-staff'},
    {label:'Manage Staff',path:'/admin/staff'},
    {label:'Manage Trekkers',path:'/admin/trekkers'},
    {label:'Bookings',path:'/admin/bookings'},
  ],
  staff: [
    {label:'Dashboard',path:'/staff'},
    {label:'My Treks / Participants',path:'/staff/my-treks'},
  ],
  trekker: [
    {label:'Dashboard',path:'/trekker'},
    {label:'Browse Treks',path:'/trekker/browse'},
    {label:'My Bookings',path:'/trekker/bookings'},
    {label:'Trekking History',path:'/trekker/history'},
    {label:'Profile',path:'/trekker/profile'},
    {label:'Notifications',path:'/trekker/notifications'},
  ],
}
const menuItems = menus[authStore.userRole] || []
</script>
<template>
  <aside class="sidebar bg-white border-end">
    <div class="p-3 border-bottom fw-semibold">Menu</div>
    <nav class="nav flex-column p-2">
      <RouterLink v-for="item in menuItems" :key="item.path" :to="item.path" class="nav-link" active-class="active">{{item.label}}</RouterLink>
    </nav>
  </aside>
</template>
<style scoped>
.sidebar{width:220px;min-height:calc(100vh - 57px);flex-shrink:0}
.nav-link{color:#343a40;padding:10px 12px;border-radius:4px;font-size:14px}
.nav-link.active{background:#e7f1ff;color:#0d6efd;font-weight:600}
</style>
