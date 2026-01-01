import React, { useState } from "react";
import PropTypes from "prop-types";
import { Link, useNavigate } from "react-router-dom";
import { useCart } from "../../utils/CartContext";
import { useAuth } from "../../utils/AuthContext";
import { CircularProgress } from "@mui/material";
import "../../styles/agri-theme.css";
import {
  Whatshot,
  Favorite,
  FavoriteBorder,
  Inventory,
  Check,
  TrendingUp,
  TrendingDown,
  Add
} from "@mui/icons-material";

/**
 * AGRIM-Style Product Card
 * Features: Badges, Packing options, Price trends, Bulk pricing, Add to Cart
 */
const AgriProductCard = ({
  product,
  showTrend = false,
  trendPercentage = 0,
  showBulkPrice = true,
  onWishlistToggle,
}) => {
  const [selectedPacking, setSelectedPacking] = useState(0);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [isInWishlist, setIsInWishlist] = useState(
    product.in_wishlist || false,
  );
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();

  // Parse packing options (from JSON or default)
  const packingOptions = product.packing_options || [
    { size: product.unit || "1 Unit", price: product.price },
  ];

  // Parse bulk pricing logic based on model fields or JSON
  const bulkPricing = product.bulk_pricing || (product.bulk_price && product.bulk_min_quantity ? {
    price: product.bulk_price,
    min_qty: product.bulk_min_quantity
  } : null);

  // Current selected price
  const currentPrice = packingOptions[selectedPacking]?.price || product.price;
  const mrp = product.mrp || product.compare_at_price || currentPrice * 1.15;
  const discountPercent = Math.round(((mrp - currentPrice) / mrp) * 100);

  // Handle add to cart
  const handleAddToCart = async (e) => {
    e.stopPropagation();
    if (loading || success) return;

    setLoading(true);

    try {
      await addToCart(product.id, 1, packingOptions[selectedPacking]?.size);
      setLoading(false);
      setSuccess(true);
      // Briefly show success state
      setTimeout(() => setSuccess(false), 2000);
    } catch (error) {
      console.error("Failed to add to cart:", error);
      setLoading(false);
    }
  };

  // Handle wishlist toggle
  const handleWishlistClick = (e) => {
    e.stopPropagation();
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    setIsInWishlist(!isInWishlist);
    if (onWishlistToggle) {
      onWishlistToggle(product.id, !isInWishlist);
    }
  };

  return (
    <article className="agri-product-card">
      {/* Badges */}
      <div className="agri-product-badges">
        {product.is_instant_pack && (
          <span className="agri-badge agri-badge-instant">Instant Pack</span>
        )}
        {product.is_new && (
          <span className="agri-badge agri-badge-new">New</span>
        )}
        {product.trending_score > 80 && (
          <span className="agri-badge agri-badge-trending"><Whatshot fontSize="small" style={{ fontSize: '0.8rem', verticalAlign: 'text-bottom' }} /> Trending</span>
        )}
        {!product.is_instant_pack &&
          !product.is_new &&
          discountPercent >= 10 && (
            <span className="agri-badge agri-badge-discount">
              {discountPercent}% OFF
            </span>
          )}
      </div>

      {/* Wishlist Button */}
      <button
        className={`agri-product-wishlist ${isInWishlist ? "active" : ""}`}
        onClick={handleWishlistClick}
        aria-label={isInWishlist ? "Remove from wishlist" : "Add to wishlist"}
      >
        {isInWishlist ? <Favorite fontSize="small" /> : <FavoriteBorder fontSize="small" />}
      </button>

      {/* Product Image */}
      <Link
        to={`/product/${product.slug}`}
        className="agri-product-image-wrapper d-block"
        tabIndex="0"
      >
        <img
          src={product.image || "/placeholder-product.png"}
          alt={product.name}
          className="agri-product-image"
          loading="lazy"
        />
      </Link>

      {/* Product Info */}
      <div className="agri-product-info">
        {/* Brand */}
        {product.brand && (
          <div className="agri-product-brand">{product.brand}</div>
        )}

        {/* Name */}
        <h3 className="agri-product-name">
            <Link to={`/product/${product.slug}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                {product.name}
            </Link>
        </h3>

        {/* Packing Options */}
        {packingOptions.length > 1 && (
          <div className="agri-product-packing" role="group" aria-label="Packing options">
            {packingOptions.slice(0, 3).map((option, optionIndex) => (
              <button
                type="button"
                key={`pack-${option.size}`}
                className={`agri-packing-option ${selectedPacking === optionIndex ? "active" : ""}`}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedPacking(optionIndex);
                }}
                aria-pressed={selectedPacking === optionIndex}
                aria-label={`Select ${option.size} pack`}
              >
                {option.size}
              </button>
            ))}
            {packingOptions.length > 3 && (
              <span className="agri-packing-option agri-packing-more" role="presentation">
                +{packingOptions.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Pricing */}
        <div className="agri-product-pricing">
          <div className="agri-price-row">
            <span className="agri-price-current">
              ₹{currentPrice.toLocaleString()}
            </span>
            {mrp > currentPrice && (
              <>
                <span className="agri-price-mrp">₹{mrp.toLocaleString()}</span>
                <span className="agri-price-discount">
                  {discountPercent}% OFF
                </span>
              </>
            )}
          </div>

          {/* Price Trend */}
          {showTrend && trendPercentage !== 0 && (
            <span
              className={`agri-price-trend ${trendPercentage > 0 ? "up" : "down"}`}
            >
              {trendPercentage > 0 ? <TrendingUp fontSize="small" style={{ fontSize: '0.8rem' }} /> : <TrendingDown fontSize="small" style={{ fontSize: '0.8rem' }} />} {Math.abs(trendPercentage)}%
            </span>
          )}

          {/* Bulk Pricing */}
          {showBulkPrice && bulkPricing && (
            <div className="agri-price-bulk">
              <Inventory fontSize="small" style={{ fontSize: '0.9rem', marginRight: 4 }} /> Bulk: ₹{bulkPricing.price}/unit ({bulkPricing.min_qty}+ units)
            </div>
          )}
        </div>

        {/* Add to Cart Button */}
        <button
          type="button"
          className={`agri-add-to-cart ${success ? "added" : ""}`}
          onClick={handleAddToCart}
          disabled={loading}
          aria-live="polite"
        >
          {loading ? (
            <CircularProgress size={20} color="inherit" />
          ) : success ? (
            <><Check fontSize="small" /> Added</>
          ) : (
            <><Add fontSize="small" /> Add to Cart</>
          )}
        </button>
      </div>
    </article>
  );
};

AgriProductCard.propTypes = {
  product: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    slug: PropTypes.string.isRequired,
    price: PropTypes.number.isRequired,
    image: PropTypes.string,
    brand: PropTypes.string,
    mrp: PropTypes.number,
    compare_at_price: PropTypes.number,
    unit: PropTypes.string,
    packing_options: PropTypes.arrayOf(
      PropTypes.shape({
        size: PropTypes.string,
        price: PropTypes.number,
      }),
    ),
    bulk_pricing: PropTypes.shape({
      min_qty: PropTypes.number,
      price: PropTypes.number,
    }),
    bulk_price: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    bulk_min_quantity: PropTypes.number,
    is_instant_pack: PropTypes.bool,
    is_new: PropTypes.bool,
    trending_score: PropTypes.number,
    in_wishlist: PropTypes.bool,
  }).isRequired,
  showTrend: PropTypes.bool,
  trendPercentage: PropTypes.number,
  showBulkPrice: PropTypes.bool,
  onWishlistToggle: PropTypes.func,
};

export default AgriProductCard;
