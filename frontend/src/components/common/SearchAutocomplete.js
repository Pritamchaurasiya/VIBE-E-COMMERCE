import React, { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import PropTypes from "prop-types";
import {
  Box,
  TextField,
  InputAdornment,
  Paper,
  List,
  ListItemText,
  ListItemAvatar,
  ListItemButton,
  Avatar,
  Typography,
  Chip,
  CircularProgress,
  Divider,
  IconButton,
  Popper,
  Fade,
  ClickAwayListener,
} from "@mui/material";
import {
  Search as SearchIcon,
  Clear,
  TrendingUp,
  History,
  Category,
} from "@mui/icons-material";
import { productsAPI } from "../../services/api";
import debounce from "lodash/debounce";

const SEARCH_HISTORY_KEY = "vibe_search_history";
const MAX_HISTORY = 5;

/**
 * Enhanced Search component with autocomplete, suggestions, and history
 */
const SearchAutocomplete = ({
  onSearch,
  placeholder = "Search products...",
  fullWidth = false,
}) => {
  const navigate = useNavigate();
  const inputRef = useRef(null);
  const anchorRef = useRef(null);

  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);

  // Popular searches (could be fetched from API)
  const popularSearches = [
    "Fertilizers",
    "Seeds",
    "Pesticides",
    "Organic Products",
    "Farm Equipment",
  ];

  // Load search history from localStorage
  useEffect(() => {
    try {
      const history = JSON.parse(
        localStorage.getItem(SEARCH_HISTORY_KEY) || "[]",
      );
      setSearchHistory(history.slice(0, MAX_HISTORY));
    } catch {
      setSearchHistory([]);
    }
  }, []);

  // Save to search history
  const saveToHistory = useCallback((searchTerm) => {
    if (!searchTerm.trim()) return;

    try {
      const history = JSON.parse(
        localStorage.getItem(SEARCH_HISTORY_KEY) || "[]",
      );
      const filtered = history.filter(
        (h) => h.toLowerCase() !== searchTerm.toLowerCase(),
      );
      const newHistory = [searchTerm, ...filtered].slice(0, MAX_HISTORY);
      localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(newHistory));
      setSearchHistory(newHistory);
    } catch {
      // Ignore storage errors
    }
  }, []);

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce(async (searchQuery) => {
      if (!searchQuery.trim() || searchQuery.length < 2) {
        setResults([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const response = await productsAPI.getProducts({
          search: searchQuery,
          limit: 5,
        });
        setResults(response.data.results || response.data || []);
      } catch (error) {
        console.error("Search error:", error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300),
    [],
  );

  // Handle input change
  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    setOpen(true);
    debouncedSearch(value);
  };

  // Handle search submission
  const handleSearch = (searchTerm = query) => {
    if (searchTerm.trim()) {
      saveToHistory(searchTerm.trim());
      setOpen(false);
      setQuery("");

      if (onSearch) {
        onSearch(searchTerm.trim());
      } else {
        navigate(`/products?search=${encodeURIComponent(searchTerm.trim())}`);
      }
    }
  };

  // Handle key press
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  // Handle product click
  const handleProductClick = (product) => {
    setOpen(false);
    setQuery("");
    navigate(`/products/${product.slug}`);
  };

  // Handle clear
  const handleClear = () => {
    setQuery("");
    setResults([]);
    inputRef.current?.focus();
  };

  // Clear search history
  const clearHistory = () => {
    localStorage.removeItem(SEARCH_HISTORY_KEY);
    setSearchHistory([]);
  };

  const showSuggestions =
    open && (query.length > 0 || searchHistory.length > 0);

  return (
    <ClickAwayListener onClickAway={() => setOpen(false)}>
      <Box
        ref={anchorRef}
        sx={{
          position: "relative",
          width: fullWidth ? "100%" : { xs: "100%", md: 400 },
        }}
      >
        <TextField
          ref={inputRef}
          fullWidth
          size="small"
          placeholder={placeholder}
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setOpen(true)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                {loading && <CircularProgress size={20} />}
                {!loading && query && (
                  <IconButton size="small" onClick={handleClear}>
                    <Clear fontSize="small" />
                  </IconButton>
                )}
              </InputAdornment>
            ),
          }}
          sx={{
            "& .MuiOutlinedInput-root": {
              borderRadius: 3,
              backgroundColor: "background.paper",
              "&:hover": {
                "& .MuiOutlinedInput-notchedOutline": {
                  borderColor: "primary.main",
                },
              },
            },
          }}
        />

        <Popper
          open={showSuggestions}
          anchorEl={anchorRef.current}
          placement="bottom-start"
          transition
          style={{
            width: anchorRef.current?.offsetWidth,
            zIndex: 1300,
          }}
        >
          {({ TransitionProps }) => (
            <Fade {...TransitionProps} timeout={200}>
              <Paper
                elevation={8}
                sx={{
                  mt: 1,
                  maxHeight: 400,
                  overflow: "auto",
                  borderRadius: 2,
                }}
              >
                {/* Search Results */}
                {query.length >= 2 && results.length > 0 && (
                  <>
                    <Typography
                      variant="overline"
                      sx={{
                        px: 2,
                        pt: 1,
                        display: "block",
                        color: "text.secondary",
                      }}
                    >
                      Products
                    </Typography>
                    <List dense>
                      {results.map((product) => (
                        <ListItemButton
                          key={product.id}
                          onClick={() => handleProductClick(product)}
                        >
                          <ListItemAvatar>
                            <Avatar
                              src={product.image}
                              variant="rounded"
                              sx={{ width: 40, height: 40 }}
                            >
                              <Category />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={product.name}
                            secondary={
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 1,
                                }}
                              >
                                <Typography
                                  variant="body2"
                                  color="primary"
                                  fontWeight="bold"
                                >
                                  {'\u20B9'}{product.price}
                                </Typography>
                                {product.vendor_name && (
                                  <>
                                    <Typography
                                      variant="body2"
                                      color="text.secondary"
                                    >
                                      {'\u2022'}
                                    </Typography>
                                    <Typography
                                      variant="body2"
                                      color="text.secondary"
                                    >
                                      {product.vendor_name}
                                    </Typography>
                                  </>
                                )}
                              </Box>
                            }
                          />
                        </ListItemButton>
                      ))}
                    </List>
                    <Divider />
                    <ListItemButton
                      onClick={() => handleSearch()}
                      sx={{ justifyContent: "center" }}
                    >
                      <Typography variant="body2" color="primary">
                        View all results for "{query}"
                      </Typography>
                    </ListItemButton>
                  </>
                )}

                {/* No Results */}
                {query.length >= 2 && results.length === 0 && !loading && (
                  <Box sx={{ p: 2, textAlign: "center" }}>
                    <Typography variant="body2" color="text.secondary">
                      No products found for "{query}"
                    </Typography>
                  </Box>
                )}

                {/* Search History */}
                {query.length < 2 && searchHistory.length > 0 && (
                  <>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        px: 2,
                        pt: 1,
                      }}
                    >
                      <Typography variant="overline" color="text.secondary">
                        Recent Searches
                      </Typography>
                      <Typography
                        variant="caption"
                        color="primary"
                        sx={{
                          cursor: "pointer",
                          "&:hover": { textDecoration: "underline" },
                        }}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            clearHistory();
                          }
                        }}
                        onClick={clearHistory}
                      >
                        Clear
                      </Typography>
                    </Box>
                    <List dense>
                      {searchHistory.map((term) => (
                        <ListItemButton
                          key={`history-${term}`}
                          onClick={() => {
                            setQuery(term);
                            handleSearch(term);
                          }}
                        >
                          <ListItemAvatar>
                            <Avatar sx={{ bgcolor: "transparent" }}>
                              <History color="action" />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText primary={term} />
                        </ListItemButton>
                      ))}
                    </List>
                    <Divider />
                  </>
                )}

                {/* Popular Searches */}
                {query.length < 2 && (
                  <>
                    <Typography
                      variant="overline"
                      sx={{
                        px: 2,
                        pt: 1,
                        display: "block",
                        color: "text.secondary",
                      }}
                    >
                      <TrendingUp
                        fontSize="small"
                        sx={{ verticalAlign: "middle", mr: 0.5 }}
                      />
                      Popular Searches
                    </Typography>
                    <Box
                      sx={{ p: 1.5, display: "flex", flexWrap: "wrap", gap: 1 }}
                    >
                      {popularSearches.map((term) => (
                        <Chip
                          key={`popular-${term}`}
                          label={term}
                          size="small"
                          onClick={() => {
                            setQuery(term);
                            handleSearch(term);
                          }}
                          sx={{
                            "&:hover": {
                              backgroundColor: "primary.light",
                              color: "primary.contrastText",
                            },
                          }}
                        />
                      ))}
                    </Box>
                  </>
                )}
              </Paper>
            </Fade>
          )}
        </Popper>
      </Box>
    </ClickAwayListener>
  );
};

SearchAutocomplete.propTypes = {
  onSearch: PropTypes.func,
  placeholder: PropTypes.string,
  fullWidth: PropTypes.bool,
};

export default SearchAutocomplete;
