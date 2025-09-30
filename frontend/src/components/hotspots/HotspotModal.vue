&lt;template&gt;
  &lt;div v-if="show" class="modal-overlay" @click.self="handleCancel"&gt;
    &lt;div class="modal-content"&gt;
      &lt;div class="modal-header"&gt;
        &lt;h3 class="modal-title"&gt;{{ mode === 'create' ? '新建热点' : '编辑热点' }}&lt;/h3&gt;
        &lt;button @click="handleCancel" class="modal-close"&gt;×&lt;/button&gt;
      &lt;/div&gt;
      &lt;div class="modal-body"&gt;
        &lt;form @submit.prevent="handleSubmit"&gt;
          &lt;div class="form-group"&gt;
            &lt;label for="name"&gt;热点名称&lt;/label&gt;
            &lt;input 
              id="name"
              v-model="formData.name" 
              type="text" 
              required 
              class="form-control"
            &gt;
          &lt;/div&gt;
          &lt;div class="form-group"&gt;
            &lt;label for="mac"&gt;MAC地址&lt;/label&gt;
            &lt;input 
              id="mac"
              v-model="formData.mac" 
              type="text" 
              required 
              class="form-control"
            &gt;
          &lt;/div&gt;
          &lt;div class="form-group"&gt;
            &lt;label for="type"&gt;热点类型&lt;/label&gt;
            &lt;input 
              id="type"
              v-model="formData.type" 
              type="text" 
              class="form-control"
            &gt;
          &lt;/div&gt;
        &lt;/form&gt;
      &lt;/div&gt;
      &lt;div class="modal-footer"&gt;
        &lt;button @click="handleCancel" class="btn btn-secondary"&gt;取消&lt;/button&gt;
        &lt;button @click="handleSubmit" class="btn btn-primary"&gt;
          {{ mode === 'create' ? '创建' : '更新' }}
        &lt;/button&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  &lt;/div&gt;
&lt;/template&gt;

&lt;script setup lang="ts"&gt;
import { ref, reactive, watch } from 'vue'
import type { Hotspot, HotspotCreate, HotspotUpdate } from '@/types/hotspot'

interface Props {
  show: boolean
  mode: 'create' | 'edit'
  hotspot?: Hotspot | null
}

interface Emits {
  (e: 'submit', data: HotspotCreate | HotspotUpdate): void
  (e: 'cancel'): void
}

const props = defineProps&lt;Props&gt;()
const emit = defineEmits&lt;Emits&gt;()

const formData = reactive({
  name: '',
  mac: '',
  type: '',
  geocode: '',
  owner: '',
  email_owner: '',
  manager: '',
  email_manager: '',
  address: '',
  phone1: '',
  phone2: '',
  company: '',
  companywebsite: '',
  companyemail: '',
  companycontact: '',
  companyphone: ''
})

watch(() => props.hotspot, (newHotspot) => {
  if (newHotspot) {
    Object.assign(formData, newHotspot)
  } else {
    // Reset form for create mode
    Object.keys(formData).forEach(key => {
      (formData as any)[key] = ''
    })
  }
}, { immediate: true })

const handleSubmit = () => {
  emit('submit', formData)
}

const handleCancel = () => {
  emit('cancel')
}
&lt;/script&gt;

&lt;style scoped&gt;
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.modal-body {
  padding: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.875rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}
&lt;/style&gt;