export type CropModelKind =
  | "maize"
  | "potato"
  | "rice"
  | "wheat"
  | "onion"
  | "tomato"
  | "avocado"
  | "coffee"
  | "sugarcane"
  | "quinoa"
  | "generic";


export interface CropVisualProfile {
  key: CropModelKind;
  label: string;
  rowSpacingM: number;
  plantSpacingM: number;
  populationUnit: string;
  maxRenderedInstances: number;
  baseScale: number;
  healthyColor: string;
  stressedColor: string;
}


/*
 * Configurable visualization defaults.
 * They estimate population for the 3D viewer; they are not
 * a farm-specific agronomic prescription.
 */
const PROFILES:
Record<CropModelKind, CropVisualProfile> = {

  maize: {
    key: "maize",
    label: "Maíz",
    rowSpacingM: 0.75,
    plantSpacingM: 0.20,
    populationUnit: "plantas",
    maxRenderedInstances: 800,
    baseScale: 0.82,
    healthyColor: "#2f9e44",
    stressedColor: "#b5a642",
  },

  potato: {
    key: "potato",
    label: "Papa",
    rowSpacingM: 0.80,
    plantSpacingM: 0.30,
    populationUnit: "plantas",
    maxRenderedInstances: 850,
    baseScale: 0.82,
    healthyColor: "#3a9d4f",
    stressedColor: "#a8a843",
  },

  rice: {
    key: "rice",
    label: "Arroz",
    rowSpacingM: 0.20,
    plantSpacingM: 0.20,
    populationUnit: "golpes",
    maxRenderedInstances: 1200,
    baseScale: 0.85,
    healthyColor: "#53a548",
    stressedColor: "#b7a64b",
  },

  wheat: {
    key: "wheat",
    label: "Trigo",
    rowSpacingM: 0.20,
    plantSpacingM: 0.05,
    populationUnit: "plantas",
    maxRenderedInstances: 1200,
    baseScale: 0.80,
    healthyColor: "#7fa94c",
    stressedColor: "#c1a957",
  },

  onion: {
    key: "onion",
    label: "Cebolla",
    rowSpacingM: 0.30,
    plantSpacingM: 0.10,
    populationUnit: "plantas",
    maxRenderedInstances: 1000,
    baseScale: 0.72,
    healthyColor: "#47a65c",
    stressedColor: "#b4aa55",
  },

  tomato: {
    key: "tomato",
    label: "Tomate",
    rowSpacingM: 1.20,
    plantSpacingM: 0.50,
    populationUnit: "plantas",
    maxRenderedInstances: 600,
    baseScale: 0.95,
    healthyColor: "#2f9548",
    stressedColor: "#a5a74c",
  },

  avocado: {
    key: "avocado",
    label: "Palta",
    rowSpacingM: 6.00,
    plantSpacingM: 4.00,
    populationUnit: "árboles",
    maxRenderedInstances: 220,
    baseScale: 1.15,
    healthyColor: "#2d8742",
    stressedColor: "#8d9850",
  },

  coffee: {
    key: "coffee",
    label: "Café",
    rowSpacingM: 2.00,
    plantSpacingM: 1.00,
    populationUnit: "plantas",
    maxRenderedInstances: 500,
    baseScale: 0.90,
    healthyColor: "#277c3c",
    stressedColor: "#8b9450",
  },

  sugarcane: {
    key: "sugarcane",
    label: "Caña de azúcar",
    rowSpacingM: 1.50,
    plantSpacingM: 0.30,
    populationUnit: "cepas",
    maxRenderedInstances: 900,
    baseScale: 1.05,
    healthyColor: "#3b9a4b",
    stressedColor: "#a7a84c",
  },

  quinoa: {
    key: "quinoa",
    label: "Quinua",
    rowSpacingM: 0.50,
    plantSpacingM: 0.10,
    populationUnit: "plantas",
    maxRenderedInstances: 800,
    baseScale: 0.82,
    healthyColor: "#4c9b4f",
    stressedColor: "#b49b57",
  },

  generic: {
    key: "generic",
    label: "Cultivo",
    rowSpacingM: 0.75,
    plantSpacingM: 0.25,
    populationUnit: "plantas",
    maxRenderedInstances: 850,
    baseScale: 0.90,
    healthyColor: "#37934a",
    stressedColor: "#aca34c",
  },
};


export function normalizeCropKey(
  cropType:
    | string
    | null
    | undefined
): CropModelKind {

  const value =
    cropType
      ?.trim()
      .toLowerCase()
    ?? "";


  const aliases:
  Record<string, CropModelKind> = {
    maize: "maize",
    corn: "maize",
    maíz: "maize",
    maiz: "maize",
    potato: "potato",
    papa: "potato",
    rice: "rice",
    arroz: "rice",
    wheat: "wheat",
    trigo: "wheat",
    onion: "onion",
    cebolla: "onion",
    tomato: "tomato",
    tomate: "tomato",
    avocado: "avocado",
    palta: "avocado",
    coffee: "coffee",
    café: "coffee",
    cafe: "coffee",
    sugarcane: "sugarcane",
    "sugar cane": "sugarcane",
    "caña de azúcar": "sugarcane",
    "cana de azucar": "sugarcane",
    quinoa: "quinoa",
    quinua: "quinoa",
  };


  return (
    aliases[value]
    ?? "generic"
  );
}


export function getCropVisualProfile(
  cropType:
    | string
    | null
    | undefined
): CropVisualProfile {

  return PROFILES[
    normalizeCropKey(
      cropType
    )
  ];
}


export function resolveVisualizationAreaHa(
  declaredAreaHa:
    | number
    | null
    | undefined,
  geometryAreaHa:
    | number
    | null
    | undefined
): number {

  if (
    typeof declaredAreaHa === "number"
    &&
    Number.isFinite(declaredAreaHa)
    &&
    declaredAreaHa > 0
  ) {
    return declaredAreaHa;
  }


  if (
    typeof geometryAreaHa === "number"
    &&
    Number.isFinite(geometryAreaHa)
    &&
    geometryAreaHa > 0
  ) {
    return geometryAreaHa;
  }


  return 1;
}


export function estimateCropPopulation(
  areaHa: number,
  profile: CropVisualProfile
): number {

  const squareMeters =
    Math.max(
      0.01,
      areaHa
    )
    * 10_000;


  const areaPerPlant =
    Math.max(
      0.001,
      profile.rowSpacingM
      *
      profile.plantSpacingM
    );


  return Math.max(
    1,
    Math.round(
      squareMeters
      /
      areaPerPlant
    )
  );
}


export function estimateRenderedInstanceCount(
  actualPopulation: number,
  profile: CropVisualProfile
): number {

  /*
   * The 3D parcel is a normalized miniature, not a 1:1 physical scene.
   * Rendering a proportional fraction of every real plant makes large
   * parcels look like an impenetrable wall of vegetation.
   *
   * This square-root sampling deliberately prioritizes visual realism:
   * enough plants to communicate field-scale density, but enough space
   * to perceive rows, soil and individual crop morphology.
   */
  const densityMultiplier =
    profile.key === "avocado"
      ? 22
      : profile.key === "coffee"
        ? 28
        : profile.key === "tomato"
          ? 30
          : profile.key === "maize"
            ? 24
            : profile.key === "potato"
              ? 27
              : profile.key === "sugarcane"
                ? 25
                : profile.key === "rice"
                  ? 23
                  : profile.key === "wheat"
                    ? 22
                    : 24;


  const representative =
    Math.round(
      densityMultiplier
      *
      Math.sqrt(
        Math.max(
          1,
          actualPopulation
        )
        /
        1000
      )
    );


  return Math.max(
    profile.key === "avocado"
      ? 24
      : 70,
    Math.min(
      profile.maxRenderedInstances,
      representative
    )
  );
}
