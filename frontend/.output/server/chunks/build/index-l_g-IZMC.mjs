import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, ref, computed, mergeProps, withCtx, createTextVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderAttr, ssrRenderList, ssrIncludeBooleanAttr, ssrLooseContain, ssrLooseEqual, ssrInterpolate, ssrRenderComponent, ssrRenderStyle } from 'vue/server-renderer';
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
    const { movies, loading } = storeToRefs(moviesStore);
    const searchKeyword = ref("");
    const selectedGenre = ref("T\u1EA5t c\u1EA3");
    const selectedYear = ref("T\u1EA5t c\u1EA3");
    const selectedCountry = ref("T\u1EA5t c\u1EA3");
    const activeSort = ref("M\u1EDBi nh\u1EA5t");
    const genresList = ["T\u1EA5t c\u1EA3", "H\xE0nh \u0111\u1ED9ng", "Vi\u1EC5n t\u01B0\u1EDFng", "Kinh d\u1ECB", "Ho\u1EA1t h\xECnh", "L\xE3ng m\u1EA1n", "H\xE0i h\u01B0\u1EDBc", "T\xE2m l\xFD", "T\xE0i li\u1EC7u"];
    const yearsList = ["T\u1EA5t c\u1EA3", "2026", "2025", "2024", "2023"];
    const countriesList = ["T\u1EA5t c\u1EA3", "Vi\u1EC7t Nam", "M\u1EF9", "H\xE0n Qu\u1ED1c", "Nh\u1EADt B\u1EA3n"];
    const sortsList = ["M\u1EDBi nh\u1EA5t", "\u0110\xE1nh gi\xE1 cao nh\u1EA5t", "T\xEAn A-Z", "T\xEAn Z-A"];
    const filteredMovies = computed(() => {
      let result = movies.value;
      if (searchKeyword.value.trim()) {
        const kw = searchKeyword.value.toLowerCase();
        result = result.filter((m) => m.title.toLowerCase().includes(kw));
      }
      if (selectedGenre.value !== "T\u1EA5t c\u1EA3") {
        result = result.filter((m) => m.genre.some((g) => g.toLowerCase().includes(selectedGenre.value.toLowerCase())));
      }
      if (activeSort.value === "\u0110\xE1nh gi\xE1 cao nh\u1EA5t") {
        result = [...result].sort((a, b) => parseFloat(b.rating || "0") - parseFloat(a.rating || "0"));
      } else if (activeSort.value === "T\xEAn A-Z") {
        result = [...result].sort((a, b) => a.title.localeCompare(b.title));
      } else if (activeSort.value === "T\xEAn Z-A") {
        result = [...result].sort((a, b) => b.title.localeCompare(a.title));
      }
      return result;
    });
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "min-h-screen pt-20" }, _attrs))}><section class="bg-surface-container-low border-b border-white/10 py-12"><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop"><div class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8"><div><h1 class="font-headline-xl text-headline-xl text-on-surface mb-2">Danh m\u1EE5c phim</h1><p class="text-on-surface-variant">Duy\u1EC7t qua h\xE0ng ng\xE0n b\u1ED9 phim \u0111ang chi\u1EBFu v\xE0 s\u1EAFp chi\u1EBFu t\u1EA1i c\xE1c c\u1EE5m r\u1EA1p.</p></div><div class="relative w-full md:w-80"><span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant">search</span><input${ssrRenderAttr("value", searchKeyword.value)} type="text" placeholder="T\xECm t\xEAn phim..." class="w-full bg-surface-container border border-white/10 rounded-xl py-3 pl-12 pr-4 text-on-surface placeholder:text-on-surface-variant outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container transition-all"></div></div><div class="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-2xl border border-white/10 bg-surface"><div class="flex flex-col gap-1.5"><label class="text-[10px] text-on-surface-variant uppercase font-bold tracking-wider px-2">Th\u1EC3 lo\u1EA1i</label><div class="relative"><select class="w-full bg-surface-container-high border-none rounded-lg py-2.5 px-3 text-sm text-on-surface appearance-none outline-none cursor-pointer"><!--[-->`);
      ssrRenderList(genresList, (g) => {
        _push(`<option${ssrIncludeBooleanAttr(Array.isArray(selectedGenre.value) ? ssrLooseContain(selectedGenre.value, null) : ssrLooseEqual(selectedGenre.value, null)) ? " selected" : ""}>${ssrInterpolate(g)}</option>`);
      });
      _push(`<!--]--></select><span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[18px]">expand_more</span></div></div><div class="flex flex-col gap-1.5"><label class="text-[10px] text-on-surface-variant uppercase font-bold tracking-wider px-2">Qu\u1ED1c gia</label><div class="relative"><select class="w-full bg-surface-container-high border-none rounded-lg py-2.5 px-3 text-sm text-on-surface appearance-none outline-none cursor-pointer"><!--[-->`);
      ssrRenderList(countriesList, (c) => {
        _push(`<option${ssrIncludeBooleanAttr(Array.isArray(selectedCountry.value) ? ssrLooseContain(selectedCountry.value, null) : ssrLooseEqual(selectedCountry.value, null)) ? " selected" : ""}>${ssrInterpolate(c)}</option>`);
      });
      _push(`<!--]--></select><span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[18px]">expand_more</span></div></div><div class="flex flex-col gap-1.5"><label class="text-[10px] text-on-surface-variant uppercase font-bold tracking-wider px-2">N\u0103m</label><div class="relative"><select class="w-full bg-surface-container-high border-none rounded-lg py-2.5 px-3 text-sm text-on-surface appearance-none outline-none cursor-pointer"><!--[-->`);
      ssrRenderList(yearsList, (y) => {
        _push(`<option${ssrIncludeBooleanAttr(Array.isArray(selectedYear.value) ? ssrLooseContain(selectedYear.value, null) : ssrLooseEqual(selectedYear.value, null)) ? " selected" : ""}>${ssrInterpolate(y)}</option>`);
      });
      _push(`<!--]--></select><span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[18px]">expand_more</span></div></div><div class="flex flex-col gap-1.5"><label class="text-[10px] text-on-surface-variant uppercase font-bold tracking-wider px-2">S\u1EAFp x\u1EBFp</label><div class="relative"><select class="w-full bg-surface-container-high border-none rounded-lg py-2.5 px-3 text-sm text-on-surface appearance-none outline-none cursor-pointer"><!--[-->`);
      ssrRenderList(sortsList, (s) => {
        _push(`<option${ssrIncludeBooleanAttr(Array.isArray(activeSort.value) ? ssrLooseContain(activeSort.value, null) : ssrLooseEqual(activeSort.value, null)) ? " selected" : ""}>${ssrInterpolate(s)}</option>`);
      });
      _push(`<!--]--></select><span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[18px]">expand_more</span></div></div></div></div></section><section class="max-w-container-max mx-auto px-6 md:px-margin-desktop py-12 pb-24"><div class="flex items-center justify-between mb-6"><h2 class="text-on-surface font-headline-md text-headline-md">T\xECm th\u1EA5y <span class="text-primary-container">${ssrInterpolate(filteredMovies.value.length)}</span> phim</h2><div class="flex gap-2 text-on-surface-variant"><button class="w-8 h-8 rounded bg-surface-container flex items-center justify-center text-primary-container"><span class="material-symbols-outlined text-[20px]">grid_view</span></button><button class="w-8 h-8 rounded bg-surface-container flex items-center justify-center hover:text-white transition-colors"><span class="material-symbols-outlined text-[20px]">view_list</span></button></div></div>`);
      if (filteredMovies.value.length === 0) {
        _push(`<div class="py-20 text-center flex flex-col items-center"><span class="material-symbols-outlined text-6xl text-white/10 mb-4">movie_off</span><p class="text-on-surface-variant text-lg">Kh\xF4ng t\xECm th\u1EA5y phim n\xE0o kh\u1EDBp v\u1EDBi b\u1ED9 l\u1ECDc.</p><button class="mt-4 text-primary-container hover:underline font-bold">X\xF3a b\u1ED9 l\u1ECDc</button></div>`);
      } else {
        _push(`<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6"><!--[-->`);
        ssrRenderList(filteredMovies.value, (m) => {
          _push(`<div class="flex flex-col group cursor-pointer"><div class="relative aspect-[2/3] rounded-xl overflow-hidden mb-4 bg-surface-container"><img class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"${ssrRenderAttr("src", m.poster)}${ssrRenderAttr("alt", m.title)}><div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center p-6 text-center">`);
          _push(ssrRenderComponent(_component_NuxtLink, {
            to: `/movies/${m.id}`,
            class: "bg-primary-container text-white px-4 py-2 rounded-lg font-label-sm text-label-sm font-bold hover:shadow-[0_0_25px_-5px_rgba(229,9,20,0.5)] transition-all"
          }, {
            default: withCtx((_, _push2, _parent2, _scopeId) => {
              if (_push2) {
                _push2(`Chi ti\u1EBFt`);
              } else {
                return [
                  createTextVNode("Chi ti\u1EBFt")
                ];
              }
            }),
            _: 2
          }, _parent));
          _push(`</div><div class="absolute top-2 right-2 px-2 py-1 rounded text-label-sm text-white flex items-center gap-1 font-bold" style="${ssrRenderStyle({ "background": "rgba(31,31,31,0.6)", "backdrop-filter": "blur(12px)", "border": "1px solid rgba(255,255,255,0.1)" })}"><span class="material-symbols-outlined text-[14px] text-primary" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}">star</span> ${ssrInterpolate(m.rating || "4.5")}</div><div class="absolute top-2 left-2 px-2 py-1 bg-surface-container-highest rounded text-[10px] text-white font-bold border border-white/5 uppercase">${ssrInterpolate(m.format || "2D")}</div></div><h4 class="font-label-md text-label-md group-hover:text-primary-container transition-colors text-on-surface">${ssrInterpolate(m.title)}</h4><p class="text-on-surface-variant font-label-sm text-label-sm truncate">${ssrInterpolate(m.genre.join(", "))}</p></div>`);
        });
        _push(`<!--]--></div>`);
      }
      _push(`</section></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/movies/index.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=index-l_g-IZMC.mjs.map
