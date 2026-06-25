import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, ref, computed, mergeProps, unref, withCtx, createTextVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrRenderAttr, ssrInterpolate, ssrRenderStyle, ssrRenderList, ssrRenderClass } from 'vue/server-renderer';
import { useRoute } from 'vue-router';
import { s as storeToRefs } from './server.mjs';
import { u as useMoviesStore } from './movies-Csr32Sbi.mjs';
import { u as useTicketsStore } from './tickets-DLGytZJQ.mjs';
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
import './api-rwjTvGO1.mjs';
import 'axios';

const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "[id]",
  __ssrInlineRender: true,
  setup(__props) {
    useRoute();
    const moviesStore = useMoviesStore();
    useTicketsStore();
    const { activeMovie, activeShowtimes, loading } = storeToRefs(moviesStore);
    const selectedBranch = ref("");
    const selectedDate = ref("");
    const branches = computed(() => {
      const list = activeShowtimes.value.map((s) => s.branchName);
      return [...new Set(list)];
    });
    const dates = computed(() => {
      const list = activeShowtimes.value.filter((s) => s.branchName === selectedBranch.value).map((s) => s.date);
      return [...new Set(list)];
    });
    const filteredShowtimes = computed(() => {
      return activeShowtimes.value.filter(
        (s) => s.branchName === selectedBranch.value && s.date === selectedDate.value
      );
    });
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "pb-16" }, _attrs))}>`);
      if (unref(loading)) {
        _push(`<div class="py-24 text-center animate-pulse text-on-surface-variant"> \u0110ang t\u1EA3i chi ti\u1EBFt phim v\xE0 l\u1ECBch chi\u1EBFu... </div>`);
      } else if (!unref(activeMovie)) {
        _push(`<div class="py-24 text-center text-on-surface-variant"> \u26A0\uFE0F Kh\xF4ng t\xECm th\u1EA5y th\xF4ng tin b\u1ED9 phim n\xE0y tr\xEAn h\u1EC7 th\u1ED1ng. <div class="mt-4">`);
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: "/movies",
          class: "text-primary-container font-bold hover:underline"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`Quay l\u1EA1i danh m\u1EE5c`);
            } else {
              return [
                createTextVNode("Quay l\u1EA1i danh m\u1EE5c")
              ];
            }
          }),
          _: 1
        }, _parent));
        _push(`</div></div>`);
      } else {
        _push(`<div><section class="relative w-full h-[40vh] md:h-[50vh] overflow-hidden"><div class="absolute inset-0 z-0"><img${ssrRenderAttr("src", unref(activeMovie).poster)}${ssrRenderAttr("alt", unref(activeMovie).title)} class="w-full h-full object-cover blur-[8px] scale-105 opacity-30"><div class="absolute inset-0 bg-background/80"></div><div class="absolute inset-0 gradient-fade-bottom"></div></div><div class="relative z-10 max-w-container-max mx-auto px-6 md:px-margin-desktop h-full flex items-end pb-12"><div class="flex flex-col md:flex-row items-center md:items-end gap-8 w-full"><div class="w-48 md:w-56 aspect-[2/3] rounded-2xl overflow-hidden border border-glass-stroke shadow-2xl relative -mb-16 md:-mb-24 flex-shrink-0 z-20"><img${ssrRenderAttr("src", unref(activeMovie).poster)}${ssrRenderAttr("alt", unref(activeMovie).title)} class="w-full h-full object-cover"></div><div class="text-center md:text-left flex-grow"><span class="bg-primary-container/10 border border-primary-container/20 text-primary-container text-xs font-bold px-3.5 py-1 rounded-full inline-block mb-3">${ssrInterpolate(unref(activeMovie).format.join(" | "))}</span><h1 class="font-headline-xl text-3xl md:text-5xl font-black text-on-surface tracking-tight mb-4">${ssrInterpolate(unref(activeMovie).title)}</h1><div class="flex flex-wrap items-center justify-center md:justify-start gap-4 text-xs font-semibold text-on-surface-variant"><span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm text-yellow-500" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}">star</span> ${ssrInterpolate(unref(activeMovie).rating.toFixed(1))}</span><span>\u2022</span><span>${ssrInterpolate(unref(activeMovie).duration)} ph\xFAt</span><span>\u2022</span><span>${ssrInterpolate(unref(activeMovie).genre.join(", "))}</span><span>\u2022</span><span>Kh\u1EDFi chi\u1EBFu: ${ssrInterpolate(unref(activeMovie).releaseDate)}</span></div></div></div></div></section><section class="max-w-container-max mx-auto px-6 md:px-margin-desktop pt-24 md:pt-32 grid grid-cols-1 lg:grid-cols-12 gap-12"><div class="lg:col-span-7 space-y-8"><div><h3 class="font-headline-md text-xl font-bold mb-4 flex items-center gap-2"><span class="material-symbols-outlined text-primary-container">play_circle</span> Official Trailer </h3><div class="aspect-video w-full rounded-2xl overflow-hidden border border-glass-stroke bg-black shadow-lg"><iframe${ssrRenderAttr("src", unref(activeMovie).trailer)} title="Movie Trailer" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen class="w-full h-full"></iframe></div></div><div><h3 class="font-headline-md text-xl font-bold mb-3">T\xF3m t\u1EAFt phim</h3><p class="text-sm text-on-surface-variant leading-relaxed whitespace-pre-line">${ssrInterpolate(unref(activeMovie).description)}</p></div><div class="grid grid-cols-1 md:grid-cols-2 gap-6 bg-surface-container/30 border border-glass-stroke/40 p-6 rounded-2xl"><div><span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">\u0110\u1EA1o di\u1EC5n</span><span class="text-sm font-semibold text-on-surface">${ssrInterpolate(unref(activeMovie).director)}</span></div><div><span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Di\u1EC5n vi\xEAn ch\xEDnh</span><span class="text-sm font-semibold text-on-surface">${ssrInterpolate(unref(activeMovie).cast.join(", "))}</span></div></div></div><div class="lg:col-span-5 space-y-6"><div class="glass-panel border border-glass-stroke rounded-2xl p-6 md:p-8"><h3 class="font-headline-md text-xl font-bold mb-6 flex items-center gap-2"><span class="material-symbols-outlined text-secondary">schedule</span> L\u1ECBch Chi\u1EBFu &amp; \u0110\u1EB7t V\xE9 </h3><div class="space-y-4 mb-6"><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Ch\u1ECDn C\u1EE5m R\u1EA1p</label>`);
        if (branches.value.length === 0) {
          _push(`<div class="text-sm text-on-surface-variant py-4 text-center"> Kh\xF4ng c\xF3 l\u1ECBch chi\u1EBFu kh\u1EA3 d\u1EE5ng cho phim n\xE0y. </div>`);
        } else {
          _push(`<div class="flex flex-col gap-2"><!--[-->`);
          ssrRenderList(branches.value, (branch) => {
            _push(`<button class="${ssrRenderClass([selectedBranch.value === branch ? "bg-purple-950 border-purple-500 text-purple-200" : "bg-surface border-glass-stroke text-on-surface-variant hover:text-on-surface hover:bg-white/5", "w-full text-left px-4 py-3 rounded-xl border text-xs font-bold transition-all flex items-center justify-between"])}"><span>${ssrInterpolate(branch)}</span><span class="material-symbols-outlined text-sm">chevron_right</span></button>`);
          });
          _push(`<!--]--></div>`);
        }
        _push(`</div>`);
        if (branches.value.length > 0) {
          _push(`<div class="space-y-4 mb-6"><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Ch\u1ECDn Ng\xE0y</label><div class="flex items-center gap-2 overflow-x-auto hide-scrollbar pb-2"><!--[-->`);
          ssrRenderList(dates.value, (date) => {
            _push(`<button class="${ssrRenderClass([selectedDate.value === date ? "bg-primary-container border-primary-container text-white" : "bg-surface border-glass-stroke text-on-surface-variant hover:text-on-surface", "flex-shrink-0 px-4 py-2.5 rounded-xl border text-xs font-bold transition-all"])}">${ssrInterpolate(date)}</button>`);
          });
          _push(`<!--]--></div></div>`);
        } else {
          _push(`<!---->`);
        }
        if (branches.value.length > 0) {
          _push(`<div class="space-y-4"><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Su\u1EA5t Chi\u1EBFu Kh\u1EA3 D\u1EE5ng</label><div class="grid grid-cols-2 gap-3"><!--[-->`);
          ssrRenderList(filteredShowtimes.value, (showtime) => {
            _push(`<button class="bg-surface-container border border-glass-stroke rounded-xl p-4 text-center hover:border-primary-container hover:scale-[1.02] active:scale-95 transition-all text-left"><span class="block text-lg font-black text-on-surface tracking-tight">${ssrInterpolate(showtime.time)}</span><span class="text-[10px] font-bold text-on-surface-variant block mt-1 uppercase">${ssrInterpolate(showtime.screenName)}</span><span class="text-xs text-primary-fixed-dim block mt-1.5 font-bold">${ssrInterpolate(showtime.price.toLocaleString())} VN\u0110</span></button>`);
          });
          _push(`<!--]--></div></div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div></div></section></div>`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/movies/[id].vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=_id_-DvlQX7ew.mjs.map
