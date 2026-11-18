
<script setup>
import { ref, onMounted } from 'vue'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import {
  getTreks,
  createTrek,
  updateTrek,
  deleteTrek,
} from '../services/treks'
import {
  getStaff,
  getAssignedStaff,
  assignStaff,
  removeAssignedStaff,
} from '../services/people'

const treks = ref([])
const searchText = ref('')
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showForm = ref(false)
const editingTrekId = ref(null)

const emptyForm = () => ({
  name: '',
  location: '',
  description: '',
  difficulty: 'Easy',
  duration: 1,
  available_slots: 1,
  start_date: '',
  end_date: '',
})

const form = ref(emptyForm())
const assignmentTrek = ref(null)
const staffMembers = ref([])
const assignedStaff = ref([])
const selectedStaffId = ref('')
const assignmentMessage = ref('')

async function loadTreks() {
  loading.value = true
  errorMessage.value = ''

  try {
    const data = await getTreks(searchText.value)
    treks.value = data.treks || []
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message || 'Unable to fetch treks.'
  } finally {
    loading.value = false
  }
}

function openAddForm() {
  editingTrekId.value = null
  form.value = emptyForm()
  errorMessage.value = ''
  successMessage.value = ''
  showForm.value = true
}

function openEditForm(trek) {
  editingTrekId.value = trek.id

  form.value = {
    name: trek.name,
    location: trek.location,
    description: trek.description || '',
    difficulty: trek.difficulty,
    duration: trek.duration,
    available_slots: trek.available_slots,
    start_date: trek.start_date,
    end_date: trek.end_date,
  }

  errorMessage.value = ''
  successMessage.value = ''
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingTrekId.value = null
  form.value = emptyForm()
}

async function saveTrek() {
  errorMessage.value = ''
  successMessage.value = ''

  if (form.value.end_date < form.value.start_date) {
    errorMessage.value = 'End date cannot be before start date.'
    return
  }

  saving.value = true

  const trekData = {
    ...form.value,
    duration: Number(form.value.duration),
    available_slots: Number(form.value.available_slots),
  }

  try {
    if (editingTrekId.value) {
      await updateTrek(editingTrekId.value, trekData)
      successMessage.value = 'Trek updated successfully.'
    } else {
      await createTrek(trekData)
      successMessage.value = 'Trek created successfully.'
    }

    closeForm()
    await loadTreks()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message || 'Unable to save trek.'
  } finally {
    saving.value = false
  }
}

async function openAssignments(trek) {
  assignmentTrek.value = trek
  assignmentMessage.value = ''
  try {
    const [staffData, assignedData] = await Promise.all([
      getStaff(),
      getAssignedStaff(trek.id),
    ])
    staffMembers.value = (staffData.staff || []).filter(s => s.is_approved && !s.is_blacklisted)
    assignedStaff.value = assignedData.staff || []
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Unable to load staff assignments.'
  }
}

async function addStaffAssignment() {
  if (!selectedStaffId.value || !assignmentTrek.value) return
  try {
    const result = await assignStaff(assignmentTrek.value.id, Number(selectedStaffId.value))
    assignmentMessage.value = result.message
    selectedStaffId.value = ''
    const data = await getAssignedStaff(assignmentTrek.value.id)
    assignedStaff.value = data.staff || []
  } catch (error) {
    assignmentMessage.value = error.response?.data?.message || 'Unable to assign staff.'
  }
}

async function removeStaffAssignment(staffId) {
  if (!confirm('Remove this staff member from the trek?')) return
  try {
    const result = await removeAssignedStaff(assignmentTrek.value.id, staffId)
    assignmentMessage.value = result.message
    const data = await getAssignedStaff(assignmentTrek.value.id)
    assignedStaff.value = data.staff || []
  } catch (error) {
    assignmentMessage.value = error.response?.data?.message || 'Unable to remove staff.'
  }
}

async function removeTrek(trek) {
  const confirmed = window.confirm(
    `Are you sure you want to delete "${trek.name}"?`
  )

  if (!confirmed) return

  errorMessage.value = ''
  successMessage.value = ''

  try {
    const data = await deleteTrek(trek.id)
    successMessage.value = data.message || 'Trek deleted successfully.'
    await loadTreks()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message || 'Unable to delete trek.'
  }
}

onMounted(loadTreks)
</script>

<template>
  <DashboardLayout>
    <div class="container-fluid p-0">

      <div class="d-flex justify-content-between align-items-center mb-4">
        <h3 class="fw-semibold mb-0">Manage Treks</h3>

        <button class="btn btn-primary" @click="openAddForm">
          + Add Trek
        </button>
      </div>

      <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
      </div>

      <div v-if="errorMessage && !showForm" class="alert alert-danger">
        {{ errorMessage }}
      </div>

      <!-- Add / Edit Trek Form -->
      <div v-if="showForm" class="card border shadow-sm mb-4">
        <div class="card-header bg-white py-3">
          <h5 class="mb-0">
            {{ editingTrekId ? 'Edit Trek' : 'Add New Trek' }}
          </h5>
        </div>

        <div class="card-body">
          <div v-if="errorMessage" class="alert alert-danger">
            {{ errorMessage }}
          </div>

          <form @submit.prevent="saveTrek">
            <div class="row g-3">

              <div class="col-md-6">
                <label class="form-label">Trek Name</label>
                <input
                  v-model="form.name"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-6">
                <label class="form-label">Location</label>
                <input
                  v-model="form.location"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-6">
                <label class="form-label">Difficulty</label>
                <select v-model="form.difficulty" class="form-select" required>
                  <option value="Easy">Easy</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Hard">Hard</option>
                </select>
              </div>

              <div class="col-md-3">
                <label class="form-label">Duration (Days)</label>
                <input
                  v-model.number="form.duration"
                  type="number"
                  min="1"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-3">
                <label class="form-label">Available Slots</label>
                <input
                  v-model.number="form.available_slots"
                  type="number"
                  min="0"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-6">
                <label class="form-label">Start Date</label>
                <input
                  v-model="form.start_date"
                  type="date"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-6">
                <label class="form-label">End Date</label>
                <input
                  v-model="form.end_date"
                  type="date"
                  class="form-control"
                  :min="form.start_date"
                  required
                />
              </div>

              <div class="col-12">
                <label class="form-label">Description</label>
                <textarea
                  v-model="form.description"
                  class="form-control"
                  rows="3"
                ></textarea>
              </div>

            </div>

            <div class="mt-4 d-flex gap-2">
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="saving"
              >
                {{ saving ? 'Saving...' : 'Save Trek' }}
              </button>

              <button
                type="button"
                class="btn btn-secondary"
                @click="closeForm"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Search -->
      <div class="card border shadow-sm mb-4">
        <div class="card-body">
          <form class="row g-2" @submit.prevent="loadTreks">
            <div class="col-md-9">
              <input
                v-model="searchText"
                type="text"
                class="form-control"
                placeholder="Search by trek name or location"
              />
            </div>

            <div class="col-md-3 d-flex gap-2">
              <button type="submit" class="btn btn-primary">
                Search
              </button>

              <button
                type="button"
                class="btn btn-outline-secondary"
                @click="searchText = ''; loadTreks()"
              >
                Clear
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Trek Table -->
      <div class="card border shadow-sm">
        <div class="card-header bg-white py-3">
          <h5 class="mb-0 fw-semibold">Trek List</h5>
        </div>

        <div class="card-body">
          <div v-if="loading" class="text-center py-4">
            Loading treks...
          </div>

          <div v-else class="table-responsive">
            <table class="table table-bordered table-hover">
              <thead class="table-light">
                <tr>
                  <th>ID</th>
                  <th>Trek Name</th>
                  <th>Location</th>
                  <th>Difficulty</th>
                  <th>Duration</th>
                  <th>Slots</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="trek in treks" :key="trek.id">
                  <td>{{ trek.id }}</td>
                  <td>{{ trek.name }}</td>
                  <td>{{ trek.location }}</td>
                  <td>{{ trek.difficulty }}</td>
                  <td>{{ trek.duration }} days</td>
                  <td>{{ trek.available_slots }}</td>
                  <td>
                    <span
                      class="badge"
                      :class="{
                        'bg-success': trek.status === 'Open',
                        'bg-warning text-dark': trek.status === 'Full',
                        'bg-secondary': trek.status === 'Closed'
                      }"
                    >
                      {{ trek.status }}
                    </span>
                  </td>
                  <td>
                    <div class="d-flex gap-2">
                      <button
                        class="btn btn-sm btn-outline-primary"
                        @click="openEditForm(trek)"
                      >
                        Edit
                      </button>

                      <button
                        class="btn btn-sm btn-outline-secondary"
                        @click="openAssignments(trek)"
                      >
                        Staff
                      </button>
                      <button
                        class="btn btn-sm btn-outline-danger"
                        @click="removeTrek(trek)"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>

                <tr v-if="treks.length === 0">
                  <td colspan="8" class="text-center text-muted py-4">
                    No treks found.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="assignmentTrek" class="card border shadow-sm mt-4">
        <div class="card-header bg-white d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Staff Assignments – {{ assignmentTrek.name }}</h5>
          <button class="btn btn-sm btn-outline-secondary" @click="assignmentTrek = null">Close</button>
        </div>
        <div class="card-body">
          <div v-if="assignmentMessage" class="alert alert-info py-2">{{ assignmentMessage }}</div>
          <form class="row g-2 mb-3" @submit.prevent="addStaffAssignment">
            <div class="col-md-8">
              <select v-model="selectedStaffId" class="form-select" required>
                <option value="">Select approved staff</option>
                <option v-for="staff in staffMembers" :key="staff.id" :value="String(staff.id)">
                  {{ staff.name }} ({{ staff.email }})
                </option>
              </select>
            </div>
            <div class="col-md-4"><button class="btn btn-primary" :disabled="!selectedStaffId">Assign Staff</button></div>
          </form>
          <div class="table-responsive">
            <table class="table table-bordered table-sm mb-0">
              <thead class="table-light"><tr><th>Name</th><th>Email</th><th>Phone</th><th>Action</th></tr></thead>
              <tbody>
                <tr v-for="staff in assignedStaff" :key="staff.staff_id">
                  <td>{{ staff.name }}</td><td>{{ staff.email }}</td><td>{{ staff.phone || '—' }}</td>
                  <td><button class="btn btn-sm btn-outline-danger" @click="removeStaffAssignment(staff.staff_id)">Remove</button></td>
                </tr>
                <tr v-if="!assignedStaff.length"><td colspan="4" class="text-center text-muted">No staff assigned.</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  </DashboardLayout>
</template>

