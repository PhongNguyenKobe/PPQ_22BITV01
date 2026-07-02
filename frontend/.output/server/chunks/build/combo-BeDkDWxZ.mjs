import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, ref, computed, mergeProps, withCtx, createVNode, createTextVNode, unref, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrInterpolate, ssrRenderList, ssrRenderAttr, ssrRenderClass } from 'vue/server-renderer';
import { s as storeToRefs } from './server.mjs';
import { u as useTicketsStore } from './tickets-DLGytZJQ.mjs';
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
  __name: "combo",
  __ssrInlineRender: true,
  setup(__props) {
    const ticketsStore = useTicketsStore();
    const moviesStore = useMoviesStore();
    const { selectedShowtime, selectedSeats, totalAmount } = storeToRefs(ticketsStore);
    const { activeMovie } = storeToRefs(moviesStore);
    const combos = ref([
      { id: "c1", name: "CGV Combo Solo", price: 85e3, desc: "1 B\u1EAFp l\u1EDBn + 1 N\u01B0\u1EDBc ng\u1ECDt l\u1EDBn", img: "https://images.unsplash.com/photo-1585647347384-259e51c8651a?q=80&w=300&auto=format&fit=crop", qty: 0 },
      { id: "c2", name: "CGV Combo Couple", price: 12e4, desc: "1 B\u1EAFp si\xEAu l\u1EDBn + 2 N\u01B0\u1EDBc ng\u1ECDt l\u1EDBn", img: "https://images.unsplash.com/photo-1599059813005-11265ba4b4ce?q=80&w=300&auto=format&fit=crop", qty: 0 },
      { id: "c3", name: "Snack Khoai T\xE2y", price: 45e3, desc: "Khoai t\xE2y chi\xEAn gi\xF2n tan v\u1ECB ph\xF4 mai", img: "https://images.unsplash.com/photo-1576107025879-ff00ab9c3dd2?q=80&w=300&auto=format&fit=crop", qty: 0 }
    ]);
    const totalComboPrice = computed(() => {
      return combos.value.reduce((acc, curr) => acc + curr.price * curr.qty, 0);
    });
    return (_ctx, _push, _parent, _attrs) => {
      var _a, _b;
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "max-w-container-max mx-auto px-6 md:px-margin-desktop py-12 pt-24" }, _attrs))}><div class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4"><div>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/checkout/seat",
        class: "text-xs text-on-surface-variant hover:text-primary-container flex items-center gap-1 mb-2"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`<span class="material-symbols-outlined text-sm"${_scopeId}>arrow_back</span> Quay l\u1EA1i Ch\u1ECDn Gh\u1EBF `);
          } else {
            return [
              createVNode("span", { class: "material-symbols-outlined text-sm" }, "arrow_back"),
              createTextVNode(" Quay l\u1EA1i Ch\u1ECDn Gh\u1EBF ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`<h1 class="font-headline-lg text-2xl md:text-3xl font-black text-on-surface"> Ch\u1ECDn B\u1EAFp N\u01B0\u1EDBc (T\xF9y ch\u1ECDn) </h1></div><div class="flex items-center gap-3 text-[10px] md:text-xs font-bold bg-surface-container-low border border-white/10 px-4 py-2.5 rounded-full overflow-x-auto whitespace-nowrap hide-scrollbar max-w-full"><span class="text-on-surface-variant flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">check_circle</span> Gh\u1EBF</span><span class="text-on-surface-variant">/</span><span class="text-primary-container">2. B\u1EAFp N\u01B0\u1EDBc</span><span class="text-on-surface-variant">/</span><span class="text-on-surface-variant">3. Thanh To\xE1n</span></div></div><div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start"><div class="lg:col-span-8 space-y-6"><div class="bg-surface-container-low border border-white/10 rounded-2xl p-6"><div class="flex items-center gap-3 mb-6"><span class="material-symbols-outlined text-primary-container text-3xl">local_dining</span><h2 class="text-on-surface font-headline-md text-xl">Combo \u0111\u1ED9c quy\u1EC1n t\u1EEB ${ssrInterpolate(((_a = unref(selectedShowtime)) == null ? void 0 : _a.branchName) || "R\u1EA1p")}</h2></div><div class="space-y-4"><!--[-->`);
      ssrRenderList(combos.value, (combo, index) => {
        _push(`<div class="flex items-center gap-4 p-4 rounded-xl border border-white/5 bg-surface hover:border-primary-container/30 transition-colors"><div class="w-20 h-20 rounded-lg overflow-hidden flex-shrink-0 bg-surface-container"><img${ssrRenderAttr("src", combo.img)}${ssrRenderAttr("alt", combo.name)} class="w-full h-full object-cover"></div><div class="flex-grow"><h3 class="text-on-surface font-bold text-sm mb-1">${ssrInterpolate(combo.name)}</h3><p class="text-on-surface-variant text-xs mb-2">${ssrInterpolate(combo.desc)}</p><span class="text-primary-container font-bold text-sm">${ssrInterpolate(combo.price.toLocaleString())}\u0111</span></div><div class="flex items-center gap-3 bg-surface-container-high rounded-full p-1 border border-white/10"><button class="${ssrRenderClass([combo.qty === 0 ? "opacity-50 cursor-not-allowed" : "", "w-8 h-8 rounded-full bg-surface hover:bg-white/10 flex items-center justify-center transition-colors text-on-surface"])}"><span class="material-symbols-outlined text-[16px]">remove</span></button><span class="w-4 text-center font-bold text-on-surface text-sm">${ssrInterpolate(combo.qty)}</span><button class="w-8 h-8 rounded-full bg-primary-container text-on-primary-container hover:scale-105 flex items-center justify-center transition-transform"><span class="material-symbols-outlined text-[16px]">add</span></button></div></div>`);
      });
      _push(`<!--]--></div></div></div><div class="lg:col-span-4"><div class="bg-surface-container-low border border-white/10 rounded-2xl p-6 md:p-8 space-y-6 sticky top-24 shadow-xl"><div class="border-b border-white/10 pb-4"><h3 class="font-bold text-lg text-on-surface mb-2">T\xF3m T\u1EAFt \u0110\u01A1n H\xE0ng</h3><span class="text-sm font-semibold text-primary-container block">${ssrInterpolate(((_b = unref(activeMovie)) == null ? void 0 : _b.title) || "Phim")}</span></div><div class="space-y-3 text-sm text-on-surface-variant border-b border-white/10 pb-4"><div class="flex justify-between items-start"><span>Gh\u1EBF x${ssrInterpolate(unref(selectedSeats).length)}:</span><div class="text-right flex flex-col"><span class="font-bold text-on-surface">${ssrInterpolate(unref(selectedSeats).map((s) => s.row + s.number).join(", "))}</span><span class="text-xs">${ssrInterpolate(unref(totalAmount).toLocaleString())}\u0111</span></div></div></div>`);
      if (totalComboPrice.value > 0) {
        _push(`<div class="space-y-3 text-sm text-on-surface-variant border-b border-white/10 pb-4"><span class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">B\u1EAFp n\u01B0\u1EDBc</span><!--[-->`);
        ssrRenderList(combos.value.filter((c) => c.qty > 0), (combo) => {
          _push(`<div class="flex justify-between items-center text-xs"><span>${ssrInterpolate(combo.qty)}x ${ssrInterpolate(combo.name)}</span><span class="font-bold text-on-surface">${ssrInterpolate((combo.price * combo.qty).toLocaleString())}\u0111</span></div>`);
        });
        _push(`<!--]--></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div class="pt-2"><div class="flex justify-between items-end mb-6"><span class="text-on-surface-variant font-medium">T\u1ED5ng thanh to\xE1n:</span><span class="text-3xl font-black text-primary-container">${ssrInterpolate((unref(totalAmount) + totalComboPrice.value).toLocaleString())}\u0111</span></div><button class="w-full bg-primary-container text-on-primary-container hover:bg-primary py-4 rounded-xl font-bold transition-all shadow-[0_0_20px_-5px_rgba(229,9,20,0.4)] flex justify-center items-center gap-2"> Ti\u1EBFp t\u1EE5c Thanh to\xE1n <span class="material-symbols-outlined">arrow_forward</span></button></div></div></div></div></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/checkout/combo.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=combo-BeDkDWxZ.mjs.map
