import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/Layout';
import { POSScreen } from './features/billing/POSScreen';
import { ProductList } from './features/products/ProductList';
import { AccountingDashboard } from './features/accounting/AccountingDashboard';
import { Login } from './features/auth/Login';
import { MobileScannerPage } from './features/scanner/MobileScannerPage';
import { DeveloperPortal } from './features/developer/DeveloperPortal';
import { Toaster } from 'react-hot-toast';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, isLoading } = useAuth();
  if (isLoading) return <div className="p-8 text-center text-slate-400">Loading store...</div>;
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Toaster position="top-right" />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/developer" element={<DeveloperPortal />} />
          <Route path="/scanner" element={<MobileScannerPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<POSScreen />} />
            <Route path="products" element={<ProductList />} />
            <Route path="accounting" element={<AccountingDashboard />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
