import {
  useEffect,
  useState,
} from "react";

import {
  AtSign,
  Building2,
  CalendarDays,
  Save,
  ShieldCheck,
  UserRound,
  BriefcaseBusiness,
} from "lucide-react";

import {
  getMyProfile,
  updateMyProfile,
} from "../api/users";

import {
  useAuth,
} from "../auth/AuthContext";

import {
  useLanguage,
} from "../i18n/LanguageContext";


export function ProfilePage() {

  const {
    updateCurrentUser,
  } = useAuth();

  const {
    language,
  } = useLanguage();

  const [
    fullName,
    setFullName,
  ] = useState("");

  const [
    email,
    setEmail,
  ] = useState("");

  const [
    role,
    setRole,
  ] = useState("");

  const [
    status,
    setStatus,
  ] = useState("");

  const [
    createdAt,
    setCreatedAt,
  ] = useState("");

  const [
    organization,
    setOrganization,
  ] = useState("");

  const [
    jobTitle,
    setJobTitle,
  ] = useState("");

  const [
    phone,
    setPhone,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    message,
    setMessage,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState("");


  useEffect(
    () => {

      const load =
        async () => {

          try {

            setLoading(true);

            const profile =
              await getMyProfile();

            setFullName(
              profile.full_name
            );

            setEmail(
              profile.email
            );

            setRole(
              profile.system_role
            );

            setStatus(
              profile.status
            );

            setCreatedAt(
              profile.created_at
            );

            setOrganization(
              String(
                profile.metadata
                  ?.organization
                ?? ""
              )
            );

            setJobTitle(
              String(
                profile.metadata
                  ?.job_title
                ?? ""
              )
            );

            setPhone(
              String(
                profile.metadata
                  ?.phone
                ?? ""
              )
            );

          } catch {

            setError(
              language === "es"
                ? "No se pudo cargar el perfil."
                : "Could not load profile."
            );

          } finally {

            setLoading(false);
          }
        };

      void load();

    },
    []
  );


  const save =
    async (
      event:
        React.FormEvent
    ) => {

      event.preventDefault();

      try {

        setSaving(true);
        setError("");
        setMessage("");

        const updated =
          await updateMyProfile({
            full_name:
              fullName,
            metadata: {
              organization,
              job_title:
                jobTitle,
              phone,
            },
          });

        updateCurrentUser(
          updated
        );

        setMessage(
          language === "es"
            ? "Perfil actualizado correctamente."
            : "Profile updated successfully."
        );

      } catch {

        setError(
          language === "es"
            ? "No se pudo actualizar el perfil."
            : "Could not update profile."
        );

      } finally {

        setSaving(false);
      }
    };


  if (loading) {
    return (
      <div className="loading-row">
        {language === "es"
          ? "Cargando perfil..."
          : "Loading profile..."}
      </div>
    );
  }


  return (
    <div className="profile-page">

      <section className="page-header">
        <div>
          <h1>
            {language === "es"
              ? "Mi perfil"
              : "My profile"}
          </h1>

          <p>
            {language === "es"
              ? "Información personal y contexto profesional asociado a tu cuenta."
              : "Personal information and professional context associated with your account."}
          </p>
        </div>
      </section>


      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {message && (
        <div className="profile-success">
          {message}
        </div>
      )}


      <section className="profile-grid">

        <article className="panel profile-identity-card">

          <div className="profile-large-avatar">
            <UserRound size={34} />
          </div>

          <h2>
            {fullName}
          </h2>

          <span>
            {email}
          </span>

          <div className="profile-role-badge">
            <ShieldCheck size={15} />
            {role}
          </div>

          <div className="profile-meta-list">

            <div>
              <AtSign size={16} />
              <span>Email</span>
              <strong>
                {email}
              </strong>
            </div>

            <div>
              <ShieldCheck size={16} />
              <span>
                {language === "es"
                  ? "Estado"
                  : "Status"}
              </span>
              <strong>
                {status}
              </strong>
            </div>

            <div>
              <CalendarDays size={16} />
              <span>
                {language === "es"
                  ? "Cuenta creada"
                  : "Account created"}
              </span>
              <strong>
                {createdAt
                  ? new Date(
                      createdAt
                    ).toLocaleDateString(
                      language === "es"
                        ? "es-PE"
                        : "en-US"
                    )
                  : "—"}
              </strong>
            </div>

          </div>

        </article>


        <form
          className="panel profile-form"
          onSubmit={
            save
          }
        >

          <div className="profile-form-header">
            <strong>
              {language === "es"
                ? "Información del perfil"
                : "Profile information"}
            </strong>

            <span>
              {language === "es"
                ? "Estos campos no cambian tus permisos."
                : "These fields do not change your permissions."}
            </span>
          </div>

          <label>
            {language === "es"
              ? "Nombre completo"
              : "Full name"}

            <input
              required
              value={fullName}
              onChange={(
                event
              ) =>
                setFullName(
                  event.target.value
                )
              }
            />
          </label>

          <label>
            Email

            <input
              disabled
              value={email}
            />
          </label>

          <label>
            <Building2 size={15} />
            {language === "es"
              ? "Organización"
              : "Organization"}

            <input
              value={organization}
              onChange={(
                event
              ) =>
                setOrganization(
                  event.target.value
                )
              }
              placeholder={
                language === "es"
                  ? "Universidad, empresa, asociación..."
                  : "University, company, association..."
              }
            />
          </label>

          <label>
            <BriefcaseBusiness size={15} />
            {language === "es"
              ? "Cargo o función"
              : "Position or role"}

            <input
              value={jobTitle}
              onChange={(
                event
              ) =>
                setJobTitle(
                  event.target.value
                )
              }
              placeholder={
                language === "es"
                  ? "Agricultor, investigador, agrónomo..."
                  : "Farmer, researcher, agronomist..."
              }
            />
          </label>

          <label>
            {language === "es"
              ? "Teléfono"
              : "Phone"}

            <input
              value={phone}
              onChange={(
                event
              ) =>
                setPhone(
                  event.target.value
                )
              }
            />
          </label>

          <div className="profile-form-actions">
            <button
              className="button-primary"
              type="submit"
              disabled={
                saving
              }
            >
              <Save size={16} />

              {saving
                ? (
                  language === "es"
                    ? "Guardando..."
                    : "Saving..."
                )
                : (
                  language === "es"
                    ? "Guardar perfil"
                    : "Save profile"
                )}
            </button>
          </div>

        </form>

      </section>

    </div>
  );
}
