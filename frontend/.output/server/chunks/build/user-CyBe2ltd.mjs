import { d as defineStore } from './server.mjs';
import { ref } from 'vue';

const useUserStore = defineStore("user", () => {
  const registeredUsers = ref([
    { id: "u1", name: "Nguy\u1EC5n \u0110\u0103ng Kh\xE1ch", email: "customer@gmail.com", role: "customer" },
    { id: "u2", name: "Admin CineAI", email: "admin@cineai.vn", role: "admin" },
    { id: "u3", name: "Sala Branch Manager", email: "branch@cineai.vn", role: "branch-admin", branchId: "b1" }
  ]);
  const currentUser = ref(null);
  const isAuthenticated = ref(false);
  function login(email, role) {
    const matched = registeredUsers.value.find((u) => u.email === email && u.role === role);
    if (matched) {
      currentUser.value = matched;
      isAuthenticated.value = true;
      return true;
    }
    return false;
  }
  function register(name, email) {
    const exists = registeredUsers.value.some((u) => u.email === email);
    if (exists) return false;
    const newUser = {
      id: `u-${Date.now()}`,
      name,
      email,
      role: "customer"
    };
    registeredUsers.value.push(newUser);
    currentUser.value = newUser;
    isAuthenticated.value = true;
    return true;
  }
  function logout() {
    currentUser.value = null;
    isAuthenticated.value = false;
  }
  return {
    currentUser,
    isAuthenticated,
    registeredUsers,
    login,
    register,
    logout
  };
});

export { useUserStore as u };
//# sourceMappingURL=user-CyBe2ltd.mjs.map
