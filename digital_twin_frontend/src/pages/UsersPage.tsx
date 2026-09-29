import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Search,
  ShieldCheck,
  UserPlus,
  Users,
  UserRound,
  X,
} from "lucide-react";

import {
  createUser,
  getUsers,
  updateUser,
} from "../api/users";

import type {
  User,
} from "../api/auth";

import {
  useAuth,
} from "../auth/AuthContext";

import {
  useLanguage,
} from "../i18n/LanguageContext";


export function UsersPage() {

  const {
    user: currentUser,
  } = useAuth();

  const {
    language,
  } = useLanguage();

  const [
    users,
    setUsers,
  ] = useState<User[]>([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");

  const [
    search,
    setSearch,
  ] = useState("");

  const [
    roleFilter,
    setRoleFilter,
  ] = useState("");

  const [
    showCreate,
    setShowCreate,
  ] = useState(false);

  const [
    fullName,
    setFullName,
  ] = useState("");

  const [
    email,
    setEmail,
  ] = useState("");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    role,
    setRole,
  ] = useState<
    "ADMIN"
    | "USER"
  >("USER");

  const [
    saving,
    setSaving,
  ] = useState(false);


  const loadUsers =
    async () => {

      try {

        setLoading(true);
        setError("");

        setUsers(
          await getUsers()
        );

      } catch {

        setError(
          language === "es"
            ? "No se pudieron cargar los usuarios."
            : "Could not load users."
        );

      } finally {

        setLoading(false);
      }
    };


  useEffect(
    () => {
      void loadUsers();
    },
    []
  );


  const filtered =
    useMemo(
      () =>
        users.filter(
          (
            item
          ) => {

            const query =
              search
                .trim()
                .toLowerCase();

            const matchesSearch =
              !query
              ||
              item.full_name
                .toLowerCase()
                .includes(
                  query
                )
              ||
              item.email
                .toLowerCase()
                .includes(
                  query
                );

            const matchesRole =
              !roleFilter
              ||
              item.system_role
              === roleFilter;

            return (
              matchesSearch
              &&
              matchesRole
            );
          }
        ),
      [
        users,
        search,
        roleFilter,
      ]
    );


  const submitCreate =
    async (
      event:
        React.FormEvent
    ) => {

      event.preventDefault();

      try {

        setSaving(true);
        setError("");

        await createUser({
          email,
          full_name:
            fullName,
          password,
          system_role:
            role,
          metadata: {},
        });

        setShowCreate(
          false
        );

        setFullName("");
        setEmail("");
        setPassword("");
        setRole("USER");

        await loadUsers();

      } catch {

        setError(
          language === "es"
            ? "No se pudo crear el usuario."
            : "Could not create user."
        );

      } finally {

        setSaving(false);
      }
    };


  const changeUser =
    async (
      item: User,
      changes: {
        system_role?:
          | "ADMIN"
          | "USER";
        status?:
          | "ACTIVE"
          | "DISABLED";
      }
    ) => {

      try {

        setError("");

        await updateUser(
          item.user_id,
          changes
        );

        await loadUsers();

      } catch {

        setError(
          language === "es"
            ? "No se pudo actualizar el usuario."
            : "Could not update user."
        );
      }
    };


  if (
    currentUser
      ?.system_role
    !== "ADMIN"
  ) {

    return (
      <div className="users-forbidden panel">
        <ShieldCheck size={28} />

        <strong>
          {language === "es"
            ? "Acceso administrativo"
            : "Administrative access"}
        </strong>

        <span>
          {language === "es"
            ? "Esta sección está disponible solo para administradores."
            : "This section is available to administrators only."}
        </span>
      </div>
    );
  }


  return (
    <div className="users-page">

      <section className="page-header">

        <div>
          <h1>
            {language === "es"
              ? "Usuarios y roles"
              : "Users and roles"}
          </h1>

          <p>
            {language === "es"
              ? "Administra cuentas, roles del sistema y estado de acceso."
              : "Manage accounts, system roles and access status."}
          </p>
        </div>

        <button
          className="button-primary"
          type="button"
          onClick={() =>
            setShowCreate(
              true
            )
          }
        >
          <UserPlus size={17} />

          {language === "es"
            ? "Nuevo usuario"
            : "New user"}
        </button>

      </section>


      {error && (
        <div className="error">
          {error}
        </div>
      )}


      <section className="users-summary-grid">

        <article className="users-summary-card">
          <Users size={20} />
          <div>
            <span>
              {language === "es"
                ? "Usuarios"
                : "Users"}
            </span>
            <strong>
              {users.length}
            </strong>
          </div>
        </article>

        <article className="users-summary-card">
          <ShieldCheck size={20} />
          <div>
            <span>
              {language === "es"
                ? "Administradores"
                : "Administrators"}
            </span>
            <strong>
              {
                users.filter(
                  (item) =>
                    item.system_role
                    === "ADMIN"
                ).length
              }
            </strong>
          </div>
        </article>

        <article className="users-summary-card">
          <UserRound size={20} />
          <div>
            <span>
              {language === "es"
                ? "Activos"
                : "Active"}
            </span>
            <strong>
              {
                users.filter(
                  (item) =>
                    item.status
                    === "ACTIVE"
                ).length
              }
            </strong>
          </div>
        </article>

      </section>


      <section className="panel users-toolbar">

        <div className="users-search">
          <Search size={17} />

          <input
            value={search}
            onChange={(
              event
            ) =>
              setSearch(
                event.target.value
              )
            }
            placeholder={
              language === "es"
                ? "Buscar por nombre o correo..."
                : "Search by name or email..."
            }
          />
        </div>

        <select
          value={roleFilter}
          onChange={(
            event
          ) =>
            setRoleFilter(
              event.target.value
            )
          }
        >
          <option value="">
            {language === "es"
              ? "Todos los roles"
              : "All roles"}
          </option>

          <option value="ADMIN">
            ADMIN
          </option>

          <option value="USER">
            USER
          </option>
        </select>

      </section>


      <section className="panel users-table-panel">

        {loading ? (
          <div className="loading-row">
            {language === "es"
              ? "Cargando usuarios..."
              : "Loading users..."}
          </div>
        ) : (
          <div className="users-table-wrap">
            <table className="users-table">

              <thead>
                <tr>
                  <th>
                    {language === "es"
                      ? "Usuario"
                      : "User"}
                  </th>
                  <th>
                    {language === "es"
                      ? "Rol"
                      : "Role"}
                  </th>
                  <th>
                    {language === "es"
                      ? "Estado"
                      : "Status"}
                  </th>
                  <th>
                    {language === "es"
                      ? "Creado"
                      : "Created"}
                  </th>
                  <th>
                    {language === "es"
                      ? "Acciones"
                      : "Actions"}
                  </th>
                </tr>
              </thead>

              <tbody>

                {filtered.map(
                  (
                    item
                  ) => {

                    const isSelf =
                      item.user_id
                      === currentUser
                        ?.user_id;

                    return (
                      <tr
                        key={
                          item.user_id
                        }
                      >
                        <td>
                          <div className="users-person">
                            <div className="users-avatar">
                              {item.full_name
                                .charAt(0)
                                .toUpperCase()}
                            </div>

                            <div>
                              <strong>
                                {item.full_name}
                              </strong>
                              <span>
                                {item.email}
                              </span>
                            </div>
                          </div>
                        </td>

                        <td>
                          <select
                            value={
                              item.system_role
                            }
                            disabled={
                              isSelf
                            }
                            onChange={(
                              event
                            ) =>
                              void changeUser(
                                item,
                                {
                                  system_role:
                                    event.target.value as
                                      | "ADMIN"
                                      | "USER",
                                }
                              )
                            }
                          >
                            <option value="ADMIN">
                              ADMIN
                            </option>
                            <option value="USER">
                              USER
                            </option>
                          </select>
                        </td>

                        <td>
                          <span
                            className={
                              item.status
                              === "ACTIVE"
                                ? "user-status active"
                                : "user-status disabled"
                            }
                          >
                            {item.status}
                          </span>
                        </td>

                        <td>
                          {new Date(
                            item.created_at
                          ).toLocaleDateString(
                            language === "es"
                              ? "es-PE"
                              : "en-US"
                          )}
                        </td>

                        <td>
                          <button
                            className={
                              item.status
                              === "ACTIVE"
                                ? "danger-button"
                                : "success-button"
                            }
                            disabled={
                              isSelf
                            }
                            onClick={() =>
                              void changeUser(
                                item,
                                {
                                  status:
                                    item.status
                                    === "ACTIVE"
                                      ? "DISABLED"
                                      : "ACTIVE",
                                }
                              )
                            }
                          >
                            {item.status
                            === "ACTIVE"
                              ? (
                                language === "es"
                                  ? "Desactivar"
                                  : "Disable"
                              )
                              : (
                                language === "es"
                                  ? "Activar"
                                  : "Enable"
                              )}
                          </button>
                        </td>
                      </tr>
                    );
                  }
                )}

              </tbody>

            </table>
          </div>
        )}

      </section>


      {showCreate && (
        <div
          className="user-modal-backdrop"
          onMouseDown={(
            event
          ) => {
            if (
              event.target
              === event.currentTarget
            ) {
              setShowCreate(
                false
              );
            }
          }}
        >

          <form
            className="user-modal-card"
            onSubmit={
              submitCreate
            }
          >

            <div className="user-modal-header">
              <div>
                <strong>
                  {language === "es"
                    ? "Crear usuario"
                    : "Create user"}
                </strong>
                <span>
                  {language === "es"
                    ? "La cuenta quedará activa inmediatamente."
                    : "The account will be active immediately."}
                </span>
              </div>

              <button
                type="button"
                className="icon-button"
                onClick={() =>
                  setShowCreate(
                    false
                  )
                }
              >
                <X size={18} />
              </button>
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
                required
                type="email"
                value={email}
                onChange={(
                  event
                ) =>
                  setEmail(
                    event.target.value
                  )
                }
              />
            </label>

            <label>
              {language === "es"
                ? "Contraseña temporal"
                : "Temporary password"}
              <input
                required
                type="password"
                minLength={8}
                value={password}
                onChange={(
                  event
                ) =>
                  setPassword(
                    event.target.value
                  )
                }
              />
            </label>

            <label>
              {language === "es"
                ? "Rol del sistema"
                : "System role"}
              <select
                value={role}
                onChange={(
                  event
                ) =>
                  setRole(
                    event.target.value as
                      | "ADMIN"
                      | "USER"
                  )
                }
              >
                <option value="USER">
                  USER
                </option>
                <option value="ADMIN">
                  ADMIN
                </option>
              </select>
            </label>

            <div className="user-modal-actions">
              <button
                type="button"
                className="button-secondary"
                onClick={() =>
                  setShowCreate(
                    false
                  )
                }
              >
                {language === "es"
                  ? "Cancelar"
                  : "Cancel"}
              </button>

              <button
                type="submit"
                className="button-primary"
                disabled={
                  saving
                }
              >
                {saving
                  ? (
                    language === "es"
                      ? "Creando..."
                      : "Creating..."
                  )
                  : (
                    language === "es"
                      ? "Crear usuario"
                      : "Create user"
                  )}
              </button>
            </div>

          </form>

        </div>
      )}

    </div>
  );
}
