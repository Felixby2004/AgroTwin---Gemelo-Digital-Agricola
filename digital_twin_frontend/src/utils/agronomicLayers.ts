export type TwinAgronomicLayer =
  | "crop"
  | "ndvi"
  | "ndmi"
  | "soil-moisture"
  | "soil-profile";


export function clamp01(
  value: number
): number {

  return Math.max(
    0,
    Math.min(
      1,
      value
    )
  );
}


export function ndviColor(
  value:
    | number
    | null
    | undefined
): string {

  if (
    typeof value !==
    "number"
  ) {
    return "#64748b";
  }


  if (value < 0.20) {
    return "#9a5b38";
  }

  if (value < 0.35) {
    return "#d58a32";
  }

  if (value < 0.50) {
    return "#c9aa32";
  }

  if (value < 0.65) {
    return "#75a93d";
  }

  return "#27843c";
}


export function ndmiColor(
  value:
    | number
    | null
    | undefined
): string {

  if (
    typeof value !==
    "number"
  ) {
    return "#64748b";
  }


  if (value < -0.25) {
    return "#985838";
  }

  if (value < 0) {
    return "#bf815b";
  }

  if (value < 0.20) {
    return "#80a990";
  }

  if (value < 0.40) {
    return "#4e9298";
  }

  return "#3279a5";
}


export function soilMoistureColor(
  value:
    | number
    | null
    | undefined
): string {

  if (
    typeof value !==
    "number"
  ) {
    return "#795b43";
  }


  const normalized =
    clamp01(
      value / 0.40
    );


  if (normalized < 0.28) {
    return "#94623f";
  }

  if (normalized < 0.50) {
    return "#7f684e";
  }

  if (normalized < 0.72) {
    return "#557a72";
  }

  return "#3d7189";
}


export function layerLabel(
  layer: TwinAgronomicLayer
): string {

  switch (layer) {

    case "crop":
      return "Cultivo";

    case "ndvi":
      return "NDVI";

    case "ndmi":
      return "NDMI";

    case "soil-moisture":
      return "Humedad";

    case "soil-profile":
      return "Perfil de suelo";

    default:
      return "Cultivo";
  }
}


export function formatLayerValue(
  value:
    | number
    | null
    | undefined,
  digits = 3
): string {

  if (
    typeof value !==
    "number"
  ) {
    return "—";
  }


  return value.toFixed(
    digits
  );
}
