<script setup lang="ts">
import { ref, computed } from 'vue'

definePageMeta({ layout: 'default' })

export interface NewsArticle {
    id: string
    title: string
    summary: string
    content: string
    category: 'vietnam' | 'hollywood' | 'review' | 'behind'
    categoryLabel: string
    imageUrl: string
    author: string
    publishedAt: string
    readTime: string
    isFeatured?: boolean
}

// State
const activeTab = ref<string>('all')
const searchQuery = ref<string>('')
const selectedArticle = ref<NewsArticle | null>(null)

// Mock News Articles Data
const articles = ref<NewsArticle[]>([
    {
        id: 'n1',
        title: 'Phim Tết Việt Bứt Phá Doanh Thu Phòng Vé Toàn Quốc 2026',
        summary: 'Điện ảnh Việt Nam ghi nhận kỷ lục mới về lượng vé bán ra trong tuần đầu công chiếu với sự đầu tư kỹ lưỡng về kịch bản.',
        content: 'Thị trường điện ảnh Việt Nam tiếp tục đón nhận những tín hiệu vô cùng tích cực khi các tác phẩm nội địa liên tục thiết lập kỷ lục doanh thu. Sự đầu tư công phu về mặt hình ảnh, âm thanh cùng kịch bản chạm tới cảm xúc khán giả đã giúp điện ảnh Việt khẳng định vị thế trên sân nhà.',
        category: 'vietnam',
        categoryLabel: 'ĐIỆN ẢNH VIỆT',
        imageUrl: 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=1000&auto=format&fit=crop',
        author: 'Tuấn Anh',
        publishedAt: '2 giờ trước',
        readTime: '3 phút đọc',
        isFeatured: true
    },
    {
        id: 'n2',
        title: 'Vũ Trụ Marvel Công Bố Dàn Nhân Vật Mới Trong Bom Tấn Thế Giới',
        summary: 'Marvel Studios chính thức tung trailer giới thiệu giai đoạn tiếp theo với kỹ xảo hoành tráng và sự xuất hiện của các siêu anh hùng mới.',
        content: 'Tại sự kiện điện ảnh quốc tế vừa diễn ra, Marvel Studios đã làm bùng nổ hội trường khi giới thiệu dàn nhân vật sẽ xuất hiện trong bom tấn tiếp theo. Kỹ xảo CGI được nâng cấp mạnh mẽ hứa hẹn mang đến trải nghiệm IMAX bùng nổ.',
        category: 'hollywood',
        categoryLabel: 'HOLLYWOOD',
        imageUrl: 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1000&auto=format&fit=crop',
        author: 'Minh Hoàng',
        publishedAt: '5 giờ trước',
        readTime: '4 phút đọc'
    },
    {
        id: 'n3',
        title: 'Đánh Giá Chi Tiết Siêu Phẩm Viễn Tưởng Đang Chiếu Rạp',
        summary: 'Một kiệt tác điện ảnh về mặt thị giác lẫn âm thanh. Liệu đây có phải là ứng cử viên sáng giá cho giải Oscar?',
        content: 'Bộ phim không chỉ làm tốt ở khía cạnh giải trí mà còn gài gắm nhiều thông điệp triết học sâu sắc. Diễn xuất xuất thần của dàn diễn viên chính cùng phần nhạc nền giao hưởng thực sự quyến rũ.',
        category: 'review',
        categoryLabel: 'REVIEW PHIM',
        imageUrl: 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=1000&auto=format&fit=crop',
        author: 'CineAI Critic',
        publishedAt: '1 ngày trước',
        readTime: '5 phút đọc'
    },
    {
        id: 'n4',
        title: 'Bí Mật Hậu Trường Kỹ Xảo Điện Ảnh 3D Thế Hệ Mới',
        summary: 'Khám phá công nghệ quay phim Volume LED và AI rendering đang thay đổi hoàn toàn quy trình làm phim hiện đại.',
        content: 'Công nghệ điện ảnh đang tiến những bước dài nhờ sự can thiệp của trí tuệ nhân tạo và hệ thống màn hình LED khổng lồ, giúp các đạo diễn tái hiện vũ trụ ảo ngay trong phim trường.',
        category: 'behind',
        categoryLabel: 'HẬU TRƯỜNG',
        imageUrl: 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?q=80&w=1000&auto=format&fit=crop',
        author: 'Đăng Khoa',
        publishedAt: '2 ngày trước',
        readTime: '6 phút đọc'
    }
])

// Computed
const featuredArticle = computed(() => articles.value.find(a => a.isFeatured) || articles.value[0])

const filteredArticles = computed(() => {
    return articles.value.filter(a => {
        const matchCategory = activeTab.value === 'all' || a.category === activeTab.value
        const matchSearch = a.title.toLowerCase().includes(searchQuery.value.toLowerCase())
        return matchCategory && matchSearch
    })
})
</script>

<template>
    <div class="min-h-screen bg-[#0b0c10] text-gray-100 pt-20 pb-24 selection:bg-red-600 selection:text-white">

        <!-- 1. HEADER SECTION -->
        <section class="border-b border-white/10 bg-gradient-to-b from-black/80 via-black/40 to-[#0b0c10] py-10">
            <div
                class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <span class="text-xs font-bold text-red-500 tracking-widest uppercase">CineAI Magazine</span>
                    <h1 class="text-3xl md:text-5xl font-black text-white tracking-tight mt-1">Tin Tức Điện Ảnh</h1>
                </div>

                <div class="relative w-full md:w-96">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                        <span class="material-symbols-outlined text-base">search</span>
                    </span>
                    <input v-model="searchQuery" type="text" placeholder="Tìm tin tức, bài viết..."
                        class="w-full pl-10 pr-4 py-2 rounded-full bg-white/10 border border-white/20 text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 transition" />
                </div>


            </div>
        </section>

        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">

            <!-- 2. HERO FEATURED NEWS -->
            <section v-if="featuredArticle && !searchQuery"
                class="relative group cursor-pointer overflow-hidden rounded-3xl border border-white/10 shadow-2xl"
                @click="selectedArticle = featuredArticle">
                <div class="relative h-[400px] md:h-[480px] w-full">
                    <img :src="featuredArticle.imageUrl" :alt="featuredArticle.title"
                        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
                    <div class="absolute inset-0 bg-gradient-to-t from-[#0b0c10] via-[#0b0c10]/50 to-transparent"></div>

                    <div class="absolute bottom-0 left-0 right-0 p-6 md:p-10 space-y-3">
                        <span
                            class="px-3 py-1 bg-red-600 text-white font-extrabold text-[10px] rounded-lg tracking-wider uppercase">
                            {{ featuredArticle.categoryLabel }}
                        </span>
                        <h2
                            class="text-2xl md:text-4xl font-black text-white group-hover:text-red-400 transition-colors leading-tight">
                            {{ featuredArticle.title }}
                        </h2>
                        <p class="text-xs md:text-sm text-gray-300 line-clamp-2 max-w-3xl font-light">
                            {{ featuredArticle.summary }}
                        </p>
                        <div class="flex items-center gap-4 text-xs text-gray-400 pt-2 font-medium">
                            <span>Bởi {{ featuredArticle.author }}</span>
                            <span>•</span>
                            <span>{{ featuredArticle.publishedAt }}</span>
                            <span>•</span>
                            <span class="text-red-400 font-bold">{{ featuredArticle.readTime }}</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 3. CATEGORY TABS -->
            <section class="flex items-center gap-3 overflow-x-auto scrollbar-none pb-2 border-b border-white/10">
                <button v-for="tab in [
                    { id: 'all', label: 'Tất Cả Tin Tức' },
                    { id: 'vietnam', label: 'Điện Ảnh Việt Nam' },
                    { id: 'hollywood', label: 'Thế Giới / Hollywood' },
                    { id: 'review', label: 'Review & Phân Tích' },
                    { id: 'behind', label: 'Tin Hậu Trường' }
                ]" :key="tab.id" @click="activeTab = tab.id"
                    class="flex-none px-5 py-2.5 rounded-xl border text-xs font-extrabold transition-all duration-300"
                    :class="activeTab === tab.id
                        ? 'bg-red-600 border-red-500 text-white shadow-[0_0_15px_rgba(229,9,20,0.4)]'
                        : 'bg-white/5 border-white/10 text-gray-400 hover:border-white/30 hover:text-white'">
                    {{ tab.label }}
                </button>
            </section>

            <!-- 4. MAIN NEWS GRID & SIDEBAR -->
            <section class="grid grid-cols-1 lg:grid-cols-12 gap-8">

                <!-- Articles Grid (8 cols) -->
                <div class="lg:col-span-8 space-y-6">
                    <div v-if="filteredArticles.length === 0"
                        class="py-16 text-center bg-white/5 rounded-3xl border border-white/10">
                        <span class="material-symbols-outlined text-5xl text-gray-500 mb-2">article</span>
                        <p class="text-gray-400 text-sm">Chưa có bài viết nào thuộc danh mục này.</p>
                    </div>

                    <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        <div v-for="a in filteredArticles" :key="a.id" @click="selectedArticle = a"
                            class="bg-gradient-to-b from-[#14161d] to-[#0d0e12] border border-white/10 rounded-2xl overflow-hidden hover:border-red-500/50 transition-all duration-300 hover:-translate-y-1 cursor-pointer flex flex-col justify-between group shadow-xl">
                            <div class="relative h-44 overflow-hidden">
                                <img :src="a.imageUrl" :alt="a.title"
                                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                                <span
                                    class="absolute top-3 left-3 px-2 py-0.5 bg-black/70 backdrop-blur-md text-red-400 font-extrabold text-[9px] rounded-md border border-white/10">
                                    {{ a.categoryLabel }}
                                </span>
                            </div>

                            <div class="p-5 space-y-3 flex-1 flex flex-col justify-between">
                                <div>
                                    <h3
                                        class="text-sm font-bold text-white group-hover:text-red-400 transition-colors line-clamp-2 leading-snug">
                                        {{ a.title }}
                                    </h3>
                                    <p class="text-xs text-gray-400 mt-2 line-clamp-2 font-light leading-relaxed">
                                        {{ a.summary }}
                                    </p>
                                </div>

                                <div
                                    class="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-gray-500">
                                    <span>{{ a.publishedAt }}</span>
                                    <span class="text-gray-400 font-medium">{{ a.readTime }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Sidebar Widget (4 cols) -->
                <div class="lg:col-span-4 space-y-6">
                    <div
                        class="bg-gradient-to-b from-[#14161d] to-[#0d0e12] border border-white/10 rounded-3xl p-6 shadow-xl space-y-4">
                        <h3
                            class="text-base font-black text-white flex items-center gap-2 border-b border-white/10 pb-3">
                            <span class="material-symbols-outlined text-red-500">local_fire_department</span>
                            TIN HOT TRONG TUẦN
                        </h3>

                        <div class="space-y-4">
                            <div v-for="(item, idx) in articles.slice(0, 3)" :key="item.id"
                                @click="selectedArticle = item" class="flex gap-3 cursor-pointer group">
                                <span class="text-xl font-black text-red-500/80 group-hover:text-red-500">0{{ idx + 1
                                    }}</span>
                                <div>
                                    <h4
                                        class="text-xs font-bold text-gray-200 group-hover:text-red-400 line-clamp-2 transition-colors">
                                        {{ item.title }}
                                    </h4>
                                    <span class="text-[10px] text-gray-500 mt-1 block">{{ item.readTime }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </section>

        </div>

        <!-- 5. QUICK ARTICLE READ MODAL -->
        <div v-if="selectedArticle"
            class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <div
                class="bg-[#14161d] border border-white/10 rounded-3xl max-w-2xl w-full p-6 md:p-8 space-y-5 relative shadow-2xl max-h-[85vh] overflow-y-auto">
                <button @click="selectedArticle = null" class="absolute top-4 right-4 text-gray-400 hover:text-white">
                    <span class="material-symbols-outlined">close</span>
                </button>

                <span
                    class="px-2.5 py-1 bg-red-600 text-white font-black text-[10px] rounded-md tracking-wider uppercase inline-block">
                    {{ selectedArticle.categoryLabel }}
                </span>

                <h2 class="text-xl md:text-2xl font-black text-white leading-tight">{{ selectedArticle.title }}</h2>

                <div class="flex items-center gap-4 text-xs text-gray-400 border-b border-white/10 pb-4">
                    <span>Tác giả: <strong class="text-white">{{ selectedArticle.author }}</strong></span>
                    <span>•</span>
                    <span>{{ selectedArticle.publishedAt }}</span>
                </div>

                <img :src="selectedArticle.imageUrl" :alt="selectedArticle.title"
                    class="w-full h-56 object-cover rounded-2xl border border-white/10" />

                <p class="text-xs md:text-sm text-gray-300 leading-relaxed font-light whitespace-pre-line">
                    {{ selectedArticle.content }}
                </p>

                <div class="pt-4 border-t border-white/10 flex justify-end">
                    <button @click="selectedArticle = null"
                        class="px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white font-bold text-xs rounded-xl transition-all">
                        Đóng Bài Viết
                    </button>
                </div>
            </div>
        </div>

    </div>
</template>

<style scoped>
.scrollbar-none::-webkit-scrollbar {
    display: none;
}

.scrollbar-none {
    -ms-overflow-style: none;
    scrollbar-width: none;
}
</style>