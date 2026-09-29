import {
  useEffect,
  useState,
} from "react";

import {
  Save,
  X,
} from "lucide-react";

import {
  CROP_CATALOG,
  getCropBackendValue,
  getCropCodeFromValue,
} from "../../config/cropCatalog";

import type {
  Parcel,
  ParcelCreateInput,
  ParcelUpdateInput,
} from "../../api/parcels";


interface ParcelFormProps {
  parcel?: Parcel | null;
  submitting?: boolean;
  onCancel: () => void;
  onSubmit: (
    payload:
      ParcelCreateInput
      | ParcelUpdateInput
  ) => void | Promise<void>;
}


export function ParcelForm({
  parcel = null,
  submitting = false,
  onCancel,
  onSubmit,
}: ParcelFormProps) {

  const [
    name,
    setName,
  ] = useState(
    parcel?.name ?? ""
  );


  const [
    cropCode,
    setCropCode,
  ] = useState(
    getCropCodeFromValue(
      parcel?.crop_type
    )
  );


  const [
    areaHa,
    setAreaHa,
  ] = useState(
    parcel?.area_ha != null
      ? String(
          parcel.area_ha
        )
      : ""
  );


  const [
    error,
    setError,
  ] = useState("");


  useEffect(
    () => {

      setName(
        parcel?.name ?? ""
      );

      setCropCode(
        getCropCodeFromValue(
          parcel?.crop_type
        )
      );

      setAreaHa(
        parcel?.area_ha != null
          ? String(
              parcel.area_ha
            )
          : ""
      );

      setError("");

    },
    [
      parcel,
    ]
  );


  const submit =
    async () => {

      const trimmedName =
        name.trim();


      if (!trimmedName) {

        setError(
          "Ingresa un nombre para la parcela."
        );

        return;
      }


      if (!cropCode) {

        setError(
          "Selecciona un cultivo."
        );

        return;
      }


      const numericArea =
        Number(
          areaHa
        );


      if (
        !Number.isFinite(
          numericArea
        )
        ||
        numericArea <= 0
      ) {

        setError(
          "Ingresa un área válida mayor que cero."
        );

        return;
      }


      setError("");


      await onSubmit(
        {
          name:
            trimmedName,

          crop_type:
            getCropBackendValue(
              cropCode
            ),

          area_ha:
            numericArea,
        }
      );
    };


  const selectedCrop =
    CROP_CATALOG.find(
      (crop) =>
        crop.code ===
        cropCode
    );


  return (

    <div className="parcel-form-card">

      <div className="parcel-form-header">

        <div>

          <strong>
            {parcel
              ? "Editar parcela"
              : "Nueva parcela"}
          </strong>

          <span>
            Registre los datos básicos. La geometría se administra después desde el mapa.
          </span>

        </div>


        <button
          type="button"
          className="icon-button"
          onClick={
            onCancel
          }
          aria-label="Cerrar formulario"
        >
          <X size={17} />
        </button>

      </div>


      <div className="parcel-form-grid">

        <label>

          Nombre de la parcela

          <input
            type="text"
            value={
              name
            }
            maxLength={200}
            placeholder="Ej. Parcela Norte"
            onChange={
              (
                event
              ) =>
                setName(
                  event
                    .target
                    .value
                )
            }
          />

        </label>


        <label>

          Cultivo

          <select
            value={
              cropCode
            }
            onChange={
              (
                event
              ) =>
                setCropCode(
                  event
                    .target
                    .value
                )
            }
          >

            <option value="">
              Seleccionar cultivo...
            </option>


            {CROP_CATALOG.map(
              (
                crop
              ) => (

                <option
                  key={
                    crop.code
                  }
                  value={
                    crop.code
                  }
                >
                  {crop.labelEs}
                </option>

              )
            )}

          </select>

        </label>


        <label>

          Área

          <div className="parcel-area-input">

            <input
              type="number"
              min="0.01"
              step="0.01"
              value={
                areaHa
              }
              placeholder="Ej. 2.5"
              onChange={
                (
                  event
                ) =>
                  setAreaHa(
                    event
                      .target
                      .value
                  )
              }
            />

            <span>
              ha
            </span>

          </div>

        </label>

      </div>


      {selectedCrop && (

        <div
          className={
            selectedCrop.supportStatus === "SUPPORTED"
              ? "crop-form-support supported"
              : "crop-form-support experimental"
          }
        >

          <strong>
            {selectedCrop.labelEs}
          </strong>

          <span>
            {selectedCrop.supportStatus === "SUPPORTED"
              ? "Este cultivo tiene un perfil agronómico configurado en el motor actual."
              : "Puede registrarse y gestionarse, pero su perfil agronómico específico todavía está en soporte experimental."}
          </span>

        </div>

      )}


      {error && (

        <div className="error">
          {error}
        </div>

      )}


      <div className="parcel-form-actions">

        <button
          type="button"
          className="button-secondary"
          onClick={
            onCancel
          }
          disabled={
            submitting
          }
        >
          Cancelar
        </button>


        <button
          type="button"
          className="button-primary"
          onClick={() =>
            void submit()
          }
          disabled={
            submitting
          }
        >

          <Save size={16} />

          {submitting
            ? "Guardando..."
            : parcel
              ? "Guardar cambios"
              : "Crear parcela"}

        </button>

      </div>

    </div>
  );
}
