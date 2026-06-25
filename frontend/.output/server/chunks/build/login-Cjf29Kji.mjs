import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, ref, mergeProps, withCtx, createTextVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderClass, ssrInterpolate, ssrRenderAttr, ssrRenderComponent } from 'vue/server-renderer';
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
import './server.mjs';
import '../routes/renderer.mjs';
import 'vue-bundle-renderer/runtime';
import 'unhead/server';
import 'devalue';
import 'unhead/utils';
import 'unhead/plugins';
import 'vue-router';

const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "login",
  __ssrInlineRender: true,
  setup(__props) {
    useUserStore();
    const email = ref("customer@gmail.com");
    const role = ref("customer");
    const error = ref("");
    const credentialsHelp = {
      customer: { email: "customer@gmail.com", desc: "T\xE0i kho\u1EA3n kh\xE1ch h\xE0ng m\u1EB7c \u0111\u1ECBnh" },
      admin: { email: "admin@cineai.vn", desc: "T\xE0i kho\u1EA3n Qu\u1EA3n tr\u1ECB vi\xEAn t\u1ED5ng h\u1EC7 th\u1ED1ng" },
      "branch-admin": { email: "branch@cineai.vn", desc: "T\xE0i kho\u1EA3n Qu\u1EA3n l\xFD chi nh\xE1nh Sala" }
    };
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "min-h-[80vh] flex items-center justify-center py-16 px-4" }, _attrs))}><div class="absolute inset-0 bg-[url(&#39;https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&amp;w=2070&amp;auto=format&amp;fit=crop&#39;)] bg-cover bg-center bg-no-repeat opacity-10 pointer-events-none z-0"></div><div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-8 relative z-10 shadow-2xl"><div class="text-center mb-8"><h1 class="font-headline-xl text-3xl font-bold text-on-surface mb-2">\u0110\u0103ng Nh\u1EADp</h1><p class="text-xs text-on-surface-variant">Ch\xE0o m\u1EEBng \u0111\u1EBFn v\u1EDBi h\u1EC7 th\u1ED1ng v\xE9 xem phim th\xF4ng minh CineAI</p></div><div class="grid grid-cols-3 gap-2 bg-surface-container-low border border-glass-stroke p-1 rounded-xl mb-6"><button type="button" class="${ssrRenderClass([role.value === "customer" ? "bg-primary-container text-white" : "text-on-surface-variant hover:text-on-surface", "py-2 text-xs font-semibold rounded-lg transition-all"])}"> Kh\xE1ch h\xE0ng </button><button type="button" class="${ssrRenderClass([role.value === "branch-admin" ? "bg-purple-950 border border-purple-500/20 text-purple-300" : "text-on-surface-variant hover:text-on-surface", "py-2 text-xs font-semibold rounded-lg transition-all"])}"> Chi nh\xE1nh </button><button type="button" class="${ssrRenderClass([role.value === "admin" ? "bg-neutral-800 border border-white/10 text-white" : "text-on-surface-variant hover:text-on-surface", "py-2 text-xs font-semibold rounded-lg transition-all"])}"> Admin </button></div><form class="space-y-5">`);
      if (error.value) {
        _push(`<div class="bg-red-950/20 border border-red-500/20 text-red-400 text-xs px-4 py-2.5 rounded-xl"> \u26A0\uFE0F ${ssrInterpolate(error.value)}</div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Email t\xE0i kho\u1EA3n</label><input${ssrRenderAttr("value", email.value)} type="email" required class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface" placeholder="Nh\u1EADp email \u0111\u0103ng nh\u1EADp"></div><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">M\u1EADt kh\u1EA9u</label><input type="password" value="123456" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface" placeholder="Nh\u1EADp m\u1EADt kh\u1EA9u"></div><button type="submit" class="w-full bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-105 active:scale-95 transition-all text-sm shadow-lg red-glow"> \u0110\u0103ng Nh\u1EADp </button></form>`);
      if (role.value === "customer") {
        _push(`<div class="mt-6 text-center text-xs text-on-surface-variant"> Ch\u01B0a c\xF3 t\xE0i kho\u1EA3n? `);
        _push(ssrRenderComponent(_component_NuxtLink, {
          to: "/register",
          class: "text-primary-container font-bold hover:underline"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              _push2(`\u0110\u0103ng k\xFD ngay`);
            } else {
              return [
                createTextVNode("\u0110\u0103ng k\xFD ngay")
              ];
            }
          }),
          _: 1
        }, _parent));
        _push(`</div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div class="mt-8 border-t border-glass-stroke/40 pt-4"><div class="bg-surface-container-low/60 rounded-xl p-3 border border-glass-stroke/50"><span class="text-[10px] font-bold uppercase text-secondary tracking-wider block mb-1">\u{1F4A1} T\xE0i kho\u1EA3n th\u1EED nghi\u1EC7m (M\u1EADt kh\u1EA9u: 123)</span><p class="text-[11px] text-on-surface-variant leading-relaxed"><span class="font-semibold text-on-surface">${ssrInterpolate(credentialsHelp[role.value].email)}</span><br>${ssrInterpolate(credentialsHelp[role.value].desc)}</p></div></div></div></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/login.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=login-Cjf29Kji.mjs.map
