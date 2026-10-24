import React, { lazy, Suspense } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";
import { Loading } from "./components/UI";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Login from "./pages/Login";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
const SiteCrawl = lazy(() => import("./pages/SiteCrawl"));
const AuditCompare = lazy(() => import("./pages/AuditCompare"));
const SnippetEditor = lazy(() => import("./pages/SnippetEditor"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Audits = lazy(() => import("./pages/Audits"));
const Keywords = lazy(() => import("./pages/Keywords"));
const Recommendations = lazy(() => import("./pages/Recommendations"));
const Agent = lazy(() => import("./pages/Agent"));

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <Loading />;
  if (!user)
    return (
      <Navigate
        to="/login"
        state={{ from: location.pathname + location.search }}
        replace
      />
    );
  return <Layout>{children}</Layout>;
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <a href="#main-content" className="skip-link">
          Skip to content
        </a>
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/audits"
              element={
                <PrivateRoute>
                  <Audits />
                </PrivateRoute>
              }
            />
            <Route
              path="/keywords"
              element={
                <PrivateRoute>
                  <Keywords />
                </PrivateRoute>
              }
            />
            <Route
              path="/recommendations"
              element={
                <PrivateRoute>
                  <Recommendations />
                </PrivateRoute>
              }
            />
            <Route
              path="/agent"
              element={
                <PrivateRoute>
                  <Agent />
                </PrivateRoute>
              }
            />
            <Route
              path="/site-crawl"
              element={
                <PrivateRoute>
                  <SiteCrawl />
                </PrivateRoute>
              }
            />
            <Route
              path="/compare"
              element={
                <PrivateRoute>
                  <AuditCompare />
                </PrivateRoute>
              }
            />
            <Route
              path="/snippet"
              element={
                <PrivateRoute>
                  <SnippetEditor />
                </PrivateRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
