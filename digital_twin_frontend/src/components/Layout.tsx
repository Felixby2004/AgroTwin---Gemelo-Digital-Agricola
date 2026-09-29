import {
  useEffect,
  useState,
} from "react";

import {
  NavLink,
  Outlet,
} from "react-router-dom";

import {
  LayoutDashboard,
  Map,
  ShieldCheck,
  FileText,
  LogOut,
  Leaf,
  PanelLeftClose,
  PanelLeftOpen,
  Wifi,
  BookOpenText,
  Moon,
  Sun,
  Users,
  Settings2,
} from "lucide-react";

import { useAuth } from "../auth/AuthContext";

import { useLanguage } from "../i18n/LanguageContext";


type ThemeMode =
  | "light"
  | "dark";


function getInitialTheme():
ThemeMode {

  const stored =
    localStorage.getItem(
      "agrotwin_theme"
    );


  if (
    stored === "light"
    ||
    stored === "dark"
  ) {
    return stored;
  }


  return window
    .matchMedia(
      "(prefers-color-scheme: dark)"
    )
    .matches
      ? "dark"
      : "light";
}


export function Layout() {

  const {
    user,
    logout,
  } = useAuth();


  const {
    language,
    toggleLanguage,
    t,
    roleLabel,
  } = useLanguage();


  const [
    sidebarCollapsed,
    setSidebarCollapsed,
  ] = useState(false);


  const [
    theme,
    setTheme,
  ] = useState<ThemeMode>(
    getInitialTheme
  );


  useEffect(
    () => {

      document
        .documentElement
        .setAttribute(
          "data-theme",
          theme
        );


      localStorage.setItem(
        "agrotwin_theme",
        theme
      );

    },
    [
      theme,
    ]
  );


  const toggleTheme =
    () => {

      setTheme(
        (
          current
        ) =>
          current === "light"
            ? "dark"
            : "light"
      );
    };


  const toggleSidebar = () => {

    setSidebarCollapsed(
      (current) => !current
    );
  };


  return (
    <div
      className={
        sidebarCollapsed
          ? "app-shell sidebar-collapsed"
          : "app-shell"
      }
    >

      {/* ============================================= */}
      {/* SIDEBAR                                      */}
      {/* ============================================= */}

      <aside className="sidebar">

        <div className="sidebar-top">

          <div className="brand">

            <div className="brand-icon">
              <Leaf size={22} />
            </div>


            <div className="brand-text">

              <div className="brand-title">
                AgroTwin
              </div>

              <div className="brand-subtitle">
                {t("brand.subtitle")}
              </div>

            </div>

          </div>


          <div className="sidebar-section-label">
            {t("sidebar.digitalTwins")}
          </div>


          <nav className="sidebar-nav">

            <NavLink
              to="/"
              end
              title={t("sidebar.dashboard")}
            >
              <LayoutDashboard size={19} />

              <span>
                {t("sidebar.dashboard")}
              </span>
            </NavLink>


            <NavLink
              to="/parcels"
              title={t("sidebar.parcels")}
            >
              <Map size={19} />

              <span>
                {t("sidebar.parcels")}
              </span>
            </NavLink>


            <NavLink
              to="/sensors"
              title={t("sidebar.sensors")}
            >
              <Wifi size={19} />

              <span>
                {t("sidebar.sensors")}
              </span>
            </NavLink>


            <NavLink
              to="/glossary"
              title={t("sidebar.glossary")}
            >
              <BookOpenText size={19} />

              <span>
                {t("sidebar.glossary")}
              </span>
            </NavLink>


            <NavLink
              to="/profile"
              title={
                language === "es"
                  ? "Mi perfil"
                  : "My profile"
              }
            >
              <Settings2 size={19} />

              <span>
                {language === "es"
                  ? "Mi perfil"
                  : "My profile"}
              </span>
            </NavLink>


            {user?.system_role === "ADMIN" && (

              <NavLink
                to="/users"
                title={
                  language === "es"
                    ? "Usuarios y roles"
                    : "Users and roles"
                }
              >
                <Users size={19} />

                <span>
                  {language === "es"
                    ? "Usuarios y roles"
                    : "Users and roles"}
                </span>
              </NavLink>

            )}


            <div className="sidebar-section-label secondary">
              {t("sidebar.dataSovereignty")}
            </div>


            <NavLink
              to="/governance"
              title={t("sidebar.governance")}
            >
              <ShieldCheck size={19} />

              <span>
                {t("sidebar.governance")}
              </span>
            </NavLink>


            <div className="sidebar-section-label secondary">
              {t("sidebar.reportsSection")}
            </div>


            <NavLink
              to="/reports"
              title={t("sidebar.reports")}
            >
              <FileText size={19} />

              <span>
                {t("sidebar.reports")}
              </span>
            </NavLink>

          </nav>

        </div>


        <div className="sidebar-bottom">

          <button
            className="logout-button"
            onClick={logout}
            title={t("sidebar.logout")}
          >
            <LogOut size={18} />

            <span>
              {t("sidebar.logout")}
            </span>
          </button>

        </div>

      </aside>


      {/* ============================================= */}
      {/* RIGHT SIDE                                   */}
      {/* ============================================= */}

      <div className="app-right">

        {/* =========================================== */}
        {/* TOPBAR                                     */}
        {/* =========================================== */}

        <header className="topbar">

          <div className="topbar-left">

            <button
              className="sidebar-toggle-button"
              type="button"
              onClick={toggleSidebar}
              title={
                sidebarCollapsed
                  ? t("topbar.expand")
                  : t("topbar.collapse")
              }
            >

              {sidebarCollapsed ? (
                <PanelLeftOpen size={20} />
              ) : (
                <PanelLeftClose size={20} />
              )}

            </button>


            <div className="topbar-title-group">

              <strong>
                {t("topbar.title")}
              </strong>

              <span>
                {t("topbar.subtitle")}
              </span>

            </div>

          </div>


          <div className="topbar-right">

            <button
              className="language-toggle-button"
              type="button"
              onClick={
                toggleLanguage
              }
              title={
                language === "es"
                  ? t("language.english")
                  : t("language.spanish")
              }
              aria-label={
                language === "es"
                  ? t("language.english")
                  : t("language.spanish")
              }
            >

              <span
                className={
                  language === "es"
                    ? "active"
                    : ""
                }
              >
                ES
              </span>

              <span
                className={
                  language === "en"
                    ? "active"
                    : ""
                }
              >
                EN
              </span>

            </button>


            <button
              className="theme-toggle-button"
              type="button"
              onClick={
                toggleTheme
              }
              title={
                theme === "light"
                  ? t("theme.dark")
                  : t("theme.light")
              }
              aria-label={
                theme === "light"
                  ? t("theme.dark")
                  : t("theme.light")
              }
            >

              {theme === "light" ? (
                <Moon size={18} />
              ) : (
                <Sun size={18} />
              )}

            </button>

            <div className="topbar-user">

              <div className="topbar-user-text">

                <strong>
                  {user?.full_name}
                </strong>

                <span>
                  {roleLabel(user?.system_role)}
                </span>

              </div>


              <div className="topbar-avatar">

                {user?.full_name
                  ?.charAt(0)
                  ?.toUpperCase() || "U"}

              </div>

            </div>

          </div>

        </header>


        {/* =========================================== */}
        {/* PAGE CONTENT                                */}
        {/* =========================================== */}

        <main className="main-content">
          <Outlet />
        </main>

      </div>

    </div>
  );
}