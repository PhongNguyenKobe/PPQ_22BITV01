import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, ref, mergeProps, withCtx, createTextVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderStyle, ssrRenderAttr, ssrRenderList, ssrInterpolate, ssrRenderClass, ssrIncludeBooleanAttr, ssrLooseContain, ssrLooseEqual, ssrRenderComponent } from 'vue/server-renderer';
import { u as useMoviesStore } from './movies-Csr32Sbi.mjs';
import { s as storeToRefs } from './server.mjs';
import '../_/nitro.mjs';
import 'node:http';
import 'node:https';
import 'node:events';
import 'node:buffer';
import 'node:fs';
import 'node:path';
import 'node:crypto';
import 'node:url';
import './api-rwjTvGO1.mjs';
import 'axios';
import '../routes/renderer.mjs';
import 'vue-bundle-renderer/runtime';
import 'unhead/server';
import 'devalue';
import 'unhead/utils';
import 'unhead/plugins';
import 'vue-router';

const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "ai-discovery",
  __ssrInlineRender: true,
  setup(__props) {
    const moviesStore = useMoviesStore();
    const { movies } = storeToRefs(moviesStore);
    const searchInput = ref("");
    const selectedGenre = ref("T\u1EA5t c\u1EA3 phim");
    const activeSort = ref("\u0110\u1ED9 ph\xF9 h\u1EE3p AI");
    const genres = ["T\u1EA5t c\u1EA3 phim", "H\xE0nh \u0110\u1ED9ng", "Vi\u1EC5n T\u01B0\u1EDFng", "T\xE2m L\xFD", "K\u1ECBch T\xEDnh", "Cyberpunk", "Neon-Noir", "Phim T\xE0i Li\u1EC7u"];
    const sorts = ["\u0110\u1ED9 ph\xF9 h\u1EE3p AI", "Ng\xE0y Ph\xE1t H\xE0nh", "Ph\u1ED5 Bi\u1EBFn"];
    const suggestions = [
      "Phim vi\u1EC5n t\u01B0\u1EDFng v\u0169 tr\u1EE5 ho\xE0nh tr\xE1ng",
      "H\xE0nh \u0111\u1ED9ng k\u1ECBch t\xEDnh ngh\u1EB9t th\u1EDF",
      "Cyberpunk neon \u0111en t\u1ED1i m\u1EDBi nh\u1EA5t",
      "Phim c\u1EE7a \u0111\u1EA1o di\u1EC5n Christopher Nolan"
    ];
    const aiMovies = [
      { title: "Techno-Dystopia: T\xEDn Hi\u1EC7u Cu\u1ED1i", genre: "Vi\u1EC5n T\u01B0\u1EDFng", score: "98%", badge: "AI L\u1EF1a Ch\u1ECDn H\xE0ng \u0110\u1EA7u", img: "https://lh3.googleusercontent.com/aida-public/AB6AXuApX8V3ac0arkT6yk4kzv8Yw7ILjPdcDl879XQvy3C9I2bt0qO4ksMSkGKyM4yQnmcCtTvEX1oDLfr1O2aZnTYg3wQ9VBnBBnl4KLMfkg0R_LqPzSH-YxlvxiLSyXrVFUTbbKBCS2gWfT2o7SGmREu5rzFkfKAPJc6ZqlgQ1-ZjWchKP5pRsXzqGX90XfLy7FPQicSCMja312CH216FNHMpZ61TdiwsL7akjZZ-CGT-4de7l6oc9iVO8UoAQCJHsjIOzD_ki3m0VQHU" },
      { title: "Ti\u1EBFng Vang C\u1EE7a Thu\u1EADt To\xE1n", genre: "T\xE2m L\xFD", score: "95%", badge: "Tuy\u1EC7t T\xE1c", img: "https://lh3.googleusercontent.com/aida-public/AB6AXuDBKGmSMrGByy2OJMqN0m9EMoxzjyatedzRHy4_2jzbNm103d-rNfYmTRIsK9aCUl6vDhdxoxHJ8r4ebmTn9qw5frwtVPSDwa0ZzGwJtryO-Ai17TtL9_vmfCsXTtJaRkG5b1A_94BaAd2MZwoXRgfKSH0qKUMJrDO8-DcSjqd7vcOE44R6GmmUzhQRfcZJ_ldfXW4Xz2oZCT-J5MrMjI9WZO2HrXUZmgEW-k6a5Qu_KJGqP4FgU4AGiG7x8CGJWtcWx0FFmUMOKUn7" }
    ];
    const movieGrid = [
      { title: "Gi\u1EA5c M\u01A1 Robot", genre: "Vi\u1EC5n T\u01B0\u1EDFng", rating: "8.9", img: "https://lh3.googleusercontent.com/aida-public/AB6AXuAIzDZyiO4JqUEg_LDomlwA8haE6bBgMLvOdO2ZRHCvG-oBi841ymz-C4vv7lEiHWaVmWXDbOpdb-IgAVOtUH7vlK70p2ZQqzrXOKn6rjL3n8gobVlVpLNvG1rbUqGd_iGTA1fSJfbeTeWNAQ3LXP2uFuC6oXp78nqR4fu9g_jnAOvHpz8Cv1gUZQ5-HGv3SntcXdHwwFNcu_pqjLzzpe3hoXP9K7liTJ7p_zW6rnF9aZJ8y0wMljdK0cGR2Ph-tQPBWoEFyvYcIq9G" },
      { title: "Th\xE0nh Ph\u1ED1 Neo", genre: "Cyberpunk", rating: "9.1", img: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=800&auto=format&fit=crop" },
      { title: "\u0110\u01B0\u1EDDng H\u1EADu To\xE0n", genre: "H\xE0nh \u0110\u1ED9ng", rating: "8.5", img: "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=800&auto=format&fit=crop" },
      { title: "Ng\u01B0\u1EDDi \u0110\u1ECF B\u1EA5t B\u1EA1i", genre: "Vi\u1EC5n T\u01B0\u1EDFng", rating: "7.8", img: "https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=800&auto=format&fit=crop" },
      { title: "Bi\u1EBFn C\u1ED1 2099", genre: "Vi\u1EC5n T\u01B0\u1EDFng", rating: "8.2", img: "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=800&auto=format&fit=crop" }
    ];
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "min-h-screen pt-20" }, _attrs))}><section class="relative h-[400px] flex items-center overflow-hidden"><div class="absolute inset-0 z-0"><div class="w-full h-full bg-[url(&#39;https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&amp;w=2070&amp;auto=format&amp;fit=crop&#39;)] bg-cover bg-center"></div><div class="absolute inset-0" style="${ssrRenderStyle({ "background": "rgba(18,20,20,0.8)" })}"></div><div class="absolute inset-0" style="${ssrRenderStyle({ "background": "linear-gradient(to top,rgba(18,20,20,1) 0%,rgba(18,20,20,0) 100%)" })}"></div></div><div class="relative z-10 max-w-container-max mx-auto px-6 md:px-margin-desktop w-full text-center"><div class="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6" style="${ssrRenderStyle({ "background": "rgba(229,9,20,0.1)", "border": "1px solid rgba(229,9,20,0.2)" })}"><span class="material-symbols-outlined text-primary-container text-[20px] animate-pulse">psychology</span><span class="text-label-sm font-bold tracking-wider uppercase text-primary-container">Kh\xE1m Ph\xE1 AI</span></div><h1 class="font-headline-xl text-headline-xl mb-6 text-on-surface">Tr\u1EA3i Nghi\u1EC7m Tr\xED Tu\u1EC7 <span class="text-primary-container">\u0110i\u1EC7n \u1EA2nh</span></h1><div class="max-w-2xl mx-auto relative group"><div class="absolute -inset-1 rounded-full blur opacity-25 group-hover:opacity-50 transition duration-1000" style="${ssrRenderStyle({ "background": "linear-gradient(to right,#e50914,#8a2be2)" })}"></div><div class="relative flex items-center rounded-full p-2" style="${ssrRenderStyle({ "background": "rgba(31,31,31,0.6)", "backdrop-filter": "blur(12px)", "border": "1px solid rgba(255,255,255,0.1)" })}"><span class="material-symbols-outlined ml-4 text-primary-container" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}">psychology</span><input${ssrRenderAttr("value", searchInput.value)} class="bg-transparent border-none focus:ring-0 w-full text-on-surface px-4 py-3 placeholder:text-on-surface-variant outline-none" placeholder="Th\u1EED &#39;T\xECm phim trinh th\xE1m v\u1EC1 AI&#39;..." type="text"><button class="bg-primary-container text-on-primary-container px-8 py-3 rounded-full font-bold hover:scale-105 transition-all flex items-center gap-2 shadow-[0_0_20px_-5px_rgba(229,9,20,0.5)]"> Kh\xE1m Ph\xE1 </button></div></div><div class="mt-8 flex flex-wrap justify-center gap-3"><span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Xu h\u01B0\u1EDBng:</span><!--[-->`);
      ssrRenderList(suggestions, (sug) => {
        _push(`<button class="px-4 py-1 rounded-full text-on-surface text-label-md hover:bg-white/10 transition-colors" style="${ssrRenderStyle({ "background": "rgba(31,31,31,0.6)", "backdrop-filter": "blur(12px)", "border": "1px solid rgba(255,255,255,0.1)" })}">${ssrInterpolate(sug)}</button>`);
      });
      _push(`<!--]--></div></div></section><section class="py-6 sticky top-20 z-40" style="${ssrRenderStyle({ "background": "rgba(18,20,20,0.8)", "backdrop-filter": "blur(16px)" })}"><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop"><div class="flex items-center gap-4 overflow-x-auto pb-2" style="${ssrRenderStyle({ "scrollbar-width": "none" })}"><!--[-->`);
      ssrRenderList(genres, (g) => {
        _push(`<button class="${ssrRenderClass([selectedGenre.value === g ? "bg-primary-container text-on-primary-container" : "text-on-surface hover:bg-white/10 transition-colors", "flex-shrink-0 px-6 py-2 rounded-lg font-label-md text-label-md transition-all"])}" style="${ssrRenderStyle(selectedGenre.value === g ? "" : "background:rgba(31,31,31,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1)")}">${ssrInterpolate(g)}</button>`);
      });
      _push(`<!--]--><div class="ml-auto flex items-center gap-2 pl-4 shrink-0"><span class="font-label-md text-label-md text-on-surface-variant whitespace-nowrap">S\u1EAFp x\u1EBFp:</span><select class="bg-transparent border border-white/10 rounded-lg text-on-surface font-label-md py-1 px-3 outline-none"><!--[-->`);
      ssrRenderList(sorts, (s) => {
        _push(`<option${ssrIncludeBooleanAttr(Array.isArray(activeSort.value) ? ssrLooseContain(activeSort.value, null) : ssrLooseEqual(activeSort.value, null)) ? " selected" : ""}>${ssrInterpolate(s)}</option>`);
      });
      _push(`<!--]--></select></div></div></div></section><section class="py-16 bg-surface-container-lowest"><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop"><div class="flex items-center justify-between mb-12"><div><h2 class="font-headline-lg text-headline-lg text-on-surface flex items-center gap-3"><span class="material-symbols-outlined text-primary-container" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}">auto_awesome</span> G\u1EE3i \xDD Cho B\u1EA1n </h2><p class="text-on-surface-variant mt-2">Tuy\u1EC3n t\u1EADp \u0111\u01B0\u1EE3c AI l\u1EF1a ch\u1ECDn d\u1EF1a tr\xEAn h\u1ED3 s\u01A1 xem phim c\u1EE7a b\u1EA1n.</p></div>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "text-primary-container font-label-md hover:underline"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Xem T\u1EA5t C\u1EA3`);
          } else {
            return [
              createTextVNode("Xem T\u1EA5t C\u1EA3")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div><div class="grid grid-cols-1 md:grid-cols-2 gap-8"><!--[-->`);
      ssrRenderList(aiMovies, (m) => {
        _push(`<div class="group relative rounded-2xl overflow-hidden" style="${ssrRenderStyle({ "aspect-ratio": "16/9" })}"><img${ssrRenderAttr("src", m.img)}${ssrRenderAttr("alt", m.title)} class="w-full h-full object-cover"><div class="absolute inset-0 flex flex-col justify-end p-8" style="${ssrRenderStyle({ "background": "linear-gradient(to top,rgba(18,20,20,0.95) 0%,transparent 100%)" })}"><div class="flex items-center gap-2 mb-4"><span class="bg-secondary-container text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-widest">${ssrInterpolate(m.badge)}</span><span class="text-white/80 text-sm">${ssrInterpolate(m.score)} T\u01B0\u01A1ng Th\xEDch</span></div><h3 class="font-headline-lg text-headline-lg text-white mb-2">${ssrInterpolate(m.title)}</h3><div class="flex items-center gap-4"><button class="bg-primary-container text-on-primary-container px-6 py-2 rounded-lg font-bold hover:scale-105 transition-all">Xem Trailer</button>`);
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: `/movies/1`,
          class: "px-6 py-2 rounded-lg font-bold hover:bg-white/10 transition-colors text-white border border-white/20"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`Chi Ti\u1EBFt`);
            } else {
              return [
                createTextVNode("Chi Ti\u1EBFt")
              ];
            }
          }),
          _: 2
        }, _parent));
        _push(`</div></div></div>`);
      });
      _push(`<!--]--></div></div></section><section class="py-16"><div class="max-w-container-max mx-auto px-6 md:px-margin-desktop"><h2 class="font-headline-lg text-headline-lg text-on-surface mb-12">Kh\xE1m Ph\xE1 Phim</h2><div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6"><!--[-->`);
      ssrRenderList(movieGrid, (m) => {
        _push(`<div class="relative rounded-xl overflow-hidden group hover:scale-105 transition-transform duration-300 cursor-pointer" style="${ssrRenderStyle({ "aspect-ratio": "2/3" })}"><img${ssrRenderAttr("src", m.img)}${ssrRenderAttr("alt", m.title)} class="w-full h-full object-cover"><div class="absolute inset-0 flex flex-col justify-end p-4" style="${ssrRenderStyle({ "background": "linear-gradient(to top,rgba(0,0,0,0.9) 0%,rgba(0,0,0,0.3) 50%,transparent 100%)" })}"><div class="flex justify-between items-center mb-2"><span class="text-[#8a2be2] text-xs font-bold uppercase">${ssrInterpolate(m.genre)}</span><div class="flex items-center gap-1 px-2 py-1 rounded" style="${ssrRenderStyle({ "background": "rgba(52,53,53,0.9)" })}"><span class="material-symbols-outlined text-[14px] text-primary" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}">star</span><span class="text-white text-[12px] font-bold">${ssrInterpolate(m.rating)}</span></div></div><h4 class="font-headline-md text-[14px] text-white mb-3">${ssrInterpolate(m.title)}</h4>`);
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: "/checkout/seat",
          class: "w-full bg-primary-container text-on-primary-container py-2 rounded-lg text-label-md font-bold text-center block opacity-0 group-hover:opacity-100 transition-opacity"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(` \u0110\u1EB7t ch\u1ED7 `);
            } else {
              return [
                createTextVNode(" \u0110\u1EB7t ch\u1ED7 ")
              ];
            }
          }),
          _: 2
        }, _parent));
        _push(`</div></div>`);
      });
      _push(`<!--]--></div></div></section></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/ai-discovery.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=ai-discovery-BXZUObQt.mjs.map
