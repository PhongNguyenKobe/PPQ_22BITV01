import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, ref, mergeProps, withCtx, createVNode, createTextVNode, unref, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrRenderList, ssrRenderClass, ssrInterpolate, ssrIncludeBooleanAttr } from 'vue/server-renderer';
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
  __name: "payment",
  __ssrInlineRender: true,
  setup(__props) {
    const ticketsStore = useTicketsStore();
    const moviesStore = useMoviesStore();
    const { selectedShowtime, selectedSeats, totalAmount, loading } = storeToRefs(ticketsStore);
    const { activeMovie } = storeToRefs(moviesStore);
    const selectedPayment = ref("V\xED Momo");
    const processing = ref(false);
    const showQR = ref(false);
    const paymentMethods = [
      { name: "V\xED Momo", icon: "payments", desc: "Thanh to\xE1n qua \u1EE9ng d\u1EE5ng Momo" },
      { name: "V\xED VNPAY", icon: "account_balance_wallet", desc: "Thanh to\xE1n qua c\u1ED5ng VNPAY" },
      { name: "Th\u1EBB ATM/T\xEDn D\u1EE5ng", icon: "credit_card", desc: "Visa, Mastercard, JCB ho\u1EB7c th\u1EBB n\u1ED9i \u0111\u1ECBa" },
      { name: "Qu\xE9t M\xE3 QR", icon: "qr_code_scanner", desc: "Qu\xE9t m\xE3 QR \u0111\u1EC3 chuy\u1EC3n kho\u1EA3n nhanh" }
    ];
    return (_ctx, _push, _parent, _attrs) => {
      var _a;
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "max-w-container-max mx-auto px-6 md:px-margin-desktop py-12" }, _attrs))}><div class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4"><div>`);
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
      _push(`<h1 class="font-headline-lg text-2xl md:text-3xl font-black text-on-surface"> Thanh To\xE1n \u0110\u01A1n V\xE9 </h1></div><div class="flex items-center gap-3 text-xs font-bold bg-surface-container-low border border-glass-stroke px-4 py-2.5 rounded-full"><span class="text-on-surface-variant">1. Ch\u1ECDn Gh\u1EBF</span><span class="text-on-surface-variant">/</span><span class="text-primary-container">2. Thanh To\xE1n</span><span class="text-on-surface-variant">/</span><span class="text-on-surface-variant">3. Nh\u1EADn V\xE9</span></div></div><div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start"><div class="lg:col-span-8 space-y-6"><div class="glass-panel border border-glass-stroke rounded-2xl p-6 md:p-8"><h3 class="font-bold text-lg text-on-surface mb-6 flex items-center gap-2"><span class="material-symbols-outlined text-primary-container">payment</span> Ch\u1ECDn Ph\u01B0\u01A1ng Th\u1EE9c Thanh To\xE1n </h3><div class="grid grid-cols-1 md:grid-cols-2 gap-4"><!--[-->`);
      ssrRenderList(paymentMethods, (method) => {
        _push(`<button class="${ssrRenderClass([selectedPayment.value === method.name ? "bg-primary-container/5 border-primary-container shadow-md" : "bg-surface border-glass-stroke hover:bg-white/5", "border rounded-2xl p-4 text-left flex items-start gap-4 transition-all"])}"><div class="w-10 h-10 rounded-xl flex items-center justify-center bg-surface-container border border-glass-stroke text-primary-container"><span class="material-symbols-outlined">${ssrInterpolate(method.icon)}</span></div><div><span class="block text-sm font-semibold text-on-surface">${ssrInterpolate(method.name)}</span><span class="text-xs text-on-surface-variant block mt-1">${ssrInterpolate(method.desc)}</span></div></button>`);
      });
      _push(`<!--]--></div></div>`);
      if (selectedPayment.value === "Qu\xE9t M\xE3 QR" && showQR.value) {
        _push(`<div class="glass-panel border border-purple-500/20 rounded-2xl p-6 md:p-8 flex flex-col items-center text-center"><span class="bg-secondary-container/20 border border-secondary-container/30 text-secondary text-[11px] font-bold px-3 py-1 rounded-full inline-flex items-center gap-1.5 backdrop-blur-md mb-4"><span class="material-symbols-outlined text-xs">qr_code</span> C\u1ED5ng thanh to\xE1n t\u1EF1 \u0111\u1ED9ng </span><h4 class="font-bold text-base text-on-surface mb-2">Qu\xE9t M\xE3 QR \u0110\u1EC3 Thanh To\xE1n</h4><p class="text-xs text-on-surface-variant max-w-sm mb-6">M\xE3 QR b\xEAn d\u01B0\u1EDBi ch\u1EE9a th\xF4ng tin t\xE0i kho\u1EA3n v\xE0 t\u1ED5ng s\u1ED1 ti\u1EC1n thanh to\xE1n c\u1EE7a b\u1EA1n.</p><div class="w-48 h-48 bg-white p-3 rounded-2xl border border-glass-stroke mb-4 shadow-xl"><img src="https://api.qrserver.com/v1/create-qr-code/?size=180x180&amp;data=CineAI_Checkout_Booking" alt="Mock QR Code Checkout" class="w-full h-full"></div><span class="text-xs text-on-surface-variant">Vui l\xF2ng qu\xE9t m\xE3 v\xE0 x\xE1c nh\u1EADn chuy\u1EC3n kho\u1EA3n \u0111\u1EC3 ho\xE0n t\u1EA5t.</span></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
      if (unref(selectedShowtime)) {
        _push(`<div class="lg:col-span-4"><div class="glass-panel border border-glass-stroke rounded-2xl p-6 md:p-8 space-y-6"><div><h3 class="font-bold text-lg text-on-surface mb-2">\u0110\u01A1n V\xE9 C\u1EE7a B\u1EA1n</h3><span class="text-sm font-semibold text-primary-fixed-dim block">${ssrInterpolate((_a = unref(activeMovie)) == null ? void 0 : _a.title)}</span></div><div class="space-y-3 text-xs text-on-surface-variant border-t border-glass-stroke/40 pt-4"><div class="flex justify-between"><span>R\u1EA1p:</span><span class="font-bold text-on-surface">${ssrInterpolate(unref(selectedShowtime).branchName)}</span></div><div class="flex justify-between"><span>Su\u1EA5t chi\u1EBFu:</span><span class="font-bold text-on-surface text-primary">${ssrInterpolate(unref(selectedShowtime).time)} | ${ssrInterpolate(unref(selectedShowtime).date)}</span></div><div class="flex justify-between"><span>Ph\xF2ng chi\u1EBFu:</span><span class="font-bold text-on-surface uppercase">${ssrInterpolate(unref(selectedShowtime).screenName)}</span></div><div class="flex justify-between"><span>Gh\u1EBF ng\u1ED3i:</span><div class="flex flex-wrap gap-1 justify-end max-w-[60%]"><!--[-->`);
        ssrRenderList(unref(selectedSeats), (seat) => {
          _push(`<span class="font-bold text-on-surface">${ssrInterpolate(seat.row)}${ssrInterpolate(seat.number)}, </span>`);
        });
        _push(`<!--]--></div></div></div><div class="border-t border-glass-stroke/40 pt-4 space-y-4"><div class="flex justify-between items-center text-xs"><span class="text-on-surface-variant">Ph\u01B0\u01A1ng th\u1EE9c:</span><span class="font-bold text-on-surface">${ssrInterpolate(selectedPayment.value)}</span></div><div class="flex justify-between items-center"><span class="text-xs text-on-surface-variant">T\u1ED5ng s\u1ED1 ti\u1EC1n:</span><span class="text-lg font-black text-primary">${ssrInterpolate(unref(totalAmount).toLocaleString())} VN\u0110</span></div></div><button${ssrIncludeBooleanAttr(processing.value) ? " disabled" : ""} class="w-full bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-105 active:scale-95 transition-all text-xs flex items-center justify-center gap-2 red-glow disabled:opacity-50">`);
        if (processing.value) {
          _push(`<!--[--><span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span> \u0110ang x\xE1c th\u1EF1c... <!--]-->`);
        } else {
          _push(`<!--[--> X\xE1c Nh\u1EADn Thanh To\xE1n <!--]-->`);
        }
        _push(`</button></div></div>`);
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
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/checkout/payment.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=payment-DDKY5JbJ.mjs.map
