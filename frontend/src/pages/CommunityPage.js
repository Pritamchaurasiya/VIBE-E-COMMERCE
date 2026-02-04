import React, { useState, useEffect } from "react";
import {
  Container,
  Grid,
  Card,
  CardHeader,
  CardContent,
  CardActions,
  Typography,
  Button,
  TextField,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
  Fab
} from "@mui/material";
import { Add, Comment, ThumbUp, Share } from "@mui/icons-material";
import { forumAPI } from "../services/api";
import { useAuth } from "../utils/AuthContext";

const CommunityPage = () => {
  const [posts, setPosts] = useState([]);
  const [openPostDialog, setOpenPostDialog] = useState(false);
  const [newPost, setNewPost] = useState({ title: "", content: "", tags: "" });
  const [expandedPost, setExpandedPost] = useState(null);
  const [newComment, setNewComment] = useState("");
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await forumAPI.getPosts();
      setPosts(response.data);
    } catch (error) {
      console.error("Error fetching posts:", error);
    }
  };

  const handleCreatePost = async () => {
    try {
      await forumAPI.createPost(newPost);
      setOpenPostDialog(false);
      setNewPost({ title: "", content: "", tags: "" });
      fetchPosts();
    } catch (error) {
      console.error("Error creating post:", error);
    }
  };

  const handleCommentSubmit = async (postId) => {
    if (!newComment.trim()) return;
    try {
      await forumAPI.addComment(postId, { content: newComment });
      setNewComment("");
      // Refresh post to see new comment (or update locally)
      fetchPosts();
    } catch (error) {
      console.error("Error adding comment:", error);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" fontWeight="bold">
          Farmer Community
        </Typography>
        {isAuthenticated && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpenPostDialog(true)}
          >
            Create Post
          </Button>
        )}
      </Box>

      <Grid container spacing={3}>
        {posts.map((post) => (
          <Grid item xs={12} key={post.id}>
            <Card>
              <CardHeader
                avatar={<Avatar>{post.user.charAt(0)}</Avatar>}
                title={post.title}
                subheader={`Posted by ${post.user} on ${new Date(post.created_at).toLocaleDateString()}`}
              />
              <CardContent>
                <Typography variant="body1">{post.content}</Typography>
                {post.tags && (
                  <Typography variant="caption" color="primary" sx={{ mt: 1, display: 'block' }}>
                    Tags: {post.tags}
                  </Typography>
                )}
              </CardContent>
              <CardActions disableSpacing>
                <IconButton aria-label="like">
                  <ThumbUp />
                </IconButton>
                <Typography variant="caption" sx={{ mr: 2 }}>{post.likes.length}</Typography>
                <IconButton aria-label="comment" onClick={() => setExpandedPost(expandedPost === post.id ? null : post.id)}>
                  <Comment />
                </IconButton>
                <Typography variant="caption">{post.comment_count}</Typography>
                <IconButton aria-label="share" sx={{ ml: 'auto' }}>
                  <Share />
                </IconButton>
              </CardActions>

              {expandedPost === post.id && (
                <Box sx={{ p: 2, bgcolor: 'action.hover' }}>
                  <List dense>
                    {post.comments && post.comments.map((comment) => (
                      <React.Fragment key={comment.id}>
                        <ListItem alignItems="flex-start">
                          <ListItemAvatar>
                            <Avatar sx={{ width: 24, height: 24, fontSize: '0.8rem' }}>
                              {comment.user.charAt(0)}
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={comment.user}
                            secondary={comment.content}
                          />
                        </ListItem>
                        <Divider variant="inset" component="li" />
                      </React.Fragment>
                    ))}
                  </List>
                  {isAuthenticated && (
                    <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                      <TextField
                        fullWidth
                        size="small"
                        placeholder="Write a comment..."
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                      />
                      <Button variant="contained" onClick={() => handleCommentSubmit(post.id)}>
                        Post
                      </Button>
                    </Box>
                  )}
                </Box>
              )}
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openPostDialog} onClose={() => setOpenPostDialog(false)} fullWidth maxWidth="sm">
        <DialogTitle>Create New Post</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Title"
              fullWidth
              value={newPost.title}
              onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
            />
            <TextField
              label="Content"
              multiline
              rows={4}
              fullWidth
              value={newPost.content}
              onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
            />
            <TextField
              label="Tags (comma separated)"
              fullWidth
              value={newPost.tags}
              onChange={(e) => setNewPost({ ...newPost, tags: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenPostDialog(false)}>Cancel</Button>
          <Button onClick={handleCreatePost} variant="contained">Post</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CommunityPage;
