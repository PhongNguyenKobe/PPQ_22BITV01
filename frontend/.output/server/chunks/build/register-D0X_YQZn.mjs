import { _ as __nuxt_component_0 } from './nuxt-link-DOnPTYkR.mjs';
import { defineComponent, ref, mergeProps, withCtx, createTextVNode, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrInterpolate, ssrRenderAttr, ssrRenderComponent } from 'vue/server-renderer';
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
  __name: "register",
  __ssrInlineRender: true,
  setup(__props) {
    useUserStore();
    const name = ref("");
    const email = ref("");
    const error = ref("");
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "min-h-[80vh] flex items-center justify-center py-16 px-4" }, _attrs))}><div class="absolute inset-0 bg-[url(&#39;https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&amp;w=2070&amp;auto=format&amp;fit=crop&#39;)] bg-cover bg-center bg-no-repeat opacity-10 pointer-events-none z-0"></div><div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-8 relative z-10 shadow-2xl"><div class="text-center mb-8"><h1 class="font-headline-xl text-3xl font-bold text-on-surface mb-2">\u0110\u0103ng K\xFD Kh\xE1ch H\xE0ng</h1><p class="text-xs text-on-surface-variant">T\u1EA1o t\xE0i kho\u1EA3n \u0111\u1EC3 nh\u1EADn c\xE1c g\u1EE3i \xFD phim c\xE1 nh\xE2n h\xF3a t\u1EEB AI</p></div><form class="space-y-5">`);
      if (error.value) {
        _push(`<div class="bg-red-950/20 border border-red-500/20 text-red-400 text-xs px-4 py-2.5 rounded-xl"> \u26A0\uFE0F ${ssrInterpolate(error.value)}</div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">H\u1ECD v\xE0 t\xEAn</label><input${ssrRenderAttr("value", name.value)} type="text" required class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface" placeholder="Nh\u1EADp h\u1ECD v\xE0 t\xEAn c\u1EE7a b\u1EA1n"></div><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">Email c\xE1 nh\xE2n</label><input${ssrRenderAttr("value", email.value)} type="email" required class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface" placeholder="example@gmail.com"></div><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2">M\u1EADt kh\u1EA9u</label><input type="password" required class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary-container text-on-surface" placeholder="Nh\u1EADp m\u1EADt kh\u1EA9u"></div><button type="submit" class="w-full bg-primary-container text-on-primary-container py-3.5 rounded-xl font-bold hover:scale-105 active:scale-95 transition-all text-sm shadow-lg red-glow"> \u0110\u0103ng K\xFD T\xE0i Kho\u1EA3n </button></form><div class="mt-6 text-center text-xs text-on-surface-variant"> \u0110\xE3 c\xF3 t\xE0i kho\u1EA3n? `);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/login",
        class: "text-primary-container font-bold hover:underline"
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
      _push(`</div></div></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/register.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=register-D0X_YQZn.mjs.map
