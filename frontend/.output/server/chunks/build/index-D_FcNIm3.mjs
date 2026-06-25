import { defineComponent, ref, computed, mergeProps, unref, withCtx, createTextVNode, createVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrRenderList, ssrRenderClass, ssrInterpolate, ssrIncludeBooleanAttr, ssrLooseContain, ssrLooseEqual, ssrRenderStyle, ssrRenderAttr } from 'vue/server-renderer';
import { u as useMoviesStore } from './movies-Csr32Sbi.mjs';
import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { s as storeToRefs } from './server.mjs';
import { _ as _sfc_main$3 } from './MovieCard-CFTDOcJL.mjs';
import './api-rwjTvGO1.mjs';
import 'axios';
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

const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "SemanticSearch",
  __ssrInlineRender: true,
  setup(__props) {
    const searchInput = ref("");
    useMoviesStore();
    const suggestions = [
      "Phim vi\u1EC5n t\u01B0\u1EDFng v\u0169 tr\u1EE5 ho\xE0nh tr\xE1ng",
      "H\xE0nh \u0111\u1ED9ng k\u1ECBch t\xEDnh ngh\u1EB9t th\u1EDF",
      "Cyberpunk neon \u0111en t\u1ED1i m\u1EDBi nh\u1EA5t",
      "Phim c\u1EE7a \u0111\u1EA1o di\u1EC5n Christopher Nolan"
    ];
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "w-full max-w-3xl mx-auto my-8" }, _attrs))}><div class="relative group"><div class="absolute -inset-1 bg-gradient-to-r from-primary-container to-secondary-container rounded-full blur opacity-25 group-hover:opacity-40 transition duration-500"></div><div class="relative flex items-center glass-panel rounded-full p-2 border border-glass-stroke"><span class="material-symbols-outlined ml-4 text-primary-container animate-pulse" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}"> psychology </span><input${ssrRenderAttr("value", searchInput.value)} type="text" class="bg-transparent border-none focus:ring-0 w-full text-on-surface px-4 py-3 placeholder:text-on-surface-variant text-base" placeholder="Th\u1EED nh\u1EADp: &#39;phim vi\u1EC5n t\u01B0\u1EDFng v\u0169 tr\u1EE5&#39; ho\u1EB7c &#39;h\xE0nh \u0111\u1ED9ng k\u1ECBch t\xEDnh t\u1ED1i nay&#39;...">`);
      if (searchInput.value) {
        _push(`<button type="button" class="p-2 text-on-surface-variant hover:text-on-surface mr-2"><span class="material-symbols-outlined">close</span></button>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<button class="bg-primary-container text-on-primary-container px-8 py-3 rounded-full font-bold hover:scale-105 active:scale-95 transition-all flex items-center gap-2 red-glow"><span class="material-symbols-outlined text-sm">search</span> Kh\xE1m Ph\xE1 AI </button></div></div><div class="mt-4 flex flex-wrap justify-center gap-2"><span class="text-xs text-on-surface-variant flex items-center gap-1 py-1"><span class="material-symbols-outlined text-xs">auto_awesome</span> G\u1EE3i \xFD kh\u1EA9u l\u1EC7nh: </span><!--[-->`);
      ssrRenderList(suggestions, (sug) => {
        _push(`<button class="px-3.5 py-1 rounded-full bg-surface-container border border-glass-stroke text-on-surface-variant hover:text-primary-container hover:border-primary-container text-xs transition-colors">${ssrInterpolate(sug)}</button>`);
      });
      _push(`<!--]--></div></div>`);
    };
  }
});
const _sfc_setup$2 = _sfc_main$2.setup;
_sfc_main$2.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/ai/SemanticSearch.vue");
  return _sfc_setup$2 ? _sfc_setup$2(props, ctx) : void 0;
};
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "Recommendation",
  __ssrInlineRender: true,
  setup(__props) {
    const moviesStore = useMoviesStore();
    const { recommendations, loading } = storeToRefs(moviesStore);
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "my-12" }, _attrs))}><div class="flex items-center justify-between mb-8"><div><h2 class="font-headline-lg text-2xl md:text-3xl text-on-surface flex items-center gap-3"><span class="material-symbols-outlined text-secondary" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}"> auto_awesome </span> G\u1EE3i \xDD Phim T\u1EEB CineAI </h2><p class="text-on-surface-variant text-sm mt-1">C\xE1c t\xE1c ph\u1EA9m \u0111\u01B0\u1EE3c ph\xE2n t\xEDch v\xE0 \u0111\u1EC1 xu\u1EA5t theo th\xF3i quen xem phim c\u1EE7a b\u1EA1n.</p></div></div>`);
      if (unref(loading)) {
        _push(`<div class="grid grid-cols-1 md:grid-cols-2 gap-6"><!--[-->`);
        ssrRenderList(2, (n) => {
          _push(`<div class="animate-pulse bg-surface-container h-[200px] rounded-2xl border border-glass-stroke"></div>`);
        });
        _push(`<!--]--></div>`);
      } else {
        _push(`<div class="grid grid-cols-1 md:grid-cols-2 gap-8"><!--[-->`);
        ssrRenderList(unref(recommendations), (movie) => {
          _push(`<div class="group relative rounded-2xl overflow-hidden aspect-[16/9] border border-glass-stroke hover:border-primary-container/40 transition-all duration-300 shadow-lg"><img${ssrRenderAttr("src", movie.poster)}${ssrRenderAttr("alt", movie.title)} class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"><div class="absolute inset-0 bg-gradient-to-t from-surface via-surface/60 to-transparent p-6 flex flex-col justify-end"><div class="mb-4"><span class="bg-secondary-container/20 border border-secondary-container/30 text-secondary text-[11px] font-bold px-3 py-1 rounded-full inline-flex items-center gap-1.5 backdrop-blur-md mb-3"><span class="material-symbols-outlined text-xs">psychology</span> AI Match </span><h3 class="font-headline-md text-xl md:text-2xl font-bold text-on-surface mb-2">${ssrInterpolate(movie.title)}</h3><p class="text-xs md:text-sm text-on-surface-variant line-clamp-2 leading-relaxed">${ssrInterpolate(movie.description)}</p></div><div class="flex items-center justify-between border-t border-glass-stroke/40 pt-4 mt-1"><div class="flex items-center gap-4 text-xs font-semibold text-on-surface-variant"><span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm text-yellow-500" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}">star</span> ${ssrInterpolate(movie.rating.toFixed(1))}</span><span>${ssrInterpolate(movie.genre.join(", "))}</span></div>`);
          _push(ssrRenderComponent(_component_NuxtLink, {
            to: `/movies/${movie.id}`,
            class: "bg-primary-container hover:bg-opacity-90 text-on-primary-container px-5 py-2 rounded-xl text-xs font-bold transition-all hover:scale-105 active:scale-95 flex items-center gap-1.5 red-glow"
          }, {
            default: withCtx((_, _push2, _parent2, _scopeId) => {
              if (_push2) {
                _push2(` \u0110\u1EB7t V\xE9 <span class="material-symbols-outlined text-xs"${_scopeId}>arrow_forward</span>`);
              } else {
                return [
                  createTextVNode(" \u0110\u1EB7t V\xE9 "),
                  createVNode("span", { class: "material-symbols-outlined text-xs" }, "arrow_forward")
                ];
              }
            }),
            _: 2
          }, _parent));
          _push(`</div></div><div class="absolute top-4 left-4 right-4 bg-black/50 backdrop-blur-md border border-glass-stroke/50 p-2.5 rounded-xl text-xs text-secondary-fixed opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"> \u{1F4A1} ${ssrInterpolate(movie.aiMatchReason)}</div></div>`);
        });
        _push(`<!--]--></div>`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup$1 = _sfc_main$1.setup;
_sfc_main$1.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/ai/Recommendation.vue");
  return _sfc_setup$1 ? _sfc_setup$1(props, ctx) : void 0;
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "index",
  __ssrInlineRender: true,
  setup(__props) {
    const moviesStore = useMoviesStore();
    const { movies, loading } = storeToRefs(moviesStore);
    const selectedGenre = ref("T\u1EA5t C\u1EA3 Phim");
    const activeSort = ref("\u0110\u1ED9 Ph\xF9 H\u1EE3p AI");
    const genresList = [
      "T\u1EA5t C\u1EA3 Phim",
      "H\xE0nh \u0110\u1ED9ng",
      "Vi\u1EC5n T\u01B0\u1EDFng",
      "K\u1ECBch T\xEDnh",
      "T\xE2m L\xFD",
      "Cyberpunk",
      "Neon-Noir"
    ];
    const filteredMovies = computed(() => {
      if (selectedGenre.value === "T\u1EA5t C\u1EA3 Phim") {
        return movies.value;
      }
      return movies.value.filter(
        (movie) => movie.genre.some((g) => g.toLowerCase() === selectedGenre.value.toLowerCase())
      );
    });
    return (_ctx, _push, _parent, _attrs) => {
      const _component_AiSemanticSearch = _sfc_main$2;
      const _component_AiRecommendation = _sfc_main$1;
      const _component_MovieCard = _sfc_main$3;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "pb-16" }, _attrs))}><section class="relative py-12 flex items-center overflow-hidden bg-gradient-to-b from-[#161718] to-background"><div class="relative z-10 max-w-container-max mx-auto px-6 md:px-margin-desktop w-full text-center"><h1 class="font-headline-xl text-3xl md:text-5xl font-bold mb-4 text-on-surface"> Tr\u1EA3i Nghi\u1EC7m Tr\xED Tu\u1EC7 <span class="text-primary-container">\u0110i\u1EC7n \u1EA2nh</span></h1><p class="text-xs md:text-sm text-on-surface-variant max-w-lg mx-auto mb-6"> T\xECm ki\u1EBFm l\u1ECBch chi\u1EBFu b\u1EB1ng ng\xF4n ng\u1EEF t\u1EF1 nhi\xEAn th\xF4ng qua AI v\xE0 nh\u1EADn ngay su\u1EA5t chi\u1EBFu ph\xF9 h\u1EE3p nh\u1EA5t. </p>`);
      _push(ssrRenderComponent(_component_AiSemanticSearch, null, null, _parent));
      _push(`</div></section><section class="bg-surface-container-lowest/30 border-y border-glass-stroke/50 py-8"><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop">`);
      _push(ssrRenderComponent(_component_AiRecommendation, null, null, _parent));
      _push(`</div></section><section class="py-12"><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop"><div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-glass-stroke pb-6 mb-8"><div class="flex items-center gap-2 overflow-x-auto hide-scrollbar w-full md:w-auto pb-2 md:pb-0"><!--[-->`);
      ssrRenderList(genresList, (genre) => {
        _push(`<button class="${ssrRenderClass([selectedGenre.value === genre ? "bg-primary-container text-on-primary-container shadow-md red-glow" : "bg-surface-container border border-glass-stroke text-on-surface-variant hover:text-on-surface hover:bg-white/5", "flex-shrink-0 px-4 py-2 rounded-xl text-xs font-bold transition-all"])}">${ssrInterpolate(genre)}</button>`);
      });
      _push(`<!--]--></div><div class="flex items-center gap-2 self-end md:self-auto flex-shrink-0"><span class="text-xs text-on-surface-variant font-medium">S\u1EAFp x\u1EBFp:</span><select class="bg-surface-container border border-glass-stroke rounded-xl text-on-surface font-label-md text-xs py-2 px-4 outline-none focus:ring-1 focus:ring-primary-container"><option${ssrIncludeBooleanAttr(Array.isArray(activeSort.value) ? ssrLooseContain(activeSort.value, null) : ssrLooseEqual(activeSort.value, null)) ? " selected" : ""}>\u0110\u1ED9 Ph\xF9 H\u1EE3p AI</option><option${ssrIncludeBooleanAttr(Array.isArray(activeSort.value) ? ssrLooseContain(activeSort.value, null) : ssrLooseEqual(activeSort.value, null)) ? " selected" : ""}>Ng\xE0y Ph\xE1t H\xE0nh</option><option${ssrIncludeBooleanAttr(Array.isArray(activeSort.value) ? ssrLooseContain(activeSort.value, null) : ssrLooseEqual(activeSort.value, null)) ? " selected" : ""}>\u0110i\u1EC3m \u0110\xE1nh Gi\xE1</option></select></div></div>`);
      if (unref(loading)) {
        _push(`<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6"><!--[-->`);
        ssrRenderList(4, (n) => {
          _push(`<div class="animate-pulse bg-surface-container h-[350px] rounded-2xl border border-glass-stroke"></div>`);
        });
        _push(`<!--]--></div>`);
      } else if (unref(filteredMovies).length === 0) {
        _push(`<div class="py-16 text-center text-on-surface-variant"><span class="material-symbols-outlined text-[48px] mb-2 text-on-surface-variant">search_off</span><p class="text-sm font-medium">Kh\xF4ng t\xECm th\u1EA5y b\u1ED9 phim n\xE0o ph\xF9 h\u1EE3p v\u1EDBi b\u1ED9 l\u1ECDc hi\u1EC7n t\u1EA1i.</p></div>`);
      } else {
        _push(`<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6"><!--[-->`);
        ssrRenderList(unref(filteredMovies), (movie) => {
          _push(ssrRenderComponent(_component_MovieCard, {
            key: movie.id,
            movie
          }, null, _parent));
        });
        _push(`<!--]--></div>`);
      }
      _push(`</div></section></div>`);
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
//# sourceMappingURL=index-D_FcNIm3.mjs.map
