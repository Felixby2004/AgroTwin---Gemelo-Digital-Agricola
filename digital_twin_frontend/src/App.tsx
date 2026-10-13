import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import {
  AuthProvider,
} from "./auth/AuthContext";

import {
  LanguageProvider,
} from "./i18n/LanguageContext";

import {
  ProtectedRoute,
} from "./auth/ProtectedRoute";

import {
  Layout,
} from "./components/Layout";

import {
  AgriTwinAssistant,
} from "./components/chat/AgriTwinAssistant";

import {
  LoginPage,
} from "./pages/LoginPage";

import {
  DashboardPage,
} from "./pages/DashboardPage";

import {
  ParcelsPage,
} from "./pages/ParcelsPage";

import {
  ParcelDetailPage,
} from "./pages/ParcelDetailPage";

import {
  SensorsPage,
} from "./pages/SensorsPage";

import {
  GovernancePage,
} from "./pages/GovernancePage";

import {
  ReportsPage,
} from "./pages/ReportsPage";

import {
  GlossaryPage,
} from "./pages/GlossaryPage";

import {
  UsersPage,
} from "./pages/UsersPage";

import {
  ProfilePage,
} from "./pages/ProfilePage";


function App() {

  return (

    <BrowserRouter>

      <LanguageProvider>

        <AuthProvider>

          <Routes>

            <Route
              path="/login"
              element={
                <LoginPage />
              }
            />


            <Route
              element={
                <ProtectedRoute>
                  <>
                    <Layout />
                    <AgriTwinAssistant />
                  </>
                </ProtectedRoute>
              }
            >

              <Route
                path="/"
                element={
                  <DashboardPage />
                }
              />


              <Route
                path="/parcels"
                element={
                  <ParcelsPage />
                }
              />


              <Route
                path="/parcels/:parcelId"
                element={
                  <ParcelDetailPage />
                }
              />


              <Route
                path="/sensors"
                element={
                  <SensorsPage />
                }
              />


              <Route
                path="/governance"
                element={
                  <GovernancePage />
                }
              />


              <Route
                path="/reports"
                element={
                  <ReportsPage />
                }
              />


              <Route
                path="/glossary"
                element={
                  <GlossaryPage />
                }
              />


              <Route
                path="/profile"
                element={
                  <ProfilePage />
                }
              />


              <Route
                path="/users"
                element={
                  <UsersPage />
                }
              />

            </Route>

          </Routes>

        </AuthProvider>

      </LanguageProvider>

    </BrowserRouter>

  );
}


export default App;
