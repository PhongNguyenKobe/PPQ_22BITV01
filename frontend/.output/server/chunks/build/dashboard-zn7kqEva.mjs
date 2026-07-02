import { defineComponent, ref, computed, mergeProps, unref, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrInterpolate, ssrRenderList, ssrRenderStyle, ssrRenderClass, ssrRenderAttr, ssrIncludeBooleanAttr, ssrLooseContain, ssrLooseEqual } from 'vue/server-renderer';
import { a as mockMovies } from './api-rwjTvGO1.mjs';
import 'axios';

const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "dashboard",
  __ssrInlineRender: true,
  setup(__props) {
    const activeTab = ref("showtimes");
    const ticketsSold = ref(0);
    const activeShowtimes = ref(0);
    const activePromos = ref(0);
    const branchRevenue = ref(0);
    const salesChartData = ref([]);
    const showtimesList = ref([]);
    const promotionsList = ref([]);
    const screensList = ref([
      { id: "sc1", name: "IMAX Room A", type: "IMAX 3D", capacity: 120, status: "Ho\u1EA1t \u0111\u1ED9ng" },
      { id: "sc2", name: "Screen Room B", type: "4DX Dolby", capacity: 80, status: "Ho\u1EA1t \u0111\u1ED9ng" },
      { id: "sc3", name: "Screen Room C", type: "Standard 2D", capacity: 100, status: "Ho\u1EA1t \u0111\u1ED9ng" },
      { id: "sc4", name: "Screen Room D", type: "Standard 2D", capacity: 100, status: "\u0110ang d\u1ECDn d\u1EB9p" }
    ]);
    const showAddShowtimeModal = ref(false);
    const selectMovieId = ref("1");
    const selectScreenName = ref("IMAX Room A");
    const inputDate = ref("2026-06-25");
    const inputTime = ref("20:00");
    const inputPrice = ref(9e4);
    const maxTicketSalesValue = computed(() => {
      if (salesChartData.value.length === 0) return 1;
      return Math.max(...salesChartData.value.map((c) => c.tickets));
    });
    function getMovieTitle(id) {
      const m = mockMovies.find((item) => item.id === id);
      return m ? m.title : "Phim \u0111\xE3 \u1EA9n";
    }
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "space-y-8" }, _attrs))}><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"><div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md"><div><span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Doanh thu chi nh\xE1nh</span><span class="text-2xl font-black text-purple-400">${ssrInterpolate(branchRevenue.value.toLocaleString())}\u0111</span></div><div class="w-12 h-12 bg-purple-950/20 border border-purple-500/20 rounded-xl flex items-center justify-center text-purple-400 animate-pulse"><span class="material-symbols-outlined text-[28px]">payments</span></div></div><div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md"><div><span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">V\xE9 \u0111\xE3 b\xE1n</span><span class="text-2xl font-black text-on-surface">${ssrInterpolate(ticketsSold.value)}</span></div><div class="w-12 h-12 bg-surface-container-high border border-glass-stroke rounded-xl flex items-center justify-center text-on-surface-variant"><span class="material-symbols-outlined text-[28px]">confirmation_number</span></div></div><div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md"><div><span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Su\u1EA5t chi\u1EBFu \u0111ang ch\u1EA1y</span><span class="text-2xl font-black text-on-surface">${ssrInterpolate(activeShowtimes.value)}</span></div><div class="w-12 h-12 bg-surface-container-high border border-glass-stroke rounded-xl flex items-center justify-center text-on-surface-variant"><span class="material-symbols-outlined text-[28px]">calendar_today</span></div></div><div class="glass-panel border border-glass-stroke p-6 rounded-2xl flex items-center justify-between shadow-md"><div><span class="text-xs text-on-surface-variant uppercase tracking-wider font-bold block mb-1">Khuy\u1EBFn m\xE3i ch\u1EA1y</span><span class="text-2xl font-black text-primary-fixed-dim">${ssrInterpolate(activePromos.value)}</span></div><div class="w-12 h-12 bg-primary-container/10 border border-primary-container/20 rounded-xl flex items-center justify-center text-primary-container"><span class="material-symbols-outlined text-[28px]">local_activity</span></div></div></div><div class="grid grid-cols-1 md:grid-cols-3 gap-6"><div class="glass-panel border border-primary-container/30 p-6 rounded-2xl shadow-lg relative overflow-hidden group"><div class="absolute inset-0 bg-gradient-to-br from-primary-container/10 to-transparent"></div><div class="relative z-10 flex items-start gap-4"><div class="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center text-primary-container shrink-0"><span class="material-symbols-outlined">weather_snowy</span></div><div><h4 class="text-sm font-bold text-on-surface mb-1">D\u1EF1 b\xE1o theo th\u1EDDi ti\u1EBFt</h4><p class="text-xs text-on-surface-variant mb-2">Tr\u1EDDi m\u01B0a l\u1EA1nh v\xE0o t\u1ED1i mai. D\u1EF1 ki\u1EBFn kh\xE1ch xem phim th\u1EC3 lo\u1EA1i t\xECnh c\u1EA3m t\u0103ng m\u1EA1nh.</p><span class="text-lg font-black text-primary-container">+15% Doanh thu</span></div></div></div><div class="glass-panel border border-[#8a2be2]/30 p-6 rounded-2xl shadow-lg relative overflow-hidden group"><div class="absolute inset-0 bg-gradient-to-br from-[#8a2be2]/10 to-transparent"></div><div class="relative z-10 flex items-start gap-4"><div class="w-10 h-10 rounded-full bg-[#8a2be2]/20 flex items-center justify-center text-[#8a2be2] shrink-0"><span class="material-symbols-outlined">trending_up</span></div><div><h4 class="text-sm font-bold text-on-surface mb-1">Trend M\u1EA1ng X\xE3 H\u1ED9i</h4><p class="text-xs text-on-surface-variant mb-2">Phim &quot;\u0110\u01B0\u1EDDng \u0110ua R\u1EF1c L\u1EEDa&quot; \u0111ang viral top 1 Tiktok khu v\u1EF1c n\xE0y.</p><span class="text-sm font-black text-[#8a2be2]">G\u1EE3i \xFD: T\u0103ng c\u01B0\u1EDDng su\u1EA5t chi\u1EBFu</span></div></div></div><div class="glass-panel border border-green-500/30 p-6 rounded-2xl shadow-lg relative overflow-hidden group"><div class="absolute inset-0 bg-gradient-to-br from-green-500/10 to-transparent"></div><div class="relative z-10 flex items-start gap-4"><div class="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center text-green-500 shrink-0"><span class="material-symbols-outlined">tips_and_updates</span></div><div><h4 class="text-sm font-bold text-on-surface mb-1">AI T\u1ED1i \u01AFu Gi\xE1</h4><p class="text-xs text-on-surface-variant mb-3">Khung gi\u1EDD 14:00 Th\u1EE9 4 \u0111ang tr\u1ED1ng &gt;60% gh\u1EBF tr\u1ED1ng.</p><button class="text-xs font-bold text-green-500 hover:text-green-400 border border-green-500/50 px-3 py-1.5 rounded-lg bg-green-500/10 hover:bg-green-500/20 transition-all flex items-center gap-1 w-full justify-center"><span class="material-symbols-outlined text-[14px]">bolt</span> K\xEDch ho\u1EA1t Flash Sale </button></div></div></div></div><div class="glass-panel border border-glass-stroke p-6 md:p-8 rounded-2xl shadow-lg"><h3 class="font-bold text-base text-on-surface mb-6 flex items-center gap-2"><span class="material-symbols-outlined text-purple-400 animate-pulse">monitoring</span> S\u1ED1 L\u01B0\u1EE3ng V\xE9 B\xE1n Theo Ng\xE0y Trong Tu\u1EA7n </h3><div class="h-64 flex items-end gap-4 md:gap-8 justify-center pt-8 border-b border-glass-stroke"><!--[-->`);
      ssrRenderList(salesChartData.value, (bar) => {
        _push(`<div class="flex flex-col items-center flex-1 max-w-[60px] group relative"><span class="absolute -top-8 bg-black/85 border border-glass-stroke text-[10px] font-bold text-white px-2.5 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">${ssrInterpolate(bar.tickets)} v\xE9 </span><div class="w-full rounded-t-lg bg-gradient-to-t from-purple-900 to-purple-500 transition-all hover:brightness-110" style="${ssrRenderStyle({ height: `${bar.tickets / maxTicketSalesValue.value * 160}px` })}"></div><span class="text-xs text-on-surface-variant font-bold mt-2 pb-2 truncate w-full text-center">${ssrInterpolate(bar.label)}</span></div>`);
      });
      _push(`<!--]--></div></div><div class="glass-panel border border-glass-stroke rounded-2xl overflow-hidden shadow-lg"><div class="bg-surface-container-high/80 border-b border-glass-stroke flex items-center justify-between px-6 py-4"><div class="flex items-center gap-4"><button class="${ssrRenderClass([activeTab.value === "showtimes" ? "border-purple-500 text-purple-400" : "border-transparent text-on-surface-variant hover:text-on-surface", "text-sm font-bold pb-2 transition-all border-b-2"])}"> Qu\u1EA3n L\xFD Su\u1EA5t Chi\u1EBFu </button><button class="${ssrRenderClass([activeTab.value === "screens" ? "border-purple-500 text-purple-400" : "border-transparent text-on-surface-variant hover:text-on-surface", "text-sm font-bold pb-2 transition-all border-b-2"])}"> Qu\u1EA3n L\xFD Ph\xF2ng Chi\u1EBFu </button><button class="${ssrRenderClass([activeTab.value === "promos" ? "border-purple-500 text-purple-400" : "border-transparent text-on-surface-variant hover:text-on-surface", "text-sm font-bold pb-2 transition-all border-b-2"])}"> M\xE3 Khuy\u1EBFn M\xE3i </button></div>`);
      if (activeTab.value === "showtimes") {
        _push(`<button class="bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-1.5 shadow-md transition-all"><span class="material-symbols-outlined text-sm">add</span> Th\xEAm Su\u1EA5t Chi\u1EBFu </button>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div><div class="p-6">`);
      if (activeTab.value === "showtimes") {
        _push(`<div class="overflow-x-auto"><table class="w-full text-left text-xs border-collapse"><thead><tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold"><th class="py-3.5 px-4">T\xEAn Phim</th><th class="py-3.5 px-4">Ph\xF2ng chi\u1EBFu</th><th class="py-3.5 px-4 text-center">Ng\xE0y Chi\u1EBFu</th><th class="py-3.5 px-4 text-center">Gi\u1EDD Chi\u1EBFu</th><th class="py-3.5 px-4 text-center">Gi\xE1 V\xE9</th><th class="py-3.5 px-4 text-right">Thao T\xE1c</th></tr></thead><tbody class="divide-y divide-glass-stroke/40"><!--[-->`);
        ssrRenderList(showtimesList.value, (showtime) => {
          _push(`<tr class="hover:bg-white/5 transition-colors"><td class="py-4 px-4 font-bold text-on-surface">${ssrInterpolate(getMovieTitle(showtime.movieId))}</td><td class="py-4 px-4 text-on-surface-variant uppercase font-mono">${ssrInterpolate(showtime.screenName)}</td><td class="py-4 px-4 text-center text-on-surface-variant">${ssrInterpolate(showtime.date)}</td><td class="py-4 px-4 text-center text-purple-400 font-bold">${ssrInterpolate(showtime.time)}</td><td class="py-4 px-4 text-center text-on-surface-variant font-mono">${ssrInterpolate(showtime.price.toLocaleString())}\u0111</td><td class="py-4 px-4 text-right"><button class="text-red-400 hover:text-red-300 font-semibold">X\xF3a</button></td></tr>`);
        });
        _push(`<!--]--></tbody></table></div>`);
      } else {
        _push(`<!---->`);
      }
      if (activeTab.value === "screens") {
        _push(`<div class="overflow-x-auto"><table class="w-full text-left text-xs border-collapse"><thead><tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold"><th class="py-3.5 px-4">T\xEAn Ph\xF2ng</th><th class="py-3.5 px-4">Lo\u1EA1i C\u1EA5u H\xECnh</th><th class="py-3.5 px-4 text-center">S\u1EE9c Ch\u1EE9a (Gh\u1EBF)</th><th class="py-3.5 px-4 text-center">Tr\u1EA1ng Th\xE1i</th></tr></thead><tbody class="divide-y divide-glass-stroke/40"><!--[-->`);
        ssrRenderList(screensList.value, (screen) => {
          _push(`<tr class="hover:bg-white/5 transition-colors"><td class="py-4 px-4 font-bold text-on-surface">${ssrInterpolate(screen.name)}</td><td class="py-4 px-4 text-on-surface-variant font-bold font-mono">${ssrInterpolate(screen.type)}</td><td class="py-4 px-4 text-center text-on-surface-variant font-mono">${ssrInterpolate(screen.capacity)}</td><td class="py-4 px-4 text-center"><span class="${ssrRenderClass([screen.status === "Ho\u1EA1t \u0111\u1ED9ng" ? "bg-green-950 text-green-400 border border-green-500/20" : "bg-yellow-950 text-yellow-400 border border-yellow-500/20", "px-2.5 py-0.5 rounded-full font-bold text-[10px]"])}">${ssrInterpolate(screen.status)}</span></td></tr>`);
        });
        _push(`<!--]--></tbody></table></div>`);
      } else {
        _push(`<!---->`);
      }
      if (activeTab.value === "promos") {
        _push(`<div class="overflow-x-auto"><table class="w-full text-left text-xs border-collapse"><thead><tr class="border-b border-glass-stroke text-on-surface-variant uppercase tracking-wider font-bold"><th class="py-3.5 px-4">M\xE3 Khuy\u1EBFn M\xE3i</th><th class="py-3.5 px-4 text-center">M\u1EE9c Gi\u1EA3m</th><th class="py-3.5 px-4">M\xF4 T\u1EA3 Ch\u01B0\u01A1ng Tr\xECnh</th><th class="py-3.5 px-4 text-center">Tr\u1EA1ng Th\xE1i</th></tr></thead><tbody class="divide-y divide-glass-stroke/40"><!--[-->`);
        ssrRenderList(promotionsList.value, (promo) => {
          _push(`<tr class="hover:bg-white/5 transition-colors"><td class="py-4 px-4 font-bold text-purple-300 font-mono">${ssrInterpolate(promo.code)}</td><td class="py-4 px-4 text-center text-primary-fixed-dim font-bold">${ssrInterpolate(promo.discount)}%</td><td class="py-4 px-4 text-on-surface-variant">${ssrInterpolate(promo.desc)}</td><td class="py-4 px-4 text-center"><span class="${ssrRenderClass([promo.active ? "bg-green-950 text-green-400 border border-green-500/20" : "bg-neutral-800 text-neutral-400 border border-glass-stroke", "px-2.5 py-0.5 rounded-full font-bold text-[10px]"])}">${ssrInterpolate(promo.active ? "\u0110ang ch\u1EA1y" : "H\u1EBFt h\u1EA1n")}</span></td></tr>`);
        });
        _push(`<!--]--></tbody></table></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div></div>`);
      if (showAddShowtimeModal.value) {
        _push(`<div class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"><div class="glass-panel w-full max-w-md rounded-2xl border border-glass-stroke p-6 relative"><button class="absolute top-4 right-4 text-on-surface-variant hover:text-on-surface"><span class="material-symbols-outlined">close</span></button><h3 class="font-headline-md text-lg font-bold text-on-surface mb-6">Th\xEAm Su\u1EA5t Chi\u1EBFu M\u1EDBi</h3><form class="space-y-4"><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Ch\u1ECDn phim</label><select class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:ring-1 focus:ring-purple-500"><!--[-->`);
        ssrRenderList(unref(mockMovies), (movie) => {
          _push(`<option${ssrRenderAttr("value", movie.id)}${ssrIncludeBooleanAttr(Array.isArray(selectMovieId.value) ? ssrLooseContain(selectMovieId.value, movie.id) : ssrLooseEqual(selectMovieId.value, movie.id)) ? " selected" : ""}>${ssrInterpolate(movie.title)}</option>`);
        });
        _push(`<!--]--></select></div><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Ph\xF2ng chi\u1EBFu</label><select class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface focus:ring-1 focus:ring-purple-500"><option${ssrIncludeBooleanAttr(Array.isArray(selectScreenName.value) ? ssrLooseContain(selectScreenName.value, null) : ssrLooseEqual(selectScreenName.value, null)) ? " selected" : ""}>IMAX Room A</option><option${ssrIncludeBooleanAttr(Array.isArray(selectScreenName.value) ? ssrLooseContain(selectScreenName.value, null) : ssrLooseEqual(selectScreenName.value, null)) ? " selected" : ""}>Screen Room B</option><option${ssrIncludeBooleanAttr(Array.isArray(selectScreenName.value) ? ssrLooseContain(selectScreenName.value, null) : ssrLooseEqual(selectScreenName.value, null)) ? " selected" : ""}>Screen Room C</option><option${ssrIncludeBooleanAttr(Array.isArray(selectScreenName.value) ? ssrLooseContain(selectScreenName.value, null) : ssrLooseEqual(selectScreenName.value, null)) ? " selected" : ""}>Screen Room D</option></select></div><div class="grid grid-cols-2 gap-4"><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Ng\xE0y chi\u1EBFu</label><input${ssrRenderAttr("value", inputDate.value)} type="date" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface"></div><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Gi\u1EDD chi\u1EBFu</label><input${ssrRenderAttr("value", inputTime.value)} type="time" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface"></div></div><div><label class="block text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-1">Gi\xE1 v\xE9 g\u1ED1c (VN\u0110)</label><input${ssrRenderAttr("value", inputPrice.value)} type="number" class="w-full bg-surface-container border border-glass-stroke rounded-xl px-4 py-2.5 text-xs text-on-surface"></div><button type="submit" class="w-full bg-purple-600 text-white py-3 rounded-xl text-xs font-bold hover:scale-105 active:scale-95 transition-all shadow-md"> T\u1EA1o su\u1EA5t chi\u1EBFu m\u1EDBi </button></form></div></div>`);
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
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/branch-admin/dashboard.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };
//# sourceMappingURL=dashboard-zn7kqEva.mjs.map
