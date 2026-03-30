// Example Integration - How to use AIDashboard in your App
import React from 'react';
import './styles/AITheme.css'; // Import this first!
import AIDashboard from './pages/AIDashboard';

/**
 * Example 1: Simple Direct Integration (Recommended)
 */
function App() {
  return <AIDashboard />;
}

export default App;

/**
 * Example 2: With Custom Layout Wrapper
 */
function AppWithLayout() {
  return (
    <div className="min-h-screen bg-background">
      <AIDashboard />
    </div>
  );
}

/**
 * Example 3: With Authentication Check
 */
function AppWithAuth() {
  const [isAuthenticated, setIsAuthenticated] = React.useState(true);

  if (!isAuthenticated) {
    return <div className="min-h-screen flex items-center justify-center">Please login</div>;
  }

  return <AIDashboard />;
}

/**
 * Example 4: With Error Boundary
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Dashboard Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-background">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-on-background mb-4">Something went wrong</h1>
            <button
              onClick={() => this.setState({ hasError: false })}
              className="bg-primary text-white px-6 py-3 rounded-full font-headline font-bold"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return <AIDashboard />;
  }
}

function AppWithErrorBoundary() {
  return (
    <ErrorBoundary>
      <AIDashboard />
    </ErrorBoundary>
  );
}

/**
 * Example 5: Advanced Setup with Context API
 */
function AppWithContext() {
  const [user, setUser] = React.useState({
    name: 'Alex',
    email: 'alex@example.com',
    role: 'admin',
  });

  return (
    <UserContext.Provider value={{ user, setUser }}>
      <AIDashboard />
    </UserContext.Provider>
  );
}

const UserContext = React.createContext();

/**
 * Example 6: With Custom Theme Provider
 */
function AppWithThemeProvider() {
  const [theme, setTheme] = React.useState('light');

  return (
    <div className={theme === 'dark' ? 'dark' : 'light'}>
      <AIDashboard />
      {/* Theme switcher button */}
      <button
        onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
        className="fixed bottom-20 right-6 p-3 bg-primary rounded-full text-white"
      >
        {theme === 'light' ? '🌙' : '☀️'}
      </button>
    </div>
  );
}

/**
 * Example 7: Standalone Page Integration
 * If you want to integrate it as just one page in a larger app
 */
function AppWithNavigation() {
  const [currentPage, setCurrentPage] = React.useState('dashboard');

  return (
    <div className="min-h-screen">
      <nav className="bg-primary text-white p-4">
        <button
          className={`mr-6 px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-primary-fixed' : ''}`}
          onClick={() => setCurrentPage('dashboard')}
        >
          Dashboard
        </button>
        <button
          className={`mr-6 px-4 py-2 rounded ${currentPage === 'home' ? 'bg-primary-fixed' : ''}`}
          onClick={() => setCurrentPage('home')}
        >
          Home
        </button>
        <button
          className={`px-4 py-2 rounded ${currentPage === 'settings' ? 'bg-primary-fixed' : ''}`}
          onClick={() => setCurrentPage('settings')}
        >
          Settings
        </button>
      </nav>

      <main>
        {currentPage === 'dashboard' && <AIDashboard />}
        {currentPage === 'home' && <div className="p-8">Home Page</div>}
        {currentPage === 'settings' && <div className="p-8">Settings Page</div>}
      </main>
    </div>
  );
}

/**
 * Example 8: With Real-time Updates using WebSocket
 */
function AppWithRealTimeUpdates() {
  const [data, setData] = React.useState(null);
  const wsRef = React.useRef(null);

  React.useEffect(() => {
    // Connect to WebSocket
    wsRef.current = new WebSocket('wss://your-api.com/updates');

    wsRef.current.onmessage = (event) => {
      const update = JSON.parse(event.data);
      setData(update);
      // Update dashboard data based on WebSocket updates
      console.log('Real-time update:', update);
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return <AIDashboard />;
}

/**
 * Example 9: Production Ready Setup with All Features
 */
function AppProduction() {
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [user, setUser] = React.useState(null);

  React.useEffect(() => {
    // Fetch user data on mount
    const fetchUser = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('/api/user');
        const userData = await response.json();
        setUser(userData);
      } catch (err) {
        setError('Failed to load user data');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-error mb-4">{error}</h2>
          <button
            onClick={() => window.location.reload()}
            className="bg-primary text-white px-6 py-3 rounded-full"
          >
            Reload Page
          </button>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div>Please login to continue</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Optional Header */}
      <header className="bg-white/70 backdrop-blur-md border-b border-white/20 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="font-headline font-bold text-on-background">Welcome, {user.name}!</h1>
          <button onClick={() => setUser(null)} className="text-primary hover:underline">
            Logout
          </button>
        </div>
      </header>

      {/* Dashboard */}
      <div className="flex-1">
        <AIDashboard />
      </div>

      {/* Optional Footer */}
      <footer className="bg-white/70 backdrop-blur-md border-t border-white/20 p-4 text-center text-sm text-on-surface-variant">
        © 2024 AI Solutions. All rights reserved.
      </footer>
    </div>
  );
}

// Export the recommended version
// export default App;

// Or export any of the examples above based on your needs
// export default AppWithErrorBoundary;
// export default AppWithAuth;
// export default AppProduction;
