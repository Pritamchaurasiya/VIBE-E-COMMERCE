import React from "react";
import { NavLink, useLocation } from "react-router-dom";
import { Home, Store, AccountBalanceWallet, LocalOffer, Person } from "@mui/icons-material";
import "../../styles/agri-theme.css";

/**
 * AGRIM-Style Bottom Navigation Bar
 * 5 Tabs: Home | Store | Credit | Offers | Account
 */
const BottomNav = () => {
  const location = useLocation();

  const navItems = [
    {
      path: "/",
      label: "Home",
      icon: <Home />,
      activeIcon: <Home />,
    },
    {
      path: "/store",
      label: "Store",
      icon: <Store />,
      activeIcon: <Store />,
    },
    {
      path: "/credit",
      label: "Credit",
      icon: <AccountBalanceWallet />,
      activeIcon: <AccountBalanceWallet />,
    },
    {
      path: "/offers",
      label: "Offers",
      icon: <LocalOffer />,
      activeIcon: <LocalOffer />,
    },
    {
      path: "/account",
      label: "Account",
      icon: <Person />,
      activeIcon: <Person />,
    },
  ];

  // Check if current path matches nav item
  const isActive = (path) => {
    if (path === "/") {
      return location.pathname === "/";
    }
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="agri-bottom-nav" aria-label="Main navigation">
      {navItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={`agri-nav-item ${isActive(item.path) ? "active" : ""}`}
          aria-current={isActive(item.path) ? "page" : undefined}
        >
          <span className="agri-nav-item-icon">
            {item.icon}
          </span>
          <span className="agri-nav-item-label">{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
};

export default BottomNav;
