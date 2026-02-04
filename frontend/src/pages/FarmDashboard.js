import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import TopNav from '../components/layout/TopNav';
import { Card, CardContent, Typography, Switch, FormControlLabel, Box } from '@mui/material';
import api from '../services/api';

const FarmDashboard = () => {
  const [widgets, setWidgets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await api.get('/api/v1/dashboard/config/');
      // Map config to widget objects
      const configWidgets = response.data.widgets || ['weather', 'soil', 'market'];
      const allWidgets = [
        { id: 'weather', content: 'Weather Forecast', visible: configWidgets.includes('weather') },
        { id: 'soil', content: 'Soil Health', visible: configWidgets.includes('soil') },
        { id: 'market', content: 'Mandi Prices', visible: configWidgets.includes('market') },
        { id: 'news', content: 'Agri News', visible: configWidgets.includes('news') },
      ];
      setWidgets(allWidgets);
    } catch (error) {
      console.error("Failed to load dashboard config", error);
      // Fallback
      setWidgets([
        { id: 'weather', content: 'Weather Forecast', visible: true },
        { id: 'soil', content: 'Soil Health', visible: true },
        { id: 'market', content: 'Mandi Prices', visible: true },
        { id: 'news', content: 'Agri News', visible: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async (newWidgets) => {
    try {
      const visibleWidgets = newWidgets.filter(w => w.visible).map(w => w.id);
      await api.post('/api/v1/dashboard/config/', {
        configuration: { widgets: visibleWidgets }
      });
    } catch (error) {
      console.error("Failed to save config", error);
    }
  };

  const onDragEnd = (result) => {
    if (!result.destination) return;
    const items = Array.from(widgets);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    setWidgets(items);
    saveConfig(items);
  };

  const toggleWidget = (id) => {
    const newWidgets = widgets.map(w =>
      w.id === id ? { ...w, visible: !w.visible } : w
    );
    setWidgets(newWidgets);
    saveConfig(newWidgets);
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="agri-theme">
      <TopNav />
      <div style={{ padding: 20 }}>
        <Typography variant="h4" gutterBottom>My Farm Dashboard</Typography>

        <Box mb={2}>
          <Typography variant="h6">Customize Widgets:</Typography>
          {widgets.map(widget => (
            <FormControlLabel
              key={widget.id}
              control={<Switch checked={widget.visible} onChange={() => toggleWidget(widget.id)} />}
              label={widget.content}
            />
          ))}
        </Box>

        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="dashboard">
            {(provided) => (
              <div {...provided.droppableProps} ref={provided.innerRef}>
                {widgets.filter(w => w.visible).map((widget, index) => (
                  <Draggable key={widget.id} draggableId={widget.id} index={index}>
                    {(provided) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        style={{
                          userSelect: 'none',
                          padding: 16,
                          margin: '0 0 8px 0',
                          backgroundColor: 'white',
                          ...provided.draggableProps.style
                        }}
                      >
                        <Card elevation={2}>
                          <CardContent>
                            <Typography variant="h6">{widget.content}</Typography>
                            <Typography color="textSecondary">Widget content goes here...</Typography>
                          </CardContent>
                        </Card>
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      </div>
    </div>
  );
};

export default FarmDashboard;
