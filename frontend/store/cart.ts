import { defineStore } from "pinia";

interface CartItem {
  id: number;
  name: string;
  price: number;
  imageUrl: string;
  qty: number;
}

export const useCartStore = defineStore("cart", {
  state: () => ({ items: [] as CartItem[] }),
  getters: {
    total: (state) => state.items.reduce((sum, i) => sum + i.price * i.qty, 0),
  },
  actions: {
    addItem(product: {
      id: number;
      name: string;
      price: number;
      imageUrl: string;
    }) {
      const existing = this.items.find((i) => i.id === product.id);
      existing ? existing.qty++ : this.items.push({ ...product, qty: 1 });
    },
    removeItem(id: number) {
      this.items = this.items.filter((i) => i.id !== id);
    },
    clearCart() {
      this.items = [];
    },
  },
});
