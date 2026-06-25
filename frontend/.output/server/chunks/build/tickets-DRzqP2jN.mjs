import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, mergeProps, unref, withCtx, createTextVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrRenderList, ssrRenderAttr, ssrInterpolate } from 'vue/server-renderer';
import { s as storeToRefs } from './server.mjs';
import { u as useTicketsStore } from './tickets-DLGytZJQ.mjs';
import { u as useUserStore } from './user-CyBe2ltd.mjs';
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
  __name: "tickets",
  __ssrInlineRender: true,
  setup(__props) {
    const ticketsStore = useTicketsStore();
    const userStore = useUserStore();
    const { ticketHistory } = storeToRefs(ticketsStore);
    const { currentUser, isAuthenticated } = storeToRefs(userStore);
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "max-w-container-max mx-auto px-6 md:px-margin-desktop py-12" }, _attrs))}>`);
      if (!unref(isAuthenticated)) {
        _push(`<div class="py-24 text-center text-on-surface-variant"> \u26A0\uFE0F Vui l\xF2ng \u0111\u0103ng nh\u1EADp \u0111\u1EC3 xem th\xF4ng tin v\xE9 \u0111i\u1EC7n t\u1EED c\u1EE7a b\u1EA1n. <div class="mt-4">`);
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: "/login",
          class: "bg-primary-container text-white px-6 py-2.5 rounded-xl font-bold"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`\u0110\u0103ng nh\u1EADp`);
            } else {
              return [
                createTextVNode("\u0110\u0103ng nh\u1EADp")
              ];
            }
          }),
          _: 1
        }, _parent));
        _push(`</div></div>`);
      } else {
        _push(`<div class="space-y-12"><div class="border-b border-glass-stroke pb-6"><h1 class="font-headline-lg text-2xl md:text-3xl font-black text-on-surface">V\xE9 \u0110i\u1EC7n T\u1EED C\u1EE7a T\xF4i</h1><p class="text-xs text-on-surface-variant mt-1"> L\u01B0u tr\u1EEF th\xF4ng tin v\xE9 v\xE0 qu\xE9t m\xE3 QR t\u1EA1i qu\u1EA7y so\xE1t v\xE9 \u0111\u1EC3 v\xE0o ph\xF2ng chi\u1EBFu. </p></div>`);
        if (unref(ticketHistory).length === 0) {
          _push(`<div class="py-16 text-center text-on-surface-variant"><span class="material-symbols-outlined text-[48px] mb-2 text-on-surface-variant">confirmation_number</span><p class="text-sm font-medium">B\u1EA1n ch\u01B0a th\u1EF1c hi\u1EC7n b\u1EA5t k\u1EF3 giao d\u1ECBch \u0111\u1EB7t v\xE9 n\xE0o.</p>`);
          _push(ssrRenderComponent(_component_NuxtLink, {
            to: "/movies",
            class: "text-primary-container font-bold hover:underline mt-2 inline-block"
          }, {
            default: withCtx((_, _push2, _parent2, _scopeId) => {
              if (_push2) {
                _push2(`\u0110\u1EB7t v\xE9 ngay`);
              } else {
                return [
                  createTextVNode("\u0110\u1EB7t v\xE9 ngay")
                ];
              }
            }),
            _: 1
          }, _parent));
          _push(`</div>`);
        } else {
          _push(`<div class="grid grid-cols-1 lg:grid-cols-2 gap-8"><!--[-->`);
          ssrRenderList(unref(ticketHistory), (ticket) => {
            _push(`<div class="glass-panel border border-glass-stroke rounded-3xl overflow-hidden flex flex-col md:flex-row shadow-xl relative"><div class="hidden md:block absolute left-[65%] top-0 -translate-y-1/2 w-8 h-8 rounded-full bg-background z-20"></div><div class="hidden md:block absolute left-[65%] bottom-0 translate-y-1/2 w-8 h-8 rounded-full bg-background z-20"></div><div class="p-6 md:w-[65%] flex flex-col justify-between space-y-4"><div class="flex gap-4"><img${ssrRenderAttr("src", ticket.poster)}${ssrRenderAttr("alt", ticket.movieTitle)} class="w-20 h-28 object-cover rounded-xl border border-glass-stroke flex-shrink-0"><div><span class="text-[10px] bg-primary-container/10 border border-primary-container/20 text-primary-container px-2 py-0.5 rounded font-bold uppercase"> V\xE9 \u0110\xE3 X\xE1c Nh\u1EADn </span><h3 class="font-black text-base text-on-surface line-clamp-2 mt-1 leading-snug">${ssrInterpolate(ticket.movieTitle)}</h3><p class="text-[11px] text-on-surface-variant mt-1">M\xE3 \u0111\u1EB7t v\xE9: <span class="text-on-surface font-bold font-mono">${ssrInterpolate(ticket.id)}</span></p></div></div><div class="grid grid-cols-2 gap-3 text-xs text-on-surface-variant border-t border-glass-stroke/40 pt-4"><div><span class="block text-[10px] uppercase text-on-surface-variant mb-0.5">R\u1EA1p Chi\u1EBFu</span><span class="font-bold text-on-surface truncate block">${ssrInterpolate(ticket.branchName)}</span></div><div><span class="block text-[10px] uppercase text-on-surface-variant mb-0.5">Ph\xF2ng Chi\u1EBFu</span><span class="font-bold text-on-surface uppercase">${ssrInterpolate(ticket.screenName)}</span></div><div><span class="block text-[10px] uppercase text-on-surface-variant mb-0.5">Th\u1EDDi Gian</span><span class="font-bold text-primary block">${ssrInterpolate(ticket.time)} | ${ssrInterpolate(ticket.date)}</span></div><div><span class="block text-[10px] uppercase text-on-surface-variant mb-0.5">Gh\u1EBF Ng\u1ED3i</span><span class="font-bold text-on-surface truncate block">${ssrInterpolate(ticket.seats.join(", "))}</span></div></div><div class="border-t border-glass-stroke/20 pt-3 flex justify-between items-center text-xs text-on-surface-variant"><span>Ng\xE0y \u0111\u1EB7t: ${ssrInterpolate(ticket.bookingDate)}</span><span class="font-bold text-on-surface">${ssrInterpolate(ticket.totalAmount.toLocaleString())}\u0111</span></div></div><div class="border-t md:border-t-0 md:border-l border-dashed border-glass-stroke/60 relative"></div><div class="p-6 md:w-[35%] bg-surface-container/20 flex flex-col items-center justify-center text-center space-y-4"><div class="w-32 h-32 bg-white p-2 rounded-2xl border border-glass-stroke shadow-md"><img${ssrRenderAttr("src", `https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=${ticket.qrCode}`)} alt="E-Ticket QR code" class="w-full h-full"></div><div><span class="text-[10px] text-on-surface-variant uppercase tracking-wider block">Qu\xE9t t\u1EA1i qu\u1EA7y v\xE9</span><span class="text-xs font-bold text-on-surface mt-0.5 block font-mono">${ssrInterpolate(ticket.id)}</span></div></div></div>`);
          });
          _push(`<!--]--></div>`);
        }
        _push(`</div>`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/profile/tickets.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=tickets-DRzqP2jN.mjs.map
