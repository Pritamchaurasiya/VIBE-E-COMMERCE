import React, { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import TopNav from "../components/layout/TopNav";
import BottomNav from "../components/layout/BottomNav";
import AgriProductCard from "../components/products/AgriProductCard";
import WeatherWidget from "../components/common/WeatherWidget";
import {
  productsAPI,
  wishlistAPI,
  recentlyViewedAPI,
  locationAPI,
  highMarginAPI,
  newlyLaunchedAPI,
  dealOfDayAPI
} from "../services/api";
import "../styles/agri-theme.css";
// Premium MUI Icons
import {
  Agriculture,
  Science,
  Spa,
  Grass,
  PestControl,
  Handyman,
  WaterDrop,
  LocalFlorist,
  BugReport,
  Coronavirus,
  Grain,
  ScatterPlot,
  Verified,
  LocalOffer,
  NewReleases,
  TrendingUp,
  Place,
  AccessTime,
  ContentCopy,
  ArrowForward,
  Category,
  Store
} from "@mui/icons-material";

/**
 * AGRIM-Style Homepage
 * Sections: Promo Banner, Deal of Day, Recently Viewed, Popular in City,
 * Shop by Category/Crop/Disease, High Margin, Newly Launched, Shop by Brand
 */
const AgriHome = () => {
  // State for various sections
  const [dealProducts, setDealProducts] = useState([]);
  const [recentlyViewed, setRecentlyViewed] = useState([]);
  const [popularProducts, setPopularProducts] = useState([]);
  const [trendingProducts, setTrendingProducts] = useState([]);
  const [newProducts, setNewProducts] = useState([]);
  const [userLocation, setUserLocation] = useState("Your City");
  const [isLoading, setIsLoading] = useState(true);

  // Deal timer state
  const [dealTimer, setDealTimer] = useState({
    hours: 23,
    minutes: 59,
    seconds: 59,
  });

  // Promo banner slides
  const promoSlides = [
    {
      id: 1,
      type: "gold",
      badge: "LIMITED OFFER",
      title: "Get ?400 OFF",
      subtitle: "On orders above ?2000",
      code: "APP400",
      image: <Agriculture fontSize="inherit" />,
    },
    {
      id: 2,
      type: "deal",
      badge: "FLASH SALE",
      title: "Up to 50% OFF",
      subtitle: "On all fertilizers",
      code: "FERT50",
      image: <Science fontSize="inherit" />,
    },
    {
      id: 3,
      type: "green",
      badge: "NEW ARRIVALS",
      title: "Premium Seeds",
      subtitle: "High yield varieties now available",
      code: "SEED100",
      image: <Spa fontSize="inherit" />,
    },
  ];

  const [currentSlide, setCurrentSlide] = useState(0);

  // Categories for Shop by Category
  const categories = [
    { id: 1, name: "Seeds", icon: <Grass />, slug: "seeds" },
    { id: 2, name: "Fertilizers", icon: <Science />, slug: "fertilizers" },
    { id: 3, name: "Pesticides", icon: <PestControl />, slug: "pesticides" },
    { id: 4, name: "Tools", icon: <Handyman />, slug: "tools" },
    { id: 5, name: "Irrigation", icon: <WaterDrop />, slug: "irrigation" },
    { id: 6, name: "Organic", icon: <LocalFlorist />, slug: "organic" },
  ];

  // Crops for Shop by Crop
  const crops = [
    { id: 1, name: "Cauliflower", icon: <Spa />, slug: "cauliflower" },
    { id: 2, name: "Bhindi", icon: <LocalFlorist />, slug: "bhindi" },
    { id: 3, name: "Radish", icon: <Grass />, slug: "radish" },
    { id: 4, name: "Tomato", icon: <Spa />, slug: "tomato" },
    { id: 5, name: "Potato", icon: <ScatterPlot />, slug: "potato" },
    { id: 6, name: "Onion", icon: <Spa />, slug: "onion" },
    { id: 7, name: "Wheat", icon: <Agriculture />, slug: "wheat" },
    { id: 8, name: "Rice", icon: <Grain />, slug: "rice" },
  ];

  // Diseases for Shop by Disease
  const diseases = [
    { id: 1, name: "Leaf Miner", icon: <BugReport />, slug: "leaf-miner" },
    { id: 2, name: "Powdery Mildew", icon: <ScatterPlot />, slug: "powdery-mildew" },
    { id: 3, name: "Aphids", icon: <PestControl />, slug: "aphids" },
    { id: 4, name: "Root Rot", icon: <Grass />, slug: "root-rot" },
    { id: 5, name: "Blight", icon: <Coronavirus />, slug: "blight" },
    { id: 6, name: "Whitefly", icon: <BugReport />, slug: "whitefly" },
  ];

  // Brands for Shop by Brand
  const brands = [
    { id: 1, name: "Sumitomo", logo: <Verified /> },
    { id: 2, name: "Gharda", logo: <Science /> },
    { id: 3, name: "Parijat", logo: <LocalFlorist /> },
    { id: 4, name: "Bayer", logo: <Science /> },
    { id: 5, name: "UPL", logo: <Agriculture /> },
    { id: 6, name: "Syngenta", logo: <Spa /> },
  ];

  // Fetch products data
  const fetchProducts = useCallback(async () => {
    setIsLoading(true);
    try {
      // Determine user location
      let city = "Varanasi";
      try {
        const locRes = await locationAPI.detect();
        if (locRes.data?.city) {
          city = locRes.data.city;
          setUserLocation(city);
        }
      } catch (e) {
        console.warn("Location detection failed, using default");
      }

      // Fetch various product lists
      const [dealsRes, , newRes, recentRes, popularLocRes, highMarginRes] = await Promise.all([
        dealOfDayAPI.get().catch(() => ({ data: { products: [] } })),
        productsAPI.getTrending().catch(() => ({ data: { products: [] } })),
        newlyLaunchedAPI.get().catch(() => ({ data: { products: [] } })),
        recentlyViewedAPI.getRecentlyViewed().catch(() => ({ data: { products: [] } })),
        locationAPI.getPopular(city).catch(() => ({ data: { products: [] } })),
        highMarginAPI.get().catch(() => ({ data: { products: [] } })),
      ]);

      setDealProducts(dealsRes.data?.products || []);
      setTrendingProducts(highMarginRes.data?.products || []);
      setNewProducts(newRes.data?.products || []);
      setRecentlyViewed(recentRes.data?.products || []);
      setPopularProducts(popularLocRes.data?.products || []);

    } catch (error) {
      console.error("Failed to fetch products:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts();

    // Detect user location (mock for now)
    setUserLocation("Varanasi");

    // Auto-slide promo banner
    const slideInterval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % promoSlides.length);
    }, 5000);

    return () => clearInterval(slideInterval);
  }, [fetchProducts, promoSlides.length]);

  // Deal countdown timer
  useEffect(() => {
    const timerInterval = setInterval(() => {
      setDealTimer((prev) => {
        if (prev.seconds > 0) {
          return { ...prev, seconds: prev.seconds - 1 };
        } else if (prev.minutes > 0) {
          return { ...prev, minutes: prev.minutes - 1, seconds: 59 };
        } else if (prev.hours > 0) {
          return { hours: prev.hours - 1, minutes: 59, seconds: 59 };
        }
        return prev;
      });
    }, 1000);

    return () => clearInterval(timerInterval);
  }, []);

  // Handle wishlist toggle
  const handleWishlistToggle = async (productId, isAdding) => {
    try {
      if (isAdding) {
        await wishlistAPI.add(productId);
      } else {
        await wishlistAPI.remove(productId);
      }
    } catch (error) {
      console.error("Wishlist toggle failed:", error);
    }
  };

  // Copy promo code
  const copyPromoCode = (code) => {
    navigator.clipboard.writeText(code);
    // Could show a toast notification here
  };

  return (
    <div className="agri-theme">
      <TopNav />

      <main className="agri-main">
        <div className="agri-container">
          <WeatherWidget />

          {/* ===== PROMO BANNER CAROUSEL ===== */}
          <section className="agri-promo-carousel">
            <div
              className={`agri-promo-slide ${promoSlides[currentSlide].type}`}
              style={{ transition: "all 0.5s ease" }}
            >
              <div className="agri-promo-content">
                <span className="agri-promo-badge">
                  {promoSlides[currentSlide].badge}
                </span>
                <h2 className="agri-promo-title">
                  {promoSlides[currentSlide].title}
                </h2>
                <p className="agri-promo-subtitle">
                  {promoSlides[currentSlide].subtitle}
                </p>
                <button
                  className="agri-promo-code"
                  onClick={() => copyPromoCode(promoSlides[currentSlide].code)}
                >
                  <ContentCopy fontSize="small" style={{ marginRight: 8 }} /> {promoSlides[currentSlide].code}
                </button>
              </div>
              <div className="agri-promo-image" style={{ fontSize: "5rem" }}>
                {promoSlides[currentSlide].image}
              </div>
            </div>

            {/* Carousel Dots */}
            <div className="agri-carousel-dots">
              {promoSlides.map((slide) => (
                <button
                  key={`slide-${slide.id}`}
                  className={`agri-carousel-dot ${slide.id - 1 === currentSlide ? "active" : ""}`}
                  onClick={() => setCurrentSlide(slide.id - 1)}
                  aria-label={`Go to slide ${slide.id}`}
                />
              ))}
            </div>
          </section>

          {/* ===== DEAL OF THE DAY ===== */}
          <section className="agri-deal-section">
            <div className="agri-deal-header">
              <h2 className="agri-deal-title"><LocalOffer style={{ color: '#ffffff', marginRight: 8 }} /> Deal of the Day</h2>
              <div className="agri-deal-timer">
                <div className="agri-timer-block">
                  <span className="agri-timer-value">
                    {String(dealTimer.hours).padStart(2, "0")}
                  </span>
                  <span className="agri-timer-label">Hours</span>
                </div>
                <div className="agri-timer-block">
                  <span className="agri-timer-value">
                    {String(dealTimer.minutes).padStart(2, "0")}
                  </span>
                  <span className="agri-timer-label">Mins</span>
                </div>
                <div className="agri-timer-block">
                  <span className="agri-timer-value">
                    {String(dealTimer.seconds).padStart(2, "0")}
                  </span>
                  <span className="agri-timer-label">Secs</span>
                </div>
              </div>
            </div>

            <div className="agri-deal-products">
              {isLoading
                ? new Array(4)
                    .fill(0)
                    .map((_, i) => (
                      <div
                        key={`deal-skeleton-${i}`}
                        className="agri-skeleton agri-skeleton-card"
                        style={{ width: 180, flexShrink: 0 }}
                      />
                    ))
                : dealProducts
                    .slice(0, 6)
                    .map((product) => (
                      <AgriProductCard
                        key={product.id}
                        product={product}
                        onWishlistToggle={handleWishlistToggle}
                      />
                    ))}
            </div>
          </section>

          {/* ===== RECENTLY VIEWED ===== */}
          {recentlyViewed.length > 0 && (
            <section className="agri-section">
              <div className="agri-section-header">
                <h2 className="agri-section-title">
                  <span className="agri-section-title-icon"><AccessTime /></span> Recently Viewed
                </h2>
                <Link to="/recently-viewed" className="agri-section-link">
                  View All <ArrowForward fontSize="small" style={{ marginLeft: '4px' }} />
                </Link>
              </div>

              <div className="agri-scroll-row">
                {recentlyViewed.map((product, index) => (
                  <AgriProductCard
                    key={product.id}
                    product={product}
                    showTrend={true}
                    trendPercentage={[79, -12, 45, -8][index % 4]}
                    onWishlistToggle={handleWishlistToggle}
                  />
                ))}
              </div>
            </section>
          )}

          {/* ===== POPULAR IN [CITY] ===== */}
          <section className="agri-section">
            <div className="agri-section-header">
              <h2 className="agri-section-title">
                <span className="agri-section-title-icon"><Place /></span> Popular in
                <span className="agri-location-badge" style={{ marginLeft: 8 }}>
                  {userLocation}
                </span>
              </h2>
              <Link to="/popular" className="agri-section-link">
                View All <ArrowForward fontSize="small" style={{ marginLeft: '4px' }} />
              </Link>
            </div>

            <div className="agri-scroll-row">
              {isLoading
                ? new Array(4)
                    .fill(0)
                    .map((_, i) => (
                      <div
                        key={`popular-skeleton-${i}`}
                        className="agri-skeleton agri-skeleton-card"
                        style={{ width: 180, flexShrink: 0 }}
                      />
                    ))
                : popularProducts.map((product) => (
                    <AgriProductCard
                      key={product.id}
                      product={product}
                      onWishlistToggle={handleWishlistToggle}
                    />
                  ))}
            </div>
          </section>

          {/* ===== SHOP BY CATEGORY ===== */}
          <section className="agri-section">
            <div className="agri-section-header">
              <h2 className="agri-section-title">
                <span className="agri-section-title-icon"><Category /></span> Shop by Category
              </h2>
            </div>

            <div className="agri-category-grid">
              {categories.map((category) => (
                <Link
                  key={category.id}
                  to={`/category/${category.slug}`}
                  className="agri-category-card"
                >
                  <span className="agri-category-icon mui-icon">
                    {category.icon}
                  </span>
                  <span className="agri-category-name">{category.name}</span>
                </Link>
              ))}
            </div>
          </section>

          {/* ===== SHOP BY CROP ===== */}
          <section className="agri-section">
            <div className="agri-section-header">
              <h2 className="agri-section-title">
                <span className="agri-section-title-icon"><Agriculture /></span> Shop by Crop
              </h2>
              <Link to="/crops" className="agri-section-link">
                View All <ArrowForward fontSize="small" style={{ marginLeft: '4px' }} />
              </Link>
            </div>

            <div className="agri-category-grid">
              {crops.map((crop) => (
                <Link
                  key={crop.id}
                  to={`/crop/${crop.slug}`}
                  className="agri-category-card"
                >
                  <span className="agri-category-icon mui-icon">{crop.icon}</span>
                  <span className="agri-category-name">{crop.name}</span>
                </Link>
              ))}
            </div>
          </section>

          {/* ===== SHOP BY DISEASE ===== */}
          <section className="agri-section">
            <div className="agri-section-header">
              <h2 className="agri-section-title">
                <span className="agri-section-title-icon"><BugReport /></span> Shop by Disease
              </h2>
              <Link to="/diseases" className="agri-section-link">
                View All <ArrowForward fontSize="small" style={{ marginLeft: '4px' }} />
              </Link>
            </div>

            <div className="agri-category-grid">
              {diseases.map((disease) => (
                <Link
                  key={disease.id}
                  to={`/disease/${disease.slug}`}
                  className="agri-category-card"
                >
                  <span className="agri-category-icon mui-icon">
                    {disease.icon}
                  </span>
                  <span className="agri-category-name">{disease.name}</span>
                </Link>
              ))}
            </div>
          </section>

          {/* ===== HIGH MARGIN PRODUCTS ===== */}
          <section className="agri-section">
            <div className="agri-section-header">
              <h2 className="agri-section-title">
                <span className="agri-section-title-icon"><TrendingUp /></span> High Margin Products
              </h2>
              <Link to="/high-margin" className="agri-section-link">
                View All <ArrowForward fontSize="small" style={{ marginLeft: '4px' }} />
              </Link>
            </div>

            <div className="agri-scroll-row">
              {trendingProducts.slice(0, 6).map((product) => (
                <AgriProductCard
                  key={product.id}
                  product={{
                    ...product,
                    margin_percentage: Math.floor(Math.random() * 20) + 15,
                  }}
                  showBulkPrice={true}
                  onWishlistToggle={handleWishlistToggle}
                />
              ))}
            </div>
          </section>

          {/* ===== NEWLY LAUNCHED ===== */}
          <section className="agri-section">
            <div className="agri-section-header">
              <h2 className="agri-section-title">
                <span className="agri-section-title-icon"><NewReleases /></span> Newly Launched
              </h2>
              <Link to="/new-arrivals" className="agri-section-link">
                View All <ArrowForward fontSize="small" style={{ marginLeft: '4px' }} />
              </Link>
            </div>

            <div className="agri-product-grid">
              {newProducts.slice(0, 4).map((product) => (
                <AgriProductCard
                  key={product.id}
                  product={{ ...product, is_new: true }}
                  onWishlistToggle={handleWishlistToggle}
                />
              ))}
            </div>
          </section>

          {/* ===== SHOP BY BRAND ===== */}
          <section className="agri-section">
            <div className="agri-section-header">
              <h2 className="agri-section-title">
                <span className="agri-section-title-icon"><Store /></span> Shop by Brand
              </h2>
              <Link to="/brands" className="agri-section-link">
                View All <ArrowForward fontSize="small" style={{ marginLeft: '4px' }} />
              </Link>
            </div>

            <div className="agri-brand-scroll">
              {brands.map((brand) => (
                <Link
                  key={brand.id}
                  to={`/brand/${brand.name.toLowerCase()}`}
                  className="agri-brand-card"
                >
                  <span style={{ fontSize: "2rem", color: 'var(--agri-green-primary)' }}>{brand.logo}</span>
                  <span style={{ fontSize: "0.75rem", marginTop: 4 }}>
                    {brand.name}
                  </span>
                </Link>
              ))}
            </div>
          </section>
        </div>
      </main>

      <BottomNav />
    </div>
  );
};

export default AgriHome;
