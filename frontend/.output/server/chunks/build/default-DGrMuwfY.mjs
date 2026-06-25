import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { mergeProps, defineComponent, ref, withCtx, createTextVNode, unref, createVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrRenderSlot, ssrRenderList, ssrInterpolate, ssrRenderAttr } from 'vue/server-renderer';
import { _ as _export_sfc, a as __nuxt_component_2, s as storeToRefs } from './server.mjs';
import { u as useUserStore } from './user-CyBe2ltd.mjs';
import { u as useMoviesStore } from './movies-Csr32Sbi.mjs';
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
import './api-rwjTvGO1.mjs';
import 'axios';

const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "Header",
  __ssrInlineRender: true,
  setup(__props) {
    const userStore = useUserStore();
    useMoviesStore();
    const { currentUser, isAuthenticated } = storeToRefs(userStore);
    const searchVal = ref("");
    const showProfileDropdown = ref(false);
    const showBranchDropdown = ref(false);
    const branches = [
      "CineAI H\xF9ng V\u01B0\u01A1ng",
      "CineAI Sala Q2",
      "CineAI Nguy\u1EC5n Du",
      "CineAI Vincom B\xE0 Tri\u1EC7u",
      "CineAI \u0110\xE0 N\u1EB5ng Plaza"
    ];
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<header${ssrRenderAttrs(mergeProps({ class: "fixed top-0 left-0 w-full z-50 bg-surface/60 backdrop-blur-[32px] border-b border-glass-stroke h-[80px]" }, _attrs))}><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop h-full flex items-center justify-between"><div class="flex items-center gap-8">`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "font-headline-md text-headline-md font-bold text-primary-container hover:scale-105 transition-all"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` CineAI `);
          } else {
            return [
              createTextVNode(" CineAI ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`<nav class="hidden md:flex items-center gap-6 font-body-md text-body-md">`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "text-on-surface-variant hover:text-on-surface transition-colors",
        "active-class": "text-on-surface font-bold border-b-2 border-primary-container pb-1"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` Phim `);
          } else {
            return [
              createTextVNode(" Phim ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "text-on-surface-variant hover:text-on-surface transition-colors"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` L\u1ECBch Chi\u1EBFu `);
          } else {
            return [
              createTextVNode(" L\u1ECBch Chi\u1EBFu ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "text-on-surface-variant hover:text-on-surface transition-colors"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` Kh\xE1m Ph\xE1 AI `);
          } else {
            return [
              createTextVNode(" Kh\xE1m Ph\xE1 AI ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`<div class="relative branch-dropdown-wrap"><button class="text-on-surface-variant hover:text-on-surface transition-colors flex items-center gap-1 font-medium focus:outline-none"> R\u1EA1p Chi\u1EBFu <span class="material-symbols-outlined text-xs select-none">keyboard_arrow_down</span></button>`);
      if (showBranchDropdown.value) {
        _push(`<div class="absolute left-0 mt-3 w-56 rounded-2xl bg-surface border border-glass-stroke shadow-2xl p-2 z-50 glass-panel"><!--[-->`);
        ssrRenderList(branches, (b) => {
          _push(`<a href="#" class="block px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-colors">${ssrInterpolate(b)}</a>`);
        });
        _push(`<!--]--></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div></nav></div><div class="flex items-center gap-6"><form class="relative hidden sm:block"><span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]"> search </span><input${ssrRenderAttr("value", searchVal.value)} class="bg-surface-container-high border border-glass-stroke rounded-full pl-10 pr-4 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-primary-container w-64 text-on-surface placeholder:text-on-surface-variant" placeholder="T\xECm ki\u1EBFm phim..." type="text"></form>`);
      if (unref(isAuthenticated) && unref(currentUser)) {
        _push(`<div class="relative profile-dropdown-wrap"><div class="w-10 h-10 rounded-full overflow-hidden border-2 border-primary-container cursor-pointer hover:scale-105 active:scale-95 transition-all shadow-[0_0_10px_rgba(229,9,20,0.3)]"><img class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDAq3Ng_339WB6mfv_mphK39dGLHMFszhx-AgYKMNAvdIBLaztowKDKDJpjtfA1Hc4jtWnPWz-O1b3Xl4xNoHEyMW1Bf6zs9uyhZGSAweY4AhvQFeh3HyIasFX6W2bT7swfWEEUAQj4wOEWFCuLZR-tYeEf6icRjw1AX3rtxEilO1_XTlXh7u73vegugRIYMB-OuZT8VKVaoS3YbMPNSw30Kyi-OSCHogqRKyoYdEVuLlJOEqJo2UTT1aXKfDROvvaMuTmh2lPPsUsn" alt="User Profile Picture"></div>`);
        if (showProfileDropdown.value) {
          _push(`<div class="absolute right-0 mt-3 w-64 rounded-2xl bg-surface border border-glass-stroke shadow-2xl p-2 z-50 glass-panel"><div class="px-4 py-3 border-b border-glass-stroke/40 mb-2"><h5 class="text-xs font-bold text-on-surface truncate">${ssrInterpolate(unref(currentUser).name)}</h5><span class="text-[10px] text-on-surface-variant truncate block mt-0.5">${ssrInterpolate(unref(currentUser).email)}</span></div>`);
          if (unref(currentUser).role === "customer") {
            _push(ssrRenderComponent(_component_NuxtLink, {
              to: "/profile/tickets",
              onClick: ($event) => showProfileDropdown.value = false,
              class: "flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-colors"
            }, {
              default: withCtx((_, _push2, _parent2, _scopeId) => {
                if (_push2) {
                  _push2(`<span class="material-symbols-outlined text-sm"${_scopeId}>confirmation_number</span> V\xE9 c\u1EE7a t\xF4i `);
                } else {
                  return [
                    createVNode("span", { class: "material-symbols-outlined text-sm" }, "confirmation_number"),
                    createTextVNode(" V\xE9 c\u1EE7a t\xF4i ")
                  ];
                }
              }),
              _: 1
            }, _parent));
          } else {
            _push(`<!---->`);
          }
          if (unref(currentUser).role === "admin") {
            _push(ssrRenderComponent(_component_NuxtLink, {
              to: "/admin/dashboard",
              onClick: ($event) => showProfileDropdown.value = false,
              class: "flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-colors"
            }, {
              default: withCtx((_, _push2, _parent2, _scopeId) => {
                if (_push2) {
                  _push2(`<span class="material-symbols-outlined text-sm"${_scopeId}>dashboard</span> Qu\u1EA3n tr\u1ECB h\u1EC7 th\u1ED1ng `);
                } else {
                  return [
                    createVNode("span", { class: "material-symbols-outlined text-sm" }, "dashboard"),
                    createTextVNode(" Qu\u1EA3n tr\u1ECB h\u1EC7 th\u1ED1ng ")
                  ];
                }
              }),
              _: 1
            }, _parent));
          } else {
            _push(`<!---->`);
          }
          if (unref(currentUser).role === "branch-admin") {
            _push(ssrRenderComponent(_component_NuxtLink, {
              to: "/branch-admin/dashboard",
              onClick: ($event) => showProfileDropdown.value = false,
              class: "flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-colors"
            }, {
              default: withCtx((_, _push2, _parent2, _scopeId) => {
                if (_push2) {
                  _push2(`<span class="material-symbols-outlined text-sm"${_scopeId}>storefront</span> Qu\u1EA3n l\xFD chi nh\xE1nh `);
                } else {
                  return [
                    createVNode("span", { class: "material-symbols-outlined text-sm" }, "storefront"),
                    createTextVNode(" Qu\u1EA3n l\xFD chi nh\xE1nh ")
                  ];
                }
              }),
              _: 1
            }, _parent));
          } else {
            _push(`<!---->`);
          }
          _push(`<button class="w-full text-left flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs text-red-400 hover:bg-red-500/10 transition-colors border-t border-glass-stroke/40 mt-2 pt-2"><span class="material-symbols-outlined text-sm">logout</span> \u0110\u0103ng xu\u1EA5t </button></div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div>`);
      } else {
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: "/login",
          class: "bg-primary-container text-on-primary-container px-6 py-2.5 rounded-xl font-label-md text-label-md font-bold hover:scale-105 active:scale-95 transition-all ai-glow"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(` \u0110\u0103ng Nh\u1EADp `);
            } else {
              return [
                createTextVNode(" \u0110\u0103ng Nh\u1EADp ")
              ];
            }
          }),
          _: 1
        }, _parent));
      }
      _push(`</div></div></header>`);
    };
  }
});
const _sfc_setup$2 = _sfc_main$2.setup;
_sfc_main$2.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/Header.vue");
  return _sfc_setup$2 ? _sfc_setup$2(props, ctx) : void 0;
};
const _sfc_main$1 = {};
function _sfc_ssrRender$1(_ctx, _push, _parent, _attrs) {
  const _component_NuxtLink = __nuxt_component_0;
  _push(`<footer${ssrRenderAttrs(mergeProps({ class: "border-t border-glass-stroke bg-surface-container-lowest/80 backdrop-blur-md py-12 mt-auto" }, _attrs))}><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop flex flex-col md:flex-row justify-between items-center gap-6"><div><h3 class="font-headline-md text-headline-md font-bold text-primary-container">CineAI</h3><p class="text-sm text-on-surface-variant mt-2 max-w-sm"> Tr\u1EA3i nghi\u1EC7m \u0111\u1EB7t v\xE9 xem phim th\u1EBF h\u1EC7 m\u1EDBi h\u1ED7 tr\u1EE3 b\u1EDFi Tr\xED Tu\u1EC7 Nh\xE2n T\u1EA1o. Nhanh ch\xF3ng, ti\u1EC7n l\u1EE3i, v\xE0 t\u1ED1i \u01B0u h\xF3a cho b\u1EA1n. </p></div><div class="flex gap-8 text-sm text-on-surface-variant font-medium">`);
  _push(ssrRenderComponent(_component_NuxtLink, {
    to: "/movies",
    class: "hover:text-primary transition-colors"
  }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`Danh s\xE1ch phim`);
      } else {
        return [
          createTextVNode("Danh s\xE1ch phim")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`<a href="#" class="hover:text-primary transition-colors">\u0110i\u1EC1u kho\u1EA3n d\u1ECBch v\u1EE5</a><a href="#" class="hover:text-primary transition-colors">Ch\xEDnh s\xE1ch b\u1EA3o m\u1EADt</a><a href="#" class="hover:text-primary transition-colors">H\u1ED7 tr\u1EE3 kh\xE1ch h\xE0ng</a></div></div><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop text-center text-xs text-on-surface-variant mt-8 border-t border-glass-stroke/50 pt-6"> \xA9 2026 CineAI System. Designed for Software Engineering Project. All rights reserved. </div></footer>`);
}
const _sfc_setup$1 = _sfc_main$1.setup;
_sfc_main$1.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/Footer.vue");
  return _sfc_setup$1 ? _sfc_setup$1(props, ctx) : void 0;
};
const __nuxt_component_1 = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["ssrRender", _sfc_ssrRender$1]]);
const _sfc_main = {};
function _sfc_ssrRender(_ctx, _push, _parent, _attrs) {
  const _component_Header = _sfc_main$2;
  const _component_Footer = __nuxt_component_1;
  const _component_ClientOnly = __nuxt_component_2;
  _push(`<div${ssrRenderAttrs(mergeProps({ class: "flex flex-col min-h-screen bg-background text-on-surface" }, _attrs))}>`);
  _push(ssrRenderComponent(_component_Header, null, null, _parent));
  _push(`<main class="flex-grow pt-[80px]">`);
  ssrRenderSlot(_ctx.$slots, "default", {}, null, _push, _parent);
  _push(`</main>`);
  _push(ssrRenderComponent(_component_Footer, null, null, _parent));
  _push(ssrRenderComponent(_component_ClientOnly, null, {}, _parent));
  _push(`</div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("layouts/default.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const _default = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);

export { _default as default };
//# sourceMappingURL=default-DGrMuwfY.mjs.map
