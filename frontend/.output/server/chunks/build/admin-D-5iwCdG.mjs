import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, mergeProps, withCtx, createVNode, createTextVNode, unref, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrInterpolate, ssrRenderSlot } from 'vue/server-renderer';
import { s as storeToRefs } from './server.mjs';
import { u as useUserStore } from './user-CyBe2ltd.mjs';
import '../_/nitro.mjs';
import 'node:http';
import 'node:https';
import 'node:events';
import 'node:buffer';
import 'node:fs';
import 'node:path';
import 'node:crypto';
import 'node:url';
import '../routes/renderer.mjs';
import 'vue-bundle-renderer/runtime';
import 'unhead/server';
import 'devalue';
import 'unhead/utils';
import 'unhead/plugins';
import 'vue-router';

const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "admin",
  __ssrInlineRender: true,
  setup(__props) {
    const userStore = useUserStore();
    const { currentUser, isAuthenticated } = storeToRefs(userStore);
    return (_ctx, _push, _parent, _attrs) => {
      var _a, _b, _c, _d, _e, _f, _g;
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "flex h-screen bg-[#0d0e0f] text-on-surface" }, _attrs))}><aside class="w-64 bg-surface border-r border-glass-stroke flex flex-col justify-between"><div><div class="h-20 flex items-center px-6 border-b border-glass-stroke">`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "font-headline-md text-xl font-bold text-primary-container flex items-center gap-2"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`<span class="material-symbols-outlined"${_scopeId}>shield</span> CineAI Portal `);
          } else {
            return [
              createVNode("span", { class: "material-symbols-outlined" }, "shield"),
              createTextVNode(" CineAI Portal ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div><nav class="p-4 space-y-2"><div class="px-3 mb-2 text-xs font-bold uppercase tracking-wider text-on-surface-variant">${ssrInterpolate(((_a = unref(currentUser)) == null ? void 0 : _a.role) === "admin" ? "Qu\u1EA3n tr\u1ECB h\u1EC7 th\u1ED1ng" : "Qu\u1EA3n l\xFD chi nh\xE1nh")}</div>`);
      if (((_b = unref(currentUser)) == null ? void 0 : _b.role) === "admin") {
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: "/admin/dashboard",
          class: "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-sm transition-colors text-on-surface-variant hover:text-on-surface",
          "active-class": "bg-primary-container/10 border border-primary-container/20 !text-primary-container font-semibold"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`<span class="material-symbols-outlined text-lg"${_scopeId}>dashboard</span> B\u1EA3ng \u0111i\u1EC1u khi\u1EC3n `);
            } else {
              return [
                createVNode("span", { class: "material-symbols-outlined text-lg" }, "dashboard"),
                createTextVNode(" B\u1EA3ng \u0111i\u1EC1u khi\u1EC3n ")
              ];
            }
          }),
          _: 1
        }, _parent));
      } else {
        _push(`<!---->`);
      }
      if (((_c = unref(currentUser)) == null ? void 0 : _c.role) === "branch-admin") {
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: "/branch-admin/dashboard",
          class: "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-sm transition-colors text-on-surface-variant hover:text-on-surface",
          "active-class": "bg-purple-950/20 border border-purple-500/30 !text-purple-400 font-semibold"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`<span class="material-symbols-outlined text-lg"${_scopeId}>storefront</span> B\u1EA3ng chi nh\xE1nh `);
            } else {
              return [
                createVNode("span", { class: "material-symbols-outlined text-lg" }, "storefront"),
                createTextVNode(" B\u1EA3ng chi nh\xE1nh ")
              ];
            }
          }),
          _: 1
        }, _parent));
      } else {
        _push(`<!---->`);
      }
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-sm transition-colors text-on-surface-variant hover:text-on-surface"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`<span class="material-symbols-outlined text-lg"${_scopeId}>movie</span> Trang b\xE1n v\xE9 `);
          } else {
            return [
              createVNode("span", { class: "material-symbols-outlined text-lg" }, "movie"),
              createTextVNode(" Trang b\xE1n v\xE9 ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</nav></div><div class="p-4 border-t border-glass-stroke bg-surface-container-low/40"><div class="flex items-center gap-3 mb-4"><div class="w-10 h-10 rounded-full bg-surface-container-high border border-glass-stroke flex items-center justify-center font-bold text-sm text-primary">${ssrInterpolate((_d = unref(currentUser)) == null ? void 0 : _d.name.substring(0, 2).toUpperCase())}</div><div class="flex-1 min-w-0"><h5 class="text-sm font-semibold truncate text-on-surface">${ssrInterpolate((_e = unref(currentUser)) == null ? void 0 : _e.name)}</h5><span class="text-xs text-on-surface-variant capitalize">${ssrInterpolate((_f = unref(currentUser)) == null ? void 0 : _f.role)}</span></div></div><button class="w-full bg-red-950/20 border border-red-500/20 text-red-400 hover:bg-red-500/10 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2"><span class="material-symbols-outlined text-sm">logout</span> \u0110\u0103ng xu\u1EA5t </button></div></aside><div class="flex-1 flex flex-col overflow-hidden"><header class="h-20 bg-surface border-b border-glass-stroke flex items-center justify-between px-8"><div><h2 class="text-lg font-bold text-on-surface flex items-center gap-2">${ssrInterpolate(((_g = unref(currentUser)) == null ? void 0 : _g.role) === "admin" ? "H\u1EC7 th\u1ED1ng Qu\u1EA3n tr\u1ECB T\u1ED5ng" : "H\u1EC7 th\u1ED1ng Qu\u1EA3n tr\u1ECB Chi nh\xE1nh")}</h2></div><div class="flex items-center gap-4">`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "text-xs font-bold bg-white/5 border border-glass-stroke hover:bg-white/10 px-4 py-2 rounded-xl text-on-surface flex items-center gap-2"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`<span class="material-symbols-outlined text-sm"${_scopeId}>home</span> Quay v\u1EC1 trang b\xE1n v\xE9 `);
          } else {
            return [
              createVNode("span", { class: "material-symbols-outlined text-sm" }, "home"),
              createTextVNode(" Quay v\u1EC1 trang b\xE1n v\xE9 ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div></header><main class="flex-1 overflow-y-auto p-8">`);
      ssrRenderSlot(_ctx.$slots, "default", {}, null, _push, _parent);
      _push(`</main></div></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("layouts/admin.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=admin-D-5iwCdG.mjs.map
