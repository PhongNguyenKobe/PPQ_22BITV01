import { defineComponent, ref, computed, mergeProps, unref, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrInterpolate, ssrRenderList, ssrRenderStyle, ssrRenderClass, ssrRenderAttr } from 'vue/server-renderer';

const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "dashboard",
  __ssrInlineRender: true,
  setup(__props) {
    const activeTab = ref("movies");
    const totalBranches = ref(0);
    const totalMovies = ref(0);
    const totalUsers = ref(0);
    const totalRevenue = ref(0);
    const revenueChartData = ref([]);
    const moviesList = ref([]);
    const usersList = ref([]);
    const branchesList = ref([
      { id: "b1", name: "CineAI H\xF9ng V\u01B0\u01A1ng", city: "TP. H\u1ED3 Ch\xED Minh", screens: 6, status: "Ho\u1EA1t \u0111\u1ED9ng" },
      { id: "b2", name: "CineAI Sala Q2", city: "TP. H\u1ED3 Ch\xED Minh", screens: 8, status: "Ho\u1EA1t \u0111\u1ED9ng" },
      { id: "b3", name: "CineAI Nguy\u1EC5n Du", city: "TP. H\u1ED3 Ch\xED Minh", screens: 4, status: "Ho\u1EA1t \u0111\u1ED9ng" },
      { id: "b4", name: "CineAI Vincom B\xE0 Tri\u1EC7u", city: "H\xE0 N\u1ED9i", screens: 5, status: "Ho\u1EA1t \u0111\u1ED9ng" },
      { id: "b5", name: "CineAI \u0110\xE0 N\u1EB5ng Plaza", city: "\u0110\xE0 N\u1EB5ng", screens: 4, status: "B\u1EA3o tr\xEC" }
    ]);
    const showAddMovieModal = ref(false);
    const newMovieTitle = ref("");
    const newMovieGenre = ref("");
    const newMovieDirector = ref("");
    const newMovieDuration = ref(120);
    ref(4.5);
    const maxRevenueValue = computed(() => {
      if (revenueChartData.value.length === 0) return 1;
      return Math.max(...revenueChartData.value.map((c) => c.value));
    });
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "space-y-8" }, _attrs))}><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"><div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md"><div><span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">T\u1ED5ng doanh thu</span><span class="text-2xl font-black text-primary">${ssrInterpolate(totalRevenue.value.toLocaleString())}\u0111</span></div><div class="w-12 h-12 bg-primary-container/10 border border-primary-container/20 rounded-xl flex items-center justify-center text-primary-container"><span class="material-symbols-outlined text-[28px]">monitoring</span></div></div><div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md"><div><span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">T\u1ED5ng chi nh\xE1nh</span><span class="text-2xl font-black text-on-surface">${ssrInterpolate(totalBranches.value)}</span></div><div class="w-12 h-12 bg-surface-container-high border border-glass-stroke rounded-xl flex items-center justify-center text-on-surface-variant"><span class="material-symbols-outlined text-[28px]">storefront</span></div></div><div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md"><div><span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Phim qu\u1EA3n l\xFD</span><span class="text-2xl font-black text-on-surface">${ssrInterpolate(totalMovies.value)}</span></div><div class="w-12 h-12 bg-surface-container-high border border-glass-stroke rounded-xl flex items-center justify-center text-on-surface-variant"><span class="material-symbols-outlined text-[28px]">movie</span></div></div><div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md"><div><span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Kh\xE1ch h\xE0ng</span><span class="text-2xl font-black text-secondary">${ssrInterpolate(totalUsers.value)}</span></div><div class="w-12 h-12 bg-secondary-container/10 border border-secondary-container/20 rounded-xl flex items-center justify-center text-secondary"><span class="material-symbols-outlined text-[28px]">groups</span></div></div></div><div class="glass-panel border border-glass-stroke p-6 md:p-8 rounded-2xl shadow-lg"><h3 class="font-bold text-base text-on-surface mb-6 flex items-center gap-2"><span class="material-symbols-outlined text-primary-container">bar_chart</span> Bi\u1EC3u \u0110\u1ED3 Doanh Thu H\u1EC7 Th\u1ED1ng </h3><div class="h-64 flex items-end gap-4 md:gap-8 justify-center pt-8 border-b border-glass-stroke"><!--[-->`);
      ssrRenderList(revenueChartData.value, (bar) => {
        _push(`<div class="flex flex-col items-center flex-1 max-w-[60px] group relative"><span class="absolute -top-8 bg-black/85 border border-glass-stroke text-[10px] font-bold text-white px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10 shadow-lg">${ssrInterpolate((bar.value / 1e6).toFixed(1))}M\u0111 </span><div class="w-full rounded-t-lg bg-gradient-to-t from-primary-container/60 to-primary-container transition-all hover:brightness-110" style="${ssrRenderStyle({ height: `${bar.value / unref(maxRevenueValue) * 160}px` })}"></div><span class="text-xs text-on-surface-variant font-bold mt-2 pb-2 truncate w-full text-center">${ssrInterpolate(bar.label)}</span></div>`);
      });
      _push(`<!--]--></div></div><div class="glass-panel border border-glass-stroke rounded-2xl overflow-hidden shadow-lg"><div class="bg-surface-container-high/80 border-b border-glass-stroke flex items-center justify-between px-6 py-4"><div class="flex items-center gap-4"><button class="${ssrRenderClass([activeTab.value === "movies" ? "border-primary-container text-on-surface" : "border-transparent text-on-surface-variant hover:text-on-surface", "text-sm font-bold pb-2 transition-all border-b-2"])}"> Qu\u1EA3n L\xFD Phim </button><button class="${ssrRenderClass([activeTab.value === "branches" ? "border-primary-container text-on-surface" : "border-transparent text-on-surface-variant hover:text-on-surface", "text-sm font-bold pb-2 transition-all border-b-2"])}"> Qu\u1EA3n L\xFD Chi Nh\xE1nh </button><button class="${ssrRenderClass([activeTab.value === "users" ? "border-primary-container text-on-surface" : "border-transparent text-on-surface-variant hover:text-on-surface", "text-sm font-bold pb-2 transition-all border-b-2"])}"> Qu\u1EA3n L\xFD Th\xE0nh Vi\xEAn </button></div>`);
      if (activeTab.value === "movies") {
        _push(`<button class="bg-primary-container hover:bg-opacity-90 text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-1.5 red-glow transition-all"><span class="material-symbols-outlined text-sm">add</span> Th\xEAm Phim M\u1EDBi </button>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div><div class="p-6">`);
      if (activeTab.value === "movies") {
        _push(`<div class="overflow-x-auto"><table class="w-full text-left text-xs border-collapse"><thead><tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold"><th class="py-3.5 px-4">T\xEAn Phim</th><th class="py-3.5 px-4">\u0110\u1EA1o Di\u1EC5n</th><th class="py-3.5 px-4">Th\u1EC3 Lo\u1EA1i</th><th class="py-3.5 px-4 text-center">Th\u1EDDi L\u01B0\u1EE3ng</th><th class="py-3.5 px-4 text-center">\u0110\xE1nh Gi\xE1</th><th class="py-3.5 px-4 text-right">Thao T\xE1c</th></tr></thead><tbody class="divide-y divide-glass-stroke/40"><!--[-->`);
        ssrRenderList(moviesList.value, (movie) => {
          _push(`<tr class="hover:bg-white/5 transition-colors"><td class="py-4 px-4 font-bold text-on-surface">${ssrInterpolate(movie.title)}</td><td class="py-4 px-4 text-on-surface-variant">${ssrInterpolate(movie.director)}</td><td class="py-4 px-4 text-on-surface-variant">${ssrInterpolate(movie.genre.join(", "))}</td><td class="py-4 px-4 text-center text-on-surface-variant font-mono">${ssrInterpolate(movie.duration)} ph\xFAt</td><td class="py-4 px-4 text-center text-yellow-500 font-bold">\u2605 ${ssrInterpolate(movie.rating.toFixed(1))}</td><td class="py-4 px-4 text-right space-x-2"><button class="text-red-400 hover:text-red-300 font-semibold">X\xF3a</button></td></tr>`);
        });
        _push(`<!--]--></tbody></table></div>`);
      } else {
        _push(`<!---->`);
      }
      if (activeTab.value === "branches") {
        _push(`<div class="overflow-x-auto"><table class="w-full text-left text-xs border-collapse"><thead><tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold"><th class="py-3.5 px-4">T\xEAn Chi Nh\xE1nh</th><th class="py-3.5 px-4">Khu V\u1EF1c</th><th class="py-3.5 px-4 text-center">S\u1ED1 Ph\xF2ng Chi\u1EBFu</th><th class="py-3.5 px-4 text-center">Tr\u1EA1ng Th\xE1i</th></tr></thead><tbody class="divide-y divide-glass-stroke/40"><!--[-->`);
        ssrRenderList(branchesList.value, (branch) => {
          _push(`<tr class="hover:bg-white/5 transition-colors"><td class="py-4 px-4 font-bold text-on-surface">${ssrInterpolate(branch.name)}</td><td class="py-4 px-4 text-on-surface-variant">${ssrInterpolate(branch.city)}</td><td class="py-4 px-4 text-center text-on-surface-variant font-mono">${ssrInterpolate(branch.screens)}</td><td class="py-4 px-4 text-center"><span class="${ssrRenderClass([branch.status === "Ho\u1EA1t \u0111\u1ED9ng" ? "bg-green-950 text-green-400 border border-green-500/20" : "bg-yellow-950 text-yellow-400 border border-yellow-500/20", "px-2.5 py-0.5 rounded-full font-bold text-[10px]"])}">${ssrInterpolate(branch.status)}</span></td></tr>`);
        });
        _push(`<!--]--></tbody></table></div>`);
      } else {
        _push(`<!---->`);
      }
      if (activeTab.value === "users") {
        _push(`<div class="overflow-x-auto"><table class="w-full text-left text-xs border-collapse"><thead><tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold"><th class="py-3.5 px-4">H\u1ECD T\xEAn</th><th class="py-3.5 px-4">Email</th><th class="py-3.5 px-4">Ph\xE2n Quy\u1EC1n</th><th class="py-3.5 px-4">Thao T\xE1c</th></tr></thead><tbody class="divide-y divide-glass-stroke/40"><!--[-->`);
        ssrRenderList(usersList.value, (user) => {
          _push(`<tr class="hover:bg-white/5 transition-colors"><td class="py-4 px-4 font-bold text-on-surface">${ssrInterpolate(user.name)}</td><td class="py-4 px-4 text-on-surface-variant font-mono">${ssrInterpolate(user.email)}</td><td class="py-4 px-4 capitalize"><span class="${ssrRenderClass([user.role === "admin" ? "bg-red-950 text-red-400 border border-red-500/20" : user.role === "branch-admin" ? "bg-purple-950 text-purple-400 border border-purple-500/20" : "bg-blue-950 text-blue-400 border border-blue-500/20", "px-2.5 py-0.5 rounded-full font-bold text-[10px]"])}">${ssrInterpolate(user.role)}</span></td><td class="py-4 px-4"><button class="text-primary-container font-semibold hover:underline">Ch\u1EC9nh s\u1EEDa</button></td></tr>`);
        });
        _push(`<!--]--></tbody></table></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div></div>`);
      if (showAddMovieModal.value) {
        _push(`<div class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"><div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-6 relative"><button class="absolute top-4 right-4 text-on-surface-variant hover:text-on-surface"><span class="material-symbols-outlined">close</span></button><h3 class="font-headline-md text-lg font-bold text-on-surface mb-6">Th\xEAm Phim M\u1EDBi</h3><form class="space-y-4"><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">T\xEAn phim</label><input${ssrRenderAttr("value", newMovieTitle.value)} type="text" required class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" placeholder="Nh\u1EADp t\xEAn phim"></div><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Th\u1EC3 lo\u1EA1i (ng\u0103n c\xE1ch b\u1EB1ng d\u1EA5u ph\u1EA9y)</label><input${ssrRenderAttr("value", newMovieGenre.value)} type="text" required class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" placeholder="H\xE0nh \u0110\u1ED9ng, Vi\u1EC5n T\u01B0\u1EDFng"></div><div class="grid grid-cols-2 gap-4"><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">\u0110\u1EA1o di\u1EC5n</label><input${ssrRenderAttr("value", newMovieDirector.value)} type="text" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface" placeholder="Denis Villeneuve"></div><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Th\u1EDDi l\u01B0\u1EE3ng (ph\xFAt)</label><input${ssrRenderAttr("value", newMovieDuration.value)} type="number" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface"></div></div><button type="submit" class="w-full bg-primary-container text-white py-3 rounded-xl text-xs font-bold hover:scale-105 active:scale-95 transition-all shadow-md red-glow"> T\u1EA1o phim m\u1EDBi </button></form></div></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/admin/dashboard.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=dashboard-CG8gPObD.mjs.map
