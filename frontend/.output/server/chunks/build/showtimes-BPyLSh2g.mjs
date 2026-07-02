import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, ref, mergeProps, withCtx, createVNode, createTextVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderStyle, ssrRenderList, ssrIncludeBooleanAttr, ssrLooseContain, ssrLooseEqual, ssrInterpolate, ssrRenderClass, ssrRenderComponent } from 'vue/server-renderer';
import { _ as _export_sfc } from './server.mjs';
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
  __name: "showtimes",
  __ssrInlineRender: true,
  setup(__props) {
    const selectedTheater = ref("T\u1EA5t c\u1EA3 r\u1EA1p");
    const selectedMovie = ref("T\u1EA5t c\u1EA3 phim");
    const selectedDay = ref(0);
    const theaters = ["T\u1EA5t c\u1EA3 r\u1EA1p", "CineAI Landmark 81", "CineAI Bitexco Financial", "CineAI West Lake Hanoi", "CineAI \u0110\xE0 N\u1EB5ng Dragon"];
    const movieList = ["T\u1EA5t c\u1EA3 phim", "Dune: Ph\u1EA7n Hai", "Oppenheimer", "Mai", "Kung Fu Panda 4"];
    const days = [
      { label: "TH 3", date: 12 },
      { label: "TH 4", date: 13 },
      { label: "TH 5", date: 14 },
      { label: "TH 6", date: 15 },
      { label: "TH 7", date: 16 },
      { label: "CN", date: 17 },
      { label: "TH 2", date: 18 }
    ];
    const aiCards = [
      { badge: "Tr\u1EA3i nghi\u1EC7m t\u1ED1t nh\u1EA5t", badgeColor: "bg-primary-container/10 text-primary-container", match: "98%", movie: "Dune: Ph\u1EA7n Hai", desc: "B\u1EA1n th\u01B0\u1EDDng xem phim sci-fi v\xE0o t\u1ED1i Th\u1EE9 3 t\u1EA1i c\xE1c r\u1EA1p IMAX.", time: "H\xF4m nay, 20:15", theater: "CineAI Landmark 81" },
      { badge: "Su\u1EA5t chi\u1EBFu v\u1EAFng kh\xE1ch", badgeColor: "bg-[#8a2be2]/10 text-[#8a2be2]", match: "85%", movie: "Oppenheimer", desc: "D\xE0nh cho b\u1EA1n mu\u1ED1n kh\xF4ng gian y\xEAn t\u0129nh \u0111\u1EC3 c\u1EA3m th\u1EE5 t\xE1c ph\u1EA9m d\xE0i.", time: "H\xF4m nay, 14:30", theater: "CineAI Bitexco" },
      { badge: "\u01AFu \u0111\xE3i th\xE0nh vi\xEAn", badgeColor: "bg-green-500/10 text-green-500", match: "92%", movie: "Mai", desc: "Th\xE0nh vi\xEAn Diamond \u0111\u01B0\u1EE3c gi\u1EA3m 30% gi\xE1 v\xE9 cho su\u1EA5t chi\u1EBFu n\xE0y.", time: "H\xF4m nay, 19:45", theater: "CineAI West Lake" }
    ];
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "min-h-screen pt-20" }, _attrs))} data-v-a97efb8d><section class="relative pt-12 pb-8 px-6 md:px-margin-desktop bg-gradient-to-b from-surface-container-lowest to-surface" data-v-a97efb8d><div class="max-w-container-max mx-auto" data-v-a97efb8d><h1 class="font-headline-xl text-headline-xl mb-10 text-on-surface" data-v-a97efb8d>L\u1ECBch Chi\u1EBFu</h1><div class="flex flex-col md:flex-row items-start md:items-center gap-6 p-6 rounded-2xl mb-8" style="${ssrRenderStyle({ "background": "rgba(31,31,31,0.6)", "backdrop-filter": "blur(12px)", "border": "1px solid rgba(255,255,255,0.1)" })}" data-v-a97efb8d><div class="w-full md:w-1/4" data-v-a97efb8d><label class="block text-label-sm font-label-sm text-on-surface-variant mb-2 px-1" data-v-a97efb8d>Ch\u1ECDn R\u1EA1p</label><div class="relative" data-v-a97efb8d><select class="w-full bg-surface-container-high border-white/10 text-on-surface rounded-lg py-3 px-4 appearance-none focus:ring-primary-container focus:border-primary-container font-label-md text-label-md cursor-pointer outline-none border border-white/10" data-v-a97efb8d><!--[-->`);
      ssrRenderList(theaters, (t) => {
        _push(`<option data-v-a97efb8d${ssrIncludeBooleanAttr(Array.isArray(selectedTheater.value) ? ssrLooseContain(selectedTheater.value, null) : ssrLooseEqual(selectedTheater.value, null)) ? " selected" : ""}>${ssrInterpolate(t)}</option>`);
      });
      _push(`<!--]--></select><span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant" data-v-a97efb8d>expand_more</span></div></div><div class="w-full md:w-1/4" data-v-a97efb8d><label class="block text-label-sm font-label-sm text-on-surface-variant mb-2 px-1" data-v-a97efb8d>Ch\u1ECDn Phim</label><div class="relative" data-v-a97efb8d><select class="w-full bg-surface-container-high border-white/10 text-on-surface rounded-lg py-3 px-4 appearance-none focus:ring-primary-container focus:border-primary-container font-label-md text-label-md cursor-pointer outline-none border border-white/10" data-v-a97efb8d><!--[-->`);
      ssrRenderList(movieList, (m) => {
        _push(`<option data-v-a97efb8d${ssrIncludeBooleanAttr(Array.isArray(selectedMovie.value) ? ssrLooseContain(selectedMovie.value, null) : ssrLooseEqual(selectedMovie.value, null)) ? " selected" : ""}>${ssrInterpolate(m)}</option>`);
      });
      _push(`<!--]--></select><span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant" data-v-a97efb8d>expand_more</span></div></div><div class="w-full md:w-2/4" data-v-a97efb8d><label class="block text-label-sm font-label-sm text-on-surface-variant mb-2 px-1" data-v-a97efb8d>Ch\u1ECDn Ng\xE0y</label><div class="flex gap-3 overflow-x-auto pb-2" style="${ssrRenderStyle({ "scrollbar-width": "none" })}" data-v-a97efb8d><!--[-->`);
      ssrRenderList(days, (d, i) => {
        _push(`<button class="${ssrRenderClass([selectedDay.value === i ? "bg-primary-container text-white shadow-[0_0_20px_-5px_rgba(229,9,20,0.3)]" : "bg-surface-container-high border border-white/5 hover:border-primary-container text-on-surface", "flex-shrink-0 flex flex-col items-center justify-center min-w-[70px] h-[70px] rounded-xl transition-all"])}" data-v-a97efb8d><span class="text-label-sm font-label-sm opacity-80" data-v-a97efb8d>${ssrInterpolate(d.label)}</span><span class="text-headline-md font-bold" data-v-a97efb8d>${ssrInterpolate(d.date)}</span></button>`);
      });
      _push(`<!--]--></div></div></div></div></section><section class="px-6 md:px-margin-desktop py-12" data-v-a97efb8d><div class="max-w-container-max mx-auto" data-v-a97efb8d><div class="flex items-center gap-3 mb-8" data-v-a97efb8d><span class="material-symbols-outlined text-primary-container text-[32px]" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}" data-v-a97efb8d>psychology</span><h2 class="font-headline-lg text-headline-lg text-on-surface" data-v-a97efb8d>G\u1EE3i \xFD su\u1EA5t chi\u1EBFu AI</h2></div><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8" data-v-a97efb8d><!--[-->`);
      ssrRenderList(aiCards, (c) => {
        _push(`<div class="overflow-hidden rounded-xl" style="${ssrRenderStyle({ "position": "relative", "background": "rgba(31,31,31,0.8)", "border-radius": "12px", "padding": "1px" })}" data-v-a97efb8d><div class="absolute inset-0 rounded-xl" style="${ssrRenderStyle({ "padding": "1.5px", "background": "linear-gradient(45deg,#e50914,#8a2be2,#e50914)", "background-size": "200% 200%", "animation": "gradient-move 4s linear infinite", "-webkit-mask": "linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0)", "-webkit-mask-composite": "xor", "mask-composite": "exclude" })}" data-v-a97efb8d></div><div class="p-6 rounded-[11px] flex flex-col justify-between h-full" style="${ssrRenderStyle({ "background": "#1e2020" })}" data-v-a97efb8d><div data-v-a97efb8d><div class="flex justify-between items-start mb-4" data-v-a97efb8d><div class="${ssrRenderClass([c.badgeColor, "px-3 py-1 rounded-full text-label-sm font-bold uppercase tracking-wider"])}" data-v-a97efb8d>${ssrInterpolate(c.badge)}</div><span class="text-on-surface-variant text-label-sm" data-v-a97efb8d>\u0110\u1ED9 kh\u1EDBp: ${ssrInterpolate(c.match)}</span></div><h3 class="font-headline-md text-headline-md text-on-surface mb-2" data-v-a97efb8d>${ssrInterpolate(c.movie)}</h3><p class="text-on-surface-variant font-body-md mb-6" data-v-a97efb8d>${ssrInterpolate(c.desc)}</p></div><div class="flex items-center justify-between" data-v-a97efb8d><div class="flex flex-col" data-v-a97efb8d><span class="text-label-sm text-on-surface-variant" data-v-a97efb8d>${ssrInterpolate(c.time)}</span><span class="text-label-md font-bold text-on-surface" data-v-a97efb8d>${ssrInterpolate(c.theater)}</span></div>`);
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: "/checkout/seat",
          class: "bg-primary-container text-on-primary-container p-3 rounded-full hover:scale-110 transition-transform"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`<span class="material-symbols-outlined" data-v-a97efb8d${_scopeId}>confirmation_number</span>`);
            } else {
              return [
                createVNode("span", { class: "material-symbols-outlined" }, "confirmation_number")
              ];
            }
          }),
          _: 2
        }, _parent));
        _push(`</div></div></div>`);
      });
      _push(`<!--]--></div></div></section><section class="px-6 md:px-margin-desktop py-12 pb-24" data-v-a97efb8d><div class="max-w-container-max mx-auto" data-v-a97efb8d><div class="flex justify-between items-end mb-10 border-b border-white/10 pb-4" data-v-a97efb8d><h2 class="font-headline-lg text-headline-lg text-on-surface" data-v-a97efb8d>Danh S\xE1ch R\u1EA1p &amp; Su\u1EA5t Chi\u1EBFu</h2><button class="flex items-center gap-2 text-label-md font-label-md text-primary-container hover:underline" data-v-a97efb8d><span class="material-symbols-outlined text-[18px]" data-v-a97efb8d>near_me</span> R\u1EA1p g\u1EA7n nh\u1EA5t </button></div><div class="space-y-12" data-v-a97efb8d><div class="flex flex-col lg:flex-row gap-8" data-v-a97efb8d><div class="lg:w-1/3" data-v-a97efb8d><div class="sticky top-24" data-v-a97efb8d><h3 class="font-headline-md text-headline-md text-on-surface mb-2" data-v-a97efb8d>CineAI Landmark 81</h3><p class="text-on-surface-variant text-body-md mb-4" data-v-a97efb8d>T\u1EA7ng B1, Vincom Landmark 81, 720A \u0110i\u1EC7n Bi\xEAn Ph\u1EE7, P.22, Q. B\xECnh Th\u1EA1nh, TP.HCM</p><div class="flex gap-3" data-v-a97efb8d><span class="px-3 py-1 bg-surface-container-high rounded-full text-label-sm font-label-sm border border-white/5" data-v-a97efb8d>IMAX Laser</span><span class="px-3 py-1 bg-surface-container-high rounded-full text-label-sm font-label-sm border border-white/5" data-v-a97efb8d>Dolby Atmos</span></div></div></div><div class="lg:w-2/3 space-y-8" data-v-a97efb8d><div class="p-6 rounded-2xl flex flex-col sm:flex-row gap-6" style="${ssrRenderStyle({ "background": "rgba(31,31,31,0.6)", "backdrop-filter": "blur(12px)", "border": "1px solid rgba(255,255,255,0.1)" })}" data-v-a97efb8d><div class="w-full sm:w-24 h-36 flex-shrink-0 overflow-hidden rounded-lg bg-surface-container-high" data-v-a97efb8d><img class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuA2DxRn9LX5nB6WnIAOYW9DKmmhcE6uElKuus5BETh5P_NWANMiCRx-rqmtYAxDlmZvgAlW0rr9mR3clYlocTp4sgJWWIFgiY8Egy-m9kjSdQzQefnKidmumxbH1SC9yMkJ1A1PxXkTbfQcwOPI6m6ANsupHZwga1EHmOkHe7PIiC0nuS1GtSiJXzpIxoy3xwRd24xogsNOCN8BrGsfp3cR-pSosZ4x8r2iKZc9n-CLepGxXjH2dYfNoob6raeE_deBtuqFCMduTY5Z" alt="Dune" data-v-a97efb8d></div><div class="flex-grow" data-v-a97efb8d><h4 class="font-headline-md text-headline-md text-on-surface mb-4" data-v-a97efb8d>Dune: Ph\u1EA7n Hai (T13)</h4><div class="space-y-4" data-v-a97efb8d><div data-v-a97efb8d><p class="text-label-sm font-label-sm text-primary-container mb-3 uppercase tracking-tighter font-bold" data-v-a97efb8d>IMAX 2D - Ph\u1EE5 \u0110\u1EC1</p><div class="flex flex-wrap gap-3" data-v-a97efb8d>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/checkout/seat",
        class: "px-6 py-2 bg-surface-container-highest rounded-lg border border-white/10 hover:border-primary-container hover:bg-primary-container/10 transition-all font-label-md text-label-md text-on-surface"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`19:30`);
          } else {
            return [
              createTextVNode("19:30")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/checkout/seat",
        class: "px-6 py-2 bg-surface-container-highest rounded-lg border border-white/10 hover:border-primary-container hover:bg-primary-container/10 transition-all font-label-md text-label-md text-on-surface"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`22:15`);
          } else {
            return [
              createTextVNode("22:15")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div></div><div data-v-a97efb8d><p class="text-label-sm font-label-sm text-on-surface-variant mb-3 uppercase tracking-tighter" data-v-a97efb8d>2D - Ph\u1EE5 \u0110\u1EC1</p><div class="flex flex-wrap gap-3" data-v-a97efb8d>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/checkout/seat",
        class: "px-6 py-2 bg-surface-container-highest rounded-lg border border-white/10 hover:border-primary-container hover:bg-primary-container/10 transition-all font-label-md text-label-md text-on-surface"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`18:00`);
          } else {
            return [
              createTextVNode("18:00")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`<span class="px-6 py-2 bg-surface-container-highest rounded-lg border border-white/10 font-label-md text-label-md text-on-surface-variant opacity-50 cursor-not-allowed" data-v-a97efb8d>21:00 (H\u1EBFt v\xE9)</span></div></div></div></div></div></div></div></div></div></section></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/showtimes.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const showtimes = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-a97efb8d"]]);

export { showtimes as default };
//# sourceMappingURL=showtimes-BPyLSh2g.mjs.map
