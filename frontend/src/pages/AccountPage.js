import React from "react";
import { Link } from "react-router-dom";
import TopNav from "../components/layout/TopNav";
import BottomNav from "../components/layout/BottomNav";
import { useAuth } from "../utils/AuthContext";
import "../styles/agri-theme.css";
import {
  Business,
  ShoppingBag,
  LocationOn,
  AccountBalanceWallet,
  LocalOffer,
  Favorite,
  Notifications,
  Settings,
  Help,
  ExitToApp,
  Person,
  MonetizationOn
} from "@mui/icons-material";

/**
 * AGRIM-Style Account Page
 * Business profile, coin balance, menu options
 */
const AccountPage = () => {
  const { user, isAuthenticated, logout } = useAuth();

  // Account menu items
  const menuItems = [
    {
      icon: <Business />,
      title: "Business Profile",
      subtitle: "PAN, GST, Address details",
      path: "/account/business",
    },
    {
      icon: <ShoppingBag />,
      title: "My Orders",
      subtitle: "Track and manage orders",
      path: "/orders",
    },
    {
      icon: <LocationOn />,
      title: "Shipping Addresses",
      subtitle: "Manage delivery locations",
      path: "/account/addresses",
    },
    {
      icon: <AccountBalanceWallet />,
      title: "Credit & Statements",
      subtitle: "View credit limit and invoices",
      path: "/credit",
    },
    {
      icon: <LocalOffer />,
      title: "My Offers",
      subtitle: "Active coupons and rewards",
      path: "/offers",
    },
    {
      icon: <Favorite />,
      title: "Wishlist",
      subtitle: "Saved products",
      path: "/wishlist",
    },
    {
      icon: <Notifications />,
      title: "Notification Settings",
      subtitle: "Manage alerts and preferences",
      path: "/account/notifications",
    },
    {
      icon: <Settings />,
      title: "App Settings",
      subtitle: "Language, theme, privacy",
      path: "/account/settings",
    },
    {
      icon: <Help />,
      title: "Help & Support",
      subtitle: "FAQs, contact support",
      path: "/help",
    },
  ];

  if (!isAuthenticated) {
    return (
      <div className="agri-theme">
        <TopNav />
        <main className="agri-main">
          <div
            className="agri-container"
            style={{ textAlign: "center", paddingTop: 80 }}
          >
            <div style={{ marginBottom: 16, color: "var(--agri-green-primary)" }}>
              <Person style={{ fontSize: "4rem" }} />
            </div>
            <h2 style={{ marginBottom: 8 }}>Welcome to AGRI-VIBE</h2>
            <p style={{ color: "#666", marginBottom: 24 }}>
              Login to access your account
            </p>
            <Link
              to="/login"
              style={{
                display: "inline-block",
                padding: "12px 32px",
                background: "var(--agri-green-primary)",
                color: "white",
                borderRadius: "8px",
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              Login / Register
            </Link>
          </div>
        </main>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="agri-theme">
      <TopNav />

      {/* Account Header */}
      <div className="agri-account-header">
        <div className="agri-account-info">
          <div className="agri-account-avatar">
            <Person style={{ fontSize: "2rem", color: "white" }} />
          </div>
          <div>
            <div className="agri-account-name">
              {user?.first_name || "User"} {user?.last_name || ""}
            </div>
            <div className="agri-account-business">
              {user?.business_name || "Agricultural Retailer"}
            </div>
            <div className="agri-coin-balance">
              <MonetizationOn style={{ fontSize: "1rem", marginRight: 4 }} />
              {user?.coin_balance || 250} Coins
            </div>
          </div>
        </div>
      </div>

      <main className="agri-main" style={{ paddingTop: 0 }}>
        {/* Account Menu */}
        <div className="agri-account-menu" style={{ marginTop: -16 }}>
          {menuItems.map((item) => (
            <Link key={item.path} to={item.path} className="agri-account-menu-item">
              <span className="agri-account-menu-icon" style={{ color: "var(--agri-green-primary)" }}>
                {React.cloneElement(item.icon, { fontSize: "medium" })}
              </span>
              <div className="agri-account-menu-text">
                <div className="agri-account-menu-title">{item.title}</div>
                <div className="agri-account-menu-subtitle">
                  {item.subtitle}
                </div>
              </div>
              <span className="agri-account-menu-arrow">?</span>
            </Link>
          ))}
        </div>

        {/* Logout Button */}
        <div
            className="agri-container"
            style={{ marginTop: 24, marginBottom: 24 }}
        >
            <button
            onClick={logout}
            style={{
                width: "100%",
                padding: "14px",
                background: "white",
                border: "1px solid #E53935",
                color: "#E53935",
                borderRadius: "12px",
                fontWeight: 600,
                fontSize: "1rem",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px"
            }}
            >
            <ExitToApp /> Logout
            </button>
        </div>

        {/* App Version */}
        <div
          style={{
            textAlign: "center",
            color: "#9E9E9E",
            fontSize: "0.75rem",
            paddingBottom: 80,
          }}
        >
          AGRI-VIBE v1.0.0
        </div>
      </main>

      <BottomNav />
    </div>
  );
};

export default AccountPage;
