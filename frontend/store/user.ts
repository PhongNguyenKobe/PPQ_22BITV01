import { defineStore } from "pinia";
import { ref } from "vue";
import { authService, setAuthToken, type UserProfile } from "~/services/api";

export const useUserStore = defineStore("user", () => {
  // Pre-configured mock accounts:
  // 1. Customer: customer@gmail.com / customer123
  // 2. Admin: admin@cineai.vn / admin123
  // 3. Branch Admin: branch@cineai.vn / branch123
  const registeredUsers = ref<UserProfile[]>([
    {
      id: "u1",
      name: "Nguyễn Đăng Khách",
      email: "customer@gmail.com",
      role: "customer",
    },
    { id: "u2", name: "Admin CineAI", email: "admin@cineai.vn", role: "admin" },
    {
      id: "u3",
      name: "Sala Branch Manager",
      email: "branch@cineai.vn",
      role: "branch-admin",
      branchId: "b1",
    },
  ]);

  const currentUser = ref<UserProfile | null>(null);
  const isAuthenticated = ref(false);
  const authToken = ref<string | null>(null);

  // Initialize from client-side localStorage if available
  if (process.client) {
    const saved = localStorage.getItem("cineai_user");
    const savedToken = localStorage.getItem("cineai_token");

    if (savedToken) {
      authToken.value = savedToken;
      setAuthToken(savedToken);
    }

    if (saved) {
      try {
        currentUser.value = JSON.parse(saved);
        isAuthenticated.value = true;
      } catch (e) {
        localStorage.removeItem("cineai_user");
      }
    }
  }

  async function login(
    email: string,
    role: "customer" | "admin" | "branch-admin",
    password?: string,
  ): Promise<boolean> {
    const defaultPasswordByRole: Record<
      "customer" | "admin" | "branch-admin",
      string
    > = {
      customer: "customer123",
      admin: "admin123",
      "branch-admin": "branch123",
    };

    const resolvedPassword = password || defaultPasswordByRole[role];

    try {
      const backendUser = await authService.login(email, resolvedPassword);
      if (backendUser.role !== role) {
        throw new Error("Role mismatch");
      }

      const mappedUser: UserProfile = {
        id: `u-${Date.now()}`,
        name:
          backendUser.email === "admin@cineai.vn"
            ? "Admin CineAI"
            : backendUser.email === "branch@cineai.vn"
              ? "Sala Branch Manager"
              : "Khách hàng CineAI",
        email: backendUser.email,
        role: backendUser.role,
      };

      currentUser.value = mappedUser;
      isAuthenticated.value = true;
      authToken.value = backendUser.access_token;

      if (process.client) {
        localStorage.setItem("cineai_user", JSON.stringify(mappedUser));
        localStorage.setItem("cineai_token", backendUser.access_token);
      }

      setAuthToken(backendUser.access_token);
      return true;
    } catch (error) {
      const matched = registeredUsers.value.find(
        (u) => u.email === email && u.role === role,
      );
      if (matched) {
        currentUser.value = matched;
        isAuthenticated.value = true;
        authToken.value = null;
        if (process.client) {
          localStorage.setItem("cineai_user", JSON.stringify(matched));
          localStorage.removeItem("cineai_token");
        }
        setAuthToken(null);
        return true;
      }
      return false;
    }
  }

  function register(name: string, email: string): boolean {
    const exists = registeredUsers.value.some((u) => u.email === email);
    if (exists) return false;

    const newUser: UserProfile = {
      id: `u-${Date.now()}`,
      name,
      email,
      role: "customer",
    };

    registeredUsers.value.push(newUser);
    currentUser.value = newUser;
    isAuthenticated.value = true;
    if (process.client) {
      localStorage.setItem("cineai_user", JSON.stringify(newUser));
    }
    return true;
  }

  function logout() {
    currentUser.value = null;
    isAuthenticated.value = false;
    authToken.value = null;
    if (process.client) {
      localStorage.removeItem("cineai_user");
      localStorage.removeItem("cineai_token");
    }
    setAuthToken(null);
  }

  return {
    currentUser,
    isAuthenticated,
    authToken,
    registeredUsers,
    login,
    register,
    logout,
  };
});
