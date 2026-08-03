<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useUserStore } from '~/store/user'
import { comboService, type CinemaCombo } from '~/services/api'

const { currentUser } = storeToRefs(useUserStore())
const rows = ref<CinemaCombo[]>([])
const loading = ref(false)
const editing = ref<CinemaCombo | null>(null)
const form = reactive({ name: '', description: '', price: 59000, image_url: '', stock_quantity: null as number | null, is_active: true })
async function load(){ loading.value=true; try{rows.value=await comboService.getManage()}finally{loading.value=false} }
async function importStarter(){ loading.value=true; try{rows.value=await comboService.importStarter()}finally{loading.value=false} }
onMounted(load)
function reset(){editing.value=null; Object.assign(form,{name:'',description:'',price:59000,image_url:'',stock_quantity:null,is_active:true})}
function edit(row:CinemaCombo){editing.value=row; Object.assign(form,{name:row.name,description:row.description||'',price:Number(row.price),image_url:row.image_url||'',stock_quantity:row.stock_quantity,is_active:row.is_active})}
async function save(){
  const branchId=currentUser.value?.branchId || editing.value?.branch_id
  if(!branchId) return
  const payload={branch_id:branchId,...form,description:form.description||null,image_url:form.image_url||null}
  if(editing.value) await comboService.update(editing.value.id,payload); else await comboService.create(payload)
  reset(); await load()
}
</script>
<template>
  <div class="grid gap-5 xl:grid-cols-[380px_1fr]">
    <form class="panel space-y-4 p-5" @submit.prevent="save">
      <h2 class="text-lg font-black text-white">{{ editing ? 'Chỉnh sửa combo' : 'Tạo combo mới' }}</h2>
      <input v-model="form.name" required minlength="2" placeholder="Tên combo" class="admin-input">
      <textarea v-model="form.description" rows="3" placeholder="Mô tả thành phần" class="admin-input"></textarea>
      <input v-model.number="form.price" required min="1000" type="number" placeholder="Giá bán" class="admin-input">
      <input v-model="form.image_url" placeholder="URL hình ảnh (không bắt buộc)" class="admin-input">
      <input v-model.number="form.stock_quantity" min="0" type="number" placeholder="Tồn kho (để trống = không giới hạn)" class="admin-input">
      <label class="flex gap-2 text-sm text-gray-300"><input v-model="form.is_active" type="checkbox"> Đang mở bán</label>
      <div class="flex gap-2"><button class="flex-1 rounded-xl bg-red-600 px-4 py-3 font-bold text-white">{{ editing?'Lưu thay đổi':'Tạo combo' }}</button><button v-if="editing" type="button" class="rounded-xl border border-white/10 px-4" @click="reset">Hủy</button></div>
    </form>
    <div class="panel overflow-hidden"><div class="flex items-center justify-between gap-4 border-b border-white/10 p-5"><div><h2 class="font-black text-white">Combo của chi nhánh</h2><p class="text-xs text-gray-400">Dữ liệu này hiển thị trực tiếp cho khách khi đặt vé.</p></div><button class="rounded-xl border border-orange-400/30 bg-orange-400/10 px-4 py-2 text-xs font-bold text-orange-200" :disabled="loading" @click="importStarter">Thêm nhanh 4 combo mẫu</button></div>
      <div v-if="loading" class="p-8 text-center text-gray-400">Đang tải...</div><div v-else class="divide-y divide-white/5">
        <div v-for="row in rows" :key="row.id" class="flex items-center justify-between gap-4 p-5"><div><div class="flex gap-2"><strong class="text-white">{{row.name}}</strong><span :class="row.is_active?'text-emerald-300':'text-gray-500'" class="text-xs">{{row.is_active?'Đang bán':'Đã ẩn'}}</span></div><p class="mt-1 text-sm text-gray-400">{{Number(row.price).toLocaleString('vi-VN')}}đ · Tồn: {{row.stock_quantity ?? 'Không giới hạn'}}</p></div><button class="text-sm font-bold text-sky-300" @click="edit(row)">Chỉnh sửa</button></div>
        <p v-if="!rows.length" class="p-10 text-center text-gray-400">Chưa có combo nào.</p>
      </div>
    </div>
  </div>
</template>
<style scoped>.admin-input{width:100%;border:1px solid rgba(255,255,255,.1);border-radius:.75rem;background:#101212;padding:.75rem;color:white;outline:none}.panel{border:1px solid rgba(255,255,255,.08);border-radius:1rem;background:#1a1c1c}</style>
