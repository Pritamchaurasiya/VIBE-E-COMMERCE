import React, { useState, useEffect } from 'react';
import {
  Container, Typography, Box, Grid, Paper, List, ListItem,
  ListItemText, ListItemIcon, Divider, Chip, LinearProgress
} from '@mui/material';
import {
  MonetizationOn, History, TrendingUp, TrendingDown, Star
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { coinsAPI } from '../../services/api';
import { LoadingSpinner } from '../common/LoadingSkeleton';

const MyRewards = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCoins = async () => {
      try {
        const response = await coinsAPI.getBalance();
        setData(response.data);
      } catch (error) {
        console.error("Failed to fetch rewards", error);
      } finally {
        setLoading(false);
      }
    };
    fetchCoins();
  }, []);

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <LoadingSpinner />
      </Container>
    );
  }

  // Calculate progress to next tier (example logic)
  const nextTier = 1000;
  const progress = Math.min((data?.lifetime_earned / nextTier) * 100, 100);

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          My Rewards
        </Typography>
        <Typography color="text.secondary">
          Earn coins with every purchase and redeem them for discounts.
        </Typography>
      </Box>

      {/* Balance Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper
            elevation={3}
            sx={{
              p: 3,
              background: 'linear-gradient(135deg, #FFD700 0%, #FDB931 100%)',
              color: '#333',
              borderRadius: 3,
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            <Box sx={{ position: 'relative', zIndex: 1 }}>
              <Typography variant="subtitle1" fontWeight="bold" sx={{ opacity: 0.8 }}>
                Current Balance
              </Typography>
              <Typography variant="h2" fontWeight="bold">
                {data?.balance || 0}
              </Typography>
              <Typography variant="body2" fontWeight="medium">
                VIBE COINS
              </Typography>
            </Box>
            <MonetizationOn
              sx={{
                position: 'absolute',
                right: -20,
                bottom: -20,
                fontSize: 150,
                opacity: 0.2,
                color: 'white'
              }}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: '100%', borderRadius: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Lifetime Earned
                </Typography>
                <Typography variant="h5" fontWeight="bold" color="success.main">
                  +{data?.lifetime_earned || 0}
                </Typography>
              </Box>
              <Box sx={{ textAlign: 'right' }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Lifetime Spent
                </Typography>
                <Typography variant="h5" fontWeight="bold" color="error.main">
                  -{data?.lifetime_spent || 0}
                </Typography>
              </Box>
            </Box>

            <Divider sx={{ my: 2 }} />

            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" fontWeight="bold">
                  Progress to Gold Tier
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {data?.lifetime_earned || 0} / {nextTier}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Transaction History */}
      <Paper elevation={2} sx={{ borderRadius: 3, overflow: 'hidden' }}>
        <Box sx={{ p: 2, bgcolor: 'grey.50', borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <History /> Transaction History
          </Typography>
        </Box>
        <List>
          {data?.recent_transactions?.length > 0 ? (
            data.recent_transactions.map((transaction, index) => (
              <React.Fragment key={index}>
                <ListItem>
                  <ListItemIcon>
                    {transaction.type === 'credit' ? (
                      <TrendingUp color="success" />
                    ) : (
                      <TrendingDown color="error" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={transaction.reason || (transaction.type === 'credit' ? 'Coins Earned' : 'Coins Spent')}
                    secondary={new Date(transaction.date).toLocaleDateString()}
                  />
                  <Typography
                    fontWeight="bold"
                    color={transaction.type === 'credit' ? 'success.main' : 'error.main'}
                  >
                    {transaction.type === 'credit' ? '+' : '-'}{transaction.amount}
                  </Typography>
                </ListItem>
                {index < data.recent_transactions.length - 1 && <Divider component="li" />}
              </React.Fragment>
            ))
          ) : (
            <ListItem>
              <ListItemText
                primary="No transactions yet"
                secondary="Start shopping to earn rewards!"
                sx={{ textAlign: 'center', py: 4 }}
              />
            </ListItem>
          )}
        </List>
      </Paper>
    </Container>
  );
};

export default MyRewards;
