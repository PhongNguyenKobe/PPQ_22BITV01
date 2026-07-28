import type { RouterConfig } from '@nuxt/schema'

export default <RouterConfig>{
  scrollBehavior() {
    return { left: 0, top: 0 }
  },
}
