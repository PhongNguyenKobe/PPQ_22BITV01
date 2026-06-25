import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, mergeProps, withCtx, createTextVNode, createVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderAttr, ssrInterpolate, ssrRenderComponent, ssrRenderList, ssrRenderStyle } from 'vue/server-renderer';

const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "MovieCard",
  __ssrInlineRender: true,
  props: {
    movie: {}
  },
  setup(__props) {
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "group relative bg-surface-container-low border border-glass-stroke rounded-2xl overflow-hidden shadow-lg hover:border-primary-container/30 transition-all duration-300 flex flex-col h-full" }, _attrs))}><div class="relative overflow-hidden aspect-[2/3] w-full bg-surface-container-high"><img${ssrRenderAttr("src", __props.movie.poster)}${ssrRenderAttr("alt", __props.movie.title)} class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"><div class="absolute inset-0 bg-black/80 p-4 opacity-0 group-hover:opacity-100 transition-all duration-300 flex flex-col justify-between"><div><span class="text-xs text-secondary font-bold flex items-center gap-1 mb-2"><span class="material-symbols-outlined text-xs">auto_awesome</span> CineAI Match </span><p class="text-xs text-on-surface-variant line-clamp-6 leading-relaxed">${ssrInterpolate(__props.movie.description)}</p></div><div class="space-y-2"><div class="text-xs text-on-surface-variant flex flex-wrap gap-1"><span class="text-white font-semibold">\u0110\u1EA1o di\u1EC5n:</span><span>${ssrInterpolate(__props.movie.director)}</span></div>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: `/movies/${__props.movie.id}`,
        class: "w-full bg-primary-container text-on-primary-container py-2.5 rounded-xl font-bold text-center block text-sm transition-all hover:scale-105 active:scale-95 red-glow"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` Xem Chi Ti\u1EBFt `);
          } else {
            return [
              createTextVNode(" Xem Chi Ti\u1EBFt ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div></div><div class="absolute top-3 left-3 flex flex-col gap-1 z-10"><!--[-->`);
      ssrRenderList(__props.movie.format, (fmt) => {
        _push(`<span class="bg-black/60 border border-white/20 text-[10px] font-bold px-2.5 py-0.5 rounded text-white tracking-wide uppercase backdrop-blur-sm">${ssrInterpolate(fmt)}</span>`);
      });
      _push(`<!--]--></div><div class="absolute top-3 right-3 bg-yellow-500/90 text-black font-bold text-xs px-2.5 py-1 rounded-lg flex items-center gap-1 z-10 backdrop-blur-sm"><span class="material-symbols-outlined text-xs text-black" style="${ssrRenderStyle({ "font-variation-settings": "'FILL' 1" })}">star</span> ${ssrInterpolate(__props.movie.rating.toFixed(1))}</div></div><div class="p-4 flex-1 flex flex-col justify-between bg-surface-container/30"><div><h3 class="font-bold text-base text-on-surface line-clamp-1 mb-1 group-hover:text-primary-container transition-colors">${ssrInterpolate(__props.movie.title)}</h3><p class="text-xs text-on-surface-variant line-clamp-1">${ssrInterpolate(__props.movie.genre.join(" | "))}</p></div><div class="flex items-center justify-between border-t border-glass-stroke/40 pt-3 mt-3"><span class="text-xs text-on-surface-variant"> \u23F1\uFE0F ${ssrInterpolate(__props.movie.duration)} ph\xFAt </span>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: `/movies/${__props.movie.id}`,
        class: "text-xs font-bold text-primary-container hover:underline flex items-center gap-1"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(` \u0110\u1EB7t V\xE9 <span class="material-symbols-outlined text-xs"${_scopeId}>chevron_right</span>`);
          } else {
            return [
              createTextVNode(" \u0110\u1EB7t V\xE9 "),
              createVNode("span", { class: "material-symbols-outlined text-xs" }, "chevron_right")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div></div></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/MovieCard.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as _ };
//# sourceMappingURL=MovieCard-CFTDOcJL.mjs.map
