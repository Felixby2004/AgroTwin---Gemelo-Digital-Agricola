import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  CircleUserRound,
  RefreshCw,
  Trash2,
  UserPlus,
  Users,
} from "lucide-react";

import {
  getUsers,
} from "../../api/users";

import type {
  User,
} from "../../api/auth";

import type {
  ParcelRole,
} from "../../api/permissions";

import {
  addParcelMember,
  getMembershipRole,
  getParcelMembers,
  removeParcelMember,
  updateParcelMemberRole,
  type ParcelMembership,
} from "../../api/memberships";

import {
  useLanguage,
} from "../../i18n/LanguageContext";

import "./ParcelMembersPanel.css";


interface ParcelMembersPanelProps {
  parcelId: string;
}


type Translate = (
  es: string,
  en: string
) => string;


const ROLES:
ParcelRole[] = [
  "OWNER",
  "FARMER",
  "AGRONOMIST",
  "VIEWER",
];


/* ===================================================== */
/* ROLE PARSER                                           */
/* ===================================================== */

function parseParcelRole(
  value: string
): ParcelRole {

  switch (
    value
  ) {

    case "OWNER":
      return "OWNER";

    case "FARMER":
      return "FARMER";

    case "AGRONOMIST":
      return "AGRONOMIST";

    case "VIEWER":
      return "VIEWER";

    default:
      return "VIEWER";
  }
}


/* ===================================================== */
/* ROLE LABEL                                            */
/* ===================================================== */

function getRoleLabel(
  role: ParcelRole,
  tr: Translate
): string {

  switch (
    role
  ) {

    case "OWNER":

      return tr(
        "Propietario",
        "Owner"
      );


    case "FARMER":

      return tr(
        "Agricultor",
        "Farmer"
      );


    case "AGRONOMIST":

      return tr(
        "Agrónomo",
        "Agronomist"
      );


    case "VIEWER":

      return tr(
        "Observador",
        "Viewer"
      );
  }
}


/* ===================================================== */
/* ROLE DESCRIPTION                                      */
/* ===================================================== */

function getRoleDescription(
  role: ParcelRole,
  tr: Translate
): string {

  switch (
    role
  ) {

    case "OWNER":

      return tr(
        "Control total de la parcela, incluida la gestión de miembros y gobernanza.",
        "Full control of the parcel, including member management and governance."
      );


    case "FARMER":

      return tr(
        "Puede editar la parcela, aportar conocimiento, ejecutar IA y responder recomendaciones.",
        "Can edit the parcel, contribute knowledge, run the decision engine and respond to recommendations."
      );


    case "AGRONOMIST":

      return tr(
        "Puede editar, aportar conocimiento, ejecutar IA, responder recomendaciones y exportar datos.",
        "Can edit, contribute knowledge, run the decision engine, respond to recommendations and export data."
      );


    case "VIEWER":

      return tr(
        "Acceso de solo lectura al gemelo digital.",
        "Read-only access to the digital twin."
      );
  }
}


/* ===================================================== */
/* PERMISSIONS                                           */
/* ===================================================== */

function getRolePermissions(
  role: ParcelRole,
  tr: Translate
): string[] {

  const view =
    tr(
      "Ver",
      "View"
    );

  const edit =
    tr(
      "Editar",
      "Edit"
    );

  const knowledge =
    tr(
      "Conocimiento",
      "Knowledge"
    );

  const runReasoning =
    tr(
      "Ejecutar IA",
      "Run decision engine"
    );

  const respond =
    tr(
      "Responder recomendación",
      "Respond to recommendation"
    );

  const governance =
    tr(
      "Gobernanza",
      "Governance"
    );

  const exportData =
    tr(
      "Exportar",
      "Export"
    );

  const manageMembers =
    tr(
      "Gestionar miembros",
      "Manage members"
    );


  switch (
    role
  ) {

    case "OWNER":

      return [
        view,
        edit,
        knowledge,
        runReasoning,
        respond,
        governance,
        exportData,
        manageMembers,
      ];


    case "FARMER":

      return [
        view,
        edit,
        knowledge,
        runReasoning,
        respond,
      ];


    case "AGRONOMIST":

      return [
        view,
        edit,
        knowledge,
        runReasoning,
        respond,
        exportData,
      ];


    case "VIEWER":

      return [
        view,
      ];
  }
}


/* ===================================================== */
/* ERROR                                                 */
/* ===================================================== */

function getErrorMessage(
  error: unknown,
  fallback: string
) {

  if (
    typeof error ===
      "object"
    &&
    error !==
      null
    &&
    "response" in
      error
  ) {

    const response =
      (
        error as {
          response?: {
            data?: {
              detail?: string;
            };
          };
        }
      ).response;


    if (
      response
        ?.data
        ?.detail
    ) {

      return response
        .data
        .detail;
    }
  }


  return fallback;
}


/* ===================================================== */
/* COMPONENT                                             */
/* ===================================================== */

export function ParcelMembersPanel({
  parcelId,
}: ParcelMembersPanelProps) {

  const {
    tr,
  } = useLanguage();


  const [
    memberships,
    setMemberships,
  ] = useState<
    ParcelMembership[]
  >(
    []
  );


  const [
    users,
    setUsers,
  ] = useState<
    User[]
  >(
    []
  );


  const [
    usersAvailable,
    setUsersAvailable,
  ] = useState(
    true
  );


  const [
    loading,
    setLoading,
  ] = useState(
    true
  );


  const [
    saving,
    setSaving,
  ] = useState(
    false
  );


  const [
    updatingUserId,
    setUpdatingUserId,
  ] = useState<
    string | null
  >(
    null
  );


  const [
    deletingUserId,
    setDeletingUserId,
  ] = useState<
    string | null
  >(
    null
  );


  const [
    error,
    setError,
  ] = useState(
    ""
  );


  const [
    success,
    setSuccess,
  ] = useState(
    ""
  );


  const [
    selectedUserId,
    setSelectedUserId,
  ] = useState(
    ""
  );


  const [
    manualUserId,
    setManualUserId,
  ] = useState(
    ""
  );


  const [
    selectedRole,
    setSelectedRole,
  ] = useState<
    ParcelRole
  >(
    "FARMER"
  );


  /* =================================================== */
  /* DERIVED DATA                                        */
  /* =================================================== */

  const userMap =
    useMemo(
      () => {

        return new Map(
          users.map(
            (
              user
            ) => [
              user.user_id,
              user,
            ]
          )
        );
      },

      [
        users,
      ]
    );


  const existingIds =
    useMemo(
      () => {

        return new Set(
          memberships.map(
            (
              membership
            ) =>
              membership.user_id
          )
        );
      },

      [
        memberships,
      ]
    );


  const eligibleUsers =
    useMemo(
      () => {

        return users.filter(
          (
            user
          ) =>
            user.status !==
              "DISABLED"
            &&
            !existingIds.has(
              user.user_id
            )
        );
      },

      [
        users,
        existingIds,
      ]
    );


  /* =================================================== */
  /* LOAD                                                */
  /* =================================================== */

  const loadData =
    async () => {

      setLoading(
        true
      );

      setError(
        ""
      );

      setSuccess(
        ""
      );


      try {

        const memberData =
          await getParcelMembers(
            parcelId
          );


        setMemberships(
          memberData
        );


        /*
         * /users is currently an ADMIN endpoint.
         * ADMIN gets a selector.
         *
         * A parcel OWNER with USER system role
         * can still manage memberships using
         * a known user_id.
         */
        try {

          const userData =
            await getUsers();


          setUsers(
            userData
          );


          setUsersAvailable(
            true
          );


        } catch {

          setUsers(
            []
          );

          setUsersAvailable(
            false
          );
        }


      } catch (
        loadError
      ) {

        setError(
          getErrorMessage(
            loadError,
            tr(
              "No se pudieron cargar los miembros de la parcela.",
              "Could not load parcel members."
            )
          )
        );


      } finally {

        setLoading(
          false
        );
      }
    };


  useEffect(
    () => {

      void loadData();

    },
    [
      parcelId,
    ]
  );


  /* =================================================== */
  /* ADD MEMBER                                          */
  /* =================================================== */

  const handleAddMember =
    async () => {

      const userId =
        (
          usersAvailable
            ? selectedUserId
            : manualUserId
        )
          .trim();


      if (
        !userId
      ) {

        setError(
          usersAvailable

            ? tr(
                "Selecciona un usuario.",
                "Select a user."
              )

            : tr(
                "Ingresa el ID del usuario.",
                "Enter the user ID."
              )
        );

        return;
      }


      setSaving(
        true
      );

      setError(
        ""
      );

      setSuccess(
        ""
      );


      try {

        await addParcelMember(
          parcelId,
          userId,
          selectedRole
        );


        setSelectedUserId(
          ""
        );

        setManualUserId(
          ""
        );


        setSuccess(
          tr(
            "Miembro agregado correctamente.",
            "Member added successfully."
          )
        );


        const memberData =
          await getParcelMembers(
            parcelId
          );


        setMemberships(
          memberData
        );


      } catch (
        addError
      ) {

        setError(
          getErrorMessage(
            addError,
            tr(
              "No se pudo agregar el miembro.",
              "Could not add the member."
            )
          )
        );


      } finally {

        setSaving(
          false
        );
      }
    };


  /* =================================================== */
  /* UPDATE ROLE                                         */
  /* =================================================== */

  const handleRoleChange =
    async (
      userId: string,
      role: ParcelRole
    ) => {

      setUpdatingUserId(
        userId
      );

      setError(
        ""
      );

      setSuccess(
        ""
      );


      try {

        await updateParcelMemberRole(
          parcelId,
          userId,
          role
        );


        setMemberships(
          (
            current
          ) =>
            current.map(
              (
                membership
              ) => {

                if (
                  membership.user_id !==
                  userId
                ) {

                  return membership;
                }


                return {
                  ...membership,
                  role,
                  parcel_role:
                    role,
                };
              }
            )
        );


        setSuccess(
          tr(
            "Rol actualizado correctamente.",
            "Role updated successfully."
          )
        );


      } catch (
        updateError
      ) {

        setError(
          getErrorMessage(
            updateError,
            tr(
              "No se pudo actualizar el rol.",
              "Could not update the role."
            )
          )
        );


        /*
         * The server remains authoritative,
         * including last-OWNER protection.
         */
        const memberData =
          await getParcelMembers(
            parcelId
          );


        setMemberships(
          memberData
        );


      } finally {

        setUpdatingUserId(
          null
        );
      }
    };


  /* =================================================== */
  /* REMOVE MEMBER                                       */
  /* =================================================== */

  const handleRemove =
    async (
      membership:
        ParcelMembership
    ) => {

      const user =
        userMap.get(
          membership.user_id
        );


      const label =
        user?.full_name
        ||
        user?.email
        ||
        membership.user_id;


      const confirmed =
        window.confirm(
          tr(
            `¿Eliminar a ${label} de esta parcela?`,
            `Remove ${label} from this parcel?`
          )
        );


      if (
        !confirmed
      ) {
        return;
      }


      setDeletingUserId(
        membership.user_id
      );

      setError(
        ""
      );

      setSuccess(
        ""
      );


      try {

        await removeParcelMember(
          parcelId,
          membership.user_id
        );


        setMemberships(
          (
            current
          ) =>
            current.filter(
              (
                item
              ) =>
                item.user_id !==
                membership.user_id
            )
        );


        setSuccess(
          tr(
            "Miembro eliminado correctamente.",
            "Member removed successfully."
          )
        );


      } catch (
        removeError
      ) {

        setError(
          getErrorMessage(
            removeError,
            tr(
              "No se pudo eliminar el miembro.",
              "Could not remove the member."
            )
          )
        );


      } finally {

        setDeletingUserId(
          null
        );
      }
    };


  /* =================================================== */
  /* LOADING                                             */
  /* =================================================== */

  if (
    loading
  ) {

    return (

      <section className="panel parcel-members-panel">

        <div className="members-loading">

          <RefreshCw
            size={18}
            className="members-spin"
          />

          {tr(
            "Cargando miembros...",
            "Loading members..."
          )}

        </div>

      </section>
    );
  }


  /* =================================================== */
  /* VIEW                                                */
  /* =================================================== */

  return (

    <section className="panel parcel-members-panel">

      {/* ================================================= */}
      {/* HEADER                                            */}
      {/* ================================================= */}

      <div className="panel-header">

        <div className="panel-header-title">

          <div className="panel-icon">

            <Users
              size={20}
            />

          </div>


          <div>

            <h2>

              {tr(
                "Miembros y permisos",
                "Members and permissions"
              )}

            </h2>


            <p>

              {tr(
                "Roles específicos para esta parcela",
                "Roles specific to this parcel"
              )}

            </p>

          </div>

        </div>


        <button
          type="button"
          className="button-secondary members-refresh-button"
          onClick={() =>
            void loadData()
          }
        >

          <RefreshCw
            size={16}
          />

          {tr(
            "Actualizar",
            "Refresh"
          )}

        </button>

      </div>


      {/* ================================================= */}
      {/* MESSAGES                                          */}
      {/* ================================================= */}

      {error && (

        <div className="members-message error">
          {error}
        </div>
      )}


      {success && (

        <div className="members-message success">
          {success}
        </div>
      )}


      {/* ================================================= */}
      {/* MEMBERS                                           */}
      {/* ================================================= */}

      <div className="members-list">

        {memberships.length ===
          0 ? (

          <div className="members-empty">

            {tr(
              "Esta parcela todavía no tiene miembros registrados.",
              "This parcel does not have any registered members yet."
            )}

          </div>

        ) : (

          memberships.map(
            (
              membership
            ) => {

              const user =
                userMap.get(
                  membership.user_id
                );


              const role =
                getMembershipRole(
                  membership
                );


              const isUpdating =
                updatingUserId ===
                membership.user_id;


              const isDeleting =
                deletingUserId ===
                membership.user_id;


              return (

                <article
                  className="member-row"
                  key={
                    membership.user_id
                  }
                >

                  {/* ===================================== */}
                  {/* IDENTITY                              */}
                  {/* ===================================== */}

                  <div className="member-identity">

                    <div className="member-avatar">

                      <CircleUserRound
                        size={22}
                      />

                    </div>


                    <div>

                      <strong>

                        {user
                          ?.full_name
                          ||
                          tr(
                            "Usuario de la parcela",
                            "Parcel user"
                          )}

                      </strong>


                      <span>

                        {user
                          ?.email
                          ||
                          membership.user_id}

                      </span>


                      {user && (

                        <small>

                          {tr(
                            "Global:",
                            "Global:"
                          )}{" "}

                          {user.system_role}

                        </small>
                      )}

                    </div>

                  </div>


                  {/* ===================================== */}
                  {/* ROLE                                  */}
                  {/* ===================================== */}

                  <div className="member-role-control">

                    <label>

                      {tr(
                        "Rol en esta parcela",
                        "Role in this parcel"
                      )}

                    </label>


                    <select
                      value={
                        role
                      }
                      disabled={
                        isUpdating
                        ||
                        isDeleting
                      }
                      onChange={
                        (
                          event
                        ) => {

                          const nextRole =
                            parseParcelRole(
                              event
                                .currentTarget
                                .value
                            );


                          void handleRoleChange(
                            membership.user_id,
                            nextRole
                          );
                        }
                      }
                    >

                      {ROLES.map(
                        (
                          item
                        ) => (

                          <option
                            key={
                              item
                            }
                            value={
                              item
                            }
                          >

                            {getRoleLabel(
                              item,
                              tr
                            )}

                          </option>
                        )
                      )}

                    </select>


                    <small>

                      {isUpdating

                        ? tr(
                            "Guardando...",
                            "Saving..."
                          )

                        : getRoleDescription(
                            role,
                            tr
                          )}

                    </small>

                  </div>


                  {/* ===================================== */}
                  {/* DELETE                                */}
                  {/* ===================================== */}

                  <button
                    type="button"
                    className="member-delete-button"
                    disabled={
                      isDeleting
                      ||
                      isUpdating
                    }
                    onClick={() =>
                      void handleRemove(
                        membership
                      )
                    }
                    title={tr(
                      "Eliminar de la parcela",
                      "Remove from parcel"
                    )}
                  >

                    <Trash2
                      size={17}
                    />


                    {isDeleting

                      ? tr(
                          "Eliminando...",
                          "Removing..."
                        )

                      : tr(
                          "Eliminar",
                          "Remove"
                        )}

                  </button>

                </article>
              );
            }
          )
        )}

      </div>


      {/* ================================================= */}
      {/* ADD MEMBER                                        */}
      {/* ================================================= */}

      <div className="add-member-card">

        <div className="add-member-heading">

          <UserPlus
            size={19}
          />


          <div>

            <strong>

              {tr(
                "Agregar miembro",
                "Add member"
              )}

            </strong>


            <span>

              {tr(
                "Vincula un usuario existente con esta parcela.",
                "Link an existing user to this parcel."
              )}

            </span>

          </div>

        </div>


        <div className="add-member-grid">

          {/* ============================================= */}
          {/* USER                                          */}
          {/* ============================================= */}

          <label>

            <span>

              {tr(
                "Usuario",
                "User"
              )}

            </span>


            {usersAvailable ? (

              <select
                value={
                  selectedUserId
                }
                onChange={
                  (
                    event
                  ) =>
                    setSelectedUserId(
                      event
                        .target
                        .value
                    )
                }
              >

                <option value="">

                  {tr(
                    "Seleccionar usuario",
                    "Select user"
                  )}

                </option>


                {eligibleUsers.map(
                  (
                    user
                  ) => (

                    <option
                      key={
                        user.user_id
                      }
                      value={
                        user.user_id
                      }
                    >

                      {user.full_name}

                      {" · "}

                      {user.email}

                    </option>
                  )
                )}

              </select>

            ) : (

              <input
                type="text"
                value={
                  manualUserId
                }
                onChange={
                  (
                    event
                  ) =>
                    setManualUserId(
                      event
                        .target
                        .value
                    )
                }
                placeholder="USER-XXXXXXXXXXXX"
              />

            )}


            {!usersAvailable && (

              <small>

                {tr(
                  "Tu cuenta puede gestionar la parcela, pero no consultar el directorio global. Ingresa el ID del usuario.",
                  "Your account can manage this parcel but cannot access the global user directory. Enter the user ID."
                )}

              </small>
            )}

          </label>


          {/* ============================================= */}
          {/* ROLE                                          */}
          {/* ============================================= */}

          <label>

            <span>

              {tr(
                "Rol en la parcela",
                "Role in parcel"
              )}

            </span>


            <select
              value={
                selectedRole
              }
              onChange={
                (
                  event
                ) => {

                  setSelectedRole(
                    parseParcelRole(
                      event
                        .currentTarget
                        .value
                    )
                  );
                }
              }
            >

              {ROLES.map(
                (
                  role
                ) => (

                  <option
                    key={
                      role
                    }
                    value={
                      role
                    }
                  >

                    {getRoleLabel(
                      role,
                      tr
                    )}

                  </option>
                )
              )}

            </select>


            <small>

              {getRoleDescription(
                selectedRole,
                tr
              )}

            </small>

          </label>


          {/* ============================================= */}
          {/* ADD                                           */}
          {/* ============================================= */}

          <button
            type="button"
            className="button-primary add-member-button"
            disabled={
              saving
            }
            onClick={() =>
              void handleAddMember()
            }
          >

            <UserPlus
              size={17}
            />


            {saving

              ? tr(
                  "Agregando...",
                  "Adding..."
                )

              : tr(
                  "Agregar miembro",
                  "Add member"
                )}

          </button>

        </div>


        {/* =============================================== */}
        {/* SELECTED ROLE PERMISSIONS                       */}
        {/* =============================================== */}

        <div className="selected-role-permissions">

          <strong>

            {tr(
              `Permisos de ${getRoleLabel(
                selectedRole,
                tr
              )}`,
              `${getRoleLabel(
                selectedRole,
                tr
              )} permissions`
            )}

          </strong>


          <div>

            {getRolePermissions(
              selectedRole,
              tr
            ).map(
              (
                permission
              ) => (

                <span
                  key={
                    permission
                  }
                >

                  ✓ {permission}

                </span>
              )
            )}

          </div>

        </div>

      </div>


      {/* ================================================= */}
      {/* ROLE MATRIX                                       */}
      {/* ================================================= */}

      <details className="role-matrix">

        <summary>

          {tr(
            "Ver matriz de roles y permisos",
            "View roles and permissions matrix"
          )}

        </summary>


        <div className="role-matrix-grid">

          {ROLES.map(
            (
              role
            ) => (

              <article
                key={
                  role
                }
              >

                <strong>

                  {getRoleLabel(
                    role,
                    tr
                  )}

                </strong>


                <span className="role-code">

                  {role}

                </span>


                <p>

                  {getRoleDescription(
                    role,
                    tr
                  )}

                </p>


                <div>

                  {getRolePermissions(
                    role,
                    tr
                  ).map(
                    (
                      permission
                    ) => (

                      <span
                        key={
                          permission
                        }
                      >

                        ✓ {permission}

                      </span>
                    )
                  )}

                </div>

              </article>
            )
          )}

        </div>

      </details>

    </section>
  );
}