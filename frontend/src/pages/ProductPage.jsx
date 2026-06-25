import { useEffect, useState } from 'react';
import axios from 'axios';
import ProductList from '../components/ProductList';

const ProductPage = () => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [sortOption, setSortOption] = useState('none');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // useEffect 1: Fetch data khi component mount
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await axios.get('https://fakestoreapi.com/products');
        const mapped = res.data.map((item) => ({
          id: item.id,
          name: item.title,
          price: item.price,
          category: item.category,
          imageUrl: item.image,
          description: item.description,
        }));
        setProducts(mapped);
        setFilteredProducts(mapped);
      } catch (err) {
        setError('Failed to load products. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []); // [] = chỉ chạy 1 lần khi mount

  // useEffect 2: Lọc/sort lại khi search, category, sort thay đổi
  useEffect(() => {
    let updated = [...products];

    if (searchTerm.trim() !== '') {
      const lower = searchTerm.toLowerCase();
      updated = updated.filter((p) => p.name.toLowerCase().includes(lower));
    }

    if (selectedCategory !== 'All') {
      updated = updated.filter((p) => p.category === selectedCategory);
    }

    if (sortOption === 'price-asc') updated.sort((a, b) => a.price - b.price);
    else if (sortOption === 'price-desc') updated.sort((a, b) => b.price - a.price);

    setFilteredProducts(updated);
  }, [searchTerm, selectedCategory, sortOption, products]);

  const categories = ['All', ...Array.from(new Set(products.map((p) => p.category)))];

  if (loading) return <p style={{ padding: '24px' }}>Loading products...</p>;
  if (error) return <p style={{ padding: '24px', color: 'red' }}>{error}</p>;

  return (
    <section style={{ padding: '24px' }}>
      <h2>Product Catalog</h2>

      {/* Filter bar */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', margin: '16px 0' }}>
        <input
          type="text"
          placeholder="Search by product name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ padding: '8px', minWidth: '200px' }}
        />
        <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} style={{ padding: '8px' }}>
          {categories.map((cat) => <option key={cat} value={cat}>{cat}</option>)}
        </select>
        <select value={sortOption} onChange={(e) => setSortOption(e.target.value)} style={{ padding: '8px' }}>
          <option value="none">Sort by price (none)</option>
          <option value="price-asc">Price: Low → High</option>
          <option value="price-desc">Price: High → Low</option>
        </select>
        <button onClick={() => { setSearchTerm(''); setSelectedCategory('All'); setSortOption('none'); }}>
          Clear Filters
        </button>
      </div>

      <p style={{ color: '#555' }}>Showing {filteredProducts.length} of {products.length} products</p>
      <ProductList products={filteredProducts} />
    </section>
  );
};

export default ProductPage;