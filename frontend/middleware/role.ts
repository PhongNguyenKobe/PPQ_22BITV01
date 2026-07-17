import { defineNuxtRouteMiddleware, navigateTo } from "#app";
import { useUserStore } from "~/store/user";

export default defineNuxtRouteMiddleware((to) => {
  const userStore = useUserStore();
  const { currentUser, isAuthenticated } = userStore;

  const requiredRole = to.meta.requiredRole as string | undefined;
  const fallbackRouteByRole: Record<string, string> = {
    customer: "/movies",
    admin: "/admin/dashboard",
    "branch-admin": "/branch-admin/dashboard",
  };

  if (!isAuthenticated || !currentUser) {
    return navigateTo("/login");
  }

  if (!requiredRole) {
    return;
  }

  if (currentUser.role !== requiredRole) {
    const fallbackRoute = fallbackRouteByRole[currentUser.role] || "/login";
    return navigateTo(fallbackRoute);
  }
});
