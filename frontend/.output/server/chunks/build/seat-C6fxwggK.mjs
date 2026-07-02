import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, mergeProps, withCtx, createVNode, createTextVNode, unref, ref, computed, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrInterpolate, ssrRenderList, ssrIncludeBooleanAttr, ssrRenderAttr, ssrRenderClass } from 'vue/server-renderer';
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

const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "SeatSelection",
  __ssrInlineRender: true,
  setup(__props) {
    const ticketsStore = useTicketsStore();
    const { selectedShowtime, selectedSeats } = storeToRefs(ticketsStore);
    const seatsList = ref([]);
    const loading = ref(false);
    const seatsByRow = computed(() => {
      const map = {};
      seatsList.value.forEach((seat) => {
        if (!map[seat.row]) {
          map[seat.row] = [];
        }
        map[seat.row].push(seat);
      });
      return Object.keys(map).sort().reduce((acc, key) => {
        acc[key] = map[key].sort((a, b) => a.number - b.number);
        return acc;
      }, {});
    });
    function isSeatSelected(seatId) {
      return selectedSeats.value.some((s) => s.id === seatId);
    }
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "glass-panel rounded-2xl border border-glass-stroke p-6 md:p-8 flex flex-col items-center" }, _attrs))}>`);
      if (loading.value) {
        _push(`<div class="py-12 text-center text-on-surface-variant animate-pulse"> \u0110ang t\u1EA3i s\u01A1 \u0111\u1ED3 ph\xF2ng chi\u1EBFu th\xF4ng minh... </div>`);
      } else if (!unref(selectedShowtime)) {
        _push(`<div class="py-12 text-center text-on-surface-variant"> \u26A0\uFE0F Vui l\xF2ng quay l\u1EA1i trang chi ti\u1EBFt phim \u0111\u1EC3 l\u1EF1a ch\u1ECDn su\u1EA5t chi\u1EBFu. </div>`);
      } else {
        _push(`<div class="w-full flex flex-col items-center"><div class="w-full max-w-2xl mb-12 text-center screen-curve"><div class="w-full bg-white/20 h-1 rounded-full shadow-[0_2px_15px_rgba(255,255,255,0.3)]"></div><div class="screen-glow"></div><span class="text-xs text-on-surface-variant tracking-[0.2em] uppercase font-bold mt-2 inline-block">M\xC0N H\xCCNH CH\u1EA4T L\u01AF\u1EE2NG CAO</span></div><div class="overflow-x-auto w-full max-w-3xl flex justify-center pb-6 hide-scrollbar"><div class="flex flex-col gap-3 min-w-[500px]"><!--[-->`);
        ssrRenderList(unref(seatsByRow), (rowSeats, rowName) => {
          _push(`<div class="flex items-center gap-3"><span class="w-6 font-bold text-sm text-on-surface-variant text-center mr-2">${ssrInterpolate(rowName)}</span><div class="flex items-center gap-2"><!--[-->`);
          ssrRenderList(rowSeats, (seat) => {
            _push(`<button${ssrIncludeBooleanAttr(seat.status === "occupied") ? " disabled" : ""}${ssrRenderAttr("title", `${seat.row}${seat.number} - ${seat.type.toUpperCase()} (${seat.price.toLocaleString()}\u0111)`)} class="${ssrRenderClass([[
              seat.status === "occupied" ? "bg-neutral-800 border-neutral-700 text-neutral-600 cursor-not-allowed" : isSeatSelected(seat.id) ? "bg-primary-container border-primary-container text-white scale-110 shadow-[0_0_12px_rgba(229,9,20,0.5)]" : seat.type === "vip" ? "bg-purple-950/40 border-purple-600 text-purple-200 hover:bg-purple-700/30" : seat.type === "couple" ? "bg-pink-950/40 border-pink-600 text-pink-200 w-16 hover:bg-pink-700/30" : "bg-surface-container-high border-glass-stroke text-on-surface hover:bg-white/10"
            ], "w-8 h-8 rounded-lg text-[10px] font-bold transition-all relative flex items-center justify-center border"])}">${ssrInterpolate(seat.number)}</button>`);
          });
          _push(`<!--]--></div><span class="w-6 font-bold text-sm text-on-surface-variant text-center ml-2">${ssrInterpolate(rowName)}</span></div>`);
        });
        _push(`<!--]--></div></div><div class="flex flex-wrap justify-center gap-6 border-t border-glass-stroke/40 pt-8 w-full max-w-2xl mt-4"><div class="flex items-center gap-2 text-xs"><div class="w-5 h-5 bg-surface-container-high border border-glass-stroke rounded"></div><span class="text-on-surface-variant font-medium">Gh\u1EBF Th\u01B0\u1EDDng</span></div><div class="flex items-center gap-2 text-xs"><div class="w-5 h-5 bg-purple-950/40 border border-purple-600 rounded"></div><span class="text-on-surface-variant font-medium">Gh\u1EBF VIP (+30%)</span></div><div class="flex items-center gap-2 text-xs"><div class="w-10 h-5 bg-pink-950/40 border border-pink-600 rounded"></div><span class="text-on-surface-variant font-medium">Gh\u1EBF \u0110\xF4i (+50%)</span></div><div class="flex items-center gap-2 text-xs"><div class="w-5 h-5 bg-primary-container border border-primary-container rounded shadow-[0_0_8px_rgba(229,9,20,0.4)]"></div><span class="text-on-surface-variant font-medium">\u0110ang Ch\u1ECDn</span></div><div class="flex items-center gap-2 text-xs"><div class="w-5 h-5 bg-neutral-800 border border-neutral-700 rounded"></div><span class="text-on-surface-variant font-medium">\u0110\xE3 B\xE1n</span></div></div></div>`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup$1 = _sfc_main$1.setup;
_sfc_main$1.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/SeatSelection.vue");
  return _sfc_setup$1 ? _sfc_setup$1(props, ctx) : void 0;
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "seat",
  __ssrInlineRender: true,
  setup(__props) {
    const ticketsStore = useTicketsStore();
    const moviesStore = useMoviesStore();
    const { selectedShowtime, selectedSeats, totalAmount } = storeToRefs(ticketsStore);
    const { activeMovie } = storeToRefs(moviesStore);
    return (_ctx, _push, _parent, _attrs) => {
      var _a;
      const _component_NuxtLink = __nuxt_component_0;
      const _component_SeatSelection = _sfc_main$1;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "max-w-container-max mx-auto px-6 md:px-margin-desktop py-12" }, _attrs))}><div class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4"><div>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/movies",
        class: "text-xs text-on-surface-variant hover:text-primary-container flex items-center gap-1 mb-2"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`<span class="material-symbols-outlined text-sm"${_scopeId}>arrow_back</span> Quay l\u1EA1i L\u1ECBch Chi\u1EBFu `);
          } else {
            return [
              createVNode("span", { class: "material-symbols-outlined text-sm" }, "arrow_back"),
              createTextVNode(" Quay l\u1EA1i L\u1ECBch Chi\u1EBFu ")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`<h1 class="font-headline-lg text-2xl md:text-3xl font-black text-on-surface"> Ch\u1ECDn Gh\u1EBF Ng\u1ED3i Th\xF4ng Minh </h1></div><div class="flex items-center gap-3 text-[10px] md:text-xs font-bold bg-surface-container-low border border-white/10 px-4 py-2.5 rounded-full overflow-x-auto whitespace-nowrap hide-scrollbar max-w-full"><span class="text-primary-container">1. Ch\u1ECDn Gh\u1EBF</span><span class="text-on-surface-variant">/</span><span class="text-on-surface-variant">2. B\u1EAFp N\u01B0\u1EDBc</span><span class="text-on-surface-variant">/</span><span class="text-on-surface-variant">3. Thanh To\xE1n</span></div></div><div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start"><div class="lg:col-span-8">`);
      _push(ssrRenderComponent(_component_SeatSelection, null, null, _parent));
      _push(`</div>`);
      if (unref(selectedShowtime)) {
        _push(`<div class="lg:col-span-4"><div class="glass-panel border border-glass-stroke rounded-2xl p-6 md:p-8 space-y-6"><div class="border-b border-glass-stroke/40 pb-4"><h3 class="font-bold text-lg text-on-surface mb-2">Th\xF4ng Tin Su\u1EA5t Chi\u1EBFu</h3><span class="text-sm font-semibold text-primary-fixed-dim block">${ssrInterpolate((_a = unref(activeMovie)) == null ? void 0 : _a.title)}</span></div><div class="space-y-3 text-xs text-on-surface-variant border-b border-glass-stroke/40 pb-4"><div class="flex justify-between"><span>R\u1EA1p:</span><span class="font-bold text-on-surface">${ssrInterpolate(unref(selectedShowtime).branchName)}</span></div><div class="flex justify-between"><span>Ph\xF2ng chi\u1EBFu:</span><span class="font-bold text-on-surface uppercase">${ssrInterpolate(unref(selectedShowtime).screenName)}</span></div><div class="flex justify-between"><span>Ng\xE0y chi\u1EBFu:</span><span class="font-bold text-on-surface">${ssrInterpolate(unref(selectedShowtime).date)}</span></div><div class="flex justify-between"><span>Gi\u1EDD chi\u1EBFu:</span><span class="font-bold text-on-surface text-sm text-primary">${ssrInterpolate(unref(selectedShowtime).time)}</span></div></div><div class="border-b border-glass-stroke/40 pb-4"><span class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Gh\u1EBF \u0110\xE3 Ch\u1ECDn</span>`);
        if (unref(selectedSeats).length === 0) {
          _push(`<div class="text-xs text-on-surface-variant italic"> Vui l\xF2ng ch\u1ECDn gh\u1EBF ng\u1ED3i tr\xEAn s\u01A1 \u0111\u1ED3. </div>`);
        } else {
          _push(`<div class="flex flex-wrap gap-2"><!--[-->`);
          ssrRenderList(unref(selectedSeats), (seat) => {
            _push(`<span class="bg-primary-container/10 border border-primary-container/20 text-primary-container text-xs font-bold px-3 py-1 rounded-lg">${ssrInterpolate(seat.row)}${ssrInterpolate(seat.number)}</span>`);
          });
          _push(`<!--]--></div>`);
        }
        _push(`</div><div class="flex items-center justify-between border-t border-glass-stroke/10 pt-4"><div class="flex flex-col"><span class="text-xs text-on-surface-variant">T\u1ED5ng c\u1ED9ng:</span><span class="text-xl font-black text-primary-fixed-dim">${ssrInterpolate(unref(totalAmount).toLocaleString())} VN\u0110</span></div><button${ssrIncludeBooleanAttr(unref(selectedSeats).length === 0) ? " disabled" : ""} class="bg-primary-container text-on-primary-container px-6 py-3 rounded-xl text-xs font-bold hover:scale-105 active:scale-95 transition-all flex items-center gap-1.5 red-glow disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100 disabled:shadow-none"> Ti\u1EBFp t\u1EE5c <span class="material-symbols-outlined text-xs">arrow_forward</span></button></div></div></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/checkout/seat.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=seat-C6fxwggK.mjs.map
