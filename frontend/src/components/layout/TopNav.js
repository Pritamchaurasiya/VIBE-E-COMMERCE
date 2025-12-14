import React, { useState, useEffect, useRef, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { productsAPI } from "../../services/api";
import { useCart } from "../../utils/CartContext";
import { useAuth } from "../../utils/AuthContext";
import "../../styles/agri-theme.css";
import { Search, Notifications, ShoppingCart, Spa, AccessTime, FavoriteBorder } from "@mui/icons-material";

/**
 * AGRIM-Style Top Navigation Bar
 * Features: Logo, Search with Autocomplete, Notifications, Cart, Wishlist
 */
const TopNav = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [recentSearches, setRecentSearches] = useState([]);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [notificationCount, setNotificationCount] = useState(0);
  const searchRef = useRef(null);
  const searchTimeout = useRef(null);
  const navigate = useNavigate();
  const { cartCount } = useCart();
  const { isAuthenticated } = useAuth();

  // Load recent searches from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("agri_recent_searches");
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved).slice(0, 5));
      } catch (parseError) {
        console.error("Failed to parse recent searches:", parseError.message);
        localStorage.removeItem("agri_recent_searches");
      }
    }

    // Fetch notification count
    const fetchNotificationCount = async () => {
      try {
        // This would be an API call in production
        setNotificationCount(3); // Mock count
      } catch (fetchError) {
        console.error("Failed to fetch notifications:", fetchError.message);
        setNotificationCount(0);
      }
    };

    if (isAuthenticated) {
      fetchNotificationCount();
    }
  }, [isAuthenticated]);

  // Handle search with debounce
  const handleSearch = useCallback(async (query) => {
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    setIsLoading(true);
    try {
      const response = await productsAPI.search(query);
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error("Search error:", error);
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Debounced search input handler
  const handleSearchInput = (e) => {
    const query = e.target.value;
    setSearchQuery(query);

    if (searchTimeout.current) {
      clearTimeout(searchTimeout.current);
    }

    searchTimeout.current = setTimeout(() => {
      handleSearch(query);
    }, 300);
  };

  // Save recent search
  const saveRecentSearch = (term) => {
    if (!term || term.length < 2) return;

    const updated = [
      term,
      ...recentSearches.filter((s) => s.toLowerCase() !== term.toLowerCase()),
    ].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem("agri_recent_searches", JSON.stringify(updated));
  };

  // Handle search submit
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      saveRecentSearch(searchQuery.trim());
      navigate(`/products?search=${encodeURIComponent(searchQuery)}`);
      setIsSearchOpen(false);
    }
  };

  // Handle clicking on a recent search
  const handleRecentSearchClick = (term) => {
    setSearchQuery(term);
    handleSearch(term);
  };

  // Handle clicking on a product result
  const handleProductClick = (product) => {
    saveRecentSearch(product.name);
    setIsSearchOpen(false);
    navigate(`/product/${product.slug}`);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setIsSearchOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <nav className="agri-top-nav">
      {/* Logo */}
      <Link to="/" className="agri-logo">
        <span className="agri-logo-icon"><Spa fontSize="medium" style={{ color: 'var(--agri-green-primary)' }} /></span>
        <span className="agri-logo-text">AGRI-VIBE</span>
      </Link>

      {/* Search Bar */}
      <div className="agri-search-wrapper" ref={searchRef}>
        <form onSubmit={handleSearchSubmit}>
          <input
            type="text"
            className="agri-search-input"
            placeholder="Search seeds, fertilizers, pesticides..."
            value={searchQuery}
            onChange={handleSearchInput}
            onFocus={() => setIsSearchOpen(true)}
            aria-label="Search products"
          />
          <span className="agri-search-icon">{isLoading ? "..." : <Search fontSize="small" />}</span>
        </form>

        {/* Search Dropdown */}
        {isSearchOpen && (
          <div className="agri-search-dropdown active">
            {/* Recent Searches */}
            {!searchQuery && recentSearches.length > 0 && (
              <>
                <div className="agri-search-section-title">Recent Searches</div>
                {recentSearches.map((term) => (
                  <button
                    key={term}
                    className="agri-search-item"
                    onClick={() => handleRecentSearchClick(term)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        handleRecentSearchClick(term);
                      }
                    }}
                    type="button"
                    style={{ cursor: "pointer", width: '100%', textAlign: 'left', background: 'none', border: 'none', padding: '8px 12px' }}
                  >
                    <span style={{ fontSize: "1.25rem", color: "#9E9E9E", marginRight: '10px' }}>
                      <AccessTime fontSize="small" />
                    </span>
                    <div className="agri-search-item-info">
                      <div className="agri-search-item-name">{term}</div>
                    </div>
                  </button>
                ))}
              </>
            )}

            {/* Search Results */}
            {searchQuery && searchResults.length > 0 && (
              <>
                <div className="agri-search-section-title">Products</div>
                {searchResults.slice(0, 6).map((product) => (
                  <button
                    key={product.id}
                    className="agri-search-item"
                    onClick={() => handleProductClick(product)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        handleProductClick(product);
                      }
                    }}
                    type="button"
                    style={{ cursor: "pointer", width: '100%', textAlign: 'left', background: 'none', border: 'none', padding: '8px 12px' }}
                  >
                    <img
                      src={product.image || "/placeholder-product.png"}
                      alt={product.name}
                      className="agri-search-item-img"
                    />
                    <div className="agri-search-item-info">
                      <div className="agri-search-item-name">
                        {product.name}
                      </div>
                      <div className="agri-search-item-category">
                        {product.category?.name || ""}
                      </div>
                    </div>
                    <div className="agri-search-item-price">
                      {new Intl.NumberFormat("en-IN", {
                        style: "currency",
                        currency: "INR",
                      }).format(product.price)}
                    </div>
                  </button>
                ))}
              </>
            )}

            {/* No Results */}
            {searchQuery && searchResults.length === 0 && !isLoading && (
              <div
                style={{
                  padding: "24px",
                  textAlign: "center",
                  color: "#9E9E9E",
                }}
              >
                No products found for "{searchQuery}"
              </div>
            )}
          </div>
        )}
      </div>

      {/* Nav Actions */}
      <div className="agri-nav-actions">
        {/* Wishlist */}
        <button
          className="agri-nav-btn"
          onClick={() => navigate("/wishlist")}
          aria-label="Wishlist"
        >
          <FavoriteBorder />
        </button>

        {/* Notifications */}
        <button
          className="agri-nav-btn"
          onClick={() => navigate("/notifications")}
          aria-label="Notifications"
        >
          <Notifications />
          {notificationCount > 0 && (
            <span className="agri-nav-badge">{notificationCount}</span>
          )}
        </button>

        {/* Cart */}
        <button
          className="agri-nav-btn"
          onClick={() => navigate("/cart")}
          aria-label="Shopping Cart"
        >
          <ShoppingCart />
          {cartCount > 0 && <span className="agri-nav-badge">{cartCount}</span>}
        </button>
      </div>
    </nav>
  );
};

export default TopNav;
