import { defineStore } from "pinia";
import { ref, computed } from "vue";

export interface CartItem {
  id: string;
  title: string;
  poster: string;
  price: number;
  quantity: number;
  showtime?: string;
}

export interface CartProductPayload {
  id: string;
  title: string;
  poster: string;
  price: number;
  showtime?: string;
}

export const useCartStore = defineStore("cart", () => {
  const items = ref<CartItem[]>([]);

  const totalQuantity = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0);
  });

  const totalPrice = computed(() => {
    return items.value.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0,
    );
  });

  const saveCart = () => {
    if (process.client) {
      localStorage.setItem("cineai_cart", JSON.stringify(items.value));
    }
  };

  if (process.client) {
    const stored = localStorage.getItem("cineai_cart");
    if (stored) {
      try {
        items.value = JSON.parse(stored);
      } catch (e) {
        localStorage.removeItem("cineai_cart");
      }
    }
  }

  function addToCart(product: CartProductPayload, quantity = 1) {
    const existing = items.value.find((item) => item.id === product.id);
    if (existing) {
      existing.quantity += quantity;
      existing.showtime = product.showtime || existing.showtime;
    } else {
      items.value.push({
        id: product.id,
        title: product.title,
        poster: product.poster,
        price: product.price,
        quantity,
        showtime: product.showtime,
      });
    }
    saveCart();
  }

  function removeFromCart(productId: string) {
    items.value = items.value.filter((item) => item.id !== productId);
    saveCart();
  }

  function updateQuantity(productId: string, newQuantity: number) {
    const item = items.value.find((item) => item.id === productId);
    if (!item) return;
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }
    item.quantity = newQuantity;
    saveCart();
  }

  function clearCart() {
    items.value = [];
    saveCart();
  }

  return {
    items,
    totalQuantity,
    totalPrice,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
  };
});
