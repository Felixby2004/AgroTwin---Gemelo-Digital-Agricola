import {
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react";

import {
  Cpu,
  MapPin,
  Save,
  X,
} from "lucide-react";

import type {
  Parcel,
} from "../../api/parcels";

import type {
  SensorCreateInput,
  SensorVariable,
} from "../../api/sensors";

import {
  useLanguage,
} from "../../i18n/LanguageContext";


interface SensorFormProps {
  parcels: Parcel[];
  initialParcelId?: string | null;
  submitting?: boolean;
  errorMessage?: string;
  onCancel: () => void;
  onSubmit: (
    payload: SensorCreateInput
  ) => void | Promise<void>;
}


interface SensorTypeOption {
  value: string;
  labelEs: string;
  labelEn: string;
  suggestedVariables: SensorVariable[];
}


interface VariableOption {
  value: SensorVariable;
  labelEs: string;
  labelEn: string;
}


const SENSOR_TYPES:
SensorTypeOption[] = [
  {
    value: "SOIL_MOISTURE",
    labelEs: "Humedad del suelo",
    labelEn: "Soil moisture",
    suggestedVariables: [
      "soil_moisture",
    ],
  },
  {
    value: "AIR_TEMPERATURE",
    labelEs: "Temperatura del aire",
    labelEn: "Air temperature",
    suggestedVariables: [
      "air_temperature",
    ],
  },
  {
    value: "RELATIVE_HUMIDITY",
    labelEs: "Humedad relativa",
    labelEn: "Relative humidity",
    suggestedVariables: [
      "relative_humidity",
    ],
  },
  {
    value: "RAINFALL",
    labelEs: "Pluviómetro",
    labelEn: "Rain gauge",
    suggestedVariables: [
      "rainfall",
    ],
  },
  {
    value: "FLOW_RATE",
    labelEs: "Caudalímetro",
    labelEn: "Flow meter",
    suggestedVariables: [
      "flow_rate",
    ],
  },
  {
    value: "GENERIC_IOT",
    labelEs: "Sensor IoT genérico",
    labelEn: "Generic IoT sensor",
    suggestedVariables: [],
  },
];


const VARIABLE_OPTIONS:
VariableOption[] = [
  {
    value: "soil_moisture",
    labelEs: "Humedad del suelo",
    labelEn: "Soil moisture",
  },
  {
    value: "air_temperature",
    labelEs: "Temperatura del aire",
    labelEn: "Air temperature",
  },
  {
    value: "relative_humidity",
    labelEs: "Humedad relativa",
    labelEn: "Relative humidity",
  },
  {
    value: "rainfall",
    labelEs: "Lluvia",
    labelEn: "Rainfall",
  },
  {
    value: "flow_rate",
    labelEs: "Caudal",
    labelEn: "Flow rate",
  },
];


function parseOptionalNumber(
  value: string
): number | null {

  const trimmed =
    value.trim();

  if (!trimmed) {
    return null;
  }

  return Number(
    trimmed
  );
}


export function SensorForm({
  parcels,
  initialParcelId = null,
  submitting = false,
  errorMessage = "",
  onCancel,
  onSubmit,
}: SensorFormProps) {

  const {
    language,
    tr,
  } = useLanguage();


  const [
    parcelId,
    setParcelId,
  ] = useState(
    initialParcelId ?? ""
  );

  const [
    sensorId,
    setSensorId,
  ] = useState("");

  const [
    name,
    setName,
  ] = useState("");

  const [
    sensorType,
    setSensorType,
  ] = useState(
    "SOIL_MOISTURE"
  );

  const [
    variables,
    setVariables,
  ] = useState<
    SensorVariable[]
  >([
    "soil_moisture",
  ]);

  const [
    latitude,
    setLatitude,
  ] = useState("");

  const [
    longitude,
    setLongitude,
  ] = useState("");

  const [
    manufacturer,
    setManufacturer,
  ] = useState("");

  const [
    model,
    setModel,
  ] = useState("");

  const [
    installedAt,
    setInstalledAt,
  ] = useState("");

  const [
    isActive,
    setIsActive,
  ] = useState(
    true
  );

  const [
    localError,
    setLocalError,
  ] = useState("");


  useEffect(
    () => {
      if (
        initialParcelId
      ) {
        setParcelId(
          initialParcelId
        );
      }
    },
    [
      initialParcelId,
    ]
  );


  const selectedParcel =
    useMemo(
      () =>
        parcels.find(
          (parcel) =>
            parcel.id ===
            parcelId
        ) ?? null,
      [
        parcels,
        parcelId,
      ]
    );


  const toggleVariable = (
    variable: SensorVariable
  ) => {

    setVariables(
      (current) => {

        if (
          current.includes(
            variable
          )
        ) {
          return current.filter(
            (item) =>
              item !== variable
          );
        }

        return [
          ...current,
          variable,
        ];
      }
    );
  };


  const changeSensorType = (
    nextType: string
  ) => {

    setSensorType(
      nextType
    );

    const option =
      SENSOR_TYPES.find(
        (item) =>
          item.value ===
          nextType
      );

    if (
      option &&
      option.suggestedVariables.length > 0
    ) {
      setVariables(
        option.suggestedVariables
      );
    }
  };


  const submit =
    async (
      event: FormEvent
    ) => {

      event.preventDefault();

      const cleanSensorId =
        sensorId.trim();

      const cleanName =
        name.trim();

      const cleanType =
        sensorType.trim();


      if (!parcelId) {
        setLocalError(
          tr(
            "Selecciona la parcela a la que pertenecerá el sensor.",
            "Select the parcel that will own this sensor."
          )
        );
        return;
      }


      if (!cleanSensorId) {
        setLocalError(
          tr(
            "Ingresa un identificador para el sensor.",
            "Enter a sensor identifier."
          )
        );
        return;
      }


      if (!cleanName) {
        setLocalError(
          tr(
            "Ingresa un nombre para el sensor.",
            "Enter a sensor name."
          )
        );
        return;
      }


      if (!cleanType) {
        setLocalError(
          tr(
            "Selecciona un tipo de sensor.",
            "Select a sensor type."
          )
        );
        return;
      }


      if (
        variables.length ===
        0
      ) {
        setLocalError(
          tr(
            "Selecciona al menos una variable medida.",
            "Select at least one measured variable."
          )
        );
        return;
      }


      const parsedLatitude =
        parseOptionalNumber(
          latitude
        );

      const parsedLongitude =
        parseOptionalNumber(
          longitude
        );


      if (
        (
          parsedLatitude === null
        ) !==
        (
          parsedLongitude === null
        )
      ) {
        setLocalError(
          tr(
            "Registra latitud y longitud juntas, o deja ambas vacías.",
            "Enter latitude and longitude together, or leave both blank."
          )
        );
        return;
      }


      if (
        parsedLatitude !== null &&
        (
          !Number.isFinite(
            parsedLatitude
          ) ||
          parsedLatitude < -90 ||
          parsedLatitude > 90
        )
      ) {
        setLocalError(
          tr(
            "La latitud debe estar entre -90 y 90.",
            "Latitude must be between -90 and 90."
          )
        );
        return;
      }


      if (
        parsedLongitude !== null &&
        (
          !Number.isFinite(
            parsedLongitude
          ) ||
          parsedLongitude < -180 ||
          parsedLongitude > 180
        )
      ) {
        setLocalError(
          tr(
            "La longitud debe estar entre -180 y 180.",
            "Longitude must be between -180 and 180."
          )
        );
        return;
      }


      let installedAtIso:
        string | null = null;

      if (
        installedAt
      ) {
        const date =
          new Date(
            installedAt
          );

        if (
          Number.isNaN(
            date.getTime()
          )
        ) {
          setLocalError(
            tr(
              "La fecha de instalación no es válida.",
              "The installation date is invalid."
            )
          );
          return;
        }

        installedAtIso =
          date.toISOString();
      }


      setLocalError("");


      await onSubmit({
        sensor_id:
          cleanSensorId,

        parcel_id:
          parcelId,

        name:
          cleanName,

        sensor_type:
          cleanType,

        variables,

        latitude:
          parsedLatitude,

        longitude:
          parsedLongitude,

        manufacturer:
          manufacturer.trim() ||
          null,

        model:
          model.trim() ||
          null,

        installed_at:
          installedAtIso,

        is_active:
          isActive,

        metadata: {},
      });
    };


  return (

    <form
      className="sensor-create-form"
      onSubmit={
        submit
      }
    >

      <div className="sensor-create-form-header">

        <div className="sensor-create-form-heading">

          <div className="sensor-create-form-icon">
            <Cpu size={20} />
          </div>

          <div>

            <span>
              {tr(
                "Registro IoT",
                "IoT registry"
              )}
            </span>

            <h2>
              {tr(
                "Nuevo sensor",
                "New sensor"
              )}
            </h2>

            <p>
              {tr(
                "Vincula un dispositivo real a una parcela. Registrarlo no crea lecturas ficticias.",
                "Link a real device to a parcel. Registering it does not create fake readings."
              )}
            </p>

          </div>

        </div>


        <button
          type="button"
          className="sensor-close-button"
          onClick={
            onCancel
          }
          disabled={
            submitting
          }
          aria-label={
            tr(
              "Cerrar",
              "Close"
            )
          }
        >
          <X size={18} />
        </button>

      </div>


      <div className="sensor-create-form-body">

        <div className="sensor-create-form-grid">

          <label className="sensor-form-field sensor-form-field-full">

            <span>
              {tr(
                "Parcela *",
                "Parcel *"
              )}
            </span>

            <select
              value={
                parcelId
              }
              onChange={
                (event) =>
                  setParcelId(
                    event.target.value
                  )
              }
              disabled={
                submitting
              }
            >

              <option value="">
                {tr(
                  "Seleccionar parcela...",
                  "Select parcel..."
                )}
              </option>

              {parcels.map(
                (parcel) => (
                  <option
                    key={
                      parcel.id
                    }
                    value={
                      parcel.id
                    }
                  >
                    {parcel.name}
                  </option>
                )
              )}

            </select>

            {selectedParcel && (
              <small>
                {tr(
                  "El dispositivo quedará asociado a esta parcela.",
                  "The device will be associated with this parcel."
                )}
              </small>
            )}

          </label>


          <label className="sensor-form-field">

            <span>
              {tr(
                "ID del sensor *",
                "Sensor ID *"
              )}
            </span>

            <input
              type="text"
              value={
                sensorId
              }
              placeholder="SOIL-002"
              autoComplete="off"
              disabled={
                submitting
              }
              onChange={
                (event) =>
                  setSensorId(
                    event.target.value
                  )
              }
            />

            <small>
              {tr(
                "Identificador único del dispositivo.",
                "Unique device identifier."
              )}
            </small>

          </label>


          <label className="sensor-form-field">

            <span>
              {tr(
                "Nombre *",
                "Name *"
              )}
            </span>

            <input
              type="text"
              value={
                name
              }
              placeholder={
                tr(
                  "Humedad sector norte",
                  "North sector moisture"
                )
              }
              disabled={
                submitting
              }
              onChange={
                (event) =>
                  setName(
                    event.target.value
                  )
              }
            />

          </label>


          <label className="sensor-form-field sensor-form-field-full">

            <span>
              {tr(
                "Tipo de sensor *",
                "Sensor type *"
              )}
            </span>

            <select
              value={
                sensorType
              }
              disabled={
                submitting
              }
              onChange={
                (event) =>
                  changeSensorType(
                    event.target.value
                  )
              }
            >

              {SENSOR_TYPES.map(
                (option) => (
                  <option
                    key={
                      option.value
                    }
                    value={
                      option.value
                    }
                  >
                    {language === "es"
                      ? option.labelEs
                      : option.labelEn}
                  </option>
                )
              )}

            </select>

          </label>


          <fieldset className="sensor-variable-selector sensor-form-field-full">

            <legend>
              {tr(
                "Variables medidas *",
                "Measured variables *"
              )}
            </legend>

            <div className="sensor-variable-options">

              {VARIABLE_OPTIONS.map(
                (option) => {

                  const checked =
                    variables.includes(
                      option.value
                    );

                  return (
                    <label
                      key={
                        option.value
                      }
                      className={
                        checked
                          ? "sensor-variable-option selected"
                          : "sensor-variable-option"
                      }
                    >

                      <input
                        type="checkbox"
                        checked={
                          checked
                        }
                        disabled={
                          submitting
                        }
                        onChange={() =>
                          toggleVariable(
                            option.value
                          )
                        }
                      />

                      <span>
                        {language === "es"
                          ? option.labelEs
                          : option.labelEn}
                      </span>

                    </label>
                  );
                }
              )}

            </div>

          </fieldset>


          <div className="sensor-location-heading sensor-form-field-full">

            <MapPin size={17} />

            <div>
              <strong>
                {tr(
                  "Ubicación del dispositivo",
                  "Device location"
                )}
              </strong>

              <span>
                {tr(
                  "Opcional. Registra ambas coordenadas si el sensor está georreferenciado.",
                  "Optional. Enter both coordinates when the sensor is georeferenced."
                )}
              </span>
            </div>

          </div>


          <label className="sensor-form-field">

            <span>
              {tr(
                "Latitud",
                "Latitude"
              )}
            </span>

            <input
              type="number"
              step="any"
              min="-90"
              max="90"
              value={
                latitude
              }
              placeholder="-8.100000"
              disabled={
                submitting
              }
              onChange={
                (event) =>
                  setLatitude(
                    event.target.value
                  )
              }
            />

          </label>


          <label className="sensor-form-field">

            <span>
              {tr(
                "Longitud",
                "Longitude"
              )}
            </span>

            <input
              type="number"
              step="any"
              min="-180"
              max="180"
              value={
                longitude
              }
              placeholder="-79.000000"
              disabled={
                submitting
              }
              onChange={
                (event) =>
                  setLongitude(
                    event.target.value
                  )
              }
            />

          </label>


          <label className="sensor-form-field">

            <span>
              {tr(
                "Fabricante",
                "Manufacturer"
              )}
            </span>

            <input
              type="text"
              value={
                manufacturer
              }
              placeholder="Decagon / Campbell / ..."
              disabled={
                submitting
              }
              onChange={
                (event) =>
                  setManufacturer(
                    event.target.value
                  )
              }
            />

          </label>


          <label className="sensor-form-field">

            <span>
              {tr(
                "Modelo",
                "Model"
              )}
            </span>

            <input
              type="text"
              value={
                model
              }
              placeholder="Modelo del dispositivo"
              disabled={
                submitting
              }
              onChange={
                (event) =>
                  setModel(
                    event.target.value
                  )
              }
            />

          </label>


          <label className="sensor-form-field sensor-form-field-full">

            <span>
              {tr(
                "Fecha de instalación",
                "Installation date"
              )}
            </span>

            <input
              type="datetime-local"
              value={
                installedAt
              }
              disabled={
                submitting
              }
              onChange={
                (event) =>
                  setInstalledAt(
                    event.target.value
                  )
              }
            />

          </label>


          <label className="sensor-active-toggle sensor-form-field-full">

            <input
              type="checkbox"
              checked={
                isActive
              }
              disabled={
                submitting
              }
              onChange={
                (event) =>
                  setIsActive(
                    event.target.checked
                  )
              }
            />

            <div>
              <strong>
                {tr(
                  "Sensor activo",
                  "Active sensor"
                )}
              </strong>

              <span>
                {tr(
                  "El dispositivo queda habilitado para recibir futuras lecturas IoT.",
                  "The device remains enabled for future IoT readings."
                )}
              </span>
            </div>

          </label>

        </div>


        {(localError || errorMessage) && (
          <div className="error sensor-create-error">
            {localError || errorMessage}
          </div>
        )}


        <div className="sensor-create-form-note">
          {tr(
            "Registrar el sensor solo crea el dispositivo y su vínculo con la parcela. El estado permanecerá «Sin datos» hasta recibir una lectura real.",
            "Registering the sensor only creates the device and its parcel link. Its status remains “No data” until a real reading is received."
          )}
        </div>

      </div>


      <div className="sensor-create-form-actions">

        <button
          type="button"
          className="button-secondary"
          disabled={
            submitting
          }
          onClick={
            onCancel
          }
        >
          {tr(
            "Cancelar",
            "Cancel"
          )}
        </button>


        <button
          type="submit"
          className="button-primary"
          disabled={
            submitting ||
            parcels.length === 0
          }
        >
          <Save size={16} />

          {submitting
            ? tr(
                "Registrando...",
                "Registering..."
              )
            : tr(
                "Registrar sensor",
                "Register sensor"
              )}
        </button>

      </div>

    </form>
  );
}
