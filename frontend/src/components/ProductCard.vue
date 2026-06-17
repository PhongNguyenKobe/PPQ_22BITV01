<script setup lang="ts">
defineProps<{
  id: number
  name: string
  price: number
  category: string
  imageUrl: string
  description: string
}>()
</script>

<template>
  <div class="product-card">
    <div class="product-card__poster">
      <img :src="imageUrl" :alt="name" />
      <div class="product-card__fade"></div>
      <span class="product-card__badge">{{ category }}</span>
    </div>

    <div class="product-card__content">
      <p class="product-card__desc">{{ description }}</p>
      <h3>{{ name }}</h3>
      <div class="product-card__actions">
        <button class="button button--primary button--block">{{ price }}k – Đặt ngay</button>
        <button class="button button--ghost button--block">Chi tiết</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-card {
  position: relative;
  width: 220px;
  height: 300px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
}

/* Ảnh nền full card */
.product-card__poster {
  position: absolute;
  inset: 0;
}

.product-card__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.product-card:hover .product-card__poster img {
  transform: scale(1.05);
}

/* Gradient tối dần từ dưới lên */
.product-card__fade {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.92) 0%,
    rgba(0, 0, 0, 0.4) 50%,
    rgba(0, 0, 0, 0.1) 100%
  );
}

/* Badge category góc trên trái */
.product-card__badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  backdrop-filter: blur(4px);
}

/* Nội dung phía dưới */
.product-card__content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 12px;
  color: #fff;
}

.product-card__content h3 {
  margin: 0 0 8px;
  font-size: 0.95rem;
  line-height: 1.3;
}

/* Mô tả + nút ẩn ban đầu, hiện khi hover */
.product-card__desc,
.product-card__actions {
  overflow: hidden;
  max-height: 0;
  opacity: 0;
  transition: max-height 0.35s ease, opacity 0.3s ease;
}

.product-card:hover .product-card__desc,
.product-card:hover .product-card__actions {
  max-height: 120px;
  opacity: 1;
}

.product-card__desc {
  font-size: 0.8rem;
  color: rgba(255,255,255,0.75);
  margin: 0 0 8px;
  line-height: 1.4;
}

.product-card__actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
</style>