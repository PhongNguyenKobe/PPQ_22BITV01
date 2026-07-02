import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, withCtx, createVNode, createTextVNode, unref, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderStyle, ssrRenderComponent, ssrRenderList, ssrRenderAttr, ssrInterpolate, ssrRenderClass } from 'vue/server-renderer';
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
    const features = [
      { icon: "chair", title: "\u0110\u1EB7t v\xE9 tr\u1EF1c tuy\u1EBFn", desc: "Ch\u1ECDn ch\u1ED7 ng\u1ED3i theo th\u1EDDi gian th\u1EF1c t\u1EA1i m\u1ECDi c\u1EE5m r\u1EA1p tr\xEAn to\xE0n qu\u1ED1c v\u1EDBi \u0111\u1ED9 ch\xEDnh x\xE1c tuy\u1EC7t \u0111\u1ED1i." },
      { icon: "smart_toy", title: "Tr\u1EE3 l\xFD AI Chatbot", desc: "T\xECm phim b\u1EB1ng ng\xF4n ng\u1EEF t\u1EF1 nhi\xEAn, nh\u1EADn \u0111\u1EC1 xu\u1EA5t c\xE1 nh\xE2n h\xF3a d\u1EF1a tr\xEAn s\u1EDF th\xEDch c\u1EE7a b\u1EA1n." },
      { icon: "payments", title: "Thanh to\xE1n \u0111a k\xEAnh", desc: "H\u1ED7 tr\u1EE3 thanh to\xE1n nhanh ch\xF3ng qua Momo, VNPAY, th\u1EBB t\xEDn d\u1EE5ng ho\u1EB7c qu\xE9t m\xE3 QR an to\xE0n." },
      { icon: "qr_code", title: "Qu\u1EA3n l\xFD v\xE9 \u0111i\u1EC7n t\u1EED", desc: "L\u01B0u tr\u1EEF v\xE9 th\xF4ng minh, qu\xE9t m\xE3 QR t\u1EA1i r\u1EA1p kh\xF4ng c\u1EA7n in gi\u1EA5y, th\xE2n thi\u1EC7n v\u1EDBi m\xF4i tr\u01B0\u1EDDng." }
    ];
    const promos = [
      { icon: "loyalty", label: "T\u1EB7ng ngay", title: "M\xE3 gi\u1EA3m gi\xE1 20% l\u1EA7n \u0111\u1EA7u" },
      { icon: "local_dining", label: "\u0110\u1ED3ng gi\xE1", title: "Combo b\u1EAFp n\u01B0\u1EDBc 99k" }
    ];
    const showtimeButtons = ["19:30", "20:15", "21:00"];
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(_attrs)}><header class="relative w-full min-h-[90vh] flex items-center pt-20"><div class="absolute inset-0 z-0"><div class="w-full h-full bg-[url(&#39;https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&amp;w=2070&amp;auto=format&amp;fit=crop&#39;)] bg-cover bg-center bg-no-repeat"></div><div class="absolute inset-0" style="${ssrRenderStyle({ "background": "rgba(18,20,20,0.8)" })}"></div><div class="absolute inset-0" style="${ssrRenderStyle({ "background": "linear-gradient(to top,rgba(18,20,20,1) 0%,rgba(18,20,20,0) 100%)" })}"></div></div><div class="relative z-10 w-full max-w-container-max mx-auto px-6 md:px-margin-desktop py-24"><div class="max-w-4xl relative"><div class="absolute -top-24 -left-24 w-96 h-96 rounded-full pointer-events-none z-0 animate-pulse" style="${ssrRenderStyle({ "background": "rgba(229,9,20,0.1)", "filter": "blur(120px)" })}"></div><div class="absolute top-1/2 -right-48 w-64 h-64 rounded-full pointer-events-none z-0" style="${ssrRenderStyle({ "background": "rgba(138,43,226,0.1)", "filter": "blur(100px)" })}"></div><div class="relative z-10"><div class="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-8" style="${ssrRenderStyle({ "background": "rgba(229,9,20,0.1)", "border": "1px solid rgba(229,9,20,0.2)", "backdrop-filter": "blur(16px)" })}"><span class="material-symbols-outlined text-primary-container text-[20px] animate-pulse">psychology</span><span class="text-label-md font-bold tracking-wider uppercase text-primary-container">Tr\xED tu\u1EC7 \u0111i\u1EC7n \u1EA3nh th\u1EBF h\u1EC7 m\u1EDBi</span></div><h1 class="font-headline-xl md:text-[72px] md:leading-[80px] font-bold mb-8 text-on-surface tracking-tight"> \u0110\u1EB7t v\xE9 xem phim <br>th\xF4ng minh v\u1EDBi <span class="relative inline-block ml-2"><span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-container to-[#ffb4aa]" style="${ssrRenderStyle({ "filter": "drop-shadow(0 0 15px rgba(229,9,20,0.6))" })}">AI</span><span class="absolute -inset-1 rounded-full" style="${ssrRenderStyle({ "background": "rgba(229,9,20,0.2)", "filter": "blur(16px)" })}"></span></span></h1><p class="font-body-lg text-body-lg text-on-surface-variant mb-12 max-w-2xl leading-relaxed"> Tr\u1EA3i nghi\u1EC7m t\u01B0\u01A1ng lai c\u1EE7a \u0111i\u1EC7n \u1EA3nh. T\xECm ki\u1EBFm, kh\xE1m ph\xE1 v\xE0 \u0111\u1EB7t v\xE9 ch\u1EC9 trong v\xE0i gi\xE2y v\u1EDBi tr\u1EE3 l\xFD AI th\xF4ng minh c\u1EE7a CineAI. </p><div class="flex flex-col sm:flex-row gap-6">`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "group relative bg-primary-container text-on-primary-container font-label-md text-label-md px-10 py-5 rounded-xl flex items-center justify-center gap-3 transition-all duration-300 overflow-hidden",
        style: { "box-shadow": "0 0 25px -2px rgba(229,9,20,0.3)" }
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`<div class="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300"${_scopeId}></div><span class="relative z-10"${_scopeId}>\u0110\u1EB7t v\xE9 ngay</span><span class="material-symbols-outlined text-[22px] relative z-10 group-hover:translate-x-1 transition-transform"${_scopeId}>arrow_forward</span>`);
          } else {
            return [
              createVNode("div", { class: "absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300" }),
              createVNode("span", { class: "relative z-10" }, "\u0110\u1EB7t v\xE9 ngay"),
              createVNode("span", { class: "material-symbols-outlined text-[22px] relative z-10 group-hover:translate-x-1 transition-transform" }, "arrow_forward")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/ai-discovery",
        class: "group bg-surface-container/40 backdrop-blur-md text-on-surface border border-white/10 font-label-md text-label-md px-10 py-5 rounded-xl flex items-center justify-center gap-3 hover:bg-white/10 hover:border-primary-container/50 transition-all duration-300"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`<span class="material-symbols-outlined text-[22px] text-primary-container group-hover:rotate-12 transition-transform"${_scopeId}>smart_toy</span> Tr\u1EA3i nghi\u1EC7m tr\u1EE3 l\xFD AI `);
          } else {
            return [
              createVNode("span", { class: "material-symbols-outlined text-[22px] text-primary-container group-hover:rotate-12 transition-transform" }, "smart_toy"),
              createTextVNode(" Tr\u1EA3i nghi\u1EC7m tr\u1EE3 l\xFD AI ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div><div class="mt-16 flex items-center gap-8 opacity-60"><div class="flex flex-col"><span class="text-headline-md font-bold text-on-surface">500k+</span><span class="text-label-sm text-on-surface-variant uppercase">Ng\u01B0\u1EDDi d\xF9ng</span></div><div class="w-px h-10 bg-white/10"></div><div class="flex flex-col"><span class="text-headline-md font-bold text-on-surface">99.9%</span><span class="text-label-sm text-on-surface-variant uppercase">Ch\xEDnh x\xE1c</span></div><div class="w-px h-10 bg-white/10"></div><div class="flex flex-col"><span class="text-headline-md font-bold text-on-surface">24/7</span><span class="text-label-sm text-on-surface-variant uppercase">H\u1ED7 tr\u1EE3 AI</span></div></div></div></div></div></header><main class="flex-grow"><section class="w-full max-w-container-max mx-auto px-6 md:px-margin-desktop py-24"><div class="flex justify-between items-end mb-12"><h2 class="font-headline-lg text-headline-lg font-bold text-on-surface">Phim \u0111ang chi\u1EBFu</h2>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "hidden md:flex items-center gap-1 text-primary-container font-label-md text-label-md hover:text-primary transition-colors"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` Xem t\u1EA5t c\u1EA3 <span class="material-symbols-outlined text-[20px]"${_scopeId}>chevron_right</span>`);
          } else {
            return [
              createTextVNode(" Xem t\u1EA5t c\u1EA3 "),
              createVNode("span", { class: "material-symbols-outlined text-[20px]" }, "chevron_right")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div><div class="grid grid-cols-2 md:grid-cols-4 gap-6"><!--[-->`);
      ssrRenderList(unref(movies).slice(0, 4), (movie) => {
        _push(`<article class="group relative rounded-xl overflow-hidden bg-surface-container hover:scale-[1.02] transition-transform duration-300"><div class="aspect-[2/3] w-full bg-surface-variant relative overflow-hidden">`);
        if (movie.poster) {
          _push(`<img${ssrRenderAttr("src", movie.poster)}${ssrRenderAttr("alt", movie.title)} class="w-full h-full object-cover">`);
        } else {
          _push(`<div class="w-full h-full bg-[url(&#39;https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&amp;w=1925&amp;auto=format&amp;fit=crop&#39;)] bg-cover bg-center"></div>`);
        }
        _push(`<div class="absolute inset-0" style="${ssrRenderStyle({ "background": "linear-gradient(to top,rgba(18,20,20,1) 0%,rgba(18,20,20,0) 100%)" })}"></div><div class="absolute top-4 left-4"><span class="bg-[#1F1F1F] text-on-surface px-3 py-1 rounded-full font-label-sm text-label-sm border border-white/10">${ssrInterpolate(movie.format || "IMAX")}</span></div></div><div class="absolute bottom-0 w-full p-6 translate-y-4 group-hover:translate-y-0 transition-transform duration-300"><div class="flex items-center gap-1 text-primary mb-2"><span class="material-symbols-outlined text-[16px]" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}">star</span><span class="font-label-sm text-label-sm text-on-surface font-semibold">${ssrInterpolate(movie.rating || "4.8")}</span></div><h3 class="font-headline-md text-headline-md font-bold text-on-surface mb-4 truncate">${ssrInterpolate(movie.title)}</h3><div class="flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-100">`);
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: `/movies/${movie.id}`,
          class: "w-full bg-primary-container text-on-primary-container font-label-md text-label-md py-2.5 rounded-lg text-center transition-all",
          style: { "box-shadow": "0 0 25px -2px rgba(229,9,20,0.3)" }
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`\u0110\u1EB7t ch\u1ED7`);
            } else {
              return [
                createTextVNode("\u0110\u1EB7t ch\u1ED7")
              ];
            }
          }),
          _: 2
        }, _parent));
        _push(`<button class="w-full bg-transparent border border-white/20 text-on-surface font-label-md text-label-md py-2.5 rounded-lg hover:bg-white/10 transition-colors">Xem trailer</button></div></div></article>`);
      });
      _push(`<!--]--></div></section><section class="w-full bg-surface-container-low py-24 relative overflow-hidden"><div class="absolute top-0 right-0 w-[500px] h-[500px] pointer-events-none" style="${ssrRenderStyle({ "background": "rgba(229,9,20,0.05)", "filter": "blur(100px)" })}"></div><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop relative z-10"><div class="text-center mb-16"><h2 class="font-headline-lg text-headline-lg font-bold text-on-surface mb-4">C\xF4ng ngh\u1EC7 d\u1EABn \u0111\u1EA7u tr\u1EA3i nghi\u1EC7m</h2><p class="font-body-lg text-body-lg text-on-surface-variant max-w-2xl mx-auto">H\u1EC7 sinh th\xE1i th\xF4ng minh gi\xFAp h\xE0nh tr\xECnh xem phim c\u1EE7a b\u1EA1n li\u1EC1n m\u1EA1ch t\u1EEB l\xFAc ch\u1ECDn gh\u1EBF \u0111\u1EBFn khi v\xE0o r\u1EA1p.</p></div><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"><!--[-->`);
      ssrRenderList(features, (f) => {
        _push(`<div class="p-8 rounded-xl hover:-translate-y-2 transition-transform duration-300" style="${ssrRenderStyle({ "background": "rgba(31,31,31,0.6)", "backdrop-filter": "blur(12px)", "border": "1px solid rgba(255,255,255,0.1)" })}"><div class="w-14 h-14 bg-surface-variant rounded-lg flex items-center justify-center mb-6 border border-white/5"><span class="material-symbols-outlined text-[28px] text-primary">${ssrInterpolate(f.icon)}</span></div><h3 class="font-headline-md text-[20px] leading-tight font-bold text-on-surface mb-3">${ssrInterpolate(f.title)}</h3><p class="font-body-md text-body-md text-on-surface-variant">${ssrInterpolate(f.desc)}</p></div>`);
      });
      _push(`<!--]--></div></div></section><section class="w-full max-w-container-max mx-auto px-6 md:px-margin-desktop py-24"><div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center"><div><h2 class="font-headline-xl text-headline-xl font-bold text-on-surface mb-6">Giao ti\u1EBFp t\u1EF1 nhi\xEAn, <br>nh\u1EADn v\xE9 t\u1EE9c th\xEC</h2><p class="font-body-lg text-body-lg text-on-surface-variant mb-8">Kh\xF4ng c\u1EA7n duy\u1EC7t qua h\xE0ng t\xE1 l\u1ECBch chi\u1EBFu ph\u1EE9c t\u1EA1p. Ch\u1EC9 c\u1EA7n n\xF3i cho AI c\u1EE7a ch\xFAng t\xF4i bi\u1EBFt b\u1EA1n mu\u1ED1n xem g\xEC, \u1EDF \u0111\xE2u v\xE0 m\u1EE9c gi\xE1 mong mu\u1ED1n.</p><ul class="space-y-4 mb-10"><li class="flex items-center gap-3 text-on-surface"><span class="material-symbols-outlined text-primary">check_circle</span><span class="font-body-md text-body-md">X\u1EED l\xFD ng\xF4n ng\u1EEF t\u1EF1 nhi\xEAn ti\u1EBFng Vi\u1EC7t ch\xEDnh x\xE1c</span></li><li class="flex items-center gap-3 text-on-surface"><span class="material-symbols-outlined text-primary">check_circle</span><span class="font-body-md text-body-md">So s\xE1nh gi\xE1 v\xE0 su\u1EA5t chi\u1EBFu \u0111a r\u1EA1p theo th\u1EDDi gian th\u1EF1c</span></li><li class="flex items-center gap-3 text-on-surface"><span class="material-symbols-outlined text-primary">check_circle</span><span class="font-body-md text-body-md">T\u1EF1 \u0111\u1ED9ng \u0111\u1EC1 xu\u1EA5t combo b\u1EAFp n\u01B0\u1EDBc t\u1ED1i \u01B0u</span></li></ul>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/ai-discovery",
        class: "bg-transparent text-on-surface border-[1.5px] border-white/20 font-label-md text-label-md px-8 py-3 rounded-lg hover:bg-white/10 transition-colors duration-300 inline-block"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` Kh\xE1m ph\xE1 t\xEDnh n\u0103ng AI `);
          } else {
            return [
              createTextVNode(" Kh\xE1m ph\xE1 t\xEDnh n\u0103ng AI ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div><div class="relative"><div class="absolute -inset-1 rounded-2xl blur opacity-20" style="${ssrRenderStyle({ "background": "linear-gradient(to right,#e50914,#8a2be2)" })}"></div><div class="relative rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[480px]" style="${ssrRenderStyle({ "background": "#121212", "border": "1px solid #1F1F1F" })}"><div class="p-4 flex items-center gap-3 border-b border-white/5" style="${ssrRenderStyle({ "background": "#1F1F1F" })}"><div class="w-10 h-10 rounded-full flex items-center justify-center" style="${ssrRenderStyle({ "background": "rgba(229,9,20,0.2)" })}"><span class="material-symbols-outlined text-primary text-[20px]">smart_toy</span></div><div><h4 class="font-label-md text-label-md text-on-surface font-bold">Tr\u1EE3 l\xFD CineAI</h4><span class="font-label-sm text-label-sm text-primary flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-primary inline-block animate-pulse"></span> Tr\u1EF1c tuy\u1EBFn </span></div></div><div class="flex-grow p-6 flex flex-col gap-6 overflow-y-auto"><div class="flex justify-end"><div class="bg-[#1F1F1F] text-on-surface font-body-md text-body-md p-4 rounded-2xl rounded-tr-sm max-w-[80%] border border-white/5"> T\xECm phim h\xE0nh \u0111\u1ED9ng t\u1ED1i nay \u1EDF Qu\u1EADn 7 gi\xE1 d\u01B0\u1EDBi 150k </div></div><div class="flex justify-start items-end gap-2"><div class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center mb-1" style="${ssrRenderStyle({ "background": "rgba(229,9,20,0.2)" })}"><span class="material-symbols-outlined text-primary text-[16px]">smart_toy</span></div><div class="text-on-surface font-body-md text-body-md p-4 rounded-2xl rounded-tl-sm max-w-[85%]" style="${ssrRenderStyle({ "background": "rgba(229,9,20,0.1)", "border": "1px solid rgba(229,9,20,0.2)" })}"> Ch\xE0o b\u1EA1n! T\xF4i t\xECm th\u1EA5y 3 su\u1EA5t chi\u1EBFu phim <span class="text-primary font-semibold">&#39;John Wick 4&#39;</span> t\u1EA1i <span class="font-semibold text-on-surface">CGV SC VivoCity</span>:<br><br><div class="flex gap-2 my-2"><!--[-->`);
      ssrRenderList(showtimeButtons, (t) => {
        _push(`<span class="${ssrRenderClass([t === "19:30" ? "bg-primary-container text-on-primary-container" : "border border-white/20 text-on-surface", "px-3 py-1 rounded font-label-sm text-label-sm font-bold"])}">${ssrInterpolate(t)}</span>`);
      });
      _push(`<!--]--></div><br>Gi\xE1 v\xE9 \u0111ang \u01B0u \u0111\xE3i ch\u1EC9 t\u1EEB <span class="text-primary font-bold">120k</span>. B\u1EA1n c\xF3 mu\u1ED1n \u0111\u1EB7t v\xE9 ngay kh\xF4ng? </div></div></div><div class="p-4 border-t border-white/5 flex gap-3 items-center" style="${ssrRenderStyle({ "background": "#1F1F1F" })}"><div class="flex-grow rounded-full px-4 py-3 flex items-center gap-2 transition-all" style="${ssrRenderStyle({ "background": "#121212", "border": "1px solid #2A2A2A" })}"><span class="material-symbols-outlined text-on-surface-variant text-[20px]">mic</span><span class="text-on-surface-variant font-body-md text-body-md">\u0110\u1EB7t v\xE9 su\u1EA5t 19:30</span></div>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/checkout/seat",
        class: "w-12 h-12 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center transition-all flex-shrink-0 hover:scale-105",
        style: { "box-shadow": "0 0 20px -5px rgba(229,9,20,0.3)" }
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`<span class="material-symbols-outlined"${_scopeId}>send</span>`);
          } else {
            return [
              createVNode("span", { class: "material-symbols-outlined" }, "send")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div></div></div></div></section><section class="w-full max-w-container-max mx-auto px-6 md:px-margin-desktop py-12"><div class="border-l-4 border-l-primary-container rounded-r-xl p-8 flex flex-col md:flex-row items-center justify-between gap-8 relative overflow-hidden" style="${ssrRenderStyle({ "background": "rgba(31,31,31,0.6)", "backdrop-filter": "blur(12px)", "border": "1px solid rgba(255,255,255,0.1)" })}"><div class="absolute top-0 right-0 w-64 h-64 pointer-events-none" style="${ssrRenderStyle({ "background": "rgba(229,9,20,0.1)", "filter": "blur(48px)" })}"></div><div class="relative z-10 flex-shrink-0"><h2 class="font-headline-lg text-headline-md md:text-headline-lg font-bold text-on-surface mb-2">\u01AFu \u0111\xE3i \u0111\u1ED9c quy\u1EC1n cho th\xE0nh vi\xEAn CineAI</h2><p class="font-body-md text-body-md text-on-surface-variant">\u0110\u0103ng k\xFD ngay \u0111\u1EC3 nh\u1EADn nh\u1EEFng \u0111\u1EB7c quy\u1EC1n d\xE0nh ri\xEAng cho b\u1EA1n.</p></div><div class="relative z-10 flex flex-wrap gap-4 w-full md:w-auto justify-start md:justify-end"><!--[-->`);
      ssrRenderList(promos, (p) => {
        _push(`<div class="rounded-lg px-6 py-4 flex items-center gap-4" style="${ssrRenderStyle({ "background": "#121212", "border": "1px solid rgba(255,255,255,0.1)" })}"><div class="w-12 h-12 rounded-full flex items-center justify-center text-primary-container" style="${ssrRenderStyle({ "background": "rgba(229,9,20,0.2)" })}"><span class="material-symbols-outlined">${ssrInterpolate(p.icon)}</span></div><div><p class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">${ssrInterpolate(p.label)}</p><p class="font-headline-md text-[18px] font-bold text-on-surface">${ssrInterpolate(p.title)}</p></div></div>`);
      });
      _push(`<!--]--></div></div></section><section class="w-full bg-surface-container-low py-24 mt-12 relative overflow-hidden"><div class="absolute inset-0 z-0 opacity-20"><div class="w-full h-full bg-[url(&#39;https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&amp;w=2070&amp;auto=format&amp;fit=crop&#39;)] bg-cover bg-center"></div></div><div class="absolute inset-0 bg-gradient-to-t from-background to-transparent z-0"></div><div class="max-w-4xl mx-auto px-6 text-center relative z-10"><h2 class="font-headline-xl text-headline-xl md:text-[56px] md:leading-[64px] font-bold text-on-surface mb-8">Kh\xE1m ph\xE1 tr\u1EA3i nghi\u1EC7m \u0111\u1EB7t v\xE9 th\xF4ng minh ngay h\xF4m nay!</h2>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/register",
        class: "bg-primary-container text-on-primary-container font-label-md text-label-md px-10 py-5 rounded-lg text-lg inline-flex items-center gap-2 transition-all duration-300 hover:scale-105",
        style: { "box-shadow": "0 0 25px -2px rgba(229,9,20,0.3)" }
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` \u0110\u0103ng k\xFD ngay <span class="material-symbols-outlined"${_scopeId}>arrow_forward</span>`);
          } else {
            return [
              createTextVNode(" \u0110\u0103ng k\xFD ngay "),
              createVNode("span", { class: "material-symbols-outlined" }, "arrow_forward")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div></section></main></div>`);
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
//# sourceMappingURL=index-z347Snmo.mjs.map
