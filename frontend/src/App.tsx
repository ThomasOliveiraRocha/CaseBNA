import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthContext, AuthProvider } from './AuthContext';
import Login from './Login';
import Register from './Register';
import Scraper from './Scraper';
import AdminPanel from './AdminPanel';


function RequireAuth({ children }: any) {
  const { user } = useContext(AuthContext);
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AppLayout() {
  const { user, logout } = useContext(AuthContext);

  return (
    <div>
      <nav style={{ padding: 10, borderBottom: '1px solid #ccc', marginBottom: 20 }}>
        {user ? (
          <>
            <span>Olá, {user.username}!</span> |{' '}
            <Link to="/">Analisar URL</Link> |{' '}
            {user.is_admin && <Link to="/admin">Painel Admin</Link>} |{' '}
            <button onClick={logout}>Sair</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link> | <Link to="/register">Registrar</Link>
          </>
        )}
      </nav>

      <Routes>
        <Route
          path="/"
          element={
            <RequireAuth>
              <Scraper />
            </RequireAuth>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/admin"
          element={
            <RequireAuth>
              {user?.is_admin ? <AdminPanel /> : <Navigate to="/" replace />}
            </RequireAuth>
          }
        />
        {/* Redireciona qualquer rota desconhecida para / */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <AppLayout />
      </Router>
    </AuthProvider>
  );
}
