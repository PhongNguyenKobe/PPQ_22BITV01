import { defineEventHandler } from 'h3'

export default defineEventHandler((event) => {
  const domain = 'http://localhost:3000'
  const routes = [
    '',
    '/showtimes',
    '/cinemas',
    '/promotions',
    '/news',
    '/ai-discovery',
  ]

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${routes.map(route => `  <url>
    <loc>${domain}${route}</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>daily</changefreq>
    <priority>${route === '' ? '1.0' : '0.8'}</priority>
  </url>`).join('\n')}
</urlset>`

  event.node.res.setHeader('Content-Type', 'application/xml')
  return sitemap
})
