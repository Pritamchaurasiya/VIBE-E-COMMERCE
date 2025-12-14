import { useEffect, useRef } from 'react';

// Performance Monitoring Constants
export const PERFORMANCE_CONSTANTS = {
  MAX_LOAD_TIME: 3000, // 3 seconds
  MAX_TTI: 5000, // 5 seconds for Time to Interactive
  MAX_FCP: 2000, // 2 seconds for First Contentful Paint
  MAX_LCP: 2500, // 2.5 seconds for Largest Contentful Paint
  MAX_CLS: 0.1, // 0.1 for Cumulative Layout Shift
  PERFORMANCE_CHECK_INTERVAL: 10000, // 10 seconds
  MEMORY_WARNING_THRESHOLD: 0.8, // 80% of memory limit
  CPU_WARNING_THRESHOLD: 0.75 // 75% CPU usage
};

// Performance Monitor Hook
export const usePerformanceMonitor = (onPerformanceIssue) => {
  const performanceRef = useRef({
    metrics: {},
    issues: [],
    lastCheck: Date.now()
  });

  useEffect(() => {
    // Initialize performance monitoring
    if (window.performance) {
      const [performanceEntries] = window.performance.getEntriesByType('navigation');
      if (performanceEntries) {
        performanceRef.current.metrics.navigation = performanceEntries;
      }
    }

    // Set up performance observers
    const setupObservers = () => {
      try {
        // Largest Contentful Paint
        if ('LargestContentfulPaint' in window.performance) {
          const lcpObserver = new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            const lastEntry = entries[entries.length - 1];
            performanceRef.current.metrics.lcp = lastEntry.startTime;

            if (lastEntry.startTime > PERFORMANCE_CONSTANTS.MAX_LCP) {
              reportPerformanceIssue('LCP', lastEntry.startTime, PERFORMANCE_CONSTANTS.MAX_LCP);
            }
          });

          lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
        }

        // Cumulative Layout Shift
        if ('CumulativeLayoutShift' in window.performance) {
          const clsObserver = new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            const clsValue = entries.reduce((sum, entry) => sum + entry.value, 0);

            performanceRef.current.metrics.cls = clsValue;

            if (clsValue > PERFORMANCE_CONSTANTS.MAX_CLS) {
              reportPerformanceIssue('CLS', clsValue, PERFORMANCE_CONSTANTS.MAX_CLS);
            }
          });

          clsObserver.observe({ type: 'layout-shift', buffered: true });
        }

        // Long Tasks
        const longTaskObserver = new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          entries.forEach(entry => {
            if (entry.duration > 50) { // Long task is >50ms
              reportPerformanceIssue('LongTask', entry.duration, 50, {
                name: entry.name,
                startTime: entry.startTime
              });
            }
          });
        });

        longTaskObserver.observe({ type: 'longtask', buffered: true });

        // Memory monitoring (if available)
        if (window.performance && window.performance.memory) {
          const memoryCheck = setInterval(() => {
            const memory = window.performance.memory;
            const memoryUsage = memory.usedJSHeapSize / memory.jsHeapLimit;

            performanceRef.current.metrics.memoryUsage = memoryUsage;

            if (memoryUsage > PERFORMANCE_CONSTANTS.MEMORY_WARNING_THRESHOLD) {
              reportPerformanceIssue('Memory', memoryUsage, PERFORMANCE_CONSTANTS.MEMORY_WARNING_THRESHOLD, {
                usedHeapSize: memory.usedJSHeapSize,
                heapLimit: memory.jsHeapLimit
              });
            }
          }, PERFORMANCE_CONSTANTS.PERFORMANCE_CHECK_INTERVAL);

          return () => clearInterval(memoryCheck);
        }

      } catch (error) {
        console.error('Performance monitoring setup failed:', error);
      }
    };

    const reportPerformanceIssue = (type, actual, threshold, details = {}) => {
      const issue = {
        id: Date.now().toString(),
        type,
        actual,
        threshold,
        timestamp: new Date().toISOString(),
        details,
        severity: actual > threshold * 1.5 ? 'critical' : 'warning'
      };

      performanceRef.current.issues.push(issue);

      if (onPerformanceIssue) {
        onPerformanceIssue(issue);
      }

      // Log to console
      console.warn(`[Performance Issue] ${type}: ${actual} (threshold: ${threshold})`, details);
    };

    // Initial performance check
    const checkInitialPerformance = () => {
      if (window.performance && window.performance.timing) {
        const timing = window.performance.timing;

        // Calculate load time
        const loadTime = timing.loadEventEnd - timing.navigationStart;
        performanceRef.current.metrics.loadTime = loadTime;

        if (loadTime > PERFORMANCE_CONSTANTS.MAX_LOAD_TIME) {
          reportPerformanceIssue('LoadTime', loadTime, PERFORMANCE_CONSTANTS.MAX_LOAD_TIME);
        }

        // Calculate Time to Interactive
        const tti = timing.domInteractive - timing.navigationStart;
        performanceRef.current.metrics.tti = tti;

        if (tti > PERFORMANCE_CONSTANTS.MAX_TTI) {
          reportPerformanceIssue('TTI', tti, PERFORMANCE_CONSTANTS.MAX_TTI);
        }

        // Calculate First Contentful Paint (approximation)
        const fcp = timing.domContentLoadedEventStart - timing.navigationStart;
        performanceRef.current.metrics.fcp = fcp;

        if (fcp > PERFORMANCE_CONSTANTS.MAX_FCP) {
          reportPerformanceIssue('FCP', fcp, PERFORMANCE_CONSTANTS.MAX_FCP);
        }
      }
    };

    // Set up observers and initial check
    setupObservers();
    checkInitialPerformance();

    // Cleanup
    return () => {
      // Performance observers will be automatically disconnected when the component unmounts
    };
  }, [onPerformanceIssue]);

  return {
    metrics: performanceRef.current.metrics,
    issues: performanceRef.current.issues,
    getPerformanceReport: () => ({
      timestamp: new Date().toISOString(),
      metrics: performanceRef.current.metrics,
      issues: performanceRef.current.issues,
      userAgent: window.navigator.userAgent,
      url: window.location.href
    })
  };
};

// Performance Marker Utility
export const markPerformance = (name, detail = {}) => {
  if (window.performance) {
    window.performance.mark(`${name}_start`);

    return {
      end: () => {
        window.performance.mark(`${name}_end`);
        window.performance.measure(name, `${name}_start`, `${name}_end`);

        const measure = window.performance.getEntriesByName(name, 'measure')[0];
        if (measure) {
          console.log(`[Performance] ${name}: ${measure.duration.toFixed(2)}ms`, detail);
          return measure.duration;
        }
        return null;
      }
    };
  }

  return {
    end: () => null
  };
};

// Resource Loading Monitor
export const monitorResourceLoading = (onResourceLoaded) => {
  useEffect(() => {
    if (!window.performance || !window.performance.getEntriesByType) return;

    const checkResources = () => {
      const resources = window.performance.getEntriesByType('resource');

      resources.forEach(resource => {
        if (resource.initiatorType === 'script' || resource.initiatorType === 'link') {
          onResourceLoaded({
            name: resource.name,
            type: resource.initiatorType,
            duration: resource.duration,
            size: resource.transferSize,
            startTime: resource.startTime,
            responseEnd: resource.responseEnd
          });
        }
      });
    };

    // Check immediately and then set up interval
    checkResources();
    const interval = setInterval(checkResources, PERFORMANCE_CONSTANTS.PERFORMANCE_CHECK_INTERVAL);

    return () => clearInterval(interval);
  }, [onResourceLoaded]);
};

// Network Performance Monitor
export const useNetworkMonitor = (onNetworkChange) => {
  useEffect(() => {
    let connection = null;

    const updateConnection = () => {
      if ('connection' in navigator) {
        connection = navigator.connection;

        const networkInfo = {
          effectiveType: connection.effectiveType,
          downlink: connection.downlink,
          rtt: connection.rtt,
          saveData: connection.saveData,
          type: connection.type
        };

        if (onNetworkChange) {
          onNetworkChange(networkInfo);
        }

        console.log('[Network Monitor] Connection info:', networkInfo);
      }
    };

    // Initial check
    updateConnection();

    // Set up event listeners if available
    if ('connection' in navigator) {
      navigator.connection.addEventListener('change', updateConnection);
    }

    return () => {
      if ('connection' in navigator) {
        navigator.connection.removeEventListener('change', updateConnection);
      }
    };
  }, [onNetworkChange]);
};

// Error Tracking Utility
export const trackError = (error, context = {}) => {
  const errorData = {
    id: Date.now().toString(),
    timestamp: new Date().toISOString(),
    message: error.message || String(error),
    stack: error.stack,
    context,
    userAgent: window.navigator.userAgent,
    url: window.location.href,
    severity: 'error'
  };

  console.error('[Error Tracker]', errorData);

  // In a real app, you would send this to your error tracking service
  // For example: Sentry.captureException(error, { extra: context });

  return errorData;
};

// Performance Budget Checker
export const checkPerformanceBudget = (metrics) => {
  const budgetResults = {
    passed: true,
    issues: []
  };

  const checks = [
    {
      name: 'Load Time',
      metric: 'loadTime',
      actual: metrics.loadTime,
      budget: PERFORMANCE_CONSTANTS.MAX_LOAD_TIME
    },
    {
      name: 'Time to Interactive',
      metric: 'tti',
      actual: metrics.tti,
      budget: PERFORMANCE_CONSTANTS.MAX_TTI
    },
    {
      name: 'First Contentful Paint',
      metric: 'fcp',
      actual: metrics.fcp,
      budget: PERFORMANCE_CONSTANTS.MAX_FCP
    },
    {
      name: 'Largest Contentful Paint',
      metric: 'lcp',
      actual: metrics.lcp,
      budget: PERFORMANCE_CONSTANTS.MAX_LCP
    },
    {
      name: 'Cumulative Layout Shift',
      metric: 'cls',
      actual: metrics.cls,
      budget: PERFORMANCE_CONSTANTS.MAX_CLS
    }
  ];

  checks.forEach(check => {
    if (check.actual && check.actual > check.budget) {
      budgetResults.passed = false;
      budgetResults.issues.push({
        name: check.name,
        metric: check.metric,
        actual: check.actual,
        budget: check.budget,
        overBudget: check.actual - check.budget,
        percentageOver: ((check.actual - check.budget) / check.budget * 100).toFixed(2) + '%'
      });
    }
  });

  return budgetResults;
};

// Web Vitals Monitoring
export const monitorWebVitals = (onVitalsUpdate) => {
  useEffect(() => {
    if (!('getEntriesByType' in window.performance)) return;

    const reportWebVitals = () => {
      const vitals = {
        fcp: null,
        lcp: null,
        cls: null,
        fid: null,
        tbt: null
      };

      // First Contentful Paint
      const fcpEntries = window.performance.getEntriesByType('paint');
      const fcp = fcpEntries.find(entry => entry.name === 'first-contentful-paint');
      if (fcp) {
        vitals.fcp = fcp.startTime;
      }

      // Largest Contentful Paint
      const lcpEntries = window.performance.getEntriesByType('largest-contentful-paint');
      if (lcpEntries.length > 0) {
        vitals.lcp = lcpEntries[lcpEntries.length - 1].startTime;
      }

      // Cumulative Layout Shift
      const clsEntries = window.performance.getEntriesByType('layout-shift');
      if (clsEntries.length > 0) {
        vitals.cls = clsEntries.reduce((sum, entry) => sum + entry.value, 0);
      }

      // First Input Delay (requires user interaction)
      // This would typically be measured with a separate observer

      // Total Blocking Time
      const longTasks = window.performance.getEntriesByType('longtask');
      if (longTasks.length > 0) {
        vitals.tbt = longTasks.reduce((sum, task) => {
          return sum + (task.duration > 50 ? task.duration - 50 : 0);
        }, 0);
      }

      if (onVitalsUpdate) {
        onVitalsUpdate(vitals);
      }

      console.log('[Web Vitals]', vitals);
    };

    // Initial report
    reportWebVitals();

    // Set up observers for continuous monitoring
    const setupVitalsObservers = () => {
      try {
        // LCP Observer
        new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          const lastEntry = entries[entries.length - 1];
          if (onVitalsUpdate) {
            onVitalsUpdate({ lcp: lastEntry.startTime });
          }
        }).observe({ type: 'largest-contentful-paint', buffered: true });

        // CLS Observer
        new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          const clsValue = entries.reduce((sum, entry) => sum + entry.value, 0);
          if (onVitalsUpdate) {
            onVitalsUpdate({ cls: clsValue });
          }
        }).observe({ type: 'layout-shift', buffered: true });

        // Long Tasks Observer (for TBT)
        new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          const tbt = entries.reduce((sum, task) => {
            return sum + (task.duration > 50 ? task.duration - 50 : 0);
          }, 0);

          if (onVitalsUpdate) {
            onVitalsUpdate({ tbt });
          }
        }).observe({ type: 'longtask', buffered: true });

      } catch (error) {
        console.error('Failed to set up vitals observers:', error);
      }
    };

    setupVitalsObservers();

    // Periodic check
    const interval = setInterval(reportWebVitals, PERFORMANCE_CONSTANTS.PERFORMANCE_CHECK_INTERVAL);

    return () => clearInterval(interval);
  }, [onVitalsUpdate]);
};

// Export all performance utilities
export default {
  PERFORMANCE_CONSTANTS,
  usePerformanceMonitor,
  markPerformance,
  monitorResourceLoading,
  useNetworkMonitor,
  trackError,
  checkPerformanceBudget,
  monitorWebVitals
};