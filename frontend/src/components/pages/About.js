import React from "react";
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Avatar,
  Button,
  Paper,
  Divider,
  Chip,
  Rating,
} from "@mui/material";
import {
  Agriculture,
  LocalShipping,
  VerifiedUser,
  EmojiEmotions,
  TrendingUp,
  People,
  StarBorder,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import ScrollAnimation from "../common/ScrollAnimation";

const About = () => {
  const stats = [
    { icon: <People />, value: "50,000+", label: "Happy Customers" },
    { icon: <Agriculture />, value: "5,000+", label: "Products" },
    { icon: <LocalShipping />, value: "100+", label: "Vendors" },
    { icon: <StarBorder />, value: "4.8", label: "Average Rating" },
  ];

  const values = [
    {
      icon: <VerifiedUser sx={{ fontSize: 40 }} />,
      title: "Quality Assurance",
      description:
        "We ensure every product meets our high-quality standards before reaching you.",
    },
    {
      icon: <Agriculture sx={{ fontSize: 40 }} />,
      title: "Sustainable Sourcing",
      description:
        "Supporting local farmers and vendors with sustainable and ethical practices.",
    },
    {
      icon: <EmojiEmotions sx={{ fontSize: 40 }} />,
      title: "Customer First",
      description:
        "Your satisfaction is our priority. We go above and beyond for our customers.",
    },
    {
      icon: <TrendingUp sx={{ fontSize: 40 }} />,
      title: "Innovation",
      description:
        "Constantly improving our platform with cutting-edge technology.",
    },
  ];

  const team = [
    { name: "Raj Kumar", role: "CEO & Founder", avatar: "R" },
    { name: "Priya Sharma", role: "CTO", avatar: "P" },
    { name: "Amit Patel", role: "Head of Operations", avatar: "A" },
    { name: "Sneha Gupta", role: "Marketing Director", avatar: "S" },
  ];

  const testimonials = [
    {
      name: "Mohan Singh",
      role: "Farmer, Punjab",
      content:
        "VIBE has transformed how I sell my produce. The platform is easy to use and I reach customers I never could before.",
      rating: 5,
    },
    {
      name: "Lakshmi Devi",
      role: "Retailer, Karnataka",
      content:
        "Excellent product quality and fast delivery. My customers love the products I source from VIBE.",
      rating: 5,
    },
    {
      name: "Arjun Reddy",
      role: "Organic Store Owner",
      content:
        "The variety of organic products is amazing. Our partnership has been incredibly beneficial.",
      rating: 4,
    },
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background:
            "linear-gradient(135deg, #22c55e 0%, #16a34a 50%, #15803d 100%)",
          color: "white",
          py: { xs: 8, md: 12 },
          position: "relative",
          overflow: "hidden",
        }}
      >
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <Typography
              variant="h2"
              component="h1"
              fontWeight="bold"
              gutterBottom
              textAlign="center"
            >
              About VIBE E-Commerce
            </Typography>
            <Typography
              variant="h5"
              textAlign="center"
              sx={{ opacity: 0.9, maxWidth: 800, mx: "auto" }}
            >
              Connecting farmers, vendors, and customers through a sustainable
              and innovative marketplace.
            </Typography>
          </motion.div>
        </Container>

        {/* Decorative elements */}
        <Box
          sx={{
            position: "absolute",
            top: -100,
            right: -100,
            width: 300,
            height: 300,
            borderRadius: "50%",
            background: "rgba(255,255,255,0.1)",
          }}
        />
      </Box>

      {/* Stats Section */}
      <Container maxWidth="lg" sx={{ mt: -6, position: "relative", zIndex: 1 }}>
        <Grid container spacing={3}>
          {stats.map((stat, index) => (
            <Grid item xs={6} md={3} key={stat.label}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Paper
                  elevation={4}
                  sx={{
                    p: 3,
                    textAlign: "center",
                    borderRadius: 3,
                    transition: "transform 0.3s ease",
                    "&:hover": {
                      transform: "translateY(-5px)",
                    },
                  }}
                >
                  <Box sx={{ color: "primary.main", mb: 1 }}>{stat.icon}</Box>
                  <Typography variant="h4" fontWeight="bold" color="primary">
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.label}
                  </Typography>
                </Paper>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Our Story */}
      <Container maxWidth="lg" sx={{ py: 10 }}>
        <ScrollAnimation animation="fadeUp">
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h3" fontWeight="bold" gutterBottom>
                Our Story
              </Typography>
              <Typography variant="body1" paragraph color="text.secondary">
                Founded in 2020, VIBE E-Commerce was born from a simple idea: to
                create a transparent marketplace that benefits both producers
                and consumers.
              </Typography>
              <Typography variant="body1" paragraph color="text.secondary">
                We started with a small team of passionate individuals who
                believed in the power of technology to transform agricultural
                commerce. Today, we connect thousands of farmers and vendors
                with customers across the country.
              </Typography>
              <Typography variant="body1" paragraph color="text.secondary">
                Our mission is to make quality products accessible while
                ensuring fair prices for everyone involved in the supply chain.
              </Typography>
              <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", mt: 3 }}>
                <Chip label="Est. 2020" color="primary" variant="outlined" />
                <Chip
                  label="100% Indian"
                  color="secondary"
                  variant="outlined"
                />
                <Chip
                  label="Farmer Friendly"
                  color="success"
                  variant="outlined"
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                sx={{
                  background:
                    "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)",
                  borderRadius: 4,
                  p: 4,
                  height: 400,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Agriculture
                  sx={{ fontSize: 200, color: "primary.main", opacity: 0.3 }}
                />
              </Box>
            </Grid>
          </Grid>
        </ScrollAnimation>
      </Container>

      {/* Our Values */}
      <Box sx={{ bgcolor: "grey.50", py: 10 }}>
        <Container maxWidth="lg">
          <ScrollAnimation animation="fadeUp">
            <Typography
              variant="h3"
              fontWeight="bold"
              textAlign="center"
              gutterBottom
            >
              Our Values
            </Typography>
            <Typography
              variant="body1"
              color="text.secondary"
              textAlign="center"
              sx={{ mb: 6 }}
            >
              The principles that guide everything we do
            </Typography>
          </ScrollAnimation>

          <Grid container spacing={4}>
            {values.map((value, index) => (
              <Grid item xs={12} sm={6} md={3} key={value.title}>
                <ScrollAnimation animation="fadeUp" delay={index * 0.1}>
                  <Card
                    sx={{
                      height: "100%",
                      textAlign: "center",
                      p: 3,
                      borderRadius: 3,
                      transition: "all 0.3s ease",
                      "&:hover": {
                        transform: "translateY(-8px)",
                        boxShadow: 6,
                      },
                    }}
                  >
                    <Box sx={{ color: "primary.main", mb: 2 }}>
                      {value.icon}
                    </Box>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      {value.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {value.description}
                    </Typography>
                  </Card>
                </ScrollAnimation>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Team Section */}
      <Container maxWidth="lg" sx={{ py: 10 }}>
        <ScrollAnimation animation="fadeUp">
          <Typography
            variant="h3"
            fontWeight="bold"
            textAlign="center"
            gutterBottom
          >
            Meet Our Team
          </Typography>
          <Typography
            variant="body1"
            color="text.secondary"
            textAlign="center"
            sx={{ mb: 6 }}
          >
            The passionate people behind VIBE
          </Typography>
        </ScrollAnimation>

        <Grid container spacing={4} justifyContent="center">
          {team.map((member, index) => (
            <Grid item xs={6} sm={3} key={member.name}>
              <ScrollAnimation animation="fadeUp" delay={index * 0.1}>
                <Box sx={{ textAlign: "center" }}>
                  <Avatar
                    sx={{
                      width: 120,
                      height: 120,
                      mx: "auto",
                      mb: 2,
                      bgcolor: "primary.main",
                      fontSize: "2.5rem",
                      fontWeight: "bold",
                    }}
                  >
                    {member.avatar}
                  </Avatar>
                  <Typography variant="h6" fontWeight="bold">
                    {member.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {member.role}
                  </Typography>
                </Box>
              </ScrollAnimation>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Testimonials */}
      <Box sx={{ bgcolor: "primary.main", color: "white", py: 10 }}>
        <Container maxWidth="lg">
          <Typography
            variant="h3"
            fontWeight="bold"
            textAlign="center"
            gutterBottom
          >
            What People Say
          </Typography>
          <Typography
            variant="body1"
            textAlign="center"
            sx={{ mb: 6, opacity: 0.9 }}
          >
            Hear from our community
          </Typography>

          <Grid container spacing={4}>
            {testimonials.map((testimonial, index) => (
              <Grid item xs={12} md={4} key={testimonial.name}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Card sx={{ height: "100%", borderRadius: 3 }}>
                    <CardContent sx={{ p: 3 }}>
                      <Rating
                        value={testimonial.rating}
                        readOnly
                        sx={{ mb: 2 }}
                      />
                      <Typography
                        variant="body1"
                        paragraph
                        sx={{ fontStyle: "italic" }}
                      >
                        "{testimonial.content}"
                      </Typography>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="subtitle2" fontWeight="bold">
                        {testimonial.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {testimonial.role}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Container maxWidth="md" sx={{ py: 10, textAlign: "center" }}>
        <ScrollAnimation animation="fadeUp">
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            Join Our Journey
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Whether you're a farmer, vendor, or customer, there's a place for
            you at VIBE.
          </Typography>
          <Box
            sx={{
              display: "flex",
              gap: 2,
              justifyContent: "center",
              flexWrap: "wrap",
            }}
          >
            <Button variant="contained" size="large" sx={{ px: 4 }}>
              Start Shopping
            </Button>
            <Button variant="outlined" size="large" sx={{ px: 4 }}>
              Become a Vendor
            </Button>
          </Box>
        </ScrollAnimation>
      </Container>
    </Box>
  );
};

export default About;
