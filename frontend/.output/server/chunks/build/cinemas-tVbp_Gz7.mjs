import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, ref, mergeProps, withCtx, createTextVNode, createVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderList, ssrIncludeBooleanAttr, ssrLooseContain, ssrLooseEqual, ssrInterpolate, ssrRenderStyle, ssrRenderClass, ssrRenderAttr, ssrRenderComponent } from 'vue/server-renderer';
import '../_/nitro.mjs';
import 'node:http';
import 'node:https';
import 'node:events';
import 'node:buffer';
import 'node:fs';
import 'node:path';
import 'node:crypto';
import 'node:url';
import './server.mjs';
import '../routes/renderer.mjs';
import 'vue-bundle-renderer/runtime';
import 'unhead/server';
import 'devalue';
import 'unhead/utils';
import 'unhead/plugins';
import 'vue-router';

const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "cinemas",
  __ssrInlineRender: true,
  setup(__props) {
    const selectedChain = ref("T\u1EA5t c\u1EA3 chu\u1ED7i r\u1EA1p");
    const activeCinema = ref(0);
    const chains = ["T\u1EA5t c\u1EA3 chu\u1ED7i r\u1EA1p", "CGV Cinemas", "Galaxy Cinema", "Lotte Cinema", "BHD Star Cineplex", "Beta Cinemas"];
    const cinemaList = [
      { name: "CGV Vincom \u0110\u1ED3ng Kh\u1EDFi", address: "T\u1EA7ng 3, Vincom Center B, 72 L\xEA Th\xE1nh T\xF4n, Q.1", distance: "0.8 km", rating: "4.8", reviews: "2.1k", status: "M\u1EDF c\u1EEDa" },
      { name: "CGV Aeon B\xECnh T\xE2n", address: "S\u1ED1 1 \u0110\u01B0\u1EDDng S\u1ED1 17A, Khu ph\u1ED1 11, B\xECnh T\xE2n", distance: "5.2 km", rating: "4.5", reviews: "1.5k", status: "M\u1EDF c\u1EEDa" },
      { name: "CGV Landmark 81", address: "B1 Vincom Center Landmark 81, B\xECnh Th\u1EA1nh", distance: "3.1 km", rating: "4.9", reviews: "3.2k", status: "M\u1EDF c\u1EEDa" },
      { name: "CGV Crescent Mall", address: "L\u1EA7u 5, Crescent Mall, Q.7", distance: "6.7 km", rating: "4.7", reviews: "1.8k", status: "M\u1EDF c\u1EEDa" },
      { name: "CGV Vivo City", address: "L\u1EA7u 5, SC VivoCity, 1058 Nguy\u1EC5n V\u0103n Linh, Q.7", distance: "7.2 km", rating: "4.6", reviews: "1.2k", status: "M\u1EDF c\u1EEDa" }
    ];
    const movieGrid = [
      { name: "Neural Breach", genre: "H\xE0nh \u0111\u1ED9ng, Vi\u1EC5n t\u01B0\u1EDFng - 124 ph", rating: "T16", img: "https://lh3.googleusercontent.com/aida-public/AB6AXuB5MLLqulnK8Oj5wJ2HAQV6DbvVtSweCD5FKG110-UWQkANqW-99hDHi_vktcnEFrh5ZfSEDFZrM1QYiVS1Uks3MkNGyFJQNylExj0dE2WOKciVgMIA7_x99ckjcFRg4VX639s5lO1ylETkGDzA2VlwbZOW9Pou1ilbSFJWGL9Ifn5SMmIjjqo0PkM270uAav0vFdlZ8i2K9dm1QcurSy-cK2X7A8E4zet_xAZNmeYfCUuNoWmEeBW3vFkJosF71Mtqm698I8LLUKFv" },
      { name: "Echoes of Eden", genre: "Phi\xEAu l\u01B0u, K\u1EF3 \u1EA3o - 142 ph", rating: "P", img: "https://lh3.googleusercontent.com/aida-public/AB6AXuB5uxjgTkJfkk1Ny9uwjY1w8giBjHS5RRYy2dFvd_kzLnYY0TANQCGD6QJv3BApG4OJt2dcZzqZ2MH8_LGD2kan7q3BO8SfqedxGwtSiQTE35Mdo9fDklFpDdlasbR4_WBywjgh7tRhrY__K6d55TJATtzy0lJCkNxvGHXfsnRPSFtKTAVygIL-t08xQugu11-3ACIPZa1cxzLxx_M8yFLlEDFTiVnd0g_-lghtdbOUQVhTWGriV3993SUeXBXpwqhRPXol9TZwAbK6" },
      { name: "The Void Project", genre: "Kinh d\u1ECB, B\xED \u1EA9n - 98 ph", rating: "T18", img: "https://lh3.googleusercontent.com/aida-public/AB6AXuD-QStG-CpQUnc-FJ7TE-nJe_3BKqDEeiJYJ8Zb7a22kZ7Dufx2F7Bf1qFlmnjXxj4a_zyPpK8n6JN06GzZ4WAmDO83A23Og1P0G_VSQVcc7OSlQArJcRCcr_s5xrZ6E0mfsD1FPLISVHrCX8yF4_CrE84FfHEPdzS_DJWLmTUAH_8Ta-Ga8JRbnsYJxdjJ66lXQ7kFY6secJVtr8d0OaC1VN0-R7lzNFrO4ESrH53UhHvX16g6R4FtV1hwulp6TRTgm6zEdaJdZbhU" },
      { name: "Midnight Strings", genre: "L\xE3ng m\u1EA1n, \xC2m nh\u1EA1c - 115 ph", rating: "T13", img: "https://lh3.googleusercontent.com/aida-public/AB6AXuAgoEnJkBVQIW0xHvbvChQiMfsHWVBU1AIH8IgBRj0GpOPVIEgpFcdAElDz5CP67U04y2XXr-bKitzrt2WQRAeJ6GnORKOfOArR9bh-PLKTIb1cKCr4ev0zayyffz8uJEVmthrqFxA_VDdMoPzLcZ2fdYZQ4c9xyTXzYwicZfLYveJYLSBshlYFYdQ" }
    ];
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "min-h-screen pt-20" }, _attrs))}><section class="w-full px-6 md:px-margin-desktop py-12 bg-gradient-to-b from-surface-container-low to-background"><div class="max-w-container-max mx-auto"><div class="flex flex-col md:flex-row md:items-end justify-between gap-8"><div><h1 class="font-headline-xl text-headline-xl mb-2 text-on-surface">H\u1EC7 Th\u1ED1ng R\u1EA1p</h1><p class="text-on-surface-variant font-body-lg text-body-lg">T\xECm ki\u1EBFm r\u1EA1p chi\u1EBFu phim CineAI g\u1EA7n b\u1EA1n nh\u1EA5t v\u1EDBi c\xF4ng ngh\u1EC7 tr\u1EA3i nghi\u1EC7m t\u01B0\u01A1ng lai.</p></div><div class="flex flex-col gap-3"><label class="font-label-md text-label-md text-primary-container ml-1">Ch\u1ECDn chu\u1ED7i r\u1EA1p</label><div class="relative min-w-[280px]"><select class="w-full bg-surface-container border border-white/10 rounded-xl px-4 py-3 text-on-surface appearance-none focus:border-primary-container focus:ring-0 cursor-pointer outline-none"><!--[-->`);
      ssrRenderList(chains, (c) => {
        _push(`<option${ssrIncludeBooleanAttr(Array.isArray(selectedChain.value) ? ssrLooseContain(selectedChain.value, null) : ssrLooseEqual(selectedChain.value, null)) ? " selected" : ""}>${ssrInterpolate(c)}</option>`);
      });
      _push(`<!--]--></select><span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span></div></div></div></div></section><section class="px-6 md:px-margin-desktop pb-24"><div class="max-w-container-max mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6"><aside class="lg:col-span-4 flex flex-col gap-4"><div class="flex items-center justify-between mb-2"><h3 class="font-headline-md text-headline-md text-on-surface">Chi nh\xE1nh (${ssrInterpolate(cinemaList.length)})</h3><button class="text-primary-container flex items-center gap-1 font-label-sm text-label-sm hover:underline"><span class="material-symbols-outlined text-[18px]">location_on</span> G\u1EA7n t\xF4i nh\u1EA5t </button></div><div class="rounded-2xl overflow-hidden" style="${ssrRenderStyle({ "background": "rgba(31,31,31,0.6)", "backdrop-filter": "blur(12px)", "border": "1px solid rgba(255,255,255,0.1)", "max-height": "600px", "overflow-y": "auto" })}"><!--[-->`);
      ssrRenderList(cinemaList, (cinema, i) => {
        _push(`<div class="${ssrRenderClass([activeCinema.value === i ? "border-l-4 border-l-primary-container bg-primary-container/5" : "", "p-5 border-b border-white/5 cursor-pointer hover:bg-white/5 transition-all"])}"><div class="flex justify-between items-start mb-1"><h4 class="font-headline-md text-[16px] text-on-surface">${ssrInterpolate(cinema.name)}</h4><span class="bg-primary-container/20 text-primary-container text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">${ssrInterpolate(cinema.status)}</span></div><p class="text-on-surface-variant text-label-md mb-3 truncate">${ssrInterpolate(cinema.address)}</p><div class="flex items-center gap-4 text-on-surface-variant text-label-sm"><span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">distance</span> ${ssrInterpolate(cinema.distance)}</span><span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">stars</span> ${ssrInterpolate(cinema.rating)} (${ssrInterpolate(cinema.reviews)} \u0111\xE1nh gi\xE1)</span></div></div>`);
      });
      _push(`<!--]--></div></aside><div class="lg:col-span-8 flex flex-col gap-6"><div class="rounded-3xl overflow-hidden" style="${ssrRenderStyle({ "background": "rgba(31,31,31,0.6)", "backdrop-filter": "blur(12px)", "border": "1px solid rgba(255,255,255,0.1)" })}"><div class="h-64 w-full relative"><img class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBsxpm-_EKZxL5GSj0I6E4HsmRq4e0n81zJ5l6suZ5a4BnxdZcMRpEbSEATKmxS4YXVSTb_tGvr6eaFydsNWZDtOCPa1ADc0JM8dnjYpvYyoBwgLpjPHeRCDnowXFA5IOSshiHdnutAbIONd2FjMZdn7mV8Bzc_qX3w_VGtpVi9ERUSugQjUwyOjlWqBE7X1vcJA-exhK1gl8Gc27j9n9KPqo0YVlhWcES-RJZU6xlzxT4yAxwaWSJrhHXjAhIF8gjCuo1okyEyu-Mw" alt="Cinema"><div class="absolute inset-0 bg-gradient-to-t from-background via-background/40 to-transparent"></div><div class="absolute bottom-6 left-8 right-8 flex justify-between items-end"><div><h2 class="font-headline-xl text-headline-xl text-white drop-shadow-lg">${ssrInterpolate(cinemaList[activeCinema.value].name)}</h2><div class="flex items-center gap-3 mt-2"><span class="bg-primary-container px-3 py-1 rounded text-white font-bold text-label-sm">IMAX</span><span class="px-3 py-1 rounded text-white font-bold text-label-sm border" style="${ssrRenderStyle({ "background": "rgba(138,43,226,0.3)", "border-color": "rgba(138,43,226,0.5)" })}">4DX + AI ENHANCED</span></div></div><div class="flex gap-2"><button class="p-3 rounded-full transition-colors border" style="${ssrRenderStyle({ "background": "rgba(255,255,255,0.1)", "backdrop-filter": "blur(8px)", "border-color": "rgba(255,255,255,0.1)" })}"><span class="material-symbols-outlined">share</span></button><button class="p-3 rounded-full transition-colors border" style="${ssrRenderStyle({ "background": "rgba(255,255,255,0.1)", "backdrop-filter": "blur(8px)", "border-color": "rgba(255,255,255,0.1)" })}"><span class="material-symbols-outlined">favorite</span></button></div></div></div><div class="p-8 grid grid-cols-1 md:grid-cols-2 gap-8"><div class="space-y-4"><div><h5 class="text-on-surface-variant font-label-md text-label-md uppercase tracking-widest mb-1">\u0110\u1ECBa ch\u1EC9</h5><p class="font-body-lg text-body-lg text-on-surface">${ssrInterpolate(cinemaList[activeCinema.value].address)}</p></div><div class="flex gap-4"><button class="flex-1 bg-white/5 hover:bg-white/10 border border-white/10 py-3 rounded-xl flex items-center justify-center gap-2 transition-all text-on-surface"><span class="material-symbols-outlined">call</span> G\u1ECDi r\u1EA1p </button><button class="flex-1 bg-white/5 hover:bg-white/10 border border-white/10 py-3 rounded-xl flex items-center justify-center gap-2 transition-all text-on-surface"><span class="material-symbols-outlined">directions</span> Ch\u1EC9 \u0111\u01B0\u1EDDng </button></div></div><div class="rounded-2xl overflow-hidden h-40 border border-white/10 opacity-80 hover:opacity-100 transition-all duration-500" style="${ssrRenderStyle({ "filter": "grayscale(0.5) contrast(1.2)" })}"><div class="w-full h-full bg-surface-container-high flex items-center justify-center relative"><div class="w-8 h-8 bg-primary-container rounded-full animate-ping absolute"></div><span class="material-symbols-outlined text-primary-container text-4xl relative z-10" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}">location_on</span></div></div></div></div><div><div class="flex items-center justify-between mb-6"><h3 class="font-headline-md text-headline-md text-on-surface">Phim \u0111ang chi\u1EBFu</h3><div class="flex items-center gap-4"><button class="text-on-surface-variant font-label-md text-label-md pb-1 border-b-2 border-primary-container text-primary-container">H\xF4m nay</button><button class="text-on-surface-variant font-label-md text-label-md pb-1 hover:text-on-surface transition-colors">Ng\xE0y mai</button></div></div><div class="grid grid-cols-1 md:grid-cols-2 gap-6"><!--[-->`);
      ssrRenderList(movieGrid, (m) => {
        _push(`<div class="rounded-2xl p-4 flex gap-4 hover:border-primary-container/50 transition-all group" style="${ssrRenderStyle({ "background": "rgba(31,31,31,0.6)", "backdrop-filter": "blur(12px)", "border": "1px solid rgba(255,255,255,0.1)" })}"><div class="w-24 h-36 rounded-lg overflow-hidden shrink-0"><img class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"${ssrRenderAttr("src", m.img)}${ssrRenderAttr("alt", m.name)}></div><div class="flex flex-col justify-between py-1 flex-1"><div><h4 class="font-headline-md text-[16px] leading-tight mb-1 group-hover:text-primary-container transition-colors text-on-surface">${ssrInterpolate(m.name)}</h4><p class="text-on-surface-variant text-label-sm">${ssrInterpolate(m.genre)}</p></div><div class="flex items-center justify-between"><span class="text-primary-container font-bold text-label-md">${ssrInterpolate(m.rating)}</span>`);
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: "/showtimes",
          class: "bg-primary-container/10 hover:bg-primary-container text-primary-container hover:text-white px-4 py-2 rounded-lg font-label-md text-label-md transition-all"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`Xem l\u1ECBch chi\u1EBFu`);
            } else {
              return [
                createTextVNode("Xem l\u1ECBch chi\u1EBFu")
              ];
            }
          }),
          _: 2
        }, _parent));
        _push(`</div></div></div>`);
      });
      _push(`<!--]--></div></div><div class="rounded-3xl p-8 flex flex-col md:flex-row items-center gap-8 relative overflow-hidden" style="${ssrRenderStyle({ "background": "rgba(31,31,31,0.6)", "backdrop-filter": "blur(12px)", "border": "1px solid rgba(255,255,255,0.1)" })}"><div class="relative z-10 flex-1"><h3 class="font-headline-lg text-headline-lg mb-4 text-on-surface">Tr\u1EE3 l\xFD CineAI gi\xFAp b\u1EA1n ch\u1ECDn phim?</h3><p class="text-on-surface-variant font-body-md text-body-md mb-6">B\u1EA1n \u0111ang \u1EDF r\u1EA1p nh\u01B0ng ch\u01B0a bi\u1EBFt xem phim g\xEC? H\xE3y \u0111\u1EC3 tr\xED tu\u1EC7 nh\xE2n t\u1EA1o c\u1EE7a ch\xFAng t\xF4i g\u1EE3i \xFD phim ph\xF9 h\u1EE3p.</p>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/ai-discovery",
        class: "bg-[#8a2be2] text-white px-8 py-3 rounded-full font-bold hover:scale-105 transition-all flex items-center gap-2 group w-fit"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`<span class="material-symbols-outlined"${_scopeId}>auto_awesome</span> Kh\xE1m ph\xE1 ngay <span class="material-symbols-outlined group-hover:translate-x-1 transition-transform"${_scopeId}>arrow_forward</span>`);
          } else {
            return [
              createVNode("span", { class: "material-symbols-outlined" }, "auto_awesome"),
              createTextVNode(" Kh\xE1m ph\xE1 ngay "),
              createVNode("span", { class: "material-symbols-outlined group-hover:translate-x-1 transition-transform" }, "arrow_forward")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div><div class="w-48 h-48 relative z-10 hidden md:block"><div class="w-full h-full rounded-full opacity-30 animate-pulse" style="${ssrRenderStyle({ "background": "linear-gradient(to top right,#e50914,#8a2be2)", "filter": "blur(48px)" })}"></div><span class="material-symbols-outlined text-[120px] text-[#8a2be2] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}">neurology</span></div></div></div></div></section></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/cinemas.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=cinemas-tVbp_Gz7.mjs.map
