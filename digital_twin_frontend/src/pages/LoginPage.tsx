import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  Leaf,
  LockKeyhole,
  Mail,
  Moon,
  Sun,
} from "lucide-react";

import {
  useAuth,
} from "../auth/AuthContext";

import {
  useLanguage,
} from "../i18n/LanguageContext";


export function LoginPage() {

  const {
    loginUser,
  } = useAuth();


  const {
    language,
    toggleLanguage,
    t,
  } = useLanguage();


  const [
    theme,
    setTheme,
  ] = useState<
    "light" | "dark"
  >(() => {

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

    return window.matchMedia(
      "(prefers-color-scheme: dark)"
    ).matches
      ? "dark"
      : "light";
  });


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


  const toggleTheme = () => {

    setTheme(
      (current) =>
        current === "dark"
          ? "light"
          : "dark"
    );
  };


  const navigate =
    useNavigate();


  const [
    email,
    setEmail,
  ] = useState(
    ""
  );


  const [
    password,
    setPassword,
  ] = useState(
    ""
  );


  const [
    error,
    setError,
  ] = useState("");


  const [
    loading,
    setLoading,
  ] = useState(false);


  const handleSubmit = async (
    event: React.FormEvent
  ) => {

    event.preventDefault();

    setError("");

    setLoading(true);


    try {

      await loginUser(
        email,
        password
      );


      navigate("/");

    } catch {

      setError(
        t("login.invalid")
      );

    } finally {

      setLoading(false);

    }
  };


  return (
    <div className="login-page">

      <div className="login-top-controls">

        <button
          type="button"
          className="login-theme-toggle"
          onClick={
            toggleTheme
          }
          title={
            theme === "dark"
              ? (
                language === "es"
                  ? "Cambiar a tema claro"
                  : "Switch to light theme"
              )
              : (
                language === "es"
                  ? "Cambiar a tema oscuro"
                  : "Switch to dark theme"
              )
          }
          aria-label={
            theme === "dark"
              ? "Light theme"
              : "Dark theme"
          }
        >
          {theme === "dark" ? (
            <Sun size={17} />
          ) : (
            <Moon size={17} />
          )}
        </button>


        <button
          type="button"
          className="login-language-toggle"
          onClick={
            toggleLanguage
          }
          title={
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

      </div>


      <div className="login-wrapper">

        {/* =========================================== */}
        {/* BRAND                                      */}
        {/* =========================================== */}

        <div className="login-brand">

          <div className="login-logo">
            <Leaf size={26} />
          </div>


          <h1>
            AgroTwin
          </h1>


          <p>
            {t("login.platform")}
          </p>

        </div>


        {/* =========================================== */}
        {/* CARD                                       */}
        {/* =========================================== */}

        <div className="login-card">

          <div className="login-card-header">

            <h2>
              {t("login.title")}
            </h2>

            <p>
              {t("login.subtitle")}
            </p>

          </div>


          <form
            className="login-form"
            onSubmit={handleSubmit}
          >

            <label>
              {t("login.email")}
            </label>


            <div className="input-wrapper">

              <Mail size={18} />

              <input
                value={email}
                onChange={(event) =>
                  setEmail(
                    event.target.value
                  )
                }
                type="email"
                placeholder={t("login.emailPlaceholder")}
              />

            </div>


            <label>
              {t("login.password")}
            </label>


            <div className="input-wrapper">

              <LockKeyhole size={18} />

              <input
                value={password}
                onChange={(event) =>
                  setPassword(
                    event.target.value
                  )
                }
                type="password"
                placeholder="••••••••"
              />

            </div>


            {error && (
              <div className="error">
                {error}
              </div>
            )}


            <button
              className="login-submit"
              type="submit"
              disabled={loading}
            >

              {loading
                ? t("login.loading")
                : t("login.submit")}

            </button>

          </form>

        </div>

      </div>

    </div>
  );
}