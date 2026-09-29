import {
  useEffect,
  useState,
} from "react";

import {
  ShieldCheck,
  ShieldX,
  History,
  CheckCircle2,
  XCircle,
  Clock3,
} from "lucide-react";

import {
  getParcels,
  type Parcel,
} from "../api/parcels";

import {
  getParcelConsents,
  getParcelAudit,
  updateConsentStatus,
  type Consent,
  type AuditEvent,
} from "../api/governance";

import {
  useLanguage,
} from "../i18n/LanguageContext";


export function GovernancePage() {

  const {
    t,
    language,
  } = useLanguage();


  const [
    parcels,
    setParcels,
  ] = useState<Parcel[]>([]);

  const [
    selectedParcelId,
    setSelectedParcelId,
  ] = useState("");

  const [
    consents,
    setConsents,
  ] = useState<Consent[]>([]);

  const [
    audit,
    setAudit,
  ] = useState<AuditEvent[]>([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");


  const loadGovernance = async (
    parcelId: string
  ) => {

    try {

      setLoading(true);
      setError("");

      const [
        consentData,
        auditData,
      ] = await Promise.all([
        getParcelConsents(
          parcelId
        ),
        getParcelAudit(
          parcelId
        ),
      ]);

      setConsents(
        consentData
      );

      setAudit(
        auditData
      );

    } catch {

      setError(
        t("governance.loadError")
      );

    } finally {

      setLoading(false);

    }

  };


  useEffect(() => {

    const init = async () => {

      try {

        const parcelData =
          await getParcels();

        setParcels(
          parcelData
        );

        const preferred =
          parcelData.find(
            (item) =>
              item.name ===
              "Adapter Test Parcel"
          ) ||
          parcelData[0];

        if (preferred) {

          setSelectedParcelId(
            preferred.id
          );

          await loadGovernance(
            preferred.id
          );

        }

      } catch {

        setError(
          t("governance.parcelsLoadError")
        );

        setLoading(false);

      }

    };


    void init();

  }, []);


  const selectedParcel =
    parcels.find(
      (item) =>
        item.id ===
        selectedParcelId
    );


  const activeCount =
    consents.filter(
      (item) =>
        item.status ===
        "ACTIVE"
    ).length;


  const revokedCount =
    consents.filter(
      (item) =>
        item.status ===
        "REVOKED"
    ).length;


  const handleParcelChange = async (
    parcelId: string
  ) => {

    setSelectedParcelId(
      parcelId
    );

    await loadGovernance(
      parcelId
    );

  };


  const handleStatusChange = async (
    consentId: string,
    status:
      | "ACTIVE"
      | "REVOKED"
  ) => {

    try {

      await updateConsentStatus(
        consentId,
        status
      );

      await loadGovernance(
        selectedParcelId
      );

    } catch {

      setError(
        t("governance.updateError")
      );

    }

  };


  return (
    <div>

      <section className="page-header">

        <div>

          <h1>
            {t("governance.title")}
          </h1>

          <p>
            {t("governance.subtitle")}
          </p>

        </div>


        <select
          className="page-select"
          value={selectedParcelId}
          onChange={(event) =>
            void handleParcelChange(
              event.target.value
            )
          }
        >

          {parcels.map(
            (parcel) => (

              <option
                key={parcel.id}
                value={parcel.id}
              >
                {parcel.name}
              </option>

            )
          )}

        </select>

      </section>


      {error && (
        <div className="error">
          {error}
        </div>
      )}


      <section className="governance-metrics">

        <article className="governance-stat">

          <div className="governance-stat-icon green">
            <ShieldCheck size={22} />
          </div>

          <div>

            <span>
              {t("governance.activeConsents")}
            </span>

            <strong>
              {activeCount}
            </strong>

          </div>

        </article>


        <article className="governance-stat">

          <div className="governance-stat-icon red">
            <ShieldX size={22} />
          </div>

          <div>

            <span>
              {t("governance.revoked")}
            </span>

            <strong>
              {revokedCount}
            </strong>

          </div>

        </article>


        <article className="governance-stat">

          <div className="governance-stat-icon blue">
            <History size={22} />
          </div>

          <div>

            <span>
              {t("governance.auditEvents")}
            </span>

            <strong>
              {audit.length}
            </strong>

          </div>

        </article>

      </section>


      <section className="governance-grid">

        <article className="panel">

          <div className="panel-header">

            <div className="panel-header-title">

              <div className="panel-icon">
                <ShieldCheck size={20} />
              </div>

              <div>

                <h2>
                  {t("governance.consents")}
                </h2>

                <p>
                  {selectedParcel?.name ||
                    t("governance.parcelFallback")}
                </p>

              </div>

            </div>

          </div>


          <div className="consent-list">

            {loading && (
              <div className="loading-row">
                {t("governance.loading")}
              </div>
            )}


            {!loading &&
              consents.length === 0 && (

              <div className="loading-row">
                {t("governance.noConsents")}
              </div>

            )}


            {consents.map(
              (consent) => (

                <div
                  key={
                    consent.consent_id
                  }
                  className="consent-card"
                >

                  <div className="consent-main">

                    <div
                      className={
                        consent.status ===
                        "ACTIVE"
                          ? "consent-status-icon active"
                          : "consent-status-icon revoked"
                      }
                    >

                      {consent.status ===
                      "ACTIVE" ? (
                        <CheckCircle2
                          size={19}
                        />
                      ) : (
                        <XCircle
                          size={19}
                        />
                      )}

                    </div>


                    <div>

                      <strong>
                        {consent.status === "ACTIVE"
                          ? t("governance.status.ACTIVE")
                          : consent.status === "REVOKED"
                            ? t("governance.status.REVOKED")
                            : consent.status}
                      </strong>

                      <span>
                        {consent
                          .purposes
                          .join(" · ")}
                      </span>

                      <small>
                        {consent
                          .permissions
                          .join(" · ")}
                      </small>

                    </div>

                  </div>


                  <div className="consent-actions">

                    {consent.status ===
                    "ACTIVE" ? (

                      <button
                        className="danger-button"
                        onClick={() =>
                          void handleStatusChange(
                            consent.consent_id,
                            "REVOKED"
                          )
                        }
                      >
                        {t("governance.revoke")}
                      </button>

                    ) : (

                      <button
                        className="success-button"
                        onClick={() =>
                          void handleStatusChange(
                            consent.consent_id,
                            "ACTIVE"
                          )
                        }
                      >
                        {t("governance.activate")}
                      </button>

                    )}

                  </div>

                </div>

              )
            )}

          </div>

        </article>


        <article className="panel">

          <div className="panel-header">

            <div className="panel-header-title">

              <div className="panel-icon purple-icon">
                <History size={20} />
              </div>

              <div>

                <h2>
                  {t("governance.auditTraceability")}
                </h2>

                <p>
                  {t("governance.latestOperations")}
                </p>

              </div>

            </div>

          </div>


          <div className="audit-list">

            {audit.map(
              (event) => (

                <div
                  key={event.audit_id}
                  className="audit-row"
                >

                  <div
                    className={
                      event.allowed
                        ? "audit-icon allowed"
                        : "audit-icon denied"
                    }
                  >

                    {event.allowed ? (
                      <CheckCircle2
                        size={17}
                      />
                    ) : (
                      <XCircle
                        size={17}
                      />
                    )}

                  </div>


                  <div className="audit-content">

                    <strong>
                      {event.action}
                    </strong>

                    <span>
                      {event.actor_id}
                    </span>

                    <small>
                      <Clock3 size={12} />
                      {new Date(
                        event.created_at
                      ).toLocaleString(
                        language === "es"
                          ? "es-PE"
                          : "en-US"
                      )}
                    </small>

                  </div>


                  <span
                    className={
                      event.allowed
                        ? "audit-result allowed"
                        : "audit-result denied"
                    }
                  >
                    {event.allowed
                      ? t("governance.allowed")
                      : t("governance.denied")}
                  </span>

                </div>

              )
            )}

          </div>

        </article>

      </section>

    </div>
  );
}