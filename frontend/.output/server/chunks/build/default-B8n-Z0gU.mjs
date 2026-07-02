import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { mergeProps, defineComponent, ref, withCtx, createTextVNode, unref, createVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrRenderSlot, ssrRenderAttr, ssrRenderStyle, ssrInterpolate } from 'vue/server-renderer';
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
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<header${ssrRenderAttrs(mergeProps({ class: "fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 md:px-margin-desktop h-20 bg-surface/80 backdrop-blur-[32px] border-b border-white/10 shadow-[0_8px_32px_0_rgba(229,9,20,0.1)]" }, _attrs))}><div class="flex items-center gap-12">`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/",
        class: "font-headline-lg text-headline-lg font-bold text-primary-container tracking-tighter hover:scale-105 transition-all duration-300"
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
      _push(`<nav class="hidden md:flex items-center gap-8">`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "font-label-md text-label-md font-medium text-on-surface-variant hover:text-primary-container hover:scale-105 transition-all duration-300",
        "active-class": "text-primary-container font-bold border-b-2 border-primary-container pb-1"
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
        to: "/ai-discovery",
        class: "font-label-md text-label-md font-medium text-on-surface-variant hover:text-primary-container hover:scale-105 transition-all duration-300",
        "active-class": "text-primary-container font-bold border-b-2 border-primary-container pb-1"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` Kh\xE1m ph\xE1 AI `);
          } else {
            return [
              createTextVNode(" Kh\xE1m ph\xE1 AI ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/showtimes",
        class: "font-label-md text-label-md font-medium text-on-surface-variant hover:text-primary-container hover:scale-105 transition-all duration-300",
        "active-class": "text-primary-container font-bold border-b-2 border-primary-container pb-1"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` L\u1ECBch chi\u1EBFu `);
          } else {
            return [
              createTextVNode(" L\u1ECBch chi\u1EBFu ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/cinemas",
        class: "font-label-md text-label-md font-medium text-on-surface-variant hover:text-primary-container hover:scale-105 transition-all duration-300",
        "active-class": "text-primary-container font-bold border-b-2 border-primary-container pb-1"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` R\u1EA1p phim `);
          } else {
            return [
              createTextVNode(" R\u1EA1p phim ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</nav></div><div class="flex items-center gap-6"><form class="hidden lg:flex items-center bg-surface-container-low px-4 py-2 rounded-full border border-white/5 focus-within:border-primary-container transition-all w-64"><span class="material-symbols-outlined text-on-surface-variant text-[20px]">search</span><input${ssrRenderAttr("value", searchVal.value)} class="bg-transparent border-none focus:ring-0 text-label-md font-label-md placeholder:text-on-surface-variant text-on-surface w-full ml-2 outline-none" placeholder="T\xECm phim, r\u1EA1p..." type="text"></form>`);
      if (unref(isAuthenticated) && unref(currentUser)) {
        _push(`<div class="relative profile-dropdown-wrap"><div class="w-10 h-10 rounded-full overflow-hidden border-2 border-primary-container cursor-pointer hover:scale-105 active:scale-95 transition-all shadow-[0_0_10px_rgba(229,9,20,0.3)]"><img class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDAq3Ng_339WB6mfv_mphK39dGLHMFszhx-AgYKMNAvdIBLaztowKDKDJpjtfA1Hc4jtWnPWz-O1b3Xl4xNoHEyMW1Bf6zs9uyhZGSAweY4AhvQFeh3HyIasFX6W2bT7swfWEEUAQj4wOEWFCuLZR-tYeEf6icRjw1AX3rtxEilO1_XTlXh7u73vegugRIYMB-OuZT8VKVaoS3YbMPNSw30Kyi-OSCHogqRKyoYdEVuLlJOEqJo2UTT1aXKfDROvvaMuTmh2lPPsUsn" alt="Profile"></div>`);
        if (showProfileDropdown.value) {
          _push(`<div class="absolute right-0 mt-3 w-64 rounded-2xl border border-white/10 shadow-2xl p-2 z-50" style="${ssrRenderStyle({ "background": "rgba(18,20,20,0.96)", "backdrop-filter": "blur(12px)" })}"><div class="px-4 py-3 border-b border-white/10 mb-2"><h5 class="text-xs font-bold text-on-surface truncate">${ssrInterpolate(unref(currentUser).name)}</h5><span class="text-[10px] text-on-surface-variant truncate block mt-0.5">${ssrInterpolate(unref(currentUser).email)}</span></div>`);
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
          _push(`<button class="w-full text-left flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs text-red-400 hover:bg-red-500/10 transition-colors border-t border-white/10 mt-2 pt-2"><span class="material-symbols-outlined text-sm">logout</span> \u0110\u0103ng xu\u1EA5t </button></div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div>`);
      } else {
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: "/login",
          class: "bg-primary-container text-on-primary-container font-label-md text-label-md font-bold px-6 py-2.5 rounded-xl hover:scale-105 active:scale-95 transition-all duration-300 shadow-[0_0_20px_-5px_rgba(229,9,20,0.3)]"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(` \u0110\u0103ng nh\u1EADp `);
            } else {
              return [
                createTextVNode(" \u0110\u0103ng nh\u1EADp ")
              ];
            }
          }),
          _: 1
        }, _parent));
      }
      _push(`</div></header>`);
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
  _push(`<footer${ssrRenderAttrs(mergeProps({ class: "w-full px-6 md:px-margin-desktop py-12 flex flex-col md:flex-row justify-between items-center gap-6 bg-surface-container-lowest border-t border-outline-variant/30" }, _attrs))}><div class="flex flex-col items-center md:items-start gap-4">`);
  _push(ssrRenderComponent(_component_NuxtLink, {
    to: "/",
    class: "font-headline-md text-headline-md font-bold text-primary-container"
  }, {
    default: withCtx((_, _push2, _parent2, _scopeId) => {
      if (_push2) {
        _push2(`CineAI`);
      } else {
        return [
          createTextVNode("CineAI")
        ];
      }
    }),
    _: 1
  }, _parent));
  _push(`<p class="font-body-md text-body-md text-on-surface-variant text-center md:text-left max-w-sm"> \xA9 2026 CineAI Studios. Powered by Cinema Intelligence. H\u1EC7 th\u1ED1ng r\u1EA1p chi\u1EBFu phim th\xF4ng minh h\xE0ng \u0111\u1EA7u Vi\u1EC7t Nam. </p></div><div class="flex flex-wrap justify-center gap-6"><a href="#" class="font-label-sm text-label-sm text-on-surface-variant hover:text-primary-container transition-colors">Ch\xEDnh s\xE1ch b\u1EA3o m\u1EADt</a><a href="#" class="font-label-sm text-label-sm text-on-surface-variant hover:text-primary-container transition-colors">\u0110i\u1EC1u kho\u1EA3n d\u1ECBch v\u1EE5</a><a href="#" class="font-label-sm text-label-sm text-on-surface-variant hover:text-primary-container transition-colors">C\xE0i \u0111\u1EB7t Cookie</a><a href="#" class="font-label-sm text-label-sm text-on-surface-variant hover:text-primary-container transition-colors">Trung t\xE2m h\u1ED7 tr\u1EE3</a></div><div class="flex gap-4"><a href="#" class="w-10 h-10 rounded-full bg-surface-container border border-white/10 flex items-center justify-center hover:bg-primary-container group transition-all"><span class="material-symbols-outlined text-on-surface-variant group-hover:text-white text-xl">language</span></a><a href="#" class="w-10 h-10 rounded-full bg-surface-container border border-white/10 flex items-center justify-center hover:bg-primary-container group transition-all"><span class="material-symbols-outlined text-on-surface-variant group-hover:text-white text-xl">smart_toy</span></a></div></footer>`);
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
//# sourceMappingURL=default-B8n-Z0gU.mjs.map
