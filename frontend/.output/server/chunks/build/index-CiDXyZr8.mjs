import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { _ as _sfc_main$1 } from './MovieCard-CFTDOcJL.mjs';
import { defineComponent, withCtx, createVNode, createTextVNode, unref, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrRenderList, ssrInterpolate } from 'vue/server-renderer';
import { s as storeToRefs } from './server.mjs';
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

const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "index",
  __ssrInlineRender: true,
  setup(__props) {
    const moviesStore = useMoviesStore();
    const { movies } = storeToRefs(moviesStore);
    const highlights = [
      {
        icon: "chair",
        title: "\u0110\u1EB7t v\xE9 tr\u1EF1c quan",
        description: "Ch\u1ECDn gh\u1EBF ng\u1ED3i th\xF4ng minh theo th\u1EDDi gian th\u1EF1c t\u1EA1i c\xE1c chi nh\xE1nh v\u1EDBi \u0111\u1ED9 ch\xEDnh x\xE1c cao."
      },
      {
        icon: "smart_toy",
        title: "Tr\u1EE3 l\xFD \u1EA3o AI",
        description: "T\xECm ki\u1EBFm b\u1EB1ng ng\xF4n ng\u1EEF t\u1EF1 nhi\xEAn, g\u1EE3i \xFD phim c\xE1 nh\xE2n h\xF3a theo gu \u0111i\u1EC7n \u1EA3nh."
      },
      {
        icon: "payments",
        title: "Thanh to\xE1n \u0111a k\xEAnh",
        description: "H\u1ED7 tr\u1EE3 Momo, VNPAY, th\u1EBB ng\xE2n h\xE0ng qu\xE9t m\xE3 QR an to\xE0n, b\u1EA3o m\u1EADt tuy\u1EC7t \u0111\u1ED1i."
      },
      {
        icon: "qr_code",
        title: "V\xE9 \u0111i\u1EC7n t\u1EED th\xF4ng minh",
        description: "L\u01B0u tr\u1EEF v\xE9 s\u1ED1 h\xF3a ngay tr\xEAn t\xE0i kho\u1EA3n, check-in qu\xE9t m\xE3 QR nhanh t\u1EA1i r\u1EA1p."
      }
    ];
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      const _component_MovieCard = _sfc_main$1;
      _push(`<div${ssrRenderAttrs(_attrs)}><header class="relative w-full min-h-[85vh] flex items-center pt-8 overflow-hidden"><div class="absolute inset-0 z-0"><div class="w-full h-full bg-[url(&#39;https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&amp;w=2070&amp;auto=format&amp;fit=crop&#39;)] bg-cover bg-center bg-no-repeat"></div><div class="absolute inset-0 bg-background/85 backdrop-blur-[2px]"></div><div class="absolute inset-0 gradient-fade-bottom"></div></div><div class="relative z-10 w-full max-w-container-max mx-auto px-6 md:px-margin-desktop py-16"><div class="max-w-4xl relative"><div class="absolute -top-24 -left-24 w-96 h-96 bg-primary-container/10 rounded-full blur-[120px] animate-pulse pointer-events-none z-0"></div><div class="absolute top-1/2 -right-48 w-64 h-64 bg-secondary-container/15 rounded-full blur-[100px] pointer-events-none z-0"></div><div class="relative z-10"><div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-container/10 border border-primary-container/20 mb-8 backdrop-blur-xl"><span class="material-symbols-outlined text-primary-container text-[20px] animate-pulse">psychology</span><span class="text-[11px] font-bold tracking-wider uppercase text-primary-container">Tr\xED tu\u1EC7 \u0111i\u1EC7n \u1EA3nh th\u1EBF h\u1EC7 m\u1EDBi</span></div><h1 class="font-headline-xl text-[40px] leading-[48px] md:text-[68px] md:leading-[76px] font-bold mb-6 text-on-surface tracking-tight"> \u0110\u1EB7t v\xE9 xem phim <br>th\xF4ng minh v\u1EDBi <span class="relative inline-block ml-2"><span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-container to-[#ffb4aa] drop-shadow-[0_0_15px_rgba(229,9,20,0.6)]">AI</span><span class="absolute -inset-1 bg-primary-container/20 blur-xl rounded-full"></span></span></h1><p class="font-body-lg text-body-lg text-on-surface-variant mb-10 max-w-2xl leading-relaxed"> Tr\u1EA3i nghi\u1EC7m t\u01B0\u01A1ng lai c\u1EE7a \u0111i\u1EC7n \u1EA3nh c\xF9ng CineAI. T\xECm ki\u1EBFm l\u1ECBch chi\u1EBFu, \u0111\u1EB7t gh\u1EBF th\xF4ng minh v\xE0 nh\u1EADn \u0111\u1EC1 xu\u1EA5t c\xE1c t\xE1c ph\u1EA9m phim ph\xF9 h\u1EE3p v\u1EDBi gu c\xE1 nh\xE2n ch\u1EC9 trong nh\xE1y m\u1EAFt. </p><div class="flex flex-col sm:flex-row gap-4">`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "group relative bg-primary-container text-on-primary-container font-label-md text-label-md px-10 py-4.5 rounded-xl flex items-center justify-center gap-3 red-glow-hover transition-all duration-300 overflow-hidden"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`<span class="relative z-10"${_scopeId}>\u0110\u1EB7t V\xE9 Ngay</span><span class="material-symbols-outlined text-[20px] relative z-10 group-hover:translate-x-1 transition-transform"${_scopeId}>arrow_forward</span>`);
          } else {
            return [
              createVNode("span", { class: "relative z-10" }, "\u0110\u1EB7t V\xE9 Ngay"),
              createVNode("span", { class: "material-symbols-outlined text-[20px] relative z-10 group-hover:translate-x-1 transition-transform" }, "arrow_forward")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "group bg-surface-container/40 backdrop-blur-md text-on-surface border border-white/10 font-label-md text-label-md px-10 py-4.5 rounded-xl flex items-center justify-center gap-3 hover:bg-white/10 hover:border-primary-container/50 transition-all duration-300"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`<span class="material-symbols-outlined text-[20px] text-secondary group-hover:rotate-12 transition-transform"${_scopeId}>smart_toy</span> Kh\xE1m Ph\xE1 Phim AI `);
          } else {
            return [
              createVNode("span", { class: "material-symbols-outlined text-[20px] text-secondary group-hover:rotate-12 transition-transform" }, "smart_toy"),
              createTextVNode(" Kh\xE1m Ph\xE1 Phim AI ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div></div></div></div></header><section class="py-16 bg-surface-container-lowest/40 relative"><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop"><div class="text-center mb-16 max-w-2xl mx-auto"><span class="text-xs font-bold text-secondary uppercase tracking-widest block mb-2">\u0110\u1EB7c Quy\u1EC1n CineAI</span><h2 class="font-headline-lg text-3xl font-bold text-on-surface">C\xF4ng Ngh\u1EC7 Cho Tr\u1EA3i Nghi\u1EC7m \u0110\u1EC9nh Cao</h2><p class="text-sm text-on-surface-variant mt-3">Ch\xFAng t\xF4i mang l\u1EA1i gi\u1EA3i ph\xE1p to\xE0n di\u1EC7n gi\xFAp \u0111\u01A1n gi\u1EA3n h\xF3a m\u1ECDi \u0111i\u1EC3m ch\u1EA1m \u0111\u1EB7t v\xE9 c\u1EE7a kh\xE1ch h\xE0ng.</p></div><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"><!--[-->`);
      ssrRenderList(highlights, (hl, index) => {
        _push(`<div class="glass-panel rounded-2xl border border-glass-stroke p-6 hover:border-primary-container/30 transition-all duration-300 flex flex-col"><div class="w-12 h-12 rounded-xl bg-surface-container-high border border-glass-stroke flex items-center justify-center text-primary-container mb-6"><span class="material-symbols-outlined text-[28px]">${ssrInterpolate(hl.icon)}</span></div><h3 class="font-bold text-lg text-on-surface mb-2">${ssrInterpolate(hl.title)}</h3><p class="text-xs text-on-surface-variant leading-relaxed">${ssrInterpolate(hl.description)}</p></div>`);
      });
      _push(`<!--]--></div></div></section><section class="py-16"><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop"><div class="flex items-center justify-between mb-12"><div><h2 class="font-headline-lg text-2xl md:text-3xl text-on-surface font-bold">Phim \u0110ang Chi\u1EBFu N\u1ED5i B\u1EADt</h2><p class="text-sm text-on-surface-variant mt-1">Danh s\xE1ch c\xE1c b\u1ED9 phim bom t\u1EA5n kh\xF4ng th\u1EC3 b\u1ECF qua t\u1EA1i c\xE1c c\u1EE5m r\u1EA1p CineAI.</p></div>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "text-sm font-bold text-primary hover:underline flex items-center gap-1"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` Xem t\u1EA5t c\u1EA3 <span class="material-symbols-outlined text-xs"${_scopeId}>arrow_forward</span>`);
          } else {
            return [
              createTextVNode(" Xem t\u1EA5t c\u1EA3 "),
              createVNode("span", { class: "material-symbols-outlined text-xs" }, "arrow_forward")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div><div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6"><!--[-->`);
      ssrRenderList(unref(movies).slice(0, 4), (movie) => {
        _push(ssrRenderComponent(_component_MovieCard, {
          key: movie.id,
          movie
        }, null, _parent));
      });
      _push(`<!--]--></div></div></section></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/index.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=index-CiDXyZr8.mjs.map
