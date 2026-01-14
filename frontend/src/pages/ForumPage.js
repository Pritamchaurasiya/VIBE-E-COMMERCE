import React, { useState, useEffect } from 'react';
import { Box, Typography, Container, Card, CardContent, CardActions, Button, TextField, Avatar, Divider, Chip, CircularProgress } from '@mui/material';
import { Favorite, Comment, AccessTime } from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../utils/AuthContext';

const ForumPage = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth(); // Assuming AuthContext provides user info

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await axios.get('/api/v1/community/posts/');
      setPosts(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching forum posts:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" color="primary">
          Community Forum
        </Typography>
        <Button variant="contained" color="primary">
          Create Post
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box>
          {posts.map((post) => (
            <Card key={post.id} sx={{ mb: 3, borderRadius: 2, boxShadow: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                    {post.author ? post.author[0].toUpperCase() : 'U'}
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {post.author || 'Anonymous'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center' }}>
                      <AccessTime fontSize="small" sx={{ mr: 0.5, fontSize: 14 }} />
                      {new Date(post.created_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                  <Chip
                    label={post.category || 'General'}
                    size="small"
                    sx={{ ml: 'auto' }}
                    color="primary"
                    variant="outlined"
                  />
                </Box>
                <Typography variant="h6" gutterBottom>
                  {post.title}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  {post.content.substring(0, 200)}...
                </Typography>
              </CardContent>
              <Divider />
              <CardActions sx={{ px: 2, py: 1.5 }}>
                <Button size="small" startIcon={<Favorite />}>
                  {post.like_count} Likes
                </Button>
                <Button size="small" startIcon={<Comment />}>
                  {post.comment_count} Comments
                </Button>
                <Button size="small" sx={{ ml: 'auto' }}>
                  Read More
                </Button>
              </CardActions>
            </Card>
          ))}
          {posts.length === 0 && (
            <Typography align="center" color="text.secondary">
                No posts yet. Be the first to start a discussion!
            </Typography>
          )}
        </Box>
      )}
    </Container>
  );
};

export default ForumPage;
