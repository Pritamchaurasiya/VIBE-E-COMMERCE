import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Typography, Card, CardContent, Divider, Box, TextField, Button, CircularProgress, Avatar } from '@mui/material';
import { forumAPI } from '../services/api';

const ForumPostDetail = () => {
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [comment, setComment] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchPost();
  }, [id]);

  const fetchPost = async () => {
    try {
      const response = await forumAPI.getPost(id);
      setPost(response.data);
    } catch (error) {
      console.error("Error fetching post:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCommentSubmit = async () => {
    if (!comment.trim()) return;
    try {
      await forumAPI.createComment(id, { content: comment });
      setComment('');
      fetchPost(); // Refresh to see new comment
    } catch (error) {
      alert('Failed to post comment');
    }
  };

  if (loading) return <Box display="flex" justifyContent="center" p={5}><CircularProgress /></Box>;
  if (!post) return <Container><Typography variant="h5" sx={{ mt: 4 }}>Post not found</Typography></Container>;

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Button onClick={() => navigate('/community')} sx={{ mb: 2 }}>&larr; Back to Forum</Button>

      <Card sx={{ mb: 4, boxShadow: 3 }}>
        <CardContent>
          <Typography variant="h4" gutterBottom fontWeight="bold">{post.title}</Typography>
          <Box display="flex" alignItems="center" mb={2}>
            <Avatar sx={{ bgcolor: 'secondary.main', mr: 1 }}>{post.author ? post.author[0].toUpperCase() : 'U'}</Avatar>
            <Typography variant="subtitle2" color="text.secondary">
              Posted by {post.author} on {new Date(post.created_at).toLocaleDateString()}
            </Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
            {post.content}
          </Typography>
        </CardContent>
      </Card>

      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Comments ({post.comments?.length || 0})
      </Typography>

      <Box component="form" sx={{ mb: 4 }}>
        <TextField
          fullWidth
          multiline
          rows={3}
          variant="outlined"
          placeholder="Add a comment..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          sx={{ mb: 1, bgcolor: 'background.paper' }}
        />
        <Button variant="contained" onClick={handleCommentSubmit} disabled={!comment.trim()}>
          Post Comment
        </Button>
      </Box>

      {post.comments && post.comments.map((comment) => (
        <Card key={comment.id} sx={{ mb: 2, bgcolor: '#f9f9f9' }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between">
                <Typography variant="subtitle2" fontWeight="bold">{comment.author}</Typography>
                <Typography variant="caption" color="text.secondary">{new Date(comment.created_at).toLocaleDateString()}</Typography>
            </Box>
            <Typography variant="body2" sx={{ mt: 1 }}>{comment.content}</Typography>
          </CardContent>
        </Card>
      ))}
    </Container>
  );
};

export default ForumPostDetail;
