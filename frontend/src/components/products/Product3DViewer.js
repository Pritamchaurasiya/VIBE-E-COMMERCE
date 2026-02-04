import React, { useRef, useState, useEffect, Suspense } from "react";
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment, useGLTF, Html } from '@react-three/drei';
import { Box, CircularProgress, IconButton, Tooltip, Typography } from '@mui/material';
import { ViewInAr, Fullscreen, FullscreenExit, CameraAlt, ZoomIn, ZoomOut } from '@mui/icons-material';
import * as THREE from 'three';

const ProductModel = ({ modelUrl, scale = 1, position = [0, 0, 0] }) => {
  const { scene } = useGLTF(modelUrl);
  const modelRef = useRef();

  // Auto-rotate the model
  useFrame(() => {
    if (modelRef.current) {
      modelRef.current.rotation.y += 0.005;
    }
  });

  return <primitive ref={modelRef} object={scene} scale={scale} position={position} />;
};

const Product3DViewer = ({
  modelUrl,
  productName,
  productImage,
  onArClick,
  onFullscreenToggle,
  isFullscreen,
  loading = false,
  error = null,
}) => {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const [cameraPosition, setCameraPosition] = useState([0, 0, 5]);
  const controlsRef = useRef();

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 0.2, 3));
    setCameraPosition(prev => [prev[0], prev[1], prev[2] - 1]);
  };

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev - 0.2, 0.5));
    setCameraPosition(prev => [prev[0], prev[1], prev[2] + 1]);
  };

  const handleResetView = () => {
    setZoomLevel(1);
    setCameraPosition([0, 0, 5]);
    if (controlsRef.current) {
      controlsRef.current.reset();
    }
  };

  const toggleControls = () => {
    setShowControls(!showControls);
  };

  if (loading) {
    return (
      <Box
        sx={{
          width: '100%',
          height: '500px',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
        }}
      >
        <CircularProgress size={60} />
        <Typography variant="body1" sx={{ mt: 2 }}>Loading 3D model...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        sx={{
          width: '100%',
          height: '500px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          p: 3,
        }}
      >
        <Typography variant="h6" color="error" gutterBottom>
          Error loading 3D model
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {error}
        </Typography>
        <Box
          component="img"
          src={productImage}
          alt={productName}
          sx={{
            maxWidth: '300px',
            maxHeight: '300px',
            objectFit: 'contain',
            borderRadius: '4px',
          }}
        />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        width: '100%',
        height: '500px',
        position: 'relative',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px',
        overflow: 'hidden',
      }}
    >
      {/* 3D Canvas */}
      <Canvas
        camera={{ position: cameraPosition, fov: 50 }}
        style={{ height: '100%', width: '100%' }}
      >
        <ambientLight intensity={0.5} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} />
        <pointLight position={[-10, -10, -10]} />

        <Suspense fallback={null}>
          {modelUrl ? (
            <ProductModel modelUrl={modelUrl} scale={zoomLevel} />
          ) : (
            <Html center>
              <Typography variant="body1">No 3D model available</Typography>
            </Html>
          )}
        </Suspense>

        <Environment preset="city" />

        <OrbitControls
          ref={controlsRef}
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minPolarAngle={0}
          maxPolarAngle={Math.PI}
        />
      </Canvas>

      {/* Controls Overlay */}
      {showControls && (
        <Box
          sx={{
            position: 'absolute',
            bottom: 16,
            left: 16,
            right: 16,
            display: 'flex',
            justifyContent: 'center',
            gap: 1,
            zIndex: 10,
          }}
        >
          <Tooltip title="AR View" arrow>
            <IconButton
              onClick={onArClick}
              sx={{ backgroundColor: 'rgba(255, 255, 255, 0.8)' }}
            >
              <ViewInAr />
            </IconButton>
          </Tooltip>

          <Tooltip title="Zoom In" arrow>
            <IconButton
              onClick={handleZoomIn}
              sx={{ backgroundColor: 'rgba(255, 255, 255, 0.8)' }}
            >
              <ZoomIn />
            </IconButton>
          </Tooltip>

          <Tooltip title="Zoom Out" arrow>
            <IconButton
              onClick={handleZoomOut}
              sx={{ backgroundColor: 'rgba(255, 255, 255, 0.8)' }}
            >
              <ZoomOut />
            </IconButton>
          </Tooltip>

          <Tooltip title="Reset View" arrow>
            <IconButton
              onClick={handleResetView}
              sx={{ backgroundColor: 'rgba(255, 255, 255, 0.8)' }}
            >
              <CameraAlt />
            </IconButton>
          </Tooltip>

          <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"} arrow>
            <IconButton
              onClick={onFullscreenToggle}
              sx={{ backgroundColor: 'rgba(255, 255, 255, 0.8)' }}
            >
              {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Tooltip>
        </Box>
      )}

      {/* Product Info Overlay */}
      <Box
        sx={{
          position: 'absolute',
          top: 16,
          left: 16,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          color: 'white',
          padding: '8px 16px',
          borderRadius: '20px',
          zIndex: 10,
        }}
      >
        <Typography variant="subtitle1">{productName}</Typography>
      </Box>
    </Box>
  );
};

export default Product3DViewer;