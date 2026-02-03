import React, { useState, useEffect } from 'react';
import {
  Container, Grid, Card, CardHeader, CardContent, CardActions, Typography, Button,
  Avatar, TextField, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Collapse, Box
} from '@mui/material';
import { forumAPI } from '../services/api';
import { Favorite, Comment, Add } from '@mui/icons-material';

const CommunityPage = () => {
  const [posts, setPosts] = useState([]);
  const [open, setOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [expandedPost, setExpandedPost] = useState(null);
  const [comments, setComments] = useState({});
  const [newComment, setNewComment] = useState('');

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await forumAPI.getPosts();
      const data = response.data.results || response.data || [];
      setPosts(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error fetching posts:", error);
    }
  };

  const handleCreatePost = async () => {
    try {
      await forumAPI.createPost({ title: newTitle, content: newContent });
      setOpen(false);
      setNewTitle('');
      setNewContent('');
      fetchPosts();
    } catch (error) {
      console.error("Error creating post:", error);
      alert('Failed to create post');
    }
  };

  const handleExpandClick = async (postId) => {
    if (expandedPost === postId) {
      setExpandedPost(null);
    } else {
      setExpandedPost(postId);
      if (!comments[postId]) {
        try {
          const response = await forumAPI.getComments(postId);
          const data = response.data.results || response.data || [];
          setComments(prev => ({ ...prev, [postId]: data }));
        } catch (error) {
          console.error("Error fetching comments:", error);
        }
      }
    }
  };

  const handlePostComment = async (postId) => {
    try {
      await forumAPI.createComment({ post: postId, content: newComment });
      setNewComment('');
      // Refresh comments
      const response = await forumAPI.getComments(postId);
      const data = response.data.results || response.data || [];
      setComments(prev => ({ ...prev, [postId]: data }));
    } catch (error) {
      console.error("Error posting comment:", error);
    }
  };

  return (
    <Container sx={{ py: 4 }}>
      <Grid container justifyContent="space-between" alignItems="center" mb={4}>
        <Grid item>
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: '#ff9800' }}>
            Farmer Community
          </Typography>
          <Typography variant="body1">
            Connect, share knowledge, and grow together.
          </Typography>
        </Grid>
        <Grid item>
          <Button
            variant="contained"
            startIcon={<Add />}
            color="warning"
            onClick={() => setOpen(true)}
          >
            Create Post
          </Button>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {posts.length > 0 ? (
          posts.map((post) => (
            <Grid item xs={12} key={post.id}>
              <Card>
                <CardHeader
                  avatar={<Avatar sx={{ bgcolor: '#ff9800' }}>{post.user ? post.user[0].toUpperCase() : 'U'}</Avatar>}
                  title={post.title}
                  subheader={`Posted by ${post.user} on ${new Date(post.created_at).toLocaleDateString()}`}
                />
                <CardContent>
                  <Typography variant="body1">
                    {post.content}
                  </Typography>
                </CardContent>
                <CardActions disableSpacing>
                  <IconButton aria-label="add to favorites">
                    <Favorite color={post.is_liked ? "error" : "action"} />
                  </IconButton>
                  <Typography variant="body2" color="text.secondary">
                    {post.likes_count}
                  </Typography>
                  <IconButton
                    onClick={() => handleExpandClick(post.id)}
                    aria-expanded={expandedPost === post.id}
                    aria-label="show more"
                    sx={{ ml: 'auto' }}
                  >
                    <Comment />
                  </IconButton>
                </CardActions>
                <Collapse in={expandedPost === post.id} timeout="auto" unmountOnExit>
                  <CardContent>
                    <Typography paragraph variant="subtitle2">Comments:</Typography>
                    {comments[post.id]?.length > 0 ? (
                      comments[post.id].map((comment) => (
                        <Typography key={comment.id} paragraph variant="body2" sx={{ bgcolor: '#f5f5f5', p: 1, borderRadius: 1 }}>
                          <strong>{comment.user}:</strong> {comment.content}
                        </Typography>
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary" paragraph>No comments yet.</Typography>
                    )}
                    <Box display="flex" mt={2}>
                      <TextField
                        fullWidth
                        size="small"
                        placeholder="Write a comment..."
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                      />
                      <Button onClick={() => handlePostComment(post.id)} sx={{ ml: 1 }}>Post</Button>
                    </Box>
                  </CardContent>
                </Collapse>
              </Card>
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
            <Typography align="center" color="text.secondary">No posts yet. Be the first to share something!</Typography>
          </Grid>
        )}
      </Grid>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Create New Post</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Title"
            fullWidth
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
          />
          <TextField
            margin="dense"
            label="Content"
            fullWidth
            multiline
            rows={4}
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreatePost} variant="contained" color="warning">Post</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CommunityPage;
