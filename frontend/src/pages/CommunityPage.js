import React, { useState, useEffect } from 'react';
import { Container, Typography, Card, CardContent, CardActionArea, Grid, CircularProgress, Box, Chip, Fab, Dialog, DialogTitle, DialogContent, TextField, DialogActions, Button } from '@mui/material';
import { Add as AddIcon, ThumbUp, Comment } from '@mui/icons-material';
import { forumAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

const CommunityPage = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [newPost, setNewPost] = useState({ title: '', content: '', category_id: '' });
  const navigate = useNavigate();

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await forumAPI.getPosts();
      setPosts(response.data);
    } catch (error) {
      console.error("Error fetching posts:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePost = async () => {
    try {
        // Using a default category for simplicity if not selected
        // Ideally fetch categories and show a dropdown
        await forumAPI.createPost({ ...newPost, category_id: 1 });
        setOpen(false);
        setNewPost({ title: '', content: '', category_id: '' });
        fetchPosts();
        alert('Post created successfully!');
    } catch (error) {
        alert('Failed to create post. Ensure you are logged in and a category exists.');
        console.error(error);
    }
  };

  if (loading) return <Box display="flex" justifyContent="center" p={5}><CircularProgress /></Box>;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main', mb: 4 }}>
        Farmer Community Forum
      </Typography>

      {posts.length === 0 ? (
          <Typography variant="body1" align="center">No posts yet. Be the first to start a discussion!</Typography>
      ) : (
        <Grid container spacing={3}>
            {posts.map((post) => (
            <Grid item xs={12} key={post.id}>
                <Card sx={{ boxShadow: 2 }}>
                <CardActionArea onClick={() => navigate(`/community/post/${post.id}`)}>
                    <CardContent>
                    <Typography variant="h6" gutterBottom>{post.title}</Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                        {post.content.length > 200 ? post.content.substring(0, 200) + '...' : post.content}
                    </Typography>
                    <Box display="flex" gap={2} alignItems="center">
                        <Chip icon={<ThumbUp />} label={post.likes_count || 0} size="small" variant="outlined" />
                        <Chip icon={<Comment />} label={post.comments?.length || 0} size="small" variant="outlined" />
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                        Posted by {post.author} on {new Date(post.created_at).toLocaleDateString()}
                        </Typography>
                    </Box>
                    </CardContent>
                </CardActionArea>
                </Card>
            </Grid>
            ))}
        </Grid>
      )}

      <Fab color="primary" sx={{ position: 'fixed', bottom: 32, right: 32 }} onClick={() => setOpen(true)}>
        <AddIcon />
      </Fab>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Create New Post</DialogTitle>
        <DialogContent>
            <TextField
                autoFocus
                margin="dense"
                label="Title"
                fullWidth
                variant="outlined"
                value={newPost.title}
                onChange={(e) => setNewPost({...newPost, title: e.target.value})}
            />
            <TextField
                margin="dense"
                label="Content"
                fullWidth
                multiline
                rows={6}
                variant="outlined"
                value={newPost.content}
                onChange={(e) => setNewPost({...newPost, content: e.target.value})}
                helperText="Share your question or experience..."
            />
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setOpen(false)}>Cancel</Button>
            <Button onClick={handleCreatePost} variant="contained">Post</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CommunityPage;
