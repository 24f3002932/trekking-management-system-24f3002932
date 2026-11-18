<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import api from '../services/api'
import { getStaff, updateStaff, updateStaffStatus, getTrekkers, updateTrekkerStatus, getAdminBookings, cancelAdminBooking } from '../services/people'
import { getMyBookings, bookTrek, cancelBooking, getHistory, getMyProfile, updateMyProfile, getNotifications, markNotificationRead } from '../services/trekker'
import { getMyTreks, getParticipants, manageAssignedTrek } from '../services/staff-work'

const route = useRoute()
const mode = computed(() => route.meta.screen)
const titleMap = {
  'manage-staff':'Manage Staff', 'manage-trekkers':'Manage Trekkers',
  'admin-bookings':'Manage Bookings', 'staff-treks':'My Assigned Treks',
  'staff-participants':'Trek Participants', 'browse-treks':'Browse Treks',
  'my-bookings':'My Bookings', 'history':'Trekking History',
  'profile':'My Profile', 'notifications':'Notifications'
}
const title = computed(() => titleMap[mode.value] || 'Management')
const rows = ref([])
const treks = ref([])
const search = ref('')
const loading = ref(false)
const error = ref('')
const message = ref('')
const selectedTrek = ref(null)
const participants = ref([])
const profile = ref({name:'', email:'', phone:''})
const editStaff = ref(null)
const staffForm = ref({name:'',email:'',phone:'',experience:0,specialization:'',contact:''})
const trekForm = ref({available_slots:0,status:'Open'})
const filterText = ref('')

async function load() {
  loading.value = true; error.value = ''; message.value = ''
  try {
    if (mode.value === 'manage-staff') rows.value = (await getStaff(search.value)).staff || []
    else if (mode.value === 'manage-trekkers') rows.value = (await getTrekkers(search.value)).users || []
    else if (mode.value === 'admin-bookings') rows.value = (await getAdminBookings(search.value)).bookings || []
    else if (mode.value === 'browse-treks') treks.value = (await api.get('/treks/', {params: search.value ? {search:search.value} : {}})).data.treks || []
    else if (mode.value === 'staff-treks') treks.value = (await getMyTreks()).treks || []
    else if (mode.value === 'my-bookings') rows.value = (await getMyBookings()).bookings || []
    else if (mode.value === 'history') rows.value = (await getHistory()).history || []
    else if (mode.value === 'profile') profile.value = (await getMyProfile()).user
    else if (mode.value === 'notifications') rows.value = (await getNotifications()).notifications || []
  } catch (e) {
    error.value = e.response?.data?.message || 'Unable to load information.'
  } finally { loading.value = false }
}
onMounted(load)

async function toggleStaffStatus(staff) {
  try {
    const data = staff.is_blacklisted
      ? {is_blacklisted:false}
      : {is_blacklisted:true}
    await updateStaffStatus(staff.id, data)
    message.value = 'Staff status updated.'
    await load()
  } catch(e) { error.value = e.response?.data?.message || 'Status update failed.' }
}
async function toggleApproval(staff) {
  try {
    await updateStaffStatus(staff.id, {is_approved:!staff.is_approved})
    message.value = 'Approval status updated.'
    await load()
  } catch(e) { error.value = e.response?.data?.message || 'Approval update failed.' }
}
function startEditStaff(staff) {
  editStaff.value = staff.id
  staffForm.value = {name:staff.name,email:staff.email,phone:staff.phone || '',experience:staff.experience || 0,specialization:staff.specialization || '',contact:staff.contact || ''}
}
async function saveStaff() {
  try {
    await updateStaff(editStaff.value, staffForm.value)
    editStaff.value = null; message.value = 'Staff details updated.'
    await load()
  } catch(e) { error.value = e.response?.data?.message || 'Could not update staff.' }
}
async function toggleTrekker(user) {
  try {
    await updateTrekkerStatus(user.id, {is_blacklisted:!user.is_blacklisted})
    message.value = 'Trekker status updated.'
    await load()
  } catch(e) { error.value = e.response?.data?.message || 'Status update failed.' }
}
async function cancelAdmin(row) {
  if (!confirm('Cancel this booking?')) return
  try { await cancelAdminBooking(row.booking_id); message.value='Booking cancelled.'; await load() }
  catch(e) { error.value=e.response?.data?.message || 'Cancellation failed.' }
}
async function book(trek) {
  if (!confirm(`Book ${trek.name}?`)) return
  try { const r=await bookTrek(trek.id); message.value=r.message; await load() }
  catch(e) { error.value=e.response?.data?.message || 'Booking failed.' }
}
async function cancelMyBooking(row) {
  if (!confirm('Cancel this booking?')) return
  try { await cancelBooking(row.booking_id); message.value='Booking cancelled.'; await load() }
  catch(e) { error.value=e.response?.data?.message || 'Cancellation failed.' }
}
async function openParticipants(trek) {
  selectedTrek.value = trek
  trekForm.value = {available_slots:trek.available_slots,status:trek.status === 'Closed' ? 'Closed':'Open'}
  try { participants.value=(await getParticipants(trek.trek_id)).participants || [] }
  catch(e) { error.value=e.response?.data?.message || 'Unable to load participants.' }
}
async function saveAssignedTrek() {
  try {
    const result=await manageAssignedTrek(selectedTrek.value.trek_id, trekForm.value)
    message.value=result.message
    await load()
    await openParticipants(selectedTrek.value)
  } catch(e) { error.value=e.response?.data?.message || 'Unable to update trek.' }
}
async function saveProfile() {
  try { const r=await updateMyProfile(profile.value); profile.value=r.user; message.value=r.message }
  catch(e) { error.value=e.response?.data?.message || 'Profile update failed.' }
}
async function readNotification(item) {
  try { await markNotificationRead(item.notification_id); await load() }
  catch(e) { error.value=e.response?.data?.message || 'Unable to update notification.' }
}
function date(value) { return value ? new Date(value).toLocaleDateString('en-IN') : '—' }
</script>

<template>
<DashboardLayout>
  <div class="container-fluid p-0">
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4">
      <h3 class="fw-semibold mb-0">{{ title }}</h3>
      <div class="d-flex gap-2">
        <RouterLink v-if="mode==='manage-staff'" to="/admin/create-staff" class="btn btn-primary btn-sm">+ Create Staff</RouterLink>
        <button v-if="['manage-staff','manage-trekkers','admin-bookings','browse-treks'].includes(mode)" class="btn btn-outline-secondary btn-sm" @click="load">Refresh</button>
      </div>
    </div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="loading" class="text-center py-4">Loading...</div>

    <template v-if="!loading && ['manage-staff','manage-trekkers','admin-bookings','browse-treks'].includes(mode)">
      <form class="card card-body border shadow-sm mb-3" @submit.prevent="load">
        <div class="input-group">
          <input v-model="search" class="form-control" placeholder="Search by name, email, trek or location">
          <button class="btn btn-primary">Search</button>
          <button type="button" class="btn btn-outline-secondary" @click="search='';load()">Clear</button>
        </div>
      </form>
    </template>

    <div v-if="mode==='manage-staff' && !loading" class="card border shadow-sm">
      <div class="table-responsive"><table class="table table-bordered table-hover mb-0">
        <thead class="table-light"><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Experience</th><th>Approval</th><th>Blacklist</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="s in rows" :key="s.id"><td>{{s.id}}</td><td>{{s.name}}</td><td>{{s.email}}</td><td>{{s.phone || '—'}}</td><td>{{s.experience}} years</td><td>{{s.is_approved?'Approved':'Pending'}}</td><td>{{s.is_blacklisted?'Blocked':'Active'}}</td><td class="text-nowrap"><button class="btn btn-sm btn-outline-primary me-1" @click="startEditStaff(s)">Edit</button><button class="btn btn-sm btn-outline-secondary me-1" @click="toggleApproval(s)">{{s.is_approved?'Unapprove':'Approve'}}</button><button class="btn btn-sm btn-outline-danger" @click="toggleStaffStatus(s)">{{s.is_blacklisted?'Unblock':'Block'}}</button></td></tr>
          <tr v-if="!rows.length"><td colspan="8" class="text-center text-muted">No staff members found.</td></tr>
        </tbody>
      </table></div>
      <div v-if="editStaff" class="card-body border-top">
        <h5>Edit Staff #{{editStaff}}</h5>
        <form class="row g-2" @submit.prevent="saveStaff">
          <div class="col-md-4"><input v-model="staffForm.name" class="form-control" placeholder="Name" required></div>
          <div class="col-md-4"><input v-model="staffForm.email" type="email" class="form-control" placeholder="Email" required></div>
          <div class="col-md-4"><input v-model="staffForm.phone" class="form-control" placeholder="Phone"></div>
          <div class="col-md-4"><input v-model.number="staffForm.experience" type="number" min="0" class="form-control" placeholder="Experience"></div>
          <div class="col-md-4"><input v-model="staffForm.specialization" class="form-control" placeholder="Specialization"></div>
          <div class="col-md-4"><input v-model="staffForm.contact" class="form-control" placeholder="Contact"></div>
          <div class="col-12"><button class="btn btn-primary me-2">Save Changes</button><button type="button" class="btn btn-secondary" @click="editStaff=null">Cancel</button></div>
        </form>
      </div>
    </div>

    <div v-if="mode==='manage-trekkers' && !loading" class="card border shadow-sm"><div class="table-responsive">
      <table class="table table-bordered table-hover mb-0"><thead class="table-light"><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Registered</th><th>Status</th><th>Action</th></tr></thead>
      <tbody><tr v-for="u in rows" :key="u.id"><td>{{u.id}}</td><td>{{u.name}}</td><td>{{u.email}}</td><td>{{u.phone||'—'}}</td><td>{{date(u.created_at)}}</td><td>{{u.is_blacklisted?'Blocked':'Active'}}</td><td><button class="btn btn-sm" :class="u.is_blacklisted?'btn-outline-success':'btn-outline-danger'" @click="toggleTrekker(u)">{{u.is_blacklisted?'Unblock':'Block'}}</button></td></tr><tr v-if="!rows.length"><td colspan="7" class="text-center text-muted">No trekkers found.</td></tr></tbody></table>
    </div></div>

    <div v-if="mode==='admin-bookings' && !loading" class="card border shadow-sm"><div class="table-responsive">
      <table class="table table-bordered table-hover mb-0"><thead class="table-light"><tr><th>Booking ID</th><th>Trekker</th><th>Email</th><th>Trek</th><th>Location</th><th>Booking Date</th><th>Status</th><th>Action</th></tr></thead>
      <tbody><tr v-for="b in rows" :key="b.booking_id"><td>{{b.booking_id}}</td><td>{{b.user.name}}</td><td>{{b.user.email}}</td><td>{{b.trek.name}}</td><td>{{b.trek.location}}</td><td>{{date(b.booking_date)}}</td><td>{{b.status}}</td><td><button v-if="b.status==='Booked'" class="btn btn-sm btn-outline-danger" @click="cancelAdmin(b)">Cancel</button><span v-else>—</span></td></tr><tr v-if="!rows.length"><td colspan="8" class="text-center text-muted">No bookings found.</td></tr></tbody></table>
    </div></div>

    <div v-if="mode==='browse-treks' && !loading" class="row g-3">
      <div v-for="t in treks" :key="t.id" class="col-12 col-md-6 col-xl-4"><div class="card h-100 border shadow-sm"><div class="card-body">
        <h5>{{t.name}}</h5><p class="text-muted mb-2">{{t.location}}</p><p>{{t.description || 'Explore this trekking experience.'}}</p>
        <div class="small mb-2">Difficulty: <strong>{{t.difficulty}}</strong> · Duration: {{t.duration}} days</div>
        <div class="small mb-3">Dates: {{date(t.start_date)}} – {{date(t.end_date)}} · Slots: {{t.available_slots}} · {{t.status}}</div>
        <button class="btn btn-primary btn-sm" :disabled="t.status!=='Open' || t.available_slots<=0" @click="book(t)">Book Trek</button>
      </div></div></div>
      <div v-if="!treks.length" class="text-center text-muted py-4">No treks available.</div>
    </div>

    <div v-if="mode==='staff-treks' && !loading" class="card border shadow-sm"><div class="table-responsive"><table class="table table-bordered mb-0"><thead class="table-light"><tr><th>Trek</th><th>Location</th><th>Dates</th><th>Slots</th><th>Status</th><th>Action</th></tr></thead><tbody>
      <tr v-for="t in treks" :key="t.trek_id"><td>{{t.name}}</td><td>{{t.location}}</td><td>{{date(t.start_date)}} – {{date(t.end_date)}}</td><td>{{t.available_slots}}</td><td>{{t.status}}</td><td><button class="btn btn-sm btn-primary" @click="openParticipants(t)">Participants / Manage</button></td></tr>
      <tr v-if="!treks.length"><td colspan="6" class="text-center text-muted">No treks assigned to you.</td></tr>
    </tbody></table></div></div>

    <div v-if="mode==='staff-treks' && selectedTrek" class="card border shadow-sm mt-3">
      <div class="card-header bg-white"><strong>{{selectedTrek.name}} – Manage Participants</strong></div>
      <div class="card-body">
        <form class="row g-2 align-items-end mb-3" @submit.prevent="saveAssignedTrek">
          <div class="col-md-4"><label class="form-label">Available Slots</label><input v-model.number="trekForm.available_slots" type="number" min="0" class="form-control"></div>
          <div class="col-md-4"><label class="form-label">Status</label><select v-model="trekForm.status" class="form-select"><option>Open</option><option>Closed</option></select></div>
          <div class="col-md-4"><button class="btn btn-primary">Update Trek</button></div>
        </form>
        <h6>Participants ({{participants.length}})</h6>
        <div class="table-responsive"><table class="table table-sm table-bordered"><thead><tr><th>Booking</th><th>Name</th><th>Email</th><th>Phone</th><th>Date</th></tr></thead><tbody><tr v-for="p in participants" :key="p.booking_id"><td>{{p.booking_id}}</td><td>{{p.name}}</td><td>{{p.email}}</td><td>{{p.phone||'—'}}</td><td>{{date(p.booking_date)}}</td></tr><tr v-if="!participants.length"><td colspan="5" class="text-center">No active participants.</td></tr></tbody></table></div>
      </div>
    </div>

    <div v-if="['my-bookings','history'].includes(mode) && !loading" class="card border shadow-sm"><div class="table-responsive"><table class="table table-bordered table-hover mb-0">
      <thead class="table-light"><tr><th>Booking ID</th><th>Trek</th><th>Location</th><th>Difficulty</th><th>Dates</th><th>Booking Date</th><th>Status</th><th v-if="mode==='my-bookings'">Action</th></tr></thead>
      <tbody><tr v-for="b in rows" :key="b.booking_id"><td>{{b.booking_id}}</td><td>{{b.trek_name}}</td><td>{{b.location}}</td><td>{{b.difficulty}}</td><td>{{date(b.start_date)}} – {{date(b.end_date)}}</td><td>{{date(b.booking_date)}}</td><td>{{b.booking_status || b.status}}</td><td v-if="mode==='my-bookings'"><button v-if="b.booking_status==='Booked'" class="btn btn-sm btn-outline-danger" @click="cancelMyBooking(b)">Cancel</button><span v-else>—</span></td></tr><tr v-if="!rows.length"><td :colspan="mode==='my-bookings'?8:7" class="text-center text-muted">No records found.</td></tr></tbody>
    </table></div></div>

    <div v-if="mode==='profile' && !loading" class="card border shadow-sm"><div class="card-body"><form class="row g-3" @submit.prevent="saveProfile">
      <div class="col-md-6"><label class="form-label">Full Name</label><input v-model="profile.name" class="form-control" required></div>
      <div class="col-md-6"><label class="form-label">Email</label><input v-model="profile.email" type="email" class="form-control" required></div>
      <div class="col-md-6"><label class="form-label">Phone</label><input v-model="profile.phone" class="form-control"></div>
      <div class="col-12"><button class="btn btn-primary">Save Profile</button></div>
    </form></div></div>

    <div v-if="mode==='notifications' && !loading" class="list-group">
      <div v-for="n in rows" :key="n.notification_id" class="list-group-item d-flex justify-content-between align-items-center"><div><div>{{n.message}}</div><small class="text-muted">{{date(n.created_at)}} · {{n.status}}</small></div><button v-if="n.status==='Unread'" class="btn btn-sm btn-outline-primary" @click="readNotification(n)">Mark read</button></div>
      <div v-if="!rows.length" class="list-group-item text-center text-muted">No notifications.</div>
    </div>
  </div>
</DashboardLayout>
</template>
